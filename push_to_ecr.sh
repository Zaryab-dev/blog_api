#!/bin/bash
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
export AWS_REGION=us-east-1
export AWS_ACCOUNT_ID=816709078703
export ECR_REPO=django-blog-api
export IMAGE_TAG=v3

echo "╔════════════════════════════════════════════════════════════╗"
echo "║           Push Docker Image to AWS ECR                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "AWS Region:    $AWS_REGION"
echo "AWS Account:   $AWS_ACCOUNT_ID"
echo "ECR Repo:      $ECR_REPO"
echo "Image Tag:     $IMAGE_TAG"
echo ""

# Step 1: Check if local image exists
echo -e "${YELLOW}[1/5] Checking local Docker image...${NC}"
if ! docker images | grep -q "django-blog-api.*test"; then
    echo -e "${RED}✗ Local image 'django-blog-api:test' not found!${NC}"
    echo "Run './test_local_deployment.sh' first to build and test the image."
    exit 1
fi
echo -e "${GREEN}✓ Local image found${NC}"
echo ""

# Step 2: Authenticate to ECR
echo -e "${YELLOW}[2/5] Authenticating to AWS ECR...${NC}"
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin \
  $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com || {
    echo -e "${RED}✗ ECR authentication failed!${NC}"
    echo "Make sure AWS CLI is configured: aws configure"
    exit 1
}
echo -e "${GREEN}✓ Successfully authenticated to ECR${NC}"
echo ""

# Step 3: Create ECR repository if it doesn't exist
echo -e "${YELLOW}[3/5] Checking ECR repository...${NC}"
if aws ecr describe-repositories \
  --repository-names $ECR_REPO \
  --region $AWS_REGION \
  >/dev/null 2>&1; then
    echo -e "${GREEN}✓ ECR repository exists${NC}"
else
    echo "Creating ECR repository..."
    aws ecr create-repository \
      --repository-name $ECR_REPO \
      --region $AWS_REGION \
      --image-scanning-configuration scanOnPush=true || {
        echo -e "${RED}✗ Failed to create ECR repository!${NC}"
        exit 1
    }
    echo -e "${GREEN}✓ ECR repository created${NC}"
fi
echo ""

# Step 4: Tag images
echo -e "${YELLOW}[4/5] Tagging Docker images...${NC}"
ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO"

docker tag django-blog-api:test $ECR_URI:$IMAGE_TAG
docker tag django-blog-api:test $ECR_URI:latest

echo -e "${GREEN}✓ Images tagged:${NC}"
echo "  - $ECR_URI:$IMAGE_TAG"
echo "  - $ECR_URI:latest"
echo ""

# Step 5: Push images to ECR
echo -e "${YELLOW}[5/5] Pushing images to ECR...${NC}"
echo "This may take a few minutes..."
echo ""

echo "Pushing $IMAGE_TAG..."
docker push $ECR_URI:$IMAGE_TAG || {
    echo -e "${RED}✗ Failed to push image!${NC}"
    exit 1
}
echo -e "${GREEN}✓ Pushed $IMAGE_TAG${NC}"
echo ""

echo "Pushing latest..."
docker push $ECR_URI:latest || {
    echo -e "${RED}✗ Failed to push latest tag!${NC}"
    exit 1
}
echo -e "${GREEN}✓ Pushed latest${NC}"
echo ""

# Verify push
echo "Verifying images in ECR..."
aws ecr describe-images \
  --repository-name $ECR_REPO \
  --region $AWS_REGION \
  --image-ids imageTag=$IMAGE_TAG \
  --query 'imageDetails[0].[imageTags[0],imageSizeInBytes,imagePushedAt]' \
  --output table

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║           ✅ IMAGES PUSHED TO ECR SUCCESSFULLY! ✅          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Image URIs:"
echo "  $ECR_URI:$IMAGE_TAG"
echo "  $ECR_URI:latest"
echo ""
echo "Next step: Deploy to App Runner"
echo "Use image: $ECR_URI:$IMAGE_TAG"
echo ""
