#!/usr/bin/env python3
"""
Update Airtable Participants table with skin color and tone data from Excel file
"""

import pandas as pd
import requests
import json
from typing import Dict, List, Optional
import time

# Configuration - loaded from env-config.js
AIRTABLE_API_KEY = ""  # Will be set from command line or environment
AIRTABLE_BASE_ID = "appZcPs57spwdoKQH"
PARTICIPANTS_TABLE_ID = "tblxMzwX1wWJKIOhY"

# Excel file path
EXCEL_FILE = "/Users/owlers_dylan/Downloads/makeuptest_AP_Bueatylink_20250927.xlsx"

# Mapping for skin color values
SKIN_COLOR_MAP = {
    "1": "1(F)",
    "2": "2(L)",
    "3": "3(LM)",
    "4": "4(M)",
    "5": "5(MD)",
    "6": "6(D)",
    "7": "7(R)",
    "1(F)": "1(F)",
    "2(L)": "2(L)",
    "3(LM)": "3(LM)",
    "4(M)": "4(M)",
    "5(MD)": "5(MD)",
    "6(D)": "6(D)",
    "7(R)": "7(R)"
}

# Mapping for skin tone values
SKIN_TONE_MAP = {
    "쿨": "Cool",
    "쿨톤": "Cool",
    "Cool": "Cool",
    "뉴트럴": "Neutral",
    "중립": "Neutral",
    "Neutral": "Neutral",
    "웜": "Warm",
    "웜톤": "Warm",
    "Warm": "Warm",
    "올리브": "Olive",
    "Olive": "Olive"
}


def read_excel_data(file_path: str) -> pd.DataFrame:
    """Read Excel file and return DataFrame with relevant columns"""
    print(f"Reading Excel file: {file_path}")

    # Read Excel file
    df = pd.read_excel(file_path)

    # Print column names for debugging
    print(f"Excel columns: {list(df.columns)}")
    print(f"Total rows in Excel: {len(df)}")

    # Show first few rows for debugging
    print("\nFirst 3 rows of Excel data:")
    for col in df.columns:
        print(f"  {col}: {df[col].head(3).tolist()}")

    return df


def get_airtable_participants(api_key: str) -> Dict[str, dict]:
    """Fetch all participants from Airtable"""
    print("\nFetching participants from Airtable...")

    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{PARTICIPANTS_TABLE_ID}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    all_records = []
    offset = None
    page_count = 0

    while True:
        params = {}
        if offset:
            params['offset'] = offset
        params['pageSize'] = 100

        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            print(f"Error fetching data: {response.status_code}")
            print(response.text)
            raise Exception(f"Failed to fetch Airtable data: {response.status_code}")

        data = response.json()
        page_count += 1
        print(f"  Page {page_count}: {len(data['records'])} records")

        all_records.extend(data['records'])

        offset = data.get('offset')
        if not offset:
            break

    print(f"Total participants fetched: {len(all_records)}")

    # Create dictionary keyed by P-ID
    participants_dict = {}
    for record in all_records:
        pid = record['fields'].get('P-ID') or record['fields'].get('ID')
        if pid:
            participants_dict[str(pid)] = record

    print(f"Participants with P-ID: {len(participants_dict)}")

    # Show sample of P-IDs
    sample_pids = list(participants_dict.keys())[:5]
    print(f"Sample P-IDs: {sample_pids}")

    return participants_dict


def update_participant(api_key: str, record_id: str, skin_color: str, skin_tone: str) -> bool:
    """Update a single participant record in Airtable"""
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{PARTICIPANTS_TABLE_ID}/{record_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "fields": {
            "skinColor": skin_color,
            "skinTone": skin_tone
        }
    }

    response = requests.patch(url, headers=headers, json=data)

    if response.status_code == 200:
        return True
    else:
        print(f"  Error updating record {record_id}: {response.status_code}")
        print(f"  Response: {response.text}")
        return False


