# Maarif Modeli & Muallimin Manevi Rehberi (MMR) Materyal Üreticisi

Türkiye Yüzyılı Maarif Modeli (TYMM), Bağlam Temelli Öğrenme, Erdem-Değer-Eylem (EDE) yaklaşımı ve Muallimin Manevi Rehberi (MMR) pedagojik çerçevesiyle çalışan **Çalışma Kağıdı** ve **Yaprak Test** üretim platformu.

---

## 🌟 Özellikler

* **Pedagojik Omurga:** `Öğrenme Çıktısı → Bilgi → Düşünme → Anlamlandırma → Tefekkür → Değer → Eylem`
* **Çalışma Kağıdı (10 Bölüm):**
  1. Merak Et
  2. Bağlamı İncele
  3. Fark Et
  4. Bilgiyi Kullan
  5. Düşün ve İlişkilendir
  6. Tefekkür Penceresi
  7. Erdem ve Değer
  8. Müzakere Edelim
  9. Eyleme Dönüştür
  10. Kendimi Değerlendiriyorum
* **Yaprak Test:**
  * Bilişsel basamaklara göre dengeli dağılım (Hatırlama, Anlama, Uygulama, Analiz, Değerlendirme).
  * 4 seçenekli, bilimsel kavram yanılgılarına dayalı çeldiriciler.
  * Öğretmen için **Cevap Anahtarı ve Bilişsel Düzey Matrisi**.
* **Çift Çıktı Entegrasyonu:**
  * MEB Maarif Modeli **Öğrenme Çıktısı (Kazanım)** ve hemen altında **Manevi Öğrenme Çıktısı**.
* **Dışa Aktarma Seçenekleri:**
  * Doğrudan A4 baskı ve PDF kaydetme (`@media print` uyumlu).
  * Tek tıkla Microsoft Word belgesi (`.docx`) olarak indirme.
  * Markdown panoya kopyalama.
* **Google Gemini API Desteği:**
  * Model fallback desteği (`gemini-3.6-flash`, `gemini-3.5-flash`, `gemini-2.5-flash-lite`).
  * Güvenli sunucu tarafı API yönetimi (`.env`).

---

## 🚀 Hızlı Başlangıç

### 1. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

### 2. API Anahtarını Tanımlayın

`.env.example` dosyasını `.env` olarak kopyalayın ve Google AI Studio'dan aldığınız API anahtarını ekleyin:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Sunucuyu Başlatın

```bash
python app.py
```

Tarayıcınızda açın: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 📁 Proje Yapısı

```text
├── app.py                     # Flask backend ve Gemini API entegrasyonu
├── requirements.txt           # Python bağımlılıkları
├── .env.example               # Çevre değişkeni şablonu
├── .gitignore                 # Güvenlik ve önbellek yoksayma kuralları
├── materyal_goruntuleyici.html# Standalone materyal vitrini ve baskı sayfası
├── test_backend.py            # Uçtan uca sistem test paketi
├── templates/
│   └── index.html             # Web arayüzü şablonu
└── static/
    ├── css/
    │   └── style.css          # Arayüz ve baskı stilleri
    └── js/
        └── app.js             # İstemci tarafı betikleri
```

---

## 📄 Lisans

Bu proje eğitim ve öğretim tasarımı amaçlı geliştirilmiştir.
