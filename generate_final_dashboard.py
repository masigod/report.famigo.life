#!/usr/bin/env python3
"""
Generate final dashboard with properly mapped images
"""

import json

# Load all data
with open('excel_analysis.json', 'r', encoding='utf-8') as f:
    analysis_data = json.load(f)

with open('participant_final_mapping.json', 'r', encoding='utf-8') as f:
    final_mapping = json.load(f)

# Read template
with open('makeup-test-dashboard-v2.html', 'r', encoding='utf-8') as f:
    html_template = f.read()

# Inject data directly into HTML
script_start = html_template.find('let allParticipants = [];')
script_inject = f"""let allParticipants = {json.dumps(analysis_data['participant_data'], ensure_ascii=False)};
        let analysisData = {json.dumps(analysis_data, ensure_ascii=False)};
        let imageMapping = {json.dumps(final_mapping, ensure_ascii=False)};"""

# Replace the data loading section
html_with_data = html_template.replace(
    'let allParticipants = [];\n        let analysisData = null;\n        let imageMapping = {};',
    script_inject
)

# Comment out fetch functions
html_with_data = html_with_data.replace(
    'await loadAnalysisData();',
    '// Data embedded directly'
)
html_with_data = html_with_data.replace(
    'await loadImageMapping();',
    '// Data embedded directly'
)
html_with_data = html_with_data.replace(
    'await loadParticipantData();',
    'displayParticipants(allParticipants);'
)

# Update the showParticipantDetail function to use the enhanced mapping
updated_detail_function = """
        // Show participant detail modal with enhanced image display
        function showParticipantDetail(participant) {
            const modal = document.getElementById('participantModal');
            const aid = participant['A-ID'];
            const name = participant['What is your full name? (Please write exactly as shown in your ARC or passport)'] || 'Unknown';

            // Update modal header
            document.getElementById('modalParticipantName').textContent = name;
            document.getElementById('modalParticipantId').textContent = `A-ID: ${aid} | P-ID: ${participant['P-ID'] || '-'}`;

            // Get enhanced mapping data
            const mappingData = imageMapping[aid] || {};
            const images = mappingData.images || {};
            const data = mappingData.data || {};

            // Personal Information
            const personalInfo = document.getElementById('personalInfo');
            personalInfo.innerHTML = `
                <div class="detail-item">
                    <span class="detail-label">Name:</span>
                    <span class="detail-value">${name}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Gender:</span>
                    <span class="detail-value">${data.gender || participant['What is your gender? '] || '-'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Birth Year:</span>
                    <span class="detail-value">${data.birth_year || participant['Please enter your 4-digit year of birth(e.g., 1980) '] || '-'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Nationality:</span>
                    <span class="detail-value">${data.nationality || participant['What is your nationality?'] || '-'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Ethnicity:</span>
                    <span class="detail-value">${data.ethnicity || participant['Please select the ethnic group you identify with:'] || '-'}</span>
                </div>
            `;

            // Skin Analysis with images
            const skinColor = data.skin_brightness || participant['밝기판정'] || '-';
            const skinTone = data.skin_tone || participant['톤'] || '-';
            const colorInfo = skinColorInfo[skinColor] || { hex: '#ccc', label: skinColor };

            const skinInfo = document.getElementById('skinInfo');
            skinInfo.innerHTML = `
                <div class="detail-item">
                    <span class="detail-label">Skin Color:</span>
                    <span class="detail-value">
                        <span class="skin-color-box" style="background: ${colorInfo.hex};"></span>
                        ${skinColor}(${colorInfo.label})
                        ${images.skin_brightness_ref ? `<br><img src="excel_images/${images.skin_brightness_ref}" style="max-width: 100px; margin-top: 5px; border-radius: 5px;">` : ''}
                    </span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Skin Tone:</span>
                    <span class="detail-value">
                        <span class="tone-badge ${skinTone}">${skinTone}</span>
                    </span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Skin Type:</span>
                    <span class="detail-value">${data.skin_type || participant['What is your skin type?'] || '-'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Eye Color:</span>
                    <span class="detail-value">
                        ${data.eye_color || participant['Which of the following options most matches your natural eye color?'] || '-'}
                        ${images.eye_color_ref ? `<br><img src="excel_images/${images.eye_color_ref}" style="max-width: 100px; margin-top: 5px; border-radius: 5px;">` : ''}
                    </span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Hair Type:</span>
                    <span class="detail-value">
                        ${data.hair_type || participant['What is your Natural-born hair(not styled)?[Please select from the 10 options below]'] || '-'}
                        ${images.hair_type_ref ? `<br><img src="excel_images/${images.hair_type_ref}" style="max-width: 100px; margin-top: 5px; border-radius: 5px;">` : ''}
                    </span>
                </div>
            `;

            // Makeup Preferences
            const makeupInfo = document.getElementById('makeupInfo');
            makeupInfo.innerHTML = `
                <div class="detail-item">
                    <span class="detail-label">Makeup Frequency:</span>
                    <span class="detail-value">${data.makeup_frequency || participant['How often do you usually apply face makeup? '] || '-'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Cushion Usage:</span>
                    <span class="detail-value">${data.cushion_usage || participant['Have you ever used a cushion foundation?'] || '-'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Sunscreen Usage:</span>
                    <span class="detail-value">${participant['How often do you usually use sunscreen products?'] || '-'}</span>
                </div>
            `;

            // Survey Responses
            const surveyInfo = document.getElementById('surveyInfo');
            surveyInfo.innerHTML = `
                <div class="detail-item">
                    <span class="detail-label">Set Date:</span>
                    <span class="detail-value">${participant['setDate'] || '-'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Set Time:</span>
                    <span class="detail-value">${participant['setTime'] || '-'}</span>
                </div>
            `;

            // Load participant face photo
            const imagesContainer = document.getElementById('participantImages');
            if (images.face_photo) {
                imagesContainer.innerHTML = `
                    <div class="participant-image" style="max-width: 400px; margin: 0 auto;">
                        <img src="excel_images/${images.face_photo}"
                             alt="${name} - Face Photo"
                             style="width: 100%; height: auto; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1);"
                             onerror="this.parentElement.innerHTML='<div class=\\"no-images\\">No face photo available</div>'">
                    </div>
                `;
            } else {
                imagesContainer.innerHTML = '<div class="no-images">No face photo available for this participant</div>';
            }

            // Show modal
            modal.style.display = 'block';
        }"""

# Replace the showParticipantDetail function
search_pattern = "// Show participant detail modal"
end_pattern = "// Close participant modal"
start_idx = html_with_data.find(search_pattern)
end_idx = html_with_data.find(end_pattern)

if start_idx != -1 and end_idx != -1:
    html_with_data = html_with_data[:start_idx] + updated_detail_function + "\n\n        " + html_with_data[end_idx:]

# Save the final dashboard
with open('makeup-test-dashboard-final.html', 'w', encoding='utf-8') as f:
    f.write(html_with_data)

print("Generated makeup-test-dashboard-final.html with enhanced image display")
print("This file includes:")
print("- Individual face photos for each participant")
print("- Reference images for skin color, hair type, and eye color")
print("- All data embedded directly in the HTML")