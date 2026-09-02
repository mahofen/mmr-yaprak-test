document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const form = document.getElementById('generateForm');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = document.getElementById('btnText');
    const sampleSelect = document.getElementById('sampleSelect');
    const apiStatus = document.getElementById('apiStatus');
    const testExtraParams = document.getElementById('testExtraParams');
    const formAlert = document.getElementById('formAlert');
    
    const typeWorksheetLabel = document.getElementById('typeWorksheetLabel');
    const typeTestLabel = document.getElementById('typeTestLabel');
    const typeWorksheetRadio = document.querySelector('input[name="contentType"][value="worksheet"]');
    const typeTestRadio = document.querySelector('input[name="contentType"][value="test"]');

    const emptyState = document.getElementById('emptyState');
    const loadingBox = document.getElementById('loadingBox');
    const loadingTitle = document.getElementById('loadingTitle');
    const contentArea = document.getElementById('contentArea');
    const renderedMarkdown = document.getElementById('renderedMarkdown');
    const resultActions = document.getElementById('resultActions');
    const editHintBanner = document.getElementById('editHintBanner');

    const editToggleBtn = document.getElementById('editToggleBtn');
    const resetBtn = document.getElementById('resetBtn');
    const copyBtn = document.getElementById('copyBtn');
    const docxBtn = document.getElementById('docxBtn');
    const printBtn = document.getElementById('printBtn');

    let originalMarkdown = '';
    let currentMarkdown = '';
    let currentTitle = 'Materyal';
    let isEditing = false;

    // 1. Health Check and Client API Key Support
    function updateApiStatusUI(hasKey, custom = false) {
        if (!apiStatus) return;
        const dot = apiStatus.querySelector('.status-dot');
        const text = apiStatus.querySelector('.status-text');
        if (hasKey) {
            dot.className = 'status-dot active';
            text.textContent = custom ? 'Gemini API Bağlı (Kişisel)' : 'Gemini API Bağlı';
            apiStatus.title = 'API Anahtarı hazır. Değiştirmek veya güncellemek için tıklayınız.';
        } else {
            dot.className = 'status-dot error';
            text.textContent = 'API Anahtarı Eksik (Tıkla & Gir)';
            apiStatus.title = 'Vercel ortam değişkeni eklemediyseniz buraya tıklayarak Gemini API anahtarınızı yapıştırabilirsiniz.';
        }
    }

    const localStoredKey = localStorage.getItem('user_gemini_api_key');
    if (localStoredKey) {
        updateApiStatusUI(true, true);
    }

    fetch('/api/health')
        .then(res => res.json())
        .then(data => {
            if (data.has_api_key) {
                updateApiStatusUI(true, false);
            } else if (!localStoredKey) {
                updateApiStatusUI(false, false);
            }
        })
        .catch(() => {
            if (!localStoredKey) {
                const dot = apiStatus.querySelector('.status-dot');
                const text = apiStatus.querySelector('.status-text');
                dot.className = 'status-dot error';
                text.textContent = 'Sunucu Bağlantı Hatası';
            }
        });

    if (apiStatus) {
        apiStatus.style.cursor = 'pointer';
        apiStatus.addEventListener('click', () => {
            const currentKey = localStorage.getItem('user_gemini_api_key') || '';
            const newKey = prompt('Google AI Studio Gemini API Anahtarınızı giriniz:\n(Vercel ortam değişkeni girmediyseniz buradan doğrudan tarayıcınıza kaydedip kullanabilirsiniz)', currentKey);
            if (newKey !== null) {
                if (newKey.trim()) {
                    localStorage.setItem('user_gemini_api_key', newKey.trim());
                    updateApiStatusUI(true, true);
                    showAlert('Gemini API anahtarınız tarayıcınıza başarıyla kaydedildi!', 'success');
                } else {
                    localStorage.removeItem('user_gemini_api_key');
                    location.reload();
                }
            }
        });
    }

    // 2. Load Sample Units
    let sampleUnitsData = [];
    fetch('/api/sample-units')
        .then(res => res.json())
        .then(data => {
            sampleUnitsData = data.units || [];
            sampleUnitsData.forEach((unit, idx) => {
                const opt = document.createElement('option');
                opt.value = idx;
                opt.textContent = unit.title;
                sampleSelect.appendChild(opt);
            });
        })
        .catch(err => console.warn('Sample units error:', err));

    sampleSelect.addEventListener('change', () => {
        const val = sampleSelect.value;
        if (val !== '') {
            const selected = sampleUnitsData[parseInt(val)];
            if (selected) {
                document.getElementById('grade').value = selected.grade;
                document.getElementById('subject').value = selected.subject;
                document.getElementById('learningArea').value = selected.learning_area;
                document.getElementById('topic').value = selected.topic;
                document.getElementById('learningOutcome').value = selected.learning_outcome;
                const maneviElem = document.getElementById('maneviOutcome');
                if (maneviElem) {
                    maneviElem.value = selected.manevi_outcome || '';
                }
            }
        }
    });

    // 3. Content Type Toggle
    function updateContentTypeUI() {
        if (typeWorksheetRadio.checked) {
            typeWorksheetLabel.classList.add('active');
            typeTestLabel.classList.remove('active');
            testExtraParams.classList.add('hidden');
            submitBtn.className = 'btn-generate btn-worksheet';
            btnText.textContent = 'ÇALIŞMA KAĞIDI OLUŞTUR';
        } else {
            typeTestLabel.classList.add('active');
            typeWorksheetLabel.classList.remove('active');
            testExtraParams.classList.remove('hidden');
            submitBtn.className = 'btn-generate btn-test';
            btnText.textContent = 'YAPRAK TEST OLUŞTUR';
        }
    }

    typeWorksheetRadio.addEventListener('change', updateContentTypeUI);
    typeTestRadio.addEventListener('change', updateContentTypeUI);

    // 4. Form Submit & AI Generation
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideAlert();

        const grade = document.getElementById('grade').value.trim();
        const subject = document.getElementById('subject').value.trim();
        const learningArea = document.getElementById('learningArea').value.trim();
        const topic = document.getElementById('topic').value.trim();
        const learningOutcome = document.getElementById('learningOutcome').value.trim();
        const maneviOutcomeElem = document.getElementById('maneviOutcome');
        const maneviOutcome = maneviOutcomeElem ? maneviOutcomeElem.value.trim() : '';
        const contentType = document.querySelector('input[name="contentType"]:checked').value;
        const questionCount = parseInt(document.getElementById('questionCount').value, 10);
        const difficulty = document.getElementById('difficulty').value;

        if (!grade || !subject || !learningArea || !topic || !learningOutcome) {
            showAlert('Lütfen tüm zorunlu alanları doldurunuz.');
            return;
        }

        currentTitle = `${grade}_${subject}_${contentType === 'worksheet' ? 'Calisma_Kagidi' : 'Yaprak_Test'}`;

        // Set Loading State
        if (submitBtn) submitBtn.disabled = true;
        if (emptyState) emptyState.classList.add('hidden');
        if (contentArea) contentArea.classList.add('hidden');
        if (resultActions) resultActions.style.display = 'none';
        if (loadingBox) loadingBox.classList.remove('hidden');

        if (contentType === 'worksheet') {
            if (loadingTitle) loadingTitle.textContent = 'Yapay zekâ çalışma kağıdını hazırlıyor...';
        } else {
            if (loadingTitle) loadingTitle.textContent = 'Yapay zekâ yaprak testi hazırlıyor...';
        }

        try {
            const reqHeaders = { 'Content-Type': 'application/json' };
            const clientKey = localStorage.getItem('user_gemini_api_key');
            if (clientKey) {
                reqHeaders['X-Gemini-Key'] = clientKey;
            }

            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: reqHeaders,
                body: JSON.stringify({
                    grade,
                    subject,
                    learning_area: learningArea,
                    topic,
                    learning_outcome: learningOutcome,
                    manevi_outcome: maneviOutcome,
                    content_type: contentType,
                    question_count: questionCount,
                    difficulty: difficulty
                })
            });

            const result = await response.json();

            if (!response.ok || !result.success) {
                if (result.error && result.error.includes('GEMINI_API_KEY')) {
                    const promptKey = prompt('Vercel ortam değişkeni henüz eklenmemiş.\nLütfen Gemini API anahtarınızı (AIzaSy...) buraya yapıştırıp Tamam deyin:');
                    if (promptKey && promptKey.trim()) {
                        localStorage.setItem('user_gemini_api_key', promptKey.trim());
                        updateApiStatusUI(true, true);
                        showAlert('API anahtarı kaydedildi. Şimdi lütfen tekrar "Materyal Üret" butonuna basınız!', 'success');
                        return;
                    }
                }
                throw new Error(result.error || 'İçerik oluşturulurken bir sorun oluştu. Lütfen bilgileri kontrol ederek tekrar deneyin.');
            }

            originalMarkdown = result.content;
            currentMarkdown = result.content;

            const isTest = (contentType === 'test') || /Soru\s*\d+/i.test(currentMarkdown) || /###\s*\d+\.\s*Soru/i.test(currentMarkdown);
            if (isTest) {
                renderTestContent(currentMarkdown);
            } else {
                renderModularContent(currentMarkdown);
            }

            if (loadingBox) loadingBox.classList.add('hidden');
            if (contentArea) contentArea.classList.remove('hidden');
            if (resultActions) resultActions.style.display = 'flex';
            if (resetBtn) resetBtn.style.display = 'none';

            // Scroll to preview on mobile
            if (window.innerWidth <= 1024 && contentArea) {
                contentArea.scrollIntoView({ behavior: 'smooth' });
            }

        } catch (err) {
            if (loadingBox) loadingBox.classList.add('hidden');
            if (emptyState) emptyState.classList.remove('hidden');
            showAlert(err.message || 'İçerik oluşturulurken bir sorun oluştu. Lütfen bilgileri kontrol ederek tekrar deneyiniz.');
        } finally {
            if (submitBtn) submitBtn.disabled = false;
        }
    });

    // 4.5. Text Sanitizer (Fixes LaTeX \rightarrow, \to and character bugs)
    function sanitizeEducationalText(text) {
        if (!text) return '';
        return text
            .replace(/\\rightarrow/g, '→')
            .replace(/\$\\rightarrow\$/g, '→')
            .replace(/\\to/g, '→')
            .replace(/\$\\to\$/g, '→')
            .replace(/\$([^\$]+)\$/g, '$1');
    }

    // Create Action Menu for each Section Block
    function createSectionToolbar(block) {
        const toolbar = document.createElement('div');
        toolbar.className = 'section-action-toolbar';

        // 1. Edit Button
        const editBtn = document.createElement('button');
        editBtn.className = 'btn-toolbar-action';
        editBtn.type = 'button';
        editBtn.innerHTML = '<i class="fa-solid fa-pen"></i> Düzenle';
        editBtn.title = 'Bu bölümü düzenle';
        editBtn.onclick = (e) => {
            e.stopPropagation();
            if (!isEditing && editToggleBtn) editToggleBtn.click();
            const content = block.querySelector('.block-content');
            if (content) content.focus();
        };
        toolbar.appendChild(editBtn);

        // 2. Add Section Below Button
        const addBtn = document.createElement('button');
        addBtn.className = 'btn-toolbar-action btn-toolbar-add';
        addBtn.type = 'button';
        addBtn.innerHTML = '<i class="fa-solid fa-plus"></i> Ekle';
        addBtn.title = 'Bu bölümün altına yeni etkinlik/bölüm ekle';
        addBtn.onclick = (e) => {
            e.stopPropagation();
            addNewModularSection(block);
        };
        toolbar.appendChild(addBtn);

        // 3. Move Up Button
        const upBtn = document.createElement('button');
        upBtn.className = 'btn-toolbar-action';
        upBtn.type = 'button';
        upBtn.innerHTML = '<i class="fa-solid fa-arrow-up"></i>';
        upBtn.title = 'Yukarı Taşı';
        upBtn.onclick = (e) => {
            e.stopPropagation();
            moveModularBlock(block, 'up');
        };
        toolbar.appendChild(upBtn);

        // 4. Move Down Button
        const downBtn = document.createElement('button');
        downBtn.className = 'btn-toolbar-action';
        downBtn.type = 'button';
        downBtn.innerHTML = '<i class="fa-solid fa-arrow-down"></i>';
        downBtn.title = 'Aşağı Taşı';
        downBtn.onclick = (e) => {
            e.stopPropagation();
            moveModularBlock(block, 'down');
        };
        toolbar.appendChild(downBtn);

        // 5. Delete Button
        const delBtn = document.createElement('button');
        delBtn.className = 'btn-toolbar-action btn-toolbar-del';
        delBtn.type = 'button';
        delBtn.innerHTML = '<i class="fa-solid fa-trash-can"></i> Sil';
        delBtn.title = 'Bu bölümü tamamen kaldır';
        delBtn.onclick = (e) => {
            e.stopPropagation();
            if (confirm('Bu bölümü tamamen kaldırmak istediğinize emin misiniz?')) {
                block.style.transition = 'all 0.3s ease';
                block.style.opacity = '0';
                block.style.transform = 'scale(0.96)';
                setTimeout(() => {
                    block.remove();
                    if (resetBtn) resetBtn.style.display = 'inline-flex';
                }, 250);
            }
        };
        toolbar.appendChild(delBtn);

        return toolbar;
    }

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

    function addNewModularSection(afterBlock = null) {
        const title = prompt('Eklenecek yeni bölüm başlığını yazınız:', 'YENİ ETKİNLİK / BÖLÜM');
        if (!title) return;

        const newBlock = document.createElement('div');
        newBlock.className = 'mmr-section-card editable-section-block';

        const toolbar = createSectionToolbar(newBlock);
        newBlock.appendChild(toolbar);

        const headerEl = document.createElement('div');
        headerEl.className = 'mmr-card-header';
        headerEl.innerHTML = `
            <div class="mmr-header-left">
                <div class="mmr-badge"><i class="fa-solid fa-plus"></i></div>
                <div class="mmr-title-group">
                    <h3 class="mmr-title"><i class="fa-solid fa-sparkles"></i> ${title}</h3>
                    <span class="mmr-subtitle">Öğretmen Tarafından Eklenen Etkinlik</span>
                </div>
            </div>
            <span class="mmr-tag">Ek Bölüm</span>
        `;
        newBlock.appendChild(headerEl);

        const contentWrap = document.createElement('div');
        contentWrap.className = 'mmr-card-body block-content';
        contentWrap.contentEditable = isEditing ? 'true' : 'false';
        contentWrap.innerHTML = `<p>Buraya yeni etkinlik, açıklama veya soru metnini yazabilirsiniz.</p>`;
        contentWrap.addEventListener('input', () => {
            if (resetBtn) resetBtn.style.display = 'inline-flex';
        });
        newBlock.appendChild(contentWrap);

        const footerEl = document.createElement('div');
        footerEl.className = 'mmr-card-footer';
        footerEl.innerHTML = `
            <div class="mmr-footer-label"><i class="fa-solid fa-pen"></i> Öğrenci Cevap Alanı:</div>
            <div class="mmr-footer-input" contenteditable="${isEditing ? 'true' : 'false'}">[ Öğrenci cevabı buraya yazılacaktır .......... ]</div>
        `;
        newBlock.appendChild(footerEl);

        if (afterBlock && afterBlock.parentNode) {
            afterBlock.after(newBlock);
        } else {
            renderedMarkdown.appendChild(newBlock);
        }

        if (resetBtn) resetBtn.style.display = 'inline-flex';
        newBlock.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    function moveModularBlock(block, dir) {
        if (dir === 'up') {
            const prev = block.previousElementSibling;
            if (prev && (prev.classList.contains('editable-section-block') || prev.classList.contains('mmr-section-card'))) {
                prev.before(block);
                if (resetBtn) resetBtn.style.display = 'inline-flex';
            }
        } else if (dir === 'down') {
            const next = block.nextElementSibling;
            if (next && (next.classList.contains('editable-section-block') || next.classList.contains('mmr-section-card'))) {
                next.after(block);
                if (resetBtn) resetBtn.style.display = 'inline-flex';
            }
        }
    }

    // 4.8. Modern Sınav & Çalışma Kağıdı Başlık Bloğu
    function createExamHeader(title, subtitle, badgeText) {
        const header = document.createElement('div');
        header.className = 'material-exam-header';
        header.innerHTML = `
            <div class="exam-header-top">
                <div class="exam-brand">
                    <div class="exam-brand-icon"><i class="fa-solid fa-graduation-cap"></i></div>
                    <div class="exam-titles">
                        <h2>T.C. MİLLÎ EĞİTİM BAKANLIĞI • TÜRKİYE YÜZYILI MAARİF MODELİ</h2>
                        <p>${subtitle || 'Muallimin Manevi Rehberi (MMR) İlkeleriyle Derinleştirilmiş Öğrenci Çalışma Kağıdı'}</p>
                    </div>
                </div>
                <div class="exam-badge-tag"><i class="fa-solid fa-award"></i> ${badgeText || '5. Sınıf Fen Bilimleri'}</div>
            </div>
            <div class="exam-student-grid">
                <div class="exam-student-field"><strong>Adı Soyadı:</strong> <span class="fill-line"></span></div>
                <div class="exam-student-field"><strong>Sınıf / Şube:</strong> <span class="fill-line"></span></div>
                <div class="exam-student-field"><strong>Okul No:</strong> <span class="fill-line"></span></div>
                <div class="exam-student-field"><strong>Tarih / Puan:</strong> <span class="fill-line"></span></div>
            </div>
        `;
        return header;
    }

    // 5. Modular Content Rendering with Unified MMR Cards & Page Fitting
    function renderModularContent(markdownText) {
        const cleanMarkdown = sanitizeEducationalText(markdownText);
        if (typeof marked === 'undefined') {
            renderedMarkdown.innerText = cleanMarkdown;
            return;
        }

        const rawHtml = marked.parse(cleanMarkdown);
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = rawHtml;

        const children = Array.from(tempDiv.children);
        renderedMarkdown.innerHTML = '';

        // Add Modern MEB & Maarif Künye Anteti
        const gradeVal = gradeSelect ? gradeSelect.value : '5. Sınıf';
        const subVal = subjectSelect ? subjectSelect.value : 'Fen Bilimleri';
        const topicVal = topicInput ? topicInput.value : '';
        const examHeader = createExamHeader(
            `${gradeVal.toUpperCase()} ${subVal.toUpperCase()} ÖĞRENCİ ÇALIŞMA KAĞIDI`,
            `${topicVal ? topicVal + ' • ' : ''}Muallimin Manevi Rehberi (MMR) İlkeleriyle Derinleştirilmiş Öğrenme Kağıdı`,
            `${gradeVal} ${subVal}`
        );
        renderedMarkdown.appendChild(examHeader);

        // Add Sayfa Sığdırma Butonları (Page Chunk Nav)
        const chunkNav = document.createElement('div');
        chunkNav.className = 'page-chunk-nav';
        chunkNav.innerHTML = `
            <span style="font-size:0.8rem; font-weight:700; color:#64748b;"><i class="fa-solid fa-file-lines"></i> Sayfa Sığdırma:</span>
            <button class="btn-chunk active" type="button" data-filter="all"><i class="fa-solid fa-layer-group"></i> Tümü (1-10)</button>
            <button class="btn-chunk" type="button" data-filter="p1"><i class="fa-solid fa-1"></i> Sayfa 1 (1-4)</button>
            <button class="btn-chunk" type="button" data-filter="p2"><i class="fa-solid fa-2"></i> Sayfa 2 (5-7)</button>
            <button class="btn-chunk" type="button" data-filter="p3"><i class="fa-solid fa-3"></i> Sayfa 3 (8-10)</button>
        `;

        chunkNav.querySelectorAll('.btn-chunk').forEach(btn => {
            btn.onclick = () => {
                chunkNav.querySelectorAll('.btn-chunk').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                const filter = btn.getAttribute('data-filter');
                const cards = renderedMarkdown.querySelectorAll('.mmr-section-card');
                cards.forEach((card, idx) => {
                    const secNum = parseInt(card.getAttribute('data-sec-num')) || (idx + 1);
                    if (filter === 'all') {
                        card.style.display = 'block';
                    } else if (filter === 'p1') {
                        card.style.display = (secNum >= 1 && secNum <= 4) ? 'block' : 'none';
                    } else if (filter === 'p2') {
                        card.style.display = (secNum >= 5 && secNum <= 7) ? 'block' : 'none';
                    } else if (filter === 'p3') {
                        card.style.display = (secNum >= 8 && secNum <= 10) ? 'block' : 'none';
                    }
                });
            };
        });

        renderedMarkdown.appendChild(chunkNav);

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
                currentCard.className = 'mmr-section-card editable-section-block';
                currentCard.setAttribute('data-sec-num', secNum);

                const toolbar = createSectionToolbar(currentCard);
                currentCard.appendChild(toolbar);

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

                const contentWrap = document.createElement('div');
                contentWrap.className = 'mmr-card-body block-content';
                contentWrap.contentEditable = isEditing ? 'true' : 'false';
                contentWrap.addEventListener('input', () => {
                    if (resetBtn) resetBtn.style.display = 'inline-flex';
                });
                currentCard.appendChild(contentWrap);

                renderedMarkdown.appendChild(currentCard);

                if (['h1', 'h2', 'h3'].includes(tag) || (match && match[1])) {
                    return;
                }
            }

            const blockContent = currentCard.querySelector('.block-content');
            if (blockContent) {
                blockContent.appendChild(child);
            }
        });
    }

    // 5.5. Çift Sütunlu Yaprak Test Mizanpajı & Optik Form
    function renderTestContent(markdownText) {
        const cleanMarkdown = sanitizeEducationalText(markdownText);
        renderedMarkdown.innerHTML = '';

        // 1. Exam Header
        const gradeVal = gradeSelect ? gradeSelect.value : '5. Sınıf';
        const subVal = subjectSelect ? subjectSelect.value : 'Fen Bilimleri';
        const topicVal = topicInput ? topicInput.value : '';
        const examHeader = createExamHeader(
            `${gradeVal.toUpperCase()} ${subVal.toUpperCase()} KAZANIM DEĞERLENDİRME YAPRAK TESTİ`,
            `${topicVal ? topicVal + ' • ' : ''}Kazanım ve Süreç Değerlendirme Yaprak Testi`,
            `${gradeVal} ${subVal}`
        );
        renderedMarkdown.appendChild(examHeader);

        // 2. Toolbar Strip
        const toolbar = document.createElement('div');
        toolbar.className = 'test-toolbar-strip';
        toolbar.innerHTML = `
            <div class="left-info">
                <span><i class="fa-solid fa-table-columns" style="color:#0f766e;"></i> <strong>Mizanpaj:</strong> Çift Sütunlu Sayfa Düzeni</span>
                <span>•</span>
                <span><i class="fa-solid fa-circle-check" style="color:#1e3a8a;"></i> 4 Şıklı Çoktan Seçmeli</span>
            </div>
            <div class="right-actions">
                <button class="btn-test-action" id="appBtnToggleAnswers" type="button">
                    <i class="fa-solid fa-key"></i> Cevapları Göster / Gizle
                </button>
                <button class="btn-test-action" id="appBtnOptical" type="button">
                    <i class="fa-solid fa-circle-dot"></i> Optik Form
                </button>
                <button class="btn-test-action" id="appBtnPrint" type="button">
                    <i class="fa-solid fa-print"></i> Yazdır / PDF
                </button>
            </div>
        `;
        renderedMarkdown.appendChild(toolbar);

        // 3. Parse Questions
        const lines = cleanMarkdown.split('\n');
        const questions = [];
        let currentQ = null;
        let inAnswerKey = false;
        const answerKeyLines = [];

        lines.forEach(line => {
            const trimmed = line.trim();
            if (/^(?:#+\s*)?(?:CEVAP\s*ANAHTARI|Cevap\s*Anahtarı)/i.test(trimmed)) {
                inAnswerKey = true;
                if (currentQ) questions.push(currentQ);
                currentQ = null;
                return;
            }

            if (inAnswerKey) {
                answerKeyLines.push(line);
                return;
            }

            const qMatch = trimmed.match(/^(?:#+\s*)?(?:Soru\s*|SORU\s*)?(\d+)[.):]\s*(.*)/i);
            if (qMatch && !/^[A-D]\)/i.test(trimmed)) {
                if (currentQ) questions.push(currentQ);
                currentQ = {
                    num: qMatch[1],
                    title: qMatch[2] || '',
                    meta: '',
                    body: [],
                    options: []
                };
                return;
            }

            if (currentQ) {
                const optMatch = trimmed.match(/^[-*]?\s*([A-D])\s*[).:]\s*(.*)/i);
                if (optMatch) {
                    const optLetter = optMatch[1].toUpperCase();
                    let optText = optMatch[2].trim();
                    const isCorrect = optText.includes('✔') || optText.includes('[✔]') || optText.includes('*');
                    optText = optText.replace(/\[?✔\]?/g, '').replace(/^\*|\*$/g, '').trim();
                    currentQ.options.push({
                        letter: optLetter,
                        text: optText,
                        isCorrect: isCorrect
                    });
                } else if (/^\[?(?:Bilişsel|Düzey|Puan)/i.test(trimmed)) {
                    currentQ.meta = trimmed.replace(/^\[|\]$/g, '').trim();
                } else if (trimmed) {
                    currentQ.body.push(trimmed);
                }
            }
        });
        if (currentQ) questions.push(currentQ);

        // If no questions parsed (fallback)
        if (questions.length === 0) {
            const fallbackDiv = document.createElement('div');
            fallbackDiv.className = 'markdown-body';
            fallbackDiv.innerHTML = marked.parse(cleanMarkdown);
            renderedMarkdown.appendChild(fallbackDiv);
            return;
        }

        // 4. 2-Column Grid
        const columnsGrid = document.createElement('div');
        columnsGrid.className = 'test-columns-grid';
        columnsGrid.id = 'appTestColumnsGrid';

        const colLeft = document.createElement('div');
        colLeft.className = 'test-col';
        const colRight = document.createElement('div');
        colRight.className = 'test-col';

        const half = Math.ceil(questions.length / 2);

        questions.forEach((q, idx) => {
            const qCard = document.createElement('div');
            qCard.className = 'test-q-card editable-section-block';
            qCard.setAttribute('data-q', q.num);

            // Soru Başlığı
            const headerWrap = document.createElement('div');
            headerWrap.className = 'test-q-header';
            headerWrap.innerHTML = `
                <div class="test-q-badge-wrap">
                    <span class="test-q-num">${q.num}</span>
                    <span class="test-q-level">${q.meta ? q.meta.split('|')[0].trim() : 'Kazanım Değerlendirme'}</span>
                </div>
                <span class="test-q-point">${q.meta && q.meta.includes('|') ? q.meta.split('|')[1].trim() : '16.6 Puan'}</span>
            `;
            qCard.appendChild(headerWrap);

            // Soru Gövdesi
            const bodyWrap = document.createElement('div');
            bodyWrap.className = 'test-q-body block-content';
            bodyWrap.contentEditable = isEditing ? 'true' : 'false';
            const bodyHtml = marked.parse(q.body.join('\n\n'));
            bodyWrap.innerHTML = (q.title ? `<strong>${q.title}</strong><br>` : '') + bodyHtml;
            qCard.appendChild(bodyWrap);

            // Şıklar
            const optsWrap = document.createElement('div');
            optsWrap.className = 'test-options-list';
            q.options.forEach(opt => {
                const optEl = document.createElement('div');
                optEl.className = 'test-opt-item' + (opt.isCorrect ? ' correct-answer' : '');
                optEl.setAttribute('data-letter', opt.letter);
                optEl.innerHTML = `
                    <span class="opt-circle">${opt.letter}</span>
                    <span class="opt-text">${opt.text}</span>
                `;
                optEl.onclick = () => {
                    optsWrap.querySelectorAll('.test-opt-item').forEach(o => o.classList.remove('selected'));
                    optEl.classList.add('selected');
                    const bWrap = renderedMarkdown.querySelector(`.optical-bubbles[data-q="${q.num}"]`);
                    if (bWrap) {
                        bWrap.querySelectorAll('.optical-bubble').forEach(b => {
                            b.classList.toggle('filled', b.getAttribute('data-letter') === opt.letter);
                        });
                    }
                };
                optsWrap.appendChild(optEl);
            });
            qCard.appendChild(optsWrap);

            if (idx < half) {
                colLeft.appendChild(qCard);
            } else {
                colRight.appendChild(qCard);
            }
        });

        columnsGrid.appendChild(colLeft);
        columnsGrid.appendChild(colRight);
        renderedMarkdown.appendChild(columnsGrid);

        // 5. Mini Optik Form Simülasyonu
        const opticalBox = document.createElement('div');
        opticalBox.className = 'optical-form-card';
        opticalBox.id = 'appOpticalBox';
        opticalBox.innerHTML = `
            <div class="optical-header">
                <div class="optical-title">
                    <i class="fa-solid fa-circle-dot"></i> ÖĞRENCİ OPTİK CEVAP KODLAMA ALANI
                </div>
                <span style="font-size:0.75rem; color:#64748b;">(Cevabınızı işaretlemek için baloncuğa tıklayınız)</span>
            </div>
        `;

        const optGrid = document.createElement('div');
        optGrid.className = 'optical-grid';
        questions.forEach(q => {
            const row = document.createElement('div');
            row.className = 'optical-row';
            row.innerHTML = `
                <span class="optical-q-num">${q.num}.</span>
                <div class="optical-bubbles" data-q="${q.num}">
                    <span class="optical-bubble" data-letter="A">A</span>
                    <span class="optical-bubble" data-letter="B">B</span>
                    <span class="optical-bubble" data-letter="C">C</span>
                    <span class="optical-bubble" data-letter="D">D</span>
                </div>
            `;
            row.querySelectorAll('.optical-bubble').forEach(bubble => {
                bubble.onclick = () => {
                    const bLetter = bubble.getAttribute('data-letter');
                    row.querySelectorAll('.optical-bubble').forEach(b => b.classList.remove('filled'));
                    bubble.classList.add('filled');
                    const card = columnsGrid.querySelector(`.test-q-card[data-q="${q.num}"]`);
                    if (card) {
                        card.querySelectorAll('.test-opt-item').forEach(opt => {
                            opt.classList.toggle('selected', opt.getAttribute('data-letter') === bLetter);
                        });
                    }
                };
            });
            optGrid.appendChild(row);
        });
        opticalBox.appendChild(optGrid);
        renderedMarkdown.appendChild(opticalBox);

        // 6. Öğretmen Cevap Anahtarı ve Matris Kutusu
        const matrixBox = document.createElement('div');
        matrixBox.className = 'test-matrix-box';
        matrixBox.id = 'appMatrixBox';
        matrixBox.style.display = 'none';
        matrixBox.innerHTML = `
            <h3><i class="fa-solid fa-key"></i> Öğretmen İçin Cevap Anahtarı & Bilişsel Düzey Matrisi</h3>
        `;
        if (answerKeyLines.length > 0) {
            const akHtml = marked.parse(answerKeyLines.join('\n'));
            const akDiv = document.createElement('div');
            akDiv.innerHTML = akHtml;
            matrixBox.appendChild(akDiv);
        } else {
            const table = document.createElement('table');
            table.className = 'test-matrix-table';
            let rowsHtml = '<tr><th>Soru</th><th>Doğru Cevap</th><th>Puan</th><th>Bilişsel Düzey</th></tr>';
            questions.forEach(q => {
                const correctOpt = q.options.find(o => o.isCorrect);
                rowsHtml += `<tr>
                    <td><strong>${q.num}</strong></td>
                    <td><strong style="color:#10b981;">${correctOpt ? correctOpt.letter : '-'}</strong></td>
                    <td>16.6</td>
                    <td>${q.meta || 'Kazanım Değerlendirme'}</td>
                </tr>`;
            });
            table.innerHTML = rowsHtml;
            matrixBox.appendChild(table);
        }
        renderedMarkdown.appendChild(matrixBox);

        // 7. Buton Olayları
        const toggleBtn = toolbar.querySelector('#appBtnToggleAnswers');
        if (toggleBtn) {
            toggleBtn.onclick = () => {
                columnsGrid.classList.toggle('teacher-mode-active');
                const isActive = columnsGrid.classList.contains('teacher-mode-active');
                toggleBtn.classList.toggle('active', isActive);
                toggleBtn.innerHTML = isActive 
                    ? '<i class="fa-solid fa-eye-slash"></i> Cevapları Gizle' 
                    : '<i class="fa-solid fa-key"></i> Cevapları Göster / Gizle';
                matrixBox.style.display = isActive ? 'block' : 'none';
                if (isActive) matrixBox.scrollIntoView({ behavior: 'smooth', block: 'start' });
            };
        }

        const optBtn = toolbar.querySelector('#appBtnOptical');
        if (optBtn) {
            optBtn.onclick = () => {
                opticalBox.scrollIntoView({ behavior: 'smooth' });
            };
        }

        const printBtn = toolbar.querySelector('#appBtnPrint');
        if (printBtn) {
            printBtn.onclick = () => {
                window.print();
            };
        }
    }

    // 6. Edit Mode Toggle
    if (editToggleBtn) {
        editToggleBtn.addEventListener('click', () => {
            isEditing = !isEditing;
            if (isEditing) {
                if (renderedMarkdown) renderedMarkdown.classList.add('edit-mode-active');
                editToggleBtn.classList.add('active');
                editToggleBtn.innerHTML = '<i class="fa-solid fa-check"></i> <span>Bitti</span>';
                if (editHintBanner) editHintBanner.classList.remove('hidden');
                if (renderedMarkdown) {
                    renderedMarkdown.querySelectorAll('.block-content').forEach(el => {
                        el.contentEditable = 'true';
                    });
                }
                if (resetBtn) resetBtn.style.display = 'inline-flex';
            } else {
                if (renderedMarkdown) renderedMarkdown.classList.remove('edit-mode-active');
                editToggleBtn.classList.remove('active');
                editToggleBtn.innerHTML = '<i class="fa-solid fa-pen-to-square"></i> <span>Düzenle</span>';
                if (editHintBanner) editHintBanner.classList.add('hidden');
                if (renderedMarkdown) {
                    renderedMarkdown.querySelectorAll('.block-content').forEach(el => {
                        el.contentEditable = 'false';
                    });
                }
            }
        });
    }

    // 6.5. Top Add Section Button
    const addSectionBtn = document.getElementById('addSectionBtn');
    if (addSectionBtn) {
        addSectionBtn.addEventListener('click', () => {
            addNewModularSection();
        });
    }

    // 7. Reset to Original
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            if (confirm('Tüm değişiklikleri geri alıp içeriği ilk haline döndürmek istiyor musunuz?')) {
                const isTest = (contentTypeSelect && contentTypeSelect.value === 'test') || /Soru\s*\d+/i.test(originalMarkdown);
                if (isTest) {
                    renderTestContent(originalMarkdown);
                } else {
                    renderModularContent(originalMarkdown);
                }
                resetBtn.style.display = 'none';
                if (isEditing && editToggleBtn) {
                    editToggleBtn.click();
                }
            }
        });
    }

    // 8. Extract Current Clean Text (Ignoring Deleted Sections)
    function getCurrentCleanText() {
        const blocks = renderedMarkdown.querySelectorAll('.editable-section-block');
        if (blocks.length === 0) return originalMarkdown;

        let outputLines = [];
        blocks.forEach(block => {
            const content = block.querySelector('.block-content');
            if (content) {
                // Get innerText line by line
                outputLines.push(content.innerText.trim());
                outputLines.push('');
            }
        });
        return outputLines.join('\n');
    }

    // 9. Actions: Copy, Print, Word Export
    copyBtn.addEventListener('click', async () => {
        const textToCopy = getCurrentCleanText();
        if (!textToCopy) return;
        try {
            await navigator.clipboard.writeText(textToCopy);
            const orig = copyBtn.innerHTML;
            copyBtn.innerHTML = '<i class="fa-solid fa-check"></i> Kopyalandı!';
            setTimeout(() => { copyBtn.innerHTML = orig; }, 2000);
        } catch (err) {
            alert('Kopyalama başarısız oldu.');
        }
    });

    printBtn.addEventListener('click', () => {
        // If editing is open, close edit mode before print so no dashed borders show
        if (isEditing) {
            editToggleBtn.click();
        }
        window.print();
    });

    docxBtn.addEventListener('click', async () => {
        const textToExport = getCurrentCleanText();
        if (!textToExport) return;

        const orig = docxBtn.innerHTML;
        docxBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> İndiriliyor...';
        docxBtn.disabled = true;

        try {
            const res = await fetch('/api/export-docx', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    content: textToExport,
                    title: currentTitle
                })
            });

            if (!res.ok) throw new Error('Word dosyası indirilemedi.');

            const blob = await res.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = `${currentTitle}.docx`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(downloadUrl);
        } catch (err) {
            alert('Word dosyası oluşturulurken hata oluştu.');
        } finally {
            docxBtn.innerHTML = orig;
            docxBtn.disabled = false;
        }
    });

    function showAlert(msg) {
        formAlert.textContent = msg;
        formAlert.className = 'alert-box error';
        formAlert.classList.remove('hidden');
    }

    function hideAlert() {
        formAlert.classList.add('hidden');
        formAlert.textContent = '';
    }
});
