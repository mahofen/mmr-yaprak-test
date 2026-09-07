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
    skill = data.get('skill', '').strip() or 'KB2.4. Çözümleme / KB2.14. Yorumlama [Tahmin Edilen]'
    process_comp = data.get('process_component', '').strip() or 'Verileri ayrıştırma, parçalar arası mantıksal ilişki kurma, çıkarım yapma ve anlamlandırma'
    duration = data.get('duration', '40 Dakika')
    count = data.get('question_count', 1)

    system_instruction = (
        'Sen; PISA/TIMSS ve TYMM (Türkiye Yüzyılı Maarif Modeli) standartlarında uzman bir eğitim teknolojileri ve ölçme-değerlendirme yapay zekâsısın.\n'
        'Aynı zamanda Muallimin Manevi Rehberi (MMR) yaklaşımıyla bilimi hikmet, tefekkür, nizam ve ahlaki sorumlulukla buluşturan bir pedagoji mimarısın.\n\n'
        'TEMEL GÖREVİN:\n'
        'Verilen öğrenme çıktısına dayalı, öğrencinin bilgiyi düşünmeye, anlamlandırmaya, değere ve eyleme dönüştürmesini sağlayan '
        'standart bir TYMM + MMR ÇALIŞMA KÂĞIDI üretmektir.\n\n'
        '5 MOTORLU MİMARİ:\n'
        '1. PEDAGOJİ MOTORU: Öğrenme çıktısı + beceri + süreç bileşeni.\n'
        '2. BAĞLAM MOTORU: Gerçek hayat → Problem → Bilimsel veri seti / grafik / tablo.\n'
        '3. AKIL YÜRÜTME MOTORU: Yorumlama → İlişkilendirme → Çıkarım → Gerekçelendirme → Değerlendirme.\n'
        '4. MMR MANA MOTORU: Bilgi → Hayret → Hikmet/Kudret → Tefekkür → Değer → Sorumluluk.\n'
        '5. TASARIM MOTORU: A4 düzeni, geniş çizgili cevap alanları [ ......................................... ].\n\n'
        'ÇALIŞMA KÂĞIDI ZORUNLU 7 BÖLÜMÜ:\n'
        '1. BAĞLAM (Gerçek yaşam, bilimsel durum veya çevre problemi)\n'
        '2. KANIT / VERİ / MATERYAL (Bilimsel veri tablosu, grafik veya ölçüm seti)\n'
        '3. TYMM BECERİ GÖREVİ (Hedeflenen bilişsel beceriyi işleten görev yönergesi)\n'
        '4. AKIL YÜRÜTME (Verideki nizamı ve ilişkileri basitten karmaşığa sorgulayan analitik sorular)\n'
        '5. MMR PENCERESİ ve tefekkür (Gözlem, hayret, nizam ve yaratılış hikmeti)\n'
        '6. Değer ve Hayata Yansıtma (Erdem keşfi, insani sorumluluk ve eylem taahhüdü)\n'
        '7. MÜZAKERE (Sınıf içi akran diyaloğu ve gerekçeli savunma sorusu)\n\n'
        'DOKÜMANIN SONUNDA MUTLAKA:\n'
        '1) ÖĞRETMEN ANALİTİK DEĞERLENDİRME RUBRİĞİ (4 Ölçüt: Veri Analizi, Akıl Yürütme, Hikmet/Tefekkür, Değer/Eylem)\n'
        '2) TYMM & PISA/TIMSS 10 BOYUTLU KALİTE KONTROL RAPORU (A-J Denetimi).'
    )

    user_prompt = (
        f'## ÖLÇME ARACI KÜNYESİ\n'
        f'- **Ölçme Aracı:** TYMM Beceri Temelli Çalışma Kâğıdı\n'
        f'- **Sınıf Seviyesi:** {data.get("grade")}\n'
        f'- **Ders:** {data.get("subject")}\n'
        f'- **Öğrenme Alanı / Ünite:** {data.get("learning_area")}\n'
        f'- **Öğrenme Çıktısı:** {data.get("learning_outcome")}\n'
        f'- **Bilişsel Düzey:** {data.get("cognitive_level", "Uygulama - Analiz")}\n'
        f'- **Hedeflenen Beceri (TYMM):** {skill}\n'
        f'- **Süreç Bileşeni:** {process_comp}\n'
        f'- **Tahmini Uygulama Süresi:** {duration}\n'
        f'- **Puanlama Modeli:** Analitik Rubrik (20 Puan)\n\n'
        f'Aşağıdaki 7 kanonik bölümü, öğretmen rubriğini ve 10 maddeli kalite kontrol raporunu eksiksiz oluştur:\n\n'
        f'### BAĞLAM\n'
        f'[Otantik gerçek yaşam senaryosu, kâinattaki düzen, ölçü ve dengeyi hissettiren durum metni].\n\n'
        f'### KANIT / VERİ / MATERYAL\n'
        f'[Bağlama ait somut veri tablosu, sayısal değerler veya deney verileri].\n\n'
        f'### TYMM BECERİ GÖREVİ\n'
        f'[Öğrencinin yapacağı temel çözümleme ve modelleme görevi].\n\n'
        f'### AKIL YÜRÜTME\n'
        f'1. Verideki Düzeni ve İlişkiyi Fark Etme: ...\n'
        f'2. Çıkarım ve Muhakeme: ...\n'
        f'3. Karar ve Gerekçelendirme: ...\n'
        f'Çözüm ve Kararım: [ ............................................................................ ]\n\n'
        f'### MMR PENCERESİ ve tefekkür\n'
        f'- Gözlem ve Hayretim: [ ............................................................................ ]\n'
        f'- Hikmet ve Anlamlandırmam: [ ............................................................................ ]\n'
        f'- İnsani Sorumluluğum: [ ............................................................................ ]\n\n'
        f'### Değer ve Hayata Yansıtma\n'
        f'- Fark Ettiğim Değer / Erdem: [ ........................................................ ]\n'
        f'- Günlük Hayattaki Eylem Taahhüdüm: [ ........................................................ ]\n\n'
        f'### MÜZAKERE\n'
        f'Görüşüm ve Savunmam: [ ............................................................................ ]\n\n'
        f'### ÖĞRETMEN DEĞERLENDİRME VE DERECELİ PUANLAMA RUBRİĞİ\n'
        f'| Ölçüt | Başlangıç (1 Puan) | Gelişmekte (2 Puan) | Yetkin / Usta (3-4 Puan) |\n'
        f'| Veri ve Bağlam Analizi | Verileri yorumlayamaz. | Verileri kısmen anlar. | Verileri eksiksiz analiz edip çıkarım yapar. |\n'
        f'| TYMM Akıl Yürütme | Neden-sonuç kuramaz. | Basit ilişkileri kurar. | Çok boyutlu mantıksal gerekçelendirme yapar. |\n'
        f'| MMR Tefekkür & Nizam | Düzen ve nizamı göremez. | Ölçü ve hikmeti fark eder. | Hayret, nizam ve tefekkür şuurunu içselleştirir. |\n'
        f'| Değer ve Eyleme Yansıtma | Sorumluluk üstlenmez. | Değeri fark eder. | Somut ahlaki tutum ve eylem kararı alır. |\n\n'
        f'### 🔍 TYMM & PISA/TIMSS KALİTE KONTROL RAPORU (10 BOYUTLU DENETİM)\n'
        f'- [✓] A. Öğrenme Çıktısı Kontrolü: Görev doğrudan hedeflenen öğrenme çıktısını ve kanıtını ölçmektedir.\n'
        f'- [✓] B. Bilişsel Düzey Kontrolü: Çözümleme, akıl yürütme ve değerlendirme basamaklarıyla tam uyumludur.\n'
        f'- [✓] C. Bilimsel Doğruluk: Veriler, olgular ve kavramsal açıklamalar bilimsel gerçekliğe uygundur.\n'
        f'- [✓] D. Dil ve Anlaşılırlık: Türkçe açık, yaş düzeyine uygun ve yönergeler nettir.\n'
        f'- [✓] E. Belirsizlik Kontrolü: Soru ve görev alanlarında anlam kargaşası yoktur.\n'
        f'- [✓] F. Çeldirici / Derinlik Kontrolü: Sorular ezber değil derinlemesine akıl yürütme gerektirir.\n'
        f'- [✓] G. İpucu Kontrolü: Bölümler birbirinin cevabını ele vermez.\n'
        f'- [✓] H. Gereksiz Bilgi / Bilişsel Yük: Bağlam süs değil, verisiz çözülemez niteliktedir.\n'
        f'- [✓] I. Beceriyi Görünür Kılma: Öğrencinin düşünme süreci ve değer çıkarımı şeffaftır.\n'
        f'- [✓] J. Puanlama & Rubrik Güvenilirliği: 4 ölçütlü analitik rubrik objektif ve uygulanabilirdir.'
    )

    return system_instruction, user_prompt

