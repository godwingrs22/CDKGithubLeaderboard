import os
from datetime import datetime
import csv
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from dotenv import load_dotenv
from pathlib import Path

# Import maintainers from separate file
from maintainers import MAINTAINERS

# Load environment variables
load_dotenv()

# Constants
EXCLUDED_AUTHORS = ['github-actions'] + MAINTAINERS
EXCLUDED_LABELS = ['contribution/core']

def fetch_github_issues():
    try:
        # Set up GraphQL client
        transport = RequestsHTTPTransport(
            url='https://api.github.com/graphql',
            headers={'Authorization': f'Bearer {os.getenv("GITHUB_TOKEN")}'}
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)

        # Initialize variables for pagination
        has_next_page = True
        end_cursor = None
        all_issues = []

        while has_next_page:
            # GraphQL query
            query = gql("""
                query($cursor: String) {
                    repository(owner: "aws", name: "aws-cdk") {
                        issues(
                            first: 100,
                            after: $cursor,
                            orderBy: {field: CREATED_AT, direction: DESC},
                            filterBy: {since: "2024-01-01T00:00:00Z"}
                        ) {
                            nodes {
                                title
                                url
                                author {
                                    login
                                }
                                createdAt
                                state
                                labels(first: 100) {
                                    nodes {
                                        name
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
            """)

            # Execute query
            response = client.execute(query, variable_values={'cursor': end_cursor})
            
            # Process response
            issues = response['repository']['issues']['nodes']
            all_issues.extend(issues)
            
            # Update pagination info
            page_info = response['repository']['issues']['pageInfo']
            has_next_page = page_info['hasNextPage']
            end_cursor = page_info['endCursor']

        # Filter issues
        filtered_issues = [
            issue for issue in all_issues
            if issue.get('author') and
            issue['author']['login'] not in EXCLUDED_AUTHORS and
            not any(label['name'] in EXCLUDED_LABELS for label in issue['labels']['nodes'])
        ]

        # Group by author
        author_stats = {}
        for issue in filtered_issues:
            author = issue['author']['login']
            if author not in author_stats:
                author_stats[author] = {
                    'login': author,
                    'issue_count': 0,
                    'issues': []
                }
            
            author_stats[author]['issue_count'] += 1
            author_stats[author]['issues'].append({
                'title': issue['title'],
                'url': issue['url'],
                'created_at': issue['createdAt']
            })

        # Sort authors by issue count
        sorted_authors = sorted(
            author_stats.values(),
            key=lambda x: x['issue_count'],
            reverse=True
        )

        # Prepare output directory
        output_dir = Path(__file__).parent.parent / 'output'
        output_dir.mkdir(exist_ok=True)

        # Generate filename with current date
        current_date = datetime.now().strftime('%Y-%m-%d')
        filename = f'aws-cdk-external-contributors-{current_date}.csv'
        filepath = output_dir / filename

        # Write CSV file
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Rank', 'Author', 'Issues Created', 'Latest Issue', 
                           'Latest Issue Date', 'Latest Issue URL'])
            
            for idx, author in enumerate(sorted_authors, 1):
                latest_issue = author['issues'][0] if author['issues'] else {
                    'title': '',
                    'created_at': '',
                    'url': ''
                }
                writer.writerow([
                    idx,
                    author['login'],
                    author['issue_count'],
                    latest_issue['title'],
                    datetime.fromisoformat(latest_issue['created_at'].replace('Z', '+00:00')).strftime('%Y-%m-%d'),
                    latest_issue['url']
                ])

        # Print statistics
        print('\nAWS CDK External Contributors Statistics (Since January 1st, 2024)')
        print('===========================================================')
        print(f'Total issues analyzed: {len(all_issues)}')
        print(f'External contributor issues: {len(filtered_issues)}')
        print(f'Unique external contributors: {len(author_stats)}')
        print(f'\nExcluded:')
        print(f'- Labels: {", ".join(EXCLUDED_LABELS)}')
        print(f'- Maintainers & System: {len(EXCLUDED_AUTHORS)} users')
        print(f'\nData has been exported to: {filepath}')

    except Exception as e:
        print('Error fetching issues:', str(e))

if __name__ == '__main__':
    fetch_github_issues()
