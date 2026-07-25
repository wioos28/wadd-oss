#!/bin/bash
# ============================================================
# Build unsigned IPA for KEApp
# Requirements: macOS with Xcode installed
# ============================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="KEApp"
SCHEME="KEApp"
BUILD_DIR="build/ios"
ARCHIVE_PATH="${BUILD_DIR}/${APP_NAME}.xcarchive"
IPA_PATH="${BUILD_DIR}/${APP_NAME}.ipa"
IOS_DIR="ios-app"

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}  Building unsigned IPA for ${APP_NAME}${NC}"
echo -e "${YELLOW}========================================${NC}"

# Check if running on macOS
if [[ "$(uname)" != "Darwin" ]]; then
    echo -e "${RED}Error: This script must be run on macOS${NC}"
    exit 1
fi

# Check if Xcode is installed
if ! command -v xcodebuild &> /dev/null; then
    echo -e "${RED}Error: Xcode is not installed${NC}"
    exit 1
fi

# Check if ios-app directory exists
if [ ! -d "${IOS_DIR}" ]; then
    echo -e "${RED}Error: ${IOS_DIR} directory not found${NC}"
    exit 1
fi

# Clean previous builds
echo -e "${YELLOW}[1/5] Cleaning previous builds...${NC}"
rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}"

# Resolve SPM dependencies
echo -e "${YELLOW}[2/5] Resolving SPM dependencies...${NC}"
cd "${IOS_DIR}"
swift package resolve
cd ..

# Build archive
echo -e "${YELLOW}[3/5] Building Xcode archive...${NC}"
cd "${IOS_DIR}"
xcodebuild -scheme "${SCHEME}" \
    -destination 'generic/platform=iOS' \
    -configuration Release \
    -archivePath "$(pwd)/../${ARCHIVE_PATH}" \
    CODE_SIGNING_ALLOWED=NO \
    CODE_SIGNING_REQUIRED=NO \
    CODE_SIGN_IDENTITY="" \
    archive
cd ..

# Create Payload directory
echo -e "${YELLOW}[4/5] Creating IPA payload...${NC}"
cd "${BUILD_DIR}"
rm -rf Payload
mkdir -p Payload
cp -r "${APP_NAME}.xcarchive/Products/Applications/${APP_NAME}.app" Payload/

# Create IPA
echo -e "${YELLOW}[5/5] Packaging IPA...${NC}"
rm -f "${APP_NAME}.ipa"
zip -r "${APP_NAME}.ipa" Payload
rm -rf Payload

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  IPA built successfully!${NC}"
echo -e "${GREEN}  Output: ${IPA_PATH}${NC}"
echo -e "${GREEN}========================================${NC}"
