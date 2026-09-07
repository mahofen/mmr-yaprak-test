import { useState } from "react";
import { Sparkles, Loader2, Copy, Check, ChevronRight, AlertCircle } from "lucide-react";

// ---------------------------------------------------------------------------
// Araç veritabanı — Olcme_Araclari_Profil_Veritabani.xlsx içeriğinin özeti
// ---------------------------------------------------------------------------
// NOT: Her araç, Olcme_Araclari_Profil_Veritabani.xlsx'teki TAM profil şemasıyla
// tanımlanmıştır (amaç, ölçtüğü yapı, uygunluk koşulu, uygun olmayan durumlar, puanlama
// dahil). Eşleştirme motoru sadece bilişsel düzey/beceri/süreç etiketlerine değil, bu
// alanların tamamına bakarak karar verir.
const TOOLS = [
  { name: "Yaprak Test", kategori: "Test", amac: "Belirli bir konudaki temel bilgi/kavram hakimiyetini hızlıca taramak", olcugu: "Bilgi / temel beceri", bilisselDuzey: "Hatırlama-Anlama", beceri: "Temel Beceriler (KB1)", surec: "Tanıma / hatırlama", uygunluk: "Ünite başı/sonu hızlı bilgi taraması, geniş içerik kontrolü", uygunOlmayan: "Üst düzey düşünme veya performans ölçümü gereken kazanımlar", puanlama: "Cevap anahtarı", tymmUyumu: "Düşük", geriBildirim: "Düşük", aiUretilebilir: "Evet", agirlik: 2 },
  { name: "Bağlam Temelli Test", kategori: "Test", amac: "Bilgiyi gerçek yaşam durumunda kullanma becerisini ölçmek", olcugu: "Bilgi + beceri bütünleşik yapı", bilisselDuzey: "Uygulama-Analiz", beceri: "Bütünleşik / Üst Düzey Düşünme Becerileri", surec: "Bağlama göre değişir (yorumlama, çıkarım, akıl yürütme)", uygunluk: "TYMM'in önerdiği temel/öncelikli ölçme aracı; çoğu öğrenme çıktısında tercih edilir", uygunOlmayan: "Çok kısa sürede çok sayıda kazanımın taranması gerektiğinde (zaman alıcı)", puanlama: "Cevap anahtarı + çeldirici analizi", tymmUyumu: "Yüksek", geriBildirim: "Orta", aiUretilebilir: "Evet", agirlik: 8.5 },
  { name: "Açık Uçlu", kategori: "Test", amac: "Öğrencinin düşünce sürecini serbestçe yapılandırmasını istemek", olcugu: "İfade / yapılandırma becerisi", bilisselDuzey: "Analiz-Değerlendirme-Yaratma", beceri: "Sorgulama, akıl yürütme, sentezleme", surec: "Serbest yapılandırma / gerekçelendirme", uygunluk: "Zihinsel sürecin görünür kılınması gereken durumlar", uygunOlmayan: "Büyük gruplarda hızlı ve tutarlı puanlama gerektiğinde", puanlama: "Rubrik", tymmUyumu: "Yüksek", geriBildirim: "Yüksek", aiUretilebilir: "Evet", agirlik: 10 },
  { name: "Kısa Cevaplı", kategori: "Test", amac: "Temel bilgi/beceriyi hızlı ve az sözcükle kontrol etmek", olcugu: "Bilgi / temel beceri", bilisselDuzey: "Hatırlama-Uygulama", beceri: "Temel Beceriler (KB1)", surec: "Tanımlama / hesaplama", uygunluk: "Hızlı biçimlendirici kontrol, formül/tanım uygulama", uygunOlmayan: "Üst düzey düşünme becerilerinin ölçülmesi", puanlama: "Cevap anahtarı", tymmUyumu: "Orta", geriBildirim: "Orta", aiUretilebilir: "Evet", agirlik: 6 },
  { name: "Doğru-Yanlış", kategori: "Test", amac: "Bir önermenin doğruluğunu hızlıca test etmek", olcugu: "Bilgi", bilisselDuzey: "Hatırlama", beceri: "Temel Beceriler (KB1)", surec: "Tanıma", uygunluk: "Çok geniş içeriğin hızlı taranması", uygunOlmayan: "Derinlemesine beceri ölçme (şans başarısı yüksek)", puanlama: "Cevap anahtarı", tymmUyumu: "Düşük", geriBildirim: "Düşük", aiUretilebilir: "Evet", agirlik: 2 },
  { name: "Eşleştirme", kategori: "Test", amac: "Kavramlar/öğeler arası ilişkiyi kontrol etmek", olcugu: "Bilgi ilişkilendirme", bilisselDuzey: "Anlama", beceri: "Temel / Bütünleşik (sınıflandırma)", surec: "İlişkilendirme, sınıflandırma", uygunluk: "Kavram-tanım, neden-sonuç gibi ilişkisel bilgi kontrolü", uygunOlmayan: "Üst düzey düşünme becerisi ölçümü", puanlama: "Cevap anahtarı", tymmUyumu: "Düşük", geriBildirim: "Düşük", aiUretilebilir: "Evet", agirlik: 4.5 },
  { name: "Vaka Analizi", kategori: "Vaka/Problem", amac: "Çok boyutlu, gerçekçi bir durumu bütünleşik becerilerle çözümletmek", olcugu: "Bütünleşik / üst düzey beceri", bilisselDuzey: "Analiz-Değerlendirme", beceri: "Sorgulama, eleştirel düşünme", surec: "Yapılandırma, çıkarım yapma, değerlendirme", uygunluk: "Çok boyutlu, katmanlı bağlam gerektiren kazanımlar", uygunOlmayan: "Sadece temel bilgi kontrolü gereken durumlar", puanlama: "Rubrik", tymmUyumu: "Yüksek", geriBildirim: "Yüksek", aiUretilebilir: "Evet", agirlik: 10 },
  { name: "Problem Çözme", kategori: "Vaka/Problem", amac: "Rutin olmayan bir problemi adım adım çözme sürecini ölçmek", olcugu: "Üst düzey düşünme becerisi (KB3.2)", bilisselDuzey: "Uygulama-Analiz", beceri: "Problem Çözme", surec: "Problemi yapılandırma / özetleme / tahmin / akıl yürütme / değerlendirme (KB3.2.SB1-5)", uygunluk: "Rutin olmayan, birden fazla çözüm stratejisi mümkün olan durumlar", uygunOlmayan: "Tek adımlı, doğrudan formül uygulanan hesaplamalar", puanlama: "Aşama bazlı rubrik", tymmUyumu: "Yüksek", geriBildirim: "Yüksek", aiUretilebilir: "Evet", agirlik: 10 },
  { name: "Senaryo", kategori: "Vaka/Problem", amac: "Gerçekçi bir durumda tepki/uygulama becerisini gözlemlemek", olcugu: "Bağlamsal karar/uygulama", bilisselDuzey: "Uygulama-Analiz", beceri: "Karar verme, sorgulama", surec: "Durum değerlendirme", uygunluk: "Gerçekçi durum simülasyonu gereken kazanımlar", uygunOlmayan: "Somut, sayısal ölçüm gereken durumlar", puanlama: "Kontrol listesi / rubrik", tymmUyumu: "Yüksek", geriBildirim: "Orta-Yüksek", aiUretilebilir: "Evet", agirlik: 9.3 },
  { name: "Karar Verme", kategori: "Vaka/Problem", amac: "Seçenekler arasında gerekçeli tercih yapma becerisini ölçmek", olcugu: "Üst düzey düşünme becerisi", bilisselDuzey: "Değerlendirme", beceri: "Karar Verme", surec: "Seçenekleri karşılaştırma, gerekçelendirme", uygunluk: "Birden fazla makul seçeneğin bulunduğu gerçek durumlar", uygunOlmayan: "Tek doğru cevabı olan konular", puanlama: "Rubrik", tymmUyumu: "Yüksek", geriBildirim: "Yüksek", aiUretilebilir: "Evet", agirlik: 10 },
  { name: "Performans Görevi", kategori: "Performans", amac: "Öğrenilen bilgi/beceriyi somut bir ürün/eylemle ortaya koydurmak", olcugu: "Bütünleşik uygulama", bilisselDuzey: "Uygulama-Yaratma", beceri: "Üniteye/derse göre değişir", surec: "Bilgi ve beceriyi bütünleştirerek ürün ortaya koyma", uygunluk: "TYMM'in her ünite/tema için en az bir tane önerdiği zorunlu araç türü", uygunOlmayan: "Büyük ölçekli, hızlı tarama gereken durumlar", puanlama: "Dereceli puanlama anahtarı (rubrik)", tymmUyumu: "Yüksek", geriBildirim: "Yüksek", aiUretilebilir: "Kısmen", agirlik: 9 },
  { name: "Proje", kategori: "Performans", amac: "Uzun soluklu, çok aşamalı bir araştırma/üretim sürecini yönetme becerisini ölçmek", olcugu: "Çok boyutlu beceri bütünü", bilisselDuzey: "Analiz-Yaratma", beceri: "Araştırma, planlama, sentezleme", surec: "Planlama, uygulama, sunma", uygunluk: "Uzun vadeli, disiplinler arası kazanımlar", uygunOlmayan: "Kısa süreli biçimlendirici kontrol", puanlama: "Rubrik", tymmUyumu: "Yüksek", geriBildirim: "Yüksek", aiUretilebilir: "Kısmen", agirlik: 9 },
  { name: "Deney", kategori: "Performans", amac: "Bilimsel süreç becerilerini uygulamalı olarak ölçmek", olcugu: "Bilimsel süreç becerisi", bilisselDuzey: "Uygulama-Analiz", beceri: "Gözlem, ölçme, çıkarım yapma", surec: "Deneysel işlem basamakları", uygunluk: "Fen bilimleri; somut gözlem/ölçüm gerektiren kazanımlar", uygunOlmayan: "Soyut, deneysel olmayan kavramlar", puanlama: "Rubrik / kontrol listesi", tymmUyumu: "Yüksek", geriBildirim: "Yüksek", aiUretilebilir: "Kısmen", agirlik: 9 },
  { name: "STEM", kategori: "Performans", amac: "Disiplinler arası bilgiyi kullanarak tasarım temelli problem çözmek", olcugu: "Disiplinler arası bütünleşik beceri", bilisselDuzey: "Yaratma", beceri: "Problem çözme + tasarım", surec: "Tasarlama, test etme, iyileştirme", uygunluk: "Çok disiplinli, tasarım temelli kazanımlar", uygunOlmayan: "Kısa süreli, tek oturumluk ölçme", puanlama: "Rubrik", tymmUyumu: "Yüksek", geriBildirim: "Yüksek", aiUretilebilir: "Kısmen", agirlik: 9 },
  { name: "Tasarım", kategori: "Performans", amac: "Bir ürünü işlevsel/estetik ölçütlere göre tasarlama becerisini ölçmek", olcugu: "Uygulama/yaratma becerisi", bilisselDuzey: "Yaratma", beceri: "Tasarım, problem çözme", surec: "Ölçüte göre tasarlama", uygunluk: "Somut ürün ortaya çıkarılması istenen kazanımlar", uygunOlmayan: "Soyut/kavramsal bilgi kontrolü", puanlama: "Rubrik", tymmUyumu: "Orta-Yüksek", geriBildirim: "Orta-Yüksek", aiUretilebilir: "Kısmen", agirlik: 7 },
  { name: "Araştırma", kategori: "Performans", amac: "Bir konuyu derinlemesine inceleyip kaynaklardan sentezleme becerisini ölçmek", olcugu: "Bilgi toplama + sentezleme", bilisselDuzey: "Analiz-Değerlendirme", beceri: "Bilgi toplama, sentezleme, sorgulama", surec: "Kaynak tarama, sentezleme", uygunluk: "Derinlemesine incelenmesi gereken konular", uygunOlmayan: "Hızlı biçimlendirici kontrol gereken anlar", puanlama: "Rubrik", tymmUyumu: "Yüksek", geriBildirim: "Yüksek", aiUretilebilir: "Kısmen", agirlik: 9 },
  { name: "Poster", kategori: "Ürün", amac: "Bir konudaki bilgiyi görsel olarak özetleyip sunma becerisini ölçmek", olcugu: "Bilgiyi görselleştirme/özetleme", bilisselDuzey: "Anlama-Uygulama", beceri: "Özetleme, sentezleme", surec: "Bilgiyi düzenleme", uygunluk: "Konuyu görselleştirerek pekiştirme", uygunOlmayan: "Derinlemesine analiz ölçme", puanlama: "Rubrik", tymmUyumu: "Orta", geriBildirim: "Orta", aiUretilebilir: "Kısmen", agirlik: 5 },
  { name: "İnfografik", kategori: "Ürün", amac: "Veriyi görsel ve özet biçimde sunma becerisini ölçmek", olcugu: "Veri görselleştirme", bilisselDuzey: "Anlama-Uygulama", beceri: "Veri yorumlama, özetleme", surec: "Veri düzenleme ve görselleştirme", uygunluk: "Sayısal/istatistiksel bilgiyi sadeleştirme", uygunOlmayan: "Derinlemesine analiz ölçme", puanlama: "Rubrik", tymmUyumu: "Orta", geriBildirim: "Orta", aiUretilebilir: "Kısmen", agirlik: 5 },
  { name: "Kavram Haritası", kategori: "Ürün", amac: "Kavramlar arasındaki ilişkiyi görsel olarak yapılandırma becerisini ölçmek", olcugu: "Kavramlar arası ilişkilendirme", bilisselDuzey: "Analiz", beceri: "Sınıflandırma, ilişkilendirme, yapılandırma", surec: "Kavramsal örgütleme", uygunluk: "Kavramsal bütünleşmenin ölçülmesi gereken konular", uygunOlmayan: "Prosedürel/işlemsel beceri ölçümü", puanlama: "Rubrik / kontrol listesi", tymmUyumu: "Orta-Yüksek", geriBildirim: "Yüksek", aiUretilebilir: "Evet", agirlik: 9.3 },
  { name: "Zihin Haritası", kategori: "Ürün", amac: "Bir konu etrafındaki fikirleri serbest ve dallanmalı biçimde ilişkilendirmek", olcugu: "Yaratıcı ilişkilendirme", bilisselDuzey: "Anlama-Analiz", beceri: "Sınıflandırma, çağrışım kurma", surec: "Serbest yapılandırma", uygunluk: "Beyin fırtınası/ön bilgi etkinleştirme", uygunOlmayan: "Objektif/standart ölçme", puanlama: "Kontrol listesi", tymmUyumu: "Orta", geriBildirim: "Orta", aiUretilebilir: "Evet", agirlik: 6 },
  { name: "Model/Maket", kategori: "Ürün", amac: "Soyut bir kavramı somut, üç boyutlu bir temsille ifade etme becerisini ölçmek", olcugu: "Somut uygulama/temsil", bilisselDuzey: "Uygulama-Yaratma", beceri: "Tasarım, uygulama", surec: "Yapılandırma", uygunluk: "Soyut kavramı somutlaştırma gereken konular", uygunOlmayan: "Hızlı/geniş ölçekli tarama", puanlama: "Rubrik", tymmUyumu: "Orta", geriBildirim: "Orta-Yüksek", aiUretilebilir: "Hayır", agirlik: 5.3 },
  { name: "Sunum", kategori: "Ürün", amac: "İçeriği düzenleyip sözlü/görsel olarak aktarma becerisini ölçmek", olcugu: "İfade / iletişim + içerik hakimiyeti", bilisselDuzey: "Anlama-Değerlendirme", beceri: "İletişim, sentezleme", surec: "Bilgiyi düzenleyip aktarma", uygunluk: "İletişim becerisinin öne çıktığı kazanımlar", uygunOlmayan: "Yazılı derinlemesine analiz gereken durumlar", puanlama: "Rubrik", tymmUyumu: "Orta-Yüksek", geriBildirim: "Yüksek", aiUretilebilir: "Kısmen", agirlik: 7.8 },
  { name: "Video", kategori: "Ürün", amac: "Dijital araçlarla içerik üretme ve anlatma becerisini ölçmek", olcugu: "Dijital üretim + anlatım", bilisselDuzey: "Uygulama-Yaratma", beceri: "İletişim, sentezleme, dijital okuryazarlık", surec: "Senaryolaştırma, düzenleme", uygunluk: "Dijital üretim becerisi vurgulanan kazanımlar", uygunOlmayan: "Hızlı biçimlendirici kontrol", puanlama: "Rubrik", tymmUyumu: "Orta", geriBildirim: "Yüksek", aiUretilebilir: "Kısmen", agirlik: 6.5 },
  { name: "Rapor", kategori: "Ürün", amac: "Bir sürecin/bulgunun yazılı olarak sistematik biçimde sunulması becerisini ölçmek", olcugu: "Yazılı sentezleme/analiz", bilisselDuzey: "Analiz-Değerlendirme", beceri: "Sentezleme, akıl yürütme", surec: "Bulguları düzenleme", uygunluk: "Araştırma/deney sonrası bulguların raporlanması", uygunOlmayan: "Hızlı biçimlendirici kontrol", puanlama: "Rubrik", tymmUyumu: "Yüksek", geriBildirim: "Yüksek", aiUretilebilir: "Evet", agirlik: 10 },
  { name: "Portfolyo", kategori: "Ürün", amac: "Öğrencinin zaman içindeki gelişimini kanıtlarla belgeleme becerisini ölçmek", olcugu: "Zaman içindeki gelişim", bilisselDuzey: "Tüm bilişsel düzeyler", beceri: "Çok boyutlu (öz yansıtma dahil)", surec: "Öz yansıtma + ürün biriktirme", uygunluk: "Uzun vadeli gelişim izleme", uygunOlmayan: "Anlık/tek seferlik ölçme", puanlama: "Rubrik + öz değerlendirme", tymmUyumu: "Yüksek", geriBildirim: "Yüksek", aiUretilebilir: "Kısmen", agirlik: 9 },
  { name: "Gözlem", kategori: "Süreç", amac: "Öğrencinin doğal sınıf ortamındaki davranış/performansını izlemek", olcugu: "Davranış/performans süreci", bilisselDuzey: "Uygulama", beceri: "Üniteye/beceriye göre değişir", surec: "Gözlemlenebilir davranış", uygunluk: "Sınıf içi doğal süreçlerin izlenmesi", uygunOlmayan: "Bireysel derinlemesine bilgi gerektiren durumlar", puanlama: "Gözlem formu / kontrol listesi", tymmUyumu: "Yüksek", geriBildirim: "Yüksek", aiUretilebilir: "Kısmen", agirlik: 9 },
  { name: "Kontrol Listesi", kategori: "Süreç", amac: "Belirli ölçütlerin yerine getirilip getirilmediğini sistematik kontrol etmek", olcugu: "Ölçüt varlığı/yokluğu", bilisselDuzey: "Uygulama", beceri: "Üniteye/beceriye göre değişir", surec: "Ölçüt bazlı kontrol", uygunluk: "Süreç veya ürünün standartlara uygunluğunu kontrol etme", uygunOlmayan: "Derece/nitelik farkını ayırt etme gereken durumlar", puanlama: "Listenin kendisi bir puanlama aracıdır", tymmUyumu: "Yüksek", geriBildirim: "Orta", aiUretilebilir: "Evet", agirlik: 8.5 },
  { name: "Rubrik", kategori: "Süreç", amac: "Performans/ürün kalitesini dereceli ve açık ölçütlerle tanımlamak", olcugu: "Performans/ürün kalitesi", bilisselDuzey: "Tüm düzeyler", beceri: "Üniteye/beceriye göre değişir", surec: "Performans düzeylerini tanımlama", uygunluk: "Performans görevi, vaka, proje gibi karmaşık ürünlerin değerlendirilmesi", uygunOlmayan: "Basit bilgi testlerinin puanlanması", puanlama: "Rubrik kendisi bir puanlama aracıdır", tymmUyumu: "Yüksek", geriBildirim: "Yüksek", aiUretilebilir: "Evet", agirlik: 10 },
  { name: "Öz Değerlendirme", kategori: "Süreç", amac: "Öğrencinin kendi öğrenmesi hakkındaki farkındalığını ortaya çıkarmak", olcugu: "Öğrenme farkındalığı", bilisselDuzey: "Değerlendirme", beceri: "Yansıtma", surec: "Öz yansıtma", uygunluk: "Üst bilişi (metakognisyon) geliştirme", uygunOlmayan: "Objektif/standart puanlama gereken durumlar", puanlama: "Form / ölçek", tymmUyumu: "Yüksek", geriBildirim: "Yüksek", aiUretilebilir: "Evet", agirlik: 10 },
  { name: "Akran Değerlendirme", kategori: "Süreç", amac: "Öğrencinin bir başka öğrencinin çalışmasını ölçütlere göre değerlendirmesini sağlamak", olcugu: "Değerlendirme + eleştirel bakış", bilisselDuzey: "Değerlendirme", beceri: "Eleştirel değerlendirme, ölçüt uygulama", surec: "Ölçüt uygulama", uygunluk: "İş birlikli sınıf ortamları, grup çalışmaları", uygunOlmayan: "Tek başına güvenilirlik kritikse", puanlama: "Form", tymmUyumu: "Orta-Yüksek", geriBildirim: "Orta-Yüksek", aiUretilebilir: "Evet", agirlik: 8 },
  { name: "Grup Değerlendirme", kategori: "Süreç", amac: "Grup içindeki bireysel katkıyı ve iş birliğini adil biçimde belirlemek", olcugu: "İş birliğine katkı", bilisselDuzey: "Değerlendirme", beceri: "İş birliği, sorumluluk alma", surec: "Katkı payını belirleme", uygunluk: "Grup projelerinde adil puanlama gerektiğinde", uygunOlmayan: "Bireysel bilgi ölçme", puanlama: "Form / rubrik", tymmUyumu: "Orta", geriBildirim: "Orta", aiUretilebilir: "Evet", agirlik: 6 },
  { name: "Giriş Bileti", kategori: "Hızlı/Biçimlendirici", amac: "Derse başlamadan önce hazırbulunuşluk ve ön bilgiyi yoklamak", olcugu: "Ön bilgi / hazırbulunuşluk", bilisselDuzey: "Hatırlama", beceri: "Temel Beceriler (KB1)", surec: "Ön değerlendirme", uygunluk: "Derse başlarken ön bilgiyi belirleme (TYMM'in vurguladığı ön değerlendirme)", uygunOlmayan: "Derinlemesine/detaylı ölçme", puanlama: "Puansız gözden geçirme", tymmUyumu: "Yüksek", geriBildirim: "Orta", aiUretilebilir: "Evet", agirlik: 8.5 },
  { name: "Çıkış Bileti", kategori: "Hızlı/Biçimlendirici", amac: "Ders sonunda kazanımın ne ölçüde oluştuğunu hızlıca kontrol etmek", olcugu: "Ders sonu kazanım kontrolü", bilisselDuzey: "Anlama-Uygulama", beceri: "Üniteye göre değişir", surec: "Biçimlendirici kontrol", uygunluk: "Ders sonunda hızlı, düşük riskli kontrol", uygunOlmayan: "Not verme amaçlı kullanım", puanlama: "Puansız / basit değerlendirme", tymmUyumu: "Yüksek", geriBildirim: "Yüksek", aiUretilebilir: "Evet", agirlik: 10 },
  { name: "3-2-1", kategori: "Hızlı/Biçimlendirici", amac: "Öğrenilenleri yapılandırılmış biçimde özetletip yansıtma yaptırmak", olcugu: "Yansıtma + özetleme", bilisselDuzey: "Anlama-Değerlendirme", beceri: "Özetleme, sorgulama", surec: "Öğrenileni yapılandırma", uygunluk: "Ders/ünite sonu yansıtma", uygunOlmayan: "Objektif/standart bilgi ölçme", puanlama: "Puansız", tymmUyumu: "Yüksek", geriBildirim: "Yüksek", aiUretilebilir: "Evet", agirlik: 10 },
  { name: "Trafik Işığı", kategori: "Hızlı/Biçimlendirici", amac: "Öğrencinin konuyu anlama düzeyini anlık ve görsel biçimde ortaya çıkarmak", olcugu: "Öz algılanan anlama düzeyi", bilisselDuzey: "Öz farkındalık", beceri: "Öz değerlendirme", surec: "Anlık geri bildirim", uygunluk: "Sınıf içi anlık kontrol, hız gerektiren durumlar", uygunOlmayan: "Güvenilir/objektif ölçme gerektiğinde", puanlama: "Puanlama yok", tymmUyumu: "Orta", geriBildirim: "Orta", aiUretilebilir: "Evet", agirlik: 6 },
  { name: "Mini Beyaz Tahta", kategori: "Hızlı/Biçimlendirici", amac: "Tüm sınıfın anlık kavrayışını eş zamanlı kontrol etmek", olcugu: "Anlık kavrama kontrolü", bilisselDuzey: "Hatırlama-Uygulama", beceri: "Temel Beceriler (KB1)", surec: "Anlık tepki", uygunluk: "Tüm sınıfın aynı anda katılımının istendiği hızlı kontrol", uygunOlmayan: "Derinlemesine analiz gerektiren durumlar", puanlama: "Puanlama yok / gözlem", tymmUyumu: "Orta-Yüksek", geriBildirim: "Yüksek", aiUretilebilir: "Evet", agirlik: 8.8 },
];

