import json
import os

with open("calisma_kagidi_bankasi/bank_data.json", "r", encoding="utf-8") as f:
    bank_data = json.load(f)

html_content = """<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Çalışma Kağıdı Bankası - Muallimin Manevi Rehberi (MMR)</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        :root {
            --primary: #1e3a8a;
            --primary-dark: #172554;
            --teal: #0f766e;
            --teal-dark: #115e59;
            --accent: #d97706;
            --bg-light: #f8fafc;
            --text-main: #1e293b;
            --text-muted: #64748b;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        }

        body {
            background-color: #f1f5f9;
            color: var(--text-main);
            padding-bottom: 3rem;
        }

        /* Top Header */
        .bank-header {
            background: linear-gradient(135deg, #1e3a8a 0%, #0f766e 100%);
            color: #ffffff;
            padding: 1.25rem 2rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .header-inner {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 1rem;
        }

        .brand-box {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .brand-box i {
            font-size: 2.2rem;
            color: #38bdf8;
        }

        .brand-box h1 {
            font-size: 1.35rem;
            font-weight: 800;
            letter-spacing: 0.5px;
        }

        .brand-box p {
            font-size: 0.82rem;
            color: #cbd5e1;
        }

        .header-actions {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            flex-wrap: wrap;
        }

        .btn-bank {
            background: rgba(255,255,255,0.15);
            color: #ffffff;
            border: 1px solid rgba(255,255,255,0.25);
            padding: 0.5rem 0.9rem;
            border-radius: 6px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            transition: all 0.2s;
        }

        .btn-bank:hover {
            background: rgba(255,255,255,0.25);
            color: #ffffff;
            transform: translateY(-1px);
        }

        .btn-bank.btn-gold {
            background: #d97706;
            border-color: #f59e0b;
        }
        .btn-bank.btn-gold:hover {
            background: #b45309;
        }

        .btn-bank.btn-docx-all {
            background: #2563eb;
            border-color: #3b82f6;
        }
        .btn-bank.btn-docx-all:hover {
            background: #1d4ed8;
        }

        /* Week Nav Tabs */
        .bank-nav {
            background: #ffffff;
            border-bottom: 1px solid #e2e8f0;
            position: sticky;
            top: 74px;
            z-index: 90;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        }

        .nav-inner {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            gap: 0.4rem;
            padding: 0.5rem 1rem;
            overflow-x: auto;
        }

        .nav-tab {
            padding: 0.6rem 1rem;
            border: none;
            background: transparent;
            color: #475569;
            font-size: 0.88rem;
            font-weight: 600;
            border-radius: 6px;
            cursor: pointer;
            white-space: nowrap;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            transition: all 0.2s;
        }

        .nav-tab:hover {
            background: #f1f5f9;
            color: var(--primary);
        }

        .nav-tab.active {
            background: #0f766e;
            color: #ffffff;
        }

        /* Main Container */
        .container {
            max-width: 960px;
            margin: 1.5rem auto;
            padding: 0 1rem;
        }

        /* Worksheet Card Sheet */
        .sheet-card {
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            box-shadow: 0 4px 18px rgba(0,0,0,0.06);
            padding: 2rem 2.25rem;
            margin-bottom: 2rem;
            position: relative;
        }

        .sheet-badge {
            position: absolute;
            top: -12px;
            left: 24px;
            background: #0f766e;
            color: #ffffff;
            padding: 3px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.5px;
            box-shadow: 0 2px 6px rgba(15, 118, 110, 0.3);
        }

        .sheet-top-actions {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1.25rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid #e2e8f0;
            flex-wrap: wrap;
            gap: 0.5rem;
        }

        .sheet-title-text {
            font-size: 1.15rem;
            font-weight: 800;
            color: var(--primary);
        }

        .sheet-buttons {
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }

        .btn-sheet-action {
            background: #f8fafc;
            border: 1px solid #cbd5e1;
            color: #334155;
            padding: 4px 9px;
            border-radius: 5px;
            font-size: 0.78rem;
            font-weight: 600;
            text-decoration: none;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            transition: all 0.15s;
        }

        .btn-sheet-action:hover {
            background: #e2e8f0;
            color: #0f172a;
        }

        .btn-sheet-action.btn-docx {
            color: #1e3a8a;
            border-color: #93c5fd;
            background: #eff6ff;
        }
        .btn-sheet-action.btn-docx:hover {
            background: #1e3a8a;
            color: #ffffff;
        }

        /* Content Styling */
        .markdown-rendered {
            font-size: 0.93rem;
            line-height: 1.6;
            color: #1e293b;
        }

        .markdown-rendered h1, 
        .markdown-rendered h2 {
            font-size: 1.2rem;
            color: var(--primary);
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 0.35rem;
            margin: 1.2rem 0 0.6rem 0;
        }

        .markdown-rendered h3 {
            font-size: 1.05rem;
            color: var(--teal);
            margin: 1rem 0 0.4rem 0;
        }

        .markdown-rendered p {
            margin-bottom: 0.65rem;
        }

        .markdown-rendered ul, 
        .markdown-rendered ol {
            margin-bottom: 0.75rem;
            padding-left: 1.4rem;
        }

        .markdown-rendered li {
            margin-bottom: 0.3rem;
        }

        .markdown-rendered table {
            width: 100%;
            border-collapse: collapse;
            margin: 0.8rem 0 1rem 0;
            font-size: 0.88rem;
        }

        .markdown-rendered table th, 
        .markdown-rendered table td {
            border: 1px solid #cbd5e1;
            padding: 0.5rem 0.7rem;
        }

        .markdown-rendered table th {
            background: #f8fafc;
            color: #1e3a8a;
            font-weight: 700;
            text-align: left;
        }

        .markdown-rendered blockquote {
            border-left: 4px solid var(--teal);
            background: #f8fafc;
            padding: 0.75rem 1rem;
            margin: 0.75rem 0;
            border-radius: 0 6px 6px 0;
            font-size: 0.9rem;
            color: #334155;
        }

        /* SAYFA SIĞDIRMA DÜZENİ */
        .page-chunk-nav {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            margin-bottom: 1.35rem;
            flex-wrap: wrap;
            background: #f8fafc;
            padding: 0.5rem 0.8rem;
            border-radius: 30px;
            border: 1px solid #e2e8f0;
        }

        .btn-chunk {
            background: #ffffff;
            border: 1px solid #cbd5e1;
            color: #475569;
            padding: 0.35rem 0.8rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 700;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            transition: all 0.2s;
        }

        .btn-chunk:hover {
            border-color: #0f766e;
            color: #0f766e;
            background: #f0fdfa;
        }

        .btn-chunk.active {
            background: #0f766e;
            border-color: #0f766e;
            color: #ffffff;
            box-shadow: 0 2px 6px rgba(15, 118, 110, 0.25);
        }

        /* MMR TEK VE MODERN KART TASARIMI */
        .mmr-section-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
            padding: 1.15rem 1.35rem;
            margin-bottom: 1.2rem;
            position: relative;
            page-break-inside: avoid;
            transition: all 0.2s ease;
        }

        .mmr-section-card:hover {
            border-color: #cbd5e1;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
        }

        .mmr-card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid #f1f5f9;
            padding-bottom: 0.6rem;
            margin-bottom: 0.85rem;
            gap: 0.5rem;
            flex-wrap: wrap;
        }

        .mmr-header-left {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .mmr-badge {
            width: 32px;
            height: 32px;
            border-radius: 8px;
            background: linear-gradient(135deg, #1e3a8a 0%, #0f766e 100%);
            color: #ffffff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 0.95rem;
            box-shadow: 0 2px 5px rgba(15, 118, 110, 0.25);
            flex-shrink: 0;
        }

        .mmr-title-group {
            display: flex;
            flex-direction: column;
        }

        .mmr-title {
            font-size: 1.05rem;
            font-weight: 800;
            color: var(--primary);
            display: flex;
            align-items: center;
            gap: 0.45rem;
        }

        .mmr-title i {
            color: var(--teal);
            font-size: 0.95rem;
        }

        .mmr-subtitle {
            font-size: 0.78rem;
            color: #64748b;
            font-weight: 600;
        }

        .mmr-tag {
            background: #f1f5f9;
            color: #334155;
            padding: 0.2rem 0.65rem;
            border-radius: 12px;
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border: 1px solid #e2e8f0;
        }

        .mmr-card-body {
            font-size: 0.91rem;
            line-height: 1.55;
            color: #334155;
        }

        .mmr-card-body table {
            width: 100%;
            border-collapse: collapse;
            margin: 0.75rem 0;
            font-size: 0.88rem;
        }

        .mmr-card-body table th,
        .mmr-card-body table td {
            border: 1px solid #cbd5e1;
            padding: 0.5rem 0.7rem;
        }

        .mmr-card-body table th {
            background: #f8fafc;
            color: #1e3a8a;
            font-weight: 700;
        }

        .mmr-card-body blockquote {
            border-left: 4px solid var(--teal);
            background: #f8fafc;
            padding: 0.6rem 0.9rem;
            margin: 0.6rem 0;
            border-radius: 0 6px 6px 0;
            font-size: 0.88rem;
            color: #334155;
        }

        .mmr-card-footer {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 7px;
            padding: 0.65rem 0.85rem;
            margin-top: 0.8rem;
        }

        .mmr-footer-label {
            font-size: 0.8rem;
            font-weight: 700;
            color: var(--teal);
            display: flex;
            align-items: center;
            gap: 0.35rem;
            margin-bottom: 0.3rem;
            text-transform: uppercase;
            letter-spacing: 0.3px;
        }

        .mmr-footer-input {
            color: #475569;
            font-size: 0.88rem;
            font-style: italic;
            border-bottom: 1px dotted #94a3b8;
            min-height: 22px;
            line-height: 1.4;
        }

        /* Section Actions on Hover */
        .section-action-toolbar {
            position: absolute;
            top: 6px;
            right: 6px;
            display: none;
            align-items: center;
            gap: 3px;
            background: rgba(255,255,255,0.95);
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            padding: 2px 4px;
            z-index: 20;
            box-shadow: 0 2px 5px rgba(0,0,0,0.08);
        }

        .mmr-section-card:hover .section-action-toolbar {
            display: flex;
        }

        .btn-toolbar-action {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 4px;
            padding: 2px 5px;
            font-size: 0.72rem;
            font-weight: 600;
            color: #475569;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 2px;
        }
        .btn-toolbar-action:hover {
            background: #e2e8f0;
            color: #0f172a;
        }
        .btn-toolbar-add {
            color: #0f766e;
            background: #f0fdfa;
            border-color: #99f6e4;
        }
        .btn-toolbar-add:hover {
            background: #0f766e;
            color: #ffffff;
        }
        .btn-toolbar-del {
            color: #dc2626;
            background: #fef2f2;
            border-color: #fecaca;
        }
        .btn-toolbar-del:hover {
            background: #dc2626;
            color: #ffffff;
        }

        /* Print Media */
        @media print {
            .bank-header, .bank-nav, .sheet-top-actions, .section-action-toolbar, .page-chunk-nav {
                display: none !important;
            }
            body {
                background: #ffffff;
                color: #000000;
            }
            .container {
                max-width: 100% !important;
                margin: 0 !important;
                padding: 0 !important;
            }
            .sheet-card {
                box-shadow: none !important;
                border: none !important;
                padding: 0 !important;
                page-break-after: always;
            }
            .sheet-card:not(.active-print) {
                display: none !important;
            }
            .mmr-section-card {
                display: block !important;
                box-shadow: none !important;
                border: 1px solid #cbd5e1 !important;
            }
        }
    </style>
</head>
<body>

    <header class="bank-header">
        <div class="header-inner">
            <div class="brand-box">
                <i class="fa-solid fa-book-bookmark"></i>
                <div>
                    <h1>Muallimin Manevi Rehberi (MMR) Çalışma Kağıdı Bankası</h1>
                    <p>5. Sınıf Fen Bilimleri 1. Ünite: Güneş, Dünya ve Ay (5 Haftalık Tam Set)</p>
                </div>
            </div>
            <div class="header-actions">
                <a href="calisma_kagidi_bankasi/CALISMA_KAGIDI_BANKASI_TUMU.docx" class="btn-bank btn-docx-all" download title="Tüm 5 haftayı tek bir Word dosyasında indir">
                    <i class="fa-solid fa-file-word"></i> Tüm Bankayı İndir (.docx)
                </a>
                <button class="btn-bank btn-gold" onclick="window.print()" title="Görüntülenen çalışma kağıdını yazdır veya PDF olarak kaydet">
                    <i class="fa-solid fa-print"></i> Yazdır / PDF
                </button>
                <a href="http://127.0.0.1:5000" target="_blank" class="btn-bank" title="Canlı Yapay Zekâ Üreticisini Aç">
                    <i class="fa-solid fa-bolt"></i> Yeni Üretici
                </a>
            </div>
        </div>
    </header>

    <nav class="bank-nav">
        <div class="nav-inner">
            <button class="nav-tab active" onclick="showWeek(1)"><i class="fa-solid fa-sun"></i> 1. Hafta (Güneş'in Yapısı)</button>
            <button class="nav-tab" onclick="showWeek(2)"><i class="fa-solid fa-heart-pulse"></i> 2. Hafta (Dönme & Rahmet)</button>
            <button class="nav-tab" onclick="showWeek(3)"><i class="fa-solid fa-moon"></i> 3. Hafta (Ay'ın Özellikleri)</button>
            <button class="nav-tab" onclick="showWeek(4)"><i class="fa-solid fa-calendar-days"></i> 4. Hafta (Ay'ın Evreleri)</button>
            <button class="nav-tab" onclick="showWeek(5)"><i class="fa-solid fa-atom"></i> 5. Hafta (Muazzam Uyum)</button>
            <button class="nav-tab" onclick="showWeek('all')"><i class="fa-solid fa-layer-group"></i> Tümünü Göster</button>
        </div>
    </nav>

    <main class="container">
"""

