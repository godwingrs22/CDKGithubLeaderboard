import json
import os
import urllib.request
from typing import Dict, List, Any, Optional, Set

class GithubAPI:
    """
    GitHub API client for fetching contribution data
    """
    def __init__(self, token: str):
        self.token = token
        self.api_url = 'https://api.github.com/graphql'

    def graphql_query(self, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
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
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'User-Agent': 'GitHub-Leaderboard-Script',
        }
        
        request = urllib.request.Request(
            self.api_url,
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

    def get_contributor_prs(self, org: str, repo: str, username: str, cursor: Optional[str] = None) -> Dict[str, Any]:
        """
        Get merged PRs for a specific contributor
        """
        query = f"repo:{org}/{repo} author:{username} is:pr is:merged merged:>=2024-01-01"
        graphql_query = """
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
        """
        return self.graphql_query(graphql_query, {
            'queryString': query,
            'cursor': cursor
        })

    def get_contributor_reviews(self, org: str, repo: str, username: str, cursor: Optional[str] = None) -> Dict[str, Any]:
        """
        Get PR reviews for a specific contributor
        """
        query = f"repo:{org}/{repo} is:pr is:merged merged:>=2024-01-01 reviewed-by:{username}"
        graphql_query = """
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
        """
        return self.graphql_query(graphql_query, {
            'queryString': query,
            'cursor': cursor
        })

    def get_all_contributors(self, org: str, repo: str, cursor: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all contributors to the repository
        """
        query = f"repo:{org}/{repo} is:pr is:merged merged:>=2024-01-01"
        graphql_query = """
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
        return self.graphql_query(graphql_query, {
            'queryString': query,
            'cursor': cursor
        })

    def fetch_user_issues(self, org: str, repo: str) -> Dict[str, Any]:
        """
        Execute a GraphQL query to fetch issues created since 2024
        
        Args:
            org: GitHub organization/owner name  
            repo: Repository name
            
        Returns:
            Dictionary with total_count and items containing issue data
        """
        query = f"repo:{org}/{repo} is:issue -is:pr created:>=2024-01-01"
        graphql_query = """
            query($queryString: String!, $cursor: String) {
              search(query: $queryString, type: ISSUE, first: 100, after: $cursor) {
                pageInfo {
                  hasNextPage
                  endCursor
                }
                nodes {
                  ... on Issue {
                    number
                    author {
                      login
                    }
                    createdAt
                  }
                }
              }
            }
        """
        return self.graphql_query(graphql_query, {
            'queryString': query,
            'cursor': cursor
        })

    def get_issue_authors(self, org: str, repo: str) -> List[str]:
        """
        Get list of users who created issues
        
        Args:
            org: GitHub organization/owner name
            repo: Repository name
            
        Returns:
            List of GitHub usernames
        """
        query = f"repo:{org}/{repo} is:issue -is:pr created:>=2024-01-01"
        response = self._execute_graphql_query("""
            query($queryString: String!, $cursor: String) {
              search(query: $queryString, type: ISSUE, first: 100, after: $cursor) {
                pageInfo {
                  hasNextPage
                  endCursor
                }
                nodes {
                  ... on Issue {
                    author {
                      login
                    }
                  }
                }
              }
            }
        """, {
            'queryString': query,
            'cursor': None
        })
        
        search_data = response.get('data', {}).get('search', {})
        return [issue['author']['login'] for issue in search_data.get('nodes', []) 
                if issue.get('author', {}).get('login')]