// Kategoriye göre üretim ilkeleri (önceki prompt kütüphanesinden özetlenmiştir)
const KATEGORI_ILKELERI = {
  "Test": `Bağlam öğrencinin yaş/sınıf düzeyine uygun, günlük hayatla ilişkili, karmaşık
detaylardan arındırılmış ve tarafsız olmalı. Soru, bağlam okunmadan çözülebiliyorsa
bu bir hatadır. Çift olumsuzluk, "hepsi/hiçbiri" gibi seçenekler ve metinden birebir
kopyalanan seçenek ifadelerinden kaçın. Çeldiriciler, konuya dair gerçek kavram
yanılgılarına dayanmalı.`,
  "Vaka/Problem": `Katmanlı bir bağlam kur: veriler öğrenciye hazır ayıklanmış sunulmasın,
öğrenci veriyi kendisi ayıklayıp yapılandırsın. Rutin olmayan, birden fazla çözüm
stratejisi mümkün bir problem kurgula. Zihinsel süreci görünür kılacak, akıl yürütme
adımlarını yazdıracak sorular ekle. Aşamalı bir soru seti kullan: problemi tanımlama →
veri ayıklama → tahmin → akıl yürütme → karar/çözüm → yansıtma.`,
  "Performans": `Öğrencinin bilgi ve beceriyi bütünleştirerek somut bir ürün/eylem ortaya
koymasını sağlayan, gerçekçi ve çok aşamalı bir görev tasarla. Görev tanımı net olsun,
beklenen ürün/çıktı ve değerlendirme ölçütleri baştan açıklansın.`,
  "Ürün": `Öğrencinin bilgiyi belirli bir ürün formatında (görsel, yazılı, sözlü, dijital)
yapılandırıp sunmasını isteyen bir yönerge hazırla. Ürünün hangi ölçütlere göre
değerlendirileceğini net biçimde belirt.`,
  "Süreç": `Öğretmenin veya öğrencinin süreç içinde (davranış, performans, iş birliği,
öz farkındalık) kanıt toplamasını sağlayan bir form/rubrik/kontrol listesi hazırla.
Ölçütler gözlemlenebilir, net ve tarafsız olmalı.`,
  "Hızlı/Biçimlendirici": `Çok kısa sürede (birkaç dakika) uygulanabilecek, düşük riskli,
notlandırma amacı taşımayan, hızlı bir biçimlendirici kontrol aracı hazırla. Amaç
öğretmene anlık geri bildirim sağlamaktır.`,
};

