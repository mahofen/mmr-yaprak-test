import os
import json
import logging
import urllib.request
import urllib.error
from io import BytesIO
from flask import Flask, render_template, request, jsonify, send_file
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Load .env supporting standard UTF-8 and UTF-8-BOM
load_dotenv(encoding='utf-8-sig')

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

GEMINI_MODELS = [
    'gemini-3.5-flash-lite',
    'gemini-flash-latest',
    'gemini-3.6-flash',
    'gemini-3.1-pro-preview'
]

def get_api_key(custom_key=None):
    if custom_key and isinstance(custom_key, str) and custom_key.strip():
        return custom_key.strip()
    key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY') or ''
    return key.strip()

def call_gemini_api(system_instruction: str, user_prompt: str, custom_key: str = None) -> str:
    api_key = get_api_key(custom_key)
    if not api_key:
        raise ValueError('GEMINI_API_KEY bulunamadı. Vercel panelinde (Settings > Environment Variables) GEMINI_API_KEY tanımlayınız veya sağ üstteki API durum rozetine tıklayarak anahtarınızı giriniz.')

    payload = {
        'systemInstruction': {
            'parts': [{'text': system_instruction}]
        },
        'contents': [
            {
                'role': 'user',
                'parts': [{'text': user_prompt}]
            }
        ],
        'generationConfig': {
            'temperature': 0.7,
            'topP': 0.95,
            'maxOutputTokens': 8192
        }
    }
    
    headers = {'Content-Type': 'application/json'}
    last_error = None

    for model in GEMINI_MODELS:
        url = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}'
        try:
            logger.info(f'Gemini model {model} ile istek gönderiliyor...')
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode('utf-8'))
                candidates = result.get('candidates', [])
                if candidates and 'content' in candidates[0]:
                    parts = candidates[0]['content'].get('parts', [])
                    if parts and 'text' in parts[0]:
                        logger.info(f'Gemini model {model} başarıyla yanıt üretti.')
                        return parts[0]['text']
                raise ValueError('API geçerli bir içerik döndürmedi.')
        except urllib.error.HTTPError as e:
            err_body = e.read().decode('utf-8', errors='ignore')
            logger.warning(f'Model {model} HTTP {e.code} hatası: {err_body[:200]}')
            last_error = f'HTTP {e.code}: {err_body[:120]}'
            continue
        except Exception as e:
            logger.warning(f'Model {model} hatası: {str(e)}')
            last_error = str(e)
            continue

    raise RuntimeError(f'Gemini API çağrısı başarısız oldu. Son hata: {last_error}')

