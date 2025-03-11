import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as path from 'path';


export class CdkGithubLeaderboardStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const CdkGithubLeaderboardFunction = new lambda.Function(this, 'CdkGithubLeaderboardFunction', {
      runtime: lambda.Runtime.PYTHON_3_10,
      handler: 'handler.handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../lambda'), {
        bundling: {
          image: lambda.Runtime.PYTHON_3_9.bundlingImage,
          command: [
            'bash', '-c',
            'pip install -r requirements.txt -t /asset-output && cp -au . /asset-output'
          ],
        },
      }),
      memorySize: 512,
      timeout: cdk.Duration.seconds(30),
      environment: {
        PYTHONPATH: '/var/runtime:/var/task',
      },
      description: 'Python Lambda function deployed with TypeScript CDK',
    });

    // Output the Lambda function ARN
    new cdk.CfnOutput(this, 'PythonFunctionArn', {
      value: CdkGithubLeaderboardFunction.functionArn,
      description: 'ARN of the Python Lambda function',
    });
  }
}
