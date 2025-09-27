#!/usr/bin/env python3
"""
Create final working dashboard - complete rebuild
"""

import pandas as pd
import json
from pathlib import Path

# Load Excel data
df = pd.read_excel('/Users/owlers_dylan/APCLT/makeuptest_AP_Bueatylink_20250927.xlsx')
print(f"Loaded {len(df)} participants")

# Verify A216
if 'A216' in df['A-ID'].values:
    a216 = df[df['A-ID'] == 'A216'].iloc[0]
    print(f"A216: {a216['What is your full name? (Please write exactly as shown in your ARC or passport)']}")

# Create participant data as simple list
participants = []
for _, row in df.iterrows():
    p = {}
    for col in df.columns:
        val = row[col]
        if pd.isna(val):
            p[col] = None
        elif isinstance(val, (int, float)):
            p[col] = val
        else:
            p[col] = str(val)
    participants.append(p)

# Stats
stats = {
    'total': len(df),
    'female': len(df[df['What is your gender? '] == 'Female']),
    'male': len(df[df['What is your gender? '] == 'Male']),
    'warm': len(df[df['톤'] == 'Warm']),
    'cool': len(df[df['톤'] == 'Cool']),
    'neutral': len(df[df['톤'] == 'Neutral'])
}

# Images
image_dir = Path('images_organized_by_aid')
images = {}
for _, row in df.iterrows():
    aid = row['A-ID']
    images[aid] = {}

    face = image_dir / f'{aid}_face_photo.jpg'
    if face.exists():
        images[aid]['face'] = f'images_organized_by_aid/{aid}_face_photo.jpg'

    skin = image_dir / f'{aid}_skin_brightness.png'
    if skin.exists():
        images[aid]['skin'] = f'images_organized_by_aid/{aid}_skin_brightness.png'

    hair = image_dir / f'{aid}_hair.png'
    if hair.exists():
        images[aid]['hair'] = f'images_organized_by_aid/{aid}_hair.png'

    eye = image_dir / f'{aid}_eye_color.png'
    if eye.exists():
        images[aid]['eye'] = f'images_organized_by_aid/{aid}_eye_color.png'

