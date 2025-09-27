#!/usr/bin/env python3
"""
Generate dashboard HTML with embedded data
"""

import json
import pandas as pd

# Read Excel data
df = pd.read_excel('makeuptest_AP_Bueatylink_20250927.xlsx')

# Load analysis data
with open('excel_analysis.json', 'r', encoding='utf-8') as f:
    analysis_data = json.load(f)

# Load image mapping
with open('participant_image_mapping.json', 'r', encoding='utf-8') as f:
    image_mapping = json.load(f)

# Generate embedded HTML
html_template = open('makeup-test-dashboard-v2.html', 'r', encoding='utf-8').read()

# Find the script section and inject data
script_start = html_template.find('let allParticipants = [];')
script_inject = f"""let allParticipants = {json.dumps(analysis_data['participant_data'], ensure_ascii=False)};
        let analysisData = {json.dumps(analysis_data, ensure_ascii=False)};
        let imageMapping = {json.dumps(image_mapping, ensure_ascii=False)};"""

# Replace the data loading section
html_with_data = html_template.replace(
    'let allParticipants = [];\n        let analysisData = null;\n        let imageMapping = {};',
    script_inject
)

# Comment out the fetch functions
html_with_data = html_with_data.replace(
    'await loadAnalysisData();',
    '// await loadAnalysisData(); // Data embedded'
)
html_with_data = html_with_data.replace(
    'await loadImageMapping();',
    '// await loadImageMapping(); // Data embedded'
)
html_with_data = html_with_data.replace(
    'await loadParticipantData();',
    '// await loadParticipantData(); // Data embedded\n            displayParticipants(allParticipants);'
)

# Save the new file
with open('makeup-test-dashboard-embedded.html', 'w', encoding='utf-8') as f:
    f.write(html_with_data)

print("Generated makeup-test-dashboard-embedded.html with embedded data")
print(f"Total participants: {len(analysis_data['participant_data'])}")
print("This file can be opened directly without a web server.")