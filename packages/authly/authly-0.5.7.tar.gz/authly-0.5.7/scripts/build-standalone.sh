#!/bin/bash
# Build script for Authly standalone Docker image

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Building Authly Standalone Docker Image${NC}"
echo "========================================="

# Parse arguments
PUSH=false
PLATFORM="linux/amd64"

while [[ $# -gt 0 ]]; do
    case $1 in
        --push)
            PUSH=true
            shift
            ;;
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Usage: $0 [--push] [--platform linux/amd64,linux/arm64]"
            exit 1
            ;;
    esac
done

# Use the optimized Dockerfile.standalone
DOCKERFILE="Dockerfile.standalone"
TAG_SUFFIX=""
echo -e "${YELLOW}Building optimized standalone version${NC}"

# Get version from pyproject.toml
VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
echo -e "Version: ${GREEN}$VERSION${NC}"

# Build the image
echo -e "\n${YELLOW}Building image...${NC}"
docker build \
    --platform "$PLATFORM" \
    -f "$DOCKERFILE" \
    -t "descoped/authly-standalone:latest$TAG_SUFFIX" \
    -t "descoped/authly-standalone:$VERSION$TAG_SUFFIX" \
    .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Build successful${NC}"
else
    echo -e "${RED}✗ Build failed${NC}"
    exit 1
fi

# Show image size
echo -e "\n${YELLOW}Image size:${NC}"
docker images descoped/authly-standalone:latest$TAG_SUFFIX --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}"

# Test the image
echo -e "\n${YELLOW}Testing image...${NC}"

# Clean up any existing test container
docker rm -f authly-standalone-test 2>/dev/null || true

echo "Starting container..."
CONTAINER_ID=$(docker run -d \
    --name authly-standalone-test \
    -p 8000:8000 \
    -e AUTHLY_ADMIN_PASSWORD=test123 \
    "descoped/authly-standalone:latest$TAG_SUFFIX")

# Wait for services to start with retry mechanism
echo "Waiting for services to initialize..."
MAX_ATTEMPTS=40
ATTEMPT=0
HEALTH_CHECK_PASSED=false

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    ATTEMPT=$((ATTEMPT + 1))
    echo -n "Attempt $ATTEMPT/$MAX_ATTEMPTS: "
    
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Health check passed${NC}"
        HEALTH_CHECK_PASSED=true
        break
    else
        echo "Services not ready yet..."
        sleep 2
    fi
done

if [ "$HEALTH_CHECK_PASSED" = true ]; then
    # Try to get API info
    echo -e "\n${YELLOW}Testing API...${NC}"
    curl -s http://localhost:8000/.well-known/openid-configuration | head -5
    echo "..."
    echo -e "${GREEN}✓ API responding${NC}"
else
    echo -e "${RED}✗ Health check failed after $MAX_ATTEMPTS attempts${NC}"
    echo "Container logs (last 50 lines):"
    docker logs --tail 50 authly-standalone-test
    
    # Still cleanup even if health check failed
    docker stop authly-standalone-test > /dev/null 2>&1
    docker rm authly-standalone-test > /dev/null 2>&1
    exit 1
fi

# Cleanup
echo -e "\n${YELLOW}Cleaning up test container...${NC}"
docker stop authly-standalone-test > /dev/null
docker rm authly-standalone-test > /dev/null
echo -e "${GREEN}✓ Cleanup complete${NC}"

# Size analysis
echo -e "\n${YELLOW}Size Analysis:${NC}"
docker history "descoped/authly-standalone:latest$TAG_SUFFIX" --human --format "table {{.CreatedBy}}\t{{.Size}}" | head -20

# Push to Docker Hub if requested
if [ "$PUSH" = true ]; then
    echo -e "\n${YELLOW}Pushing to Docker Hub...${NC}"
    docker push "descoped/authly-standalone:latest$TAG_SUFFIX"
    docker push "descoped/authly-standalone:$VERSION$TAG_SUFFIX"
    echo -e "${GREEN}✓ Push complete${NC}"
fi

echo -e "\n${GREEN}Build complete!${NC}"
echo "To run interactively:"
echo "  docker run -it --rm -p 8000:8000 descoped/authly-standalone:latest$TAG_SUFFIX /bin/bash"
echo ""
echo "To run in background:"
echo "  docker run -d -p 8000:8000 --name authly descoped/authly-standalone:latest$TAG_SUFFIX"