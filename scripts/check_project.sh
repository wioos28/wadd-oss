#!/bin/bash
# check_project.sh - Script kiểm tra lỗi project.pbxproj
# Sử dụng: bash scripts/check_project.sh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_FILE="ProCameraApp.xcodeproj/project.pbxproj"

echo -e "${YELLOW}=== Kiểm tra project.pbxproj ===${NC}"
echo ""

# 1. Kiểm tra file tồn tại
if [ ! -f "$PROJECT_FILE" ]; then
    echo -e "${RED}LỖI: Không tìm thấy file $PROJECT_FILE${NC}"
    exit 1
fi
echo -e "${GREEN}[OK] File $PROJECT_FILE tồn tại${NC}"

# 2. Kiểm tra Git conflict markers
echo ""
echo -e "${YELLOW}--- Kiểm tra Git conflict markers ---${NC}"
if grep -n "<<<<<<\|=======\|>>>>>>>" "$PROJECT_FILE" > /dev/null 2>&1; then
    echo -e "${RED}LỖI: Tìm thấy conflict marker tại:${NC}"
    grep -n "<<<<<<\|=======\|>>>>>>>" "$PROJECT_FILE"
    exit 1
else
    echo -e "${GREEN}[OK] Không có conflict marker${NC}"
fi

# 3. Kiểm tra ID định nghĩa trùng lặp
echo ""
echo -e "${YELLOW}--- Kiểm tra ID định nghĩa trùng lặp ---${NC}"
# Chỉ lấy các dòng bắt đầu bằng ID 8 ký tự hex (định nghĩa object)
DEFINED_IDS=$(grep -E '^\t\t[A-F0-9]{8} /\*' "$PROJECT_FILE" | sed 's/.*\t\([A-F0-9]\{8\}\).*/\1/' | sort)
DUPLICATE_DEFS=$(echo "$DEFINED_IDS" | uniq -d)

if [ -n "$DUPLICATE_DEFS" ]; then
    echo -e "${RED}LỖI: Tìm thấy ID định nghĩa trùng lặp:${NC}"
    for id in $DUPLICATE_DEFS; do
        echo -e "${YELLOW}ID $id được định nghĩa tại:${NC}"
        grep -n "^\t\t$id /\*" "$PROJECT_FILE"
    done
    exit 1
else
    echo -e "${GREEN}[OK] Không có ID định nghĩa trùng lặp${NC}"
fi

# 4. Kiểm tra cấu trúc section
echo ""
echo -e "${YELLOW}--- Kiểm tra cấu trúc section ---${NC}"
SECTIONS=("PBXBuildFile" "PBXFileReference" "PBXFrameworksBuildPhase" "PBXGroup" "PBXNativeTarget" "PBXProject" "PBXResourcesBuildPhase" "PBXSourcesBuildPhase" "XCBuildConfiguration" "XCConfigurationList")

ALL_OK=true
for section in "${SECTIONS[@]}"; do
    BEGIN_COUNT=$(grep -c "Begin $section section" "$PROJECT_FILE" || true)
    END_COUNT=$(grep -c "End $section section" "$PROJECT_FILE" || true)

    if [ "$BEGIN_COUNT" -ne "$END_COUNT" ]; then
        echo -e "${RED}[FAIL] Section $section không khớp (Begin: $BEGIN_COUNT, End: $END_COUNT)${NC}"
        ALL_OK=false
    else
        echo -e "${GREEN}[OK] Section $section${NC}"
    fi
done

if [ "$ALL_OK" = false ]; then
    exit 1
fi

# 5. Kiểm tra braces balance
echo ""
echo -e "${YELLOW}--- Kiểm tra braces balance ---${NC}"
OPEN_BRACES=$(grep -o '{' "$PROJECT_FILE" | wc -l)
CLOSE_BRACES=$(grep -o '}' "$PROJECT_FILE" | wc -l)

if [ "$OPEN_BRACES" -ne "$CLOSE_BRACES" ]; then
    echo -e "${RED}LỖI: Braces không cân bằng (Open: $OPEN_BRACES, Close: $CLOSE_BRACES)${NC}"
    exit 1
fi
echo -e "${GREEN}[OK] Braces cân bằng ($OPEN_BRACES/$CLOSE_BRACES)${NC}"

# 6. Kiểm tra required objects
echo ""
echo -e "${YELLOW}--- Kiểm tra required objects ---${NC}"
REQUIRED_OBJECTS=("rootObject" "mainGroup" "productRefGroup")
for obj in "${REQUIRED_OBJECTS[@]}"; do
    if grep -q "$obj" "$PROJECT_FILE"; then
        echo -e "${GREEN}[OK] Có $obj${NC}"
    else
        echo -e "${RED}[FAIL] Không tìm thấy $obj${NC}"
        exit 1
    fi
done

echo ""
echo -e "${GREEN}=== TẤT CẢ KIỂM TRA ĐÃ PASSED! ===${NC}"
echo -e "${GREEN}File project.pbxproj hợp lệ.${NC}"
