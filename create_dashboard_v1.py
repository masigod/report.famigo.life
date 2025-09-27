#!/usr/bin/env python3
"""
Create makeup-test-dashboard-v1.html with correct 133 participant data
"""

import pandas as pd
import json
from pathlib import Path
from collections import Counter

# Load the correct Excel file with 133 participants
df = pd.read_excel('/Users/owlers_dylan/APCLT/makeuptest_AP_Bueatylink_20250927.xlsx')
print(f"Loaded {len(df)} participants")

# Verify we have 133
assert len(df) == 133, f"Expected 133 participants, got {len(df)}"

# Verify A216 exists
a216_exists = 'A216' in df['A-ID'].values
print(f"A216 exists: {a216_exists}")

if a216_exists:
    a216_data = df[df['A-ID'] == 'A216'].iloc[0]
    print(f"A216: {a216_data['What is your full name? (Please write exactly as shown in your ARC or passport)']}")

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

print(f"\nProcessed {len(participant_data)} participants")

# Calculate statistics for 133 participants
summary_stats = {
    'total_participants': 133,
    'gender_distribution': df['What is your gender? '].value_counts().to_dict(),
    'brightness_distribution': {str(k): int(v) for k, v in df['밝기판정'].value_counts().to_dict().items()},
    'tone_distribution': {str(k) if k else 'Unknown': int(v) for k, v in df['톤'].value_counts().to_dict().items()},
    'nationality_distribution': df['What is your nationality?'].value_counts().head(5).to_dict(),
    'ethnic_distribution': df['Please select the ethnic group you identify with:'].value_counts().to_dict(),
    'age_distribution': {
        '1990s': len(df[(df['Please enter your 4-digit year of birth(e.g., 1980) '] >= 1990) & (df['Please enter your 4-digit year of birth(e.g., 1980) '] < 2000)]),
        '2000s': len(df[df['Please enter your 4-digit year of birth(e.g., 1980) '] >= 2000])
    }
}

print(f"\nStatistics calculated:")
print(f"- Total: {summary_stats['total_participants']}")
print(f"- Brightness distribution: {summary_stats['brightness_distribution']}")
print(f"- Tone distribution: {summary_stats['tone_distribution']}")

# Create analysis data
analysis_data = {
    'total_participants': 133,
    'participant_data': participant_data,
    'summary_stats': summary_stats
}

# Create image mapping
image_dir = Path('images_organized_by_aid')
image_mapping = {}