for item in bank_data:
    unit = item['unit']
    w_num = unit['week_num']
    slug = unit['slug']
    raw_md = item['markdown']
    json_escaped_md = json.dumps(raw_md)

    html_content += f"""
        <!-- WEEK {w_num} -->
        <article class="sheet-card" id="sheet-week-{w_num}" data-week="{w_num}">
            <div class="sheet-badge">{w_num}. HAFTA ÇALIŞMA KAĞIDI</div>
            <div class="sheet-top-actions">
                <div class="sheet-title-text"><i class="fa-solid fa-file-signature"></i> {unit['title']}</div>
                <div class="sheet-buttons">
                    <a href="calisma_kagidi_bankasi/{unit['slug']}.docx" class="btn-sheet-action btn-docx" download>
                        <i class="fa-solid fa-file-word"></i> Word (.docx)
                    </a>
                    <button class="btn-sheet-action" onclick="printSingleWeek({w_num})">
                        <i class="fa-solid fa-print"></i> Yazdır
                    </button>
                    <button class="btn-sheet-action" onclick="addSectionToSheet({w_num})">
                        <i class="fa-solid fa-plus"></i> Bölüm Ekle
                    </button>
                </div>
            </div>

            <!-- Sayfa Sığdırma Butonları -->
            <div class="page-chunk-nav" id="chunk-nav-week-{w_num}">
                <span style="font-size:0.8rem; font-weight:700; color:#64748b;"><i class="fa-solid fa-file-lines"></i> Sayfa Sığdırma:</span>
                <button class="btn-chunk active" onclick="filterWeekChunks({w_num}, 'all', this)"><i class="fa-solid fa-layer-group"></i> Tümü (1-10)</button>
                <button class="btn-chunk" onclick="filterWeekChunks({w_num}, 'p1', this)"><i class="fa-solid fa-1"></i> Sayfa 1 (1-4)</button>
                <button class="btn-chunk" onclick="filterWeekChunks({w_num}, 'p2', this)"><i class="fa-solid fa-2"></i> Sayfa 2 (5-7)</button>
                <button class="btn-chunk" onclick="filterWeekChunks({w_num}, 'p3', this)"><i class="fa-solid fa-3"></i> Sayfa 3 (8-10)</button>
            </div>

            <div class="markdown-rendered" id="content-week-{w_num}"></div>
            <script>
                document.addEventListener('DOMContentLoaded', () => {{
                    renderSheetContent({w_num}, {json_escaped_md});
                }});
            </script>
        </article>
    """

