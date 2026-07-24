#!/bin/bash
# build_ipa.sh - Script build và đóng gói .ipa thủ công
# Sử dụng: bash scripts/build_ipa.sh

set -e

echo "🏗️  Bước 1: Archive project..."
xcodebuild -project ProCameraApp.xcodeproj \
  -scheme ProCameraApp \
  -configuration Release \
  -sdk iphoneos \
  CODE_SIGN_IDENTITY="" \
  CODE_SIGNING_REQUIRED=NO \
  CODE_SIGNING_ALLOWED=NO \
  -archivePath build/ProCameraApp.xcarchive \
  archive

echo ""
echo "📦 Bước 2: Đóng gói .ipa thủ công..."

XCARCHIVE_PATH="build/ProCameraApp.xcarchive"
APP_PATH="$XCARCHIVE_PATH/Products/Applications/ProCameraApp.app"

if [ ! -d "$APP_PATH" ]; then
  echo "❌ Lỗi: Không tìm thấy file .app trong thư mục archive!"
  exit 1
fi

mkdir -p Payload
cp -r "$APP_PATH" Payload/
zip -r ProCameraApp.ipa Payload
rm -rf Payload

echo ""
echo "🎉 Hoàn tất! File .ipa: $(pwd)/ProCameraApp.ipa"
