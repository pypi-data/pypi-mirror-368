#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to increment version
increment_version() {
    local version=$1
    local type=${2:-patch}
    
    IFS='.' read -ra ADDR <<< "$version"
    local major=${ADDR[0]}
    local minor=${ADDR[1]}
    local patch=${ADDR[2]}
    
    case $type in
        major)
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        minor)
            minor=$((minor + 1))
            patch=0
            ;;
        patch|*)
            patch=$((patch + 1))
            ;;
    esac
    
    echo "${major}.${minor}.${patch}"
}

echo -e "${BLUE}🚀 miamcpdoc Automated Release Script${NC}"
echo "====================================="

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}❌ Error: pyproject.toml not found. Run this script from the project root.${NC}"
    exit 1
fi

# Check if project name is miamcpdoc
if ! grep -q 'name = "miamcpdoc"' pyproject.toml; then
    echo -e "${RED}❌ Error: This script is for miamcpdoc project only.${NC}"
    exit 1
fi

# Get current version
CURRENT_VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "//' | sed 's/"//')
echo -e "${BLUE}📋 Current version: ${CURRENT_VERSION}${NC}"

# Determine bump type from argument or default to patch
BUMP_TYPE=${1:-patch}
if [[ ! "$BUMP_TYPE" =~ ^(major|minor|patch)$ ]]; then
    echo -e "${YELLOW}⚠️  Invalid bump type '$BUMP_TYPE'. Using 'patch'.${NC}"
    BUMP_TYPE="patch"
fi

# Auto-increment version
NEW_VERSION=$(increment_version "$CURRENT_VERSION" "$BUMP_TYPE")
echo -e "${GREEN}🔢 Auto-bumping ${BUMP_TYPE} version: ${CURRENT_VERSION} → ${NEW_VERSION}${NC}"

# Update version in pyproject.toml
sed -i.bak "s/^version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml
rm pyproject.toml.bak

# Update version in _version.py
echo "__version__ = \"$NEW_VERSION\"" > miamcpdoc/_version.py

echo -e "${GREEN}✅ Version updated to ${NEW_VERSION}${NC}"

# Clean previous builds
echo -e "${BLUE}🧹 Cleaning previous builds...${NC}"
rm -rf dist/ build/ *.egg-info/

# Install build if not available
if ! python -c "import build" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  build module not found. Installing...${NC}"
    pip install build
fi

# Build the package
echo -e "${BLUE}🔨 Building package...${NC}"
python -m build

# Check if build was successful
if [ ! -d "dist" ] || [ -z "$(ls -A dist/)" ]; then
    echo -e "${RED}❌ Error: Build failed - no dist files found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build completed successfully${NC}"
echo -e "${BLUE}📦 Built files:${NC}"
ls -la dist/

# Auto-upload to PyPI (skip confirmation for full automation)
echo -e "${BLUE}🌐 Auto-uploading to PyPI...${NC}"

# Check if twine is installed
if ! command -v twine &> /dev/null; then
    echo -e "${YELLOW}⚠️  twine not found. Installing...${NC}"
    pip install twine
fi

# Upload to PyPI
twine upload dist/*

if [ $? -eq 0 ]; then
    echo -e "${GREEN}🎉 Successfully uploaded miamcpdoc ${NEW_VERSION} to PyPI!${NC}"
    echo -e "${BLUE}📋 You can now install with: pip install miamcpdoc==${NEW_VERSION}${NC}"
else
    echo -e "${RED}❌ Upload failed${NC}"
    exit 1
fi

echo -e "${GREEN}✨ Release process completed!${NC}"