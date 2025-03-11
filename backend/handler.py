import json
import os
import datetime
from models import Contributor
from typing import Dict, List, Optional, TypedDict, Any, Set
from github_api import GitHubAPI
from issue_analyzer import fetch_github_issues
from constants import AUTHORS_TO_EXCLUDE

def calculate_score(contributor: Contributor) -> int:
    """
    Calculate the score for a contributor
    """
    return (
        contributor['prsMerged'] * 10 + 
        contributor['prsReviewed'] * 8 +
        contributor['issuesCreated'] * 5 +
        contributor['issuesCommented'] * 3
    )

def is_author_to_exclude(username: str) -> bool:
    """
    Check if a username belongs to an author that should be excluded
    """
    return username in AUTHORS_TO_EXCLUDE

def fetch_all_contributors(github_api: GitHubAPI, org: str, repo: str) -> Set[str]:
    """
    Fetch all contributors with pagination
    """
    contributors = set()
    has_next_page = True
    cursor = None
    
    while has_next_page:
        response = github_api.get_all_contributors(org, repo, cursor)
        search_data = response.get('data', {}).get('search', {})
        
        for pr in search_data.get('nodes', []):
            if pr.get('author', {}).get('login'):
                contributors.add(pr['author']['login'])
            
            for review in pr.get('reviews', {}).get('nodes', []):
                if review.get('author', {}).get('login'):
                    contributors.add(review['author']['login'])
        
        page_info = search_data.get('pageInfo', {})
        has_next_page = page_info.get('hasNextPage', False)
        cursor = page_info.get('endCursor')
    
    return contributors

def fetch_contributions_data(github_api: GitHubAPI, org: str, repo: str, username: str) -> Contributor:
    """
    Fetch contributions data for a specific user
    """
    # Get merged PRs count
    merged_count = 0
    has_next_page = True
    cursor = None
    
    while has_next_page:
        response = github_api.get_contributor_prs(org, repo, username, cursor)
        search_data = response.get('data', {}).get('search', {})
        merged_count += len(search_data.get('nodes', []))
        
        page_info = search_data.get('pageInfo', {})
        has_next_page = page_info.get('hasNextPage', False)
        cursor = page_info.get('endCursor')

    # Get reviews count
    review_count = 0
    has_next_page = True
    cursor = None
    
    while has_next_page:
        response = github_api.get_contributor_reviews(org, repo, username, cursor)
        search_data = response.get('data', {}).get('search', {})
        review_count += len(search_data.get('nodes', []))
        
        page_info = search_data.get('pageInfo', {})
        has_next_page = page_info.get('hasNextPage', False)
        review_cursor = page_info.get('endCursor')

    contributor: Contributor = {
        'username': username,
        'prsMerged': merged_count,
        'prsReviewed': review_count,
        'issuesCreated': issues_created,
        'issuesCommented': issues_commented,
        'totalScore': 0
    }
    
    contributor['totalScore'] = calculate_score(contributor)
    return contributor

def is_active_contributor(contributor: Contributor) -> bool:
    """
    Check if a contributor has active contributions since 2024
    
    Args:
        contributor: Contributor data to check
        
    Returns:
        True if contributor has either merged PRs or reviewed PRs, False otherwise
    """
    return (
        contributor['prsMerged'] > 0 or 
        contributor['prsReviewed'] > 0
    )

def process_contributions(org: str, repo: str) -> Dict[str, Contributor]:
    """
    Process contributions for all contributors
    
    Args:
        org: GitHub organization/owner name
        repo: Repository name
        
    Returns:
        Dictionary of active contributors and their data
    """
    active_contributors: Dict[str, Contributor] = {}
    
    print(f"Fetching contributors for {org}/{repo}")
    github_api = GithubAPI(GITHUB_TOKEN)
    
    # Get PR and review data
    pr_data = github_api.get_contributor_reviews(org, repo)
    
    # Get issues data
    issues_data = github_api.get_contributor_reviews(org, repo)
    
    # Combine all contributors
    all_contributors = set(pr_data.keys()) | set(issues_data.keys())
    
    print(f"Found {len(all_contributors)} total potential contributors")
    
    for username in all_contributors:
        pr_stats = pr_data.get(username, {'prsMerged': 0, 'prsReviewed': 0})
        issue_stats = issues_data.get(username, {'issuesCreated': 0})
        
        contributor: Contributor = {
            'username': username,
            'prsMerged': pr_stats.get('prsMerged', 0),
            'prsReviewed': pr_stats.get('prsReviewed', 0),
            'issuesCreated': issue_stats.get('issuesCreated', 0),
            'totalScore': 0
        }
        
        if is_active_contributor(contributor):
            contributor['totalScore'] = calculate_score(contributor)
            active_contributors[username] = contributor
            print(f"Added {username} with {contributor['prsMerged']} PRs merged, "
                  f"{contributor['prsReviewed']} PRs reviewed, and "
                  f"{contributor['issuesCreated']} issues created")
    
    print(f"\nFound {len(active_contributors)} active contributors")
    return active_contributors


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler function
    """
    print(f"Received event: {json.dumps(event)}")
    
    try:
        org = event.get('org', 'aws')
        repo = event.get('repo', 'aws-cdk')
        
        github_token = os.environ.get('GITHUB_TOKEN')
        if not github_token:
            raise ValueError("GITHUB_TOKEN environment variable is not set")
            
        github_api = GitHubAPI(github_token)
        print(f"Generating leaderboard for {org}/{repo}")

        # Call the fetch_github_issues function
        fetch_github_issues()
        
        contributors_dict = process_contributions(github_api, org, repo)
        
        if not contributors_dict:
            print("Warning: No contributors found")
        
        contributors_list = list(contributors_dict.values())
        contributors_list.sort(key=lambda c: c['totalScore'], reverse=True)
        top_contributors = contributors_list[:25]

        leaderboard_data = {
            'lastUpdated': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'contributors': top_contributors,
            'totalContributors': len(contributors_dict)
        }
        
        print("\nLeaderboard Data:")
        print(json.dumps(leaderboard_data, indent=2))
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(leaderboard_data, default=str)
        }
        
    except Exception as e:
        print(f"Error updating leaderboard: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'Internal server error',
                'error': str(e)
            })
        }

# For local testing
if __name__ == "__main__":
    event = {
        'org': 'aws',
        'repo': 'aws-cdk'
    }

    result = handler(event, None)
    
    # Print the status code
    print(f"\nbody: {result['body']}")
