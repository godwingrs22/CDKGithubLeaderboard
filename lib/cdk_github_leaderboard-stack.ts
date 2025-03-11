import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as path from 'path';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as iam from 'aws-cdk-lib/aws-iam';

export class CdkGithubLeaderboardStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const githubTokenSecret = new secretsmanager.Secret(this, 'GitHubTokenSecret', {
      description: 'GitHub Personal Access Token for API access',
      secretName: 'github-token',
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

    // Output the Lambda function ARN
    new cdk.CfnOutput(this, 'CdkGithubLeaderboardFunctionArn', {
      value: cdkGithubLeaderboardFunction.functionArn,
      description: 'ARN of the Python Lambda function',
    });
  }
}
