#!/usr/bin/env python3
"""
Create enhanced dashboard with image brightness display and beauty survey data
"""

import pandas as pd
import json
from pathlib import Path

# Load Excel data
df = pd.read_excel('/Users/owlers_dylan/APCLT/makeuptest_AP_Bueatylink_20250927.xlsx')
print(f"Loaded {len(df)} participants")

# Create participant data
participant_data = []
for idx, row in df.iterrows():
    participant = {}
    for col in df.columns:
        value = row[col]
        if pd.isna(value):
            participant[col] = None
        elif isinstance(value, (int, float)):
            participant[col] = value
        else:
            participant[col] = str(value)
    participant_data.append(participant)

# Calculate statistics
summary_stats = {
    'total_participants': 133,
    'gender_distribution': df['What is your gender? '].value_counts().to_dict(),
    'brightness_distribution': {str(k): int(v) for k, v in df['밝기판정'].value_counts().to_dict().items()},
    'tone_distribution': {str(k) if k else 'Unknown': int(v) for k, v in df['톤'].value_counts().to_dict().items()},
}

# Create image mapping
image_dir = Path('images_organized_by_aid')
image_mapping = {}

for idx, row in df.iterrows():
    aid = row['A-ID']
    image_mapping[aid] = {
        'pid': str(row['P-ID']),
        'name': row['What is your full name? (Please write exactly as shown in your ARC or passport)'],
        'images': {}
    }

    # Check for images
    face_photo = image_dir / f'{aid}_face_photo.jpg'
    if face_photo.exists():
        image_mapping[aid]['images']['face_photo'] = f'images_organized_by_aid/{aid}_face_photo.jpg'

    for img_type in ['skin_brightness', 'hair', 'eye_color']:
        img_path = image_dir / f'{aid}_{img_type}.png'
        if img_path.exists():
            image_mapping[aid]['images'][img_type] = f'images_organized_by_aid/{aid}_{img_type}.png'

# Define tone colors
tone_colors = {
    'Warm': '#ff9068',
    'Cool': '#68a8ff',
    'Neutral': '#a8a8a8',
    'Olive': '#8b9467'
}

