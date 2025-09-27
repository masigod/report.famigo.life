#!/usr/bin/env python3
"""
Final embed all data directly into makeup-test-dashboard.html
"""

import json
import pandas as pd
from pathlib import Path

# Load Excel data
df = pd.read_excel('makeuptest_AP_Bueatylink_20250927.xlsx')
print(f"Loaded {len(df)} participants")

# Load analysis data
with open('excel_analysis.json', 'r', encoding='utf-8') as f:
    analysis_data = json.load(f)

# Create image mapping with available face images
image_mapping = {}

# Get all A-ID face images
face_images = list(Path('excel_images').glob('A*_face.png'))
face_images.sort()
print(f"Found {len(face_images)} face images")

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

print(f"Mapped {sum(1 for p in image_mapping.values() if p['images'].get('face_photo'))} participants with face photos")

# Read the dashboard HTML
with open('makeup-test-dashboard.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Find where to inject the data (after the variable declarations)
inject_point = "let allParticipants = [];"
if inject_point in html_content:
    # Create the data injection
    data_injection = f"let allParticipants = {json.dumps(analysis_data['participant_data'], ensure_ascii=False)};"
    html_content = html_content.replace(inject_point, data_injection)

inject_point = "let analysisData = null;"
if inject_point in html_content:
    data_injection = f"let analysisData = {json.dumps(analysis_data, ensure_ascii=False)};"
    html_content = html_content.replace(inject_point, data_injection)

inject_point = "let imageMapping = {};"
if inject_point in html_content:
    data_injection = f"let imageMapping = {json.dumps(image_mapping, ensure_ascii=False)};"
    html_content = html_content.replace(inject_point, data_injection)

# Also update the initialization to not fetch the data
html_content = html_content.replace(
    "// Data embedded",
    "// Data already embedded - no fetch needed"
)

# Make sure updateStatistics is called
if "window.addEventListener('DOMContentLoaded'" in html_content:
    # Add updateStatistics() call if not present
    if "updateStatistics();" not in html_content:
        html_content = html_content.replace(
            "displayParticipants(allParticipants);",
            "displayParticipants(allParticipants);\n            updateStatistics();"
        )

# Save the updated dashboard
with open('makeup-test-dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("\nSuccessfully embedded all data into makeup-test-dashboard.html")
print(f"- Total participants: {len(analysis_data['participant_data'])}")
print(f"- Participants with face photos: {sum(1 for p in image_mapping.values() if p['images'].get('face_photo'))}")
print("\nDashboard is ready to use!")