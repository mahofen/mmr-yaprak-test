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

    // 1. Health Check
    fetch('/api/health')
        .then(res => res.json())
        .then(data => {
            const dot = apiStatus.querySelector('.status-dot');
            const text = apiStatus.querySelector('.status-text');
            if (data.has_api_key) {
                dot.className = 'status-dot active';
                text.textContent = 'Gemini API Bağlı';
            } else {
                dot.className = 'status-dot error';
                text.textContent = 'API Anahtarı Eksik (.env)';
            }
        })
        .catch(() => {
            const dot = apiStatus.querySelector('.status-dot');
            const text = apiStatus.querySelector('.status-text');
            dot.className = 'status-dot error';
            text.textContent = 'Sunucu Bağlantı Hatası';
        });

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
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
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
                throw new Error(result.error || 'İçerik oluşturulurken bir sorun oluştu. Lütfen bilgileri kontrol ederek tekrar deneyin.');
            }

            originalMarkdown = result.content;
            currentMarkdown = result.content;

            renderModularContent(currentMarkdown);

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

    function addNewModularSection(afterBlock = null) {
        const title = prompt('Eklenecek yeni bölüm başlığını yazınız:', 'YENİ ETKİNLİK / BÖLÜM');
        if (!title) return;

        const newBlock = document.createElement('div');
        newBlock.className = 'editable-section-block';

        const toolbar = createSectionToolbar(newBlock);
        newBlock.appendChild(toolbar);

        const contentWrap = document.createElement('div');
        contentWrap.className = 'block-content';
        contentWrap.contentEditable = isEditing ? 'true' : 'false';
        contentWrap.innerHTML = `<h3><i class="fa-solid fa-sparkles"></i> ${title}</h3><p>Buraya yeni etkinlik, açıklama veya soru metnini yazabilirsiniz.</p>`;
        contentWrap.addEventListener('input', () => {
            if (resetBtn) resetBtn.style.display = 'inline-flex';
        });
        newBlock.appendChild(contentWrap);

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
            if (prev && prev.classList.contains('editable-section-block')) {
                prev.before(block);
                if (resetBtn) resetBtn.style.display = 'inline-flex';
            }
        } else if (dir === 'down') {
            const next = block.nextElementSibling;
            if (next && next.classList.contains('editable-section-block')) {
                next.after(block);
                if (resetBtn) resetBtn.style.display = 'inline-flex';
            }
        }
    }

    // 5. Modular Content Rendering (Allows section-by-section deletion & editing)
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

        let currentBlock = null;

        children.forEach(child => {
            const tag = child.tagName.toLowerCase();
            // Start a new section block on headings or horizontal rules
            if (['h1', 'h2', 'h3', 'h4', 'hr'].includes(tag) || !currentBlock) {
                currentBlock = document.createElement('div');
                currentBlock.className = 'editable-section-block';

                const toolbar = createSectionToolbar(currentBlock);
                currentBlock.appendChild(toolbar);

                const contentWrap = document.createElement('div');
                contentWrap.className = 'block-content';
                contentWrap.contentEditable = isEditing ? 'true' : 'false';
                contentWrap.addEventListener('input', () => {
                    if (resetBtn) resetBtn.style.display = 'inline-flex';
                });
                currentBlock.appendChild(contentWrap);

                renderedMarkdown.appendChild(currentBlock);
            }

            const blockContent = currentBlock.querySelector('.block-content');
            if (blockContent) {
                blockContent.appendChild(child);
            }
        });
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
                renderModularContent(originalMarkdown);
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
