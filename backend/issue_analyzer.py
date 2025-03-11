import os
from datetime import datetime
import csv
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from dotenv import load_dotenv
from pathlib import Path
from typing import TypedDict, List, Literal, Dict

# Import maintainers from separate file
from constants import AUTHORS_TO_EXCLUDE, EXCLUDED_LABELS

# Load environment variables
load_dotenv()

# Constants
EXCLUDED_AUTHORS = ['github-actions'] + AUTHORS_TO_EXCLUDE

# Type definitions
class Discussion(TypedDict):
    discussion_number: int
    title: str
    role: Literal['author', 'commenter', 'replier']

class UserDiscussionStats(TypedDict):
    username: str
    discussions_answered: int
    discussions: List[Discussion]

def fetch_github_discussions(client: Client):
            query = gql("""
        query($owner: String!, $repo: String!) {
          repository(owner: $owner, name: $repo) {
            discussions(first: 100) {
                                    nodes {
                number
                title
                                author {
                                    login
                                    }
                comments(first: 100) {
                  nodes {
                    author {
                      login
                    }
                                replies(first: 100) {
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
            }
        }
            """)

    response = client.execute(query, variable_values={
        'owner': os.getenv('GITHUB_OWNER'),
        'repo': os.getenv('GITHUB_REPO')
    })
    return response['repository']['discussions']['nodes']

def analyze_user_discussion_activity(discussions_data) -> List[UserDiscussionStats]:
    user_stats: Dict[str, UserDiscussionStats] = {}
    for discussion in discussions_data:
        # Track discussion author
        author_username = discussion['author']['login']
        if author_username not in user_stats:
            user_stats[author_username] = {
                'username': author_username,
                'discussions_answered': 0,
                'discussions': []
            }
        
        user_stats[author_username]['discussions'].append({
            'discussion_number': discussion['number'],
            'title': discussion['title'],
            'role': 'author'
        })

        # Track commenters
        for comment in discussion['comments']['nodes']:
            commenter_username = comment['author']['login']
            if commenter_username not in user_stats:
                user_stats[commenter_username] = {
                    'username': commenter_username,
                    'discussions_answered': 0,
                    'discussions': []
                }

            user_stat = user_stats[commenter_username]
            if not any(d['discussion_number'] == discussion['number'] for d in user_stat['discussions']):
                user_stat['discussions_answered'] += 1
                user_stat['discussions'].append({
                    'discussion_number': discussion['number'],
                    'title': discussion['title'],
                    'role': 'commenter'
                })

            # Track reply authors
            for reply in comment['replies']['nodes']:
                replier_username = reply['author']['login']
                if replier_username not in user_stats:
                    user_stats[replier_username] = {
                        'username': replier_username,
                        'discussions_answered': 0,
                        'discussions': []
                    }

                replier_stat = user_stats[replier_username]
                if not any(d['discussion_number'] == discussion['number'] for d in replier_stat['discussions']):
                    replier_stat['discussions_answered'] += 1
                    replier_stat['discussions'].append({
                        'discussion_number': discussion['number'],
                        'title': discussion['title'],
                        'role': 'replier'
                    })

    # Sort by number of discussions answered
    return sorted(
        list(user_stats.values()),
        key=lambda x: x['discussions_answered'],
        reverse=True
        )

def generate_user_activity_report(owner: str, repo: str, user_stats: List[UserDiscussionStats]) -> str:
    report = f"Discussion Activity Report for {owner}/{repo}\n\n"
    
    for user in user_stats:
        report += f"{user['username']}:\n"
        report += f"Total Discussions Answered: {user['discussions_answered']}\n"
        report += "Discussion Participation:\n"
        
        for disc in user['discussions']:
            report += f"- #{disc['discussion_number']}: {disc['title']} ({disc['role']})\n"
        report += "\n"
    
    return report

def fetch_github_data():
    try:
        transport = RequestsHTTPTransport(
            url='https://api.github.com/graphql',
            headers={'Authorization': f'Bearer {os.getenv("GITHUB_TOKEN")}'}
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)

        # Fetch and analyze discussions
        discussions_data = fetch_github_discussions(client)
        user_discussion_stats = analyze_user_discussion_activity(discussions_data)

        # Generate report
        report = generate_user_activity_report(
            os.getenv('GITHUB_OWNER', ''),
            os.getenv('GITHUB_REPO', ''),
            user_discussion_stats
        )
        
        # Output report
        print(report)

        # Write to CSV
        current_date = datetime.now().strftime('%Y-%m-%d')
        output_dir = Path('reports')
        output_dir.mkdir(exist_ok=True)
        discussions_filename = f'aws-cdk-discussions-activity-{current_date}.csv'
        discussions_filepath = output_dir / discussions_filename
        
        with open(discussions_filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Username', 'Discussions Answered', 'Discussion Number',
                           'Discussion Title', 'Role'])
            for user_stat in user_discussion_stats:
                for discussion in user_stat['discussions']:
                    writer.writerow([
                        user_stat['username'],
                        user_stat['discussions_answered'],
                        discussion['discussion_number'],
                        discussion['title'],
                        discussion['role']
                    ])

        print(f'Discussion activity data has been exported to: {discussions_filepath}')

    except Exception as e:
        print('Error fetching data:', str(e))

if __name__ == "__main__":
    fetch_github_data()
