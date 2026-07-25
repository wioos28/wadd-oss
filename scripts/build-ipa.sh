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

# Check if xcodeproj exists
if [ ! -d "${IOS_DIR}/${APP_NAME}.xcodeproj" ]; then
    echo -e "${RED}Error: ${APP_NAME}.xcodeproj not found${NC}"
    exit 1
fi

# Clean previous builds
echo -e "${YELLOW}[1/6] Cleaning previous builds...${NC}"
rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}"

# Resolve SPM dependencies
echo -e "${YELLOW}[2/6] Resolving SPM dependencies...${NC}"
cd "${IOS_DIR}"
swift package resolve
cd ..

# Build archive with verbose output
echo -e "${YELLOW}[3/6] Building Xcode archive (this may take a while)...${NC}"
cd "${IOS_DIR}"
xcodebuild -project "${APP_NAME}.xcodeproj" \
    -scheme "${SCHEME}" \
    -destination 'generic/platform=iOS' \
    -configuration Release \
    -archivePath "$(pwd)/../${ARCHIVE_PATH}" \
    CODE_SIGNING_ALLOWED=NO \
    CODE_SIGNING_REQUIRED=NO \
    CODE_SIGN_IDENTITY="" \
    archive \
    2>&1 | tee ../build/ios/xcodebuild.log
XCODEBUILD_EXIT=${PIPESTATUS[0]}
cd ..

# Check if archive was created
if [ ! -d "${ARCHIVE_PATH}" ]; then
    echo -e "${RED}Error: Archive was not created. Check build/ios/xcodebuild.log for details${NC}"
    exit 1
fi

# Check if .app exists in archive
APP_PATH="${ARCHIVE_PATH}/Products/Applications/${APP_NAME}.app"
if [ ! -d "${APP_PATH}" ]; then
    echo -e "${RED}Error: ${APP_NAME}.app not found in archive${NC}"
    echo -e "${YELLOW}Archive contents:${NC}"
    ls -la "${ARCHIVE_PATH}/Products/Applications/" 2>/dev/null || echo "No Applications directory"
    exit 1
fi

# Check .app size
echo -e "${YELLOW}[4/6] Checking .app bundle...${NC}"
APP_SIZE=$(du -sh "${APP_PATH}" | cut -f1)
echo -e "  .app bundle size: ${APP_SIZE}"

# Check executable size
EXEC_PATH="${APP_PATH}/${APP_NAME}"
if [ -f "${EXEC_PATH}" ]; then
    EXEC_SIZE=$(ls -lh "${EXEC_PATH}" | awk '{print $5}')
    echo -e "  Executable size: ${EXEC_SIZE}"
else
    echo -e "${RED}Warning: Executable not found at ${EXEC_PATH}${NC}"
    echo -e "${YELLOW}  .app contents:${NC}"
    ls -la "${APP_PATH}/"
fi

# Create Payload directory
echo -e "${YELLOW}[5/6] Creating IPA payload...${NC}"
cd "${BUILD_DIR}"
rm -rf Payload
mkdir -p Payload
cp -r "${APP_NAME}.xcarchive/Products/Applications/${APP_NAME}.app" Payload/

# Create IPA
echo -e "${YELLOW}[6/6] Packaging IPA...${NC}"
rm -f "${APP_NAME}.ipa"
zip -r "${APP_NAME}.ipa" Payload
rm -rf Payload

# Final IPA size
IPA_SIZE=$(ls -lh "${APP_NAME}.ipa" | awk '{print $5}')
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  IPA built successfully!${NC}"
echo -e "${GREEN}  Output: ${IPA_PATH}${NC}"
echo -e "${GREEN}  IPA size: ${IPA_SIZE}${NC}"
echo -e "${GREEN}========================================${NC}"

# Warning if IPA is too small
if [ $(stat -f%z "${APP_NAME}.ipa" 2>/dev/null || stat -c%s "${APP_NAME}.ipa" 2>/dev/null) -lt 1000000 ]; then
    echo -e "${RED}WARNING: IPA is smaller than 1MB. This may indicate a build issue.${NC}"
    echo -e "${YELLOW}Check xcodebuild.log for compilation errors.${NC}"
fi
