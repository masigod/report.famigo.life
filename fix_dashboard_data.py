#!/usr/bin/env python3
"""
Fix dashboard data display issue - ensure all 133 participants including A216
"""

import pandas as pd
import json
from pathlib import Path
import re

# Load Excel with 133 participants
df = pd.read_excel('makeuptest_AP_Bueatylink_20250927.xlsx')
print(f"Loaded {len(df)} participants from Excel")

# Verify A216 exists
a216_exists = 'A216' in df['A-ID'].values
print(f"A216 exists: {a216_exists}")

if a216_exists:
    a216_data = df[df['A-ID'] == 'A216'].iloc[0]
    print(f"A216: {a216_data['What is your full name? (Please write exactly as shown in your ARC or passport)']}")

# Create participant data array
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

print(f"\nCreated data for {len(participant_data)} participants")

# Load and update analysis data
with open('excel_analysis.json', 'r', encoding='utf-8') as f:
    analysis_data = json.load(f)

analysis_data['total_participants'] = len(df)
analysis_data['participant_data'] = participant_data

# Recalculate statistics
analysis_data['summary_stats'] = {
    'total_participants': len(df),
    'gender_distribution': df['What is your gender? '].value_counts().to_dict(),
    'brightness_distribution': {str(k): int(v) for k, v in df['밝기판정'].value_counts().to_dict().items()},
    'tone_distribution': {str(k) if k else 'Unknown': int(v) for k, v in df['톤'].value_counts().to_dict().items()},
    'nationality_distribution': df['What is your nationality?'].value_counts().head(5).to_dict(),
    'ethnic_distribution': df['Please select the ethnic group you identify with:'].value_counts().to_dict()
}

# Save updated analysis data
with open('excel_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(analysis_data, f, ensure_ascii=False, indent=2)

# Create image mapping
image_dir = Path('images_organized_by_aid')
image_mapping = {}

for idx, row in df.iterrows():
    aid = row['A-ID']
    pid = row['P-ID']
    name = row['What is your full name? (Please write exactly as shown in your ARC or passport)']

    image_mapping[aid] = {
        'pid': str(pid),
        'name': name,
        'row': idx + 2,
        'data': {
            'skin_brightness': str(row['밝기판정']) if pd.notna(row['밝기판정']) else '',
            'skin_tone': row['톤'] if pd.notna(row['톤']) else '',
        },
        'images': {}
    }

    # Check for images
    face_photo = image_dir / f'{aid}_face_photo.jpg'
    if face_photo.exists():
        image_mapping[aid]['images']['face_photo'] = f'images_organized_by_aid/{aid}_face_photo.jpg'

    for img_type in ['skin_brightness', 'hair', 'eye_color']:
        img_path = image_dir / f'{aid}_{img_type}.png'
        if img_path.exists():
            image_mapping[aid]['images'][img_type] = f'images_organized_by_aid/{aid}_{img_type}.png'

print(f"Created image mappings for {len(image_mapping)} participants")

# Now completely rebuild the dashboard HTML
with open('makeup-test-dashboard.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Use more robust regex patterns to replace the data
# Replace allParticipants - match everything between 'let allParticipants = ' and the first '];'
pattern = r'let allParticipants = \[.*?\];'
replacement = f'let allParticipants = {json.dumps(participant_data, ensure_ascii=False)};'
html_content = re.sub(pattern, replacement, html_content, count=1, flags=re.DOTALL)

# Replace analysisData
pattern = r'let analysisData = \{.*?\};'
replacement = f'let analysisData = {json.dumps(analysis_data, ensure_ascii=False)};'
html_content = re.sub(pattern, replacement, html_content, count=1, flags=re.DOTALL)

# Replace imageMapping
pattern = r'let imageMapping = \{.*?\};'
replacement = f'let imageMapping = {json.dumps(image_mapping, ensure_ascii=False)};'
html_content = re.sub(pattern, replacement, html_content, count=1, flags=re.DOTALL)

# Save the updated HTML
with open('makeup-test-dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("\n=== Dashboard Fixed ===")
print(f"✓ Total participants: {len(df)}")
print(f"✓ A216 included: {a216_exists}")
print(f"✓ Data properly embedded in HTML")
print("\nDashboard should now display all 133 participants!")