def build_worksheet_prompt(data: dict) -> tuple[str, str]:
    system_instruction = (
        'Sen; Türkiye Yüzyılı Maarif Modeli (TYMM), bağlam temelli öğrenme, '
        'Erdem-Değer-Eylem (EDE) yaklaşımı ve Muallimin Manevi Rehberi (MMR) konusunda uzman '
        'bir öğretim tasarımcısı ve deneyimli bir öğretmensin.\n\n'
        'TEMEL MMR FELSEFESİ:\n'
        'Amaç çalışma kağıdına sonradan yapay manevi kelimeler eklemek değil; öğrencinin öğrendiği ders bilgisinin '
        'içindeki anlamı, hikmeti, düzeni, ölçüyü, yaratılış gerçeğini, insanın sorumluluğunu ve değer boyutunu '
        'kendi zihninde keşfetmesini sağlamaktır.\n\n'
        'Pedagojik Akış:\n'
        'Bilgi → Düşünme → Anlamlandırma → Tefekkür → Şuur → Erdem → Değer → Eylem\n\n'
        'KESİN KURALLAR VE "HAZIR CEVAP" YASAĞI:\n'
        '- MMR\'yi ayrı bir din dersi gibi uygulama; vaaz, nasihat veya hazır dogmatik sonuç verme.\n'
        '- "Bu olay Allah\'ın sonsuz kudretini gösterir / şükretmeliyiz" gibi hazır yargıları öğrenciye dayatma.\n'
        '- Bunun yerine öğrenciyi düşündür: "Bu düzen sana ne düşündürüyor?", "Bunun insan hayatındaki karşılığı ne olabilir?", "Buradaki ölçü ve denge bize ne anlatabilir?"\n'
        '- AKIL VE KALP DENGESİ: Akıl (Bilgi, Analiz, Neden-Sonuç) + Kalp (Hayret, Sorumluluk, Anlam, Hikmet, Vicdan) = ŞUUR.\n'
        '- DERSİN DOĞASINA UYGUNLUK: Fen bilimlerinde düzen, ölçü, denge, canlılık, ekolojik sorumluluk üzerinden doğal bağ kur.\n'
        '- Öğrencinin yazabileceği yeterli noktalı alanlar [ .......... ] ve işaretleme kutuları [ ] bırak.'
    )

    user_prompt = (
        f'Aşağıda verilen eğitim bilgilerini temel alarak MUALLİMİN MANEVİ REHBERİ (MMR) İLKELERİYLE DERİNLEŞTİRİLMİŞ '
        f'eksiksiz bir ÇALIŞMA KAĞIDI hazırla:\n\n'
        f'Sınıf Seviyesi: {data.get("grade")}\n'
        f'Ders: {data.get("subject")}\n'
        f'Öğrenme Alanı: {data.get("learning_area")}\n'
        f'Konu: {data.get("topic")}\n'
        f'Öğrenme Çıktısı: {data.get("learning_outcome")}\n'
        f'Manevi Öğrenme Çıktısı: {data.get("manevi_outcome", "")}\n'
        f'İçerik Türü: Çalışma Kağıdı\n\n'
        f'Başlık Tablosu: Ders, Sınıf, Öğrenme Alanı, Konu, Öğrenme Çıktısı, hemen altında Manevi Öğrenme Çıktısı, Ad Soyad ve Tarih yer alsın.\n\n'
        f'Çalışma kağıdını TAM OLARAK aşağıdaki 10 bölümden oluştur:\n\n'
        f'1. MERAK ET (Merak & İkinci Düşünme Kapısı): Konuya giriş sorusunun ardından öğrenciye "Bu sistem neden böyle çalışıyor?" ve '
        f'"Bu kadar düzenli işleyen bir sistemde seni en çok düşündüren şey nedir?" gibi arkasındaki nizamı sorgulatan açık uçlu bir soru sun.\n\n'
        f'2. BAĞLAMI İNCELE (Mana Taşıyıcısı Olay): Gerçekçi, öğrencinin hayatına yakın günlük yaşam senaryosu. Olayın içinde düzen, ölçü, '
        f'denge ve insan-doğa ilişkisi doğal olarak bulunsun. Akış: Olay → Bilgi → Gözlem → Sebep-Sonuç → Anlam.\n\n'
        f'3. FARK ET (Kainatı Okuma & Hayret): Öğrencinin düzeni, ölçüyü, parçalar arasındaki mükemmel uyumu keşfedeceği 2 etkinlik. '
        f'Sonuna "Bu düzen ve uyum sana ne düşündürüyor? Seni hayran bırakan özellik nedir?" sorusunu ekle.\n\n'
        f'4. BİLGİYİ KULLAN (Bilgiden Manaya): Sağlam bilimsel bilgi kullanımı ve yaygın kavram yanılgılarını düzelten etkinlik. '
        f'Ardından "Bu bilimsel gerçeği öğrendiğinde olaylara bakışında ne değişti?" geçişini sağla.\n\n'
        f'5. DÜŞÜN VE İLİŞKİLENDİR: Bilimsel gerçek → düzen → anlam → insan → sorumluluk zincirini kurduran 2 analitik soru.\n\n'
        f'6. TEFEKKÜR PENCERESİ (4 Aşamalı Mimari): Çalışma kağıdının kalbi. Sırasıyla şu 4 aşamayı uygulat:\n'
        f'   - 1. GÖRDÜM: Bilimsel olarak neyi fark ettim?\n'
        f'   - 2. DÜŞÜNDÜM: Bu düzen, ölçü ve denge bana ne düşündürdü?\n'
        f'   - 3. ANLAMLANDIRDIM: Bu olayın hayat, insan veya varlık açısından anlamı nedir?\n'
        f'   - 4. DEĞERLENDİRDİM: Bu farkındalık benim davranışlarımı nasıl etkileyebilir?\n\n'
        f'7. ERDEM VE DEĞER (Derinleştirilmiş Akış): Değeri doğrudan söyleme. Tablo formatında şu adımları işlet:\n'
        f'   Ne fark ettim? → Bu bana ne düşündürdü? → İnsan hayatındaki önemi nedir? → Hangi değeri görüyorum? → Davranışımda nasıl görünür?\n\n'
        f'8. MÜZAKERE EDELİM: Sınıfta tartışılabilecek, farklı fikirleri gerekçelendirmeye imkan veren 2-3 açık uçlu müzakere sorusu.\n\n'
        f'9. EYLEME DÖNÜŞTÜR (Somut Sorumluluk): Fark ettiğim şey → Değerim → Davranışım. (Ne yapacağım? Ne zaman? Kime/neye fayda sağlayacak?).\n\n'
        f'10. KENDİMİ DEĞERLENDİRİYORUM (Şuurlu Öz Değerlendirme): 3 düzeyde öz yansıtma:\n'
        f'   - BİLGİ: Bugün ne öğrendim?\n'
        f'   - ANLAM: Bugün hangi konuda farklı düşünmeye başladım?\n'
        f'   - DEĞER / EYLEM: Öğrendiğim ve fark ettiğim şey davranışlarımı nasıl etkileyecek?\n\n'
        f'BİÇİMLENDİRME VE YAZI KARAKTERİ KURALLARI:\n'
        f'- KESİNLİKLE LaTeX veya formül kodları ($\rightarrow$, \\rightarrow, \\to vb.) KULLANMA.\n'
        f'- Ok işaretleri için doğrudan UTF-8 "→" sembolünü kullan.\n'
        f'- İşaretleme kutuları için temiz [ ] veya [✔] kullan.\n'
        f'- Tefekkür Penceresi dahil tüm bölümleri aynı başlık hiyerarşisi ve tasarım bütünlüğünde sun.\n'
        f'Çıktıyı temiz, doğrudan yazdırılabilir ve öğrencinin doldurabileceği formatta üret.'
    )

    return system_instruction, user_prompt

