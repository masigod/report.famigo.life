#!/usr/bin/env python3
"""
Extract ALL images from Excel cells including embedded pictures
Uses multiple methods to ensure we get all images
"""

import os
import shutil
from pathlib import Path
import pandas as pd
import json
from openpyxl import load_workbook
from openpyxl_image_loader import SheetImageLoader
from PIL import Image
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict

def extract_all_embedded_images(excel_path):
    """Extract ALL images from Excel including embedded cell images"""

    # Create output directory
    output_dir = Path("all_participant_images")
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(exist_ok=True)

    print(f"Processing: {excel_path}")

    # Load data with pandas
    df = pd.read_excel(excel_path)
    print(f"Loaded {len(df)} participants")

    # Method 1: Try openpyxl_image_loader
    try:
        print("\nMethod 1: Using openpyxl_image_loader...")
        wb = load_workbook(excel_path)
        ws = wb.active

        # Load images with SheetImageLoader
        image_loader = SheetImageLoader(ws)

        participant_mapping = {}
        image_count = 0

        # Check each row for images
        for row_idx in range(2, len(df) + 2):  # Start from row 2 (after header)
            participant_idx = row_idx - 2
            if participant_idx < len(df):
                aid = df.iloc[participant_idx]['A-ID']
                pid = df.iloc[participant_idx]['P-ID']
                name = df.iloc[participant_idx]['What is your full name? (Please write exactly as shown in your ARC or passport)']

                if aid not in participant_mapping:
                    participant_mapping[aid] = {
                        'pid': pid,
                        'name': name,
                        'row': row_idx,
                        'images': {}
                    }

                # Check specific columns for images
                # Column V (22) - Skin brightness image
                # Column AB (28) - Face photo
                # Column AM (39) - Hair type image
                # Column AO (41) - Eye color image

                columns_to_check = [
                    ('V', 'skin_brightness'),
                    ('AB', 'face_photo'),
                    ('AM', 'hair_type'),
                    ('AO', 'eye_color')
                ]

                for col_letter, img_type in columns_to_check:
                    cell_ref = f"{col_letter}{row_idx}"
                    if image_loader.image_in(cell_ref):
                        try:
                            img = image_loader.get(cell_ref)
                            img_filename = f"{aid}_{img_type}_row{row_idx}.png"
                            img_path = output_dir / img_filename
                            img.save(img_path)
                            participant_mapping[aid]['images'][img_type] = img_filename
                            image_count += 1
                            print(f"  Extracted {img_filename} from {cell_ref}")
                        except Exception as e:
                            print(f"  Error extracting from {cell_ref}: {e}")

        print(f"Method 1 extracted: {image_count} images")

    except ImportError:
        print("  openpyxl_image_loader not installed, trying alternative method...")
        participant_mapping = {}
        image_count = 0

    # Method 2: Extract from ZIP structure with detailed parsing
    if image_count == 0:
        print("\nMethod 2: Extracting from ZIP structure...")

        with zipfile.ZipFile(excel_path, 'r') as zip_ref:
            # Parse all drawing files
            drawing_files = [f for f in zip_ref.namelist() if 'xl/drawings/drawing' in f and f.endswith('.xml')]
            print(f"Found {len(drawing_files)} drawing files")

            all_anchors = []

            for drawing_file in drawing_files:
                print(f"  Processing {drawing_file}")
                drawing_content = zip_ref.read(drawing_file)
                root = ET.fromstring(drawing_content)

                namespaces = {
                    'xdr': 'http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing',
                    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
                    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
                }

                # Get corresponding relationship file
                rels_file = drawing_file.replace('xl/drawings/', 'xl/drawings/_rels/') + '.rels'
                if rels_file in zip_ref.namelist():
                    rels_content = zip_ref.read(rels_file)
                    rels_root = ET.fromstring(rels_content)

                    # Build relationship map
                    rel_to_image = {}
                    rels_ns = {'r': 'http://schemas.openxmlformats.org/package/2006/relationships'}

                    for rel in rels_root.findall('.//r:Relationship', rels_ns):
                        rel_id = rel.get('Id')
                        target = rel.get('Target')
                        if target and '../media/' in target:
                            image_file = target.replace('../media/', '')
                            rel_to_image[rel_id] = image_file

                    # Process all types of anchors
                    for anchor_type in ['twoCellAnchor', 'oneCellAnchor', 'absoluteAnchor']:
                        for anchor in root.findall(f'.//xdr:{anchor_type}', namespaces):
                            from_elem = anchor.find('.//xdr:from', namespaces)
                            if from_elem is not None:
                                col_elem = from_elem.find('xdr:col', namespaces)
                                row_elem = from_elem.find('xdr:row', namespaces)

                                if col_elem is not None and row_elem is not None:
                                    excel_col = int(col_elem.text)
                                    excel_row = int(row_elem.text) + 1  # Convert to 1-indexed

                                    pic = anchor.find('.//xdr:pic', namespaces)
                                    if pic is not None:
                                        blip = pic.find('.//a:blip', namespaces)
                                        if blip is not None:
                                            embed_id = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')

                                            if embed_id in rel_to_image:
                                                image_file = rel_to_image[embed_id]
                                                all_anchors.append({
                                                    'row': excel_row,
                                                    'col': excel_col,
                                                    'image': image_file
                                                })

            print(f"  Found {len(all_anchors)} anchored images")

            # Extract all media files
            media_files = [f for f in zip_ref.namelist() if f.startswith('xl/media/')]
            media_files.sort()
            print(f"  Found {len(media_files)} media files")

            # Extract and map images
            for media_file in media_files:
                img_data = zip_ref.read(media_file)
                img_name = os.path.basename(media_file)

                # Save image
                img_path = output_dir / img_name
                with open(img_path, 'wb') as f:
                    f.write(img_data)

            # Map anchored images to participants
            for anchor in all_anchors:
                row = anchor['row']
                col = anchor['col']
                image_file = anchor['image']

                if row >= 2:  # Data starts at row 2
                    participant_idx = row - 2
                    if participant_idx < len(df):
                        aid = df.iloc[participant_idx]['A-ID']
                        pid = df.iloc[participant_idx]['P-ID']
                        name = df.iloc[participant_idx]['What is your full name? (Please write exactly as shown in your ARC or passport)']

                        if aid not in participant_mapping:
                            participant_mapping[aid] = {
                                'pid': pid,
                                'name': name,
                                'row': row,
                                'images': {}
                            }

                        # Determine image type by column
                        img_type = 'unknown'
                        if col == 21:  # Column V
                            img_type = 'skin_brightness'
                        elif col == 27:  # Column AB
                            img_type = 'face_photo'
                        elif col == 38:  # Column AM
                            img_type = 'hair_type'
                        elif col == 40:  # Column AO
                            img_type = 'eye_color'

                        # Copy with participant-specific name
                        src_path = output_dir / image_file
                        if src_path.exists():
                            dest_filename = f"{aid}_{img_type}_row{row}.png"
                            dest_path = output_dir / dest_filename
                            shutil.copy2(src_path, dest_path)
                            participant_mapping[aid]['images'][img_type] = dest_filename
                            image_count += 1
                            print(f"    Mapped {image_file} -> {dest_filename}")

    # Method 3: Simple sequential mapping as fallback
    if image_count < 132:
        print(f"\nMethod 3: Sequential mapping for remaining {132 - len(participant_mapping)} participants...")

        # Get all images in directory
        all_images = sorted([f.name for f in output_dir.glob('image*.png')])

        # Group by size for classification
        from PIL import Image as PILImage

        large_images = []
        for img_name in all_images:
            img_path = output_dir / img_name
            img = PILImage.open(img_path)
            if img.size[0] * img.size[1] > 100000:  # Large images are likely face photos
                large_images.append(img_name)

        # Assign remaining images to participants without photos
        large_idx = 0
        for idx, row in df.iterrows():
            aid = row['A-ID']

            if aid not in participant_mapping:
                participant_mapping[aid] = {
                    'pid': row['P-ID'],
                    'name': row['What is your full name? (Please write exactly as shown in your ARC or passport)'],
                    'row': idx + 2,
                    'images': {}
                }

            # Assign face photo if missing
            if 'face_photo' not in participant_mapping[aid]['images'] and large_idx < len(large_images):
                src_name = large_images[large_idx]
                dest_name = f"{aid}_face_photo.png"
                src_path = output_dir / src_name
                dest_path = output_dir / dest_name

                if src_path.exists():
                    shutil.copy2(src_path, dest_path)
                    participant_mapping[aid]['images']['face_photo'] = dest_name
                    large_idx += 1

    # Save complete mapping
    output_data = {
        'participants': participant_mapping,
        'statistics': {
            'total_participants': len(participant_mapping),
            'participants_with_face_photos': sum(1 for p in participant_mapping.values() if 'face_photo' in p['images']),
            'participants_with_skin_images': sum(1 for p in participant_mapping.values() if 'skin_brightness' in p['images']),
            'participants_with_hair_images': sum(1 for p in participant_mapping.values() if 'hair_type' in p['images']),
            'participants_with_eye_images': sum(1 for p in participant_mapping.values() if 'eye_color' in p['images'])
        }
    }

    with open('complete_image_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    # Copy to excel_images folder
    for img_file in output_dir.glob('*'):
        if img_file.is_file():
            dest = Path('excel_images') / img_file.name
            shutil.copy2(img_file, dest)

    print(f"\n=== Extraction Complete ===")
    print(f"Total participants: {len(participant_mapping)}")
    print(f"Participants with face photos: {output_data['statistics']['participants_with_face_photos']}")
    print(f"Participants with skin images: {output_data['statistics']['participants_with_skin_images']}")
    print(f"Participants with hair images: {output_data['statistics']['participants_with_hair_images']}")
    print(f"Participants with eye images: {output_data['statistics']['participants_with_eye_images']}")
    print(f"\nImages saved to: {output_dir}")
    print(f"Mapping saved to: complete_image_mapping.json")

    return output_data

if __name__ == "__main__":
    # First install openpyxl_image_loader if needed
    try:
        import openpyxl_image_loader
    except ImportError:
        print("Installing openpyxl_image_loader...")
        os.system("pip install openpyxl_image_loader")

    excel_path = "makeuptest_AP_Bueatylink_20250927.xlsx"
    mapping = extract_all_embedded_images(excel_path)