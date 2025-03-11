import json
import os
import datetime
import urllib.request
from typing import Dict, List, Optional, TypedDict, Any

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

def fetch_contributions_data(org: str, repo: str, cursor: Optional[str] = None) -> Dict[str, Any]:
    search_query = f"repo:{org}/{repo} is:pr is:merged merged:>=2024-01-01"
    
    query = """
        query($queryString: String!, $cursor: String) {
          search(
            query: $queryString
            type: ISSUE
            first: 100
            after: $cursor
          ) {
            nodes {
              ... on PullRequest {
                number
                author {
                  login
                }
                mergedAt
                title
                reviews(first: 100) {
                  nodes {
                    author {
                      login
                    }
                    createdAt
                    state
                  }
                }
              }
            }
            pageInfo {
              hasNextPage
              endCursor
            }
          }
        }
    """
    
    return github_graphql(query, {
        'queryString': search_query,
        'cursor': cursor
    })

def process_contributions(org: str, repo: str) -> Dict[str, Contributor]:
    """
    Process contributions for a repository
    """
    contributors: Dict[str, Contributor] = {}
    has_next_page = True
    cursor = None
    
    print(f"Fetching contributions data for {org}/{repo}")
    
    # Track PRs for debugging
    pr_details = {}
    
    while has_next_page:
        response = fetch_contributions_data(org, repo, cursor)
        search_results = response.get('data', {}).get('search')
        
        if not search_results:
            print(f"Error fetching data. Response: {json.dumps(response)}")
            break
            
        # Process pull requests
        for pr in search_results.get('nodes', []):
            if not pr or not pr.get('author'):
                continue
                
            author = pr['author']
            username = author['login']
            
            # Debug logging
            if username not in pr_details:
                pr_details[username] = []
            pr_details[username].append({
                'number': pr['number'],
                'title': pr['title'],
                'mergedAt': pr['mergedAt']
            })
            
            if username not in contributors:
                contributors[username] = {
                    'username': username,
                    'prsMerged': 0,
                    'prsReviewed': 0,
                    'totalScore': 0
                }
                
            contributors[username]['prsMerged'] += 1
            
            # Process reviews
            for review in pr.get('reviews', {}).get('nodes', []):
                if not review or not review.get('author'):
                    continue
                
                reviewer = review['author']
                reviewer_username = reviewer['login']
                
                if reviewer_username not in contributors:
                    contributors[reviewer_username] = {
                        'username': reviewer_username,
                        'prsMerged': 0,
                        'prsReviewed': 0,
                        'totalScore': 0
                    }
                    
                contributors[reviewer_username]['prsReviewed'] += 1
        
        # Update pagination
        page_info = search_results.get('pageInfo', {})
        has_next_page = page_info.get('hasNextPage', False)
        cursor = page_info.get('endCursor')
        
        print(f"Processed page. Contributors so far: {len(contributors)}")
    
    # Debug output for specific contributor
    for username, prs in pr_details.items():
        print(f"\nContributor {username} PRs in 2024:")
        for pr in prs:
            print(f"  PR #{pr['number']}: {pr['title']} (merged: {pr['mergedAt']})")
    
    print(f"\nFound {len(contributors)} contributors for {org}/{repo}")
    return contributors

def handler(event, context):
    """
    Lambda handler function for GitHub leaderboard
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
        
        contributors_list = []
        for username, contributor in contributors_dict.items():
            contributor['totalScore'] = calculate_score(contributor)
            contributors_list.append(contributor)
        
        contributors_list.sort(key=lambda c: c['totalScore'], reverse=True)
        top_contributors = contributors_list[:25]

        leaderboard_data = {
            'lastUpdated': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'contributors': top_contributors,
            'totalContributors': len(contributors_dict)
        }
        
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
    

if __name__ == "__main__":
    event = {
        'org': 'aws',
        'repo': 'aws-cdk'
    }
    result = handler(event, None)
    
    # Print the status code
    print(f"\nbody: {result['body']}")