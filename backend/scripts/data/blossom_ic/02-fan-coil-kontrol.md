# Fan Coil Kontrol — Ürün Bileşenleri

> Kaynak: Blossom-ic Fan Coil Kontrol resmi ürün dokümanı (TR).
> Hera ailesi Fan Coil bileşenleri ve Building Management System.

## Hera Fan Coil Termostat

- Çalışma gerilimi: **230 V**.
- Tüm donanımı dahili: **Modbus** ve **Bacnet** üzerinden 3. parti
  cihazlara veri akışı sağlar.
- **Dijital ekranlı**, akıllı binalardaki Fan Coil sistemlerinin
  manuel ve otomatik kontrolünü sağlar.
- Hareket sensörlerinden gelen veriyi okuyarak gece düşüş
  uygulayabilir veya ısıtmayı tamamen durdurabilir.
- Önceki Fan Coil termostatlarına göre daha çevre dostudur ve daha
  verimli çalışır:
  - **AC tüketim sürümünde %30**,
  - **DC tüketim sürümünde %18**'e kadar daha az enerji tüketir.
- AHU ve VRF veya VRV gibi merkezi soğutma/ısıtma sistemleriyle
  uyumludur.
- Akıllı binalarda **uzaktan kontrol** edilebilir.
- Aynı Hera Fan Coil Kontrol Box ile **birden fazla termostat
  bağlanarak büyük alanlar bölünebilir**.
- 0–10 V analog kontrol sinyaline ek olarak dijital modbus protokolü
  ile **tek kablodan birden fazla cihazla iletişim** kurarak kablo
  tasarrufu sağlar.

## Hera Fan Coil Kontrol Box (Kontrol Modülü)

- 230 V Hera Fan Coil termostat ile **RJ11** üzerinden bağlantı.
- Kontrol Box üzerinde merkezi sistemden gelen termostat sinyalini
  okumaya yarayan **0–10 V analog giriş** vardır; bu sayede özel BMS
  yazılımları **kontrol Box ile tüm sisteme uyum sağlayabilir**.
- Termostat ile gelen bilgi, kontrol box üzerinden **1000 stepli
  gearvalf** ile 2 veya 4 borulu Fan Coil sistemlerinde sirkülasyona
  dahil edilir.
- Üretim sırasında lehimle kapatılmış **CHANGE OVER** soketinin
  açılmasıyla termostat **NCT20 dış sıcaklık sensörü** ile birlikte
  çalışır → 2 borulu sistemler için tek setpoint kontrolü.
- Kontrol Box ve gearvalf üzerindeki step motor donanımı sayesinde
  6 V'a kadar uyumludur; ayrıca **konvertöre gerek kalmadan DC akım
  sistemlerinde de çalışır**.

## Hera+ Actor (step motorlu vana aktüatörü — fan-coil sürümü)

- Yıllarca süren AR-GE sonucu **patentli step motorlu valf**.
- **1000 step**, **M30 × 1,5 mm** vidalı bağlantı.
- Vananın açıklığına göre **otomatik vana açma/kapama koruması**.
- Düşük voltajda çalışabilir → **6 V'a kadar** uyumlu.
- **140 N** kapama kuvveti, sessiz çalışma profili.

## Blossom-ic Building Management System (BMS)

- **Wi-Fi**, **LAN kablo** veya **SIM kart** ile internete bağlanır.
- **Modbus / Bacnet bridge** olarak çalışır — mevcut BMS'lere veri
  kanalı sağlar.
- Binadaki tüm Fan Coil/termostat ünitelerinin **anlık verilerini**
  işletim programından takip etme ve uzaktan ayarlama.
- Sıcaklık eşitsizliği fark edildiğinde **dijital hidronik balanslama**
  ile **%30'a kadar tasarruf**.
- Akıllı ev cihazları ile kablosuz bağlantı:
  - Su kaçağı sensörü,
  - Panjur / perde kontrolü,
  - Alarm sistemi,
  - Pompa, kazan ve ısı pompası kontrolü.

### BMS Web Arayüzü (örnek dashboard)

- **Üç ana modül:** Gateway listesi, Avalon (radyatör) listesi,
  ısı/oda sayaçları.
- Sol panel: kat ve oda hiyerarşik ağacı.
  - Örn. *Floor 0 → Office → Kitchen, Living, Hall, Lavatory*; *Floor 1 →
    Reception*; *Floor 2 → Office (8 termostat); Floor 3, Roof, vb.*
- Sağ panel: bağlı **Avalon/Hera+** termostatlarının her biri için
  - Ad, ID, signal, mod (heating / cooling / heating&cooling),
    setpoint ve gerçek oda sıcaklığı,
  - **Auto/Zeit** veya **Manuell** programlama,
  - Min/Max **sıcaklık sınırlaması (6–30 °C)**.
- Üst bar: dil seçimi, kullanıcı menüsü, settings.

### Referans kurulum

- **IFSB Ravensburg** Building Management System dashboard'unda
  kurulu sistem (Almanya).
- Anlık veri takibi + uzaktan müdahale.

## Sistem mimarisinin kısa özeti

```
Internet  ─┬──  Building Management System (Wi-Fi / LAN / SIM)
           │
           └──  Modbus / Bacnet bridge  ──>  3. parti BMS
                          │
                          ▼
                 Hera Fan Coil Termostat (230V, RJ11)
                          │
                          ▼
                 Hera Fan Coil Kontrol Box  ──┬──  1000 stepli gearvalf (2/4 borulu)
                                              │
                                              └──  NCT20 dış sıcaklık sensörü (opsiyonel)
```

## Tipik sorulara yönelik anahtar gerçekler

- **"Hera Fan Coil 24 V mi 230 V mi?"** → Termostat 230 V; step motor
  modülü 6 V'a kadar düşürebildiği için DC sistemlerde konvertörsüz
  çalışır.
- **"2 borulu sistemde nasıl?"** → Lehim CHANGE OVER soketi açılır,
  NCT20 sensörü ile tek setpoint okumayla ısıtma/soğutma yönetilir.
- **"Birden fazla termostat aynı Fan Coil'i kontrol edebilir mi?"** →
  Evet, aynı Hera Fan Coil Kontrol Box'a birden çok termostat bağlanarak
  büyük alanlar bölünebilir.
- **"Mevcut BMS'imize entegre olur mu?"** → Evet, Modbus ve Bacnet
  destekli. 0–10 V analog giriş ile özel BMS yazılımları kontrol box ile
  iletişim kurabilir.
- **"Tasarruf vaadi nedir?"** → AC sürümünde %30, DC sürümünde %18
  enerji tasarrufu (termostat seviyesinde) + BMS dijital hidronik
  balanslama ile sistem geneli %30'a kadar ek tasarruf.
