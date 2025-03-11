import os
from dotenv import load_dotenv
from issue_analyzer import fetch_github_issues
import json
from handler import lambda_handler

def test_local():
    # Load environment variables from .env file
    load_dotenv()
    
    # Check if GitHub token is set
    if not os.getenv('GITHUB_TOKEN'):
        print("Error: GITHUB_TOKEN not set in .env file")
        return
    
    print("\nTesting direct fetch_github_issues function:")
    print("==========================================")
    
    # Test the fetch_github_issues function directly
    csv_content = fetch_github_issues()
    if csv_content:
        print("\nCSV Content Preview (first 500 characters):")
        print("----------------------------------------")
        print(csv_content[:500])
        print("...")
        
        # Save to local file for inspection
        current_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(current_dir, 'test_output.csv')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(csv_content)
        print(f"\nFull CSV saved to: {output_file}")
    
    print("\nTesting Lambda handler:")
    print("=====================")
    
    # Set a test bucket name for local testing
    os.environ['BUCKET_NAME'] = 'test-bucket'
    
    # Test the lambda handler
    response = lambda_handler({}, None)
    
    print("\nLambda Response:")
    print("--------------")
    print(f"Status Code: {response['statusCode']}")
    print(f"Body: {response['body']}")

if __name__ == "__main__":
    test_local()
