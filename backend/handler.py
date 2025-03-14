import json
import os
import datetime
from models import Contributor
from typing import Dict, List, Optional, TypedDict, Any, Set
import boto3
from botocore.exceptions import ClientError
from github_api import GitHubAPI
from discussion_analyzer import DiscussionAnalyzer
from constants import AUTHORS_TO_EXCLUDE

def get_github_token() -> str:
    """
    Retrieve GitHub token from AWS Secrets Manager using the secret ARN
    
    Returns:
        The GitHub token string
    """
    secret_arn = os.environ.get('GITHUB_TOKEN_SECRET_ARN')
    if not secret_arn:
        raise ValueError("GITHUB_TOKEN_SECRET_ARN environment variable is not set")

    region_name = os.environ.get('AWS_REGION')
    if not region_name:
        raise ValueError("AWS_REGION environment variable is not set")

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name,
         # Disable SSL verification for local testing
         #TODO: Remove later after testing
        verify=False
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_arn
        )
        return get_secret_value_response['SecretString']
    except ClientError as e:
        print(f"Error retrieving secret: {str(e)}")
        raise e

def calculate_score(contributor: Contributor) -> int:
    """
    Calculate the score for a contributor
    """
    return contributor['prsMerged'] * 10 + contributor['prsReviewed'] * 8 + contributor['issuesOpened'] * 5 + contributor['discussionsAnswered'] * 3

def is_author_to_exclude(username: str) -> bool:
    """
    Check if a username belongs to an author that should be excluded
    """
    return username in AUTHORS_TO_EXCLUDE

def fetch_all_contributors(github_api: GitHubAPI, org: str, repo: str) -> Set[str]:
    """
    Fetch all contributors with pagination
    """
    pr_contributors = set()
    has_next_page = True
    cursor = None
    
    while has_next_page:
        response = github_api.get_all_contributors(org, repo, cursor)
        search_data = response.get('data', {}).get('search', {})
        
        for pr in search_data.get('nodes', []):
            if pr.get('author', {}).get('login'):
                pr_contributors.add(pr['author']['login'])
            
            for review in pr.get('reviews', {}).get('nodes', []):
                if review.get('author', {}).get('login'):
                    pr_contributors.add(review['author']['login'])

        page_info = search_data.get('pageInfo', {})
        has_next_page = page_info.get('hasNextPage', False)
        cursor = page_info.get('endCursor')            

    #Get the contributors for issues
    issue_contributors = set()
    has_next_page = True
    cursor = None
    while has_next_page:
        response = github_api.get_issues_contributors(org, repo, cursor)
        search_data = response.get('data', {}).get('search', {})

        for issue in search_data.get('nodes', []):
            author = issue.get('author')
            if author and author.get('login'):
                issue_contributors.add(issue['author']['login'])

        page_info = search_data.get('pageInfo', {})
        has_next_page = page_info.get('hasNextPage', False)
        cursor = page_info.get('endCursor')
    
    contributors = pr_contributors.union(issue_contributors)
    return contributors

def fetch_contributions_data(github_api: GitHubAPI, org: str, repo: str, username: str, discussion_analyzer: DiscussionAnalyzer) -> Contributor:
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
        cursor = page_info.get('endCursor')

    # Get opened issues count
    issues_opened = 0
    has_next_page = True
    cursor = None 

    while has_next_page:
        response = github_api.get_issues_opened(org, repo, username, cursor)
        search_data = response.get('data', {}).get('search', {})
        issues_opened += len(search_data.get('nodes', []))

        page_info = search_data.get('pageInfo', {})
        has_next_page = page_info.get('hasNextPage', False)
        cursor = page_info.get('endCursor')


    # Get discussions data
    discussions_answered = discussion_analyzer.get_user_discussion_count(username)

    contributor: Contributor = {
        'username': username,
        'prsMerged': merged_count,
        'prsReviewed': review_count,
        'issuesOpened': issues_opened,
        'discussionsAnswered': discussions_answered,
        'totalScore': 0
    }
    
    contributor['totalScore'] = calculate_score(contributor)
    return contributor