def main(api_key: str, dry_run: bool = True):
    """Main function to update Airtable participants with Excel data"""

    # Read Excel data
    excel_df = read_excel_data(EXCEL_FILE)

    # Check for required columns
    pid_column = None
    brightness_column = None
    tone_column = None

    # Try to find P-ID column
    for col in excel_df.columns:
        if 'P-ID' in col or 'PID' in col or 'P_ID' in col:
            pid_column = col
            print(f"Found P-ID column: {col}")
            break

    # Try to find brightness (밝기판정) column
    for col in excel_df.columns:
        if '밝기' in col or '판정' in col or '밝기판정' in col:
            brightness_column = col
            print(f"Found brightness column: {col}")
            break

    # Try to find tone (톤) column
    for col in excel_df.columns:
        if col == '톤' or '톤' in col:
            tone_column = col
            print(f"Found tone column: {col}")
            break

    if not pid_column:
        print("ERROR: Could not find P-ID column in Excel file")
        print(f"Available columns: {list(excel_df.columns)}")
        return

    if not brightness_column:
        print("ERROR: Could not find brightness (밝기판정) column in Excel file")
        print(f"Available columns: {list(excel_df.columns)}")
        return

    if not tone_column:
        print("ERROR: Could not find tone (톤) column in Excel file")
        print(f"Available columns: {list(excel_df.columns)}")
        return

    # Get Airtable participants
    participants = get_airtable_participants(api_key)

    # Process updates
    updates_to_make = []
    matched_count = 0
    unmatched_count = 0

    print("\nProcessing Excel data...")

    for idx, row in excel_df.iterrows():
        pid = str(row[pid_column]) if pd.notna(row[pid_column]) else None
        brightness = str(row[brightness_column]) if pd.notna(row[brightness_column]) else None
        tone = str(row[tone_column]) if pd.notna(row[tone_column]) else None

        if not pid:
            continue

        # Map values
        skin_color = SKIN_COLOR_MAP.get(brightness, brightness) if brightness else None
        skin_tone = SKIN_TONE_MAP.get(tone, tone) if tone else None

        # Find matching participant
        if pid in participants:
            matched_count += 1
            participant = participants[pid]
            record_id = participant['id']
            current_skin_color = participant['fields'].get('skinColor')
            current_skin_tone = participant['fields'].get('skinTone')

            # Check if update needed
            if skin_color != current_skin_color or skin_tone != current_skin_tone:
                updates_to_make.append({
                    'record_id': record_id,
                    'pid': pid,
                    'name': participant['fields'].get('name', 'Unknown'),
                    'old_skin_color': current_skin_color,
                    'new_skin_color': skin_color,
                    'old_skin_tone': current_skin_tone,
                    'new_skin_tone': skin_tone
                })
        else:
            unmatched_count += 1
            if unmatched_count <= 5:  # Show first 5 unmatched
                print(f"  No match for P-ID: {pid}")

    print(f"\nMatching results:")
    print(f"  Matched: {matched_count}")
    print(f"  Unmatched: {unmatched_count}")
    print(f"  Updates needed: {len(updates_to_make)}")

    if len(updates_to_make) > 0:
        print(f"\nFirst 10 updates to be made:")
        for i, update in enumerate(updates_to_make[:10]):
            print(f"  {i+1}. {update['name']} (P-ID: {update['pid']})")
            print(f"     Color: {update['old_skin_color']} → {update['new_skin_color']}")
            print(f"     Tone: {update['old_skin_tone']} → {update['new_skin_tone']}")

    if dry_run:
        print("\n*** DRY RUN MODE - No actual updates performed ***")
        print(f"Would update {len(updates_to_make)} records")
        return

    # Perform actual updates
    if len(updates_to_make) > 0:
        print(f"\nPerforming actual updates...")

        success_count = 0
        error_count = 0

        for i, update in enumerate(updates_to_make):
            print(f"  Updating {i+1}/{len(updates_to_make)}: {update['name']}...", end='')

            success = update_participant(
                api_key,
                update['record_id'],
                update['new_skin_color'],
                update['new_skin_tone']
            )

            if success:
                success_count += 1
                print(" ✓")
            else:
                error_count += 1
                print(" ✗")

            # Rate limiting - Airtable allows 5 requests per second
            if (i + 1) % 5 == 0:
                time.sleep(1.1)

        print(f"\nUpdate complete:")
        print(f"  Success: {success_count}")
        print(f"  Errors: {error_count}")
    else:
        print("\nNo updates needed - all data already matches")


if __name__ == "__main__":
    import sys
    import os

    # Get API key from environment or command line
    api_key = os.environ.get('AIRTABLE_API_KEY')

    if not api_key and len(sys.argv) > 1:
        api_key = sys.argv[1]

    if not api_key:
        print("Please provide Airtable API key as argument or set AIRTABLE_API_KEY environment variable")
        print("Usage: python update_participants_skin_data.py <API_KEY> [--execute]")
        sys.exit(1)

    # Check for execute flag
    dry_run = True
    if len(sys.argv) > 2 and sys.argv[2] == '--execute':
        dry_run = False

    main(api_key, dry_run)