def build_test_prompt(data: dict) -> tuple[str, str]:
    count = data.get('question_count', 6)
    difficulty = data.get('difficulty', 'Orta')
    duration = data.get('duration', f'{int(count)*2} Dakika')
    skill = data.get('skill', '').strip() or 'KB1. Temel Beceriler [Tahmin Edildi]'

    system_instruction = (
        'Sen; TYMM ölçme-değerlendirme ilkeleri ve soru yazım standartlarında uzman bir test geliştiricisisin.\n'
        'Görevin, doğrudan verilen öğrenme çıktısını ölçen, geçerli ve güvenilir bir YAPRAK TEST hazırlamaktır.\n\n'
        'KURALLAR:\n'
        '- Yalnızca verilen öğrenme çıktısını ölç. Yeni kazanım ekleme.\n'
        '- Her soru 4 seçenekli (A, B, C, D) olmalı ve tek doğru cevabı bulunmalıdır.\n'
        '- Çeldiriciler öğrencilerin yaygın kavram yanılgılarına dayalı olmalı; Hepsi/Hiçbiri kullanılmamalıdır.\n'
        '- Soruları kolaydan zora sırala ve bilişsel basamakları (Hatırlama, Anlama, Basit Uygulama) belirt.\n'
        '- Testin sonunda CEVAP ANAHTARI VE BİLİŞSEL DÜZEY MATRİSİ ile 10 MADDELİ KALİTE KONTROL RAPORU ekle.'
    )

    user_prompt = (
        f'## ÖLÇME ARACI KÜNYESİ\n'
        f'- **Ölçme Aracı:** Yaprak Test (Çoktan Seçmeli)\n'
        f'- **Sınıf Seviyesi:** {data.get("grade")}\n'
        f'- **Ders:** {data.get("subject")}\n'
        f'- **Öğrenme Alanı / Ünite:** {data.get("learning_area")}\n'
        f'- **Öğrenme Çıktısı:** {data.get("learning_outcome")}\n'
        f'- **Bilişsel Düzey:** Hatırlama → Anlama → Uygulama\n'
        f'- **Hedeflenen Beceri (TYMM):** {skill}\n'
        f'- **Süreç Bileşeni:** {data.get("process_component", "Tanıma, hatırlama ve ilişkilendirme")}\n'
        f'- **Soru Sayısı:** {count}\n'
        f'- **Zorluk Seviyesi:** {difficulty}\n'
        f'- **Tahmini Süre:** {duration}\n'
        f'- **Puanlama Modeli:** Çoktan Seçmeli Cevap Anahtarı (100 Puan)\n\n'
        f'Her soruyu şu formatta eksiksiz oluştur:\n\n'
        f'### Soru 1\n'
        f'**[Bilişsel Düzey: Hatırlama | Ölçülen Beceri: Bilgi Teyidi | Puan: {round(100/int(count),1)}]**\n'
        f'Soru metni ve öncüller...\n'
        f'A) Seçenek metni\n'
        f'B) Seçenek metni [✔]\n'
        f'C) Seçenek metni\n'
        f'D) Seçenek metni\n\n'
        f'(Tüm {count} soruyu yazdıktan sonra):\n\n'
        f'### CEVAP ANAHTARI VE BİLİŞSEL DÜZEY MATRİSİ\n'
        f'| Soru No | Doğru Cevap | Bilişsel Düzey | Ölçülen Süreç Bileşeni | Çeldirici Analizi |\n'
        f'| :---: | :---: | :---: | :--- | :--- |\n\n'
        f'### 🔍 TYMM & PISA/TIMSS KALİTE KONTROL RAPORU (10 BOYUTLU DENETİM)\n'
        f'- [✓] A. Öğrenme Çıktısı Kontrolü: Sorular doğrudan çıktıyı ölçmektedir.\n'
        f'- [✓] B. Bilişsel Düzey Kontrolü: Belirtilen basamaklar dengelidir.\n'
        f'- [✓] C. Bilimsel Doğruluk: Bilimsel bilgiler ve kavramlar %100 doğrudur.\n'
        f'- [✓] D. Dil ve Anlaşılırlık: Soru kökleri açık ve tek anlamlıdır.\n'
        f'- [✓] E. Belirsizlik Kontrolü: Tek ve kesin bir doğru cevap vardır.\n'
        f'- [✓] F. Çeldirici Kontrolü: Çeldiriciler kavram yanılgılarına dayanır.\n'
        f'- [✓] G. İpucu Kontrolü: Sorular birbirinin cevabını ele vermez.\n'
        f'- [✓] H. Gereksiz Bilgi Kontrolü: Gereksiz bilişsel yük içermez.\n'
        f'- [✓] I. Beceriyi Görünür Kılma: Kazanım düzeyini net gösterir.\n'
        f'- [✓] J. Puanlama Kontrolü: Cevap anahtarı ve puan dağılımı açıktır.'
    )

    return system_instruction, user_prompt

def build_context_test_prompt(data: dict) -> tuple[str, str]:
    count = data.get('question_count', 4)
    difficulty = data.get('difficulty', 'Orta-İleri (PISA Düzeyi)')
    duration = data.get('duration', f'{int(count)*3} Dakika')
    skill = data.get('skill', '').strip() or 'KB2.4. Çözümleme / KB2.14. Yorumlama [Tahmin Edildi]'
    process_comp = data.get('process_component', '').strip() or 'Verileri yorumlama, akıl yürütme, çıkarım yapma'

    system_instruction = (
        'Sen; PISA, TIMSS ve TYMM bağlam temelli soru yazımında uzmanlaşmış kıdemli bir ölçme-değerlendirme uzmanısın.\n'
        'TEMEL GÖREVİN:\n'
        'Öğrencinin bilgiyi otantik bir bağlamda kullanmasını, verileri yorumlamasını, çıkarım yapmasını ve eleştirel karar vermesini '
        'ölçen yüksek standartta bir BAĞLAM TEMELLİ ÇOKTAN SEÇMELİ TEST hazırlamaktır.\n\n'
        'KURALLAR:\n'
        '- Önce anlamlı, yaşantısal ve bilimsel bir BAĞLAM (Gerçek yaşam senaryosu, veri tablosu, grafik veya deney sonucu) oluştur.\n'
        '- Bağlam süsleme olmamalı; sorular doğrudan bağlamdaki veriler analiz edilmeden çözülememelidir.\n'
        '- Sorular sadece metinden bilgi buldurmamalı; neden-sonuç kurma, çıkarım yapma, nizam ve dengeyi fark etme gerektirmelidir.\n'
        '- Her soru için: Soru kökü, 4 seçenek (A, B, C, D), doğru cevap, gerekçe, bilişsel düzey ve ölçülen beceri oluştur.\n'
        '- En sonda CEVAP ANAHTARI VE GEREKÇELİ ÇÖZÜMLER ile 10 MADDELİ KALİTE KONTROL RAPORU ekle.'
    )

    user_prompt = (
        f'## ÖLÇME ARACI KÜNYESİ\n'
        f'- **Ölçme Aracı:** Bağlam Temelli Çoktan Seçmeli Test (PISA/TIMSS Standardı)\n'
        f'- **Sınıf Seviyesi:** {data.get("grade")}\n'
        f'- **Ders:** {data.get("subject")}\n'
        f'- **Öğrenme Alanı / Ünite:** {data.get("learning_area")}\n'
        f'- **Öğrenme Çıktısı:** {data.get("learning_outcome")}\n'
        f'- **Bilişsel Düzey:** Uygulama → Analiz → Değerlendirme\n'
        f'- **Hedeflenen Beceri (TYMM):** {skill}\n'
        f'- **Süreç Bileşeni:** {process_comp}\n'
        f'- **Soru Sayısı:** {count}\n'
        f'- **Zorluk Seviyesi:** {difficulty}\n'
        f'- **Tahmini Süre:** {duration}\n'
        f'- **Puanlama Modeli:** Gerekçeli Cevap Anahtarı (100 Puan)\n\n'
        f'### OTANTİK BAĞLAM VE BİLİMSEL VERİ SETİ\n'
        f'[Gerçek yaşam durumu, araştırma deneyi, veri tablosu veya çevre/teknoloji olayı]:\n\n'
        f'(Bu bağlama dayalı {count} adet derinlemesine soru oluştur):\n\n'
        f'### Soru 1\n'
        f'**[Bilişsel Düzey: Analiz | Beceri: Veri Çözümleme | Puan: {round(100/int(count),1)}]**\n'
        f'Soru kökü...\n'
        f'A) Seçenek\n'
        f'B) Seçenek [✔]\n'
        f'C) Seçenek\n'
        f'D) Seçenek\n'
        f'- **Doğru Cevap Gerekçesi:** ...\n'
        f'- **Çeldirici Mantığı:** ...\n\n'
        f'### CEVAP ANAHTARI VE BİLİŞSEL DÜZEY MATRİSİ\n'
        f'| Soru No | Doğru Cevap | Bilişsel Düzey | Ölçülen Süreç Bileşeni | Gerekçe |\n\n'
        f'### 🔍 TYMM & PISA/TIMSS KALİTE KONTROL RAPORU (10 BOYUTLU DENETİM)\n'
        f'- [✓] A. Öğrenme Çıktısı Kontrolü: Sorular doğrudan öğrenme kanıtını ölçmektedir.\n'
        f'- [✓] B. Bilişsel Düzey Kontrolü: Uygulama ve analiz basamaklarında işletilmiştir.\n'
        f'- [✓] C. Bilimsel Doğruluk: Bağlam ve veriler bilimsel olarak eksiksizdir.\n'
        f'- [✓] D. Dil ve Anlaşılırlık: Metin akıcı, soru ifadeleri nettir.\n'
        f'- [✓] E. Belirsizlik Kontrolü: Çelişki yoktur, tek doğru cevap vardır.\n'
        f'- [✓] F. Çeldirici Kontrolü: Çeldiriciler kavram yanılgılarını yakalar.\n'
        f'- [✓] G. İpucu Kontrolü: Sorular bağımsızdır, birbirine ipucu vermez.\n'
        f'- [✓] H. Gereksiz Bilgi Kontrolü: Bağlam süs değil, fonksiyoneldir.\n'
        f'- [✓] I. Beceriyi Görünür Kılma: Öğrencinin akıl yürütme sürecini ortaya koyar.\n'
        f'- [✓] J. Puanlama Kontrolü: Puanlama ve gerekçeler açıkça yazılmıştır.'
    )

    return system_instruction, user_prompt

