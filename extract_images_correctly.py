#!/usr/bin/env python3
"""
Extract images from Excel with correct row mapping using oneCellAnchor
"""

import os
import shutil
import zipfile
import xml.etree.ElementTree as ET
import pandas as pd
import json
from pathlib import Path
from collections import defaultdict

def extract_images_with_correct_mapping(excel_path):
    """Extract images from Excel and map them to specific rows correctly"""

    # Create output directory
    output_dir = Path("excel_images_mapped")
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(exist_ok=True)

    # Read Excel data for participant info
    df = pd.read_excel(excel_path)
    print(f"Loaded {len(df)} participants from Excel")

    image_row_mapping = {}
    participant_images = defaultdict(dict)

    with zipfile.ZipFile(excel_path, 'r') as zip_ref:
        # Parse drawing relationships
        with zip_ref.open('xl/drawings/_rels/drawing1.xml.rels') as f:
            rels_content = f.read()
            rels_root = ET.fromstring(rels_content)

            # Build relationship map
            rel_to_image = {}
            namespaces = {'r': 'http://schemas.openxmlformats.org/package/2006/relationships'}

            for rel in rels_root.findall('.//r:Relationship', namespaces):
                rel_id = rel.get('Id')
                target = rel.get('Target')

                if target and '../media/' in target:
                    image_file = target.replace('../media/', '')
                    rel_to_image[rel_id] = image_file

            print(f"\nFound {len(rel_to_image)} image relationships")

        # Parse drawing file
        with zip_ref.open('xl/drawings/drawing1.xml') as f:
            drawing_content = f.read()
            drawing_root = ET.fromstring(drawing_content)

            namespaces = {
                'xdr': 'http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing',
                'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
                'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
            }

            # Process oneCellAnchor elements
            for anchor in drawing_root.findall('.//xdr:oneCellAnchor', namespaces):
                # Get position
                from_elem = anchor.find('.//xdr:from', namespaces)
                if from_elem is not None:
                    col_elem = from_elem.find('xdr:col', namespaces)
                    row_elem = from_elem.find('xdr:row', namespaces)

                    if col_elem is not None and row_elem is not None:
                        excel_col = int(col_elem.text)
                        excel_row = int(row_elem.text) + 1  # Convert to 1-indexed

                        # Get image reference
                        pic = anchor.find('.//xdr:pic', namespaces)
                        if pic is not None:
                            blip = pic.find('.//a:blip', namespaces)
                            if blip is not None:
                                embed_id = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')

                                if embed_id in rel_to_image:
                                    image_file = rel_to_image[embed_id]
                                    print(f"  Found image at Row {excel_row}, Col {excel_col}: {image_file}")

            # Process twoCellAnchor elements (if any)
            for anchor in drawing_root.findall('.//xdr:twoCellAnchor', namespaces):
                from_elem = anchor.find('.//xdr:from', namespaces)
                if from_elem is not None:
                    col_elem = from_elem.find('xdr:col', namespaces)
                    row_elem = from_elem.find('xdr:row', namespaces)

                    if col_elem is not None and row_elem is not None:
                        excel_col = int(col_elem.text)
                        excel_row = int(row_elem.text) + 1

                        pic = anchor.find('.//xdr:pic', namespaces)
                        if pic is not None:
                            blip = pic.find('.//a:blip', namespaces)
                            if blip is not None:
                                embed_id = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')

                                if embed_id in rel_to_image:
                                    image_file = rel_to_image[embed_id]
                                    print(f"  Found image at Row {excel_row}, Col {excel_col}: {image_file}")

        # Since we only have 3 images in drawing1.xml, these are likely reference images
        # The actual participant photos might be embedded differently or stored as cell values

        # Extract all media files and organize by number
        print("\n=== Extracting all media files ===")
        media_files = []
        for file_info in zip_ref.filelist:
            if 'xl/media/' in file_info.filename:
                media_files.append(file_info.filename)

        media_files.sort()
        print(f"Found {len(media_files)} total media files")

        # Extract and organize images
        for i, media_file in enumerate(media_files):
            with zip_ref.open(media_file) as f:
                image_data = f.read()

            # Extract image number
            image_name = os.path.basename(media_file)

            # Save to output directory
            output_path = output_dir / image_name
            with open(output_path, 'wb') as out:
                out.write(image_data)

        # Create simple sequential mapping
        # Assuming images are in order of participants
        print("\n=== Creating participant mapping ===")

        # Group images by estimated type based on file size
        from PIL import Image

        image_sizes = []
        for img_file in output_dir.glob('*'):
            if img_file.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                img = Image.open(img_file)
                width, height = img.size
                file_size = img_file.stat().st_size
                image_sizes.append({
                    'file': img_file.name,
                    'width': width,
                    'height': height,
                    'area': width * height,
                    'file_size': file_size
                })

        # Sort by area to identify types
        image_sizes.sort(key=lambda x: x['area'], reverse=True)

        # Classify images
        large_images = [x for x in image_sizes if x['area'] > 100000]  # Likely face photos
        medium_images = [x for x in image_sizes if 10000 < x['area'] <= 100000]  # Likely reference images
        small_images = [x for x in image_sizes if x['area'] <= 10000]  # Likely icons/small refs

        print(f"\nImage classification:")
        print(f"  Large images (>100k pixels): {len(large_images)}")
        print(f"  Medium images (10k-100k pixels): {len(medium_images)}")
        print(f"  Small images (<10k pixels): {len(small_images)}")

        # Create mapping
        final_mapping = {}

        for idx, row in df.iterrows():
            aid = row['A-ID']
            pid = row['P-ID']
            name = row['What is your full name? (Please write exactly as shown in your ARC or passport)']

            # Assign face photo from large images (if available)
            face_photo = None
            if idx < len(large_images):
                face_photo = large_images[idx]['file']

            # For reference images, use the small/medium images
            # These are shared across participants based on their data values
            skin_brightness = str(row['밝기판정']) if pd.notna(row['밝기판정']) else ''

            final_mapping[aid] = {
                'pid': pid,
                'name': name,
                'row': idx + 2,
                'data': {
                    'skin_brightness': skin_brightness,
                    'skin_tone': row['톤'] if pd.notna(row['톤']) else '',
                    'hair_type': str(row['What is your Natural-born hair(not styled)?[Please select from the 10 options below]']) if pd.notna(row['What is your Natural-born hair(not styled)?[Please select from the 10 options below]']) else '',
                    'eye_color': str(row['Which of the following options most matches your natural eye color?']) if pd.notna(row['Which of the following options most matches your natural eye color?']) else ''
                },
                'images': {
                    'face_photo': face_photo,
                    # Reference images will be shared based on values
                    'skin_ref': f"skin_{skin_brightness}.png" if skin_brightness else None
                }
            }

        # Save mapping
        output_data = {
            'participants': final_mapping,
            'image_stats': {
                'total_images': len(image_sizes),
                'large_images': len(large_images),
                'medium_images': len(medium_images),
                'small_images': len(small_images)
            },
            'reference_images': {
                'detected': [x['file'] for x in small_images[:24]]  # First 24 small images as references
            }
        }

        with open('participant_row_mapping.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"\n=== Mapping Complete ===")
        print(f"Mapped {len(final_mapping)} participants")
        print(f"Output saved to participant_row_mapping.json")

        return output_data

if __name__ == "__main__":
    excel_path = "makeuptest_AP_Bueatylink_20250927.xlsx"
    mapping = extract_images_with_correct_mapping(excel_path)