#!/usr/bin/env python3
"""
Extract images from Excel by reading each cell directly using openpyxl
This will properly map images to their exact row positions
"""

import os
import shutil
from pathlib import Path
import pandas as pd
import json
from openpyxl import load_workbook
from openpyxl.drawing.image import Image as XLImage
from PIL import Image
import io

def extract_images_by_cell_position(excel_path):
    """Extract images from Excel cells with exact row mapping"""

    # Create output directory
    output_dir = Path("participant_images")
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(exist_ok=True)

    print(f"Loading workbook: {excel_path}")

    # Load workbook with openpyxl
    wb = load_workbook(excel_path, data_only=True)
    ws = wb.active

    # Also load data with pandas for easy access
    df = pd.read_excel(excel_path)
    print(f"Loaded {len(df)} participants")

    # Get images from worksheet
    if hasattr(ws, '_images'):
        print(f"Found {len(ws._images)} images in worksheet")
        for img in ws._images:
            print(f"  Image at anchor: {img.anchor}")

    # Process images through _drawing if available
    participant_mapping = {}
    image_count = 0

    if hasattr(ws, '_drawing'):
        print(f"\nProcessing images from drawing object...")

        # Get all images with their positions
        for idx, image in enumerate(ws._drawing.images):
            if hasattr(image, 'anchor') and hasattr(image.anchor, '_from'):
                # Get cell position
                from_marker = image.anchor._from
                col = from_marker.col
                row = from_marker.row

                print(f"  Image {idx}: Row {row+1}, Col {col+1}")

                # Row 1 is header, data starts at row 2
                if row >= 1:  # Row 2+ in Excel (0-indexed here)
                    participant_idx = row - 1  # Convert to dataframe index

                    if participant_idx < len(df):
                        aid = df.iloc[participant_idx]['A-ID']
                        pid = df.iloc[participant_idx]['P-ID']
                        name = df.iloc[participant_idx]['What is your full name? (Please write exactly as shown in your ARC or passport)']

                        # Determine image type by column
                        # Adjust these column numbers based on your Excel structure
                        image_type = 'unknown'
                        if col == 21:  # Column V - Skin brightness
                            image_type = 'skin_brightness'
                        elif col == 27:  # Column AB - Face photo
                            image_type = 'face_photo'
                        elif col == 38:  # Column AM - Hair type
                            image_type = 'hair_type'
                        elif col == 40:  # Column AO - Eye color
                            image_type = 'eye_color'

                        # Save image
                        try:
                            img_data = image._data
                            img_filename = f"{aid}_{image_type}_{row+1}_{col+1}.png"
                            img_path = output_dir / img_filename

                            # Save image data
                            if hasattr(img_data, 'read'):
                                img_bytes = img_data.read()
                                img_data.seek(0)  # Reset for potential reuse
                            else:
                                img_bytes = img_data

                            with open(img_path, 'wb') as f:
                                f.write(img_bytes)

                            print(f"    Saved: {img_filename} for {aid} - {name[:30]}...")
                            image_count += 1

                            # Update mapping
                            if aid not in participant_mapping:
                                participant_mapping[aid] = {
                                    'pid': pid,
                                    'name': name,
                                    'row': row + 1,
                                    'images': {}
                                }

                            participant_mapping[aid]['images'][image_type] = img_filename

                        except Exception as e:
                            print(f"    Error saving image: {e}")

    # Alternative method: Extract from image parts
    if image_count == 0:
        print("\nTrying alternative extraction method...")

        # Load the Excel file as a ZIP and extract images
        import zipfile
        import xml.etree.ElementTree as ET

        with zipfile.ZipFile(excel_path, 'r') as zip_ref:
            # Get worksheet XML to find image positions
            sheet_xml = zip_ref.read('xl/worksheets/sheet1.xml')
            sheet_root = ET.fromstring(sheet_xml)

            # Extract all images
            media_files = [f for f in zip_ref.namelist() if f.startswith('xl/media/')]
            print(f"Found {len(media_files)} media files")

            # Extract images with sequential naming by row
            for i, media_file in enumerate(sorted(media_files)):
                img_data = zip_ref.read(media_file)

                # Try to map to participant by order
                if i < len(df):
                    aid = df.iloc[i]['A-ID']
                    pid = df.iloc[i]['P-ID']
                    name = df.iloc[i]['What is your full name? (Please write exactly as shown in your ARC or passport)']

                    # Determine likely type by image number patterns
                    img_filename = f"{aid}_image_{i+1}.png"
                    img_path = output_dir / img_filename

                    with open(img_path, 'wb') as f:
                        f.write(img_data)

                    if aid not in participant_mapping:
                        participant_mapping[aid] = {
                            'pid': pid,
                            'name': name,
                            'row': i + 2,
                            'images': {}
                        }

                    # Estimate image type based on position
                    if i < 132:  # First 132 likely face photos
                        participant_mapping[aid]['images']['face_photo'] = img_filename

                    image_count += 1

    # Save mapping
    output_data = {
        'participants': participant_mapping,
        'total_images_extracted': image_count,
        'total_participants': len(participant_mapping)
    }

    with open('cell_image_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n=== Extraction Complete ===")
    print(f"Extracted {image_count} images")
    print(f"Mapped to {len(participant_mapping)} participants")
    print(f"Images saved to: {output_dir}")
    print(f"Mapping saved to: cell_image_mapping.json")

    # Show sample mapping
    if participant_mapping:
        sample_aid = list(participant_mapping.keys())[0]
        sample = participant_mapping[sample_aid]
        print(f"\nSample mapping for {sample_aid}:")
        print(f"  Name: {sample['name']}")
        print(f"  Row: {sample['row']}")
        print(f"  Images: {sample['images']}")

    return output_data

if __name__ == "__main__":
    excel_path = "makeuptest_AP_Bueatylink_20250927.xlsx"
    mapping = extract_images_by_cell_position(excel_path)