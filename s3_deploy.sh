# Exit on error
set -e

echo "🚀 Starting deployment..."

# Get bucket name from CDK output
BUCKET_NAME=$(aws cloudformation describe-stacks --stack-name CdkGithubLeaderboardStack --query 'Stacks[0].Outputs[?OutputKey==`BucketName`].OutputValue' --output text)

if [ -z "$BUCKET_NAME" ]; then
    echo "❌ Could not find bucket name in CloudFormation outputs"
    exit 1
fi

# Navigate to frontend directory
cd frontend

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

# Navigate back to root
cd ..

# Deploy leaderboard data
echo "📤 Deploying leaderboard data..."
aws s3 cp data/leaderboard.json s3://$BUCKET_NAME/data/

echo "✅ Deployment complete!"
echo "🌎 Website URL: http://$BUCKET_NAME.s3-website-$(aws configure get region).amazonaws.com"