# Create HTML
html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Amore Pacific Foundation Consumer Test 2025</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>💄</text></svg>">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css">
    <style>
        body {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }}
        .header {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            text-align: center;
        }}
        .stat-number {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #667eea;
        }}
        .table-container {{
            background: white;
            border-radius: 15px;
            padding: 25px;
        }}
        .skin-img {{
            width: 40px;
            height: 40px;
            object-fit: contain;
            border-radius: 8px;
            border: 1px solid #ddd;
        }}
        .tone-warm {{ background: #ff9068; color: white; padding: 5px 10px; border-radius: 15px; }}
        .tone-cool {{ background: #68a8ff; color: white; padding: 5px 10px; border-radius: 15px; }}
        .tone-neutral {{ background: #a8a8a8; color: white; padding: 5px 10px; border-radius: 15px; }}
        .tone-olive {{ background: #8b9467; color: white; padding: 5px 10px; border-radius: 15px; }}
        .btn-details {{
            background: #667eea;
            color: white;
            border: none;
            padding: 5px 15px;
            border-radius: 20px;
        }}
        .modal-header {{
            background: #667eea;
            color: white;
        }}
        .info-section {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .ref-img {{
            width: 100%;
            height: 150px;
            object-fit: contain;
            border-radius: 12px;
            border: 1px solid #e0e0e0;
        }}
        .face-img {{
            max-width: 400px;
            width: 100%;
            border-radius: 12px;
        }}
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="header">
            <h1>Amore Pacific Foundation Consumer Test 2025 (with famigo)</h1>
            <p>Data Report: 9월 22일 ~ 26일, 2025년 | Total: {stats['total']} participants</p>
        </div>

        <div class="row">
            <div class="col-md-2">
                <div class="stat-card">
                    <div class="stat-number">{stats['total']}</div>
                    <div>Total</div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="stat-card">
                    <div class="stat-number">{stats['female']}</div>
                    <div>Female</div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="stat-card">
                    <div class="stat-number">{stats['male']}</div>
                    <div>Male</div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="stat-card">
                    <div class="stat-number">{stats['warm']}</div>
                    <div>Warm</div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="stat-card">
                    <div class="stat-number">{stats['cool']}</div>
                    <div>Cool</div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="stat-card">
                    <div class="stat-number">{stats['neutral']}</div>
                    <div>Neutral</div>
                </div>
            </div>
        </div>

        <div class="table-container">
            <table id="dataTable" class="table">
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
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody id="tableBody"></tbody>
            </table>
        </div>
    </div>

    <!-- Modal -->
    <div class="modal fade" id="detailModal" tabindex="-1">
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Participant Details</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body" id="modalBody"></div>
            </div>
        </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
    <script>
        // Data
        const data = {json.dumps(participants, ensure_ascii=False)};
        const imgs = {json.dumps(images, ensure_ascii=False)};

        console.log('Loaded', data.length, 'participants');

        // Show details
        function showDetails(aid) {{
            const p = data.find(x => x['A-ID'] === aid);
            const img = imgs[aid] || {{}};

            let html = `
                <div class="info-section">
                    <h5>Basic Information</h5>
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>A-ID:</strong> ${{p['A-ID']}}</p>
                            <p><strong>P-ID:</strong> ${{p['P-ID']}}</p>
                            <p><strong>Name:</strong> ${{p['What is your full name? (Please write exactly as shown in your ARC or passport)']}}</p>
                            <p><strong>Gender:</strong> ${{p['What is your gender? '] || '-'}}</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Nationality:</strong> ${{p['What is your nationality?'] || '-'}}</p>
                            <p><strong>Birth Year:</strong> ${{p['Please enter your 4-digit year of birth(e.g., 1980) '] || '-'}}</p>
                            <p><strong>Skin Brightness:</strong> ${{p['밝기판정'] || '-'}}</p>
                            <p><strong>Skin Tone:</strong> ${{p['톤'] || '-'}}</p>
                        </div>
                    </div>
                </div>

                <div class="info-section">
                    <h5>Beauty & Cosmetics</h5>
                    <p><strong>Makeup Frequency:</strong> ${{p['How often do you usually apply face makeup? '] || '-'}}</p>
                    <p><strong>Store Visits:</strong> ${{p['How many times do you visit cosmetic store?'] || '-'}}</p>
                    <p><strong>Skin Type:</strong> ${{p['What is your skin type?'] || '-'}}</p>
                    <p><strong>Preferred Look:</strong> ${{p['Which of the following makeup looks do you prefer the most after applying makeup?'] || '-'}}</p>
                    <p><strong>Base Products:</strong> ${{p['Please select all face/base makeup products you typically use: for your daily makeup routine (Select at least one)'] || '-'}}</p>
                    <p><strong>Cushion Usage:</strong> ${{p['Have you ever used a cushion foundation?'] || '-'}}</p>
                </div>

                <div class="info-section">
                    <h5>Reference Images</h5>
                    <div class="row">
                        <div class="col-md-3">
                            ${{img.skin ? `<img src="${{img.skin}}" class="ref-img">` : '<div style="height:150px;background:#f0f0f0;display:flex;align-items:center;justify-content:center;border-radius:12px">No Image</div>'}}
                            <p class="text-center mt-2">Skin Brightness</p>
                        </div>
                        <div class="col-md-3">
                            ${{img.hair ? `<img src="${{img.hair}}" class="ref-img">` : '<div style="height:150px;background:#f0f0f0;display:flex;align-items:center;justify-content:center;border-radius:12px">No Image</div>'}}
                            <p class="text-center mt-2">Hair</p>
                        </div>
                        <div class="col-md-3">
                            ${{img.eye ? `<img src="${{img.eye}}" class="ref-img">` : '<div style="height:150px;background:#f0f0f0;display:flex;align-items:center;justify-content:center;border-radius:12px">No Image</div>'}}
                            <p class="text-center mt-2">Eye Color</p>
                        </div>
                    </div>
                </div>

                <div class="info-section text-center">
                    <h5>Face Photo</h5>
                    ${{img.face ? `<img src="${{img.face}}" class="face-img">` : '<div style="height:300px;background:#f0f0f0;display:flex;align-items:center;justify-content:center;border-radius:12px">No Face Photo</div>'}}
                </div>
            `;

            $('#modalBody').html(html);
            $('#detailModal').modal('show');
        }}

        // Build table
        $(document).ready(function() {{
            let rows = '';
            data.forEach(p => {{
                const img = imgs[p['A-ID']] || {{}};
                const tone = p['톤'] || '';
                let toneClass = '';
                if (tone.includes('Warm')) toneClass = 'tone-warm';
                else if (tone.includes('Cool')) toneClass = 'tone-cool';
                else if (tone.includes('Neutral')) toneClass = 'tone-neutral';
                else if (tone.includes('Olive')) toneClass = 'tone-olive';

                rows += `
                    <tr>
                        <td>${{p['A-ID']}}</td>
                        <td>${{p['P-ID']}}</td>
                        <td>${{p['What is your full name? (Please write exactly as shown in your ARC or passport)']}}</td>
                        <td>${{p['What is your gender? '] || '-'}}</td>
                        <td>${{p['What is your nationality?'] || '-'}}</td>
                        <td>${{p['Please enter your 4-digit year of birth(e.g., 1980) '] || '-'}}</td>
                        <td>${{img.skin ? `<img src="${{img.skin}}" class="skin-img" title="${{p['밝기판정']}}">` : p['밝기판정'] || '-'}}</td>
                        <td>${{tone ? `<span class="${{toneClass}}">${{tone}}</span>` : '-'}}</td>
                        <td><button class="btn-details" onclick="showDetails('${{p['A-ID']}}')">View</button></td>
                    </tr>
                `;
            }});

            $('#tableBody').html(rows);
            $('#dataTable').DataTable({{
                pageLength: 25,
                order: [[0, 'asc']]
            }});
        }});
    </script>
</body>
</html>'''

# Save
with open('makeup-test-dashboard-final.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("\n✅ Dashboard created successfully!")
print(f"- Total: {len(df)} participants")
print(f"- Stats: Female={stats['female']}, Male={stats['male']}")
print(f"- Tones: Warm={stats['warm']}, Cool={stats['cool']}, Neutral={stats['neutral']}")
print("\nSaved as makeup-test-dashboard-final.html")