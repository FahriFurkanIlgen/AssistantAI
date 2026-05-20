# Bağımsız Test ve Sertifika Raporları

> Kaynak: Blossom-ic Sertifikalar dosyası (TR). Akredite kuruluşların
> AVALON (radyatör) ve Hera+ (yerden ısıtma) sistemleri hakkındaki
> uzman görüşlerinin Türkçe özetleri.

## 1) ITG Dresden — AVALON Sistemi Uzman Görüşü

- **Kuruluş:** Institut für Technische Gebäudeausrüstung Dresden
  Forschung und Anwendung GmbH (ITG Dresden).
- **İmzalayan:** Prof. Dr.-Ing. Bert Oschatz, Müdür.
- **Tarih:** 16 Aralık 2019.
- **Konu:** "Blossom-ic AVALON Sistemi" otomatik hidrolik balans
  uygunluk değerlendirmesi.

### Sistem nasıl çalışır?

- Tüm radyatörler **kablosuz veri ağı** üzerinden birbirine bağlıdır.
- Termostatlar oda sıcaklıklarını sürekli ölçer ve birbirleriyle
  paylaşır.
- **Her 5–10 dakikada bir kontrol algoritması** ayarlanmış ile gerçek
  oda sıcaklığı arasındaki **sıcaklık gradyanını ve gradyan ilerleme
  süresini** birbirleriyle karşılaştırır.
- Karşılaştırma temelinde **valf konumu** ayarlanır → hidronik
  balanslama sağlanır.

### Sonuçlar

- AVALON sisteminin **otomatik hidrolik balans yetkinliği VdZ
  (Verband der Zentralheizungswirtschaft)** teknik standardının
  4. bölümündeki **A ve B prosedürlerine göre** konvansiyonel hidrolik
  balansla **karşılaştırılabilir**.
- VdZ teknik standardının ötesinde, ısı eğrisi ayarı, sirkülasyon
  pompası işletme parametre ayarı, gece düşüşü ayarı gibi opsiyonel
  optimizasyonlar blossom-ic kurulumu sırasında da uygulanmalıdır.

## 2) ITG Dresden — Hera+ Sistemi Uzman Görüşü

- **Kuruluş:** ITG Dresden.
- **İmzalayan:** Prof. Dr.-Ing. Bert Oschatz, Müdür.
- **Tarih:** 16 Aralık 2019.
- **Konu:** Blossom-ic **Hera+ Sistemi** (yerden ısıtma) otomatik
  hidrolik balans uygunluk değerlendirmesi.

### Sistem nasıl çalışır?

- Bir oda içindeki **tüm yerden ısıtma devreleri** birbirine bağlıdır
  ve kablosuz veri ağı üzerinden bağlıdır.
- Termostatlar oda sıcaklığını sürekli ölçer.
- **Dönüş sıcaklığı sensörleri** her yerden ısıtma devresi için **dönüş
  sıcaklığı verisini** dahili olarak iletir.
- Yerden ısıtma devrelerinin oda sıcaklığı ve dönüş sıcaklığının
  zaman akışları ve gradyanları periyodik olarak karşılaştırılır.
- Karşılaştırma temelinde **valf konumu** ayarlanır → hidronik
  balanslama sağlanır.

### Sonuçlar

- Hera+ sisteminin otomatik hidrolik balans yetkinliği VdZ teknik
  standardının 4. bölümündeki **A ve B prosedürlerine göre** konvansiyonel
  hidrolik balansla karşılaştırılabilir.
- Standart-ötesi optimizasyonlar Hera+ kurulumlarında da uygulanır.

## 3) TÜV Rheinland — AVALON Sistemi Sertifikası

- **Kuruluş:** TÜV Rheinland Energy GmbH (Köln).
- **Sertifika sahibi:** blossom-ic intelligent controls AG, Memmingen.
- **Sertifika no.:** **125 386 884**.
- **Tarih:** 20 Kasım 2018.
- **Konu:** Otomatik hidronik balanslama için yeni geliştirilen AVALON
  sisteminin uygunluk değerlendirmesi.
- **Dayanak rapor:** HLK Stuttgart Forschungs- und Prüflaboratorium für
  Heizung-, Lüftungs- und Klimatechnik raporu **H.1810.S.453.BIC**.

### Çalışma prensibi

- Tüm radyatörler kablosuz veri ağı üzerinden bağlı.
- Termostatlar oda sıcaklığını sürekli ölçer ve birbirleriyle
  iletişim kurar.
- Tüm termostatların ayarlanmış sıcaklığı ile gerçek oda sıcaklığı
  arasındaki **sıcaklık gradyanı**, **gradyan ilerleme süresi**,
  **valf kaldırma süresi** **periyodik olarak** karşılaştırılır.
