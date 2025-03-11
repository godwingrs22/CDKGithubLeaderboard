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
    """
    Fetch contributions data from GitHub GraphQL API
    """
    query = """
        query($org: String!, $repo: String!, $cursor: String) {
          repository(owner: $org, name: $repo) {
            pullRequests(
              first: 50, 
              after: $cursor, 
              states: [MERGED],
              orderBy: {field: UPDATED_AT, direction: DESC}
            ) {
              nodes {
                author {
                  login
                }
                mergedAt
                updatedAt
                reviews(first: 50) {
                  nodes {
                    author {
                      login
                    }
                    updatedAt
                  }
                }
              }
              pageInfo {
                hasNextPage
                endCursor
              }
            }
          }
        }
    """
    
    return github_graphql(
        query, 
        {
            'org': org,
            'repo': repo,
            'cursor': cursor
        }
    )

def process_contributions(org: str, repo: str) -> Dict[str, Contributor]:
    """
    Process contributions for a repository
    """
    contributors: Dict[str, Contributor] = {}
    has_next_page = True
    cursor = None
    start_date = datetime.datetime.fromisoformat("2024-01-01T00:00:00+00:00")
    
    print(f"Fetching contributions data for {org}/{repo}")
    
    while has_next_page:
        response = fetch_contributions_data(org, repo, cursor)
        repository = response.get('data', {}).get('repository', {})
        
        if not repository or 'pullRequests' not in repository:
            print(f"Error fetching data. Response: {json.dumps(response)}")
            break
            
        pull_requests = repository['pullRequests']
        
        # Process pull requests
        for pr in pull_requests.get('nodes', []):
            if not pr or not pr.get('author') or not pr.get('mergedAt'):
                continue
                
            merged_at = datetime.datetime.fromisoformat(
                pr['mergedAt'].replace('Z', '+00:00')
            )
            
            # Skip if PR was merged before 2024
            if merged_at < start_date:
                has_next_page = False
                break
                
            author = pr['author']
            username = author['login']
            
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
                if not review or not review.get('author') or not review.get('updatedAt'):
                    continue
                
                review_date = datetime.datetime.fromisoformat(
                    review['updatedAt'].replace('Z', '+00:00')
                )
                
                # Skip reviews from before 2024
                if review_date < start_date:
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
        page_info = pull_requests.get('pageInfo', {})
        has_next_page = page_info.get('hasNextPage', False)
        cursor = page_info.get('endCursor')
        
        print(f"Processed page. Contributors so far: {len(contributors)}")
    
    print(f"Found {len(contributors)} contributors for {org}/{repo}")
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