def build_open_ended_prompt(data: dict) -> tuple[str, str]:
    count = data.get('question_count', 3)
    duration = data.get('duration', f'{int(count)*8} Dakika')
    skill = data.get('skill', '').strip() or 'KB2.14. Yorumlama / KB2.16. Karar Verme / Gerekçelendirme [Tahmin Edildi]'
    process_comp = data.get('process_component', '').strip() or 'Serbest yapılandırma, kanıt kullanma, gerekçeli açıklama'

    system_instruction = (
        'Sen; TYMM ve açık uçlu madde yazımında uzman bir ölçme-değerlendirme uzmanısın.\n'
        'GÖREVİN:\n'
        'Öğrencinin kendi cevabını serbestçe yapılandırmasını, gerekçelendirmesini, analiz etmesini ve çözüm önerisi geliştirmesini '
        'sağlayan standart bir AÇIK UÇLU SORU SETİ ve DERECELİ PUANLAMA RUBRİĞİ hazırlamaktır.\n\n'
        'KURALLAR:\n'
        '- Sorunun ne istediği ve sınırları açık olmalıdır.\n'
        '- Her soru için: Soru kökü, öğrencinin yazacağı çizgili alan [ ......................................... ], '
        '  beklenen tam cevap, kabul edilebilir alternatif cevaplar, yaygın öğrenci yanılgıları ve öğretmene geri bildirim önerisi ekle.\n'
        '- En sonda ANALİTİK DEĞERLENDİRME RUBRİĞİ ve 10 MADDELİ KALİTE KONTROL RAPORU sun.'
    )

    user_prompt = (
        f'## ÖLÇME ARACI KÜNYESİ\n'
        f'- **Ölçme Aracı:** Açık Uçlu Soru Seti & Analitik Rubrik\n'
        f'- **Sınıf Seviyesi:** {data.get("grade")}\n'
        f'- **Ders:** {data.get("subject")}\n'
        f'- **Öğrenme Alanı / Ünite:** {data.get("learning_area")}\n'
        f'- **Öğrenme Çıktısı:** {data.get("learning_outcome")}\n'
        f'- **Bilişsel Düzey:** Analiz → Değerlendirme\n'
        f'- **Hedeflenen Beceri (TYMM):** {skill}\n'
        f'- **Süreç Bileşeni:** {process_comp}\n'
        f'- **Soru Sayısı:** {count}\n'
        f'- **Tahmini Süre:** {duration}\n'
        f'- **Puanlama Modeli:** Analitik Rubrik\n\n'
        f'Her soruyu şu yapıda oluştur:\n\n'
        f'### Açık Uçlu Soru 1\n'
        f'**[Bilişsel Düzey: Analiz-Değerlendirme | Puan: {round(100/int(count),1)}]**\n'
        f'Soru metni ve durum açıklaması...\n'
        f'Öğrenci Cevap Alanı: [ ............................................................................ ]\n\n'
        f'- **Beklenen Tam Cevap:** ...\n'
        f'- **Kabul Edilebilir Kısmi/Alternatif Cevaplar:** ...\n'
        f'- **Olası Kavram Yanılgıları / Hatalar:** ...\n'
        f'- **Öğretmene Geri Bildirim Önerisi:** ...\n\n'
        f'### ANALİTİK DEĞERLENDİRME RUBRİĞİ\n'
        f'| Ölçüt | Yetersiz (0-1 Puan) | Gelişmekte (2 Puan) | Tam / Yetkin (3-4 Puan) |\n'
        f'| Kavramsal Açıklama | ... | ... | ... |\n'
        f'| Kanıt ve Gerekçe | ... | ... | ... |\n'
        f'| Çıkarım ve Değer | ... | ... | ... |\n\n'
        f'### 🔍 TYMM & PISA/TIMSS KALİTE KONTROL RAPORU (10 BOYUTLU DENETİM)\n'
        f'- [✓] A. Öğrenme Çıktısı Kontrolü: Açık uçlu sorular doğrudan çıktıyı yoklamaktadır.\n'
        f'- [✓] B. Bilişsel Düzey Kontrolü: Öğrencinin üst düzey düşünmesini gerektirir.\n'
        f'- [✓] C. Bilimsel Doğruluk: Beklenen cevaplar bilimsel kesinliktedir.\n'
        f'- [✓] D. Dil ve Anlaşılırlık: Soru sınırları ve beklentiler açıktır.\n'
        f'- [✓] E. Belirsizlik Kontrolü: Puanlama kriterleri nesneldir.\n'
        f'- [✓] F. Çeldirici / Derinlik Kontrolü: Ezberden kaçınılmıştır.\n'
        f'- [✓] G. İpucu Kontrolü: Yönergeler bağımsızdır.\n'
        f'- [✓] H. Gereksiz Bilgi Kontrolü: Bilişsel yük dengelenmiştir.\n'
        f'- [✓] I. Beceriyi Görünür Kılma: Öğrencinin düşünce şeması görünür kılınır.\n'
        f'- [✓] J. Puanlama Kontrolü: Rubrik ve geri bildirim yönergeleri hazırdır.'
    )

    return system_instruction, user_prompt

def build_true_false_prompt(data: dict) -> tuple[str, str]:
    count = data.get('question_count', 8)
    duration = data.get('duration', f'{int(count)*1.5} Dakika')
    skill = data.get('skill', '').strip() or 'KB1. Temel Beceriler / Önerme Kontrolü [Tahmin Edildi]'

    system_instruction = (
        'Sen; TYMM objektif ölçme araçları ve Doğru-Yanlış madde yazımında uzman bir eğitimcisin.\n'
        'GÖREVİN:\n'
        'Öğrencinin konu hakkındaki temel kavram yanılgılarını ortaya çıkaran, tek anlamlı, bilimsel kesinliği olan '
        've önermenin doğruluğunu gerekçesiyle sorgulatan bir DOĞRU-YANLIŞ TESTİ hazırlamaktır.\n\n'
        'KURALLAR:\n'
        '- Maddeler kısa, net, tek bir yargı bildiren ifadeler olmalıdır.\n'
        '- Her madde için: Önerme metni, (D / Y) kutucuğu, Doğru/Yanlış anahtarı ve bilimsel açıklaması verilmelidir.\n'
        '- En sonda CEVAP ANAHTARI ve 10 MADDELİ KALİTE KONTROL RAPORU ekle.'
    )

    user_prompt = (
        f'## ÖLÇME ARACI KÜNYESİ\n'
        f'- **Ölçme Aracı:** Doğru - Yanlış Testi (Kavram Yanılgısı Odaklı)\n'
        f'- **Sınıf Seviyesi:** {data.get("grade")}\n'
        f'- **Ders:** {data.get("subject")}\n'
        f'- **Öğrenme Alanı / Ünite:** {data.get("learning_area")}\n'
        f'- **Öğrenme Çıktısı:** {data.get("learning_outcome")}\n'
        f'- **Bilişsel Düzey:** Hatırlama → Anlama\n'
        f'- **Hedeflenen Beceri (TYMM):** {skill}\n'
        f'- **Soru Sayısı:** {count}\n'
        f'- **Tahmini Süre:** {duration}\n'
        f'- **Puanlama Modeli:** Madde Başı {round(100/int(count),1)} Puan (100 Puan)\n\n'
        f'### DOĞRU - YANLIŞ MADDELERİ\n'
        f'Aşağıdaki ifadelerin doğru (D) veya yanlış (Y) olduğunu belirleyiniz:\n\n'
        f'1. [ (D) / (Y) ] Önerme metni...\n'
        f'2. [ (D) / (Y) ] Önerme metni...\n\n'
        f'### CEVAP ANAHTARI VE BİLİMSEL AÇIKLAMALAR\n'
        f'| No | Cevap | Bilimsel Gerekçe & Kavram Yanılgısı Düzeltmesi |\n'
        f'| :---: | :---: | :--- |\n\n'
        f'### 🔍 TYMM & PISA/TIMSS KALİTE KONTROL RAPORU (10 BOYUTLU DENETİM)\n'
        f'- [✓] A. Öğrenme Çıktısı Kontrolü: Maddeler doğrudan kazanımı taramaktadır.\n'
        f'- [✓] B. Bilişsel Düzey Kontrolü: Önerme kontrolü düzeyine uygundur.\n'
        f'- [✓] C. Bilimsel Doğruluk: Doğruluk/yanlışlık ölçütleri kesindir.\n'
        f'- [✓] D. Dil ve Anlaşılırlık: Cümleler tek yargı içerir, açık ve durudur.\n'
        f'- [✓] E. Belirsizlik Kontrolü: Tartışmalı veya yoruma açık ifade yoktur.\n'
        f'- [✓] F. Çeldirici Kontrolü: Yanlış maddeler yaygın hataları hedefler.\n'
        f'- [✓] G. İpucu Kontrolü: İfadeler kalıp ipucu içermez.\n'
        f'- [✓] H. Gereksiz Bilgi Kontrolü: Sadece hedeflenen olguyu sorgular.\n'
        f'- [✓] I. Beceriyi Görünür Kılma: Ön bilgileri ve kavram yanılgılarını teşhis eder.\n'
        f'- [✓] J. Puanlama Kontrolü: Puanlama standart ve objektiftir.'
    )

    return system_instruction, user_prompt

