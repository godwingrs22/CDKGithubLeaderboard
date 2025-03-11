#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { CdkGithubLeaderboardStack } from '../lib/cdk_github_leaderboard-stack';

const app = new cdk.App();

// Get the bucket name suffix from context or use a default value
// This can be provided via cdk deploy --context bucketNameSuffix=myname
const bucketNameSuffix = app.node.tryGetContext('bucketNameSuffix') || 'default';

new CdkGithubLeaderboardStack(app, 'CdkGithubLeaderboardStack', {
  env: { 
    account: process.env.CDK_DEFAULT_ACCOUNT, 
    region: process.env.CDK_DEFAULT_REGION 
  },
  bucketNameSuffix: bucketNameSuffix,
});