def build_test_prompt(data: dict) -> tuple[str, str]:
    system_instruction = (
        'Sen; Türkiye Yüzyılı Maarif Modeli (TYMM), ölçme-değerlendirme ilkeleri, '
        'Erdem-Değer-Eylem (EDE) yaklaşımı ve Muallimin Manevi Rehberi (MMR) konusunda uzman '
        'bir ölçme-değerlendirme uzmanı ve deneyimli bir öğretmensin.\n\n'
        'Temel Görevin:\n'
        'Öğrencinin verilen öğrenme çıktısına ulaşma düzeyini geçerli, güvenilir ve nesnel biçimde '
        'ölçen bir YAPRAK TEST hazırlamaktır.\n\n'
        'Bilişsel Düzeyler:\n'
        'Hatırlama → Anlama → Uygulama → Analiz → Değerlendirme basamaklarını dengeli dağıt.\n\n'
        'KESİN ÖLÇME KURALLARI:\n'
        '- Yalnızca verilen öğrenme çıktısını ölç. Yeni kazanım ekleme.\n'
        '- Her soru 4 seçenekli (A, B, C, D) olmalıdır.\n'
        '- Tek ve tartışmasız bir doğru cevap bulunmalıdır.\n'
        '- Çeldiriciler bilimsel kavram yanılgılarına dayalı ve güçlü olmalıdır.\n'
        '- Hepsi veya Hiçbiri gibi seçenekleri asla kullanma.\n'
        '- Doğru cevabın uzunluğu diğer şıklardan belirgin biçimde farklı olmamalıdır.\n'
        '- Uygun sorularda günlük yaşam bağlamları, modeller veya tablolar kullan.\n'
        '- MMR boyutu için inancı doğrudan ölçen sorular sorma. Nizam, ölçü ve hikmet boyutunu akıl yürütmeye dayalı sor.\n'
        '- Testin en sonunda öğretmen için CEVAP ANAHTARI VE BİLİŞSEL DÜZEY MATRİSİ tablosu ekle.'
    )

    count = data.get('question_count', 8)
    difficulty = data.get('difficulty', 'Orta')

    user_prompt = (
        f'Aşağıda verilen eğitim bilgilerini temel alarak eksiksiz bir YAPRAK TEST hazırla:\n\n'
        f'Sınıf Seviyesi: {data.get("grade")}\n'
        f'Ders: {data.get("subject")}\n'
        f'Öğrenme Alanı: {data.get("learning_area")}\n'
        f'Konu: {data.get("topic")}\n'
        f'Öğrenme Çıktısı: {data.get("learning_outcome")}\n'
        f'Manevi Öğrenme Çıktısı: {data.get("manevi_outcome", "")}\n'
        f'İçerik Türü: Yaprak Test\n'
        f'Soru Sayısı: {count}\n'
        f'Zorluk Seviyesi: {difficulty}\n\n'
        f'Başlık Formatı: [{data.get("subject").upper()}] - [{data.get("grade").upper()}] YAPRAK TEST\n'
        f'Öğrenme Alanı, Konu, Öğrenme Çıktısı, hemen altına Manevi Öğrenme Çıktısı, Ad Soyad, Sınıf/No, Tarih, Puan kutusu ekle.\n\n'
        f'Soruları kolaydan zora sırala ve bilişsel basamakları dengeli dağıt.\n'
        f'Her soru için 4 seçenek (A, B, C, D) kullan.\n\n'
        f'BİÇİMLENDİRME VE YAZI KARAKTERİ KURALLARI:\n'
        f'- KESİNLİKLE LaTeX veya formül kodları ($\rightarrow$, \\rightarrow, \\to vb.) KULLANMA.\n'
        f'- Ok işaretleri için doğrudan UTF-8 "→" sembolünü kullan.\n'
        f'Çıktıyı temiz, akademik ve yazdırılabilir Markdown olarak üret.'
    )

    return system_instruction, user_prompt

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health')
def health():
    key = get_api_key()
    has_key = bool(key and len(key) > 10)
    return jsonify({
        'status': 'ok',
        'has_api_key': has_key
    })

