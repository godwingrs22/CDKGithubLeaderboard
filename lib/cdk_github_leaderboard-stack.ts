import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as path from 'path';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as s3deploy from 'aws-cdk-lib/aws-s3-deployment';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import { RemovalPolicy } from 'aws-cdk-lib';
import { join } from 'path';
import { S3BucketOrigin } from 'aws-cdk-lib/aws-cloudfront-origins';

export class CdkGithubLeaderboardStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const githubTokenSecret = new secretsmanager.Secret(this, 'GitHubTokenSecret', {
      description: 'GitHub Personal Access Token for API access',
      secretName: 'github-token',
    });

    const bucketName = `cdk-leaderboard-${this.account}-${this.region}`.toLowerCase();

    const websiteBucket = new s3.Bucket(this, 'CdkGithubLeaderboardWebsiteBucket', {
      bucketName: bucketName,
      websiteIndexDocument: 'index.html',
      websiteErrorDocument: 'index.html',
      removalPolicy: RemovalPolicy.DESTROY,
      autoDeleteObjects: true
    });

    websiteBucket.addCorsRule({
      allowedMethods: [s3.HttpMethods.GET],
      allowedOrigins: ['*'],
      allowedHeaders: ['*'],
      maxAge: 3000,
    });

    const cloudFrontOAC = new cloudfront.Distribution(this, 'CdkGithubLeaderboardCloudFrontOAC', {
      defaultBehavior: {
        origin: S3BucketOrigin.withOriginAccessControl(websiteBucket),
      },
      defaultRootObject: 'index.html',
    });

    const cdkGithubLeaderboardFunction = new lambda.Function(this, 'CdkGithubLeaderboardFunction', {
      runtime: lambda.Runtime.PYTHON_3_10,
      handler: 'handler.handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../backend'), {
        bundling: {
          image: lambda.Runtime.PYTHON_3_10.bundlingImage,
          command: [
            'bash', '-c',
            'pip install -r requirements.txt -t /asset-output && cp -au . /asset-output'
          ],
        },
      }),
      memorySize: 512,
      timeout: cdk.Duration.minutes(15),
      environment: {
        PYTHONPATH: '/var/runtime:/var/task',
        GITHUB_TOKEN_SECRET_ARN: githubTokenSecret.secretArn,
      },
      description: 'Python Lambda function deployed with TypeScript CDK',
    });

     githubTokenSecret.grantRead(cdkGithubLeaderboardFunction);

     const rule = new events.Rule(this, 'GithubLambdaTriggerRule', {
       schedule: events.Schedule.rate(cdk.Duration.hours(1)), //configured to run every 1 hour
     });
 
     rule.addTarget(new targets.LambdaFunction(cdkGithubLeaderboardFunction));

    new cdk.CfnOutput(this, 'CloudfrontDistributionName', {
      value: cloudFrontOAC.distributionDomainName,
      description: 'URL for leaderboard website',
    })
     
    new cdk.CfnOutput(this, 'CdkGithubLeaderboardFunctionArn', {
      value: cdkGithubLeaderboardFunction.functionArn,
      description: 'ARN of the Python Lambda function',
    });

    new cdk.CfnOutput(this, 'CdkGithubLeaderboardWebsiteURL', {
      value: websiteBucket.bucketWebsiteUrl,
      description: 'URL for leaderboard website',
    });

    new cdk.CfnOutput(this, 'BucketName', {
      value: websiteBucket.bucketName,
      description: 'Name of S3 bucket',
    });
  }
}