def build_matching_prompt(data: dict) -> tuple[str, str]:
    count = data.get('question_count', 6)
    duration = data.get('duration', '15 Dakika')
    skill = data.get('skill', '').strip() or 'KB1. Sınıflandırma / İlişkilendirme [Tahmin Edildi]'

    system_instruction = (
        'Sen; TYMM ilişkisel ölçme araçları ve Eşleştirme Testi tasarımında uzman bir eğitimcisin.\n'
        'GÖREVİN:\n'
        'İki anlamlı bilgi kümesi arasında (Kavram→Tanım, Olay→Sonuç, Organ→Görev, Enerji türü→Örnek, Bilim insanı→Çalışma) '
        'öğrencinin mantıksal ve pedagojik ilişki kurmasını gerektiren bir EŞLEŞTİRME ETKİNLİĞİ hazırlamaktır.\n\n'
        'KURALLAR:\n'
        '- Sol Sütun (Öncüller/Kavramlar) ve Sağ Sütun (Seçenekler/Açıklamalar) dengeli hazırlanmalıdır.\n'
        '- Tesadüfi eşleştirmeyi önlemek için seçenek sütununa 1-2 adet fazla madde (çeldirici) eklenebilir.\n'
        '- En sonda CEVAP ANAHTARI ve 10 MADDELİ KALİTE KONTROL RAPORU ekle.'
    )

    user_prompt = (
        f'## ÖLÇME ARACI KÜNYESİ\n'
        f'- **Ölçme Aracı:** İlişkisel Eşleştirme Testi\n'
        f'- **Sınıf Seviyesi:** {data.get("grade")}\n'
        f'- **Ders:** {data.get("subject")}\n'
        f'- **Öğrenme Alanı / Ünite:** {data.get("learning_area")}\n'
        f'- **Öğrenme Çıktısı:** {data.get("learning_outcome")}\n'
        f'- **Bilişsel Düzey:** Anlama → İlişkilendirme\n'
        f'- **Hedeflenen Beceri (TYMM):** {skill}\n'
        f'- **Madde Sayısı:** {count}\n'
        f'- **Tahmini Süre:** {duration}\n'
        f'- **Puanlama Modeli:** Madde Başı Puanlama (100 Puan)\n\n'
        f'### EŞLEŞTİRME YÖNERGESİ VE TABLOLARI\n'
        f'Aşağıdaki sol sütunda verilen maddeleri, sağ sütundaki doğru açıklamalarla harfleri kullanarak eşleştiriniz:\n\n'
        f'| No | I. Sütun (Kavramlar / Olgular) | Eşleşme | II. Sütun (Tanımlar / Görevler / Sonuçlar) |\n'
        f'| :---: | :--- | :---: | :--- |\n'
        f'| 1 | ... | [ &nbsp;&nbsp; ] | A) ... |\n'
        f'| 2 | ... | [ &nbsp;&nbsp; ] | B) ... |\n\n'
        f'### CEVAP ANAHTARI\n'
        f'| Soru No | Eşleşen Harf | İlişkinin Pedagojik Açıklaması |\n'
        f'| :---: | :---: | :--- |\n\n'
        f'### 🔍 TYMM & PISA/TIMSS KALİTE KONTROL RAPORU (10 BOYUTLU DENETİM)\n'
        f'- [✓] A. Öğrenme Çıktısı Kontrolü: İki bilgi kümesi kazanımla doğrudan bağlantılıdır.\n'
        f'- [✓] B. Bilişsel Düzey Kontrolü: İlişkilendirme ve anlama basamağına uygundur.\n'
        f'- [✓] C. Bilimsel Doğruluk: Tanım ve özellikler bilimsel olarak kusursuzdur.\n'
        f'- [✓] D. Dil ve Anlaşılırlık: İfadeler yalın ve sınıf seviyesine uygundur.\n'
        f'- [✓] E. Belirsizlik Kontrolü: Her öncül için tek bir doğru eşleşme vardır.\n'
        f'- [✓] F. Çeldirici Kontrolü: Homojen ve dengeli eşleştirme seçenekleri sunulmuştur.\n'
        f'- [✓] G. İpucu Kontrolü: Dilbilgisi ipuçları kaldırılmıştır.\n'
        f'- [✓] H. Gereksiz Bilgi Kontrolü: Karışıklık yaratacak fazlalıklar elenmiştir.\n'
        f'- [✓] I. Beceriyi Görünür Kılma: Kavramsal ilişkilendirmeyi net biçimde ölçer.\n'
        f'- [✓] J. Puanlama Kontrolü: Puan dağılımı eşittir.'
    )

    return system_instruction, user_prompt

def build_case_study_prompt(data: dict) -> tuple[str, str]:
    skill = data.get('skill', '').strip() or 'KB2.4. Çözümleme / KB2.14. Yorumlama / KB2.16. Karar Verme [Tahmin Edildi]'
    process_comp = data.get('process_component', '').strip() or 'Durum analizi yapma, kanıtları değerlendirme, gerekçeli karar alma ve etik/manevi boyutu yorumlama'
    duration = data.get('duration', '40 Dakika')

    system_instruction = (
        'Sen; PISA/TIMSS problem durumları, vaka temelli öğretim ve TYMM bağlam analizinde uzman kıdemli bir eğitimcisin.\n'
        'Aynı zamanda Muallimin Manevi Rehberi (MMR) ile bilimi hikmet, nizam ve ahlaki değerlerle buluşturan bir tasarımcısın.\n\n'
        'GÖREVİN:\n'
        'Öğrencinin karmaşık gerçek bir durumu çok boyutlu analiz etmesini, kanıt toplamasını, gerekçeli karar vermesini '
        've olayın ardındaki düzen, hikmet ve erdemleri fark etmesini sağlayan bir VAKA ANALİZİ MATERYALİ üretmektir.\n\n'
        'VAKA ANALİZİ AKIŞI:\n'
        'VAKA → PROBLEM → VERİLER → ANALİZ → KANIT → SONUÇ / KARAR → GEREKÇE → HİKMET / DEĞER\n\n'
        'ZORUNLU 3 ANA BÖLÜM:\n'
        '1. DURUMU ANALİZ ETME (Vaka senaryosu, aktörler, şartlar, veriler ve durum analizi soruları)\n'
        '2. ÇIKARIM VE DEĞERLENDİRME (Neden-sonuç, kanıt kullanımı, alternatif kararlar ve gerekçelendirme)\n'
        '3. HİKMET VE DEĞER (Kâinattaki ölçü, nizam, hayret, ahlaki erdem keşfi, insani sorumluluk ve akran müzakeresi)\n\n'
        'SONUNDA:\n'
        '1) ÖĞRETMEN ANALİTİK DEĞERLENDİRME RUBRİĞİ (5 Ölçüt, 20 Puan)\n'
        '2) TYMM & PISA/TIMSS 10 BOYUTLU KALİTE KONTROL RAPORU.'
    )

    user_prompt = (
        f'## ÖLÇME ARACI KÜNYESİ\n'
        f'- **Ölçme Aracı:** TYMM Otantik Vaka Analizi & Durum Çözümleme\n'
        f'- **Sınıf Seviyesi:** {data.get("grade")}\n'
        f'- **Ders:** {data.get("subject")}\n'
        f'- **Öğrenme Alanı / Ünite:** {data.get("learning_area")}\n'
        f'- **Öğrenme Çıktısı:** {data.get("learning_outcome")}\n'
        f'- **Bilişsel Düzey:** Analiz → Değerlendirme\n'
        f'- **Hedeflenen Beceri (TYMM):** {skill}\n'
        f'- **Süreç Bileşeni:** {process_comp}\n'
        f'- **Tahmini Uygulama Süresi:** {duration}\n'
        f'- **Puanlama Modeli:** 5 Kriterli Analitik Rubrik (20 Puan)\n\n'
        f'Aşağıdaki 3 ana bölümü, öğretmen rubriğini ve 10 maddeli kalite kontrol raporunu eksiksiz oluştur:\n\n'
        f'### DURUMU ANALİZ ETME\n'
        f'[Gerçek yaşam vaka senaryosu, aktörler, somut veriler, şartlar ve durum tespiti soruları]:\n'
        f'Tespit ve Analiz Alanım: [ ............................................................................ ]\n\n'
        f'### ÇIKARIM VE DEĞERLENDİRME\n'
        f'[Neden-sonuç ilişkileri, alternatif kararlar, kanıtlara dayalı analiz, gerekçelendirme soruları]:\n'
        f'Gerekçeli Değerlendirmem ve Nihai Kararım: [ ............................................................................ ]\n\n'
        f'### HİKMET VE DEĞER\n'
        f'[Vakadaki ölçü, nizam ve ilahi hikmet, ahlaki erdem keşfi, insani sorumluluk ve müzakere]:\n'
        f'- Vakadan Fark Ettiğim Değer ve Hikmet: [ ............................................................................ ]\n'
        f'- Hayata Yansıtacağım İnsani Sorumluluk: [ ............................................................................ ]\n'
        f'- Müzakere Sorusu ve Görüşüm: [ ............................................................................ ]\n\n'
        f'### ÖĞRETMEN ANALİTİK DEĞERLENDİRME RUBRİĞİ (20 PUAN)\n'
        f'| Ölçüt | Başlangıç (1 Puan) | Gelişmekte (2-3 Puan) | Yetkin / Usta (4 Puan) |\n'
        f'| Veri Analizi | Vakadaki verileri ayırt edemez. | Temel verileri tespit eder. | Tüm verileri eksiksiz analiz eder. |\n'
        f'| Kanıt Kullanımı | Çıkarımlarında kanıt sunmaz. | Kısmi kanıt kullanır. | Kararlarını somut kanıtlarla destekler. |\n'
        f'| Neden-Sonuç İlişkisi | İlişkileri kuramaz. | Temel neden-sonuçları görür. | Çok boyutlu neden-sonuç ağını çözer. |\n'
        f'| Çözüm ve Karar | Gelişigüzel karar verir. | Makul ama sığ çözümler üretir. | Gerekçeli, özgün ve uygulanabilir karar verir. |\n'
        f'| Hikmet ve Sorumluluk | Nizam ve ahlaki boyutu göremez. | Erdem ve değeri fark eder. | Hayret, nizam ve insani sorumluluğu içselleştirir. |\n\n'
        f'### 🔍 TYMM & PISA/TIMSS KALİTE KONTROL RAPORU (10 BOYUTLU DENETİM)\n'
        f'- [✓] A. Öğrenme Çıktısı Kontrolü: Vaka doğrudan hedeflenen kanıtı üretmektedir.\n'
        f'- [✓] B. Bilişsel Düzey Kontrolü: Analiz ve değerlendirme basamaklarına tam uygundur.\n'
        f'- [✓] C. Bilimsel Doğruluk: Senaryodaki olgular ve veriler bilimseldir.\n'
        f'- [✓] D. Dil ve Anlaşılırlık: Olay örgüsü merak uyandırıcı ve anlaşılırdır.\n'
        f'- [✓] E. Belirsizlik Kontrolü: Görevler ve yönergeler nettir.\n'
        f'- [✓] F. Çeldirici / Derinlik Kontrolü: Karmaşık ve katmanlı bir akıl yürütme içerir.\n'
        f'- [✓] G. İpucu Kontrolü: Senaryo hazır dogma sunmaz, keşfe yönlendirir.\n'
        f'- [✓] H. Gereksiz Bilgi Kontrolü: Veri seti problemin çözümü için şarttır.\n'
        f'- [✓] I. Beceriyi Görünür Kılma: Öğrencinin karar verme sürecini şeffaflaştırır.\n'
        f'- [✓] J. Puanlama Kontrolü: Analitik rubrik adil ve ayrıntılıdır.'
    )

    return system_instruction, user_prompt

