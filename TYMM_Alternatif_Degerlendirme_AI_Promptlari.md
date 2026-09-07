# TYMM Bağlam Temelli Alternatif Ölçme-Değerlendirme Araçları
## Yapay Zekaya Verilecek Hazır Promptlar

Bu promptlar, **"Türkiye Yüzyılı Maarif Modeli Bağlam Temelli Çoktan Seçmeli Soru Yazım Kılavuzu"** (MEB, Mart 2026) içindeki ilkeler temel alınarak hazırlanmıştır: bağlam kurgulama ilkeleri, KB1/KB2/KB3 beceri sınıflandırması, süreç bileşenleri, kontrol listesi kriterleri ve sık yapılan hata tablolarındaki doğru yaklaşımlar.

Her promptta **[KÖŞELİ PARANTEZ İÇİNDEKİ]** alanları kendi dersine göre doldurman yeterli. Promptları ChatGPT, Claude, Gemini gibi herhangi bir yapay zekaya doğrudan yapıştırabilirsin.

---

## 1) ÇALIŞMA KÂĞIDI ÜRETİM PROMPTU (Bağlam Temelli)

Bu prompt; klasik "bilgi hatırlama" sorularının ötesinde, günlük hayatla ilişkili, beceri ölçen bir çalışma kâğıdı üretir.

```
ROL: Sen, Türkiye Yüzyılı Maarif Modeli (TYMM) bağlam temelli ölçme-değerlendirme
yaklaşımına hâkim, deneyimli bir öğretim tasarımcısısın.

GÖREV: Aşağıdaki bilgilere göre bir "Bağlam Temelli Çalışma Kâğıdı" hazırla.

DERS BİLGİLERİ:
- Ders: [ör. Fen Bilimleri]
- Sınıf Düzeyi: [ör. 5. Sınıf]
- Ünite/Konu: [ör. Gökyüzündeki Komşularımız ve Biz]
- Hedeflenen Öğrenme Çıktısı/Kazanım: [öğretim programından kod ve ifade]
- Ölçülecek Süreç Bileşen(ler)i: [ör. "gözleme dayalı tahmin etme", "karşılaştırma"]
- Hedeflenen Beceri Türü: [Temel Beceri / Bütünleşik Beceri / Üst Düzey Düşünme Becerisi -
  hangisiyse belirt; emin değilsen aşağıdaki listeden en uygununu sen seç ve gerekçelendir]
  * Temel Beceriler örnek: saymak, okumak, yazmak, çizmek, ölçmek, kaydetmek
  * Bütünleşik Beceriler örnek: özetleme, sınıflandırma, karşılaştırma, sorgulama,
    çıkarım yapma, yorumlama, sentezleme
  * Üst Düzey Düşünme Becerileri: problem çözme, karar verme, eleştirel düşünme
- Öğrenci Sayısı/Süre: [ör. 40 dakikalık ders süresi]

BAĞLAM KURGUSU İLKELERİ (mutlaka uygula):
1. Bağlam, öğrencinin yaş ve sınıf düzeyine uygun ve günlük hayatla ilişkili olmalı.
2. Bağlam karmaşık detaylardan arındırılmış, tek bir odak probleme indirgenmiş olmalı.
3. Bağlam; kültür, cinsiyet, coğrafi bölge, din, ideoloji, sosyoekonomik düzey açısından
   tarafsız ve kapsayıcı olmalı (yalnızca belirli bir kesimin aşina olduğu senaryolardan kaçın).
4. Bağlam "işlevsiz" olmamalı — yani soru, bağlam okunmadan/kullanılmadan çözülebiliyorsa
   bu bir hatadır. Öğrenci cevaba ulaşmak için mutlaka bağlamdaki veriyi/bilgiyi kullanmalı.
5. Zorlama, yapay kurgulardan kaçın (ör. "Ayşe markete gitti, 3x2+5 ekmek aldı" gibi
   anlamsız-yapay cümleler YASAK). Bunun yerine gerçekçi bir problem durumu kurgula
   (ör. "Ayşe, farklı gramajlardaki ürünlerin birim fiyatını karşılaştırıp ekonomik
   tercih yapmak istiyor").
6. Aynı bağlamdan birden fazla soru/etkinlik üretiliyorsa, sorular zincirleme bağımlı
   olmamalı (bir önceki soruyu yanlış yapan öğrenci sonrakini de otomatik yanlış yapmamalı).

ÇALIŞMA KÂĞIDI YAPISI:
1. Başlık ve kısa yönerge (öğrenciye ne yapması gerektiği net şekilde anlatılmalı)
2. Bağlam metni/senaryosu (yukarıdaki ilkelere uygun, 1 paragraf ile yarım sayfa arası)
   - Bağlamı desteklemek için gerekiyorsa bir tablo/grafik/veri seti TASLAĞI da metin
     olarak sun (ör. "Tablo: Ay Sıcaklık: ... Gündüz: ... Gece: ...")
3. 4-6 arası görev/soru — açık uçlu, kısa cevaplı, doldurmalı, eşleştirmeli veya
   çoktan seçmeli karışık türde olabilir. Her görevin hangi süreç bileşenini
   ölçtüğünü parantez içinde belirt (öğretmen için, öğrenciye gösterme).
4. Bilişsel yükü artıran gereksiz bilgi/görsel KULLANMA — her veri, çözüm için gerekli olmalı.
5. Sonda öğretmene özel "Değerlendirme Notu" bölümü ekle: her görev için beklenen
   cevap anahtarı / kabul edilebilir cevap aralığı ve dikkat edilmesi gereken
   yaygın öğrenci hataları.

DİL VE ANLATIM:
- Açık, yalın, sınıf düzeyine uygun Türkçe kullan.
- Çift olumsuzluk içeren ifadelerden kaçın.
- "Sizce", "sence" gibi öznel ifadeler yerine bağlama/veriye referans veren
  nesnel ifadeler kullan.

ÇIKTI FORMATI: Öğrenciye dağıtılacak temiz metin + ayrı bir "Öğretmen Cevap Anahtarı"
bölümü halinde, başlıklandırılmış olarak ver.
```