@app.route('/api/sample-units')
def sample_units():
    units = [
        {
            'title': "1. Hafta: Güneş'in Yapısı ve Dönme Hareketi (Soba-Lamba Analojisi)",
            'grade': '5. Sınıf',
            'subject': 'Fen Bilimleri',
            'learning_area': 'Dünya ve Evren',
            'topic': "Güneş'in Yapısı ve Dönme Hareketi",
            'learning_outcome': "F.M.5.1.1.1. Güneş'in yapısı ve dönme hareketi ile ilgili bilgileri toplayabilme.",
            'manevi_outcome': "Güneş'in yapısı ve hareketleri bakımından canlılığın devamına katkısındaki mükemmel yaratılışını fark edebilme."
        },
        {
            'title': "2. Hafta: Güneş'in Dönme Hareketi ve Rahmet Boyutu",
            'grade': '5. Sınıf',
            'subject': 'Fen Bilimleri',
            'learning_area': 'Dünya ve Evren',
            'topic': "Güneş'in Dönme Hareketinin Canlılığa Etkisi",
            'learning_outcome': "F.M.5.1.1.1. Güneş'in yapısı ve dönme hareketi ile ilgili bilgileri toplayabilme ve canlılığa katkısını değerlendirebilme.",
            'manevi_outcome': "Güneş'in hareketli bir varlık olarak yaratılmasının etrafındaki gezegenlere, özellikle dünyamıza, bir rahmet olduğunu kavrayabilme."
        },
        {
            'title': "3. Hafta: Ay'ın Özellikleri ve Hareketleri (Lisan-ı Hal)",
            'grade': '5. Sınıf',
            'subject': 'Fen Bilimleri',
            'learning_area': 'Dünya ve Evren',
            'topic': "Ay'ın Özellikleri, Dönme ve Dolanma Hareketleri",
            'learning_outcome': "F.M.5.1.2.1. Ay'ın özellikleri, dönme ve dolanma hareketleri ile ilgili bilimsel çıkarım yapabilme.",
            'manevi_outcome': "Ay'ın hareketlerindeki mükemmel düzeni fark ederek, bu düzenin sonsuz güç sahibi Allah tarafından sağlandığı hakkında çıkarım yapabilme."
        },
        {
            'title': "4. Hafta: Ay'ın Evreleri (Gökyüzündeki İlahi Takvim)",
            'grade': '5. Sınıf',
            'subject': 'Fen Bilimleri',
            'learning_area': 'Dünya ve Evren',
            'topic': "Ay'ın Evreleri ve Zaman Hesaplama",
            'learning_outcome': "F.M.5.1.2.2. Ay'ın evrelerini temsil eden bilimsel model oluşturabilme.",
            'manevi_outcome': "Ay'ın hareketlerindeki ince hesap ve düzenden yola çıkarak Cenab-ı Hakkın her şeye gücünün yettiğini anlayabilme."
        },
        {
            'title': "5. Hafta: Güneş, Dünya ve Ay'ın Muazzam Uyumu (Vahdet ve Sanat)",
            'grade': '5. Sınıf',
            'subject': 'Fen Bilimleri',
            'learning_area': 'Dünya ve Evren',
            'topic': "Güneş, Dünya ve Ay'ın Birbirlerine Göre Hareketleri",
            'learning_outcome': "F.M.5.1.3.1. Güneş, Dünya ve Ay'ın birbirlerine göre hareketlerini ve hacimsel büyüklüklerini temsil eden bilimsel model oluşturabilme.",
            'manevi_outcome': "Güneş, Dünya ve Ay arasındaki harika uyum ve hareketlerin Allah'ın varlığına işaret ettiği çıkarımında bulunabilme."
        }
    ]
    return jsonify({'units': units})

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json() or {}
        grade = data.get('grade', '').strip()
        subject = data.get('subject', '').strip()
        learning_area = data.get('learning_area', '').strip()
        topic = data.get('topic', '').strip()
        learning_outcome = data.get('learning_outcome', '').strip()
        content_type = data.get('content_type', 'worksheet').strip()

        if not all([grade, subject, learning_area, topic, learning_outcome]):
            return jsonify({
                'success': False,
                'error': 'Lütfen tüm zorunlu alanları (Sınıf, Ders, Öğrenme Alanı, Konu, Öğrenme Çıktısı) doldurunuz.'
            }), 400

        if content_type == 'worksheet':
            sys_inst, user_prompt = build_worksheet_prompt(data)
        else:
            sys_inst, user_prompt = build_test_prompt(data)

        client_key = request.headers.get('X-Gemini-Key') or data.get('api_key')
        content = call_gemini_api(sys_inst, user_prompt, client_key)
        
        return jsonify({
            'success': True,
            'content_type': content_type,
            'content': content
        })

    except ValueError as e:
        logger.error(f'Validation/Key error: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        logger.error(f'Generation error: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'İçerik oluşturulurken bir sorun oluştu. Lütfen bilgileri kontrol ederek tekrar deneyiniz.'
        }), 500