for idx, row in df.iterrows():
    aid = row['A-ID']
    pid = row['P-ID']
    name = row['What is your full name? (Please write exactly as shown in your ARC or passport)']

    image_mapping[aid] = {
        'pid': str(pid),
        'name': name,
        'row': idx + 2,
        'data': {
            'skin_brightness': str(row['밝기판정']) if pd.notna(row['밝기판정']) else '',
            'skin_tone': row['톤'] if pd.notna(row['톤']) else '',
        },
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

# Count images
image_counts = {
    'face_photo': sum(1 for m in image_mapping.values() if 'face_photo' in m.get('images', {})),
    'skin_brightness': sum(1 for m in image_mapping.values() if 'skin_brightness' in m.get('images', {})),
    'hair': sum(1 for m in image_mapping.values() if 'hair' in m.get('images', {})),
    'eye_color': sum(1 for m in image_mapping.values() if 'eye_color' in m.get('images', {}))
}
print(f"\nImage counts: {image_counts}")

# Create the HTML
html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Amore Pacific Foundation Consumer Test 2025 (with famigo)</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>💄</text></svg>">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        .header h1 {
            color: #333;
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        .header .subtitle {
            color: #666;
            font-size: 1.2rem;
        }
        .stats-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            color: #666;
            font-size: 0.9rem;
            margin-top: 5px;
        }
        .main-content {
            display: grid;
            grid-template-columns: 350px 1fr;
            gap: 30px;
        }
        .sidebar {
            background: white;
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            height: fit-content;
        }
        .filters {
            margin-bottom: 20px;
        }
        .filter-group {
            margin-bottom: 15px;
        }
        .filter-group label {
            display: block;
            margin-bottom: 5px;
            color: #333;
            font-weight: 500;
        }
        .filter-group select, .filter-group input {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
        }
        .participant-list {
            max-height: 600px;
            overflow-y: auto;
        }
        .participant-item {
            padding: 10px;
            border: 1px solid #eee;
            border-radius: 8px;
            margin-bottom: 10px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .participant-item:hover {
            background: #f8f9fa;
            transform: translateX(5px);
        }
        .participant-item.active {
            background: #667eea;
            color: white;
        }
        .content-area {
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        .participant-detail {
            display: none;
        }
        .participant-detail.active {
            display: block;
        }
        .detail-header {
            border-bottom: 2px solid #eee;
            padding-bottom: 20px;
            margin-bottom: 20px;
        }
        .detail-header h2 {
            color: #333;
            margin-bottom: 10px;
        }
        .detail-info {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            color: #666;
        }
        .images-section {
            margin-top: 30px;
        }
        .images-container {
            display: flex;
            gap: 20px;
            align-items: stretch;
        }
        .face-photo-container {
            flex: 0 0 50%;
        }
        .face-photo-container img {
            width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        .reference-images {
            flex: 0 0 50%;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .reference-image {
            flex: 1;
            min-height: 150px;
            display: flex;
            flex-direction: column;
        }
        .reference-image h4 {
            color: #666;
            margin-bottom: 10px;
            font-size: 0.9rem;
        }
        .reference-image img {
            width: 100%;
            height: 150px;
            object-fit: contain;
            border-radius: 8px;
            border: 1px solid #eee;
            background: #f8f9fa;
        }
        .charts-section {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 30px;
            margin-top: 30px;
        }
        .chart-container {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        .chart-container h3 {
            margin-bottom: 15px;
            color: #333;
        }
        .no-image {
            display: flex;
            align-items: center;
            justify-content: center;
            background: #f0f0f0;
            color: #999;
            border-radius: 10px;
            height: 100%;
            min-height: 200px;
        }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Amore Pacific Foundation Consumer Test 2025 (with famigo)</h1>
            <div class="subtitle">Data Report: 9월 22일 ~ 26일, 2025년</div>
        </div>

        <div class="stats-row" id="statsRow"></div>

        <div class="main-content">
            <div class="sidebar">
                <div class="filters">
                    <div class="filter-group">
                        <label>Search by Name/ID</label>
                        <input type="text" id="searchInput" placeholder="Enter name or ID...">
                    </div>
                    <div class="filter-group">
                        <label>Filter by Skin Brightness</label>
                        <select id="brightnessFilter">
                            <option value="">All</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>Filter by Skin Tone</label>
                        <select id="toneFilter">
                            <option value="">All</option>
                        </select>
                    </div>
                </div>
                <div class="participant-list" id="participantList"></div>
            </div>

            <div class="content-area">
                <div id="welcomeMessage">
                    <h2>Welcome to the Dashboard</h2>
                    <p>Select a participant from the list to view their details.</p>
                </div>
                <div id="participantDetail" class="participant-detail"></div>
            </div>
        </div>

        <div class="charts-section">
            <div class="chart-container">
                <h3>Skin Brightness Distribution</h3>
                <canvas id="brightnessChart"></canvas>
            </div>
            <div class="chart-container">
                <h3>Skin Tone Distribution</h3>
                <canvas id="toneChart"></canvas>
            </div>
        </div>
    </div>

    <script>
        // Embed data directly
        let allParticipants = ''' + json.dumps(participant_data, ensure_ascii=False) + ''';
        let analysisData = ''' + json.dumps(analysis_data, ensure_ascii=False) + ''';
        let imageMapping = ''' + json.dumps(image_mapping, ensure_ascii=False) + ''';

        // Display functions
        function updateStatistics() {
            const stats = analysisData.summary_stats;
            const statsRow = document.getElementById('statsRow');

            const statCards = [
                { label: 'Total Participants', value: stats.total_participants },
                { label: 'Female', value: stats.gender_distribution['Female'] || 0 },
                { label: 'Male', value: stats.gender_distribution['Male'] || 0 },
                { label: 'Warm Tone', value: stats.tone_distribution['Warm'] || 0 },
                { label: 'Cool Tone', value: stats.tone_distribution['Cool'] || 0 },
                { label: 'Neutral Tone', value: stats.tone_distribution['Neutral'] || 0 }
            ];

            statsRow.innerHTML = statCards.map(stat => `
                <div class="stat-card">
                    <div class="stat-number">${stat.value}</div>
                    <div class="stat-label">${stat.label}</div>
                </div>
            `).join('');
        }

        function displayParticipants(participants) {
            const listElement = document.getElementById('participantList');
            listElement.innerHTML = participants.map(p => `
                <div class="participant-item" data-aid="${p['A-ID']}">
                    <strong>${p['A-ID']}</strong> - ${p['P-ID']}<br>
                    <small>${p['What is your full name? (Please write exactly as shown in your ARC or passport)']}</small>
                </div>
            `).join('');

            // Add click handlers
            document.querySelectorAll('.participant-item').forEach(item => {
                item.addEventListener('click', () => {
                    document.querySelectorAll('.participant-item').forEach(i => i.classList.remove('active'));
                    item.classList.add('active');
                    showParticipantDetail(item.dataset.aid);
                });
            });
        }

        function showParticipantDetail(aid) {
            const participant = allParticipants.find(p => p['A-ID'] === aid);
            const mapping = imageMapping[aid] || {};

            document.getElementById('welcomeMessage').style.display = 'none';

            const detailHtml = `
                <div class="detail-header">
                    <h2>${participant['What is your full name? (Please write exactly as shown in your ARC or passport)']}</h2>
                    <div class="detail-info">
                        <div><strong>A-ID:</strong> ${participant['A-ID']}</div>
                        <div><strong>P-ID:</strong> ${participant['P-ID']}</div>
                        <div><strong>Gender:</strong> ${participant['What is your gender? '] || 'N/A'}</div>
                        <div><strong>Nationality:</strong> ${participant['What is your nationality?'] || 'N/A'}</div>
                        <div><strong>Skin Brightness:</strong> ${participant['밝기판정'] || 'N/A'}</div>
                        <div><strong>Skin Tone:</strong> ${participant['톤'] || 'N/A'}</div>
                    </div>
                </div>

                <div class="images-section">
                    <h3>Images</h3>
                    <div class="images-container">
                        <div class="face-photo-container">
                            ${mapping.images?.face_photo ?
                                `<img src="${mapping.images.face_photo}" alt="Face Photo">` :
                                '<div class="no-image">No Face Photo Available</div>'}
                        </div>

                        <div class="reference-images">
                            <div class="reference-image">
                                <h4>Skin Brightness Reference</h4>
                                ${mapping.images?.skin_brightness ?
                                    `<img src="${mapping.images.skin_brightness}" alt="Skin Brightness">` :
                                    '<div class="no-image">No Image</div>'}
                            </div>
                            <div class="reference-image">
                                <h4>Hair Reference</h4>
                                ${mapping.images?.hair ?
                                    `<img src="${mapping.images.hair}" alt="Hair">` :
                                    '<div class="no-image">No Image</div>'}
                            </div>
                            <div class="reference-image">
                                <h4>Eye Color Reference</h4>
                                ${mapping.images?.eye_color ?
                                    `<img src="${mapping.images.eye_color}" alt="Eye Color">` :
                                    '<div class="no-image">No Image</div>'}
                            </div>
                        </div>
                    </div>
                </div>
            `;

            document.getElementById('participantDetail').innerHTML = detailHtml;
            document.getElementById('participantDetail').classList.add('active');
        }

        function initializeFilters() {
            // Populate brightness filter
            const brightnessValues = [...new Set(allParticipants.map(p => p['밝기판정']).filter(v => v))];
            const brightnessFilter = document.getElementById('brightnessFilter');
            brightnessValues.forEach(value => {
                brightnessFilter.innerHTML += `<option value="${value}">${value}</option>`;
            });

            // Populate tone filter
            const toneValues = [...new Set(allParticipants.map(p => p['톤']).filter(v => v))];
            const toneFilter = document.getElementById('toneFilter');
            toneValues.forEach(value => {
                toneFilter.innerHTML += `<option value="${value}">${value}</option>`;
            });

            // Add filter handlers
            const applyFilters = () => {
                let filtered = [...allParticipants];

                const searchTerm = document.getElementById('searchInput').value.toLowerCase();
                if (searchTerm) {
                    filtered = filtered.filter(p =>
                        p['A-ID'].toLowerCase().includes(searchTerm) ||
                        p['P-ID'].toLowerCase().includes(searchTerm) ||
                        p['What is your full name? (Please write exactly as shown in your ARC or passport)'].toLowerCase().includes(searchTerm)
                    );
                }

                const brightness = document.getElementById('brightnessFilter').value;
                if (brightness) {
                    filtered = filtered.filter(p => p['밝기판정'] == brightness);
                }

                const tone = document.getElementById('toneFilter').value;
                if (tone) {
                    filtered = filtered.filter(p => p['톤'] === tone);
                }

                displayParticipants(filtered);
            };

            document.getElementById('searchInput').addEventListener('input', applyFilters);
            document.getElementById('brightnessFilter').addEventListener('change', applyFilters);
            document.getElementById('toneFilter').addEventListener('change', applyFilters);
        }

        function initializeCharts() {
            // Brightness chart
            const brightnessCtx = document.getElementById('brightnessChart').getContext('2d');
            const brightnessData = analysisData.summary_stats.brightness_distribution;

            new Chart(brightnessCtx, {
                type: 'doughnut',
                data: {
                    labels: Object.keys(brightnessData),
                    datasets: [{
                        data: Object.values(brightnessData),
                        backgroundColor: [
                            '#FF6384',
                            '#36A2EB',
                            '#FFCE56',
                            '#4BC0C0',
                            '#9966FF'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true
                }
            });

            // Tone chart
            const toneCtx = document.getElementById('toneChart').getContext('2d');
            const toneData = analysisData.summary_stats.tone_distribution;

            new Chart(toneCtx, {
                type: 'doughnut',
                data: {
                    labels: Object.keys(toneData),
                    datasets: [{
                        data: Object.values(toneData),
                        backgroundColor: [
                            '#FF9F40',
                            '#FF6384',
                            '#4BC0C0',
                            '#9966FF'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true
                }
            });
        }

        // Initialize on page load
        window.addEventListener('DOMContentLoaded', () => {
            console.log('Total participants:', allParticipants.length);
            displayParticipants(allParticipants);
            updateStatistics();
            initializeCharts();
            initializeFilters();
        });
    </script>
</body>
</html>'''

# Save the new dashboard
with open('makeup-test-dashboard-v1.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("\n=== Dashboard V1 Created ===")
print(f"✓ Total participants: 133")
print(f"✓ A216 included: {a216_exists}")
print(f"✓ Statistics correctly show 133 participants")
print(f"✓ All data embedded in HTML")
print("\nNew dashboard saved as makeup-test-dashboard-v1.html")