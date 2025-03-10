import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as path from 'path';
// import * as sqs from 'aws-cdk-lib/aws-sqs';

export class CdkGithubLeaderboardStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const leaderboardFunction = new lambda.Function(this, 'CDKLeaderboardFunction', {
      runtime: lambda.Runtime.NODEJS_22_X,
      handler: 'lambda-handler.handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../src')),
      memorySize: 128,
      timeout: cdk.Duration.seconds(10),
      environment: {
        NODE_OPTIONS: '--enable-source-maps',
        GITHUB_TOKEN: process.env.GITHUB_TOKEN || '',
      },
    });

    new cdk.CfnOutput(this, 'LambdaFunctionArn', {
      value: leaderboardFunction.functionArn,
      description: 'ARN of the Lambda function',
    });
  }
}