@app.route('/api/export-docx', methods=['POST'])
def export_docx():
    try:
        from docx import Document
        from docx.shared import Pt, Inches

        data = request.get_json() or {}
        text = data.get('content', '')
        title = data.get('title', 'Materyal')

        doc = Document()
        for section in doc.sections:
            section.top_margin = Inches(0.7)
            section.bottom_margin = Inches(0.7)
            section.left_margin = Inches(0.8)
            section.right_margin = Inches(0.8)

        lines = text.split('\n')
        for line in lines:
            line_str = line.strip()
            if not line_str:
                doc.add_paragraph()
                continue
            
            if line_str.startswith('# '):
                h = doc.add_heading(line_str[2:], level=1)
                h.paragraph_format.space_before = Pt(12)
                h.paragraph_format.space_after = Pt(6)
            elif line_str.startswith('## '):
                h = doc.add_heading(line_str[3:], level=2)
                h.paragraph_format.space_before = Pt(10)
                h.paragraph_format.space_after = Pt(4)
            elif line_str.startswith('### '):
                h = doc.add_heading(line_str[4:], level=3)
                h.paragraph_format.space_before = Pt(8)
                h.paragraph_format.space_after = Pt(2)
            elif line_str.startswith('#### '):
                h = doc.add_heading(line_str[5:], level=4)
                h.paragraph_format.space_before = Pt(6)
                h.paragraph_format.space_after = Pt(2)
            elif line_str.startswith('* ') or line_str.startswith('- '):
                p = doc.add_paragraph(line_str[2:], style='List Bullet')
                p.paragraph_format.space_after = Pt(2)
            elif line_str.startswith('> '):
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.4)
                run = p.add_run(line_str[2:])
                run.italic = True
            elif line_str.startswith('|') and line_str.endswith('|'):
                p = doc.add_paragraph(line_str)
                p.paragraph_format.space_after = Pt(2)
            else:
                p = doc.add_paragraph(line_str)
                p.paragraph_format.space_after = Pt(4)

        bio = BytesIO()
        doc.save(bio)
        bio.seek(0)
        
        filename = f"{title.replace(' ', '_')}.docx"
        return send_file(
            bio,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )

    except Exception as e:
        logger.error(f'DOCX export error: {str(e)}')
        return jsonify({'success': False, 'error': 'Word dosyası oluşturulamadı.'}), 500

if __name__ == '__main__':
    logger.info('MMR Yaprak Test & Çalışma Kağıdı Üretim Sunucusu Başlatılıyor: http://127.0.0.1:5000')
    app.run(host='127.0.0.1', port=5000, debug=False)
