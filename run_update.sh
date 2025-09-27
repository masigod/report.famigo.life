#!/bin/bash

echo "=== Airtable Participants Skin Data Update Script ==="
echo ""
echo "This script will update the skinColor and skinTone fields in the Airtable Participants table"
echo "using data from the Excel file: makeuptest_AP_Bueatylink_20250927.xlsx"
echo ""
echo "Data mapping:"
echo "  - P-ID: Matching key between Excel and Airtable"
echo "  - 밝기판정 → skinColor (1→1(F), 2→2(L), 3→3(LM), 4→4(M), 5→5(MD), 6→6(D), 7→7(R))"
echo "  - 톤 → skinTone (Cool, Neutral, Warm, Olive)"
echo ""

# Check if API key is provided as argument
if [ -z "$1" ]; then
    echo "Please enter your Airtable API key:"
    read -s AIRTABLE_API_KEY
    echo ""
else
    AIRTABLE_API_KEY="$1"
fi

# First run in dry-run mode
echo "Step 1: Running in DRY-RUN mode to preview changes..."
echo "=================================================="
python update_participants_skin_data.py "$AIRTABLE_API_KEY"

echo ""
echo "=================================================="
echo ""
echo "Do you want to proceed with the actual update? (yes/no)"
read -r response

if [[ "$response" == "yes" || "$response" == "YES" || "$response" == "y" || "$response" == "Y" ]]; then
    echo ""
    echo "Step 2: Executing actual updates..."
    echo "=================================================="
    python update_participants_skin_data.py "$AIRTABLE_API_KEY" --execute
    echo ""
    echo "Update complete!"
else
    echo "Update cancelled."
fi