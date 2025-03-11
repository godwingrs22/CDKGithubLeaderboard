import json
import os
import datetime
import urllib.request
from typing import Dict, List, Optional, TypedDict, Any, Set

# Get GitHub token from environment variables
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')

class Contributor(TypedDict):
    username: str
    prsMerged: int
    prsReviewed: int
    totalScore: int

def github_graphql(query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a GraphQL query against GitHub API
    
    Args:
        query: The GraphQL query string
        variables: Variables for the query
        
    Returns:
        The JSON response from GitHub
    """
    request_data = json.dumps({
        'query': query, 
        'variables': variables
    }).encode('utf-8')
    
    headers = {
        'Authorization': f'Bearer {GITHUB_TOKEN}',
        'Content-Type': 'application/json',
        'User-Agent': 'GitHub-Leaderboard-Lambda',
    }
    
    request = urllib.request.Request(
        'https://api.github.com/graphql',
        data=request_data,
        headers=headers,
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"GitHub API error: {e.code} - {error_body}")
        raise Exception(f"GitHub API error: {e.code} - {error_body}")

#TODO: for score calculation for all fields
def calculate_score(contributor: Contributor) -> int:
    """
    Calculate the score for a contributor
    
    Args:
        contributor: Contributor data
        
    Returns:
        Total score
    """
    return contributor['prsMerged'] * 10 + contributor['prsReviewed'] * 8

def fetch_all_contributors(org: str, repo: str) -> Set[str]:
    """
    Fetch all contributors with pagination
    
    Args:
        org: GitHub organization/owner name
        repo: Repository name
        
    Returns:
        Set of contributor usernames
    """
    contributors: Set[str] = set()
    has_next_page = True
    cursor = None
    
    while has_next_page:
        query = """
            query($queryString: String!, $cursor: String) {
              search(query: $queryString, type: ISSUE, first: 100, after: $cursor) {
                pageInfo {
                  hasNextPage
                  endCursor
                }
                nodes {
                  ... on PullRequest {
                    author {
                      login
                    }
                    reviews(first: 100) {
                      nodes {
                        author {
                          login
                        }
                      }
                    }
                  }
                }
              }
            }
        """
        
        search_query = f"repo:{org}/{repo} is:pr is:merged merged:>=2024-01-01"
        response = github_graphql(query, {
            'queryString': search_query,
            'cursor': cursor
        })
        
        search_data = response.get('data', {}).get('search', {})
        
        # Process authors and reviewers
        for pr in search_data.get('nodes', []):
            if pr.get('author', {}).get('login'):
                contributors.add(pr['author']['login'])
            
            for review in pr.get('reviews', {}).get('nodes', []):
                if review.get('author', {}).get('login'):
                    contributors.add(review['author']['login'])
        
        page_info = search_data.get('pageInfo', {})
        has_next_page = page_info.get('hasNextPage', False)
        cursor = page_info.get('endCursor')
        
        print(f"Found {len(contributors)} contributors so far...")
    
    return contributors

def fetch_contributions_data(org: str, repo: str, username: str) -> Contributor:
    """
    Fetch contributions data for a specific user
    
    Args:
        org: GitHub organization/owner name
        repo: Repository name
        username: GitHub username
        
    Returns:
        Contributor data
    """
    # Get merged PRs count with pagination
    merged_count = 0
    merge_cursor = None
    has_next_page = True
    
    while has_next_page:
        merge_query = f"repo:{org}/{repo} author:{username} is:pr is:merged merged:>=2024-01-01"
        merge_response = github_graphql("""
            query($queryString: String!, $cursor: String) {
              search(query: $queryString, type: ISSUE, first: 100, after: $cursor) {
                pageInfo {
                  hasNextPage
                  endCursor
                }
                nodes {
                  ... on PullRequest {
                    number
                  }
                }
              }
            }
        """, {
            'queryString': merge_query,
            'cursor': merge_cursor
        })
        
        search_data = merge_response.get('data', {}).get('search', {})
        merged_count += len(search_data.get('nodes', []))
        
        page_info = search_data.get('pageInfo', {})
        has_next_page = page_info.get('hasNextPage', False)
        merge_cursor = page_info.get('endCursor')

    # Get reviews count with pagination
    review_count = 0
    review_cursor = None
    has_next_page = True
    
    while has_next_page:
        review_query = f"repo:{org}/{repo} is:pr is:merged merged:>=2024-01-01 reviewed-by:{username}"
        review_response = github_graphql("""
            query($queryString: String!, $cursor: String) {
              search(query: $queryString, type: ISSUE, first: 100, after: $cursor) {
                pageInfo {
                  hasNextPage
                  endCursor
                }
                nodes {
                  ... on PullRequest {
                    number
                  }
                }
              }
            }
        """, {
            'queryString': review_query,
            'cursor': review_cursor
        })
        
        search_data = review_response.get('data', {}).get('search', {})
        review_count += len(search_data.get('nodes', []))
        
        page_info = search_data.get('pageInfo', {})
        has_next_page = page_info.get('hasNextPage', False)
        review_cursor = page_info.get('endCursor')

    contributor: Contributor = {
        'username': username,
        'prsMerged': merged_count,
        'prsReviewed': review_count,
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
    potential_contributors = fetch_all_contributors(org, repo)
    print(f"Found {len(potential_contributors)} total potential contributors")
    
    for i, username in enumerate(potential_contributors, 1):
        print(f"Processing contributor {i}/{len(potential_contributors)}: {username}")
        contributor = fetch_contributions_data(org, repo, username)
        
        if is_active_contributor(contributor):
            active_contributors[username] = contributor
            print(f"Added {username} with {contributor['prsMerged']} PRs merged and {contributor['prsReviewed']} PRs reviewed")
        else:
            print(f"Skipped {username} (no active contributions since 2024)")
    
    print(f"\nFound {len(active_contributors)} active contributors out of {len(potential_contributors)} potential contributors")
    return active_contributors

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler function
    
    Args:
        event: Lambda event
        context: Lambda context
        
    Returns:
        API response with leaderboard data
    """
    print(f"Received event: {json.dumps(event)}")
    
    try:
        org = event.get('org', 'aws')
        repo = event.get('repo', 'aws-cdk')
        
        if not GITHUB_TOKEN:
            raise ValueError("GITHUB_TOKEN environment variable is not set")
            
        print(f"Generating leaderboard for {org}/{repo}")
        
        contributors_dict = process_contributions(org, repo)
        
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
