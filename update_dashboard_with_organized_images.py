#!/usr/bin/env python3
"""
Update dashboard with images from images_organized_by_aid folder
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

# Get all available images from organized folder
organized_images = Path('images_organized_by_aid')
all_organized_images = list(organized_images.glob('*'))
print(f"\nFound {len(all_organized_images)} total images in images_organized_by_aid folder")

# Create comprehensive mapping with organized images
image_mapping = {}
participants_with_face = 0
participants_with_any_image = 0

for idx, row in df.iterrows():
    aid = row['A-ID']
    pid = row['P-ID']
    name = row['What is your full name? (Please write exactly as shown in your ARC or passport)']

    image_mapping[aid] = {
        'pid': pid,
        'name': name,
        'row': idx + 2,
        'images': {
            'face_photo': None,
            'skin_brightness': None,
            'hair': None,
            'eye_color': None
        }
    }

    # Check for each type of image
    face_jpg = organized_images / f"{aid}_face_photo.jpg"
    face_png = organized_images / f"{aid}_face_photo.png"
    skin_img = organized_images / f"{aid}_skin_brightness.png"
    hair_img = organized_images / f"{aid}_hair.png"
    eye_img = organized_images / f"{aid}_eye_color.png"

    has_any = False

    if face_jpg.exists():
        image_mapping[aid]['images']['face_photo'] = f"images_organized_by_aid/{aid}_face_photo.jpg"
        participants_with_face += 1
        has_any = True
        print(f"✓ {aid}: face_photo.jpg")
    elif face_png.exists():
        image_mapping[aid]['images']['face_photo'] = f"images_organized_by_aid/{aid}_face_photo.png"
        participants_with_face += 1
        has_any = True
        print(f"✓ {aid}: face_photo.png")

    if skin_img.exists():
        image_mapping[aid]['images']['skin_brightness'] = f"images_organized_by_aid/{aid}_skin_brightness.png"
        has_any = True

    if hair_img.exists():
        image_mapping[aid]['images']['hair'] = f"images_organized_by_aid/{aid}_hair.png"
        has_any = True

    if eye_img.exists():
        image_mapping[aid]['images']['eye_color'] = f"images_organized_by_aid/{aid}_eye_color.png"
        has_any = True

    if has_any:
        participants_with_any_image += 1

print(f"\n=== Mapping Results ===")
print(f"Total participants: {len(image_mapping)}")
print(f"Participants with face photos: {participants_with_face}")
print(f"Participants with any images: {participants_with_any_image}")

# Now update the dashboard HTML
print("\nUpdating dashboard...")

with open('makeup-test-dashboard.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Update the imageMapping variable
import re
pattern = r'let imageMapping = .*?;'
replacement = f'let imageMapping = {json.dumps(image_mapping, ensure_ascii=False)};'
html_content = re.sub(pattern, replacement, html_content, count=1, flags=re.DOTALL)

# Update the showParticipantDetail function to properly display all image types
old_images_section = """// Load participant images
            const imagesContainer = document.getElementById('participantImages');
            const participantData = imageMapping[aid];

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

new_images_section = """// Load participant images
            const imagesContainer = document.getElementById('participantImages');
            const participantData = imageMapping[aid];

            if (participantData && participantData.images) {
                let hasImages = false;
                let imagesHTML = '';

                // Display face photo prominently
                if (participantData.images.face_photo) {
                    imagesHTML += `
                        <div class="participant-image" style="grid-column: 1/-1;">
                            <h4 style="margin-bottom: 10px;">Face Photo</h4>
                            <img src="${participantData.images.face_photo}"
                                 alt="${name} - Face Photo"
                                 style="width: 100%; height: auto; max-width: 500px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.2);"
                                 onerror="this.parentElement.style.display='none'">
                        </div>`;
                    hasImages = true;
                }

                // Display other images in a grid
                if (participantData.images.skin_brightness) {
                    imagesHTML += `
                        <div class="participant-image">
                            <h5>Skin Brightness Reference</h5>
                            <img src="${participantData.images.skin_brightness}"
                                 alt="Skin Brightness"
                                 style="width: 100%; height: auto; max-width: 200px;"
                                 onerror="this.style.display='none'">
                        </div>`;
                    hasImages = true;
                }

                if (participantData.images.hair) {
                    imagesHTML += `
                        <div class="participant-image">
                            <h5>Hair Reference</h5>
                            <img src="${participantData.images.hair}"
                                 alt="Hair Reference"
                                 style="width: 100%; height: auto; max-width: 200px;"
                                 onerror="this.style.display='none'">
                        </div>`;
                    hasImages = true;
                }

                if (participantData.images.eye_color) {
                    imagesHTML += `
                        <div class="participant-image">
                            <h5>Eye Color Reference</h5>
                            <img src="${participantData.images.eye_color}"
                                 alt="Eye Color"
                                 style="width: 100%; height: auto; max-width: 200px;"
                                 onerror="this.style.display='none'">
                        </div>`;
                    hasImages = true;
                }

                if (hasImages) {
                    imagesContainer.innerHTML = imagesHTML;
                } else {
                    imagesContainer.innerHTML = '<div class="no-images">No images available for this participant</div>';
                }
            } else {
                imagesContainer.innerHTML = '<div class="no-images">No images available for this participant</div>';
            }"""

html_content = html_content.replace(old_images_section, new_images_section)

# Save updated dashboard
with open('makeup-test-dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("\nDashboard updated successfully!")
print(f"✓ {participants_with_face} participants now have face photos")
print(f"✓ {participants_with_any_image} participants have at least one image")
print("\nDashboard now uses images from images_organized_by_aid folder")