#!/usr/bin/env python3
"""
Fix image mapping to ensure correct face photos are associated with participants
"""

import json
import pandas as pd
from pathlib import Path

# Load Excel data
df = pd.read_excel('makeuptest_AP_Bueatylink_20250927.xlsx')
print(f"Loaded {len(df)} participants")

# Load existing analysis data
with open('excel_analysis.json', 'r', encoding='utf-8') as f:
    analysis_data = json.load(f)

# Create correct mapping with available face images
image_mapping = {}

# Get all A-ID face images
face_images = list(Path('excel_images').glob('A*_face.png'))
face_images.sort()
print(f"\nFound {len(face_images)} face images:")
for img in face_images:
    print(f"  - {img.name}")

# Map each participant
for idx, row in df.iterrows():
    aid = row['A-ID']
    pid = row['P-ID']
    name = row['What is your full name? (Please write exactly as shown in your ARC or passport)']

    # Create participant entry
    image_mapping[aid] = {
        'pid': pid,
        'name': name,
        'row': idx + 2,
        'data': {
            'skin_brightness': str(row['밝기판정']) if pd.notna(row['밝기판정']) else '',
            'skin_tone': row['톤'] if pd.notna(row['톤']) else '',
            'hair_type': str(row['What is your Natural-born hair(not styled)?[Please select from the 10 options below]']) if pd.notna(row['What is your Natural-born hair(not styled)?[Please select from the 10 options below]']) else '',
            'eye_color': str(row['Which of the following options most matches your natural eye color?']) if pd.notna(row['Which of the following options most matches your natural eye color?']) else '',
            'nationality': row['What is your nationality?'] if pd.notna(row['What is your nationality?']) else '',
            'ethnicity': row['Please select the ethnic group you identify with:'] if pd.notna(row['Please select the ethnic group you identify with:']) else '',
            'birth_year': str(row['Please enter your 4-digit year of birth(e.g., 1980) ']) if pd.notna(row['Please enter your 4-digit year of birth(e.g., 1980) ']) else '',
            'gender': row['What is your gender? '] if pd.notna(row['What is your gender? ']) else '',
            'makeup_frequency': row['How often do you usually apply face makeup? '] if pd.notna(row['How often do you usually apply face makeup? ']) else '',
            'cushion_usage': row['Have you ever used a cushion foundation?'] if pd.notna(row['Have you ever used a cushion foundation?']) else '',
            'skin_type': row['What is your skin type?'] if pd.notna(row['What is your skin type?']) else '',
            'sunscreen_usage': row['How often do you usually use sunscreen products?'] if pd.notna(row['How often do you usually use sunscreen products?']) else '',
            'set_date': row['setDate'] if pd.notna(row['setDate']) else '',
            'set_time': row['setTime'] if pd.notna(row['setTime']) else ''
        },
        'images': {}
    }

    # Check if we have a face image for this A-ID
    face_img_path = Path('excel_images') / f"{aid}_face.png"
    if face_img_path.exists():
        image_mapping[aid]['images']['face_photo'] = f"{aid}_face.png"
        print(f"✓ Mapped {aid} -> {aid}_face.png")
    else:
        # No direct face image for this participant
        image_mapping[aid]['images']['face_photo'] = None

# Statistics
participants_with_images = sum(1 for p in image_mapping.values() if p['images'].get('face_photo'))
print(f"\n=== Mapping Statistics ===")
print(f"Total participants: {len(image_mapping)}")
print(f"Participants with face photos: {participants_with_images}")
print(f"Participants without photos: {len(image_mapping) - participants_with_images}")

# Save the corrected mapping
with open('corrected_image_mapping.json', 'w', encoding='utf-8') as f:
    json.dump(image_mapping, f, ensure_ascii=False, indent=2)

print(f"\nSaved corrected mapping to corrected_image_mapping.json")

# Now update the dashboard HTML with the corrected mapping
print("\nUpdating dashboard HTML...")

# Read the dashboard template
with open('makeup-test-dashboard-v2.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Inject the corrected data
script_inject = f"""let allParticipants = {json.dumps(analysis_data['participant_data'], ensure_ascii=False)};
        let analysisData = {json.dumps(analysis_data, ensure_ascii=False)};
        let imageMapping = {json.dumps(image_mapping, ensure_ascii=False)};"""

# Replace data section
html_with_data = html_content.replace(
    'let allParticipants = [];\\n        let analysisData = null;\\n        let imageMapping = {};',
    script_inject
)

# Comment out fetch functions
html_with_data = html_with_data.replace(
    'await loadAnalysisData();',
    '// Data embedded'
)
html_with_data = html_with_data.replace(
    'await loadImageMapping();',
    '// Data embedded'
)
html_with_data = html_with_data.replace(
    'await loadParticipantData();',
    'displayParticipants(allParticipants);'
)

# Save the corrected dashboard
with open('makeup-test-dashboard-corrected.html', 'w', encoding='utf-8') as f:
    f.write(html_with_data)

print("Created makeup-test-dashboard-corrected.html with correct image mappings")
print("\nDone! Open makeup-test-dashboard-corrected.html to see the corrected dashboard.")