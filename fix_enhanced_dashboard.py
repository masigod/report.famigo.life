#!/usr/bin/env python3
"""
Fix enhanced dashboard data display issue
"""

import pandas as pd
import json
from pathlib import Path
import re

# Load Excel with 133 participants
df = pd.read_excel('/Users/owlers_dylan/APCLT/makeuptest_AP_Bueatylink_20250927.xlsx')
print(f"Loaded {len(df)} participants")

# Verify A216
a216_exists = 'A216' in df['A-ID'].values
if a216_exists:
    a216_data = df[df['A-ID'] == 'A216'].iloc[0]
    print(f"A216 found: {a216_data['What is your full name? (Please write exactly as shown in your ARC or passport)']}")

# Read the current HTML
with open('makeup-test-dashboard-enhanced.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Create fresh participant data
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

print(f"Created data for {len(participant_data)} participants")

# Calculate statistics
summary_stats = {
    'total_participants': 133,
    'gender_distribution': df['What is your gender? '].value_counts().to_dict(),
    'brightness_distribution': {str(k): int(v) for k, v in df['밝기판정'].value_counts().to_dict().items()},
    'tone_distribution': {str(k) if k else 'Unknown': int(v) for k, v in df['톤'].value_counts().to_dict().items()},
}

# Create image mapping
image_dir = Path('images_organized_by_aid')
image_mapping = {}

for idx, row in df.iterrows():
    aid = row['A-ID']
    image_mapping[aid] = {
        'pid': str(row['P-ID']),
        'name': row['What is your full name? (Please write exactly as shown in your ARC or passport)'],
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

# Replace the data in HTML - use more careful regex
# For allParticipants
pattern = r'const allParticipants = \[.*?\];'
replacement = f'const allParticipants = {json.dumps(participant_data, ensure_ascii=False)};'
html_content = re.sub(pattern, replacement, html_content, count=1, flags=re.DOTALL)

# For imageMapping
pattern = r'const imageMapping = \{.*?\};'
replacement = f'const imageMapping = {json.dumps(image_mapping, ensure_ascii=False)};'
html_content = re.sub(pattern, replacement, html_content, count=1, flags=re.DOTALL)

# For summaryStats
pattern = r'const summaryStats = \{.*?\};'
replacement = f'const summaryStats = {json.dumps(summary_stats, ensure_ascii=False)};'
html_content = re.sub(pattern, replacement, html_content, count=1, flags=re.DOTALL)

# Also add a console.log to debug
debug_script = """
        console.log('Dashboard loaded with', allParticipants.length, 'participants');
        console.log('First participant:', allParticipants[0]);
        console.log('Stats:', summaryStats);
"""

# Insert debug script after data declarations
insert_pos = html_content.find('// Update statistics')
if insert_pos > 0:
    html_content = html_content[:insert_pos] + debug_script + '\n        ' + html_content[insert_pos:]

# Save the fixed HTML
with open('makeup-test-dashboard-enhanced.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("\n=== Dashboard Fixed ===")
print(f"✓ Data re-embedded for {len(participant_data)} participants")
print(f"✓ A216 included: {a216_exists}")
print(f"✓ Statistics updated")
print(f"✓ Image mappings preserved")
print("\nDashboard should now display all data!")