#!/usr/bin/env python3
"""
Create a table-based dashboard with all participant details visible
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
    'nationality_distribution': df['What is your nationality?'].value_counts().head(10).to_dict(),
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
        .btn-view-images {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85rem;
            transition: transform 0.2s;
        }
        .btn-view-images:hover {
            transform: scale(1.05);
            color: white;
        }
        .modal-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .modal-body {
            padding: 30px;
        }
        .image-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        }
        .image-item {
            text-align: center;
        }
        .image-item img {
            width: 100%;
            max-height: 300px;
            object-fit: contain;
            border-radius: 10px;
            border: 1px solid #ddd;
            background: #f8f9fa;
        }
        .image-item h6 {
            margin-top: 10px;
            color: #666;
        }
        .participant-info {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .participant-info h5 {
            color: #333;
            margin-bottom: 15px;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }
        .info-item {
            padding: 5px 0;
        }
        .info-label {
            font-weight: 600;
            color: #555;
        }
        .info-value {
            color: #333;
        }
        .filters-container {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        .filter-group {
            display: inline-block;
            margin-right: 20px;
            margin-bottom: 10px;
        }
        .filter-group label {
            margin-right: 10px;
            font-weight: 500;
            color: #555;
        }
        .filter-group select {
            padding: 5px 10px;
            border-radius: 5px;
            border: 1px solid #ddd;
        }
        .badge-brightness {
            background: #ff6b6b;
            color: white;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.85rem;
        }
        .badge-tone {
            background: #4ecdc4;
            color: white;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.85rem;
        }
        .no-image {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 200px;
            background: #f0f0f0;
            color: #999;
            border-radius: 10px;
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
                        <th>Images</th>
                    </tr>
                </thead>
                <tbody id="tableBody">
                </tbody>
            </table>
        </div>
    </div>

    <!-- Image Modal -->
    <div class="modal fade" id="imageModal" tabindex="-1">
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="modalTitle">Participant Images</h5>
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

        // Show participant images
        function showImages(aid) {
            const participant = allParticipants.find(p => p['A-ID'] === aid);
            const mapping = imageMapping[aid];

            const modalTitle = document.getElementById('modalTitle');
            const modalBody = document.getElementById('modalBody');

            modalTitle.textContent = `${participant['What is your full name? (Please write exactly as shown in your ARC or passport)']} (${aid})`;

            let modalContent = `
                <div class="participant-info">
                    <h5>Participant Information</h5>
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
                            <span class="info-value">${participant['톤'] || 'N/A'}</span>
                        </div>
                    </div>
                </div>

                <h5>Images</h5>
                <div class="image-grid">`;

            // Add face photo
            if (mapping.images.face_photo) {
                modalContent += `
                    <div class="image-item">
                        <img src="${mapping.images.face_photo}" alt="Face Photo">
                        <h6>Face Photo</h6>
                    </div>`;
            } else {
                modalContent += `
                    <div class="image-item">
                        <div class="no-image">No Face Photo</div>
                        <h6>Face Photo</h6>
                    </div>`;
            }

            // Add skin brightness
            if (mapping.images.skin_brightness) {
                modalContent += `
                    <div class="image-item">
                        <img src="${mapping.images.skin_brightness}" alt="Skin Brightness">
                        <h6>Skin Brightness Reference</h6>
                    </div>`;
            } else {
                modalContent += `
                    <div class="image-item">
                        <div class="no-image">No Image</div>
                        <h6>Skin Brightness Reference</h6>
                    </div>`;
            }

            // Add hair
            if (mapping.images.hair) {
                modalContent += `
                    <div class="image-item">
                        <img src="${mapping.images.hair}" alt="Hair">
                        <h6>Hair Reference</h6>
                    </div>`;
            } else {
                modalContent += `
                    <div class="image-item">
                        <div class="no-image">No Image</div>
                        <h6>Hair Reference</h6>
                    </div>`;
            }

            // Add eye color
            if (mapping.images.eye_color) {
                modalContent += `
                    <div class="image-item">
                        <img src="${mapping.images.eye_color}" alt="Eye Color">
                        <h6>Eye Color Reference</h6>
                    </div>`;
            } else {
                modalContent += `
                    <div class="image-item">
                        <div class="no-image">No Image</div>
                        <h6>Eye Color Reference</h6>
                    </div>`;
            }

            modalContent += '</div>';
            modalBody.innerHTML = modalContent;

            const modal = new bootstrap.Modal(document.getElementById('imageModal'));
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

                tableHtml += `
                    <tr>
                        <td><strong>${participant['A-ID']}</strong></td>
                        <td>${participant['P-ID']}</td>
                        <td>${participant['What is your full name? (Please write exactly as shown in your ARC or passport)']}</td>
                        <td>${participant['What is your gender? '] || '-'}</td>
                        <td>${participant['What is your nationality?'] || '-'}</td>
                        <td>${participant['Please enter your 4-digit year of birth(e.g., 1980) '] || '-'}</td>
                        <td><span class="badge-brightness">${participant['밝기판정'] || '-'}</span></td>
                        <td><span class="badge-tone">${participant['톤'] || '-'}</span></td>
                        <td>${participant['Please select the ethnic group you identify with:'] || '-'}</td>
                        <td>
                            ${hasImages ?
                                `<button class="btn btn-view-images" onclick="showImages('${participant['A-ID']}')">View Images</button>` :
                                '<span class="text-muted">No Images</span>'}
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
with open('makeup-test-dashboard-table.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("\n=== Table Dashboard Created ===")
print(f"✓ Total participants: 133")
print(f"✓ Full table view with all participant details")
print(f"✓ Searchable and sortable DataTable")
print(f"✓ Image modal popup for viewing")
print("\nNew dashboard saved as makeup-test-dashboard-table.html")