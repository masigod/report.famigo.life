#!/usr/bin/env python3
"""
Add missing participant A216 from Excel
"""

import pandas as pd
import json
from pathlib import Path

# Load the updated Excel file
excel_path = '/Users/owlers_dylan/Downloads/makeuptest_AP_Bueatylink_20250927.xlsx'
df = pd.read_excel(excel_path)
print(f"Loaded {len(df)} participants from Excel")

# Check if A216 exists
a216_row = df[df['A-ID'] == 'A216']
if not a216_row.empty:
    print("\nFound A216:")
    print(a216_row[['A-ID', 'P-ID', 'What is your full name? (Please write exactly as shown in your ARC or passport)']].to_string())

    # Get A216 data
    participant = a216_row.iloc[0]

    # Print key information
    print(f"\nA216 Details:")
    print(f"- Name: {participant['What is your full name? (Please write exactly as shown in your ARC or passport)']}")
    print(f"- P-ID: {participant['P-ID']}")
    print(f"- Skin Color: {participant['밝기판정']}")
    print(f"- Skin Tone: {participant['톤']}")
    print(f"- Nationality: {participant['What is your nationality?']}")
else:
    print("A216 not found in the Excel file")

# Now update all our data files with the complete 133 participants
print(f"\n=== Updating all data files to include {len(df)} participants ===")

# Re-process all participants (now 133)
all_participants = []
for idx, row in df.iterrows():
    participant_data = {}
    for col in df.columns:
        value = row[col]
        if pd.isna(value):
            participant_data[col] = None
        elif isinstance(value, (int, float)):
            participant_data[col] = value
        else:
            participant_data[col] = str(value)
    all_participants.append(participant_data)

print(f"Processed {len(all_participants)} participants")

# Save to excel_analysis.json (update the existing one)
try:
    with open('excel_analysis.json', 'r', encoding='utf-8') as f:
        analysis_data = json.load(f)

    # Update with new participant count
    analysis_data['total_participants'] = len(all_participants)
    analysis_data['participant_data'] = all_participants

    # Save updated analysis
    with open('excel_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(analysis_data, f, ensure_ascii=False, indent=2)

    print("✓ Updated excel_analysis.json")
except Exception as e:
    print(f"Error updating excel_analysis.json: {e}")

print("\nParticipant A216 has been added to the data files.")
print("Total participants: 133")