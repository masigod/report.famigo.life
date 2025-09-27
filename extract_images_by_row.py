#!/usr/bin/env python3
"""
Extract images from Excel with proper row mapping
Using openpyxl to get exact image positions
"""

import os
import shutil
import zipfile
import xml.etree.ElementTree as ET
import pandas as pd
import json
from pathlib import Path
from collections import defaultdict

def extract_images_with_row_mapping(excel_path):
    """Extract images from Excel and map them to specific rows"""

    # Create output directory
    output_dir = Path("excel_images_by_row")
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(exist_ok=True)

    # Read Excel data for participant info
    df = pd.read_excel(excel_path)

    # Create temp directory for extraction
    temp_dir = Path("temp_excel_extract")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

    image_row_mapping = {}
    participant_images = defaultdict(dict)

    try:
        # Extract Excel as ZIP
        with zipfile.ZipFile(excel_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Parse drawing relationships
        drawings_dir = temp_dir / "xl" / "drawings"
        drawing_rels_dir = temp_dir / "xl" / "drawings" / "_rels"

        # Build relationship map (ID to image file)
        rel_to_image = {}
        if drawing_rels_dir.exists():
            for rels_file in drawing_rels_dir.glob("*.xml.rels"):
                tree = ET.parse(rels_file)
                root = tree.getroot()

                namespaces = {'r': 'http://schemas.openxmlformats.org/package/2006/relationships'}

                for rel in root.findall('.//r:Relationship', namespaces):
                    rel_id = rel.get('Id')
                    target = rel.get('Target')

                    if target and '../media/' in target:
                        image_file = target.replace('../media/', '')
                        rel_to_image[rel_id] = image_file
                        print(f"Found relationship: {rel_id} -> {image_file}")

        # Parse drawing files to get cell anchors
        if drawings_dir.exists():
            for drawing_file in drawings_dir.glob("drawing*.xml"):
                print(f"\nProcessing {drawing_file.name}")
                tree = ET.parse(drawing_file)
                root = tree.getroot()

                namespaces = {
                    'xdr': 'http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing',
                    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
                    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
                }

                # Find all anchored images
                for anchor in root.findall('.//xdr:twoCellAnchor', namespaces):
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

                                        # Map to participant (row 2+ are data rows)
                                        if excel_row >= 2:
                                            participant_idx = excel_row - 2
                                            if participant_idx < len(df):
                                                aid = df.iloc[participant_idx]['A-ID']

                                                # Determine image type by column
                                                # Column 21 (V): Skin brightness image
                                                # Column 27 (AB): Face photo
                                                # Column 38 (AM): Hair type image
                                                # Column 40 (AO): Eye color image

                                                image_type = 'unknown'
                                                if excel_col == 21:  # Column V
                                                    image_type = 'skin_brightness'
                                                elif excel_col == 27:  # Column AB
                                                    image_type = 'face_photo'
                                                elif excel_col == 38:  # Column AM
                                                    image_type = 'hair_type'
                                                elif excel_col == 40:  # Column AO
                                                    image_type = 'eye_color'

                                                print(f"  Row {excel_row}, Col {excel_col} ({image_type}): {image_file} -> {aid}")

                                                if aid not in participant_images:
                                                    participant_images[aid] = {
                                                        'name': df.iloc[participant_idx]['What is your full name? (Please write exactly as shown in your ARC or passport)'],
                                                        'pid': df.iloc[participant_idx]['P-ID'],
                                                        'row': excel_row,
                                                        'images': {}
                                                    }

                                                participant_images[aid]['images'][image_type] = image_file

        # Copy actual image files with proper naming
        media_dir = temp_dir / "xl" / "media"
        if media_dir.exists():
            for aid, data in participant_images.items():
                # Create participant directory
                participant_dir = output_dir / aid
                participant_dir.mkdir(exist_ok=True)

                for img_type, img_file in data['images'].items():
                    src_path = media_dir / img_file
                    if src_path.exists():
                        # Copy with descriptive name
                        ext = src_path.suffix
                        dest_name = f"{aid}_{img_type}{ext}"
                        dest_path = participant_dir / dest_name
                        shutil.copy2(src_path, dest_path)

                        # Also copy to main directory with type prefix
                        main_dest = output_dir / dest_name
                        shutil.copy2(src_path, main_dest)

                        print(f"  Copied {img_file} -> {dest_name}")

        # Save mapping
        mapping_output = {
            'participants': {},
            'summary': {
                'total_participants': len(participant_images),
                'participants_with_face_photos': sum(1 for p in participant_images.values() if 'face_photo' in p['images']),
                'participants_with_skin_images': sum(1 for p in participant_images.values() if 'skin_brightness' in p['images']),
                'participants_with_hair_images': sum(1 for p in participant_images.values() if 'hair_type' in p['images']),
                'participants_with_eye_images': sum(1 for p in participant_images.values() if 'eye_color' in p['images'])
            }
        }

        for aid, data in participant_images.items():
            mapping_output['participants'][aid] = {
                'name': data['name'],
                'pid': data['pid'],
                'row': data['row'],
                'images': {
                    img_type: f"{aid}_{img_type}{Path(media_dir / img_file).suffix}"
                    for img_type, img_file in data['images'].items()
                    if (media_dir / img_file).exists()
                }
            }

        with open('excel_row_image_mapping.json', 'w', encoding='utf-8') as f:
            json.dump(mapping_output, f, ensure_ascii=False, indent=2)

        print(f"\n=== Extraction Complete ===")
        print(f"Total participants with images: {len(participant_images)}")
        print(f"Face photos: {mapping_output['summary']['participants_with_face_photos']}")
        print(f"Skin images: {mapping_output['summary']['participants_with_skin_images']}")
        print(f"Hair images: {mapping_output['summary']['participants_with_hair_images']}")
        print(f"Eye images: {mapping_output['summary']['participants_with_eye_images']}")

        return mapping_output

    finally:
        # Cleanup temp directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    excel_path = "makeuptest_AP_Bueatylink_20250927.xlsx"
    mapping = extract_images_with_row_mapping(excel_path)