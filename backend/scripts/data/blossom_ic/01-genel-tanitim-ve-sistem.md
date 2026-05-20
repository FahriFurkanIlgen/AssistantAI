# Blossom-ic — Genel Tanıtım ve Sistem Mimarisi

> Kaynak: Resmi Blossom-ic kurumsal sunumu (TR), 17 Nisan 2025.
> Bu doküman, son kullanıcı / tesisatçı / enerji danışmanı sorularına
> verilen yanıtların temel referansıdır.

## Marka

- **blossom-ic intelligent controls AG** — **dijital hidronik
  balanslamanın mucidi**. Yedi yıllık ürün geçmişi.
- Marka alt-mark: **dhb (digital-hydraulic-balance)**.
- Ürün ekosistemi tek bir sistem altında: ısıtma, soğutma, yerden ısıtma,
  fan-coil, akıllı ev uzantıları (Magelan ailesi), uygulama ve Building
  Management System.

## Dijital Hidronik Balanslama (DHB) — temel avantajlar

- **%40'a varan enerji tasarrufu potansiyeli.**
- **Montaj süresinden %90'a kadar tasarruf** sağlar.
- **Otonom ve adaptif** hidronik balanslama (kendi kendine öğrenir,
  binadaki değişikliklere dinamik olarak uyum sağlar).
- Termostatlar pil veya 230 V seçenekli.
- **Mevcut boru şebekesine müdahale gerektirmez.**
- **Önceden ayarlanmış termostatik vana gerekmez** — klasik vanalar
  değiştirilmeden sistem kurulur.
- Tek sistemde hem uygulama hem Building Management System kullanılabilir.

## Hidronik balanslama nedir, neden gerekir?

Bir ısıtma sisteminde su en az direnci seçer ve ısı üreticisine en hızlı
yoldan geri dönmek ister. Bu nedenle:

- Kazana yakın odalar (örn. zemin kat) **çok sıcak**,
- Kazandan uzak odalar (örn. çatı katı) **çok soğuk** olur.

**Sonuçlar:**
- Isıtma sisteminin verimsizliği → yüksek ısıtma maliyeti.
- Düşük yaşam konforu → soğuk odalar.
- Çevreye zarar.
- Radyatörlerde akış sesi.

Hidronik balanslama bu sorunları çözer ve evde **eşit ısı dağılımı**
sağlar — tüm odalarda "optimum" sıcaklık.

## Klasik (mekanik) hidronik balanslamanın zorlukları

Mevcut binalarda mekanik dengelemenin zorlukları zincir reaksiyonu
şeklindedir:

1. İnşa edilmiş planlar yok veya yanlış (boru ağı bilinmiyor).
2. Boru hattındaki değişiklikler belgelenmemiş.
3. Boruların iç yüzeylerinin durumu bilinmiyor.
4. Planlama sırasında yanlış hesaplanan radyatörler.
5. Radyatörlerin değiştirilmesi belgelenmemiş.
6. Üretici spesifikasyonlarına göre valf özellikleri yanlış.
7. Planlama sırasında belirlenen bölge ısıtma yükleri yanlış.
8. Çok fazla çaba gerektiren valf değişimi.

## Blossom-ic'in çalışma mantığı

- Sistem, **tüm termostatların hedef ve gerçek sıcaklığının
  gradyanlarını, süresini ve valf kaldırma süresini** karşılaştırır.
- Valfleri **800 ince dereceli adıma kadar** düzenler.
- Bu süreç tüm bağlı termostatlar arasında **sürekli iletişimle**
  yapılır.
- Örnek: a) odasının sıcaklığı b) odasındakinden daha hızlı yükseliyorsa,
  a) odasındaki hacimsel akış valf aracılığıyla kısılır ve akış
  b) odasına hidronik olarak yönlendirilir.
- Akıllı ev uzantıları gerektiğinde her zaman entegre edilebilir.

