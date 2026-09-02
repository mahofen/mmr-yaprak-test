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

        /* Section Actions on Blocks */
        .editable-section-block {
            position: relative;
            border: 1px dashed transparent;
            border-radius: 6px;
            padding: 0.4rem;
            margin-bottom: 0.6rem;
            transition: all 0.2s ease;
        }

        .editable-section-block:hover {
            border-color: #cbd5e1;
            background: rgba(240, 249, 255, 0.3);
        }

        .section-action-toolbar {
            position: absolute;
            top: 4px;
            right: 4px;
            display: none;
            align-items: center;
            gap: 3px;
            background: rgba(255,255,255,0.95);
            border: 1px solid #cbd5e1;
            border-radius: 5px;
            padding: 2px 4px;
            z-index: 20;
            box-shadow: 0 2px 5px rgba(0,0,0,0.08);
        }

        .editable-section-block:hover .section-action-toolbar {
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
            .bank-header, .bank-nav, .sheet-top-actions, .section-action-toolbar {
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

        function renderSheetContent(weekNum, markdownText) {
            const container = document.getElementById('content-week-' + weekNum);
            if (!container) return;

            const rawHtml = marked.parse(markdownText);
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = rawHtml;

            const children = Array.from(tempDiv.children);
            container.innerHTML = '';
            let currentBlock = null;

            children.forEach(child => {
                const tag = child.tagName.toLowerCase();
                if (['h1', 'h2', 'h3', 'h4', 'hr'].includes(tag) || !currentBlock) {
                    currentBlock = document.createElement('div');
                    currentBlock.className = 'editable-section-block';

                    const toolbar = document.createElement('div');
                    toolbar.className = 'section-action-toolbar';

                    // Edit
                    const editBtn = document.createElement('button');
                    editBtn.className = 'btn-toolbar-action';
                    editBtn.innerHTML = '<i class="fa-solid fa-pen"></i> Düzenle';
                    editBtn.onclick = (e) => {
                        e.stopPropagation();
                        const contentWrap = currentBlock.querySelector('.block-inner');
                        if (contentWrap) {
                            contentWrap.contentEditable = 'true';
                            contentWrap.focus();
                        }
                    };
                    toolbar.appendChild(editBtn);

                    // Add Below
                    const addBtn = document.createElement('button');
                    addBtn.className = 'btn-toolbar-action btn-toolbar-add';
                    addBtn.innerHTML = '<i class="fa-solid fa-plus"></i> Ekle';
                    addBtn.onclick = (e) => {
                        e.stopPropagation();
                        addSectionBelow(currentBlock);
                    };
                    toolbar.appendChild(addBtn);

                    // Move Up
                    const upBtn = document.createElement('button');
                    upBtn.className = 'btn-toolbar-action';
                    upBtn.innerHTML = '<i class="fa-solid fa-arrow-up"></i>';
                    upBtn.onclick = (e) => {
                        e.stopPropagation();
                        const prev = currentBlock.previousElementSibling;
                        if (prev && prev.classList.contains('editable-section-block')) prev.before(currentBlock);
                    };
                    toolbar.appendChild(upBtn);

                    // Move Down
                    const downBtn = document.createElement('button');
                    downBtn.className = 'btn-toolbar-action';
                    downBtn.innerHTML = '<i class="fa-solid fa-arrow-down"></i>';
                    downBtn.onclick = (e) => {
                        e.stopPropagation();
                        const next = currentBlock.nextElementSibling;
                        if (next && next.classList.contains('editable-section-block')) next.after(currentBlock);
                    };
                    toolbar.appendChild(downBtn);

                    // Delete
                    const delBtn = document.createElement('button');
                    delBtn.className = 'btn-toolbar-action btn-toolbar-del';
                    delBtn.innerHTML = '<i class="fa-solid fa-trash-can"></i> Sil';
                    delBtn.onclick = (e) => {
                        e.stopPropagation();
                        if (confirm('Bu bölümü silmek istediğinize emin misiniz?')) {
                            currentBlock.style.transition = 'all 0.25s ease';
                            currentBlock.style.opacity = '0';
                            setTimeout(() => currentBlock.remove(), 250);
                        }
                    };
                    toolbar.appendChild(delBtn);

                    currentBlock.appendChild(toolbar);

                    const blockInner = document.createElement('div');
                    blockInner.className = 'block-inner';
                    currentBlock.appendChild(blockInner);

                    container.appendChild(currentBlock);
                }

                const inner = currentBlock.querySelector('.block-inner');
                if (inner) inner.appendChild(child);
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
            newBlock.className = 'editable-section-block';
            newBlock.innerHTML = `
                <div class="block-inner" contenteditable="true">
                    <h3><i class="fa-solid fa-sparkles"></i> ${title}</h3>
                    <p>Etkinlik açıklaması ve yönergesi buraya yazılacaktır.</p>
                    <p>[ Öğrenci Cevap Alanı: ............................................................ ]</p>
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
            newBlock.className = 'editable-section-block';
            newBlock.innerHTML = `
                <div class="block-inner" contenteditable="true">
                    <h3><i class="fa-solid fa-sparkles"></i> ${title}</h3>
                    <p>Etkinlik açıklaması ve yönergesi buraya yazılacaktır.</p>
                    <p>[ Öğrenci Cevap Alanı: ............................................................ ]</p>
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
