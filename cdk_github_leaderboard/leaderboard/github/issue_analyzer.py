
from typing import Dict
from pathlib import Path
from typing import List, Dict
    if response.status_code != 200:
        raise Exception(f"Query failed with status code: {response.status_code}")
    page_count = 0
    print("\nFetching GitHub issues...")
        page_count += 1
        print(f"\rFetching page {page_count}...", end="", flush=True)
        
        result = run_github_query(
            query.replace("$cursor", f'"{cursor}"' if cursor else "null"), 
            token
        )
        
        if 'errors' in result:
            raise Exception(f"GraphQL Error: {result['errors']}")
            
        result = run_github_query(query.replace("$cursor", f'"{cursor}"' if cursor else "null"), token)
    print("\n\nProcessing data...")
    if df.empty:
        return pd.DataFrame(columns=['author', 'title', 'created_at', 'url'])
        
if __name__ == "__main__":
def handler(event, context):
    """Lambda handler function"""
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Get GitHub token
        token = os.getenv('GITHUB_TOKEN')
        if not token:
            raise ValueError("GITHUB_TOKEN environment variable is not set")
            
        # Create output directory if it doesn't exist
        script_dir = Path(__file__).parent
        output_dir = script_dir.parent.parent.parent / 'output'
        output_dir.mkdir(exist_ok=True)
        
        # Run analysis
        token = os.environ['GITHUB_TOKEN']
        # Generate output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f'cdk_contributors_{timestamp}.csv'
        # Convert to CSV
        output = df.to_csv(index=False)
        # Save to CSV
        df.to_csv(output_file, index=False)
        # You might want to save this to S3 or another storage service
        # Print summary
        print("\nAnalysis Complete!")
        print(f"Total contributors analyzed: {len(df)}")
        print(f"Results saved to: {output_file}")
        
        # Display top contributors
        print("\nTop 10 Contributors:")
        print("-----------------")
        top_10 = df.sort_values('title', ascending=False).head(10)
        for _, row in top_10.iterrows():
            print(f"{row['author']}: {row['title']} issues")
            
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Analysis completed successfully',
                'timestamp': datetime.now().isoformat(),
                'contributor_count': len(df)
            })
        }
        print(f"\nError: {str(e)}")
        raise
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