function scoreLocal(input, tool) {
  // Basit yerel ön-skorlama (API çağrısı öncesi/yedek olarak) — anahtar kelime örtüşmesi + TYMM ağırlığı
  const text = `${input.bilisselDuzey} ${input.beceri} ${input.surec}`.toLowerCase();
  const toolText = `${tool.bilisselDuzey} ${tool.beceri} ${tool.surec}`.toLowerCase();
  const words = text.split(/[\s,]+/).filter((w) => w.length > 3);
  let overlap = 0;
  words.forEach((w) => {
    if (toolText.includes(w)) overlap += 1;
  });
  const overlapScore = words.length ? overlap / words.length : 0;
  return Math.round((overlapScore * 0.6 + (tool.agirlik / 10) * 0.4) * 100);
}

async function callClaude(prompt) {
  const response = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: "claude-sonnet-4-6",
      max_tokens: 4000,
      messages: [{ role: "user", content: prompt }],
    }),
  });
  const data = await response.json();
  const text = (data.content || [])
    .map((b) => (b.type === "text" ? b.text : ""))
    .join("\n");
  return text;
}

export default function TYMMOneriMotoru() {
  const [ders, setDers] = useState("");
  const [sinif, setSinif] = useState("");
  const [kazanim, setKazanim] = useState("");
  const [bilisselDuzey, setBilisselDuzey] = useState("Uygulama");
  const [beceri, setBeceri] = useState("");
  const [surec, setSurec] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [sonuc, setSonuc] = useState(null); // {matches:[{name,pct,neden}], genelNeden}

  const [uretilenAraç, setUretilenAraç] = useState(null); // tool name
  const [uretimLoading, setUretimLoading] = useState(false);
  const [uretilenMetin, setUretilenMetin] = useState("");
  const [kopyalandi, setKopyalandi] = useState(false);

  const bilisselSecenekleri = [
    "Hatırlama", "Anlama", "Uygulama", "Analiz", "Değerlendirme", "Yaratma",
  ];

  async function analizEt() {
    if (!beceri.trim() || !surec.trim()) {
      setError("Beceri ve süreç bileşeni alanlarını doldurman gerekiyor.");
      return;
    }
    setError("");
    setLoading(true);
    setSonuc(null);
    setUretilenAraç(null);
    setUretilenMetin("");

    const dbText = TOOLS.map(
      (t) =>
        `- ${t.name} (${t.kategori}) | Bilişsel Düzey: ${t.bilisselDuzey} | Beceri: ${t.beceri} | Süreç: ${t.surec} | TYMM Uyumu: ${t.tymmUyumu} | Geri Bildirim: ${t.geriBildirim} | Temel Ağırlık: ${t.agirlik}/10`
    ).join("\n");

    const prompt = `Sen TYMM (Türkiye Yüzyılı Maarif Modeli) bağlam temelli ölçme-değerlendirme
uzmanısın. Aşağıda bir ölçme araçları veritabanı ve bir öğrenme çıktısı analizi var.

ÖLÇME ARAÇLARI VERİTABANI:
${dbText}

ÖĞRENME ÇIKTISI ANALİZİ:
- Ders: ${ders || "belirtilmedi"}
- Sınıf Düzeyi: ${sinif || "belirtilmedi"}
- Kazanım/Konu: ${kazanim || "belirtilmedi"}
- Bilişsel Düzey: ${bilisselDuzey}
- Beceri: ${beceri}
- Süreç Bileşeni: ${surec}

GÖREV: Bu öğrenme çıktısını ölçmek için veritabanındaki araçlardan en uygun 5 tanesini seç
ve her biri için 0-100 arası bir "uyum yüzdesi" hesapla. Uyum yüzdesini hesaplarken:
bilişsel düzey örtüşmesi, beceri örtüşmesi, süreç bileşeni örtüşmesi ve aracın TYMM
uyumu/temel ağırlığını birlikte değerlendir. En uygun aracı %90+ civarında, hiç uygun
olmayanları düşük puanla.

SADECE aşağıdaki JSON formatında, başka hiçbir açıklama/markdown olmadan yanıt ver:
{
  "matches": [
    {"name": "...", "pct": 94, "neden": "kısa, tek cümlelik gerekçe"},
    ...
  ],
  "genelNeden": "Bu öğrenme çıktısının doğasını 1-2 cümleyle açıklayan genel gerekçe"
}`;

    try {
      const text = await callClaude(prompt);
      const clean = text.replace(/```json|```/g, "").trim();
      const parsed = JSON.parse(clean);
      setSonuc(parsed);
    } catch (e) {
      // API/parse hatası olursa yerel skorlamaya düş
      const localMatches = TOOLS.map((t) => ({
        name: t.name,
        pct: scoreLocal({ bilisselDuzey, beceri, surec }, t),
        neden: `${t.kategori} kategorisinde, ${t.tymmUyumu.toLowerCase()} düzeyde TYMM uyumuna sahip bir araç.`,
      }))
        .sort((a, b) => b.pct - a.pct)
        .slice(0, 5);
      setSonuc({
        matches: localMatches,
        genelNeden:
          "Bu öğrenme çıktısı öğrencinin bilgiyi bir bağlam içinde kullanmasını gerektirmektedir.",
      });
    } finally {
      setLoading(false);
    }
  }

  async function aracUret(toolName) {
    const tool = TOOLS.find((t) => t.name === toolName);
    if (!tool) return;
    setUretilenAraç(toolName);
    setUretimLoading(true);
    setUretilenMetin("");
    setKopyalandi(false);

    const ilke = KATEGORI_ILKELERI[tool.kategori] || "";
    const prompt = `Sen TYMM bağlam temelli ölçme-değerlendirme yaklaşımına hâkim bir öğretim
tasarımcısısın.

GÖREV: Aşağıdaki bilgilere göre kullanıma hazır bir "${tool.name}" hazırla.

DERS BİLGİLERİ:
- Ders: ${ders || "genel"}
- Sınıf Düzeyi: ${sinif || "belirtilmedi"}
- Kazanım/Konu: ${kazanim || "belirtilmedi"}
- Bilişsel Düzey: ${bilisselDuzey}
- Hedeflenen Beceri: ${beceri}
- Ölçülecek Süreç Bileşeni: ${surec}

BU ARAÇ TÜRÜNE ÖZGÜ İLKELER:
${ilke}

GENEL TYMM İLKELERİ:
- Bağlam günlük hayatla ilişkili, yaş/sınıf düzeyine uygun, tarafsız ve kapsayıcı olmalı.
- Ölçme; not vermekten çok kanıt toplamaya ve betimleyici geri bildirime hizmet etmeli.
- Gereksiz bilişsel yük oluşturan detay/görsel kullanma.

ÇIKTI: Öğrenciye/uygulayıcıya verilecek dokümanın tam metni + ayrı bir "Öğretmen İçin
Değerlendirme Notu" bölümü. Türkçe, açık ve yalın bir dille, başlıklandırılmış olarak yaz.`;

    try {
      const text = await callClaude(prompt);
      setUretilenMetin(text);
    } catch (e) {
      setUretilenMetin(
        "Doküman üretilirken bir hata oluştu. Lütfen tekrar deneyin."
      );
    } finally {
      setUretimLoading(false);
    }
  }

  function kopyala() {
    navigator.clipboard?.writeText(uretilenMetin);
    setKopyalandi(true);
    setTimeout(() => setKopyalandi(false), 1500);
  }

  const medal = (i) => (i === 0 ? "🥇" : i === 1 ? "🥈" : i === 2 ? "🥉" : "  ");

  return (
    <div style={{ fontFamily: "'Georgia', 'Times New Roman', serif", background: "#F6F3EC", minHeight: "100%", padding: "32px 20px", color: "#1E2A38" }}>
      <div style={{ maxWidth: 760, margin: "0 auto" }}>
        <div style={{ marginBottom: 28 }}>
          <div style={{ fontFamily: "'Helvetica Neue', Arial, sans-serif", fontSize: 12, letterSpacing: 1, color: "#8A6D3B", marginBottom: 6 }}>
            TYMM · Bağlam Temelli Ölçme
          </div>
          <h1 style={{ fontSize: 28, margin: 0, fontWeight: 700, lineHeight: 1.25 }}>
            Ölçme Aracı Öneri Motoru
          </h1>
          <p style={{ fontFamily: "'Helvetica Neue', Arial, sans-serif", fontSize: 14, color: "#5B6470", marginTop: 8, lineHeight: 1.5 }}>
            Öğrenme çıktısının bilişsel düzeyini ve becerisini gir; kılavuzun 36 aracını
            TYMM ilkelerine göre karşılaştırıp en uygun olanları öner.
          </p>
        </div>

        {/* GİRİŞ FORMU */}
        <div style={{ background: "#FFFFFF", border: "1px solid #E4DFD2", borderRadius: 4, padding: 22, fontFamily: "'Helvetica Neue', Arial, sans-serif" }}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, marginBottom: 14 }}>
            <div>
              <label style={labelStyle}>Ders</label>
              <input style={inputStyle} value={ders} onChange={(e) => setDers(e.target.value)} placeholder="ör. Fen Bilimleri" />
            </div>
            <div>
              <label style={labelStyle}>Sınıf Düzeyi</label>
              <input style={inputStyle} value={sinif} onChange={(e) => setSinif(e.target.value)} placeholder="ör. 5. Sınıf" />
            </div>
          </div>

          <div style={{ marginBottom: 14 }}>
            <label style={labelStyle}>Kazanım / Konu</label>
            <input style={inputStyle} value={kazanim} onChange={(e) => setKazanim(e.target.value)} placeholder="ör. Ay'ın evreleri ve Dünya-Ay-Güneş konumu" />
          </div>

          <div style={{ marginBottom: 14 }}>
            <label style={labelStyle}>Bilişsel Düzey</label>
            <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
              {bilisselSecenekleri.map((b) => (
                <button
                  key={b}
                  onClick={() => setBilisselDuzey(b)}
                  style={{
                    ...chipStyle,
                    background: bilisselDuzey === b ? "#1E2A38" : "#FFFFFF",
                    color: bilisselDuzey === b ? "#FFFFFF" : "#1E2A38",
                  }}
                >
                  {b}
                </button>
              ))}
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, marginBottom: 18 }}>
            <div>
              <label style={labelStyle}>Beceri</label>
              <input style={inputStyle} value={beceri} onChange={(e) => setBeceri(e.target.value)} placeholder="ör. Problem çözme" />
            </div>
            <div>
              <label style={labelStyle}>Süreç Bileşeni</label>
              <input style={inputStyle} value={surec} onChange={(e) => setSurec(e.target.value)} placeholder="ör. Veriyi kullanma, akıl yürütme" />
            </div>
          </div>

          {error && (
            <div style={{ display: "flex", gap: 6, alignItems: "center", color: "#9B4B3E", fontSize: 13, marginBottom: 12 }}>
              <AlertCircle size={14} /> {error}
            </div>
          )}

          <button onClick={analizEt} disabled={loading} style={primaryBtnStyle}>
            {loading ? <Loader2 size={16} className="spin" /> : <Sparkles size={16} />}
            {loading ? "Analiz ediliyor..." : "Analiz Et"}
          </button>
        </div>

        {/* SONUÇLAR */}
        {sonuc && (
          <div style={{ marginTop: 28 }}>
            <SectionTitle text="Öğrenme Çıktısı Analizi" />
            <div style={{ fontFamily: "'Helvetica Neue', Arial, sans-serif", fontSize: 14, color: "#3C4652", marginBottom: 20, lineHeight: 1.6 }}>
              <b>Bilişsel Düzey:</b> {bilisselDuzey} &nbsp;·&nbsp; <b>Beceri:</b> {beceri} &nbsp;·&nbsp; <b>Süreç Bileşeni:</b> {surec}
            </div>

            <SectionTitle text="Önerilen Ölçme Araçları" />
            <div style={{ display: "flex", flexDirection: "column", gap: 10, marginBottom: 20 }}>
              {sonuc.matches?.map((m, i) => (
                <div key={m.name} style={{ background: "#FFFFFF", border: "1px solid #E4DFD2", borderRadius: 4, padding: "14px 16px", fontFamily: "'Helvetica Neue', Arial, sans-serif" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <span style={{ fontSize: 18 }}>{medal(i)}</span>
                      <span style={{ fontWeight: 700, fontSize: 15 }}>{m.name}</span>
                    </div>
                    <span style={{ fontFamily: "Georgia, serif", fontWeight: 700, fontSize: 18, color: i === 0 ? "#8A6D3B" : "#1E2A38" }}>
                      %{m.pct}
                    </span>
                  </div>
                  <div style={{ height: 5, background: "#EFEBE0", borderRadius: 3, marginTop: 8, marginBottom: 10 }}>
                    <div style={{ height: "100%", width: `${m.pct}%`, background: i === 0 ? "#8A6D3B" : "#1E2A38", borderRadius: 3 }} />
                  </div>
                  <div style={{ fontSize: 13, color: "#5B6470", marginBottom: 10 }}>{m.neden}</div>
                  <button onClick={() => aracUret(m.name)} style={secondaryBtnStyle}>
                    {m.name.toUpperCase()} OLUŞTUR <ChevronRight size={13} />
                  </button>
                </div>
              ))}
            </div>

            {sonuc.genelNeden && (
              <div style={{ fontFamily: "'Helvetica Neue', Arial, sans-serif", fontSize: 13, color: "#5B6470", background: "#EFEBE0", padding: "12px 14px", borderRadius: 4, lineHeight: 1.6 }}>
                💡 {sonuc.genelNeden}
              </div>
            )}
          </div>
        )}

        {/* ÜRETİLEN DOKÜMAN */}
        {uretilenAraç && (
          <div style={{ marginTop: 28 }}>
            <SectionTitle text={`Oluşturulan Doküman — ${uretilenAraç}`} />
            <div style={{ background: "#FFFFFF", border: "1px solid #E4DFD2", borderRadius: 4, padding: 20 }}>
              {uretimLoading ? (
                <div style={{ display: "flex", alignItems: "center", gap: 8, color: "#5B6470", fontFamily: "'Helvetica Neue', Arial, sans-serif", fontSize: 14 }}>
                  <Loader2 size={16} className="spin" /> Doküman hazırlanıyor...
                </div>
              ) : (
                <>
                  <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 10 }}>
                    <button onClick={kopyala} style={secondaryBtnStyle}>
                      {kopyalandi ? <Check size={13} /> : <Copy size={13} />}
                      {kopyalandi ? "Kopyalandı" : "Kopyala"}
                    </button>
                  </div>
                  <pre style={{ whiteSpace: "pre-wrap", fontFamily: "'Helvetica Neue', Arial, sans-serif", fontSize: 14, lineHeight: 1.7, color: "#1E2A38", margin: 0 }}>
                    {uretilenMetin}
                  </pre>
                </>
              )}
            </div>
          </div>
        )}
      </div>
      <style>{`
        .spin { animation: spin 1s linear infinite; }
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        button { cursor: pointer; }
        input:focus { outline: 2px solid #8A6D3B; outline-offset: 1px; }
      `}</style>
    </div>
  );
}

