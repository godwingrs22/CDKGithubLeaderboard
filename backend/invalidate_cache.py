import os
import boto3

def handler(event, context):
    codepipeline_client = boto3.client('codepipeline')
    job_id = event['CodePipeline.job']['id']
    
    distribution_id = os.environ['DISTRIBUTION_ID']
    cloudfront = boto3.client('cloudfront')
    
    response = cloudfront.create_invalidation(
        DistributionId=distribution_id,
        InvalidationBatch={
            'Paths': {
                'Quantity': 1,
                'Items': ['/data/leaderboard.json'],
            },
            'CallerReference': str(context.aws_request_id), # Unique reference for the invalidation
        }
    )

    # Signal success to CodePipeline
    codepipeline_client.put_job_success_result(jobId=job_id)
    
    return {
        'statusCode': 200,
        'body': response['Invalidation']['Id'],
    }