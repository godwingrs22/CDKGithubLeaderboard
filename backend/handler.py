import json
from issue_analyzer import fetch_github_issues

def lambda_handler(event, context):
    try:
        # Call the fetch_github_issues function
        fetch_github_issues()
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Successfully generated GitHub issues report',
                'status': 'success'
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error generating GitHub issues report: {str(e)}',
                'status': 'error'
            })
        }

# For local testing
if __name__ == '__main__':
    lambda_handler({}, None)