function SectionTitle({ text }) {
  return (
    <div style={{ fontFamily: "'Helvetica Neue', Arial, sans-serif", fontSize: 12, letterSpacing: 0.5, color: "#8A6D3B", fontWeight: 700, marginBottom: 10, textTransform: "uppercase" }}>
      {text}
    </div>
  );
}

const labelStyle = { display: "block", fontSize: 12, color: "#5B6470", marginBottom: 5, fontFamily: "'Helvetica Neue', Arial, sans-serif" };
const inputStyle = { width: "100%", padding: "9px 11px", border: "1px solid #D9D2C0", borderRadius: 4, fontSize: 14, fontFamily: "'Helvetica Neue', Arial, sans-serif", boxSizing: "border-box" };
const chipStyle = { padding: "6px 12px", border: "1px solid #D9D2C0", borderRadius: 16, fontSize: 13, fontFamily: "'Helvetica Neue', Arial, sans-serif" };
const primaryBtnStyle = { display: "flex", alignItems: "center", gap: 8, background: "#1E2A38", color: "#FFFFFF", border: "none", borderRadius: 4, padding: "11px 20px", fontSize: 14, fontWeight: 600, fontFamily: "'Helvetica Neue', Arial, sans-serif" };
const secondaryBtnStyle = { display: "flex", alignItems: "center", gap: 5, background: "#F6F3EC", color: "#1E2A38", border: "1px solid #D9D2C0", borderRadius: 4, padding: "7px 12px", fontSize: 12, fontWeight: 600, fontFamily: "'Helvetica Neue', Arial, sans-serif" };
