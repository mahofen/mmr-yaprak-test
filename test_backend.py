import sys
import json
from app import app

sys.stdout.reconfigure(encoding='utf-8')

def run_tests():
    print("=== MMR & MAARİF MATERYAL ÜRETİCİ TESTLERİ BAŞLIYOR ===")
    client = app.test_client()

    # 1. Health check
    print("\n1. Health Check Testi...")
    res = client.get('/api/health')
    assert res.status_code == 200, f"Health check failed: {res.status_code}"
    data = res.get_json()
    print("Health Status:", data)
    assert data.get('has_api_key') is True, "API Key algılanamadı!"
    print("✓ Health Check Başarılı! (API Key mevcut)")

    # 2. Sample units check
    print("\n2. Hazır Şablonlar Testi...")
    res = client.get('/api/sample-units')
    assert res.status_code == 200
    units = res.get_json().get('units', [])
    print(f"Yüklenen şablon sayısı: {len(units)}")
    assert len(units) >= 5, "Şablonlar eksik!"
    print(f"✓ İlk şablon: {units[0]['title']}")

    # 3. DOCX Export check
    print("\n3. Word (.docx) Dışa Aktarma Testi...")
    sample_md = "# 5. Sınıf Fen Bilimleri\n## Test Başlığı\n* Madde 1\n* Madde 2\n> Tefekkür penceresi"
    res = client.post('/api/export-docx', json={'content': sample_md, 'title': 'Test_Materyal'})
    assert res.status_code == 200
    assert res.content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    print(f"✓ DOCX İndirme Başarılı! (Dosya boyutu: {len(res.data)} bayt)")

    # 4. Generate Worksheet with Gemini API
    print("\n4. Gemini API ile Gerçek Çalışma Kağıdı Üretim Testi...")
    test_payload = {
        "grade": "5. Sınıf",
        "subject": "Fen Bilimleri",
        "learning_area": "Dünya ve Evren",
        "topic": "Güneş'in Yapısı ve Dönme Hareketi",
        "learning_outcome": "F.M.5.1.1.1. Güneş'in yapısı ve dönme hareketi ile ilgili bilgileri toplayabilme.",
        "content_type": "worksheet"
    }
    res = client.post('/api/generate', json=test_payload)
    assert res.status_code == 200, f"Generate failed: {res.get_json()}"
    gen_data = res.get_json()
    assert gen_data.get('success') is True, "Üretim başarısız!"
    content = gen_data.get('content', '')
    print(f"✓ Çalışma Kağıdı Başarıyla Üretildi! (Karakter sayısı: {len(content)})")
    print("Üretilen içerikten ilk 300 karakter:\n" + content[:300] + "\n...")

    # Check that required sections exist in the generated worksheet
    for sec in ["MERAK ET", "BAĞLAM", "FARK ET", "BİLGİYİ KULLAN", "TEFEKKÜR PENCERESİ", "ERDEM", "EYLEM"]:
        found = sec in content.upper()
        print(f"  - Bölüm '{sec}': {'Mevcut ✓' if found else 'Eksik ✗'}")

    print("\n=== TÜM SİSTEM TESTLERİ BAŞARIYLA TAMAMLANDI! ===")

if __name__ == '__main__':
    run_tests()