def process_contributions(github_api: GitHubAPI, org: str, repo: str) -> Dict[str, Contributor]:
    """
    Process contributions for all contributors, excluding specific authors
    """
    active_contributors: Dict[str, Contributor] = {}
    
    print(f"Fetching contributors for {org}/{repo}")
    potential_contributors = fetch_all_contributors(github_api, org, repo)
    print(f"Found {len(potential_contributors)} total potential contributors")

    discussion_analyzer = DiscussionAnalyzer(github_api)
    discussion_analyzer.initialize_discussions(org, repo)
    
    for i, username in enumerate(potential_contributors, 1):
        if is_author_to_exclude(username):
            print(f"Skipped {username} (excluded author)")
            continue
            
        print(f"Processing contributor {i}/{len(potential_contributors)}: {username}")
        contributor = fetch_contributions_data(github_api, org, repo, username, discussion_analyzer)
        
        if contributor['prsMerged'] > 0 or contributor['prsReviewed'] > 0 or contributor['issuesOpened'] > 0 or contributor['discussionsAnswered'] > 0:
            active_contributors[username] = contributor
            print(f"Added {username} with {contributor['prsMerged']} PRs merged, {contributor['prsReviewed']} PRs reviewed, {contributor['issuesOpened']} issues opened ,{contributor['discussionsAnswered']} Discussions Answered")
    
    print(f"\nSummary:")
    print(f"Total potential contributors: {len(potential_contributors)}")
    print(f"Active contributors: {len(active_contributors)}")
    return active_contributors

def upload_to_s3(data: dict, bucket: str, key: str) -> bool:
    """
    Upload JSON data to S3 bucket
    
    Args:
        data: Dictionary containing the leaderboard data
        bucket: S3 bucket name
        key: S3 object key (path/filename)
        
    Returns:
        bool: True if upload was successful, False otherwise
    """
    try:
        s3_client = boto3.client('s3')
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(data, default=str),
            ContentType='application/json'
        )
        print(f"Successfully uploaded leaderboard data to s3://{bucket}/{key}")
        return True
    except ClientError as e:
        print(f"Error uploading to S3: {str(e)}")
        return False    

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler function
    """
    print(f"Received event: {json.dumps(event)}")
    
    # Initialize the CodePipeline client
    codepipeline_client = boto3.client('codepipeline')
    job_id = event['CodePipeline.job']['id']
    
    try:
        org = event.get('org', 'aws')
        repo = event.get('repo', 'aws-cdk')
        
        github_token = get_github_token()
            
        github_api = GitHubAPI(github_token)
        print(f"Generating leaderboard for {org}/{repo}")
        
        contributors_dict = process_contributions(github_api, org, repo)
        
        if not contributors_dict:
            print("Warning: No contributors found")
        
        contributors_list = list(contributors_dict.values())
        contributors_list.sort(key=lambda c: c['totalScore'], reverse=True)
        top_contributors = contributors_list[:100]

        leaderboard_data = {
            'lastUpdated': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'contributors': top_contributors,
            'totalContributors': len(contributors_dict)
        }
        
        print("\nLeaderboard Data:")
        print(json.dumps(leaderboard_data, indent=2))
        
        # Upload data to s3
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        s3_bucket = os.environ.get('BUCKET_NAME')

        if not s3_bucket:
            raise ValueError("BUCKET_NAME environment variable is not set")
        
        # Upload file with timestamp
        s3_key = f"leaderboard/leaderboard-{timestamp}.json"
        
        upload_success = upload_to_s3(leaderboard_data, s3_bucket, s3_key)
        if not upload_success:
            print("Warning: Failed to upload leaderboard data to S3")

        # Upload to data folder 
        upload_to_s3(leaderboard_data, s3_bucket, 'data/leaderboard.json')

        # Signal success to CodePipeline
        codepipeline_client.put_job_success_result(jobId=job_id)
        
        # Signal success to CodePipeline
        codepipeline_client.put_job_success_result(jobId=job_id)

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
        
        # Signal failure to CodePipeline
        codepipeline_client.put_job_failure_result(
            jobId=job_id,
            failureDetails={
                'type': 'JobFailed',
                'message': str(e)
            }
        )
        
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
    # Set environment variables for local testing
    os.environ['AWS_REGION'] = 'us-east-1'  # Replace with your region
    # Find the secret ARN in AWS Secrets Manager console
    os.environ['GITHUB_TOKEN_SECRET_ARN'] = 'arn:aws:secretsmanager:us-east-1:916743627080:secret:github-token-zbf68F'

    os.environ['BUCKET_NAME'] = 'sample-bucket'

    event = {
        'org': 'aws',
        'repo': 'aws-cdk',
    }

    result = handler(event, None)
    
    # Print the body
    print(f"\nbody: {result['body']}")