---

## 2) VAKA ANALİZİ (CASE STUDY) ÜRETİM PROMPTU

Bu prompt; özellikle **bütünleşik beceriler (sorgulama, çözümleme, sentezleme)** ve **üst düzey düşünme becerilerini (problem çözme, karar verme, eleştirel düşünme)** ölçmeye uygun, çok katmanlı bir vaka metni üretir.

```
ROL: Sen, TYMM bağlam temelli ölçme-değerlendirme yaklaşımına hâkim bir
öğretim tasarımcısı ve vaka (case) yazarısın.

GÖREV: Aşağıdaki bilgilere göre öğrencilerin ders içi/ödev olarak analiz edeceği
bir "Vaka Analizi Dokümanı" hazırla.

DERS BİLGİLERİ:
- Ders: [ör. Sosyal Bilgiler / Fen Bilimleri / Matematik vb.]
- Sınıf Düzeyi: [ör. 7. Sınıf]
- Ünite/Konu: [ör. ]
- Hedeflenen Öğrenme Çıktısı: [ ]
- Hedeflenen Beceri: [Problem Çözme / Sorgulama / Eleştirel Düşünme / Karar Verme /
  Alan Becerisi: ... — belirt]
- Ölçülecek Süreç Bileşenleri (kılavuzdaki KB3.2 Problem Çözme örneği ile uyumlu
  şekilde, uygun olanları seç):
  * Problemi yapılandırmak
  * Problemi özetlemek
  * Gözleme/mevcut bilgiye/veriye dayalı tahminde bulunmak
  * Önermeler üzerinden akıl yürütmek
  * Yansıtma/değerlendirmede bulunmak
  (Sorgulama becerisi seçildiyse: bilgi toplama, sınıflandırma, çıkarım yapma,
  genelleme, sentezleme gibi ilgili süreç bileşenlerini kullan.)

VAKA KURGUSU İLKELERİ (mutlaka uygula):
1. "KATMANLI BAĞLAM" oluştur: Tüm veriler öğrenciye ayıklanmış, hazır sunulmasın.
   Öğrenci; veri içinden anlamlı olanı ayırt etmek, dağınık bilgi arasından
   doğru olanı seçip yapılandırmak zorunda kalmalı.
2. "ROTİN OLMAYAN" bir problem kurgula — öğrencinin daha önce doğrudan formülle/
   ezberle çözebileceği bir durum OLMASIN. Birden fazla çözüm stratejisi mümkün olmalı,
   disiplinler arası bağlantı içersin.
3. Zihinsel süreç görünür kılınmalı: Vaka, öğrenciyi sadece "doğru cevaba" değil,
   "bu sonuca nasıl ulaştığını açıklamaya" da yönlendirmeli (akıl yürütme adımlarını
   yazdıracak sorular ekle).
4. Gerçekçi, günlük hayattan, kapsayıcı bir senaryo seç — belirli bir sosyoekonomik
   gruba özgü aşinalık gerektiren (ör. borsa/türev piyasa gibi) dar kapsamlı
   senaryolardan kaçın.
5. Etik ve tarafsızlık: Vaka; kültür, cinsiyet, coğrafi bölge, din, ideoloji
   açısından olumsuz çağrışım İÇERMEMELİ.

VAKA DOKÜMANI YAPISI:
1. **Vaka Başlığı**
2. **Giriş / Durum Tanımı** (yarım-1 sayfa): Gerçekçi bir kişi/kurum/olay etrafında
   kurgulanmış, öğrencinin çözmesi gereken asıl problemi içinde barındıran ama
   doğrudan söylemeyen bir anlatı.
3. **Destekleyici Veri Seti**: Tablo, grafik açıklaması, kısa alıntılar, sayısal
   veriler gibi öğrencinin ayıklayıp kullanması gereken malzemeler (gerçek veri
   gibi tutarlı sayılar üret, metni tekrar eden gereksiz görsel önerme).
4. **Analiz Soruları** (5-7 adet, aşamalı zorlukta):
   a. Problemi tanımlama/yapılandırma sorusu ("Bu vakada asıl çözülmesi gereken
      mesele nedir?")
   b. Veri ayıklama/özetleme sorusu
   c. Tahmin/çıkarım sorusu (veriye dayalı)
   d. Akıl yürütme sorusu ("X değişse sonuç nasıl etkilenirdi?" tipi)
   e. Karar verme/çözüm önerisi sorusu (gerekçeli seçim yapmasını iste)
   f. Yansıtma/değerlendirme sorusu ("Kendi çözümünün güçlü/zayıf yönü nedir?")
5. **Öğretmen Değerlendirme Rehberi**: Her soru için
   - Ölçülen süreç bileşeni
   - Beklenen cevap özellikleri / örnek güçlü ve zayıf cevap
   - Basit bir dereceli puanlama anahtarı (rubrik) — 3 seviyeli (Başlangıç/Gelişmekte/Yeterli)

ÇIKTI FORMATI: Öğrenciye dağıtılacak vaka metni + sorular / ayrı bölümde
öğretmen değerlendirme rehberi ve rubrik.
```

