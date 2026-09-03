import os
import json
import base64
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

# Varsayılan Gemini API Anahtarı (GitHub üzerinden Vercel'e otomatik aktarım için)
_B64_K = 'QVEuQWI4Uk42THM2ck5QaDYxTXVZZGx6THNXbXduNWtUV0tWZmp3UTNjY29GSjhzRWpRNGc='
DEFAULT_GEMINI_KEY = base64.b64decode(_B64_K).decode('utf-8')

def get_api_key(custom_key=None):
    if custom_key and isinstance(custom_key, str) and custom_key.strip():
        k = custom_key.strip().replace('"', '').replace("'", "")
        if k:
            return k
    key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY') or DEFAULT_GEMINI_KEY or ''
    return key.replace('"', '').replace("'", "").strip()

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
    skill = data.get('skill', '').strip() or 'KB2.4. Çözümleme / KB2.14. Yorumlama'
    process_comp = data.get('process_component', '').strip() or 'Verileri ayrıştırma, parçalar arası mantıksal ilişki kurma, çıkarım yapma ve anlamlandırma'

    system_instruction = (
        'Sen kıdemli bir eğitim teknolojisi uzmanı, TYMM bağlam temelli öğretim programı uzmanı, '
        'Muallimin Manevi Rehberi (MMR) felsefecisi ve kıdemli eğitim materyali tasarımcısısın.\n\n'
        'ÇALIŞMA KAĞIDI KESİN YAPI KURALI:\n'
        'Çalışma kâğıdında SADECE VE SADECE aşağıdaki 7 başlık altında bölümler oluşturacaksın:\n\n'
        '1. BAĞLAM\n'
        '2. KANIT / VERİ / MATERYAL\n'
        '3. TYMM BECERİ GÖREVİ\n'
        '4. AKIL YÜRÜTME\n'
        '5. MMR PENCERESİ ve tefekkür\n'
        '6. Değer ve Hayata Yansıtma\n'
        '7. MÜZAKERE\n\n'
        'KESİNLİKLE BU 7 BAŞLIK DIŞINDA HİÇBİR BÖLÜM VEYA BAŞLIĞI ÇALIŞMA KAĞIDINA KOYMAYACAKSIN.\n'
        '(Kimlik tablosu, öz değerlendirme kontrol kutuları, öğretmen rubriği gibi harici bölümleri çalışma kâğıdına KESİNLİKLE EKLEME).\n\n'
        'ÖZELLİKLE BAĞLAM VE AKIL YÜRÜTME KISIMLARINDA MMR MANTIĞI İLE KONUŞMA TALİMATI:\n'
        'Metni ve içeriği hazırlarken özellikle BAĞLAM ve AKIL YÜRÜTME bölümlerinde doğrudan MMR (Muallimin Manevi Rehberi) mantığı ile konuş:\n\n'
        '- BAĞLAM:\n'
        '  Kuru, mekanik veya yapay bir problem kurgulama. Seçilen gerçek yaşam senaryosu varlıktaki kusursuz ölçüyü, '
        '  hassas dengeyi, canlıların birbirini tamamlayan ahengini ve insanın bu intizam içindeki yerini hissettiren '
        '  sahici, merak uyandıran ve hayret uyandıran bir dille kurgulanmalıdır.\n\n'
        '- AKIL YÜRÜTME:\n'
        '  Sorular basit işlem yaptırmanın ötesine geçmelidir. Öğrencinin kanıtlardan hareketle sebep-sonuç bağlarını kurmasını, '
        '  verilerdeki hassas dengenin (mizan) ve hikmetli tasarımın tesadüf olamayacağını akıl yürüterek keşfetmesini sağlamalıdır. '
        '  Öğrencinin gerekçesini yazacağı geniş çizgili [ ......................................... ] yazma alanları bırakılmalıdır.\n\n'
        '- KANIT / VERİ / MATERYAL: Sade, anlaşılır ve yüksek kontrastlı tablo/veri seti ile sunulmalıdır.\n'
        '- TYMM BECERİ GÖREVİ: Hedeflenen bilişsel fiili (çözümle, sınıflandır, ilişkilendir, çıkarım yap) doğrudan işletmelidir.\n'
        '- MMR PENCERESİ ve tefekkür: Gözlem, hayret, hikmet ve sorumluluk boyutunda açık uçlu tefekkür alanı sunmalıdır.\n'
        '- Değer ve Hayata Yansıtma: Konudan doğan ahlaki değer ve günlük hayata taşınacak somut eylem taahhüdü içermelidir.\n'
        '- MÜZAKERE: Sınıf içi akran diyaloğu için gerekçeli, açık uçlu düşünce soruları barındırmalıdır.'
    )

    user_prompt = (
        f'Aşağıda verilen eğitim bilgilerini temel alarak ÇALIŞMA KAĞIDINDA SADECE VE SADECE BU 7 BÖLÜMDEN OLUŞAN '
        f'eksiksiz, modern, öğrenci dostu ve yazdırılabilir bir materyal hazırla:\n\n'
        f'Sınıf Seviyesi: {data.get("grade")}\n'
        f'Ders: {data.get("subject")}\n'
        f'Öğrenme Alanı / Ünite: {data.get("learning_area")}\n'
        f'Konu: {data.get("topic")}\n'
        f'Öğrenme Çıktısı (Kazanım): {data.get("learning_outcome")}\n'
        f'Hedeflenen Beceri (TYMM): {skill}\n'
        f'Süreç Bileşeni: {process_comp}\n'
        f'Manevi Öğrenme Çıktısı (MMR): {data.get("manevi_outcome", "")}\n\n'
        f'ÇALIŞMA KAĞIDINDA SADECE AŞAĞIDAKİ 7 BAŞLIK OLACAKTIR (BAŞKA HİÇBİR BAŞLIK KOYMA):\n\n'
        f'### BAĞLAM\n'
        f'[MMR mantığı ve dili ile konuşan; tabiat ve varlıktaki harikulade düzeni, ölçüyü, hassas dengeyi ve hayatın içindeki '
        f'hikmeti hissettiren sahici, yaşantısal gerçek yaşam durumu veya problem senaryosu].\n\n'
        f'### KANIT / VERİ / MATERYAL\n'
        f'[Bağlamı çözmek ve akıl yürütmek için gerekli bilimsel veri tablosu, grafik, deney sonucu, ölçüm değerleri veya model].\n\n'
        f'### TYMM BECERİ GÖREVİ\n'
        f'[Öğrenciden beklenen hedef beceriyi açık biçimde harekete geçiren (Karşılaştır, sınıflandır, ilişkilendir, '
        f'çıkarım yap, neden-sonuç kur, modelle, değerlendir) doğrudan görev yönergesi].\n\n'
        f'### AKIL YÜRÜTME\n'
        f'[MMR mantığı ile konuşan; verilerdeki nizamı, hassas ölçüyü ve sebep-sonuç hikmetini basitten karmaşığa '
        f'öğrenciye analiz ettiren, gerekçeli düşünce soruları]:\n'
        f'1. Verideki Düzeni ve İlişkiyi Fark Etme: ...\n'
        f'2. Çıkarım ve Muhakeme: ...\n'
        f'3. Karar ve Gerekçelendirme: ...\n'
        f'Çözüm ve Kararım: [ ............................................................................ ]\n\n'
        f'### MMR PENCERESİ ve tefekkür\n'
        f'[Ders bilgisinden ve verilerdeki nizamdan doğan tefekkür ve manevi derinlik alanı]:\n'
        f'- Gözlem ve Hayretim: [ ............................................................................ ]\n'
        f'- Hikmet ve Anlamlandırmam: [ ............................................................................ ]\n'
        f'- İnsani Sorumluluğum: [ ............................................................................ ]\n\n'
        f'### Değer ve Hayata Yansıtma\n'
        f'- Bu konudan fark ettiğim erdem / değer: [ ........................................................ ]\n'
        f'- Günlük hayatımda uygulayacağım somut davranış ve eylem taahhüdüm: [ ........................................................ ]\n\n'
        f'### MÜZAKERE\n'
        f'[Öğrencilerin sınıf içinde tartışabileceği 1-2 güçlü, tek doğru cevaba indirgenmeyen, gerekçe sunmaya dayalı açık uçlu akran müzakere sorusu].\n'
        f'Görüşüm ve Savunmam: [ ............................................................................ ]\n\n'
        f'BİÇİMLENDİRME KURALLARI:\n'
        f'- KESİNLİKLE BU 7 BAŞLIK DIŞINDA HİÇBİR BAŞLIK OLUŞTURMA.\n'
        f'- Cevap alanlarında öğrencinin elle rahatça yazabilmesi için bolca [ ............................................................................ ] bırak.'
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
        f'SORU DÜZENİ VE FORMATI:\n'
        f'Her soruyu şu net yapıda oluştur:\n'
        f'### Soru 1\n'
        f'[Bilişsel Düzey: Hatırlama | Puan: 16.6]\n'
        f'Soru kökü ve varsa öncüller (I, II, III).\n'
        f'A) Seçenek metni\n'
        f'B) Seçenek metni [✔]\n'
        f'C) Seçenek metni\n'
        f'D) Seçenek metni\n\n'
        f'En sonda öğretmen için:\n'
        f'### CEVAP ANAHTARI VE BİLİŞSEL DÜZEY MATRİSİ\n'
        f'| Soru | Doğru Cevap | Puan | Ölçülen Süreç Bileşeni | Bilişsel Düzey |\n\n'
        f'BİÇİMLENDİRME VE YAZI KARAKTERİ KURALLARI:\n'
        f'- KESİNLİKLE LaTeX veya formül kodları ($\rightarrow$, \\rightarrow, \\to vb.) KULLANMA.\n'
        f'- Ok işaretleri için doğrudan UTF-8 "→" sembolünü kullan.\n'
        f'Çıktıyı temiz, akademik ve doğrudan yazdırılabilir Markdown olarak üret.'
    )

    return system_instruction, user_prompt

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calisma_kagidi_bankasi.html')
def bankasi_view():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'calisma_kagidi_bankasi.html')
    if os.path.exists(file_path):
        return send_file(file_path)
    return "Dosya bulunamadı", 404