## Akıllı algoritmalara dayalı dijital dinamik hidronik balanslama

- Benzersiz dijital yöntem — tam otomatik, özerk ve uyarlanabilir.
- Akıllı algoritmalar ile temellendirilmiş.
- Yüksek düzeyde akredite enstitüler tarafından bilimsel kanıtlarla
  kapsamlı testler.
- Son derece kısa montaj süreleri — **%90'a varan tasarruf** mümkündür.
- Mevcut boru ağı ve hidroniklere müdahale gerekmez.

## Bağımsız uzman görüşleri (özet)

- **ITG Dresden Forschung und Anwendung GmbH** — AVALON sistemi
  (radyatör) ve Hera+ sistemi (yerden ısıtma) için otomatik hidrolik
  balans uygunluk değerlendirmeleri (16 Aralık 2019). Sonuç: VdZ teknik
  standardının 4. bölümündeki A ve B prosedürlerine göre konvansiyonel
  hidrolik balansla **en az karşılaştırılabilir**.
- **TÜV Rheinland** — AVALON sistemi sertifikası (Reg. No. 125386884,
  20.11.2018). HLK Stuttgart raporu H.1810.S.453.BIC'e dayanır. Sonuç:
  AVALON sistemi konvansiyonel hidrolik balansla termostatik vanalara
  sahip sisteme eşdeğer; üstelik daha iyi yıllık tüketim rakamları
  beklenir.
- **HLK Stuttgart GmbH** — Hera+ sistemi bilimsel özeti (07.10.2019,
  rapor H.1908.S.505.BIC). Sonuç: dijital dinamik hidrolik balanslı
  Hera+, hem sıcaklık kontrolü hem yıllık ısı tüketimi açısından
  karşılaştırma sisteminden **üstündür**.
- **Mayıs 2024** — ITG Dresden tarafından **GEG (Gebäudeenergiegesetz)**
  ve **BEG EM** (yenileme teşvikleri) temelinde güncellenmiş uzman
  görüşleri yayımlandı; AVALON ve Hera+ sistemlerinin VdZ B prosedürüne
  uygunluğu yeniden teyit edildi → GEG ve BEG EM gerekliliklerini
  karşılar.
- VdZ standart-ötesi optimizasyonlar (ısı eğrisi ayarı, sirkülasyon
  pompası işletme parametreleri, gece düşüşü ayarı) blossom-ic kurulumu
  sırasında da uygulanmalıdır.

## blossom-ic kablosuz BUS (bwb) — eşsiz altyapı

- blossom-ic sistemi tamamen **kablosuz** çalışır.
- Cihazların birbirine kablo ile bağlanmasına gerek yoktur.
- Yeni ve eski binalara çok az çabayla kurulabilir.
- İzleme fonksiyonlu Building Management System sunar.
- blossom-ic ailesinin tüm bileşenleri entegre edilebilir.
- **BAC-Net | MOD-bus arayüzü** mevcuttur.
- Uygulama ve Building Management System eşzamanlı kullanılabilir.

## blossom-ic App (mobil uygulama)

- Akıllı telefon ve tablet için, App Store ve Google Play'de ücretsiz.
- "better start smart" sloganı.
- Sistem genel görünümünde kontrol edilebilir cihaz kategorileri:
  - **Heizkörper** (radyatör), **Fußbodenheizung** (yerden ısıtma),
    **Kessel** (kazan), **Etagenheizung** (kat ısıtması).
  - **Sicherheitssystem** (güvenlik), **Leckage System** (sızıntı
    koruması).
  - **Jalousien** (panjur), **Steckdose** (akıllı priz),
    **PI-Sensor** (hareket sensörü).
  - **Zirkulationssystem** (sıcak su sirkülasyon), **Fan-Coil**.
- Yardım bölümünde **video kılavuzları** ve **PDF kılavuzları** mevcut.
- Yerden ısıtma yönetimi: zon başına anlık ve hedef sıcaklık, online
  durum, port sayısı, batarya göstergesi.
