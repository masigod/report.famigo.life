#!/usr/bin/env python3
"""
Fix dashboard to show all 133 participants
"""

import pandas as pd
import json
from pathlib import Path

# Load Excel with 133 participants
df = pd.read_excel('makeuptest_AP_Bueatylink_20250927.xlsx')
print(f"Loaded {len(df)} participants")

# Verify we have 133
assert len(df) == 133, f"Expected 133 participants, got {len(df)}"

# Load existing analysis data
with open('excel_analysis.json', 'r', encoding='utf-8') as f:
    analysis_data = json.load(f)

# Update with all 133 participants
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

analysis_data['total_participants'] = 133
analysis_data['participant_data'] = participant_data

print(f"Updated to {len(participant_data)} participants")

# Save updated analysis
with open('excel_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(analysis_data, f, ensure_ascii=False, indent=2)

# Now update dashboard HTML with embedded data
with open('makeup-test-dashboard.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Create complete image mapping for all 133 participants
image_mapping = {}
for idx, row in df.iterrows():
    aid = row['A-ID']
    pid = row['P-ID']
    name = row['What is your full name? (Please write exactly as shown in your ARC or passport)']

    image_mapping[aid] = {
        'pid': pid,
        'name': name,
        'row': idx + 2,
        'data': {
            'skin_brightness': str(row['밝기판정']) if pd.notna(row['밝기판정']) else '',
            'skin_tone': row['톤'] if pd.notna(row['톤']) else '',
        },
        'images': {}
    }

    # Check for images in organized folder
    face_jpg = Path(f'images_organized_by_aid/{aid}_face_photo.jpg')
    if face_jpg.exists():
        image_mapping[aid]['images']['face_photo'] = f'images_organized_by_aid/{aid}_face_photo.jpg'

    # Check for other images
    for img_type in ['skin_brightness', 'hair', 'eye_color']:
        img_path = Path(f'images_organized_by_aid/{aid}_{img_type}.png')
        if img_path.exists():
            image_mapping[aid]['images'][img_type] = f'images_organized_by_aid/{aid}_{img_type}.png'

# Update the JavaScript data in HTML
import re

# Replace allParticipants
pattern = r'let allParticipants = .*?;'
replacement = f'let allParticipants = {json.dumps(participant_data, ensure_ascii=False)};'
html_content = re.sub(pattern, replacement, html_content, count=1, flags=re.DOTALL)

# Replace analysisData
pattern = r'let analysisData = .*?;'
replacement = f'let analysisData = {json.dumps(analysis_data, ensure_ascii=False)};'
html_content = re.sub(pattern, replacement, html_content, count=1, flags=re.DOTALL)

# Replace imageMapping
pattern = r'let imageMapping = .*?;'
replacement = f'let imageMapping = {json.dumps(image_mapping, ensure_ascii=False)};'
html_content = re.sub(pattern, replacement, html_content, count=1, flags=re.DOTALL)

# Save updated HTML
with open('makeup-test-dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("\n=== Update Complete ===")
print(f"✓ Total participants: 133")
print(f"✓ Dashboard updated with all participant data")
print(f"✓ Image mappings preserved")
print("\nDashboard is ready!")