#!/usr/bin/env python3
"""
Create dashboard with dynamic makeup visualization
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
        products = [p.strip() for p in product_list.replace('\n', ',').split(',') if p.strip()]
        all_products.extend(products)

product_counts = Counter(all_products)

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

# Calculate statistics
stats = {
    'total': len(df),
    'daily_makeup': len(df[df['How often do you usually apply face makeup? '] == 'almost everyday']),
    'cushion_users': len(df[df['Have you ever used a cushion foundation?'] == 'I currently use it']),
    'sunscreen_daily': len(df[df['How often do you usually use sunscreen products?'] == 'Almost everyday']),
    'avg_age': int(2025 - df['Please enter your 4-digit year of birth(e.g., 1980) '].mean()) if not df['Please enter your 4-digit year of birth(e.g., 1980) '].isna().all() else 0
}

# Define skin brightness to color mapping (1-7 scale)
brightness_to_color = {
    '1': '#fde4d0',  # Very fair
    '2': '#fad4b8',  # Fair
    '3': '#f5c09f',  # Light
    '4': '#e8a574',  # Medium
    '5': '#d4895a',  # Medium-dark
    '6': '#b97346',  # Dark
    '7': '#9a5d38'   # Deep
}

# Images
image_dir = Path('images_organized_by_aid')
images = {}
for _, row in df.iterrows():
    aid = row['A-ID']
    images[aid] = {}

    for img_type in ['face_photo', 'skin_brightness', 'hair', 'eye_color']:
        ext = 'jpg' if img_type == 'face_photo' else 'png'
        img_path = image_dir / f'{aid}_{img_type}.{ext}'
        if img_path.exists():
            images[aid][img_type.replace('_photo', '').replace('_', '')] = f'images_organized_by_aid/{aid}_{img_type}.{ext}'

# Create HTML
html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Amore Pacific Foundation Consumer Test 2025</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>💄</text></svg>">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css">
    <link rel="stylesheet" href="https://cdn.datatables.net/responsive/2.5.0/css/responsive.dataTables.min.css">
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

        .stats-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }}

        .stat-number {{
            font-size: 2rem;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .mobile-stats {{
            display: none;
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }}

        @media (max-width: 768px) {{
            .stats-container {{ display: none; }}
            .mobile-stats {{ display: block; }}
            .header h1 {{ font-size: 1.5rem; }}
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

        /* Dynamic face makeup visualization */
        .face-container {{
            position: relative;
            display: inline-block;
        }}

        .face-makeup-visual {{
            position: relative;
            width: 350px;
            height: 450px;
            margin: 0 auto;
            border-radius: 170px 170px 200px 200px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
            transition: all 0.5s ease;
        }}

        .makeup-area {{
            position: absolute;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.65rem;
            color: #fff;
            font-weight: 600;
            text-align: center;
            padding: 3px;
            cursor: pointer;
            transition: all 0.5s ease;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            opacity: 0.3;
            border: 2px solid transparent;
        }}

        .makeup-area.active {{
            opacity: 1;
            animation: glow 2s ease-in-out infinite;
            border: 2px solid rgba(255,255,255,0.6);
        }}

        @keyframes glow {{
            0% {{
                transform: scale(1);
                box-shadow: 0 0 5px rgba(255,255,255,0.5);
            }}
            50% {{
                transform: scale(1.05);
                box-shadow: 0 0 20px rgba(255,255,255,0.8), 0 0 40px rgba(255,255,255,0.4);
            }}
            100% {{
                transform: scale(1);
                box-shadow: 0 0 5px rgba(255,255,255,0.5);
            }}
        }}

        /* Makeup area positions */
        .forehead-area {{
            top: 30px;
            left: 50%;
            transform: translateX(-50%);
            width: 140px;
            height: 50px;
            border-radius: 70px 70px 30px 30px;
        }}

        .temple-left {{
            top: 60px;
            left: 30px;
            width: 50px;
            height: 50px;
        }}

        .temple-right {{
            top: 60px;
            right: 30px;
            width: 50px;
            height: 50px;
        }}

        .eye-area {{
            top: 100px;
            width: 70px;
            height: 35px;
            border-radius: 35px;
        }}
        .eye-left {{ left: 60px; }}
        .eye-right {{ right: 60px; }}

        .under-eye-left {{
            top: 130px;
            left: 65px;
            width: 60px;
            height: 25px;
            border-radius: 30px;
        }}

        .under-eye-right {{
            top: 130px;
            right: 65px;
            width: 60px;
            height: 25px;
            border-radius: 30px;
        }}

        .cheek-area {{
            top: 160px;
            width: 80px;
            height: 80px;
        }}
        .cheek-left {{ left: 40px; }}
        .cheek-right {{ right: 40px; }}

        .nose-bridge {{
            top: 120px;
            left: 50%;
            transform: translateX(-50%);
            width: 30px;
            height: 50px;
            border-radius: 15px;
        }}

        .nose-tip {{
            top: 165px;
            left: 50%;
            transform: translateX(-50%);
            width: 40px;
            height: 30px;
            border-radius: 20px;
        }}

        .lip-area {{
            bottom: 100px;
            left: 50%;
            transform: translateX(-50%);
            width: 90px;
            height: 40px;
            border-radius: 45px;
        }}

        .chin-area {{
            bottom: 40px;
            left: 50%;
            transform: translateX(-50%);
            width: 70px;
            height: 45px;
            border-radius: 35px;
        }}

        .jawline-left {{
            bottom: 60px;
            left: 20px;
            width: 60px;
            height: 40px;
            border-radius: 30px;
        }}

        .jawline-right {{
            bottom: 60px;
            right: 20px;
            width: 60px;
            height: 40px;
            border-radius: 30px;
        }}

        /* Dynamic product colors with gradients */
        .foundation-effect {{
            background: linear-gradient(135deg, rgba(250, 220, 190, 0.7), rgba(245, 200, 160, 0.6));
        }}

        .concealer-effect {{
            background: linear-gradient(135deg, rgba(255, 235, 210, 0.8), rgba(250, 225, 195, 0.7));
        }}

        .cushion-effect {{
            background: radial-gradient(circle, rgba(252, 218, 185, 0.8), rgba(248, 205, 170, 0.6));
        }}

        .blush-effect {{
            background: radial-gradient(ellipse, rgba(255, 182, 193, 0.7), rgba(255, 160, 170, 0.5));
        }}

        .highlighter-effect {{
            background: linear-gradient(135deg, rgba(255, 250, 235, 0.9), rgba(255, 245, 220, 0.7));
        }}

        .contour-effect {{
            background: linear-gradient(135deg, rgba(180, 140, 110, 0.5), rgba(160, 120, 90, 0.4));
        }}

        .lipstick-effect {{
            background: linear-gradient(135deg, rgba(220, 60, 90, 0.7), rgba(200, 40, 70, 0.6));
        }}

        .lip-tint-effect {{
            background: linear-gradient(135deg, rgba(255, 120, 140, 0.6), rgba(240, 100, 120, 0.5));
        }}

        .lip-gloss-effect {{
            background: linear-gradient(135deg, rgba(255, 200, 210, 0.8), rgba(255, 180, 190, 0.6));
        }}

        .primer-effect {{
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.4), rgba(245, 245, 245, 0.3));
        }}

        .face-photo-large {{
            max-width: 650px;
            width: 100%;
            border-radius: 15px;
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.2);
        }}

        .ref-img {{
            width: 100%;
            height: 150px;
            object-fit: contain;
            border-radius: 12px;
            border: 1px solid #e0e0e0;
            background: white;
            padding: 5px;
            position: relative;
        }}

        .ref-value {{
            position: absolute;
            bottom: 10px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(102, 126, 234, 0.9);
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.85rem;
            font-weight: 600;
        }}

        .product-list {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            max-height: 400px;
            overflow-y: auto;
        }}

        .product-item {{
            padding: 8px 12px;
            margin: 5px 0;
            background: white;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            font-size: 0.9rem;
            transition: all 0.3s;
        }}

        .product-item:hover {{
            transform: translateX(5px);
            box-shadow: 0 3px 10px rgba(102, 126, 234, 0.2);
        }}

        .makeup-info {{
            margin-top: 20px;
            padding: 15px;
            background: linear-gradient(135deg, #f8f9fa, #fff);
            border-radius: 10px;
            font-size: 0.85rem;
        }}

        .transformation-label {{
            text-align: center;
            margin-top: 15px;
            font-size: 0.9rem;
            color: #667eea;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="header">
            <h1>Amore Pacific Foundation Consumer Test 2025 (with famigo)</h1>
            <p class="mb-0">Data Report: 9월 22일 ~ 26일, 2025년 | Total: {stats['total']} participants</p>
        </div>

        <!-- Desktop Statistics -->
        <div class="stats-container">
            <div class="stat-card">
                <div class="stat-number">{stats['total']}</div>
                <div class="stat-label">Total Participants</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['avg_age']}</div>
                <div class="stat-label">Average Age</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['daily_makeup']}</div>
                <div class="stat-label">Daily Makeup Users</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['cushion_users']}</div>
                <div class="stat-label">Cushion Users</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['sunscreen_daily']}</div>
                <div class="stat-label">Daily Sunscreen</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(product_counts)}</div>
                <div class="stat-label">Product Types</div>
            </div>
        </div>

        <!-- Mobile Statistics -->
        <div class="mobile-stats">
            <h5 style="color: #667eea; margin-bottom: 15px;">Statistics Overview</h5>
            <div class="mobile-stat-row">
                <span class="mobile-stat-label">Total Participants</span>
                <span class="mobile-stat-value">{stats['total']}</span>
            </div>
            <div class="mobile-stat-row">
                <span class="mobile-stat-label">Average Age</span>
                <span class="mobile-stat-value">{stats['avg_age']} years</span>
            </div>
            <div class="mobile-stat-row">
                <span class="mobile-stat-label">Daily Makeup Users</span>
                <span class="mobile-stat-value">{stats['daily_makeup']}</span>
            </div>
        </div>

        <div class="table-container">
            <table id="dataTable" class="table table-hover responsive nowrap" style="width:100%">
                <thead class="table-dark">
                    <tr>
                        <th>A-ID</th>
                        <th>P-ID</th>
                        <th>Name</th>
                        <th>Gender</th>
                        <th>Nationality</th>
                        <th>Age</th>
                        <th>Brightness</th>
                        <th>Tone</th>
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
    <script src="https://cdn.datatables.net/responsive/2.5.0/js/dataTables.responsive.min.js"></script>
    <script>
        // Data
        const data = {json.dumps(participants, ensure_ascii=False)};
        const imgs = {json.dumps(images, ensure_ascii=False)};
        const brightnessColors = {json.dumps(brightness_to_color, ensure_ascii=False)};

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

            // Get skin brightness color
            const skinBrightness = p['밝기판정'];
            const faceColor = brightnessColors[skinBrightness] || brightnessColors['3'];

            // Parse lip products
            let lipProducts = [];
            const lipStr = p['Please select all the lip makeup products you typically use for your daily makeup routine.'];
            if (lipStr) {{
                lipProducts = lipStr.replace(/\\n/g, ',').split(',').map(x => x.trim()).filter(x => x);
            }}

            // Create dynamic face visualization with products
            let faceVisualization = `
                <div class="face-container">
                    <div class="face-makeup-visual" style="background: ${{faceColor}};">`;

            // Forehead - Foundation/Primer/Base
            if (userProducts.some(p => p.toLowerCase().includes('foundation') || p.includes('BB') || p.includes('CC'))) {{
                faceVisualization += `
                    <div class="makeup-area forehead-area foundation-effect active" title="Foundation applied">
                        Foundation
                    </div>`;
            }}

            // Primer on temples
            if (userProducts.some(p => p.includes('Primer') || p.includes('base'))) {{
                faceVisualization += `
                    <div class="makeup-area temple-left primer-effect active" title="Primer">Prime</div>
                    <div class="makeup-area temple-right primer-effect active" title="Primer">Prime</div>`;
            }}

            // Eyes - Concealer
            if (userProducts.some(p => p.toLowerCase().includes('concealer'))) {{
                faceVisualization += `
                    <div class="makeup-area eye-left concealer-effect active" title="Concealer">Conceal</div>
                    <div class="makeup-area eye-right concealer-effect active" title="Concealer">Conceal</div>
                    <div class="makeup-area under-eye-left concealer-effect active" title="Under-eye concealer"></div>
                    <div class="makeup-area under-eye-right concealer-effect active" title="Under-eye concealer"></div>`;
            }}

            // Cheeks - Cushion/Blush
            if (userProducts.some(p => p.toLowerCase().includes('cushion'))) {{
                faceVisualization += `
                    <div class="makeup-area cheek-left cushion-effect active" title="Cushion">Cushion</div>
                    <div class="makeup-area cheek-right cushion-effect active" title="Cushion">Cushion</div>`;
            }} else if (userProducts.some(p => p.toLowerCase().includes('blush'))) {{
                faceVisualization += `
                    <div class="makeup-area cheek-left blush-effect active" title="Blush">Blush</div>
                    <div class="makeup-area cheek-right blush-effect active" title="Blush">Blush</div>`;
            }}

            // Nose - Highlighter
            if (userProducts.some(p => p.toLowerCase().includes('highlighter'))) {{
                faceVisualization += `
                    <div class="makeup-area nose-bridge highlighter-effect active" title="Highlighter">Glow</div>
                    <div class="makeup-area nose-tip highlighter-effect active" title="Highlighter"></div>`;
            }}

            // Lips - Different lip products
            if (lipProducts.some(p => p.toLowerCase().includes('lipstick'))) {{
                faceVisualization += `
                    <div class="makeup-area lip-area lipstick-effect active" title="Lipstick">Lipstick</div>`;
            }} else if (lipProducts.some(p => p.toLowerCase().includes('tint'))) {{
                faceVisualization += `
                    <div class="makeup-area lip-area lip-tint-effect active" title="Lip tint">Tint</div>`;
            }} else if (lipProducts.some(p => p.toLowerCase().includes('gloss'))) {{
                faceVisualization += `
                    <div class="makeup-area lip-area lip-gloss-effect active" title="Lip gloss">Gloss</div>`;
            }}

            // Contour on jawline/chin
            if (userProducts.some(p => p.toLowerCase().includes('contour'))) {{
                faceVisualization += `
                    <div class="makeup-area jawline-left contour-effect active" title="Contour"></div>
                    <div class="makeup-area jawline-right contour-effect active" title="Contour"></div>
                    <div class="makeup-area chin-area contour-effect active" title="Contour">Contour</div>`;
            }}

            // Tinted moisturizer
            if (userProducts.some(p => p.includes('Tinted'))) {{
                faceVisualization += `
                    <div class="makeup-area forehead-area foundation-effect active" style="opacity: 0.5;" title="Tinted moisturizer"></div>`;
            }}

            faceVisualization += `
                    </div>
                    <div class="transformation-label">✨ Makeup Transformation Visualization</div>
                </div>`;

            let html = `
                <div class="info-section">
                    <h5>Basic Information</h5>
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>A-ID:</strong> ${{p['A-ID']}} | <strong>P-ID:</strong> ${{p['P-ID']}}</p>
                            <p><strong>Name:</strong> ${{p['What is your full name? (Please write exactly as shown in your ARC or passport)']}}</p>
                            <p><strong>Gender:</strong> ${{p['What is your gender? '] || '-'}} | <strong>Age:</strong> ${{p['Please enter your 4-digit year of birth(e.g., 1980) '] ? 2025 - p['Please enter your 4-digit year of birth(e.g., 1980) '] : '-'}}</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Nationality:</strong> ${{p['What is your nationality?'] || '-'}}</p>
                            <p><strong>Ethnic Group:</strong> ${{p['Please select the ethnic group you identify with:'] || '-'}}</p>
                            <p><strong>Skin:</strong> Brightness ${{p['밝기판정'] || '-'}} | Tone ${{p['톤'] || '-'}}</p>
                        </div>
                    </div>
                </div>

                <div class="row">
                    <div class="col-md-7">
                        <div class="info-section">
                            <h5>Beauty & Cosmetics Usage</h5>
                            <p><strong>Makeup Frequency:</strong> ${{p['How often do you usually apply face makeup? '] || '-'}}</p>
                            <p><strong>Store Visits:</strong> ${{p['How many times do you visit cosmetic store?'] || '-'}}</p>
                            <p><strong>Skin Type:</strong> ${{p['What is your skin type?'] || '-'}}</p>
                            <p><strong>Preferred Look:</strong> ${{p['Which of the following makeup looks do you prefer the most after applying makeup?'] || '-'}}</p>
                            <p><strong>Cushion Usage:</strong> ${{p['Have you ever used a cushion foundation?'] || '-'}}</p>
                            <p><strong>Sunscreen:</strong> ${{p['How often do you usually use sunscreen products?'] || '-'}}</p>
                        </div>
                    </div>

                    <div class="col-md-5">
                        <div class="info-section text-center">
                            <h5>Face Photo</h5>
                            ${{img.face ? `<img src="${{img.face}}" class="face-photo-large">` : '<div style="height:400px;background:#f0f0f0;display:flex;align-items:center;justify-content:center;border-radius:12px">No Face Photo</div>'}}
                        </div>
                    </div>
                </div>

                <div class="row">
                    <div class="col-md-6">
                        <div class="info-section">
                            <h5>Products Used by Participant</h5>
                            <div class="product-list">
                                ${{userProducts.length > 0 ?
                                    userProducts.map(prod => `<div class="product-item">✓ ${{prod}}</div>`).join('') :
                                    '<p class="text-muted mb-0">No products specified</p>'
                                }}
                                ${{lipProducts.length > 0 ?
                                    '<h6 class="mt-3 mb-2" style="color: #667eea;">Lip Products:</h6>' +
                                    lipProducts.map(prod => `<div class="product-item">✓ ${{prod}}</div>`).join('') :
                                    ''
                                }}
                            </div>
                        </div>
                    </div>

                    <div class="col-md-6">
                        <div class="info-section text-center">
                            <h5>Makeup Application Areas</h5>
                            <p class="text-muted small mb-3">Dynamic visualization based on your products</p>
                            ${{faceVisualization}}
                            <div class="makeup-info">
                                <small class="text-muted">
                                    Each glowing area represents where the participant's products are applied.
                                    The face color is based on Skin Brightness level ${{skinBrightness}}.
                                </small>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="info-section">
                    <h5>Reference Images</h5>
                    <div class="row">
                        <div class="col-md-4">
                            <div style="position: relative;">
                                ${{img.skinbrightness ? `<img src="${{img.skinbrightness}}" class="ref-img">` : '<div class="no-image">No Image</div>'}}
                                ${{img.skinbrightness ? `<div class="ref-value">Brightness: ${{p['밝기판정'] || '-'}}</div>` : ''}}
                            </div>
                            <p class="text-center mt-2">Skin Brightness Reference</p>
                        </div>
                        <div class="col-md-4">
                            <div style="position: relative;">
                                ${{img.hair ? `<img src="${{img.hair}}" class="ref-img">` : '<div class="no-image">No Image</div>'}}
                                ${{img.hair ? `<div class="ref-value">Tone: ${{p['톤'] || '-'}}</div>` : ''}}
                            </div>
                            <p class="text-center mt-2">Hair Reference</p>
                        </div>
                        <div class="col-md-4">
                            <div style="position: relative;">
                                ${{img.eyecolor ? `<img src="${{img.eyecolor}}" class="ref-img">` : '<div class="no-image">No Image</div>'}}
                                ${{img.eyecolor ? `<div class="ref-value">${{p['Please select the ethnic group you identify with:'] ? p['Please select the ethnic group you identify with:'].split(' ')[0] : '-'}}</div>` : ''}}
                            </div>
                            <p class="text-center mt-2">Eye Color Reference</p>
                        </div>
                    </div>
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

                const age = p['Please enter your 4-digit year of birth(e.g., 1980) '] ? 2025 - p['Please enter your 4-digit year of birth(e.g., 1980) '] : '-';

                rows += `
                    <tr>
                        <td><strong>${{p['A-ID']}}</strong></td>
                        <td>${{p['P-ID']}}</td>
                        <td>${{p['What is your full name? (Please write exactly as shown in your ARC or passport)']}}</td>
                        <td>${{p['What is your gender? '] || '-'}}</td>
                        <td>${{p['What is your nationality?'] || '-'}}</td>
                        <td>${{age}}</td>
                        <td>${{img.skinbrightness ? `<img src="${{img.skinbrightness}}" class="skin-img" title="Brightness: ${{p['밝기판정']}}">` : p['밝기판정'] || '-'}}</td>
                        <td>${{tone ? `<span class="${{toneClass}}">${{tone}}</span>` : '-'}}</td>
                        <td><button class="btn btn-sm btn-details" onclick="showDetails('${{p['A-ID']}}')">View</button></td>
                    </tr>
                `;
            }});

            $('#tableBody').html(rows);

            $('#dataTable').DataTable({{
                pageLength: 25,
                responsive: true,
                order: [[0, 'asc']],
                language: {{
                    search: "Search:",
                    lengthMenu: "Show _MENU_",
                    info: "Showing _START_ to _END_ of _TOTAL_"
                }}
            }});
        }});
    </script>
</body>
</html>'''

# Save as makeup-test-dashboard.html
with open('makeup-test-dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("\n✅ Dashboard enhanced with dynamic effects!")
print(f"- Hair Reference shows Tone value")
print(f"- Eye Color Reference shows Ethnic group")
print(f"- Face background based on Skin Brightness (1-7 scale)")
print(f"- Dynamic glowing effects for applied makeup areas")
print(f"- Realistic product mapping with gradients")
print(f"- Saved as: makeup-test-dashboard.html")