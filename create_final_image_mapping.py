#!/usr/bin/env python3
"""
Create final image mapping based on Excel data and image analysis
"""

import pandas as pd
import json
import os
from PIL import Image

def create_final_mapping():
    """Create the final participant to image mapping"""

    # Read Excel data
    df = pd.read_excel('makeuptest_AP_Bueatylink_20250927.xlsx')

    # Load image type mapping
    with open('image_type_mapping.json', 'r') as f:
        image_types = json.load(f)

    # Get image sizes
    image_sizes = {}
    for img_file in os.listdir('excel_images'):
        if img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
            img_path = os.path.join('excel_images', img_file)
            try:
                img = Image.open(img_path)
                width, height = img.size
                image_sizes[img_file] = {
                    'width': width,
                    'height': height,
                    'area': width * height
                }
            except:
                pass

    # Sort images by size to identify individual photos
    sorted_images = sorted(image_sizes.items(), key=lambda x: x[1]['area'], reverse=True)

    # Top 132 largest images are likely individual face photos
    individual_photos = [img[0] for img in sorted_images[:132]]

    # Small images are references
    reference_images = [img[0] for img in sorted_images[132:]]

    # Create participant mapping
    final_mapping = {}

    for idx, row in df.iterrows():
        aid = row['A-ID']
        pid = row['P-ID']
        name = row['What is your full name? (Please write exactly as shown in your ARC or passport)']

        # Assign individual photo (from large images)
        face_photo = individual_photos[idx] if idx < len(individual_photos) else None

        # Get data values
        skin_brightness = str(row['밝기판정']) if pd.notna(row['밝기판정']) else ''
        skin_tone = row['톤'] if pd.notna(row['톤']) else ''
        hair_type = str(row['What is your Natural-born hair(not styled)?[Please select from the 10 options below]']) if pd.notna(row['What is your Natural-born hair(not styled)?[Please select from the 10 options below]']) else ''
        eye_color = str(row['Which of the following options most matches your natural eye color?']) if pd.notna(row['Which of the following options most matches your natural eye color?']) else ''

        # Map reference images based on values
        # Use first 7 small images for skin colors
        skin_ref_map = {
            '1': reference_images[0] if len(reference_images) > 0 else None,
            '2': reference_images[1] if len(reference_images) > 1 else None,
            '3': reference_images[2] if len(reference_images) > 2 else None,
            '4': reference_images[3] if len(reference_images) > 3 else None,
            '5': reference_images[4] if len(reference_images) > 4 else None,
            '6': reference_images[5] if len(reference_images) > 5 else None,
            '7': reference_images[6] if len(reference_images) > 6 else None,
        }

        # Use next 10 for hair types (simplified mapping)
        hair_ref_idx = hash(hair_type.lower()) % 10 + 7
        hair_ref = reference_images[hair_ref_idx] if len(reference_images) > hair_ref_idx else None

        # Use next 7 for eye colors (simplified mapping)
        eye_ref_idx = hash(eye_color.lower()) % 7 + 17
        eye_ref = reference_images[eye_ref_idx] if len(reference_images) > eye_ref_idx else None

        final_mapping[aid] = {
            'pid': pid,
            'name': name,
            'data': {
                'skin_brightness': skin_brightness,
                'skin_tone': skin_tone,
                'hair_type': hair_type,
                'eye_color': eye_color,
                'skin_type': row['What is your skin type?'] if pd.notna(row['What is your skin type?']) else '',
                'nationality': row['What is your nationality?'] if pd.notna(row['What is your nationality?']) else '',
                'ethnicity': row['Please select the ethnic group you identify with:'] if pd.notna(row['Please select the ethnic group you identify with:']) else '',
                'birth_year': row['Please enter your 4-digit year of birth(e.g., 1980) '] if pd.notna(row['Please enter your 4-digit year of birth(e.g., 1980) ']) else '',
                'gender': row['What is your gender? '] if pd.notna(row['What is your gender? ']) else '',
                'makeup_frequency': row['How often do you usually apply face makeup? '] if pd.notna(row['How often do you usually apply face makeup? ']) else '',
                'cushion_usage': row['Have you ever used a cushion foundation?'] if pd.notna(row['Have you ever used a cushion foundation?']) else '',
            },
            'images': {
                'face_photo': face_photo,
                'skin_brightness_ref': skin_ref_map.get(skin_brightness),
                'hair_type_ref': hair_ref,
                'eye_color_ref': eye_ref
            }
        }

    # Save the final mapping
    with open('participant_final_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(final_mapping, f, ensure_ascii=False, indent=2)

    print(f"=== Final Mapping Created ===")
    print(f"Total participants: {len(final_mapping)}")
    print(f"Individual photos assigned: {len(individual_photos)}")
    print(f"Reference images identified: {len(reference_images)}")

    # Show sample
    sample_aid = 'A101'
    if sample_aid in final_mapping:
        sample = final_mapping[sample_aid]
        print(f"\nSample participant {sample_aid}:")
        print(f"  Name: {sample['name']}")
        print(f"  Face photo: {sample['images']['face_photo']}")
        print(f"  Skin brightness: {sample['data']['skin_brightness']} -> {sample['images']['skin_brightness_ref']}")
        print(f"  Hair type: {sample['data']['hair_type'][:20]}... -> {sample['images']['hair_type_ref']}")
        print(f"  Eye color: {sample['data']['eye_color']} -> {sample['images']['eye_color_ref']}")

    return final_mapping

if __name__ == "__main__":
    create_final_mapping()