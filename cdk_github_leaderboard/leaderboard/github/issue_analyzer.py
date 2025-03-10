import os
import json
from datetime import datetime
import requests
import pandas as pd
from typing import List, Dict

MAINTAINERS = [
    'rix0rrr', 'iliapolo', 'otaviomacedo', 'kaizencc',
    'TheRealAmazonKendra', 'mrgrain', 'pahud', 'ashishdhingra',
    'kellertk', 'moelasmar', 'paulhcsun', 'GavinZZ', 'xazhao',
    'gracelu0', 'shikha372', 'QuantumNeuralCoder', 'godwingrs22',
    'bergjaak', 'samson-keung', 'IanKonlog', 'Leo10Gama',
    'scorbiere', 'jiayiwang7', 'saiyush', '5d', 'iankhou',
    'SimonCMoore'
]

def run_github_query(query: str, token: str) -> Dict:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    response = requests.post(
        'https://api.github.com/graphql',
        json={'query': query},
        headers=headers
    )
    return response.json()

def analyze_issues(token: str) -> pd.DataFrame:
    query = """
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
          }
          pageInfo {
            hasNextPage
            endCursor
          }
        }
      }
    }
    """
    
    all_issues = []
    has_next_page = True
    cursor = None

    while has_next_page:
        result = run_github_query(query.replace("$cursor", f'"{cursor}"' if cursor else "null"), token)
        data = result['data']['repository']['issues']
        
        for issue in data['nodes']:
            if issue['author'] and issue['author']['login'] not in MAINTAINERS:
                all_issues.append({
                    'author': issue['author']['login'],
                    'title': issue['title'],
                    'url': issue['url'],
                    'created_at': issue['createdAt']
                })
        
        has_next_page = data['pageInfo']['hasNextPage']
        cursor = data['pageInfo']['endCursor']

    df = pd.DataFrame(all_issues)
    return df.groupby('author').agg({
        'title': 'count',
        'created_at': 'max',
        'url': lambda x: list(x)[-1]
    }).reset_index()

def handler(event, context):
    """Lambda handler function"""
    try:
        token = os.environ['GITHUB_TOKEN']
        df = analyze_issues(token)
        
        # Convert to CSV
        output = df.to_csv(index=False)
        
        # You might want to save this to S3 or another storage service
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Analysis completed successfully',
                'timestamp': datetime.now().isoformat(),
                'contributor_count': len(df)
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }

if __name__ == "__main__":
    # For local testing
    from dotenv import load_dotenv
    load_dotenv()
    
    token = os.getenv('GITHUB_TOKEN')
    df = analyze_issues(token)
    df.to_csv('output/contributor_stats.csv', index=False)
    print("Analysis completed and saved to output/contributor_stats.csv")
