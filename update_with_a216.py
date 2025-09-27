#!/usr/bin/env python3
"""
Update dashboard with A216 - check both Excel files
"""

import pandas as pd
import json
from pathlib import Path

# Check the Downloads Excel file
downloads_excel = '/Users/owlers_dylan/Downloads/makeuptest_AP_Bueatylink_20250927.xlsx'
local_excel = 'makeuptest_AP_Bueatylink_20250927.xlsx'

print("Checking Excel files:")
df_downloads = pd.read_excel(downloads_excel)
df_local = pd.read_excel(local_excel)

print(f"- Downloads Excel: {len(df_downloads)} participants")
print(f"- Local Excel: {len(df_local)} participants")

# Use the one with more participants
if len(df_downloads) > len(df_local):
    print(f"\nUsing Downloads Excel with {len(df_downloads)} participants")
    df = df_downloads

    # Copy the updated file to local
    import shutil
    shutil.copy2(downloads_excel, local_excel)
    print("✓ Copied updated Excel to local folder")
else:
    df = df_local

# Check for A216
a216_exists = 'A216' in df['A-ID'].values
print(f"\nA216 exists: {a216_exists}")

if a216_exists:
    a216_row = df[df['A-ID'] == 'A216'].iloc[0]
    print(f"A216: {a216_row['What is your full name? (Please write exactly as shown in your ARC or passport)']}")

# Update excel_analysis.json with ALL participants
print(f"\nUpdating data files with {len(df)} participants...")

# Load existing analysis
with open('excel_analysis.json', 'r', encoding='utf-8') as f:
    analysis_data = json.load(f)

# Update participant data
participant_data = []
for idx, row in df.iterrows():
    participant = {}
    for col in df.columns:
        value = row[col]
        if pd.isna(value):
            participant[col] = None
        elif isinstance(value, (int, float)):
            participant[col] = value
        else:
            participant[col] = str(value)
    participant_data.append(participant)

analysis_data['total_participants'] = len(df)
analysis_data['participant_data'] = participant_data

# Update statistics
from collections import Counter

# Recalculate all statistics with 133 participants
analysis_data['summary_stats']['total_participants'] = len(df)

# Update brightness distribution
brightness_counts = df['밝기판정'].value_counts().to_dict()
analysis_data['summary_stats']['brightness_distribution'] = {str(k): v for k, v in brightness_counts.items()}

# Update tone distribution
tone_counts = df['톤'].value_counts().to_dict()
analysis_data['summary_stats']['tone_distribution'] = {str(k): v for k, v in tone_counts.items()}

# Save updated analysis
with open('excel_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(analysis_data, f, ensure_ascii=False, indent=2)

print(f"✓ Updated excel_analysis.json with {len(df)} participants")

# Now update image mapping for A216 if it exists
if a216_exists:
    # Load current image mapping
    with open('complete_participant_image_mapping.json', 'r', encoding='utf-8') as f:
        image_mapping = json.load(f)

    # Add A216 if not exists
    if 'A216' not in image_mapping:
        image_mapping['A216'] = {
            'pid': str(a216_row['P-ID']),
            'name': a216_row['What is your full name? (Please write exactly as shown in your ARC or passport)'],
            'row': len(df) + 1,
            'images': []
        }

        # Check if A216 has images in organized folder
        organized_face = Path('images_organized_by_aid/A216_face_photo.jpg')
        if organized_face.exists():
            image_mapping['A216']['images'] = ['A216_face_photo.jpg']
            print(f"✓ Found face photo for A216")

    # Save updated mapping
    with open('complete_participant_image_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(image_mapping, f, indent=2)

print("\nCompleted! Dashboard data updated with all participants.")