def build_problem_solving_prompt(data: dict) -> tuple[str, str]:
    skill = data.get('skill', '').strip() or 'KB3.2. Problem Çözme / Eleştirel Düşünme [Tahmin Edildi]'
    process_comp = data.get('process_component', '').strip() or 'Problemi anlama, modelleme, strateji geliştirme, çözme ve gerekçelendirme'
    duration = data.get('duration', '35 Dakika')

    system_instruction = (
        'Sen; PISA/TIMSS standartlarında rutin olmayan problem çözme ve TYMM matematiksel/bilimsel akıl yürütme uzmanısın.\n'
        'GÖREVİN:\n'
        'Yalnızca sonucu değil, tüm düşünme ve çözüm sürecini 7 AŞAMADA değerlendiren bir PROBLEM ÇÖZME GÖREVİ oluşturmaktır.\n\n'
        '7 AŞAMALI PROBLEM ÇÖZME SÜRECİ:\n'
        '1. Problemi Anlama (Problem ne istiyor?)\n'
        '2. Verileri ve Kısıtları Belirleme (Hangi bilgiler var, eksikler/kısıtlar neler?)\n'
        '3. Strateji Geliştirme (Hangi yöntem, formül, model kullanılacak?)\n'
        '4. Çözümü Uygulama (Adım adım işlem ve muhakeme)\n'
        '5. Sonucu Bulma ve Anlamlandırma\n'
        '6. Sonucu Kontrol Etme (Sağlama / mantık teyidi)\n'
        '7. Çözümü Gerekçelendirme ve Hayata Yansıtma\n\n'
        'SONUNDA:\n'
        'Aşama Bazlı Puanlama Rubriği ve 10 Maddeli Kalite Kontrol Raporu ekle.'
    )

    user_prompt = (
        f'## ÖLÇME ARACI KÜNYESİ\n'
        f'- **Ölçme Aracı:** Rutin Olmayan Problem Çözme Görevi (PISA/TIMSS Standardı)\n'
        f'- **Sınıf Seviyesi:** {data.get("grade")}\n'
        f'- **Ders:** {data.get("subject")}\n'
        f'- **Öğrenme Alanı / Ünite:** {data.get("learning_area")}\n'
        f'- **Öğrenme Çıktısı:** {data.get("learning_outcome")}\n'
        f'- **Bilişsel Düzey:** Uygulama → Analiz → Değerlendirme\n'
        f'- **Hedeflenen Beceri (TYMM):** {skill}\n'
        f'- **Süreç Bileşeni:** {process_comp}\n'
        f'- **Tahmini Uygulama Süresi:** {duration}\n'
        f'- **Puanlama Modeli:** 7 Aşamalı Süreç Rubriği (100 Puan)\n\n'
        f'### PROBLEM SENARYOSU VE DURUM METNİ\n'
        f'[Gerçek yaşamdan rutin olmayan problem, sayısal/bilimsel veriler ve kısıtlar]:\n\n'
        f'### 1. AŞAMA: Problemi Kendi Cümlelerimle Tanımlama\n'
        f'[ ............................................................................ ]\n\n'
        f'### 2. AŞAMA: Verilenler, İstenenler ve Kısıtlar\n'
        f'- Verilenler: [ ........................................................ ]\n'
        f'- İstenenler: [ ........................................................ ]\n'
        f'- Kısıtlar/Şartlar: [ ........................................................ ]\n\n'
        f'### 3. AŞAMA: Stratejim ve Çözüm Planım\n'
        f'[ ............................................................................ ]\n\n'
        f'### 4. AŞAMA: Çözümün Adım Adım Uygulanması\n'
        f'[ ............................................................................ ]\n\n'
        f'### 5. AŞAMA: Bulduğum Sonuç ve Birimi\n'
        f'[ ............................................................................ ]\n\n'
        f'### 6. AŞAMA: Kontrol ve Sağlama\n'
        f'[ ............................................................................ ]\n\n'
        f'### 7. AŞAMA: Gerekçelendirme, Nizam ve Hayata Yansıtma\n'
        f'- Çözümün mantıksal gerekçesi: [ ........................................................ ]\n'
        f'- Bu problemden öğrendiğim düzen/ölçü ve hayat dersi: [ ........................................................ ]\n\n'
        f'### AŞAMA BAZLI PUANLAMA RUBRİĞİ\n'
        f'| Aşama | Puan | Değerlendirme Kriteri |\n'
        f'| 1. Problemi Anlama | 15 Puan | Problemin özünü doğru kavrama |\n'
        f'| 2. Veri ve Kısıtlar | 15 Puan | Bilgileri eksiksiz listeleme |\n'
        f'| 3. Strateji | 20 Puan | Uygun matematiksel/bilimsel yol seçme |\n'
        f'| 4. Uygulama & Sonuç | 30 Puan | İşlemleri hatasız yürütme |\n'
        f'| 5. Kontrol & Gerekçe | 20 Puan | Sağlama yapma ve hikmet/değer bağı kurma |\n\n'
        f'### 🔍 TYMM & PISA/TIMSS KALİTE KONTROL RAPORU (10 BOYUTLU DENETİM)\n'
        f'- [✓] A. Öğrenme Çıktısı Kontrolü: Problem hedeflenen süreci ölçmektedir.\n'
        f'- [✓] B. Bilişsel Düzey Kontrolü: Rutin olmayan problem basamağındadır.\n'
        f'- [✓] C. Bilimsel Doğruluk: Matematiksel/bilimsel bağıntılar teyit edilmiştir.\n'
        f'- [✓] D. Dil ve Anlaşılırlık: Problem metni net ve yaşa uygundur.\n'
        f'- [✓] E. Belirsizlik Kontrolü: Çözüm yolu mantıksal olarak tutarlıdır.\n'
        f'- [✓] F. Çeldirici / Derinlik Kontrolü: Ezber formül yerine akıl yürütme ister.\n'
        f'- [✓] G. İpucu Kontrolü: Yönergeler sonucu doğrudan vermez.\n'
        f'- [✓] H. Gereksiz Bilgi Kontrolü: Veriler lüzumludur.\n'
        f'- [✓] I. Beceriyi Görünür Kılma: 7 aşamalı düşünce haritası çıkarılmıştır.\n'
        f'- [✓] J. Puanlama Kontrolü: Aşama bazlı puanlama dengelidir.'
    )

    return system_instruction, user_prompt

def build_concept_map_prompt(data: dict) -> tuple[str, str]:
    skill = data.get('skill', '').strip() or 'KB2.3. Örgütleme / KB2.4. Çözümleme [Tahmin Edildi]'
    process_comp = data.get('process_component', '').strip() or 'Kavramlar arası önerme bağlarını kurma, sınıflandırma, ilişkilendirme'
    duration = data.get('duration', '25 Dakika')

    system_instruction = (
        'Sen; kavram öğretimi, Novak kavram haritası ilkeleri ve TYMM kavramsal örgütleme uzmanısın.\n'
        'GÖREVİN:\n'
        'Verilen konudaki ana ve alt kavramları, bağlantı okları ve ilişki önerme ifadeleriyle (örn: "... içerir", "... neden olur", "... oluşur") '
        'sistematik olarak doğrulayan ve kavram yanılgılarını gideren bir KAVRAM HARİTASI MATERYALİ üretmektir.\n\n'
        'SONUNDA:\n'
        'Kavram Haritası Analitik Rubriği ve 10 Maddeli Kalite Kontrol Raporu sun.'
    )

    user_prompt = (
        f'## ÖLÇME ARACI KÜNYESİ\n'
        f'- **Ölçme Aracı:** Kavram Haritası (Önerme Bağları & Hiyerarşi)\n'
        f'- **Sınıf Seviyesi:** {data.get("grade")}\n'
        f'- **Ders:** {data.get("subject")}\n'
        f'- **Öğrenme Alanı / Ünite:** {data.get("learning_area")}\n'
        f'- **Öğrenme Çıktısı:** {data.get("learning_outcome")}\n'
        f'- **Bilişsel Düzey:** Anlama → Analiz\n'
        f'- **Hedeflenen Beceri (TYMM):** {skill}\n'
        f'- **Süreç Bileşeni:** {process_comp}\n'
        f'- **Tahmini Süre:** {duration}\n'
        f'- **Puanlama Modeli:** Kavramsal Rubrik (100 Puan)\n\n'
        f'### KAVRAM LİSTESİ VE ÖNERME BAĞLARI\n'
        f'- Ana Kavram: [Konunun kalbindeki kavram]\n'
        f'- Birinci Düzey Kavramlar: [3-4 temel kavram]\n'
        f'- İkinci Düzey Kavramlar: [Alt kavramlar ve örnekler]\n\n'
        f'### HİYERARŞİK KAVRAM HARİTASI ŞEMASI\n'
        f'```text\n'
        f'[{data.get("topic")}]\n'
        f'  │──(içerir)──> [1. Kavram] ──(özelliğidir)──> [Özellik/Nizam]\n'
        f'  │──(sağlar)──> [2. Kavram] ──(yol açar)─────> [Süreç/Denge]\n'
        f'  └──(işaret eder)─> [3. Kavram] ──(gösterir)──> [Hikmet/Sanat]\n'
        f'```\n\n'
        f'### ÖĞRENCİ TAMAMLAMA VE ÇÖZÜMLEME GÖREVİ\n'
        f'1. Boş bırakılan bağlantı ifadelerini yazınız: [ ......................................... ]\n'
        f'2. Kavramlar arasındaki sebep-sonuç ilişkisini açıklayınız: [ ......................................... ]\n'
        f'3. Kâinattaki bütünsel düzen ve nizam çıkarımınız: [ ......................................... ]\n\n'
        f'### KAVRAM HARİTASI DEĞERLENDİRME RUBRİĞİ\n'
        f'| Ölçüt | Puan | Açıklama |\n'
        f'| Kavram Doğruluğu | 25 Puan | Tüm kavramların doğru yerleştirilmesi |\n'
        f'| Hiyerarşik Yapı | 25 Puan | Genelden özele doğru sıralama |\n'
        f'| Önerme ve Bağlantı İfadeleri | 25 Puan | Oklar üzerindeki ilişki kelimelerinin doğruluğu |\n'
        f'| Çapraz Bağlar & Bütünlük | 25 Puan | Farklı dallar arası anlamlı ilişki ve tefekkür |\n\n'
        f'### 🔍 TYMM & PISA/TIMSS KALİTE KONTROL RAPORU (10 BOYUTLU DENETİM)\n'
        f'- [✓] A. Öğrenme Çıktısı Kontrolü: Kavramsal çerçeve çıktıyla tam uyumludur.\n'
        f'- [✓] B. Bilişsel Düzey Kontrolü: Örgütleme ve ilişkilendirme düzeyindedir.\n'
        f'- [✓] C. Bilimsel Doğruluk: Önermeler bilimsel literatürle uyumludur.\n'
        f'- [✓] D. Dil ve Anlaşılırlık: Şematik gösterim sade ve anlaşılırdır.\n'
        f'- [✓] E. Belirsizlik Kontrolü: Bağlantılar net yönlü oklara sahiptir.\n'
        f'- [✓] F. Çeldirici Kontrolü: Kavram yanılgılarını düzeltecek yapıdadır.\n'
        f'- [✓] G. İpucu Kontrolü: Öğrencinin aktif ilişkilendirmesini zorunlu kılar.\n'
        f'- [✓] H. Gereksiz Bilgi Kontrolü: Sadece çekirdek kavramları içerir.\n'
        f'- [✓] I. Beceriyi Görünür Kılma: Zihinsel şemaları net görünür kılar.\n'
        f'- [✓] J. Puanlama Kontrolü: 4 boyutlu puanlama dengelidir.'
    )

    return system_instruction, user_prompt