# Create HTML
html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Amore Pacific Foundation Consumer Test 2025 (with famigo)</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>💄</text></svg>">
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.7/css/dataTables.bootstrap5.min.css">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        .main-container {
            max-width: 100%;
            margin: 0 auto;
        }
        .header {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        .header h1 {
            color: #333;
            font-size: 2.2rem;
            margin-bottom: 10px;
        }
        .header .subtitle {
            color: #666;
            font-size: 1.1rem;
        }
        .stats-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s;
        }
        .stat-card:hover {
            transform: translateY(-5px);
        }
        .stat-number {
            font-size: 2.5rem;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .stat-label {
            color: #666;
            font-size: 0.9rem;
            margin-top: 5px;
        }
        .table-container {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        .table thead th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px;
            font-weight: 500;
        }
        .table tbody tr:hover {
            background-color: #f8f9fa;
        }
        .btn-view-details {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85rem;
            transition: transform 0.2s;
        }
        .btn-view-details:hover {
            transform: scale(1.05);
            color: white;
        }
        .brightness-img {
            width: 40px;
            height: 40px;
            object-fit: contain;
            border-radius: 8px;
            border: 1px solid #ddd;
            background: #f8f9fa;
        }
        .tone-badge {
            padding: 5px 12px;
            border-radius: 15px;
            color: white;
            font-weight: 500;
            font-size: 0.85rem;
            display: inline-block;
            text-shadow: 0 1px 2px rgba(0,0,0,0.2);
        }
        .tone-warm {
            background: #ff9068;
        }
        .tone-cool {
            background: #68a8ff;
        }
        .tone-neutral {
            background: #a8a8a8;
        }
        .tone-olive {
            background: #8b9467;
        }
        .modal-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .modal-body {
            padding: 30px;
            background: #f8f9fa;
        }
        .info-section {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
        }
        .info-section h5 {
            color: #333;
            margin-bottom: 15px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
        }
        .info-item {
            padding: 8px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .info-label {
            font-weight: 600;
            color: #555;
            font-size: 0.85rem;
        }
        .info-value {
            color: #333;
            font-size: 0.95rem;
        }
        .beauty-section {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
        }
        .beauty-item {
            margin-bottom: 15px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .beauty-question {
            font-weight: 500;
            color: #555;
            font-size: 0.9rem;
            margin-bottom: 5px;
        }
        .beauty-answer {
            color: #333;
            font-size: 0.95rem;
            padding-left: 10px;
        }
        .reference-images-section {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
        }
        .reference-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        }
        .reference-item {
            text-align: center;
        }
        .reference-item img {
            width: 100%;
            height: 180px;
            object-fit: contain;
            border-radius: 12px;
            border: 1px solid #e0e0e0;
            background: white;
            padding: 10px;
        }
        .reference-item h6 {
            margin-top: 10px;
            color: #666;
            font-size: 0.9rem;
        }
        .face-photo-section {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        .face-photo-section img {
            max-width: 400px;
            width: 100%;
            height: auto;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }
        .no-image {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 180px;
            background: #f0f0f0;
            color: #999;
            border-radius: 12px;
        }
        .no-face-photo {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 300px;
            background: #f0f0f0;
            color: #999;
            border-radius: 12px;
        }
        .rating-badge {
            background: #667eea;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.85rem;
            margin-left: 5px;
        }
    </style>
</head>
<body>
    <div class="main-container">
        <div class="header">
            <h1>Amore Pacific Foundation Consumer Test 2025 (with famigo)</h1>
            <div class="subtitle">Data Report: 9월 22일 ~ 26일, 2025년 | Total Participants: <span id="totalCount">133</span></div>
        </div>

        <div class="stats-container">
            <div class="stat-card">
                <div class="stat-number">133</div>
                <div class="stat-label">Total Participants</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="femaleCount">0</div>
                <div class="stat-label">Female</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="maleCount">0</div>
                <div class="stat-label">Male</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="warmCount">0</div>
                <div class="stat-label">Warm Tone</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="coolCount">0</div>
                <div class="stat-label">Cool Tone</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="neutralCount">0</div>
                <div class="stat-label">Neutral Tone</div>
            </div>
        </div>

        <div class="table-container">
            <table id="participantsTable" class="table table-striped">
                <thead>
                    <tr>
                        <th>A-ID</th>
                        <th>P-ID</th>
                        <th>Name</th>
                        <th>Gender</th>
                        <th>Nationality</th>
                        <th>Birth Year</th>
                        <th>Skin Brightness</th>
                        <th>Skin Tone</th>
                        <th>Ethnic Group</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody id="tableBody">
                </tbody>
            </table>
        </div>
    </div>

    <!-- Detail Modal -->
    <div class="modal fade" id="detailModal" tabindex="-1">
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="modalTitle">Participant Details</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body" id="modalBody">
                </div>
            </div>
        </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.7/js/dataTables.bootstrap5.min.js"></script>
    <script>
        // Embed data
        const allParticipants = ''' + json.dumps(participant_data, ensure_ascii=False) + ''';
        const imageMapping = ''' + json.dumps(image_mapping, ensure_ascii=False) + ''';
        const summaryStats = ''' + json.dumps(summary_stats, ensure_ascii=False) + ''';

        // Update statistics
        function updateStats() {
            document.getElementById('femaleCount').textContent = summaryStats.gender_distribution['Female'] || 0;
            document.getElementById('maleCount').textContent = summaryStats.gender_distribution['Male'] || 0;
            document.getElementById('warmCount').textContent = summaryStats.tone_distribution['Warm'] || 0;
            document.getElementById('coolCount').textContent = summaryStats.tone_distribution['Cool'] || 0;
            document.getElementById('neutralCount').textContent = summaryStats.tone_distribution['Neutral'] || 0;
        }

        // Get tone class
        function getToneClass(tone) {
            if (!tone) return '';
            const lowerTone = tone.toLowerCase();
            if (lowerTone.includes('warm')) return 'tone-warm';
            if (lowerTone.includes('cool')) return 'tone-cool';
            if (lowerTone.includes('neutral')) return 'tone-neutral';
            if (lowerTone.includes('olive')) return 'tone-olive';
            return 'tone-neutral';
        }

        // Show participant details
        function showDetails(aid) {
            const participant = allParticipants.find(p => p['A-ID'] === aid);
            const mapping = imageMapping[aid];

            const modalTitle = document.getElementById('modalTitle');
            const modalBody = document.getElementById('modalBody');

            modalTitle.textContent = `${participant['What is your full name? (Please write exactly as shown in your ARC or passport)']} (${aid})`;

            let modalContent = `
                <!-- Basic Information -->
                <div class="info-section">
                    <h5>Basic Information</h5>
                    <div class="info-grid">
                        <div class="info-item">
                            <span class="info-label">A-ID:</span>
                            <span class="info-value">${participant['A-ID']}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">P-ID:</span>
                            <span class="info-value">${participant['P-ID']}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Gender:</span>
                            <span class="info-value">${participant['What is your gender? '] || 'N/A'}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Nationality:</span>
                            <span class="info-value">${participant['What is your nationality?'] || 'N/A'}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Birth Year:</span>
                            <span class="info-value">${participant['Please enter your 4-digit year of birth(e.g., 1980) '] || 'N/A'}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Ethnic Group:</span>
                            <span class="info-value">${participant['Please select the ethnic group you identify with:'] || 'N/A'}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Skin Brightness:</span>
                            <span class="info-value">${participant['밝기판정'] || 'N/A'}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Skin Tone:</span>
                            <span class="info-value"><span class="tone-badge ${getToneClass(participant['톤'])}">${participant['톤'] || 'N/A'}</span></span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">English Level:</span>
                            <span class="info-value">${participant['How would you rate your English speaking ability?'] || 'N/A'}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Time in Korea:</span>
                            <span class="info-value">${participant['How long have you been living in Korea?'] || 'N/A'}</span>
                        </div>
                    </div>
                </div>

                <!-- Beauty & Cosmetics Section -->
                <div class="beauty-section">
                    <h5>Beauty & Cosmetics Usage</h5>
                    <div class="beauty-item">
                        <div class="beauty-question">How often do you apply face makeup?</div>
                        <div class="beauty-answer">${participant['How often do you usually apply face makeup? '] || 'N/A'}</div>
                    </div>
                    <div class="beauty-item">
                        <div class="beauty-question">How often do you visit cosmetic stores?</div>
                        <div class="beauty-answer">${participant['How many times do you visit cosmetic store?'] || 'N/A'}</div>
                    </div>
                    <div class="beauty-item">
                        <div class="beauty-question">Cosmetics purchase behavior:</div>
                        <div class="beauty-answer">${participant['Please check the one that best describes how you usually buy cosmetics.'] || 'N/A'}</div>
                    </div>
                    <div class="beauty-item">
                        <div class="beauty-question">Skin type:</div>
                        <div class="beauty-answer">${participant['What is your skin type?'] || 'N/A'}</div>
                    </div>
                    <div class="beauty-item">
                        <div class="beauty-question">Preferred makeup look:</div>
                        <div class="beauty-answer">${participant['Which of the following makeup looks do you prefer the most after applying makeup?'] || 'N/A'}</div>
                    </div>
                    <div class="beauty-item">
                        <div class="beauty-question">Sunscreen usage:</div>
                        <div class="beauty-answer">${participant['How often do you usually use sunscreen products?'] || 'N/A'}</div>
                    </div>
                    <div class="beauty-item">
                        <div class="beauty-question">Base makeup products used:</div>
                        <div class="beauty-answer">${participant['Please select all face/base makeup products you typically use: for your daily makeup routine (Select at least one)'] || 'N/A'}</div>
                    </div>
                    <div class="beauty-item">
                        <div class="beauty-question">Cushion foundation usage:</div>
                        <div class="beauty-answer">${participant['Have you ever used a cushion foundation?'] || 'N/A'}</div>
                    </div>
                    <div class="beauty-item">
                        <div class="beauty-question">Lip makeup products:</div>
                        <div class="beauty-answer">${participant['Please select all the lip makeup products you typically use for your daily makeup routine.'] || 'N/A'}</div>
                    </div>
                </div>

                <!-- Beauty Behavior Ratings -->
                <div class="beauty-section">
                    <h5>Beauty Behavior Ratings (1-5 Scale)</h5>
                    <div class="beauty-item">
                        <div class="beauty-question">Makeup is fun and exciting:</div>
                        <div class="beauty-answer">
                            ${participant['Please rate the following statements to indicate your level of agreement with the items related to your cosmetics usage and purchase behavior. (purchase behavior: Disagree(1)~Agree(5)) >> For me, makeup isn't something bothersome or obligatory, but rather something fun and exciting.'] || 'N/A'}
                            <span class="rating-badge">${participant['Please rate the following statements to indicate your level of agreement with the items related to your cosmetics usage and purchase behavior. (purchase behavior: Disagree(1)~Agree(5)) >> For me, makeup isn't something bothersome or obligatory, but rather something fun and exciting.']}/5</span>
                        </div>
                    </div>
                    <div class="beauty-item">
                        <div class="beauty-question">Enjoy trying various cosmetics:</div>
                        <div class="beauty-answer">
                            ${participant['Please rate the following statements to indicate your level of agreement with the items related to your cosmetics usage and purchase behavior. (purchase behavior: Disagree(1)~Agree(5)) >> I enjoy trying out and testing various cosmetics.'] || 'N/A'}
                            <span class="rating-badge">${participant['Please rate the following statements to indicate your level of agreement with the items related to your cosmetics usage and purchase behavior. (purchase behavior: Disagree(1)~Agree(5)) >> I enjoy trying out and testing various cosmetics.']}/5</span>
                        </div>
                    </div>
                    <div class="beauty-item">
                        <div class="beauty-question">Browse stores without buying:</div>
                        <div class="beauty-answer">
                            ${participant['Please rate the following statements to indicate your level of agreement with the items related to your cosmetics usage and purchase behavior. (purchase behavior: Disagree(1)~Agree(5)) >> Even if I don't plan on buying cosmetics, I often stop by a store to browse and test products.'] || 'N/A'}
                            <span class="rating-badge">${participant['Please rate the following statements to indicate your level of agreement with the items related to your cosmetics usage and purchase behavior. (purchase behavior: Disagree(1)~Agree(5)) >> Even if I don't plan on buying cosmetics, I often stop by a store to browse and test products.']}/5</span>
                        </div>
                    </div>
                    <div class="beauty-item">
                        <div class="beauty-question">Browse cosmetics on social media:</div>
                        <div class="beauty-answer">
                            ${participant['Please rate the following statements to indicate your level of agreement with the items related to your cosmetics usage and purchase behavior. (purchase behavior: Disagree(1)~Agree(5)) >> Even when I don't plan on buying cosmetics, I browse cosmetics-related content on mobile platforms like TikTok and Instagram.'] || 'N/A'}
                            <span class="rating-badge">${participant['Please rate the following statements to indicate your level of agreement with the items related to your cosmetics usage and purchase behavior. (purchase behavior: Disagree(1)~Agree(5)) >> Even when I don't plan on buying cosmetics, I browse cosmetics-related content on mobile platforms like TikTok and Instagram.']}/5</span>
                        </div>
                    </div>
                    <div class="beauty-item">
                        <div class="beauty-question">Talk with friends about cosmetics:</div>
                        <div class="beauty-answer">
                            ${participant['Please rate the following statements to indicate your level of agreement with the items related to your cosmetics usage and purchase behavior. (purchase behavior: Disagree(1)~Agree(5)) >> I enjoy talking with friends about their experiences using cosmetics.'] || 'N/A'}
                            <span class="rating-badge">${participant['Please rate the following statements to indicate your level of agreement with the items related to your cosmetics usage and purchase behavior. (purchase behavior: Disagree(1)~Agree(5)) >> I enjoy talking with friends about their experiences using cosmetics.']}/5</span>
                        </div>
                    </div>
                </div>

                <!-- Reference Images -->
                <div class="reference-images-section">
                    <h5>Reference Images</h5>
                    <div class="reference-grid">`;

            // Add skin brightness image
            if (mapping.images.skin_brightness) {
                modalContent += `
                    <div class="reference-item">
                        <img src="${mapping.images.skin_brightness}" alt="Skin Brightness">
                        <h6>Skin Brightness Reference</h6>
                    </div>`;
            } else {
                modalContent += `
                    <div class="reference-item">
                        <div class="no-image">No Image</div>
                        <h6>Skin Brightness Reference</h6>
                    </div>`;
            }

            // Add hair image
            if (mapping.images.hair) {
                modalContent += `
                    <div class="reference-item">
                        <img src="${mapping.images.hair}" alt="Hair">
                        <h6>Hair Reference</h6>
                    </div>`;
            } else {
                modalContent += `
                    <div class="reference-item">
                        <div class="no-image">No Image</div>
                        <h6>Hair Reference</h6>
                    </div>`;
            }

            // Add eye color image
            if (mapping.images.eye_color) {
                modalContent += `
                    <div class="reference-item">
                        <img src="${mapping.images.eye_color}" alt="Eye Color">
                        <h6>Eye Color Reference</h6>
                    </div>`;
            } else {
                modalContent += `
                    <div class="reference-item">
                        <div class="no-image">No Image</div>
                        <h6>Eye Color Reference</h6>
                    </div>`;
            }

            // Empty cell for alignment
            modalContent += `
                    <div class="reference-item"></div>
                </div>
            </div>`;

            // Add face photo at the bottom (most important)
            modalContent += `
                <div class="face-photo-section">
                    <h5>Face Photo</h5>`;

            if (mapping.images.face_photo) {
                modalContent += `<img src="${mapping.images.face_photo}" alt="Face Photo">`;
            } else {
                modalContent += `<div class="no-face-photo">No Face Photo Available</div>`;
            }

            modalContent += `</div>`;

            modalBody.innerHTML = modalContent;

            const modal = new bootstrap.Modal(document.getElementById('detailModal'));
            modal.show();
        }

        // Initialize table
        $(document).ready(function() {
            // Populate table
            const tableBody = document.getElementById('tableBody');
            let tableHtml = '';

            allParticipants.forEach(participant => {
                const mapping = imageMapping[participant['A-ID']] || {};
                const hasImages = mapping.images && Object.keys(mapping.images).length > 0;
                const toneClass = getToneClass(participant['톤']);

                // Get skin brightness image
                let brightnessDisplay = participant['밝기판정'] || '-';
                if (mapping.images && mapping.images.skin_brightness) {
                    brightnessDisplay = `<img src="${mapping.images.skin_brightness}" class="brightness-img" alt="${participant['밝기판정']}" title="Brightness: ${participant['밝기판정']}">`;
                }

                // Get tone with background color
                let toneDisplay = '-';
                if (participant['톤']) {
                    toneDisplay = `<span class="tone-badge ${toneClass}">${participant['톤']}</span>`;
                }

                tableHtml += `
                    <tr>
                        <td><strong>${participant['A-ID']}</strong></td>
                        <td>${participant['P-ID']}</td>
                        <td>${participant['What is your full name? (Please write exactly as shown in your ARC or passport)']}</td>
                        <td>${participant['What is your gender? '] || '-'}</td>
                        <td>${participant['What is your nationality?'] || '-'}</td>
                        <td>${participant['Please enter your 4-digit year of birth(e.g., 1980) '] || '-'}</td>
                        <td>${brightnessDisplay}</td>
                        <td>${toneDisplay}</td>
                        <td>${participant['Please select the ethnic group you identify with:'] || '-'}</td>
                        <td>
                            <button class="btn btn-view-details" onclick="showDetails('${participant['A-ID']}')">View Details</button>
                        </td>
                    </tr>`;
            });

            tableBody.innerHTML = tableHtml;

            // Initialize DataTable
            $('#participantsTable').DataTable({
                pageLength: 25,
                responsive: true,
                order: [[0, 'asc']],
                language: {
                    search: "Search participants:",
                    lengthMenu: "Show _MENU_ participants per page",
                    info: "Showing _START_ to _END_ of _TOTAL_ participants",
                    paginate: {
                        first: "First",
                        last: "Last",
                        next: "Next",
                        previous: "Previous"
                    }
                }
            });

            updateStats();
        });
    </script>
</body>
</html>'''

# Save the new dashboard
with open('makeup-test-dashboard-enhanced.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("\n=== Enhanced Dashboard Created ===")
print(f"✓ Skin brightness shown as image thumbnail")
print(f"✓ Skin tone with colored background")
print(f"✓ Beauty survey responses added to modal")
print(f"✓ Face photo displayed prominently at bottom")
print(f"✓ All images with rounded corners")
print("\nNew dashboard saved as makeup-test-dashboard-enhanced.html")