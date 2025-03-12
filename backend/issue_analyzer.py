import logging
import requests
import os
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from collections import defaultdict

logger = logging.getLogger(__name__)

def get_answered_discussions(org: str, repo: str, github_token):
    """Get a mapping of usernames to their answered discussions"""
    transport = RequestsHTTPTransport(
        url='https://api.github.com/graphql',
        headers={'Authorization': f'Bearer {github_token}'}
    )
    
    client = Client(transport=transport, fetch_schema_from_transport=True)
    
    query = gql("""
    query($cursor: String) {
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
            result = client.execute(query, variable_values={'cursor': cursor})
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
        for username, count in user_discussions.items():
            logger.info(f"User {username} answered {count} discussions")
            
        return dict(user_discussions)
        
    except Exception as e:
        logger.error(f"Error analyzing discussions: {str(e)}")
        return {}
