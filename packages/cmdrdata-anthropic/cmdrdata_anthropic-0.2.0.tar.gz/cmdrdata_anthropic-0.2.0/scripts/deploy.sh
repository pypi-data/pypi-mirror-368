#!/bin/bash
# Deploy script for cmdrdata-anthropic
# Usage: ./scripts/deploy.sh [--test]

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}CmdrData Anthropic SDK Deployment Script${NC}"
echo "========================================="

# Check if we're deploying to test PyPI
TEST_MODE=false
if [ "$1" == "--test" ]; then
    TEST_MODE=true
    echo -e "${YELLOW}Running in TEST mode - will deploy to TestPyPI${NC}"
fi

# Step 1: Clean previous builds
echo -e "\n${YELLOW}Step 1: Cleaning previous builds...${NC}"
rm -rf dist/ build/ *.egg-info/
echo -e "${GREEN}[OK] Clean complete${NC}"

# Step 2: Install/update build tools
echo -e "\n${YELLOW}Step 2: Installing build tools...${NC}"
uv pip install --upgrade build twine
echo -e "${GREEN}[OK] Build tools installed${NC}"

# Step 3: Build the package
echo -e "\n${YELLOW}Step 3: Building package...${NC}"
uv run python -m build
echo -e "${GREEN}[OK] Package built${NC}"

# Step 4: Check the package
echo -e "\n${YELLOW}Step 4: Checking package with twine...${NC}"
uv run twine check dist/*
echo -e "${GREEN}[OK] Package check passed${NC}"

# Step 5: Display package info
echo -e "\n${YELLOW}Step 5: Package information:${NC}"
ls -lh dist/
echo ""

# Step 6: Deploy
if [ "$TEST_MODE" = true ]; then
    echo -e "${YELLOW}Step 6: Deploying to TestPyPI...${NC}"
    echo -e "${YELLOW}Make sure TEST_PYPI_API_TOKEN is set in your environment${NC}"
    
    read -p "Continue with TestPyPI deployment? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        uv run twine upload --repository testpypi dist/* --verbose
        echo -e "${GREEN}[OK] Package deployed to TestPyPI${NC}"
        echo -e "${GREEN}Install with: pip install -i https://test.pypi.org/simple/ cmdrdata-anthropic${NC}"
    else
        echo -e "${RED}Deployment cancelled${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}Step 6: Deploying to PyPI...${NC}"
    echo -e "${RED}WARNING: This will deploy to production PyPI!${NC}"
    
    read -p "Continue with PyPI deployment? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        uv run twine upload dist/*
        echo -e "${GREEN}[OK] Package deployed to PyPI${NC}"
        echo -e "${GREEN}Install with: pip install cmdrdata-anthropic${NC}"
    else
        echo -e "${RED}Deployment cancelled${NC}"
        exit 1
    fi
fi

echo -e "\n${GREEN}Deployment complete!${NC}"