- Radyatör kontrolünde 3 mod tek dokunuşta: **Comfort (22°C)**,
  **Eco (16°C)**, **Nachtabsenkung — gece düşüşü (17°C)**. Manuel veya
  Auto/Zeit modu seçilebilir. Termostat ve hareket sensörü ayrı
  açılıp kapatılabilir.

## Building Management System (web arayüzü)

- Modbus, Bacnet veya başka bir işletim sistemi olmayan binalar için
  **Wi-Fi bağlantılı web tabanlı işletim programı**.
- Tüm cihazlarla kablosuz iletişim ve kontrol.
- **LAN kablo veya SIM kart** ile internete bağlanır; binadaki tüm
  Fan Coil / termostat ünitelerinin **anlık verileri** işletim
  programından takip edilir ve uzaktan ayarlanır.
- Blossom-ic akıllı ev ürünlerine kablosuz bağlantı: su kaçağı sensörü,
  panjur/perde kontrolü, alarm sistemi, pompa, kazan ve ısı pompası
  kontrolü.
- **Dijital hidronik balans ile %30'a kadar enerji tasarrufu**.
- Üç ana fonksiyon:
  - **Merkezi izleme** (Gateway + Avalon sekmeleri, kat-bazlı ağaç).
  - **Isıtma süresinin ayarlanması** (Auto/Zeit veya Manuell mod).
  - **Sıcaklık sınırlaması** — min. 6 °C, maks. 30 °C.

## Merkezi kontrol ünitesi — Gateway GT-100

- blossom-ic ürün ailesine ait **tüm sistemlerin** kontrolü
  (radyatörler + yerden ısıtma).
- İnternete bağlanıldığında **otomatik IP algılama**.
- Sistem başına **20 adede kadar termostat** bir merkezi kontrol
  ünitesi üzerinden kontrol edilebilir.
- Tüm merkezi kontrol üniteleri birbiriyle ağa bağlanır ve ağ üzerinden
  iletişim kurar.
- Tüm uygulamalar için tek bir merkez kontrol ünitesi yeterlidir.

## Hareket sensörü (tüm termostatlarda)

- Tüm termostatlar bir **hareket sensörü** ile donatılmıştır.
- Sensör odadaki insanları algılar ve bireysel olarak ayarlanan
  ısıtma programlarını tamamlar.
- Genel kural: **1 °C sıcaklık düşüşü ≈ %6 enerji tasarrufu**.
- Uygulama aracılığıyla kapatılabilir.
- Aynı sensör teknolojisi blossom-ic bünyesindeki **alarm sistemi**
  için de kullanılır.

## Radyatör kontrolü — Avalon+ (kablosuz termostat)

- Dijital hidronik balanslama ile entegre.
- Tüm M30 × 1,5 mm vanalara uyar.
- **Pil göstergesi, valf koruma, pencere açıklığı algılama** fonksiyonu.
- Oda sıcaklığı yetersizliğini tespit eder.
- Kurulum sırasında **sinyal gücü bağlantı tespiti** (termostat
  üzerinde).
- Tüm Avalon termostatları birbiriyle bağlanabilir.
- GT-100 Gateway ile bağlantılı.

## Radyatör kontrolü — Avalon Combo+ (pilli aktüatör + oda termostatı)

- Dijital hidronik balanslama ile entegre.
- Tüm M30 × 1,5 mm vanalara uyar.
- Bir oda termostatı ile **6 adede kadar aktüatör** kontrol edilebilir.
- Pil göstergesi, valf koruma, pencere açıklığı algılama.
- Oda sıcaklığı yetersizliğini tespit eder.
- Kurulum sırasında sinyal gücü bağlantı tespiti.
- GT-100 Gateway ile bağlantılı.

## Radyatör kontrolü — Avalon Combo+ P (230 V aktüatör + oda termostatı)