def build_mind_map_prompt(data: dict) -> tuple[str, str]:
    skill = data.get('skill', '').strip() or 'KB2.3. Örgütleme / KB2.4. Çözümleme / KB2.15. Yapılandırma [Tahmin Edildi]'
    process_comp = data.get('process_component', '').strip() or 'Kavramları yapılandırma, örüntüleri ve hiyerarşik bağları kurma, bütüncül anlam çıkarma'
    duration = data.get('duration', '30 Dakika')

    system_instruction = (
        'Sen; görsel düşünme ve kavramsal zihin haritalama mimarı, bilişsel örgütleme uzmanı, '
        'TYMM bütüncül modelleme ve Muallimin Manevi Rehberi (MMR) şuur tasarımcısısın.\n\n'
        'TEMEL GÖREVİN:\n'
        'Verilen sınıf, ders, konu ve öğrenme çıktısına ait kavram ağını; parçadan bütüne, somuttan soyuta, '
        'nedenden sonuca sistematik olarak örgütleyen ve kâinattaki muazzam nizamla (bütünlük) birleştiren '
        'standart bir ZİHİN HARİTASI MATERYALİ üretmektir.\n\n'
        'ZİHİN HARİTASI KESİN 3 BÖLÜMLÜ STANDART MİMARİSİ:\n'
        '1. ÖRGÜTLEME (Merkezi Kavram → Ana Dallar)\n'
        '2. YAPILANDIRMA (Alt Dallar → Mekanizmalar → Süreçler)\n'
        '3. BÜTÜNLÜK (Parçadan Bütüne Nizam, MMR Tefekkür ve Vahdet Sentezi, İnsani Değer)\n\n'
        'SONUNDA:\n'
        'Öğretmen Değerlendirme Rubriği ve 10 Maddeli Kalite Kontrol Raporu sun.'
    )

    user_prompt = (
        f'## ÖLÇME ARACI KÜNYESİ\n'
        f'- **Ölçme Aracı:** Kavramsal Zihin Haritası & Bütünlük Sentezi\n'
        f'- **Sınıf Seviyesi:** {data.get("grade")}\n'
        f'- **Ders:** {data.get("subject")}\n'
        f'- **Öğrenme Alanı / Ünite:** {data.get("learning_area")}\n'
        f'- **Öğrenme Çıktısı:** {data.get("learning_outcome")}\n'
        f'- **Bilişsel Düzey:** Anlama → Analiz → Yaratma\n'
        f'- **Hedeflenen Beceri (TYMM):** {skill}\n'
        f'- **Süreç Bileşeni:** {process_comp}\n'
        f'- **Tahmini Süre:** {duration}\n'
        f'- **Puanlama Modeli:** Zihin Haritası Analitik Rubriği (20 Puan)\n\n'
        f'### ÖRGÜTLEME\n'
        f'[Merkezi kavram, 3-4 temel ana dal, kavramsal dayanaklar ve sınıflandırma şeması]:\n'
        f'Kavramsal Odak ve Örgütleme Notum: [ ............................................................................ ]\n\n'
        f'### YAPILANDIRMA\n'
        f'[Alt dallar, kavramlar arası ilişkiler, süreçler ve sebep-sonuç ağları]:\n'
        f'```text\n'
        f'└── [{data.get("topic")}]\n'
        f'    ├── [1. Ana Dal] ──> [Alt Kavram/Özellik] ──> [Süreç/Sonuç]\n'
        f'    ├── [2. Ana Dal] ──> [Alt Kavram/Özellik] ──> [Süreç/Sonuç]\n'
        f'    └── [3. Ana Dal / Hikmet] ──> [Kusursuz Nizam] ──> [Tefekkür]\n'
        f'```\n'
        f'Kavramlar Arası İlişki ve Çözümlemem: [ ............................................................................ ]\n\n'
        f'### BÜTÜNLÜK\n'
        f'[Parçalardan bütüne kâinattaki ahenk, nizam ve birlik (vahdet); MMR tefekkür sentezi ve ahlaki şuur]:\n'
        f'- Bütünsel Nizam ve Hikmet Tefekkürüm: [ ............................................................................ ]\n'
        f'- Bu Kavram Ağından Kazandığım Değer ve Şuur: [ ............................................................................ ]\n\n'
        f'### ÖĞRETMEN DEĞERLENDİRME VE DERECELİ PUANLAMA RUBRİĞİ (20 PUAN)\n'
        f'| Ölçüt | 1 Puan (Başlangıç) | 2-3 Puan (Gelişmekte) | 4 Puan (Yetkin / Usta) |\n'
        f'| Ana Fikrin Doğruluğu | Çekirdek kavramı tespit edemez. | Ana kavramı belirler. | Ana fikri kusursuz örgütler. |\n'
        f'| Alt Başlık Uygunluğu | Alt kavramlar ilgisizdir. | Temel alt dalları kurar. | Tüm alt dalları hiyerarşik konumlandırır. |\n'
        f'| İlişkilendirme ve Akış | Oklar ve bağlar eksiktir. | Basit bağlantılar kurar. | Çok yönlü sebep-sonuç bağı kurar. |\n'
        f'| Görsel Hiyerarşi | Düzensizdir. | Kısmi düzen içerir. | Net, estetik ağ düzeni oluşturur. |\n'
        f'| Bütünlük ve Tefekkür | Bütünsel bağı göremez. | Nizamı kısmen fark eder. | Parçadan bütüne nizam ve manayı açıklar. |\n\n'
        f'### 🔍 TYMM & PISA/TIMSS KALİTE KONTROL RAPORU (10 BOYUTLU DENETİM)\n'
        f'- [✓] A. Öğrenme Çıktısı Kontrolü: Zihinsel şema doğrudan çıktıyı yapılandırır.\n'
        f'- [✓] B. Bilişsel Düzey Kontrolü: Örgütleme ve sentez basamaklarına uygundur.\n'
        f'- [✓] C. Bilimsel Doğruluk: Kavramlar ve dallar bilimsel olarak tutarlıdır.\n'
        f'- [✓] D. Dil ve Anlaşılırlık: Terminoloji duru ve hiyerarşi açıktır.\n'
        f'- [✓] E. Belirsizlik Kontrolü: Odak kavram merkezdedir.\n'
        f'- [✓] F. Çeldirici / Derinlik Kontrolü: Yüzeysel değil bütüncül düşünme ister.\n'
        f'- [✓] G. İpucu Kontrolü: Öğrencinin kendi ilişkilendirmesini destekler.\n'
        f'- [✓] H. Gereksiz Bilgi Kontrolü: Bilişsel yük dengeli dağıtılmıştır.\n'
        f'- [✓] I. Beceriyi Görünür Kılma: Öğrencinin bütünsel kavrayışını görünür kılar.\n'
        f'- [✓] J. Puanlama Kontrolü: 5 kriterli rubrik nesneldir.'
    )

    return system_instruction, user_prompt

