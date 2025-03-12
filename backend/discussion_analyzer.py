import logging
import requests
import os
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from collections import defaultdict
from github_api import GitHubAPI

logger = logging.getLogger(__name__)

class DiscussionAnalyzer:
    def __init__(self, github_api: GitHubAPI):
        self.github_api = github_api
        self.user_discussions = {}
        self.is_initialized = False

    def initialize_discussions(self, org: str, repo: str):
        """Initialize discussion data for the repository"""
        if self.is_initialized:
            return

        transport = RequestsHTTPTransport(
            url='https://api.github.com/graphql',
            headers={'Authorization': f'Bearer {self.github_api.token}'}
        )
        
        client = Client(transport=transport, fetch_schema_from_transport=True)
        query = gql("""
        query($org: String!, $repo: String!, $cursor: String) {
            repository(owner: $org, name: $repo) {
                discussions(first: 100, after: $cursor, orderBy: {field: CREATED_AT, direction: DESC}) {
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                    nodes {
                        number
                        answer {
                            author {
                                login
                            }
                        }
                    }
                }
            }
        }
        """)
        
        try:
            user_discussions = defaultdict(int)
            has_next_page = True
            cursor = None
            total_discussions = 0
            
            while has_next_page:
                result = client.execute(query, variable_values={'org': org, 'repo': repo, 'cursor': cursor})
                discussions_data = result['repository']['discussions']
                discussions = discussions_data['nodes']
                total_discussions += len(discussions)
                
                # Process discussions in current page
                for discussion in discussions:
                    answer = discussion.get('answer', {})
                    if answer and answer.get('author'):
                        username = answer['author']['login']
                        user_discussions[username] += 1
                
                # Update pagination info
                page_info = discussions_data['pageInfo']
                has_next_page = page_info['hasNextPage']
                cursor = page_info['endCursor']

            self.user_discussions = dict(user_discussions)
            self.is_initialized = True
            
            for username, count in self.user_discussions.items():
                logger.info(f"User {username} answered {count} discussions")
                
        except Exception as e:
            logger.error(f"Error analyzing discussions: {str(e)}")
            self.user_discussions = {}
            self.is_initialized = False

    def get_user_discussion_count(self, username: str) -> int:
        """Get the number of discussions answered by a specific user"""
        return self.user_discussions.get(username, 0)
