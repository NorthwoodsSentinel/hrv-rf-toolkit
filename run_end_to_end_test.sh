#!/bin/bash
#
# End-to-End Test Script
# ======================
# Tests the complete Polar H10 → HRVisualizer pipeline with synthetic data
#
# Usage: bash run_end_to_end_test.sh
#

set -e  # Exit on error

echo "======================================================================"
echo "POLAR H10 TO HRVISUALIZER - END-TO-END TEST"
echo "======================================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Generate test data
echo -e "${BLUE}Step 1: Generating test data...${NC}"
python3 generate_test_data.py --output test_data/
echo ""

# Step 2: Run converter
echo -e "${BLUE}Step 2: Running converter...${NC}"
python3 polar_to_hrvisualizer.py \
    --rr test_data/test_rr_intervals.csv \
    --breath test_data/test_breath_schedule.csv \
    --output test_data/test_output.txt
echo ""

# Step 3: Validate output
echo -e "${BLUE}Step 3: Validating output...${NC}"

if [ -f "test_data/test_output.txt" ]; then
    echo -e "${GREEN}✅ Output file created successfully${NC}"

    # Check file size
    file_size=$(wc -c < "test_data/test_output.txt")
    if [ $file_size -gt 10000 ]; then
        echo -e "${GREEN}✅ File size OK: $(($file_size / 1024)) KB${NC}"
    else
        echo -e "${YELLOW}⚠️  Warning: File size seems small: $(($file_size / 1024)) KB${NC}"
    fi

    # Check header format
    if grep -q "Client:" "test_data/test_output.txt"; then
        echo -e "${GREEN}✅ Header format correct${NC}"
    else
        echo -e "${YELLOW}⚠️  Warning: Header format may be incorrect${NC}"
    fi

    # Count data lines
    data_lines=$(tail -n +10 "test_data/test_output.txt" | wc -l)
    echo -e "${GREEN}✅ Data lines: $data_lines${NC}"

    # Show first few lines
    echo ""
    echo -e "${BLUE}First 15 lines of output:${NC}"
    head -n 15 "test_data/test_output.txt"
    echo "..."

else
    echo -e "${YELLOW}❌ Error: Output file not created${NC}"
    exit 1
fi

echo ""
echo "======================================================================"
echo -e "${GREEN}✅ END-TO-END TEST COMPLETE!${NC}"
echo "======================================================================"
echo ""
echo "Output file: test_data/test_output.txt"
echo ""
echo "Next steps:"
echo "1. Import test_output.txt into HRVisualizer"
echo "2. Verify RF detection ≈ 5.5 bpm"
echo "3. Check max HRV window around minute 7-8"
echo ""
echo "See test_data/README_TEST_DATA.md for validation criteria"
echo ""
