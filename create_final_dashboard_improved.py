#!/usr/bin/env python3
"""
Create improved final dashboard with base products chart and better layout
"""

import pandas as pd
import json
from pathlib import Path
from collections import Counter

# Load Excel data
df = pd.read_excel('/Users/owlers_dylan/APCLT/makeuptest_AP_Bueatylink_20250927.xlsx')
print(f"Loaded {len(df)} participants")

# Analyze base products usage
base_products_column = 'Please select all face/base makeup products you typically use: for your daily makeup routine (Select at least one)'
all_products = []

for product_list in df[base_products_column].dropna():
    if isinstance(product_list, str):
        # Split by newline or comma
        products = [p.strip() for p in product_list.replace('\n', ',').split(',') if p.strip()]
        all_products.extend(products)

# Count product frequencies
product_counts = Counter(all_products)
print(f"\nBase Products Usage:")
for product, count in product_counts.most_common():
    print(f"  {product}: {count}")

# Create participant data
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
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        .header {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}
        .stat-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }}
        .stat-number {{
            font-size: 2.5rem;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .table-container {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}
        .skin-img {{
            width: 40px;
            height: 40px;
            object-fit: contain;
            border-radius: 8px;
            border: 1px solid #ddd;
            background: #f8f9fa;
        }}
        .tone-warm {{ background: #ff9068; color: white; padding: 5px 10px; border-radius: 15px; }}
        .tone-cool {{ background: #68a8ff; color: white; padding: 5px 10px; border-radius: 15px; }}
        .tone-neutral {{ background: #a8a8a8; color: white; padding: 5px 10px; border-radius: 15px; }}
        .tone-olive {{ background: #8b9467; color: white; padding: 5px 10px; border-radius: 15px; }}
        .btn-details {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 5px 15px;
            border-radius: 20px;
            transition: transform 0.2s;
        }}
        .btn-details:hover {{
            transform: scale(1.05);
            color: white;
        }}
        .modal-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        .info-section {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
        }}
        .info-section h5 {{
            color: #333;
            margin-bottom: 15px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .ref-img {{
            width: 100%;
            height: 150px;
            object-fit: contain;
            border-radius: 12px;
            border: 1px solid #e0e0e0;
            background: white;
            padding: 5px;
        }}
        .face-img {{
            width: 100%;
            max-width: 300px;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }}
        .beauty-question {{
            font-weight: 600;
            color: #555;
            font-size: 0.9rem;
            margin-top: 10px;
        }}
        .beauty-answer {{
            color: #333;
            margin-bottom: 10px;
        }}
        .chart-container {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
        }}
        .no-image {{
            height: 150px;
            background: #f0f0f0;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 12px;
            color: #999;
        }}
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="header">
            <h1>Amore Pacific Foundation Consumer Test 2025 (with famigo)</h1>
            <p class="mb-0">Data Report: 9월 22일 ~ 26일, 2025년 | Total: {stats['total']} participants</p>
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
                    <div>Warm Tone</div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="stat-card">
                    <div class="stat-number">{stats['cool']}</div>
                    <div>Cool Tone</div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="stat-card">
                    <div class="stat-number">{stats['neutral']}</div>
                    <div>Neutral Tone</div>
                </div>
            </div>
        </div>

        <div class="table-container">
            <table id="dataTable" class="table table-hover">
                <thead class="table-dark">
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
        const productCounts = {json.dumps(dict(product_counts), ensure_ascii=False)};

        console.log('Loaded', data.length, 'participants');

        // Show details
        function showDetails(aid) {{
            const p = data.find(x => x['A-ID'] === aid);
            const img = imgs[aid] || {{}};

            // Parse base products for this participant
            let userProducts = [];
            const productsStr = p['Please select all face/base makeup products you typically use: for your daily makeup routine (Select at least one)'];
            if (productsStr) {{
                userProducts = productsStr.replace(/\\n/g, ',').split(',').map(x => x.trim()).filter(x => x);
            }}

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
                            <p><strong>Ethnic Group:</strong> ${{p['Please select the ethnic group you identify with:'] || '-'}}</p>
                            <p><strong>Skin Brightness:</strong> ${{p['밝기판정'] || '-'}} | <strong>Tone:</strong> ${{p['톤'] || '-'}}</p>
                        </div>
                    </div>
                </div>

                <div class="row">
                    <div class="col-md-8">
                        <div class="info-section">
                            <h5>Beauty & Cosmetics</h5>
                            <div class="beauty-question">Makeup Frequency</div>
                            <div class="beauty-answer">${{p['How often do you usually apply face makeup? '] || '-'}}</div>

                            <div class="beauty-question">Store Visits</div>
                            <div class="beauty-answer">${{p['How many times do you visit cosmetic store?'] || '-'}}</div>

                            <div class="beauty-question">Skin Type</div>
                            <div class="beauty-answer">${{p['What is your skin type?'] || '-'}}</div>

                            <div class="beauty-question">Preferred Look</div>
                            <div class="beauty-answer">${{p['Which of the following makeup looks do you prefer the most after applying makeup?'] || '-'}}</div>

                            <div class="beauty-question">Cushion Foundation Usage</div>
                            <div class="beauty-answer">${{p['Have you ever used a cushion foundation?'] || '-'}}</div>

                            <div class="beauty-question">Sunscreen Usage</div>
                            <div class="beauty-answer">${{p['How often do you usually use sunscreen products?'] || '-'}}</div>
                        </div>
                    </div>

                    <div class="col-md-4">
                        <div class="info-section text-center">
                            <h5>Face Photo</h5>
                            ${{img.face ? `<img src="${{img.face}}" class="face-img">` : '<div style="height:250px;background:#f0f0f0;display:flex;align-items:center;justify-content:center;border-radius:12px">No Face Photo</div>'}}
                        </div>
                    </div>
                </div>

                <div class="row">
                    <div class="col-md-6">
                        <div class="info-section">
                            <h5>Base Products Used</h5>
                            ${{userProducts.length > 0 ?
                                '<ul>' + userProducts.map(prod => `<li>${{prod}}</li>`).join('') + '</ul>' :
                                '<p>No products specified</p>'
                            }}
                        </div>
                    </div>

                    <div class="col-md-6">
                        <div class="chart-container">
                            <h5>Base Products Composition (All Participants)</h5>
                            <canvas id="productChart" width="400" height="200"></canvas>
                        </div>
                    </div>
                </div>

                <div class="info-section">
                    <h5>Reference Images</h5>
                    <div class="row">
                        <div class="col-md-4">
                            ${{img.skin ? `<img src="${{img.skin}}" class="ref-img">` : '<div class="no-image">No Image</div>'}}
                            <p class="text-center mt-2">Skin Brightness Reference</p>
                        </div>
                        <div class="col-md-4">
                            ${{img.hair ? `<img src="${{img.hair}}" class="ref-img">` : '<div class="no-image">No Image</div>'}}
                            <p class="text-center mt-2">Hair Reference</p>
                        </div>
                        <div class="col-md-4">
                            ${{img.eye ? `<img src="${{img.eye}}" class="ref-img">` : '<div class="no-image">No Image</div>'}}
                            <p class="text-center mt-2">Eye Color Reference</p>
                        </div>
                    </div>
                </div>
            `;

            $('#modalBody').html(html);
            $('#detailModal').modal('show');

            // Create product chart
            setTimeout(() => {{
                const ctx = document.getElementById('productChart');
                if (ctx) {{
                    new Chart(ctx, {{
                        type: 'doughnut',
                        data: {{
                            labels: Object.keys(productCounts),
                            datasets: [{{
                                data: Object.values(productCounts),
                                backgroundColor: [
                                    '#FF6384',
                                    '#36A2EB',
                                    '#FFCE56',
                                    '#4BC0C0',
                                    '#9966FF',
                                    '#FF9F40',
                                    '#FF6384',
                                    '#C9CBCF'
                                ]
                            }}]
                        }},
                        options: {{
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {{
                                legend: {{
                                    position: 'right',
                                    labels: {{
                                        font: {{
                                            size: 10
                                        }}
                                    }}
                                }}
                            }}
                        }}
                    }});
                }}
            }}, 100);
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
                        <td><strong>${{p['A-ID']}}</strong></td>
                        <td>${{p['P-ID']}}</td>
                        <td>${{p['What is your full name? (Please write exactly as shown in your ARC or passport)']}}</td>
                        <td>${{p['What is your gender? '] || '-'}}</td>
                        <td>${{p['What is your nationality?'] || '-'}}</td>
                        <td>${{p['Please enter your 4-digit year of birth(e.g., 1980) '] || '-'}}</td>
                        <td>${{img.skin ? `<img src="${{img.skin}}" class="skin-img" title="Brightness: ${{p['밝기판정']}}">` : p['밝기판정'] || '-'}}</td>
                        <td>${{tone ? `<span class="${{toneClass}}">${{tone}}</span>` : '-'}}</td>
                        <td>${{p['Please select the ethnic group you identify with:'] || '-'}}</td>
                        <td><button class="btn-details" onclick="showDetails('${{p['A-ID']}}')">View Details</button></td>
                    </tr>
                `;
            }});

            $('#tableBody').html(rows);
            $('#dataTable').DataTable({{
                pageLength: 25,
                responsive: true,
                order: [[0, 'asc']],
                language: {{
                    search: "Search participants:",
                    lengthMenu: "Show _MENU_ participants",
                    info: "Showing _START_ to _END_ of _TOTAL_ participants"
                }}
            }});
        }});
    </script>
</body>
</html>'''

# Save as makeup-test-dashboard.html (final name)
with open('makeup-test-dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("\n✅ Dashboard created successfully!")
print(f"- Saved as: makeup-test-dashboard.html")
print(f"- Total: {len(df)} participants")
print(f"- Base products chart added")
print(f"- Face photo placed next to Beauty section")
print(f"- Ready for external sharing!")