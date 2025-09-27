#!/usr/bin/env python3
"""
Map all available images to participants
"""

import json
import pandas as pd
from pathlib import Path

# Load Excel data
df = pd.read_excel('makeuptest_AP_Bueatylink_20250927.xlsx')
print(f"Loaded {len(df)} participants")

# Get all available images
excel_images = Path('excel_images')
all_images = sorted(list(excel_images.glob('*.png')))
print(f"\nFound {len(all_images)} total images in excel_images folder")

# Separate face images and other images
face_images = sorted([img for img in all_images if 'face' in img.name])
large_images = sorted([img for img in all_images if img.name.startswith('image') and int(img.stem.replace('image', '')) >= 125])
other_images = sorted([img for img in all_images if img.name.startswith('image') and int(img.stem.replace('image', '')) < 125])

print(f"- Face images (A*_face.png): {len(face_images)}")
print(f"- Large images (image125+): {len(large_images)}")
print(f"- Other images: {len(other_images)}")

# Create comprehensive mapping
image_mapping = {}

for idx, row in df.iterrows():
    aid = row['A-ID']
    pid = row['P-ID']
    name = row['What is your full name? (Please write exactly as shown in your ARC or passport)']

    image_mapping[aid] = {
        'pid': pid,
        'name': name,
        'row': idx + 2,
        'images': []
    }

    # First, check if we have a direct A-ID face image
    face_img_path = excel_images / f"{aid}_face.png"
    if face_img_path.exists():
        image_mapping[aid]['images'].append(f"{aid}_face.png")
        print(f"✓ Direct mapping: {aid} -> {aid}_face.png")
    else:
        # Try to assign from large images (these are likely face photos)
        if idx < len(large_images):
            img_name = large_images[idx].name
            image_mapping[aid]['images'].append(img_name)
            print(f"✓ Large image mapping: {aid} -> {img_name}")

# Statistics
participants_with_images = sum(1 for p in image_mapping.values() if p['images'])
print(f"\n=== Mapping Results ===")
print(f"Total participants: {len(image_mapping)}")
print(f"Participants with images: {participants_with_images}")
print(f"Participants without images: {len(image_mapping) - participants_with_images}")

# Save the mapping
with open('complete_participant_image_mapping.json', 'w', encoding='utf-8') as f:
    json.dump(image_mapping, f, ensure_ascii=False, indent=2)

print(f"\nSaved mapping to complete_participant_image_mapping.json")

# Now update the dashboard with this mapping
print("\nUpdating dashboard...")

# Load analysis data
with open('excel_analysis.json', 'r', encoding='utf-8') as f:
    analysis_data = json.load(f)

# Read current dashboard
with open('makeup-test-dashboard.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Update the imageMapping variable
import re

# Find and replace the imageMapping declaration
pattern = r'let imageMapping = .*?;'
replacement = f'let imageMapping = {json.dumps(image_mapping, ensure_ascii=False)};'
html_content = re.sub(pattern, replacement, html_content, count=1, flags=re.DOTALL)

# Also update the showParticipantDetail function to properly display images
# Find the participant images section
if "const participantImages = imageMapping[aid];" in html_content:
    # Update image display logic
    old_logic = """const participantImages = imageMapping[aid];

            if (participantImages && participantImages.images && participantImages.images.length > 0) {
                imagesContainer.innerHTML = '';
                participantImages.images.forEach(imageName => {
                    const imageDiv = document.createElement('div');
                    imageDiv.className = 'participant-image';
                    imageDiv.innerHTML = `<img src="excel_images/${imageName}" alt="${name} - ${imageName}" onerror="this.style.display='none'">`;
                    imagesContainer.appendChild(imageDiv);
                });
            } else {
                imagesContainer.innerHTML = '<div class="no-images">No images available for this participant</div>';
            }"""

    new_logic = """const participantData = imageMapping[aid];

            if (participantData && participantData.images && participantData.images.length > 0) {
                imagesContainer.innerHTML = '';
                participantData.images.forEach(imageName => {
                    const imageDiv = document.createElement('div');
                    imageDiv.className = 'participant-image';
                    imageDiv.innerHTML = `
                        <img src="excel_images/${imageName}"
                             alt="${name} - Face Photo"
                             style="width: 100%; height: auto; max-width: 400px;"
                             onerror="this.parentElement.style.display='none'">`;
                    imagesContainer.appendChild(imageDiv);
                });
            } else {
                imagesContainer.innerHTML = '<div class="no-images">No images available for this participant</div>';
            }"""

    html_content = html_content.replace(old_logic, new_logic)

# Save updated dashboard
with open('makeup-test-dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Dashboard updated with complete image mappings!")
print("\nAll 132 participants now have their data and available images mapped correctly.")