def build_ai_outcome_analysis_prompt(data):
    grade = data.get('grade', '').strip() or '5. Sınıf'
    subject = data.get('subject', '').strip() or 'Fen Bilimleri'
    topic = data.get('topic', '').strip() or data.get('learning_outcome', '').strip()
    learning_outcome = data.get('learning_outcome', '').strip() or topic
    skill = data.get('skill', '').strip() or 'KB2.4. Çözümleme / Problem Çözme'
    process_comp = data.get('process_component', '').strip() or 'Verileri ayrıştırma, akıl yürütme, çıkarım yapma ve nizamı fark etme'
    cognitive_level = data.get('cognitive_level', '').strip() or 'Uygulama - Analiz'

    system_instruction = (
        'Sen, Türkiye Yüzyılı Maarif Modeli (TYMM) ve PISA/TIMSS standartlarında çalışan kıdemli bir Ölçme ve Değerlendirme Uzmanısın.\n'
        'Görevin, öğretmenin girdiği öğrenme çıktısını eksiksiz pedagojik analize tabi tutmak ve en uygun ölçme araçlarını 0-100 puanlayarak önermektir.\n\n'
        '10 MADDELİ ANALİZ İLKELERİ:\n'
        '1. Öğrenme çıktısı\n'
        '2. Ana eylem fiili (Örn: Tanımlar, Karşılaştırır, Analiz eder, Gerekçelendirir, Problem çözer, Tasarlar, Değerlendirir)\n'
        '3. Yardımcı eylem fiilleri\n'
        '4. İçerik ve kavramsal odak\n'
        '5. Bilişsel düzey (Öğretmen belirtmemişse tahmin et ve [Tahmin Edildi: ...] olarak göster)\n'
        '6. İlgili beceri (Öğretmen belirtmemişse [Tahmin Edildi: ...] olarak göster)\n'
        '7. Süreç bileşeni\n'
        '8. Öğrenciden beklenen davranış\n'
        '9. Beklenen öğrenme kanıtı\n'
        '10. Ölçülmesi gereken temel özellik\n\n'
        'EYLEM FİİLİ - KANIT UYGUNLUĞU:\n'
        '- Tanımlar → Bilgi/kavrama kanıtı (Yaprak Test, Doğru-Yanlış)\n'
        '- Karşılaştırır / İlişkilendirir → İlişkilendirme kanıtı (Eşleştirme, Kavram Haritası)\n'
        '- Yorumlar / Analiz eder → Analiz kanıtı (Bağlam Temelli Test, Vaka Analizi)\n'
        '- Gerekçelendirir → Açıklama ve kanıt kullanımı (Açık Uçlu Soru)\n'
        '- Problem çözer → Süreç + sonuç kanıtı (Problem Çözme Görevi)\n'
        '- Tasarlar / Örgütler → Ürün + bütünlük kanıtı (Zihin Haritası)\n'
        '- Değerlendirir → Yargı + gerekçelendirme kanıtı (Vaka Analizi, Açık Uçlu Soru)\n\n'
        'ÇIKTIYI KESİNLİKLE ŞU BÖLÜM VE FORMATTA VER:\n'
        '# 1. KATMAN — ANALİZ MOTORU (10 Maddeli Pedagojik Analiz)\n'
        '1. Öğrenme çıktısı: ...\n'
        '2. Ana eylem fiili: ...\n'
        '3. Yardımcı eylem fiilleri: ...\n'
        '4. İçerik / Kavramsal Odak: ...\n'
        '5. Bilişsel düzey: ...\n'
        '6. İlgili beceri: ...\n'
        '7. Süreç bileşeni: ...\n'
        '8. Öğrenciden beklenen davranış: ...\n'
        '9. Beklenen öğrenme kanıtı: ...\n'
        '10. Ölçülmesi gereken temel özellik: ...\n\n'
        '# 2. KATMAN — ÖNERİ MOTORU (9 Araç Uygunluk Matrisi ve En Uygun 3 Araç)\n'
        '### Tüm Ölçme Araçları Uygunluk Matrisi (0–100 Puan)\n'
        '| Ölçme Aracı | Uygunluk Puanı | TYMM & PISA/TIMSS Gerekçesi / Sınırlılığı |\n'
        '| :--- | :---: | :--- |\n'
        '(Yaprak Test, Bağlam Temelli Test, Açık Uçlu Soru, Doğru-Yanlış, Eşleştirme, Vaka Analizi, Problem Çözme, Kavram Haritası, Zihin Haritası)\n\n'
        '### En Yüksek Puanlı Üç Ölçme Aracı Önerisi\n'
        '#### 🥇 1. ARAÇ ADI: [Araç 1]\n'
        '- UYGUNLUK PUANI: %[Puan]\n'
        '- NEDEN ÖNERİLİYOR: ...\n'
        '- ÖLÇEBİLECEĞİ KANIT: ...\n'
        '- BİLİŞSEL DÜZEY UYUMU: ...\n'
        '- BECERİ UYUMU: ...\n'
        '- SÜREÇ BİLEŞENİ UYUMU: ...\n'
        '- AVANTAJI: ...\n'
        '- SINIRLILIĞI: ...\n\n'
        '#### 🥈 2. ARAÇ ADI: [Araç 2]\n'
        '- UYGUNLUK PUANI: %[Puan]\n'
        '- NEDEN ÖNERİLİYOR: ...\n'
        '- ÖLÇEBİLECEĞİ KANIT: ...\n'
        '- BİLİŞSEL DÜZEY UYUMU: ...\n'
        '- BECERİ UYUMU: ...\n'
        '- SÜREÇ BİLEŞENİ UYUMU: ...\n'
        '- AVANTAJI: ...\n'
        '- SINIRLILIĞI: ...\n\n'
        '#### 🥉 3. ARAÇ ADI: [Araç 3]\n'
        '- UYGUNLUK PUANI: %[Puan]\n'
        '- NEDEN ÖNERİLİYOR: ...\n'
        '- ÖLÇEBİLECEĞİ KANIT: ...\n'
        '- BİLİŞSEL DÜZEY UYUMU: ...\n'
        '- BECERİ UYUMU: ...\n'
        '- SÜREÇ BİLEŞENİ UYUMU: ...\n'
        '- AVANTAJI: ...\n'
        '- SINIRLILIĞI: ...\n\n'
        '### Birincil ve İkincil Ölçme Stratejisi\n'
        'Birincil Araç ve İkincil Araç entegrasyonu ve pedagojik gerekçesi.\n\n'
        '### 3. KATMANA GEÇİŞ: Öğretmen Eylem Seçenekleri\n'
        '[1] 1. Önerilen Ölçme Aracını Oluştur (Üretim Motoru)\n'
        '[2] 2. veya 3. Alternatif Aracı Oluştur\n'
        '[3] Tüm 9 Ölçme Aracını Karşılaştır\n'
        '[4] İkili Hibrit Ölçme Paketi Oluştur (Birincil + İkincil Araç + Rubrik + Kalite Kontrol)'
    )

    user_prompt = (
        f'Aşağıda verilen parametrelere göre öğrenme çıktısını 3 KATMANLI MİMARİ doğrultusunda analiz et ve TYMM raporunu hazırla:\n\n'
        f'Ders: {subject}\n'
        f'Sınıf: {grade}\n'
        f'Konu / Tema: {topic}\n'
        f'Öğrenme Çıktısı (Kazanım): {learning_outcome}\n'
        f'Hedeflenen Beceri: {skill}\n'
        f'Süreç Bileşeni: {process_comp}\n'
        f'Bilişsel Düzey: {cognitive_level}\n'
    )

    return system_instruction, user_prompt

def build_dual_tools_prompt(data):
    grade = data.get('grade', '').strip() or '5. Sınıf'
    subject = data.get('subject', '').strip() or 'Fen Bilimleri'
    topic = data.get('topic', '').strip()
    learning_outcome = data.get('learning_outcome', '').strip()
    skill = data.get('skill', '').strip() or 'KB2.4. Çözümleme / KB2.14. Yorumlama [Tahmin Edildi]'
    process_comp = data.get('process_component', '').strip() or 'Verileri ayrıştırma, akıl yürütme, nizam ve dengeyi fark etme'

    system_instruction = (
        'Sen, Türkiye Yüzyılı Maarif Modeli (TYMM) ve PISA/TIMSS standartlarında uzman bir öğretim tasarımcısısın.\n'
        'GÖREVİN:\n'
        'Aynı öğrenme çıktısı için birbirini tamamlayan İKİLİ ÖLÇME-DEĞERLENDİRME PAKETİ (Birincil + İkincil Araç) hazırlamaktır:\n\n'
        '1. BÖLÜM: BİRİNCİL ÖLÇME ARACI (Vaka Analizi / Akıl Yürütme Çalışma Kâğıdı / Problem Çözme)\n'
        '   - Gerçek yaşam bağlamı, veri tablosu, süreç analizi ve tefekkür/hikmet boyutunu içeren derinlemesine etkinlik.\n\n'
        '2. BÖLÜM: İKİNCİL ÖLÇME ARACI (Bağlam Temelli 4 Soru veya Kavramsal Zihin Haritası)\n'
        '   - Kazanım kontrolünü pekiştiren, hızlı biçimlendirici değerlendirme sağlayan bölüm.\n\n'
        '3. BÖLÜM: ÖĞRETMEN DEĞERLENDİRME VE DERECELİ PUANLAMA RUBRİĞİ.\n\n'
        '4. BÖLÜM: TYMM & PISA/TIMSS 10 BOYUTLU KALİTE KONTROL RAPORU.'
    )

    user_prompt = (
        f'## ÖLÇME ARACI KÜNYESİ\n'
        f'- **Ölçme Aracı:** İkili Hibrit Ölçme Paketi (Birincil + İkincil Araç)\n'
        f'- **Sınıf Seviyesi:** {grade}\n'
        f'- **Ders:** {subject}\n'
        f'- **Öğrenme Alanı / Ünite:** {data.get("learning_area", subject)}\n'
        f'- **Öğrenme Çıktısı:** {learning_outcome}\n'
        f'- **Hedeflenen Beceri (TYMM):** {skill}\n'
        f'- **Süreç Bileşeni:** {process_comp}\n'
        f'- **Manevi Öğrenme Çıktısı (MMR):** {data.get("manevi_outcome", "")}\n\n'
        f'İçeriği 4 ana başlık altında tamamla: (1. Birincil Araç, 2. İkincil Araç, 3. Öğretmen Rubriği, 4. 10 Boyutlu Kalite Kontrol Raporu).'
    )

    return system_instruction, user_prompt

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tymm_oneri_motoru.html')
@app.route('/oneri-motoru')
def oneri_motoru_view():
    return render_template('tymm_oneri_motoru.html')

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

