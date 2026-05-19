import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "KVKK Aydınlatma Metni — AssistantAI",
  description:
    "6698 sayılı Kişisel Verilerin Korunması Kanunu kapsamında AssistantAI tarafından sunulan aydınlatma metni.",
};

const LAST_UPDATED = "19 Mayıs 2026";

export default function KvkkPage() {
  return (
    <div className="min-h-screen bg-relate-canvas text-relate-ink">
      {/* ── Nav ── */}
      <header className="sticky top-0 z-10 bg-relate-canvas/90 backdrop-blur-sm border-b border-relate-border">
        <div className="max-w-relate mx-auto px-6 lg:px-10 h-14 flex items-center justify-between">
          <Link
            href="/"
            className="text-[15px] font-medium text-relate-ink hover:text-relate-signal transition-colors"
          >
            AssistantAI
          </Link>
          <span className="text-[13px] text-relate-ash">
            Son güncelleme: {LAST_UPDATED}
          </span>
        </div>
      </header>

      {/* ── Content ── */}
      <main className="max-w-[780px] mx-auto px-6 lg:px-0 py-16">
        <h1 className="text-[32px] sm:text-[40px] font-semibold tracking-[-0.022em] text-relate-ink mb-3">
          KVKK Aydınlatma Metni
        </h1>
        <p className="text-relate-ash text-[15px] mb-12">
          Son güncelleme: {LAST_UPDATED}
        </p>

        <div className="space-y-10 text-[15px] leading-[1.75] text-relate-graphite">
          <section>
            <h2 className="text-[20px] font-semibold text-relate-ink mb-3 tracking-[-0.015em]">
              1. Veri Sorumlusunun Kimliği
            </h2>
            <p>
              6698 sayılı Kişisel Verilerin Korunması Kanunu (&ldquo;KVKK&rdquo;)
              uyarınca veri sorumlusu sıfatıyla AssistantAI
              (&ldquo;<strong>Şirket</strong>&rdquo;), aşağıda belirtilen
              kişisel verilerinizi işlemekte ve bu hususta sizi bilgilendirmek
              istemektedir.
            </p>
          </section>

          <section>
            <h2 className="text-[20px] font-semibold text-relate-ink mb-3 tracking-[-0.015em]">
              2. İşlenen Kişisel Veriler
            </h2>
            <p>
              Demo talebi veya kayıt başvurunuz sırasında bizimle paylaştığınız
              aşağıdaki kişisel verileriniz işlenmektedir:
            </p>
            <ul className="list-disc pl-6 mt-3 space-y-1.5">
              <li>
                <strong>Kimlik Bilgileri:</strong> Ad, soyad.
              </li>
              <li>
                <strong>İletişim Bilgileri:</strong> E-posta adresi, telefon
                numarası, ikamet edilen şehir.
              </li>
              <li>
                <strong>İşletme/Müşteri Bilgileri:</strong> İşletme adı,
                sektör bilgisi, talep ettiğiniz hizmete ilişkin notlar.
              </li>
              <li>
                <strong>Hesap Bilgileri:</strong> Üyelik sürecinde
                oluşturulan kullanıcı adı, şifrelenmiş parola.
              </li>
              <li>
                <strong>İşlem Güvenliği Bilgileri:</strong> IP adresi, oturum
                kayıtları, tarayıcı ve cihaz bilgisi.
              </li>
              <li>
                <strong>Sohbet İçeriği:</strong> Yapay zekâ asistanı ile
                yaptığınız yazışmalar, varsa gönderdiğiniz görseller ve sesli
                içerikler.
              </li>
            </ul>
          </section>

          <section>
            <h2 className="text-[20px] font-semibold text-relate-ink mb-3 tracking-[-0.015em]">
              3. Kişisel Verilerin İşlenme Amaçları
            </h2>
            <p>Kişisel verileriniz aşağıdaki amaçlarla işlenmektedir:</p>
            <ul className="list-disc pl-6 mt-3 space-y-1.5">
              <li>Demo talebinizin değerlendirilmesi ve sizinle iletişime geçilmesi,</li>
              <li>Hizmet sözleşmesinin kurulması ve ifası,</li>
              <li>Yapay zekâ destekli randevu ve müşteri iletişimi hizmetinin sunulması,</li>
              <li>Hesap güvenliğinin sağlanması, sahteciliğin önlenmesi,</li>
              <li>Yasal yükümlülüklerin yerine getirilmesi,</li>
              <li>İstatistiksel analiz ve hizmet kalitesinin iyileştirilmesi.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-[20px] font-semibold text-relate-ink mb-3 tracking-[-0.015em]">
              4. Kişisel Verilerin Aktarılması
            </h2>
            <p>
              Kişisel verileriniz; hizmetin sunulabilmesi amacıyla altyapı
              hizmeti aldığımız bulut sağlayıcılarına (sunucu barındırma, veri
              tabanı, e-posta gönderimi), yapay zekâ servis sağlayıcımız
              OpenAI&apos;a ve yasal yükümlülüklerimiz kapsamında talep
              edilmesi hâlinde yetkili kamu kurum ve kuruluşlarına
              aktarılabilir. Verileriniz pazarlama amaçlı üçüncü kişilerle
              <strong> paylaşılmaz, satılmaz, kiralanmaz</strong>.
            </p>
          </section>

          <section>
            <h2 className="text-[20px] font-semibold text-relate-ink mb-3 tracking-[-0.015em]">
              5. Kişisel Veri Toplamanın Yöntemi ve Hukuki Sebebi
            </h2>
            <p>
              Kişisel verileriniz; web sitemiz üzerinden doldurduğunuz formlar,
              sohbet asistanı ile gerçekleştirdiğiniz yazışmalar ve elektronik
              iletişim kanalları aracılığıyla otomatik veya kısmen otomatik
              yollarla toplanmaktadır. Verileriniz, KVKK&apos;nın 5. ve 6.
              maddelerinde belirtilen; (i) sözleşmenin kurulması ve ifası
              için gerekli olması, (ii) hukuki yükümlülüğümüzün yerine
              getirilmesi, (iii) meşru menfaatimiz için zorunlu olması ve
              (iv) açık rızanızın bulunması hukuki sebeplerine dayanılarak
              işlenmektedir.
            </p>
          </section>

          <section>
            <h2 className="text-[20px] font-semibold text-relate-ink mb-3 tracking-[-0.015em]">
              6. Kişisel Verilerin Saklama Süresi
            </h2>
            <p>
              Kişisel verileriniz, işlendikleri amaç için gerekli olan süre
              kadar muhafaza edilir; ilgili mevzuatta öngörülen sürelere veya
              hukuki uyuşmazlıklarda zamanaşımı süreleri sona erdiğinde
              imha edilir, anonim hâle getirilir veya silinir.
            </p>
          </section>

          <section>
            <h2 className="text-[20px] font-semibold text-relate-ink mb-3 tracking-[-0.015em]">
              7. KVKK&apos;nın 11. Maddesi Kapsamındaki Haklarınız
            </h2>
            <p>İlgili kişi olarak aşağıdaki haklara sahipsiniz:</p>
            <ul className="list-disc pl-6 mt-3 space-y-1.5">
              <li>Kişisel verilerinizin işlenip işlenmediğini öğrenme,</li>
              <li>İşlenmişse buna ilişkin bilgi talep etme,</li>
              <li>İşlenme amacını ve amacına uygun kullanılıp kullanılmadığını öğrenme,</li>
              <li>Yurt içinde veya yurt dışında aktarıldığı üçüncü kişileri bilme,</li>
              <li>Eksik veya yanlış işlenmiş ise düzeltilmesini isteme,</li>
              <li>KVKK&apos;da öngörülen şartlar çerçevesinde silinmesini veya yok edilmesini isteme,</li>
              <li>Aktarıldığı üçüncü kişilere bu işlemlerin bildirilmesini isteme,</li>
              <li>Otomatik sistemlerle analiz sonucu aleyhinize bir sonuç doğmasına itiraz etme,</li>
              <li>Kanuna aykırı işlenmesi sebebiyle zarara uğramanız hâlinde zararın giderilmesini talep etme.</li>
            </ul>
            <p className="mt-3">
              Bu kapsamdaki taleplerinizi{" "}
              <a
                href="mailto:kvkk@assistantai.app"
                className="text-relate-signal hover:opacity-70 transition-opacity"
              >
                kvkk@assistantai.app
              </a>{" "}
              adresine iletebilirsiniz.
            </p>
          </section>

          <section>
            <h2 className="text-[20px] font-semibold text-relate-ink mb-3 tracking-[-0.015em]">
              8. Onay
            </h2>
            <p>
              İşbu aydınlatma metnini okuduğunuzu, anladığınızı ve kişisel
              verilerinizin yukarıda belirtilen amaçlar doğrultusunda
              işlenmesine açık rızanız bulunduğunu, kayıt / demo talep formunu
              gönderdiğinizde kabul etmiş sayılırsınız.
            </p>
          </section>

          <div className="pt-6 border-t border-relate-border">
            <Link
              href="/register"
              className="text-[14px] text-relate-signal hover:opacity-70 transition-opacity"
            >
              ← Kayıt sayfasına dön
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
