import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as nodejs from 'aws-cdk-lib/aws-lambda-nodejs';
import * as path from 'path';
// import * as sqs from 'aws-cdk-lib/aws-sqs';

export class CdkGithubLeaderboardStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // const leaderboardFunction = new nodejs.NodejsFunction(this, 'LeaderboardFunction', {
    //   runtime: lambda.Runtime.NODEJS_20_X,
    //   entry: path.join(__dirname, '../src/handler.ts'),
    //   handler: 'handler',
    //   timeout: cdk.Duration.minutes(5),
    //   environment: {
    //     GITHUB_TOKEN: process.env.GITHUB_TOKEN || ''
    //   },
    // });
  }
}