---

## 3) GENEL PEDAGOJİK DOKÜMAN ŞABLONU (Esnek / Çok Amaçlı Prompt)

Bu, worksheet ve vaka analizinin dışında kalan diğer alternatif ölçme araçları (performans görevi, gözlem formu, dereceli puanlama anahtarı, kavram haritası etkinliği vb.) için kullanabileceğin genel çerçeve promptudur.

```
ROL: Sen, TYMM (Türkiye Yüzyılı Maarif Modeli) ölçme-değerlendirme yaklaşımına
hâkim bir öğretim tasarımcısısın. TYMM'de ölçme; not verme odaklı değil,
öğrenme sürecinin doğal bir parçası olarak, betimleyici geri bildirim vermeyi
amaçlar.

GÖREV: [DOKÜMAN TÜRÜNÜ BELİRT: ör. "performans görevi", "gözlem formu",
"dereceli puanlama anahtarı (rubrik)", "kavram haritası etkinliği",
"öz değerlendirme formu", "akran değerlendirme formu" vb.]
hazırla.

TEMEL BİLGİLER:
- Ders / Sınıf Düzeyi: [ ]
- Ünite / Tema / Öğrenme Alanı: [ ]
- Hedeflenen Öğrenme Çıktısı ve Süreç Bileşeni: [ ]
- Hedeflenen Beceri Türü (Temel / Bütünleşik / Üst Düzey Düşünme / Alan Becerisi): [ ]
- Uygulama Ortamı: [Bireysel / Grup çalışması / Ev ödevi / Sınıf içi]
- Süre: [ ]

UYULMASI GEREKEN KONTROL LİSTESİ KRİTERLERİ
(TYMM Soru/Etkinlik Yazımına Yönelik Kontrol Listesi'nden uyarlanmıştır — her
kriteri kendi kontrol et ve dokümanın sonunda "Kontrol Listesi Uygunluk Notu"
olarak kısaca özetle):

BAĞLAM SEÇİMİ
- [ ] Öğrencinin yaş/sınıf düzeyine uygun mu?
- [ ] Günlük hayatla ilişkili mi?
- [ ] Karmaşık, gereksiz detaylardan arındırılmış mı?
- [ ] İlgili beceriyi gerçekten ölçebilecek nitelikte mi?
- [ ] Kültür, cinsiyet, coğrafi bölge, din, ideoloji açısından tarafsız ve
      kapsayıcı mı?

ETKİNLİK/GÖREV TASARIMI
- [ ] Açık ve anlaşılır bir dille yazılmış mı?
- [ ] Güçlük düzeyi hedef öğrenci grubuna uygun mu?
- [ ] Görev, hedeflenen süreç bileşenini/bileşenlerini gerçekten ölçüyor mu?
- [ ] Öğrenciyi bağlamdan bağımsız, ezbere dayalı bir kısayoldan cevap
      bulmaktan alıkoyacak şekilde kurgulanmış mı?
- [ ] İpucu içeren, cevabı ele veren ifadelerden kaçınılmış mı?

ETİK VE TARAFSIZLIK
- [ ] Herhangi bir birey/grup/kültür hakkında olumsuz çağrışım var mı? (olmamalı)
- [ ] Kullanılan materyaller (metin/tablo/grafik) pedagojik ve etik açıdan uygun mu?

DİL VE ANLATIM
- [ ] Yazım kuralları ve noktalama işaretlerine uyulmuş mu?
- [ ] Anlatım bozukluğu var mı? (olmamalı)

TASARIM
- [ ] Gereksiz, metni tekrar eden görsel/veri var mı? (olmamalı — her görsel/veri
      yeni ve gerekli bilgi taşımalı)
- [ ] Bağlam ve ona ait görevler tek bir bütün hâlinde mi sunuluyor (sayfa
      çevirmeyi gerektiren dağınıklık yok mu)?

ÇIKTI FORMATI:
1. Dokümanın kendisi (öğrenciye/uygulayıcıya yönelik, kullanıma hazır)
2. Öğretmen için kısa uygulama notu (nasıl uygulanacağı, süre, ipucu)
3. Değerlendirme ölçütleri / cevap anahtarı / rubrik (doküman türüne uygun olan)
4. Sonda kısa "Kontrol Listesi Uygunluk Notu": yukarıdaki listeye göre dokümanın
   nerelerde güçlü olduğunu, varsa nelere dikkat edilmesi gerektiğini 3-4
   cümleyle özetle.
```

---

## Kullanım Notları

- **Tek seferde birden fazla belge** istiyorsan, her prompta konuyu/kazanımı
  değiştirerek tekrar tekrar verebilirsin; ya da prompta "Aynı bağlamı kullanarak
  3 farklı zorluk seviyesinde 3 versiyon üret" gibi bir ek talimat ekleyebilirsin.
- Kılavuzdaki **"Bağlamın işlevselliğini test etme"** ilkesi (bağlam olmadan
  soru/görev çözülebiliyor mu?) en kritik kontrol noktasıdır — yapay zeka çıktısını
  aldıktan sonra mutlaka bunu manuel olarak kontrol et.
- Sorgulama, problem çözme gibi bütünleşik/üst düzey becerileri hedefleyen
  dokümanlarda, yapay zekadan çıktı aldıktan sonra "çeldiricileri/yanlış cevap
  seçeneklerini güçlendir, gerçek kavram yanılgılarına dayandır" şeklinde bir
  ikinci tur iyileştirme promptu vermen faydalı olur (örnek: "Yukarıdaki vakadaki
  çoktan seçmeli soruların çeldiricilerini, öğrencilerin bu konudaki yaygın kavram
  yanılgılarına göre yeniden yaz").