- Dijital hidronik balanslama ile entegre.
- Tüm M30 × 1,5 mm vanalara uyar.
- Bir oda termostatı ile 6 adede kadar aktüatör kontrol edilebilir.
- **Sinyal güçlendirici**, valf koruma ve pencere açıklığı algılama.
- Oda sıcaklığı yetersizliğini tespit eder.
- Kurulum sırasında sinyal gücü bağlantı tespiti.
- GT-100 Gateway ile bağlantılı.

> **İpucu:** Avalon Combo+ sistemleri birbiriyle karıştırılabilir.
> Örnek: 230 V aktüatör pilli termostat ile, pilli aktüatör 230 V
> termostat ile bağlanabilir.

## Tek borulu ısıtma sistemleri — Tarus String

- Tek borulu (örn. yatay dağıtım) sistemlerin kontrolü ve düzenlenmesi
  için özel kontrol ünitesi.
- Tüm ayrı, hidronik besleme ve dönüş hatları için uygundur.
- Bir Tarus String ile **20 adede kadar Avalon / Avalon+ / Avalon Combo+
  termostat** kontrol edilebilir.
- GT-100 Gateway ile bağlantılı.

## Yerden ısıtma kontrolü — Hera System (ısıtma + soğutma)

- Bir odadaki **birkaç ısıtma devresinin birbiriyle tam hidronik
  dengelenmesi**.
- **Step motorlu aktüatör**, 800 adım aralığında hassas kontrol.
- **Ek elektrik işi gerekmez** — RJ11 yama kabloları (patch) ile bağlanır.
- Pil ve 230 V termostatlar — yenileme ve güçlendirme için ideal çözüm.

### Hera+ Primus PRO S / Hera+ Extensia PRO (kablosuz yerden ısıtma şeridi)

- 6 portlu modül, sıcaklık göstergeli.
- Dijital hidronik balanslama ile entegre.
- Hera+ ve Hera Direct+ termostatları ile farklı odalar kontrol edilebilir.
- Dağıtıcıdaki akış/dönüş için entegre sensörün yanı sıra dönüş hatları
  için ek sensörler (zemin yüzey sıcaklığı optimizasyonu).
- **Bir ağ geçidine 5 adede kadar Hera+ Primus PRO** kaydedilebilir.
- Bir Hera+ Primus PRO'ya **4 adede kadar Hera+ Extensia PRO** bağlanabilir.
- Sonuç: bir ağ geçidi ile **150'ye kadar devre** kontrol edilebilir.
- GT-100 Gateway ile bağlantılı.

### Hera+ Extensia PRO MINI (3 portlu modül — yeni)

- Elektrik işi gerektirmez — kullanıma hazır RJ11 geçmeli sistem.

### Hera+ Actor (benzersiz step motorlu aktüatör)

- Dijital hidronik balanslama ile entegre.
- Hera+ ve Hera Direct+ termostatlar + kablosuz yerden ısıtma şeritleri
  ile bireysel odaları kontrol etmek için.
- **RJ11 patch kablosu** ile aktüatöre bağlantı.
- **800 adıma kadar** benzersiz step motor + **patentli valf koruma**.
- **1000 stepli gearvalf** (fan-coil sürümünde belirtilmiş; aynı motor
  ailesi).
- GT-100 Gateway ile bağlantılı.
- **Yıllık elektrik tüketimi:**
  - Konvansiyonel aktüatör: **2,50–5,00 € / yıl**
  - blossom-ic Hera+ Actor: **0,30–0,50 € / yıl**

### Hera+ Thermostat (pilli oda termostatı)

- Dijital hidronik balanslama ile entegre.
- Kablosuz yerden ısıtma boruları ve Hera+ Actor üzerinden bireysel
  odaları kontrol eder.
