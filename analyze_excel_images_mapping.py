#!/usr/bin/env python3
"""
Map images to participants by analyzing Excel structure
"""

import pandas as pd
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import json
import re

def analyze_excel_image_mapping(excel_path):
    """Analyze Excel file to map images to rows/participants"""

    # Read Excel data for A-ID mapping
    df = pd.read_excel(excel_path)

    # Create A-ID to row index mapping
    aid_to_row = {}
    for idx, row in df.iterrows():
        aid = row['A-ID']
        aid_to_row[aid] = idx + 2  # Excel rows are 1-indexed, plus header row

    # Extract and analyze Excel structure
    temp_dir = Path("temp_excel_analysis")
    image_mapping = {}

    try:
        with zipfile.ZipFile(excel_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Parse drawing relationships to find image mappings
        drawings_path = temp_dir / "xl" / "drawings"
        if drawings_path.exists():
            for drawing_file in drawings_path.glob("*.xml"):
                tree = ET.parse(drawing_file)
                root = tree.getroot()

                # Find all image references with their cell anchors
                namespaces = {
                    'xdr': 'http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing',
                    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
                    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
                }

                for anchor in root.findall('.//xdr:twoCellAnchor', namespaces):
                    # Get cell position
                    from_elem = anchor.find('.//xdr:from', namespaces)
                    if from_elem is not None:
                        col = from_elem.find('xdr:col', namespaces)
                        row = from_elem.find('xdr:row', namespaces)

                        if col is not None and row is not None:
                            excel_row = int(row.text) + 1  # Convert to 1-indexed
                            excel_col = int(col.text)

                            # Get image reference
                            blip = anchor.find('.//a:blip', namespaces)
                            if blip is not None:
                                embed_id = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')

                                # Map to participant
                                if excel_row >= 2:  # Skip header row
                                    participant_idx = excel_row - 2
                                    if participant_idx < len(df):
                                        aid = df.iloc[participant_idx]['A-ID']
                                        pid = df.iloc[participant_idx]['P-ID']
                                        name = df.iloc[participant_idx]['What is your full name? (Please write exactly as shown in your ARC or passport)']

                                        if aid not in image_mapping:
                                            image_mapping[aid] = {
                                                'row': excel_row,
                                                'pid': pid,
                                                'name': name,
                                                'images': []
                                            }

                                        # Map embed ID to actual image file
                                        image_mapping[aid]['images'].append({
                                            'embed_id': embed_id,
                                            'col': excel_col,
                                            'row': excel_row
                                        })

        # Parse relationships to get actual image files
        rels_path = temp_dir / "xl" / "drawings" / "_rels"
        if rels_path.exists():
            for rels_file in rels_path.glob("*.xml.rels"):
                tree = ET.parse(rels_file)
                root = tree.getroot()

                namespaces = {'r': 'http://schemas.openxmlformats.org/package/2006/relationships'}

                for rel in root.findall('.//r:Relationship', namespaces):
                    rel_id = rel.get('Id')
                    target = rel.get('Target')

                    if target and '../media/' in target:
                        image_name = target.split('/')[-1]

                        # Update all mappings with this relationship
                        for aid, data in image_mapping.items():
                            for img in data['images']:
                                if img['embed_id'] == rel_id:
                                    img['filename'] = image_name

    finally:
        # Clean up temp directory
        if temp_dir.exists():
            import shutil
            shutil.rmtree(temp_dir)

    # Create final mapping
    final_mapping = {}
    for aid, data in image_mapping.items():
        final_mapping[aid] = {
            'pid': data['pid'],
            'name': data['name'],
            'row': data['row'],
            'images': [img.get('filename', f"image{i+1}.png") for i, img in enumerate(data['images']) if img.get('filename')]
        }

    # If mapping is empty, create a simple sequential mapping based on rows
    if not final_mapping:
        print("Complex mapping failed, using simple row-based mapping...")

        # Assume images are in row order
        image_files = sorted(Path('excel_images').glob('*'))
        images_per_participant = len(image_files) // len(df) if len(df) > 0 else 1

        for idx, row in df.iterrows():
            aid = row['A-ID']
            pid = row['P-ID']
            name = row['What is your full name? (Please write exactly as shown in your ARC or passport)']

            # Assign images based on position
            start_idx = idx * images_per_participant
            end_idx = start_idx + images_per_participant

            participant_images = []
            for i in range(start_idx, min(end_idx, len(image_files))):
                participant_images.append(image_files[i].name)

            final_mapping[aid] = {
                'pid': pid,
                'name': name,
                'row': idx + 2,
                'images': participant_images[:4]  # Limit to 4 images per person
            }

    return final_mapping

if __name__ == "__main__":
    excel_path = "makeuptest_AP_Bueatylink_20250927.xlsx"

    print("=== Analyzing Excel Image Mapping ===")
    mapping = analyze_excel_image_mapping(excel_path)

    # Save mapping to JSON
    with open('participant_image_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

    print(f"\nTotal participants with images: {len(mapping)}")

    # Show sample mappings
    sample_count = 0
    for aid, data in mapping.items():
        if sample_count < 5:
            print(f"\n{aid}:")
            print(f"  Name: {data['name']}")
            print(f"  P-ID: {data['pid']}")
            print(f"  Row: {data['row']}")
            print(f"  Images: {data['images'][:2]}...")  # Show first 2 images
            sample_count += 1

    print("\nMapping saved to participant_image_mapping.json")