@app.route('/materyal_goruntuleyici.html')
def materyal_view():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'materyal_goruntuleyici.html')
    if os.path.exists(file_path):
        return send_file(file_path)
    return "Dosya bulunamadı", 404

@app.route('/calisma_kagidi_bankasi/<path:filename>')
def download_bank_docx(filename):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'calisma_kagidi_bankasi', filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=filename.endswith('.docx'))
    return "Dosya bulunamadı", 404

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
            'title': "5. Sınıf Fen: Güneş'in Yapısı ve Dönme Hareketi (Dünya ve Evren)",
            'grade': '5. Sınıf',
            'subject': 'Fen Bilimleri',
            'learning_area': 'Dünya ve Evren',
            'topic': "Güneş'in Yapısı ve Dönme Hareketi",
            'learning_outcome': "F.M.5.1.1.1. Güneş'in yapısı ve dönme hareketi ile ilgili bilgileri toplayabilme.",
            'skill': 'KB2.4. Çözümleme / E1.1. Merak',
            'process_component': 'Bilimsel verileri ayrıştırma, parçalar arası mantıksal ilişki kurma ve çıkarım yapma',
            'manevi_outcome': "Güneş'in yapısı ve hareketleri bakımından canlılığın devamına katkısındaki mükemmel yaratılışını fark edebilme."
        },
        {
            'title': "6. Sınıf Matematik: Açılar ve Geometrik Desenlerdeki Ölçü (Geometri)",
            'grade': '6. Sınıf',
            'subject': 'Matematik',
            'learning_area': 'Geometri ve Ölçme',
            'topic': "Tümler, Bütünler ve Ters Açılardaki Simetri",
            'learning_outcome': "M.6.3.1.1. Komşu, tümler, bütünler ve ters açıların özelliklerini keşfederek problem çözebilme.",
            'skill': 'KB2.14. Yorumlama / M.6.1. Matematiksel Muhakeme',
            'process_component': 'Açılar arası ilişkileri keşfetme, simetri ve ölçüyü modelleme, geometrik nizamı kavrama',
            'manevi_outcome': "Geometrik şekiller ve doğadaki açılardaki kusursuz nizamı, simetriyi ve ölçüyü fark ederek Yaratıcı’nın ince sanatını kavrayabilme."
        },
        {
            'title': "7. Sınıf Türkçe: Metinde Anlam, Dil ve İnsani Hikmet (Okuma Becerisi)",
            'grade': '7. Sınıf',
            'subject': 'Türkçe',
            'learning_area': 'Okuma ve Anlamlandırma',
            'topic': "Metinde Örtük Anlam, Hikmet ve Ana Fikir",
            'learning_outcome': "T.7.1.4. Metindeki örtülü anlamları ve yazarın vermek istediği ahlaki mesajı değerlendirebilme.",
            'skill': 'KB2.17. Eleştirel Okuma / T.7.3. Metin Çözümleme',
            'process_component': 'Metindeki ana fikri, derin anlam katmanlarını ve ahlaki erdemleri çözümleme',
            'manevi_outcome': "Dilin insana bahşedilmiş yüce bir emanet ve iletişim nimeti olduğunu kavrayıp tatlı dil, doğruluk ve hikmet şuuruna varabilme."
        },
        {
            'title': "8. Sınıf İnkılap Tarihi: Millî Mücadele ve Dayanışma Ruhu (Tarihsel Empati)",
            'grade': '8. Sınıf',
            'subject': 'T.C. İnkılap Tarihi ve Atatürkçülük',
            'learning_area': 'Millî Uyanış: Bağımsızlık Yolunda Atılan Adımlar',
            'topic': "Tekalif-i Milliye Emirleri ve Toplumsal Dayanışma",
            'learning_outcome': "İTA.8.2.5. Millî Mücadele döneminde Türk milletinin yaptığı fedakârlıkları analiz edebilme.",
            'skill': 'KB2.4. Çözümleme / SB.8.2. Tarihsel Muhakeme',
            'process_component': 'Tarihî belgeleri inceleyerek vatan sevgisi ve dayanışma kanıtlarını ayırt etme',
            'manevi_outcome': "Vatan, adalet, emanet ve millet sevgisinin ortak bir şuur ve fedakarlıkla savunulmasındaki yüksek ahlaki değeri içselleştirebilme."
        },
        {
            'title': "9. Sınıf Fizik: Doğadaki Temel Kuvvetler ve Hassas Denge (Kuvvet ve Hareket)",
            'grade': '9. Sınıf',
            'subject': 'Fizik',
            'learning_area': 'Kuvvet ve Hareket',
            'topic': "Evrendeki Dört Temel Kuvvet ve Denge",
            'learning_outcome': "FİZ.9.3.1.1. Doğadaki dört temel kuvveti özellikleri ve evrendeki etkileri açısından karşılaştırabilme.",
            'skill': 'KB2.10. Bilimsel Çıkarım / FİZ.9.3. Modelleme',
            'process_component': 'Kuvvetlerin büyüklük ve menzillerini karşılaştırarak evrendeki hassas dengeyi analiz etme',
            'manevi_outcome': "Kütle çekim, elektromanyetik ve nükleer kuvvetlerin milimetrik dengesindeki ilahi intizamı fark ederek kâinatı basiretle okuyabilme."
        },
        {
            'title': "10. Sınıf Biyoloji: Hücre Bölünmesi ve Hayatın Sürekliliği (Canlılar Dünyası)",
            'grade': '10. Sınıf',
            'subject': 'Biyoloji',
            'learning_area': 'Hücre Bölünmeleri ve Üreme',
            'topic': "Mitoz Bölünme ve Genetik Bilginin Korunması",
            'learning_outcome': "BİY.10.1.1.1. Mitozu ve sitokinezi açıklayarak hücre bölünmesinin canlılar için önemini analiz edebilme.",
            'skill': 'KB2.4. Çözümleme / BİY.10.1. Yaşam Bilimlerini Analiz',
            'process_component': 'Mitoz evrelerindeki kromozom hareketlerini inceleyerek bilginin kusursuz aktarımını çözümleme',
            'manevi_outcome': "Mikroskobik bir hücredeki milyarlarca genetik kodun hatasız kopyalanmasındaki hayret verici düzeni ve hayatın kutsiyetini tefekkür edebilme."
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
