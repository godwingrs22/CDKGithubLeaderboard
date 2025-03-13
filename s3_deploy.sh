# Exit on error
set -e

echo "🚀 Starting deployment..."

# Get bucket name from CDK output
BUCKET_NAME=$(aws cloudformation describe-stacks --stack-name CdkGithubLeaderboardStack --query 'Stacks[0].Outputs[?OutputKey==`BucketName`].OutputValue' --output text)

CLOUDFRONT_DOMAIN=$(aws cloudformation describe-stacks --stack-name CdkGithubLeaderboardStack --query 'Stacks[0].Outputs[?OutputKey==`CloudfrontDistributionName`].OutputValue' --output text)

# Get CloudFront distribution ID
CLOUDFRONT_ID=$(aws cloudfront list-distributions --query "DistributionList.Items[?DomainName=='$CLOUDFRONT_DOMAIN'].Id" --output text)

if [ -z "$BUCKET_NAME" ]; then
    echo "❌ Could not find bucket name in CloudFormation outputs"
    exit 1
fi

if [ -z "$CLOUDFRONT_ID" ]; then
    echo "❌ Could not find CloudFront distribution ID"
    exit 1
fi

# Navigate to frontend directory
cd frontend/cdk-leaderboard

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build the React app
echo "🔨 Building React app..."
npm run build

# Check if build directory exists
if [ ! -d "build" ]; then
    echo "❌ Build failed - build directory does not exist"
    exit 1
fi

# Deploy to S3
echo "📤 Deploying website to S3..."
aws s3 sync build/ s3://$BUCKET_NAME --delete

# Deploy leaderboard data
echo "📤 Deploying leaderboard data..."
aws s3 cp data/leaderboard.json s3://$BUCKET_NAME/data/

# Create CloudFront invalidation
echo "🔄 Creating CloudFront invalidation..."
aws cloudfront create-invalidation \
    --distribution-id $CLOUDFRONT_ID \
    --paths "/*"

# Navigate back to root
cd ../../

echo "✅ Deployment complete!"
echo "🌎 Website URL: http://$CLOUDFRONT_DOMAIN"