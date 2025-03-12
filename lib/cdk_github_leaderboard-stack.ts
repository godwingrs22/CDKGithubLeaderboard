import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as path from 'path';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as codepipeline from 'aws-cdk-lib/aws-codepipeline';
import * as codepipeline_actions from 'aws-cdk-lib/aws-codepipeline-actions';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import { RemovalPolicy } from 'aws-cdk-lib';
import { S3BucketOrigin } from 'aws-cdk-lib/aws-cloudfront-origins';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as s3_deployment from 'aws-cdk-lib/aws-s3-deployment';
import * as waf from 'aws-cdk-lib/aws-wafv2';

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

    const webAcl = new waf.CfnWebACL(this, 'WebACL', {
      defaultAction: { allow: {} },
      scope: 'CLOUDFRONT',
      visibilityConfig: {
        cloudWatchMetricsEnabled: true,
        metricName: 'WebACLMetrics',
        sampledRequestsEnabled: true,
      },
      rules: [
        // AWS Managed Rules - Common Rule Set
        {
          name: 'AWSManagedRulesCommonRuleSet',
          priority: 1,
          overrideAction: { none: {} },
          statement: {
            managedRuleGroupStatement: {
              vendorName: 'AWS',
              name: 'AWSManagedRulesCommonRuleSet',
            },
          },
          visibilityConfig: {
            cloudWatchMetricsEnabled: true,
            metricName: 'AWSManagedRulesCommonRuleSetMetric',
            sampledRequestsEnabled: true,
          },
        },
        {
          name: 'AWSManagedRulesKnownBadInputsRuleSet',
          priority: 2,
          overrideAction: { none: {} },
          statement: {
            managedRuleGroupStatement: {
              vendorName: 'AWS',
              name: 'AWSManagedRulesKnownBadInputsRuleSet',
            },
          },
          visibilityConfig: {
            cloudWatchMetricsEnabled: true,
            metricName: 'AWSManagedRulesKnownBadInputsRuleSetMetric',
            sampledRequestsEnabled: true,
          },
        },
        // Rate Limiting Rule
        {
          name: 'RateLimitRule',
          priority: 3,
          action: { block: {} },
          statement: {
            rateBasedStatement: {
              limit: 2000, // Requests per 5 minutes per IP
              aggregateKeyType: 'IP',
            },
          },
          visibilityConfig: {
            cloudWatchMetricsEnabled: true,
            metricName: 'RateLimitRuleMetric',
            sampledRequestsEnabled: true,
          },
        },
      ],
    });

    const cloudFrontOAC = new cloudfront.Distribution(this, 'CdkGithubLeaderboardCloudFrontOAC', {
      defaultBehavior: {
        origin: S3BucketOrigin.withOriginAccessControl(websiteBucket),
      },
      defaultRootObject: 'index.html',
      webAclId: webAcl.attrArn,
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
        BUCKET_NAME: websiteBucket.bucketName,
      },
      description: 'Python Lambda function deployed with TypeScript CDK',
    });

     githubTokenSecret.grantRead(cdkGithubLeaderboardFunction);
     websiteBucket.grantWrite(cdkGithubLeaderboardFunction);

    // Create an S3 bucket for the pipeline source (placeholder)
    const sourceBucket = new s3.Bucket(this, 'SourceBucket', {
      removalPolicy: cdk.RemovalPolicy.DESTROY, // For demo purposes only
      versioned: true,
    });

    // Upload the .zip file to the S3 bucket
    new s3_deployment.BucketDeployment(this, 'DeploySourceZip', {
      sources: [s3_deployment.Source.asset(path.join(__dirname, '../pipeline-source-stage'))],
      destinationBucket: sourceBucket,
      destinationKeyPrefix: '', // Upload to the root of the bucket
      retainOnDelete: false, // Delete the file when the stack is deleted
    });

    // Create the CodePipeline
    const pipeline = new codepipeline.Pipeline(this, 'LeaderboardPipeline', {
      pipelineName: 'LeaderboardPipeline',
      restartExecutionOnUpdate: true,
    });

    // Stage 1: Source (S3 placeholder)
    const sourceOutput = new codepipeline.Artifact();
    const sourceAction = new codepipeline_actions.S3SourceAction({
      actionName: 'S3Source',
      bucket: sourceBucket,
      bucketKey: 'source.zip',
      output: sourceOutput,
    });

    pipeline.addStage({
      stageName: 'Source',
      actions: [sourceAction],
    });

    // Stage 2: Invoke Lambda
    const lambdaAction = new codepipeline_actions.LambdaInvokeAction({
      actionName: 'InvokeLambda',
      lambda: cdkGithubLeaderboardFunction,
    });

    // Grant the pipeline permission to invoke the Lambda function
    cdkGithubLeaderboardFunction.grantInvoke(new iam.ServicePrincipal('codepipeline.amazonaws.com'));

    pipeline.addStage({
      stageName: 'InvokeLambda',
      actions: [lambdaAction],
    });

    const invalidateCacheFunction = new lambda.Function(this, 'InvalidateCacheFunction', {
      runtime: lambda.Runtime.PYTHON_3_10, // Or any supported runtime
      handler: 'invalidate_cache.handler',
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
        DISTRIBUTION_ID: cloudFrontOAC.distributionId, // Pass the CloudFront distribution ID
      },
    });
    
    // Grant the Lambda function permission to interact with CodePipeline
    invalidateCacheFunction.addToRolePolicy(
      new iam.PolicyStatement({
        actions: [
          'codepipeline:PutJobSuccessResult',
          'codepipeline:PutJobFailureResult',
        ],
        resources: ['*'], // Grant access to all CodePipeline jobs
      })
    );

    // Grant the Lambda function permission to create CloudFront invalidations
    cloudFrontOAC.grantCreateInvalidation(invalidateCacheFunction);

    // Stage 3: Invalidate CloudFront Cache
    pipeline.addStage({
      stageName: 'InvalidateCache',
      actions: [
        new codepipeline_actions.LambdaInvokeAction({
          actionName: 'InvalidateCache',
          lambda: invalidateCacheFunction,
        }),
      ],
    });

    // Grant the Lambda function permission to interact with CodePipeline
    cdkGithubLeaderboardFunction.addToRolePolicy(
      new iam.PolicyStatement({
        actions: [
          'codepipeline:PutJobSuccessResult',
          'codepipeline:PutJobFailureResult',
        ],
        resources: ['*'], // Grant access to all CodePipeline jobs
      })
    );

    // Create an EventBridge rule to trigger the pipeline
    const rule = new events.Rule(this, 'GithubPipelineTriggerRule', {
      schedule: events.Schedule.rate(cdk.Duration.hours(1)), // Run every hour
    });

    rule.addTarget(
      new targets.CodePipeline(pipeline)
    );

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
