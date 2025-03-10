#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { CdkGithubLeaderboardStack } from '../lib/cdk_github_leaderboard-stack';

const app = new cdk.App();
new CdkGithubLeaderboardStack(app, 'CdkGithubLeaderboardStack', {
  env: { 
    account: process.env.CDK_DEFAULT_ACCOUNT, 
    region: process.env.CDK_DEFAULT_REGION 
  },
});