- Karşılaştırma temelinde **valf konumu** ayarlanır.

### Değerlendirme metodolojisi

- AVALON, **TRNSYS V17 simülasyon sistemi** üzerinden detaylı bina
  simülasyonu ile değerlendirildi.
- Karşılaştırma sistemi: TRNSYS V17 ile simüle edilmiş referans bina,
  konvansiyonel hidrolik balans + termostatik radyatör vanaları.

### Sonuçlar

- Test edilen AVALON sistemi otomatik hidrolik balanslama açısından
  termostatik radyatör vanaları kullanılan konvansiyonel hidrolik balansa
  **eşdeğerdir**.
- AVALON sistemine sahip binalarda termostatik radyatör vanalı klasik
  hidrolik dengeli sistemlere göre **daha iyi yıllık tüketim rakamları
  beklenmektedir**.

## 4) HLK Stuttgart GmbH — Hera+ Sistemi Bilimsel Özeti

- **Kuruluş:** HLK Stuttgart GmbH (Pfaffenwaldring 6A, 70569 Stuttgart).
- **Akreditasyon:** Deutsche Akkreditierungsstelle GmbH (DAkkS),
  D-PL-19770-01-00 ve D-IS-19770-01-00 — **DIN EN ISO/IEC 17025** ve
  **DIN EN ISO/IEC 17020** standartlarına göre.
- **Rapor:** H.1908.S.505.BIC.
- **Tarih:** 28 Ağustos 2019.
- **Konu:** Hera+ Sistemi bilimsel inceleme (yerden ısıtma için dijital
  dinamik hidrolik denkleme).
- **Hera+ versiyon:** Termostat + Primus + Actor kombinasyonundan oluşan
  Hera+ **Versiyon 300**.

### İnceleme metodolojisi

- **OpenModelica yazılımı** ile Hera+ sistemi için **bir emülatör**
  programlandı.
- Hera+ sistemi tarafından gerçekleştirilen ısıtma çevrimleri üç farklı
  binada (mevcut binadan EnEV 2014 standardındaki yeni binaya kadar)
  test edildi.

### Sonuçlar

- Dijital dinamik hidrolik denklemeli Hera+ sistemi, sıcaklık kontrolü
  ve yıllık ısı tüketimi açısından **karşılaştırma sisteminden
  üstündür**.
- Hera+ sistemi standart fonksiyonlara ek olarak **akış sıcaklığını her
  ısıtma devresi için ayrı ayrı ölçer**.
- Bu sayede yerden ısıtmanın **yüzey sıcaklığı dolaylı olarak
  optimize edilir** ve sistemde **daha düşük dönüş sıcaklıkları**
  elde edilir.
- "Hera+ Versiyon 300, üretici tarafından tanımlanan kullanım
  alanlarında, klasik hidrolik balans yöntemlerinden daha iyi performans
  gösterir." (HLK Stuttgart GmbH, 28.08.2019)

## 5) 2024 Güncelleme — GEG ve BEG EM Uyumluluğu

- **Mayıs 2024**: ITG Dresden, **AVALON** ve **Hera+** sistemleri için
  uzman görüşlerini **güncellenmiş VdZ teknik standardı** (Mayıs 2022)
  bazında yeniledi.
- Yenileme **Almanya'daki güncel yasal düzenlemelere göre yapıldı**:
  - **GEG** — *Gebäudeenergiegesetz* (Bina Enerji Kanunu).
  - **BEG EM** — *Bundesförderung für effiziente Gebäude — Einzelmaßnahmen*
    (verimli binalar için federal teşvik, tekil önlemler).
- Sonuç: AVALON ve Hera+ sistemleri **VdZ B prosedürüne göre konvansiyonel
  hidrolik balansla karşılaştırılabilir** ve **GEG ile BEG EM
  gerekliliklerini karşılar**.

## Müşteri sorularına özet cevap çerçevesi

- **"Sistem gerçekten dengeleme yapıyor mu?"** → Evet. ITG Dresden,
  TÜV Rheinland ve HLK Stuttgart bağımsız olarak doğruladı.
- **"VdZ uyumu var mı?"** → Evet, hem A hem B prosedürüne göre
  konvansiyonel hidrolik balansla karşılaştırılabilir.
- **"GEG / BEG EM teşvikleri için uygun mu?"** → Evet, Mayıs 2024
  güncellemesi ile gereklilikler karşılanmaktadır.
- **"Hangi simülasyon kullanıldı?"** → AVALON için TRNSYS V17,
  Hera+ için OpenModelica tabanlı emülasyon.
- **"Klasik sisteme göre avantajı kanıtlandı mı?"** → HLK Stuttgart
  raporuna göre Hera+ Versiyon 300, kontrol kalitesi ve yıllık ısı
  tüketimi açısından klasik sistemden üstündür.
