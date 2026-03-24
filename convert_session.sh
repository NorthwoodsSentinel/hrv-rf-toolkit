#!/bin/bash
#
# Quick Session Converter
# =======================
# Easy wrapper for polar_to_hrvisualizer.py
#
# Usage:
#   ./convert_session.sh sessions/RR_20260213_143000.csv sessions/breath_schedule_20260213_143000.csv
#
# Or with auto-matching (if filenames share timestamp):
#   ./convert_session.sh 20260213_143000
#

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       Polar H10 → HRVisualizer Quick Converter        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: python3 not found${NC}"
    echo "Install Python 3 from: https://www.python.org/downloads/"
    exit 1
fi

# Check if converter script exists
if [ ! -f "polar_to_hrvisualizer.py" ]; then
    echo -e "${RED}❌ Error: polar_to_hrvisualizer.py not found${NC}"
    echo "Run this script from the HRVISUALIZER_WITH_SOURCE_CODE directory"
    exit 1
fi

# Create sessions directory if it doesn't exist
mkdir -p sessions

# Parse arguments
if [ $# -eq 1 ]; then
    # Auto-matching mode: user provided just timestamp
    TIMESTAMP=$1
    RR_FILE="sessions/RR_${TIMESTAMP}.csv"
    BREATH_FILE="sessions/breath_schedule_${TIMESTAMP}.csv"
    OUTPUT_FILE="sessions/hrv_session_${TIMESTAMP}.txt"

    echo -e "${BLUE}Auto-matching mode:${NC}"
    echo "  Looking for: RR_${TIMESTAMP}.csv"
    echo "  Looking for: breath_schedule_${TIMESTAMP}.csv"
    echo ""

elif [ $# -eq 2 ]; then
    # Manual mode: user provided both files
    RR_FILE=$1
    BREATH_FILE=$2

    # Extract timestamp from filename for output
    BASENAME=$(basename "$RR_FILE" .csv)
    TIMESTAMP=${BASENAME#RR_}
    OUTPUT_FILE="sessions/hrv_session_${TIMESTAMP}.txt"

    echo -e "${BLUE}Manual mode:${NC}"
    echo "  RR file: $RR_FILE"
    echo "  Breath file: $BREATH_FILE"
    echo ""

elif [ $# -eq 3 ]; then
    # Full manual mode: all three files specified
    RR_FILE=$1
    BREATH_FILE=$2
    OUTPUT_FILE=$3

    echo -e "${BLUE}Full manual mode:${NC}"
    echo "  RR file: $RR_FILE"
    echo "  Breath file: $BREATH_FILE"
    echo "  Output: $OUTPUT_FILE"
    echo ""

else
    echo -e "${YELLOW}Usage:${NC}"
    echo "  Quick mode (auto-match files by timestamp):"
    echo "    $0 TIMESTAMP"
    echo "    Example: $0 20260213_143000"
    echo ""
    echo "  Manual mode (specify RR and breath files):"
    echo "    $0 RR_FILE BREATH_FILE"
    echo "    Example: $0 sessions/RR_20260213_143000.csv sessions/breath_schedule_20260213_143000.csv"
    echo ""
    echo "  Full manual mode (specify all files):"
    echo "    $0 RR_FILE BREATH_FILE OUTPUT_FILE"
    echo ""
    exit 1
fi

# Verify input files exist
if [ ! -f "$RR_FILE" ]; then
    echo -e "${RED}❌ Error: RR interval file not found: $RR_FILE${NC}"
    echo ""
    echo "Available files in sessions/:"
    ls -1 sessions/*.csv 2>/dev/null | head -10 || echo "  (no CSV files found)"
    exit 1
fi

if [ ! -f "$BREATH_FILE" ]; then
    echo -e "${RED}❌ Error: Breathing schedule file not found: $BREATH_FILE${NC}"
    echo ""
    echo "Available files in sessions/:"
    ls -1 sessions/*.csv 2>/dev/null | head -10 || echo "  (no CSV files found)"
    exit 1
fi

# Show file info
echo -e "${GREEN}Input files:${NC}"
echo "  RR intervals:  $(basename "$RR_FILE") ($(wc -l < "$RR_FILE") lines)"
echo "  Breath schedule: $(basename "$BREATH_FILE") ($(wc -l < "$BREATH_FILE") lines)"
echo ""

# Run converter
echo -e "${BLUE}Running converter...${NC}"
echo ""

python3 polar_to_hrvisualizer.py \
    --rr "$RR_FILE" \
    --breath "$BREATH_FILE" \
    --output "$OUTPUT_FILE"

# Check if conversion succeeded
if [ $? -eq 0 ] && [ -f "$OUTPUT_FILE" ]; then
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                 ✅ SUCCESS!                            ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}Output file:${NC} $OUTPUT_FILE"
    echo -e "${GREEN}File size:${NC} $(du -h "$OUTPUT_FILE" | cut -f1)"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Transfer $OUTPUT_FILE to your Windows PC"
    echo "  2. Open HRVisualizer (Nexus.exe)"
    echo "  3. Import the file"
    echo "  4. View your Resonance Frequency results!"
    echo ""
    echo -e "${BLUE}Transfer options:${NC}"
    echo "  • USB drive"
    echo "  • Email to yourself"
    echo "  • Dropbox/Google Drive"
    echo "  • Network share"
    echo ""
else
    echo -e "${RED}❌ Conversion failed${NC}"
    echo "Check error messages above"
    exit 1
fi
