#!/usr/bin/env python3
"""
Extract images from Excel file and analyze data for dashboard
"""

import pandas as pd
import zipfile
import os
import shutil
from pathlib import Path
import json

def extract_images_from_excel(excel_path):
    """Extract embedded images from Excel file"""
    output_dir = Path("excel_images")
    output_dir.mkdir(exist_ok=True)

    # Excel files are actually zip archives
    temp_dir = Path("temp_excel_extract")

    try:
        # Extract Excel file as zip
        with zipfile.ZipFile(excel_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Look for media folder (contains images)
        media_path = temp_dir / "xl" / "media"
        if media_path.exists():
            print(f"Found media folder with images")

            # Copy all images to output directory
            for image_file in media_path.glob("*"):
                if image_file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                    dest_path = output_dir / image_file.name
                    shutil.copy2(image_file, dest_path)
                    print(f"  Extracted: {image_file.name}")

            return True
        else:
            print("No embedded images found in Excel file")
            return False

    except Exception as e:
        print(f"Error extracting images: {e}")
        return False

    finally:
        # Clean up temp directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

def analyze_excel_data(excel_path):
    """Analyze Excel data and prepare for dashboard"""
    df = pd.read_excel(excel_path)

    analysis = {
        "total_participants": len(df),
        "columns": list(df.columns),
        "summary_stats": {}
    }

    # Analyze key fields
    if 'P-ID' in df.columns:
        analysis['summary_stats']['unique_p_ids'] = df['P-ID'].nunique()

    if '밝기판정' in df.columns:
        analysis['summary_stats']['brightness_distribution'] = df['밝기판정'].value_counts().to_dict()

    if '톤' in df.columns:
        analysis['summary_stats']['tone_distribution'] = df['톤'].value_counts().to_dict()

    # Gender distribution
    if 'What is your gender? ' in df.columns:
        analysis['summary_stats']['gender_distribution'] = df['What is your gender? '].value_counts().to_dict()

    # Nationality distribution
    if 'What is your nationality?' in df.columns:
        analysis['summary_stats']['nationality_distribution'] = df['What is your nationality?'].value_counts().head(10).to_dict()

    # Age distribution (birth year)
    if 'Please enter your 4-digit year of birth(e.g., 1980) ' in df.columns:
        birth_years = df['Please enter your 4-digit year of birth(e.g., 1980) ']
        analysis['summary_stats']['age_range'] = {
            'min_birth_year': int(birth_years.min()) if pd.notna(birth_years.min()) else None,
            'max_birth_year': int(birth_years.max()) if pd.notna(birth_years.max()) else None,
            'avg_birth_year': int(birth_years.mean()) if pd.notna(birth_years.mean()) else None
        }

    # Ethnic group distribution
    if 'Please select the ethnic group you identify with:' in df.columns:
        analysis['summary_stats']['ethnic_distribution'] = df['Please select the ethnic group you identify with:'].value_counts().to_dict()

    # Makeup frequency
    if 'How often do you usually apply face makeup? ' in df.columns:
        analysis['summary_stats']['makeup_frequency'] = df['How often do you usually apply face makeup? '].value_counts().to_dict()

    # Cushion foundation usage
    if 'Have you ever used a cushion foundation?' in df.columns:
        analysis['summary_stats']['cushion_usage'] = df['Have you ever used a cushion foundation?'].value_counts().to_dict()

    # Skin type
    if 'What is your skin type?' in df.columns:
        analysis['summary_stats']['skin_type_distribution'] = df['What is your skin type?'].value_counts().to_dict()

    # Eye color
    if 'Which of the following options most matches your natural eye color?' in df.columns:
        analysis['summary_stats']['eye_color_distribution'] = df['Which of the following options most matches your natural eye color?'].value_counts().to_dict()

    # Convert data to list of records for table display
    analysis['participant_data'] = df.to_dict('records')

    return analysis

if __name__ == "__main__":
    excel_path = "makeuptest_AP_Bueatylink_20250927.xlsx"

    print("=== Extracting Images ===")
    has_images = extract_images_from_excel(excel_path)

    print("\n=== Analyzing Data ===")
    analysis = analyze_excel_data(excel_path)

    # Save analysis to JSON
    with open('excel_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2, default=str)

    print(f"\nTotal participants: {analysis['total_participants']}")
    print(f"Data columns: {len(analysis['columns'])}")

    if 'brightness_distribution' in analysis['summary_stats']:
        print("\nBrightness Distribution:")
        for key, value in analysis['summary_stats']['brightness_distribution'].items():
            print(f"  Level {key}: {value} participants")

    if 'tone_distribution' in analysis['summary_stats']:
        print("\nTone Distribution:")
        for key, value in analysis['summary_stats']['tone_distribution'].items():
            print(f"  {key}: {value} participants")

    print("\nAnalysis saved to excel_analysis.json")