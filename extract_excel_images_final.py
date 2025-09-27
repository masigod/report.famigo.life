#!/usr/bin/env python3
"""
Final solution: Extract images from Excel and map them properly by row
"""

import os
import shutil
from pathlib import Path
import pandas as pd
import json
from openpyxl import load_workbook
from PIL import Image
import zipfile
import xml.etree.ElementTree as ET

def extract_and_map_images(excel_path):
    """Extract images and create the best possible mapping"""

    # Create output directory
    output_dir = Path("participant_images_final")
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(exist_ok=True)

    print(f"Processing: {excel_path}")

    # Load data with pandas
    df = pd.read_excel(excel_path)
    print(f"Loaded {len(df)} participants")

    # Load workbook with openpyxl to check for embedded images
    wb = load_workbook(excel_path, data_only=True, keep_links=False)
    ws = wb.active

    # Count images in worksheet
    image_count_in_sheet = 0
    if hasattr(ws, '_images'):
        image_count_in_sheet = len(ws._images)
        print(f"Found {image_count_in_sheet} images embedded in worksheet")

    # Extract all images from the Excel ZIP structure
    participant_mapping = {}
    all_images = []

    with zipfile.ZipFile(excel_path, 'r') as zip_ref:
        # Get all media files
        media_files = [f for f in zip_ref.namelist() if f.startswith('xl/media/')]
        media_files.sort()
        print(f"Found {len(media_files)} total media files in Excel")

        # Extract and analyze each image
        for media_file in media_files:
            img_data = zip_ref.read(media_file)
            img_name = os.path.basename(media_file)

            # Save image
            img_path = output_dir / img_name
            with open(img_path, 'wb') as f:
                f.write(img_data)

            # Analyze image size
            img = Image.open(img_path)
            width, height = img.size

            all_images.append({
                'name': img_name,
                'width': width,
                'height': height,
                'area': width * height,
                'size': len(img_data)
            })

    # Sort images by area to classify them
    all_images.sort(key=lambda x: x['area'], reverse=True)

    # Classify images
    large_images = []  # Face photos (large area)
    medium_images = []  # Reference images (medium area)
    small_images = []  # Icons/small refs (small area)

    for img in all_images:
        if img['area'] > 500000:  # Very large - definitely face photos
            large_images.append(img)
        elif img['area'] > 100000:  # Large - likely face photos
            large_images.append(img)
        elif img['area'] > 10000:  # Medium - reference images
            medium_images.append(img)
        else:  # Small - icons or small references
            small_images.append(img)

    print(f"\nImage classification:")
    print(f"  Large images (likely face photos): {len(large_images)}")
    print(f"  Medium images (likely references): {len(medium_images)}")
    print(f"  Small images (likely icons): {len(small_images)}")

    # Create participant mapping
    # Assign face photos to participants in order
    for idx, row in df.iterrows():
        aid = row['A-ID']
        pid = row['P-ID']
        name = row['What is your full name? (Please write exactly as shown in your ARC or passport)']

        # Get data values
        skin_brightness = str(row['밝기판정']) if pd.notna(row['밝기판정']) else ''
        skin_tone = row['톤'] if pd.notna(row['톤']) else ''
        hair_type = str(row['What is your Natural-born hair(not styled)?[Please select from the 10 options below]']) if pd.notna(row['What is your Natural-born hair(not styled)?[Please select from the 10 options below]']) else ''
        eye_color = str(row['Which of the following options most matches your natural eye color?']) if pd.notna(row['Which of the following options most matches your natural eye color?']) else ''

        # Map face photo
        face_photo = None
        if idx < len(large_images):
            face_photo = large_images[idx]['name']
            # Create a copy with participant ID for clarity
            src_path = output_dir / face_photo
            dest_path = output_dir / f"{aid}_face.png"
            shutil.copy2(src_path, dest_path)
            face_photo = f"{aid}_face.png"

        # Map reference images (these are shared)
        skin_ref = None
        if skin_brightness and small_images:
            # Use consistent mapping for skin brightness
            skin_idx = int(skin_brightness) - 1 if skin_brightness.isdigit() else 0
            if 0 <= skin_idx < len(small_images):
                skin_ref = small_images[skin_idx]['name']

        participant_mapping[aid] = {
            'pid': pid,
            'name': name,
            'row': idx + 2,  # Excel row (1-indexed + header)
            'data': {
                'skin_brightness': skin_brightness,
                'skin_tone': skin_tone,
                'hair_type': hair_type,
                'eye_color': eye_color,
                'nationality': row['What is your nationality?'] if pd.notna(row['What is your nationality?']) else '',
                'ethnicity': row['Please select the ethnic group you identify with:'] if pd.notna(row['Please select the ethnic group you identify with:']) else '',
                'birth_year': str(row['Please enter your 4-digit year of birth(e.g., 1980) ']) if pd.notna(row['Please enter your 4-digit year of birth(e.g., 1980) ']) else '',
                'gender': row['What is your gender? '] if pd.notna(row['What is your gender? ']) else '',
                'makeup_frequency': row['How often do you usually apply face makeup? '] if pd.notna(row['How often do you usually apply face makeup? ']) else '',
                'cushion_usage': row['Have you ever used a cushion foundation?'] if pd.notna(row['Have you ever used a cushion foundation?']) else '',
                'skin_type': row['What is your skin type?'] if pd.notna(row['What is your skin type?']) else ''
            },
            'images': {
                'face_photo': face_photo,
                'skin_brightness_ref': skin_ref
            }
        }

    # Create reference image mapping
    reference_mapping = {
        'skin_brightness': {},
        'hair_types': {},
        'eye_colors': {}
    }

    # Map small images as skin brightness references (1-7)
    for i in range(min(7, len(small_images))):
        reference_mapping['skin_brightness'][str(i+1)] = small_images[i]['name']

    # Save complete mapping
    output_data = {
        'participants': participant_mapping,
        'reference_images': reference_mapping,
        'statistics': {
            'total_participants': len(participant_mapping),
            'total_images': len(all_images),
            'participants_with_photos': sum(1 for p in participant_mapping.values() if p['images']['face_photo']),
            'large_images': len(large_images),
            'medium_images': len(medium_images),
            'small_images': len(small_images)
        }
    }

    with open('final_image_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n=== Mapping Complete ===")
    print(f"Total participants: {len(participant_mapping)}")
    print(f"Participants with face photos: {output_data['statistics']['participants_with_photos']}")
    print(f"Images saved to: {output_dir}")
    print(f"Mapping saved to: final_image_mapping.json")

    # Show sample mapping
    if participant_mapping:
        sample_aid = 'A101'
        if sample_aid in participant_mapping:
            sample = participant_mapping[sample_aid]
            print(f"\nSample mapping for {sample_aid}:")
            print(f"  Name: {sample['name']}")
            print(f"  Row: {sample['row']}")
            print(f"  Face photo: {sample['images']['face_photo']}")
            print(f"  Skin brightness: {sample['data']['skin_brightness']}")
            print(f"  Skin tone: {sample['data']['skin_tone']}")

    # Copy all images to excel_images folder for dashboard
    for img_file in output_dir.glob('*'):
        if img_file.is_file():
            shutil.copy2(img_file, Path('excel_images') / img_file.name)

    print("\nImages also copied to excel_images/ for dashboard use")

    return output_data

if __name__ == "__main__":
    excel_path = "makeuptest_AP_Bueatylink_20250927.xlsx"
    mapping = extract_and_map_images(excel_path)