html_content += """
    </main>

    <script>
        let currentActiveWeek = 1;

        const SECTION_METADATA = {
            1: { icon: 'fa-lightbulb', tag: 'Düşünme', sub: 'Merak ve İkinci Düşünme Kapısı' },
            2: { icon: 'fa-compass', tag: 'Bağlam', sub: 'Mana Taşıyıcısı Olay (Olay → Bilgi → Anlam)' },
            3: { icon: 'fa-binoculars', tag: 'Gözlem', sub: 'Kâinatı Okuma Fırsatı ve Hayret' },
            4: { icon: 'fa-wrench', tag: 'Bilim', sub: 'Bilimsel Gerçekten Manaya Geçiş' },
            5: { icon: 'fa-scale-balanced', tag: 'Nizam', sub: 'Nizam, Denge ve Ekolojik Sorumluluk' },
            6: { icon: 'fa-seedling', tag: 'Tefekkür', sub: 'Gözlemden Şuura 4 Aşamalı Kalp Mimarisi' },
            7: { icon: 'fa-gem', tag: 'Değer', sub: '5 Adımlı Erdem-Değer Zinciri' },
            8: { icon: 'fa-comments', tag: 'Müzakere', sub: 'Gerekçeli Tartışma & Fikir Alışverişi' },
            9: { icon: 'fa-bullseye', tag: 'Eylem', sub: 'Farkındalık → Değerim → Somut Davranışım' },
            10: { icon: 'fa-star', tag: 'Şuur', sub: '3 Düzeyli Şuur Gelişim Çizelgesi' }
        };

        function renderSheetContent(weekNum, markdownText) {
            const container = document.getElementById('content-week-' + weekNum);
            if (!container) return;

            const rawHtml = marked.parse(markdownText);
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = rawHtml;

            const children = Array.from(tempDiv.children);
            container.innerHTML = '';
            let currentCard = null;
            let sectionCount = 0;

            children.forEach(child => {
                const tag = child.tagName.toLowerCase();
                const text = child.textContent.trim();
                const match = text.match(/^(?:#+\s*)?(\d+)\.\s*([^(:\n]+)(?:\((.*)\))?/i);

                if (['h1', 'h2', 'h3', 'h4', 'hr'].includes(tag) || (match && match[1]) || !currentCard) {
                    let secNum = ++sectionCount;
                    let titleText = 'BÖLÜM';
                    let subText = 'Öğrenme ve Tefekkür Etkinliği';
                    let iconName = 'fa-sparkles';
                    let tagName = 'Etkinlik';

                    if (match && match[1]) {
                        secNum = parseInt(match[1]);
                        titleText = match[2].trim();
                        if (match[3]) subText = match[3].trim();
                    } else if (['h1', 'h2', 'h3'].includes(tag)) {
                        titleText = text.replace(/^#+\s*/, '').replace(/^\d+\.\s*/, '');
                    }

                    const meta = SECTION_METADATA[secNum] || { icon: 'fa-sparkles', tag: 'Etkinlik', sub: subText };
                    iconName = meta.icon;
                    tagName = meta.tag;
                    if (!match || !match[3]) subText = meta.sub;

                    currentCard = document.createElement('div');
                    currentCard.className = 'mmr-section-card';
                    currentCard.setAttribute('data-sec-num', secNum);

                    // Toolbar
                    const toolbar = document.createElement('div');
                    toolbar.className = 'section-action-toolbar';

                    // Edit
                    const editBtn = document.createElement('button');
                    editBtn.className = 'btn-toolbar-action';
                    editBtn.innerHTML = '<i class="fa-solid fa-pen"></i> Düzenle';
                    editBtn.onclick = (e) => {
                        e.stopPropagation();
                        const bodyEl = currentCard.querySelector('.mmr-card-body');
                        if (bodyEl) {
                            bodyEl.contentEditable = 'true';
                            bodyEl.focus();
                        }
                    };
                    toolbar.appendChild(editBtn);

                    // Add Below
                    const addBtn = document.createElement('button');
                    addBtn.className = 'btn-toolbar-action btn-toolbar-add';
                    addBtn.innerHTML = '<i class="fa-solid fa-plus"></i> Ekle';
                    addBtn.onclick = (e) => {
                        e.stopPropagation();
                        addSectionBelow(currentCard);
                    };
                    toolbar.appendChild(addBtn);

                    // Move Up
                    const upBtn = document.createElement('button');
                    upBtn.className = 'btn-toolbar-action';
                    upBtn.innerHTML = '<i class="fa-solid fa-arrow-up"></i>';
                    upBtn.onclick = (e) => {
                        e.stopPropagation();
                        const prev = currentCard.previousElementSibling;
                        if (prev && prev.classList.contains('mmr-section-card')) prev.before(currentCard);
                    };
                    toolbar.appendChild(upBtn);

                    // Move Down
                    const downBtn = document.createElement('button');
                    downBtn.className = 'btn-toolbar-action';
                    downBtn.innerHTML = '<i class="fa-solid fa-arrow-down"></i>';
                    downBtn.onclick = (e) => {
                        e.stopPropagation();
                        const next = currentCard.nextElementSibling;
                        if (next && next.classList.contains('mmr-section-card')) next.after(currentCard);
                    };
                    toolbar.appendChild(downBtn);

                    // Delete
                    const delBtn = document.createElement('button');
                    delBtn.className = 'btn-toolbar-action btn-toolbar-del';
                    delBtn.innerHTML = '<i class="fa-solid fa-trash-can"></i> Sil';
                    delBtn.onclick = (e) => {
                        e.stopPropagation();
                        if (confirm('Bu bölümü silmek istediğinize emin misiniz?')) {
                            currentCard.style.transition = 'all 0.25s ease';
                            currentCard.style.opacity = '0';
                            setTimeout(() => currentCard.remove(), 250);
                        }
                    };
                    toolbar.appendChild(delBtn);

                    currentCard.appendChild(toolbar);

                    // Header
                    const headerEl = document.createElement('div');
                    headerEl.className = 'mmr-card-header';
                    headerEl.innerHTML = `
                        <div class="mmr-header-left">
                            <div class="mmr-badge">${secNum}</div>
                            <div class="mmr-title-group">
                                <h3 class="mmr-title"><i class="fa-solid ${iconName}"></i> ${titleText}</h3>
                                <span class="mmr-subtitle">${subText}</span>
                            </div>
                        </div>
                        <span class="mmr-tag">${tagName}</span>
                    `;
                    currentCard.appendChild(headerEl);

                    // Body
                    const bodyEl = document.createElement('div');
                    bodyEl.className = 'mmr-card-body';
                    currentCard.appendChild(bodyEl);

                    container.appendChild(currentCard);

                    if (['h1', 'h2', 'h3'].includes(tag) || (match && match[1])) {
                        return;
                    }
                }

                const body = currentCard.querySelector('.mmr-card-body');
                if (body) {
                    body.appendChild(child);
                }
            });
        }

        function filterWeekChunks(weekNum, chunkType, btn) {
            const nav = document.getElementById('chunk-nav-week-' + weekNum);
            if (nav) {
                nav.querySelectorAll('.btn-chunk').forEach(b => b.classList.remove('active'));
            }
            if (btn) btn.classList.add('active');

            const content = document.getElementById('content-week-' + weekNum);
            if (!content) return;

            const cards = content.querySelectorAll('.mmr-section-card');
            cards.forEach((card, index) => {
                const secNum = parseInt(card.getAttribute('data-sec-num')) || (index + 1);
                if (chunkType === 'all') {
                    card.style.display = 'block';
                } else if (chunkType === 'p1') {
                    card.style.display = (secNum >= 1 && secNum <= 4) ? 'block' : 'none';
                } else if (chunkType === 'p2') {
                    card.style.display = (secNum >= 5 && secNum <= 7) ? 'block' : 'none';
                } else if (chunkType === 'p3') {
                    card.style.display = (secNum >= 8 && secNum <= 10) ? 'block' : 'none';
                }
            });
        }

        function showWeek(week) {
            currentActiveWeek = week;
            const tabs = document.querySelectorAll('.nav-tab');
            const sheets = document.querySelectorAll('.sheet-card');

            tabs.forEach(t => t.classList.remove('active'));
            sheets.forEach(s => s.style.display = 'none');

            if (week === 'all') {
                tabs[5].classList.add('active');
                sheets.forEach(s => s.style.display = 'block');
            } else {
                tabs[week - 1].classList.add('active');
                const target = document.getElementById('sheet-week-' + week);
                if (target) {
                    target.style.display = 'block';
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }
        }

        function printSingleWeek(weekNum) {
            document.querySelectorAll('.sheet-card').forEach(s => s.classList.remove('active-print'));
            const sheet = document.getElementById('sheet-week-' + weekNum);
            if (sheet) sheet.classList.add('active-print');
            window.print();
        }

        function addSectionBelow(block) {
            const title = prompt('Yeni bölüm başlığını giriniz:', 'YENİ ETKİNLİK / BÖLÜM');
            if (!title) return;
            const newBlock = document.createElement('div');
            newBlock.className = 'mmr-section-card';
            newBlock.innerHTML = `
                <div class="mmr-card-header">
                    <div class="mmr-header-left">
                        <div class="mmr-badge"><i class="fa-solid fa-plus"></i></div>
                        <div class="mmr-title-group">
                            <h3 class="mmr-title"><i class="fa-solid fa-sparkles"></i> ${title}</h3>
                            <span class="mmr-subtitle">Öğretmen Tarafından Eklenen Etkinlik</span>
                        </div>
                    </div>
                    <span class="mmr-tag">Ek Bölüm</span>
                </div>
                <div class="mmr-card-body" contenteditable="true">
                    <p>Etkinlik açıklaması ve yönergesi buraya yazılacaktır.</p>
                </div>
                <div class="mmr-card-footer">
                    <div class="mmr-footer-label"><i class="fa-solid fa-pen"></i> Öğrenci Cevap Alanı:</div>
                    <div class="mmr-footer-input" contenteditable="true">[ Öğrenci cevabı buraya yazılacaktır .......... ]</div>
                </div>
            `;
            block.after(newBlock);
            newBlock.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }

        function addSectionToSheet(weekNum) {
            const container = document.getElementById('content-week-' + weekNum);
            if (!container) return;
            const title = prompt('Yeni bölüm başlığını giriniz:', 'YENİ ETKİNLİK / BÖLÜM');
            if (!title) return;
            const newBlock = document.createElement('div');
            newBlock.className = 'mmr-section-card';
            newBlock.innerHTML = `
                <div class="mmr-card-header">
                    <div class="mmr-header-left">
                        <div class="mmr-badge"><i class="fa-solid fa-plus"></i></div>
                        <div class="mmr-title-group">
                            <h3 class="mmr-title"><i class="fa-solid fa-sparkles"></i> ${title}</h3>
                            <span class="mmr-subtitle">Öğretmen Tarafından Eklenen Etkinlik</span>
                        </div>
                    </div>
                    <span class="mmr-tag">Ek Bölüm</span>
                </div>
                <div class="mmr-card-body" contenteditable="true">
                    <p>Etkinlik açıklaması ve yönergesi buraya yazılacaktır.</p>
                </div>
                <div class="mmr-card-footer">
                    <div class="mmr-footer-label"><i class="fa-solid fa-pen"></i> Öğrenci Cevap Alanı:</div>
                    <div class="mmr-footer-input" contenteditable="true">[ Öğrenci cevabı buraya yazılacaktır .......... ]</div>
                </div>
            `;
            container.appendChild(newBlock);
            newBlock.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }

        // Initialize: Show Week 1 by default
        document.addEventListener('DOMContentLoaded', () => {
            showWeek(1);
        });
    </script>
</body>
</html>
"""

with open("calisma_kagidi_bankasi.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("[HTML] Çalışma Kağıdı Bankası Görsel Portalı Başarıyla Oluşturuldu: calisma_kagidi_bankasi.html")
