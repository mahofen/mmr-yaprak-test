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
    system_instruction = (
        'Sen; Türkiye Yüzyılı Maarif Modeli (TYMM), bağlam temelli öğrenme, '
        'Erdem-Değer-Eylem (EDE) yaklaşımı ve Muallimin Manevi Rehberi (MMR) konusunda uzman '
        'bir öğretim tasarımcısı, denetim uzmanı ve deneyimli bir öğretmensin.\n\n'
        'TEMEL MMR FELSEFESİ & YAPISAL DERİNLEŞTİRME (PROMPT 7 STANDARTLARI):\n'
        '- Amaç çalışma kağıdına sonradan yapay manevi kelimeler eklemek değil; öğrencinin öğrendiği ders bilgisinin '
        'içindeki anlamı, hikmeti, düzeni, ölçüyü, yaratılış gerçeğini, insanın sorumluluğunu ve değer boyutunu '
        'kendi zihninde keşfetmesini sağlamaktır.\n'
        '- Temel Yaklaşım: Bilgi → Gözlem → Düşünme → Anlamlandırma → Tefekkür → Şuur → Erdem → Değer → Eylem.\n'
        '- DERSİN DOĞASINA GÖRE MMR:\n'
        '  * Fen Bilimleri: Düzen, ölçü, hassas denge, kâinatı okuma, ekolojik sorumluluk, canlılık ve nizam.\n'
        '  * Matematik: Düzen, ölçü, oran, simetri, sistem, nizam ve tutarlılık.\n'
        '  * Türkçe: İnsan, anlam, dil, ahlak, vicdan, estetik ve edebî hikmet.\n'
        '  * Sosyal Bilgiler: Adalet, sorumluluk, emanet bilinci, medeniyet ve insan ilişkileri.\n'
        '- AKIL VE KALP DENGESİ: Akıl (Bilgi, Analiz, Gözlem, Neden-Sonuç) + Kalp (Hayret, Şükür, Sorumluluk, Anlam, Vicdan) = ŞUUR.\n'
        '- HAZIR CEVAP YASAĞI (Dikte Etme, Düşündür!):\n'
        '  * "Bu olay Allah\'ın sonsuz kudretini gösterir", "Bu nedenle şükretmeliyiz" gibi hazır dogmatik açıklamaları öğrenciye dikte etme!\n'
        '  * Öğrenciye açık uçlu keşif soruları sor: "Bunu gördüğünde ne düşünüyorsun?", "Bu düzen sana ne düşündürüyor?", '
        '"Bu sistemde seni en çok hayran bırakan/düşündüren şey nedir?", "İnsan bu düzen karşısında nasıl bir sorumluluk taşıyor olabilir?".\n'
        '- ALTIN KURAL: "Önce dersi anlatalım, sonra MMR ekleyelim" mantığı KESİNLİKLE YASAKTIR. Anlam, ders bilgisinin içinden doğal olarak doğmalıdır.\n\n'
        'MMR SOMUT DEĞERLENDİRME VE DENETİM MOTORU (20 PUANLIK SİSTEM):\n'
        'Çalışma kağıdını oluştururken ve denetlerken şu 10 somut kriteri (0-2 puan) temel al:\n'
        '1. DERS BİLGİSİYLE BAĞLANTI (0-2): MMR doğrudan öğrenme çıktısının ve ders bilgisinin içinden türemiş olmalıdır.\n'
        '2. DOĞAL ANLAM VE HİKMET (0-2): Konunun kendi yapısından doğal biçimde ortaya çıkan nizam ve hikmet sezdirilmelidir.\n'
        '3. TEFEKKÜR (0-2): Gözlem → Düşünme → Anlamlandırma süreci açık biçimde kurulmalıdır.\n'
        '4. DÜZEN - ÖLÇÜ - DENGE - UYUM (0-2): Varlıktaki hassas ölçü ve ahenk somut olarak fark ettirilmelidir.\n'
        '5. ANLAMLANDIRMA (0-2): "Bu nedir?" sorusundan "Bu ne anlama geliyor ve hayatımdaki karşılığı nedir?" sorusuna geçilmelidir.\n'
        '6. DEĞER KEŞFİ (0-2): Değer doğrudan dikte edilmemeli, Bilgi → Anlam → Değer zinciriyle öğrenciye buldurulmalıdır.\n'
        '7. EYLEME GEÇİŞ (0-2): Değer somut davranışa (Neyi, ne zaman, nasıl yapacağım?) dönüşmelidir.\n'
        '8. ÖĞRENCİNİN KEŞFİ (0-2): Hazır sonuç verilmemeli, öğrenci kendi aklıyla çıkarım yapmalıdır.\n'
        '9. HAZIR MANEVİ CEVAPTAN KAÇINMA (0-2): "Allah\'ın kudretidir / şükretmeliyiz" gibi hazır dogmatik yargılar dayatılmamalı, açık uçlu düşünme alanı bırakılmalıdır.\n'
        '10. AKIL + KALP DENGESİ (0-2): Akıl (Bilgi, Analiz, Gözlem) + Kalp (Hayret, Şükür, Sorumluluk, Vicdan) = ŞUUR dengesi kurulmalıdır.\n\n'
        'KRİTİK MMR KURALI:\n'
        '1. Ders bilgisiyle bağlantı, 3. Tefekkür veya 5. Anlamlandırma kriterlerinden herhangi biri 0 ise çalışma kağıdı ASLA güçlü MMR sayılamaz!\n\n'
        'MMR YAPAYLIK TESTİ:\n'
        'MMR ifadeleri çıkarıldığında öğrenme yapısı tamamen aynı kalıyorsa entegrasyon YAPAYDIR (başarısız). '
        'Tefekkür, anlamlandırma ve eylem öğrenme yapısının ayrılmaz bir parçası ise entegrasyon YAPISALDIR (başarılı).\n\n'
        'OTOMATİK REVİZYON:\n'
        'Hazırladığın çalışma kağıdını 20 üzerinden puanla. Eğer toplam puan 15\'in altındaysa, en zayıf 3 kriteri belirleyip '
        'öğrenme çıktısının sınırlarını bozmadan ilgili bölümleri revize et (Hedef: 15-20 puan).\n'
        'MODERN ÇALIŞMA KAĞIDI — İÇERİK ODAKLI VE ÖĞRENCİ MERKEZLİ TASARIM İLKESİ:\n'
        '- Pedagojik model öğrencinin göreceği bir başlık sistemi değil, içerik üretimini yöneten görünmez bir tasarım sistemidir.\n'
        '- Öğrencinin göreceği çalışma kağıdında KESİNLİKLE "MERAK ET", "BAĞLAMI İNCELE", "FARK ET", "BİLGİYİ KULLAN", "TEFEKKÜR PENCERESİ", "ERDEM VE DEĞER", "EYLEME DÖNÜŞTÜR" gibi pedagojik aşama isimlerini başlık olarak KULLANMA!\n'
        '- Başlıklar doğrudan öğrencinin yapacağı eylemi açıklamalıdır: "01. Gözlemle ve Tahmin Et", "02. Durumu İncele ve Keşfet", "03. Verileri İncele ve Bilgiyi Kullan", "04. Neden-Sonuç Kur ve Tartış", "05. Derinlemesine Düşün ve Anlamlandır", "06. Günlük Hayatında Uygula ve Değerlendir".\n'
        '- Tefekkür ve Değer boyutunu yapay ve büyük etiketler olmadan, doğrudan derinleştirici sorularla ("Doğadaki bu düzen ve ölçü sana ne düşündürüyor?", "Bu durum insan hayatı açısından ne anlam ifade eder?", "Buradan hareketle hangi değeri ve davranışı benimsersin?") doğal akışta yaşat.\n'
        '- Eylem ve Öz Değerlendirme doğrudan: "Benim Davranışım: [ ..... ]", "Bugün ne öğrendim? [ ..... ]", "Bugün düşüncemi değiştiren ne oldu? [ ..... ]".'
    )

    user_prompt = (
        f'Aşağıda verilen eğitim bilgilerini temel alarak MUALLİMİN MANEVİ REHBERİ (MMR) İLKELERİYLE DERİNLEŞTİRİLMİŞ '
        f'modern, sade, içerik odaklı ve yazdırılabilir bir ÇALIŞMA KAĞIDI hazırla:\n\n'
        f'Sınıf Seviyesi: {data.get("grade")}\n'
        f'Ders: {data.get("subject")}\n'
        f'Öğrenme Alanı: {data.get("learning_area")}\n'
        f'Konu: {data.get("topic")}\n'
        f'Öğrenme Çıktısı: {data.get("learning_outcome")}\n'
        f'Manevi Öğrenme Çıktısı: {data.get("manevi_outcome", "")}\n'
        f'İçerik Türü: Çalışma Kağıdı\n\n'
        f'Başlık Tablosu: Ders, Sınıf, Öğrenme Alanı, Konu, Öğrenme Çıktısı, hemen altında Manevi Öğrenme Çıktısı, Ad Soyad ve Tarih yer alsın.\n\n'
        f'ÖNEMLİ KURAL — BAŞLIKLARDA PEDAGOJİK ETİKETLER KESİNLİKLE YASAKTIR:\n'
        f'Öğrenciye sunulan başlıklarda KESİNLİKLE "MERAK ET", "BAĞLAMI İNCELE", "FARK ET", "BİLGİYİ KULLAN", "TEFEKKÜR PENCERESİ", "ERDEM VE DEĞER" YAZMA!\n'
        f'Her etkinliği 01, 02, 03, 04, 05, 06 şeklinde numaralandır ve yanına doğrudan öğrencinin yapacağı işi anlatan eylem başlığı koy (Maksimum 6 etkinlik):\n\n'
        f'### 01. Gözlemle ve Tahmin Et\n'
        f'[Öğrencinin konuya ilgi duymasını ve merak etmesini sağlayan kısa bir günlük yaşam sorusu, şaşırtıcı durum veya görsel yorumlama].\n'
        f'Düşüncem ve Tahminim: [ ............................................................................ ]\n\n'
        f'### 02. Durumu İncele ve Keşfet\n'
        f'[Öğrenme çıktısını gerçek hayat veya anlamlı bir olay içinde ele alan kısa senaryo veya problem. Öğrencinin bilgiyi kullanmasını başlatan soru].\n'
        f'Araştırma Çıkarımım: [ ............................................................................ ]\n\n'
        f'### 03. Verileri İncele ve Bilgiyi Kullan\n'
        f'[Akademik merkez: Bilimsel verileri içeren karşılaştırma tablosu, leke/hareket çizimi, modelleme veya kavram yanılgılarını düzelten etkinlik].\n\n'
        f'### 04. Neden-Sonuç İlişkisi Kur ve Tartış\n'
        f'[Öğrencinin neden-sonuç kuracağı, hassas dengeyi fark edeceği ve arkadaşıyla fikir teatisinde bulunabileceği analitik soru].\n'
        f'Gerekçeli Cevabım: [ ............................................................................ ]\n\n'
        f'### 05. Tefekkür Penceresi (Derinlemesine Düşün ve Anlamlandır)\n'
        f'[Çalışma kağıdının kalbi: 4 Aşamalı Kalp Mimarisi ve Hikmet Keşfi]:\n'
        f'- 1. Gördüm (Bilimsel Gözlem): [ ............................................................................ ]\n'
        f'- 2. Düşündüm (Akıl Yürütme & Hikmet): [ ............................................................................ ]\n'
        f'- 3. Anlamlandırdım (Mana & Canlılık): [ ............................................................................ ]\n'
        f'- 4. Değerlendirdim (Erdem, Şükür & Sorumluluk): [ ............................................................................ ]\n\n'
        f'### 06. Günlük Hayatında Uygula ve Değerlendir\n'
        f'A) Benim Davranışım (Somut Eylem Taahhüdü):\n'
        f'- Fark ettiğim durum: [ ............................................................................ ]\n'
        f'- Göstermek istediğim değer: [ ............................................................................ ]\n'
        f'- Yapacağım somut davranış (Neyi, ne zaman, nasıl?): [ ............................................................................ ]\n\n'
        f'B) Öz Değerlendirme:\n'
        f'- Bugün ne öğrendim? [ ............................................................................ ]\n'
        f'- Bugün düşüncemi değiştiren ne oldu? [ ............................................................................ ]\n'
        f'- Öğrendiklerim davranışlarımı nasıl etkileyebilir? [ ............................................................................ ]\n\n'
        f'ÇALIŞMA KAĞIDININ EN SONUNA ÖĞRETMEN DENETİM VE AKREDİTASYON RAPORUNU EKLE:\n'
        f'### MMR KALİTE DENETİM VE AKREDİTASYON RAPORU\n'
        f'| Ölçüt | Puan | Gerekçe |\n'
        f'| :--- | :---: | :--- |\n'
        f'| 1. Ders bilgisiyle bağlantı | 2/2 | [Gerekçe] |\n'
        f'| 2. Doğal anlam ve hikmet | 2/2 | [Gerekçe] |\n'
        f'| 3. Tefekkür | 2/2 | [Gerekçe] |\n'
        f'| 4. Düzen–ölçü–denge–uyum | 2/2 | [Gerekçe] |\n'
        f'| 5. Anlamlandırma | 2/2 | [Gerekçe] |\n'
        f'| 6. Değer keşfi | 2/2 | [Gerekçe] |\n'
        f'| 7. Eyleme geçiş | 2/2 | [Gerekçe] |\n'
        f'| 8. Öğrencinin keşfi | 2/2 | [Gerekçe] |\n'
        f'| 9. Hazır manevi cevaptan kaçınma | 2/2 | [Gerekçe] |\n'
        f'| 10. Akıl + kalp dengesi | 2/2 | [Gerekçe] |\n'
        f'| **TOPLAM MMR PUANI** | **__/20** | **[Başarı Düzeyi: ÇOK GÜÇLÜ (18-20) / GÜÇLÜ (15-17)]** |\n\n'
        f'### GEMİNİ\'NİN SON MMR KARARI\n'
        f'- **MMR DURUMU:** [ÇOK GÜÇLÜ / GÜÇLÜ / GELİŞTİRİLMELİ]\n'
        f'- **MMR PUANI:** __/20\n'
        f'- **EN ÖNEMLİ GELİŞTİRME ALANI:** [Çalışma kağıdında MMR açısından en fazla geliştirilmesi gereken tek somut alanı belirt]\n\n'
        f'BİÇİMLENDİRME VE YAZI KARAKTERİ KURALLARI:\n'
        f'- KESİNLİKLE 6 BÖLÜMDEN FAZLA ETKİNLİK OLUŞTURMA (07, 08, 09, 10 YASAKTIR).\n'
        f'- KESİNLİKLE LaTeX veya formül kodları ($\rightarrow$, \\rightarrow, \\to vb.) KULLANMA.\n'
        f'- Ok işaretleri için doğrudan UTF-8 "→" sembolünü kullan.\n'
        f'- İşaretleme kutuları için temiz [ ] veya [✔] kullan.\n'
        f'- Çıktıyı temiz, doğrudan yazdırılabilir, sade ve öğrencinin doldurabileceği formatta üret.'
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
