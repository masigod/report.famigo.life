#!/usr/bin/env python3
"""
Update dashboard with ALL images from images_organized_by_aid folder
"""

import pandas as pd
import json
from pathlib import Path

# Load Excel data
df = pd.read_excel('makeuptest_AP_Bueatylink_20250927.xlsx')
print(f"Loaded {len(df)} participants from Excel")

# Directory with organized images
image_dir = Path('images_organized_by_aid')

# Create complete image mapping for ALL participants
image_mapping = {}
image_stats = {
    'face_photo': 0,
    'skin_brightness': 0,
    'hair': 0,
    'eye_color': 0
}

for idx, row in df.iterrows():
    aid = row['A-ID']
    pid = row['P-ID']
    name = row['What is your full name? (Please write exactly as shown in your ARC or passport)']

    image_mapping[aid] = {
        'pid': str(pid),
        'name': name,
        'row': idx + 2,  # Excel row (1-indexed + header)
        'data': {
            'skin_brightness': str(row['밝기판정']) if pd.notna(row['밝기판정']) else '',
            'skin_tone': row['톤'] if pd.notna(row['톤']) else '',
        },
        'images': {}
    }

    # Check for face photo (both .jpg and .jpeg)
    face_jpg = image_dir / f'{aid}_face_photo.jpg'
    face_jpeg = image_dir / f'{aid}_face_photo.jpeg'

    if face_jpg.exists():
        image_mapping[aid]['images']['face_photo'] = f'images_organized_by_aid/{aid}_face_photo.jpg'
        image_stats['face_photo'] += 1
    elif face_jpeg.exists():
        image_mapping[aid]['images']['face_photo'] = f'images_organized_by_aid/{aid}_face_photo.jpeg'
        image_stats['face_photo'] += 1

    # Check for skin brightness
    skin_img = image_dir / f'{aid}_skin_brightness.png'
    if skin_img.exists():
        image_mapping[aid]['images']['skin_brightness'] = f'images_organized_by_aid/{aid}_skin_brightness.png'
        image_stats['skin_brightness'] += 1

    # Check for hair
    hair_img = image_dir / f'{aid}_hair.png'
    if hair_img.exists():
        image_mapping[aid]['images']['hair'] = f'images_organized_by_aid/{aid}_hair.png'
        image_stats['hair'] += 1

    # Check for eye color
    eye_img = image_dir / f'{aid}_eye_color.png'
    if eye_img.exists():
        image_mapping[aid]['images']['eye_color'] = f'images_organized_by_aid/{aid}_eye_color.png'
        image_stats['eye_color'] += 1

print(f"\n=== Image Statistics ===")
print(f"Face photos: {image_stats['face_photo']}")
print(f"Skin brightness: {image_stats['skin_brightness']}")
print(f"Hair references: {image_stats['hair']}")
print(f"Eye color references: {image_stats['eye_color']}")

# Save complete image mapping
with open('complete_participant_image_mapping.json', 'w', encoding='utf-8') as f:
    json.dump(image_mapping, f, ensure_ascii=False, indent=2)

print(f"\nSaved mappings for {len(image_mapping)} participants")

# Now update the dashboard HTML with embedded data
with open('makeup-test-dashboard.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Load analysis data
with open('excel_analysis.json', 'r', encoding='utf-8') as f:
    analysis_data = json.load(f)

# Create participant data
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

# Update the embedded data in HTML
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

print("\n=== Dashboard Updated ===")
print(f"✓ Total participants: {len(df)}")
print(f"✓ Image mappings updated from images_organized_by_aid")
print(f"✓ Dashboard HTML updated with latest data")
print("\nDashboard is ready with all updated images!")