def load_mmr_unite_plani_units():
    docx_path = os.path.join(os.path.dirname(__file__), 'Muallimin_Manevi_Rehberi_1_Unite_Plani.docx')
    if os.path.exists(docx_path):
        try:
            import docx
            doc = docx.Document(docx_path)
            table = doc.tables[0]
            units = []
            
            week_titles = [
                "1. Hafta: Güneş'in Yapısı ve Canlılığın Devamı (F.M.5.1.1.1)",
                "2. Hafta: Güneş'in Dönme Hareketi ve Gezegenlere Rahmet Olması (F.M.5.1.1.1)",
                "3. Hafta: Ay'ın Özellikleri ve Hareketlerindeki Mükemmel Düzen (F.M.5.1.2.1)",
                "4. Hafta: Ay'ın Evreleri ve Zaman Ölçüsündeki İlahi İntizam (F.M.5.1.2.2)",
                "5. Hafta: Güneş, Dünya ve Ay'ın Muazzam Uyumu ve Vahdet (F.M.5.1.3.1)"
            ]
            
            week_topics = [
                "Güneş'in Yapısı ve Canlılığın Devamındaki Mükemmel Yaratılış",
                "Güneş'in Dönme Hareketi ve Dünyamıza Rahmet Olması",
                "Ay'ın Özellikleri, Dönme ve Dolanma Hareketlerindeki Mükemmel Düzen",
                "Ay'ın Evreleri ve Zaman Ölçüsündeki İlahi İntizam",
                "Güneş, Dünya ve Ay'ın Birbirine Göre Hareketleri ve Eşsiz Uyumu"
            ]

            for idx, row in enumerate(table.rows[1:]):
                cells = [c.text.replace('\r', '').strip() for c in row.cells]
                if len(cells) >= 5:
                    outcome_raw = cells[1].replace('\n', ' ')
                    proc_comp = cells[2].replace('\n', ' ')
                    degerler = cells[3].replace('\n', ' ')
                    manevi_outcome = cells[4].replace('\n', ' ')
                    
                    unit = {
                        'title': week_titles[idx] if idx < len(week_titles) else f"{cells[0]}: {cells[1][:40]}...",
                        'grade': '5. Sınıf',
                        'subject': 'Fen Bilimleri',
                        'learning_area': '1. Ünite: Güneş, Dünya ve Ay (Dünya ve Evren)',
                        'topic': week_topics[idx] if idx < len(week_topics) else cells[1].split('\n')[-1],
                        'learning_outcome': outcome_raw,
                        'skill': f'TYMM Becerisi / Değerler: {degerler}',
                        'process_component': proc_comp,
                        'manevi_outcome': manevi_outcome
                    }
                    units.append(unit)
            if units:
                return units
        except Exception as e:
            print("Docx parse error, fallback to hardcoded MMR plan:", e)

    return [
        {
            'title': "1. Hafta: Güneş'in Yapısı ve Canlılığın Devamı (F.M.5.1.1.1)",
            'grade': '5. Sınıf',
            'subject': 'Fen Bilimleri',
            'learning_area': '1. Ünite: Güneş, Dünya ve Ay (Dünya ve Evren)',
            'topic': "Güneş'in Yapısı ve Canlılığın Devamındaki Mükemmel Yaratılış",
            'learning_outcome': "F.M.5.1.1.1 Güneş'in yapısı ve dönme hareketi ile ilgili bilgileri toplayabilme.",
            'skill': 'Bilgi Toplama / Sorumluluk, Hikmet, Tefekkür, Şükür',
            'process_component': 'a) Bilgiye ulaşmak için araçları belirler. b) Belirlediği araçları kullanarak bilgileri bulur. c) Doğrular. ç) Kaydeder.',
            'manevi_outcome': "Güneş'in yapısı ve hareketleri bakımından canlılığın devamına katkısındaki mükemmel yaratılışını fark edebilme."
        },
        {
            'title': "2. Hafta: Güneş'in Dönme Hareketi ve Gezegenlere Rahmet Olması (F.M.5.1.1.1)",
            'grade': '5. Sınıf',
            'subject': 'Fen Bilimleri',
            'learning_area': '1. Ünite: Güneş, Dünya ve Ay (Dünya ve Evren)',
            'topic': "Güneş'in Dönme Hareketi ve Dünyamıza Rahmet Olması",
            'learning_outcome': "F.M.5.1.1.1 Güneş'in yapısı ve dönme hareketi ile ilgili bilgileri toplayabilme.",
            'skill': 'Bilimsel Gözlem ve Kayıt / Merhamet, İntizam, Tevhid, İbret',
            'process_component': 'a) Bilgiye ulaşmak için araçları belirler. b) Bilgileri bulur. c) Doğrular. ç) Ulaşılan bilgileri kaydeder.',
            'manevi_outcome': "Güneş'in hareketli bir varlık olarak yaratılmasının etrafındaki gezegenlere, özellikle dünyamıza, bir rahmet olduğunu kavrayabilme."
        },
        {
            'title': "3. Hafta: Ay'ın Özellikleri ve Hareketlerindeki Mükemmel Düzen (F.M.5.1.2.1)",
            'grade': '5. Sınıf',
            'subject': 'Fen Bilimleri',
            'learning_area': '1. Ünite: Güneş, Dünya ve Ay (Dünya ve Evren)',
            'topic': "Ay'ın Özellikleri, Dönme ve Dolanma Hareketlerindeki Mükemmel Düzen",
            'learning_outcome': "F.M.5.1.2.1 Ay'ın özellikleri, dönme ve dolanma hareketleri ile ilgili bilimsel çıkarım yapabilme.",
            'skill': 'Bilimsel Çıkarım / Adalet, Denge, Tevhid, Hayret ve Hayranlık',
            'process_component': "a) Ay'ın özellikleri ve hareketleri ile ilgili nitelikleri tanımlar. b) Topladığı verileri kaydeder. c) Verileri değerlendirir.",
            'manevi_outcome': "Ay'ın hareketlerindeki mükemmel düzeni fark ederek, bu düzenin sonsuz güç sahibi Allah tarafından sağlandığı hakkında çıkarım yapabilme."
        },
        {
            'title': "4. Hafta: Ay'ın Evreleri ve Zaman Ölçüsündeki İlahi İntizam (F.M.5.1.2.2)",
            'grade': '5. Sınıf',
            'subject': 'Fen Bilimleri',
            'learning_area': '1. Ünite: Güneş, Dünya ve Ay (Dünya ve Evren)',
            'topic': "Ay'ın Evreleri ve Zaman Ölçüsündeki İlahi İntizam",
            'learning_outcome': "F.M.5.1.2.2 Ay'ın evrelerini temsil eden bilimsel model oluşturabilme.",
            'skill': 'Bilimsel Modelleme / Zaman Bilinci, Şükür, Hikmet, İntizam',
            'process_component': "a) Ay'ın evrelerini temsil eden bir model önerir. b) Modelini yeni kanıtlara bağlı olarak geliştirir.",
            'manevi_outcome': "Ay'ın hareketlerindeki ince hesap ve düzenden yola çıkarak Cenab-ı Hakkın her şeye gücünün yettiğini anlayabilme."
        },
        {
            'title': "5. Hafta: Güneş, Dünya ve Ay'ın Muazzam Uyumu ve Vahdet (F.M.5.1.3.1)",
            'grade': '5. Sınıf',
            'subject': 'Fen Bilimleri',
            'learning_area': '1. Ünite: Güneş, Dünya ve Ay (Dünya ve Evren)',
            'topic': "Güneş, Dünya ve Ay'ın Birbirine Göre Hareketleri ve Eşsiz Uyumu",
            'learning_outcome': "F.M.5.1.3.1 Güneş, Dünya ve Ay'ın birbirlerine göre hareketlerini ve hacimsel büyüklüklerini temsil eden bilimsel model oluşturabilme.",
            'skill': 'Sistemik Modelleme / Uyum, Birlik (Vahdet), İntizam, Sanat',
            'process_component': "a) Güneş, Dünya ve Ay'ın birbirlerine göre hareketlerini ve büyüklüklerini temsil eden bir model önerir. b) Modelini geliştirir.",
            'manevi_outcome': "Güneş, Dünya ve Ay arasındaki harika uyum ve hareketlerin Allah'ın varlığına işaret ettiği çıkarımında bulunabilme."
        }
    ]

@app.route('/api/sample-units')
def sample_units():
    units = load_mmr_unite_plani_units()
    return jsonify({'units': units})

@app.route('/api/ai-analyze-outcome', methods=['POST'])
def ai_analyze_outcome():
    try:
        data = request.get_json() or {}
        learning_outcome = data.get('learning_outcome', '').strip() or data.get('topic', '').strip()
        if not learning_outcome:
            return jsonify({'success': False, 'error': 'Lütfen en az bir Öğrenme Çıktısı veya Konu giriniz.'}), 400

        sys_inst, user_prompt = build_ai_outcome_analysis_prompt(data)
        client_key = request.headers.get('X-Gemini-Key') or data.get('api_key')
        analysis_text = call_gemini_api(sys_inst, user_prompt, client_key)

        return jsonify({
            'success': True,
            'analysis': analysis_text
        })
    except ValueError as e:
        logger.error(f'Validation/Key error in analysis: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        logger.error(f'AI Outcome Analysis error: {str(e)}')
        return jsonify({'success': False, 'error': 'Yapay zekâ analizi sırasında bir sorun oluştu: ' + str(e)}), 500

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
        elif content_type in ['test', 'yaprak_test']:
            sys_inst, user_prompt = build_test_prompt(data)
        elif content_type in ['context_test', 'baglam_test']:
            sys_inst, user_prompt = build_context_test_prompt(data)
        elif content_type in ['open_ended', 'acik_uclu']:
            sys_inst, user_prompt = build_open_ended_prompt(data)
        elif content_type in ['true_false', 'dogru_yanlis']:
            sys_inst, user_prompt = build_true_false_prompt(data)
        elif content_type in ['matching', 'eslestirme']:
            sys_inst, user_prompt = build_matching_prompt(data)
        elif content_type in ['case_study', 'vaka_analizi']:
            sys_inst, user_prompt = build_case_study_prompt(data)
        elif content_type in ['problem_solving', 'problem_cozme']:
            sys_inst, user_prompt = build_problem_solving_prompt(data)
        elif content_type in ['concept_map', 'kavram_haritasi']:
            sys_inst, user_prompt = build_concept_map_prompt(data)
        elif content_type in ['mind_map', 'zihin_haritasi']:
            sys_inst, user_prompt = build_mind_map_prompt(data)
        elif content_type in ['dual', 'ikili_paket']:
            sys_inst, user_prompt = build_dual_tools_prompt(data)
        else:
            sys_inst, user_prompt = build_worksheet_prompt(data)

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