- **Pil sürümü: 2× AA Lityum.**
- Oda sıcaklığı göstergesi doğrudan termostat üzerinde.
- Oda sıcaklığı yetersizliğini tespit eder.
- GT-100 Gateway ile bağlantılı.
- **Isıtma + soğutma için de uygundur** (ek "Heizen/Kühlen" ürün
  varyantı vardır).

### Hera Direct+ Thermostat (230 V oda termostatı)

- Dijital hidronik balanslama ile entegre.
- Kablosuz yerden ısıtma boruları ve Hera+ Actor üzerinden bireysel
  odaları kontrol eder.
- Tüm standart **sıva altı kutular için uygundur (Ø60 mm)**.
- Siyah ve beyaz renk seçenekleri.
- Oda sıcaklığı yetersizliğini tespit eder.
- GT-100 Gateway ile bağlantılı.
- Isıtma + soğutma için de uygundur (ek varyant kodlu).

## Fan-Coil kontrolü — Hera System

- Kablosuz BUS sistemi ile **ısıtma + soğutma**.
- Bir odada birkaç devrenin birbiriyle tam hidronik dengelenmesi.
- **Analog ve dijital sinyal işleme (0-10 V)**.
- **1, 2 ve 3 numaralı fan kademeleri** için bağlantı seçeneği.
- Pil ve 230 V termostatlar — güçlendirme için ideal çözüm.
- Detaylı bileşen bilgisi için ayrı "Fan-Coil Kontrol" dokümanına bakın.

## Akıllı ev uzantıları — Magelan ailesi

Blossom-ic gateway'e kablosuz bağlanan akıllı ev cihazları:

| Cihaz | İşlev |
|---|---|
| **Magelan Pompa Kontrol Cihazı** | Sirkülasyon / ısıtma pompası kontrolü |
| **Magelan App Socket (akıllı priz)** | Cihaz başına anahtarlama |
| **Magelan Sirene** | Sesli alarm (güvenlik + sızıntı) |
| **Magelan Panjur kontrolü** | Panjur / jaluzi kontrolü |
| **RP-100 Repeater** | Sinyal güçlendirici |
| **Magelan Sirkülasyon Pompaları Regülatörleri** | Sıcak su sirkülasyon |
| **Magelan Sızıntı Sensörü** | Su kaçağı algılama |
| **Magelan Main Water Protector** | Ana su hattı koruyucu (kaçak halinde otomatik vana kapama) |

## Yeni ürünler — Q4/2025

- **Magelan Hygro** — nem sensörü. Sürekli ölçümle kritik nem
  değerlerini **küf oluşumundan önce** algılar. Sınır değerler
  uygulama üzerinden ayarlanır.
- **Avalon S** — yeni kablosuz radyatör termostatı. Benzersiz **gövde
  üstü dokunmatik ekran** ve **2 patentli hareket sensörü**.
- **Gateway GT-200** — ek **SIM kart yuvası**; internet olmayan
  yerlerde bile güvenilir veri bağlantısı.

## Genel özet

- blossom-ic **dijital hidronik balanslamanın mucididir**; yedi yıllık
  yenilik ve başarı.
- Termostatlar birbiriyle bağlantılı çalıştığı için **tüm yasal
  gereklilikleri** karşılar (HLK Stuttgart ve ITG Dresden tarafından
  doğrulanmış).
- Boru şebekesine müdahale gerekmediği için **çalışma sırasında
  kolayca kurulur**; apartman binalarında bazı daireler eksik bile olsa
  daha sonra güçlendirilebilir.
- Pencere/yalıtım gibi binadaki değişiklikler mekanik dengelemede
  yeniden ayar gerektirir; blossom-ic **otomatik uyum sağlar**.
- Blossom-Sistemi geleceğe yöneliktir — oda sıcaklığı kontrolünün
  dijitalleştirilmesi için yasal zorunluluk gelirse, bu zaten blossom-ic
  ile uygulanmıştır.
- Mekanik hidronik balanslamaya göre **daha enerji verimli, daha uygun
  maliyetli ve zaman kazandıran** bir sistemdir.
