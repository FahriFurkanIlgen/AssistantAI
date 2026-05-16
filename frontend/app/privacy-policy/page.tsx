import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Gizlilik Politikası — AssistantAI",
  description:
    "AssistantAI AI sohbet asistanı kişisel verilerin işlenmesine ilişkin gizlilik politikası.",
};

const LAST_UPDATED = "16 Mayıs 2026";

export default function PrivacyPolicyPage() {
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
          Gizlilik Politikası
        </h1>
        <p className="text-relate-ash text-[15px] mb-12">
          Son güncelleme: {LAST_UPDATED}
        </p>

        <div className="space-y-10 text-[15px] leading-[1.75] text-relate-graphite">

          {/* 1 */}
          <section>
            <h2 className="text-[20px] font-semibold tracking-[-0.015em] text-relate-ink mb-4">
              1. Veri Sorumlusu
            </h2>
            <p>
              Bu Gizlilik Politikası, <strong>AssistantAI</strong> ("biz", "platform")
              tarafından işletilen yapay zeka destekli randevu ve sohbet asistanı
              hizmetine ilişkindir. Platform, işletme (Business) sahiplerine AI sohbet
              asistanı altyapısı sağlamakta; son kullanıcılar asistan üzerinden ilgili
              işletme ile iletişim kurmaktadır.
            </p>
            <p className="mt-3">
              Kişisel verileriniz 6698 sayılı{" "}
              <strong>Kişisel Verilerin Korunması Kanunu (KVKK)</strong> ve ilgili
              AB/Avrupa Ekonomik Alanı kullanıcıları için{" "}
              <strong>Genel Veri Koruma Tüzüğü (GDPR)</strong> kapsamında işlenmektedir.
            </p>
          </section>

          {/* 2 */}
          <section>
            <h2 className="text-[20px] font-semibold tracking-[-0.015em] text-relate-ink mb-4">
              2. Toplanan Veriler
            </h2>
            <p className="mb-3">Sohbet asistanını kullandığınızda aşağıdaki veriler işlenebilir:</p>
            <ul className="list-disc list-outside ml-5 space-y-2">
              <li>
                <strong>Sohbet içeriği:</strong> Asistana yazdığınız mesajlar ve
                yüklediğiniz görseller (randevu talebi, hizmet soruları vb.).
              </li>
              <li>
                <strong>Kimlik ve iletişim bilgileri:</strong> Randevu oluşturulması
                sırasında siz gönüllü olarak paylaşırsanız ad-soyad ve telefon numarası.
              </li>
              <li>
                <strong>Oturum verileri:</strong> Sohbet oturumunu tanımlamak için
                kullanılan anonim oturum kimliği (session ID); kişisel kimlik
                bilgisi içermez.
              </li>
              <li>
                <strong>Tercihler:</strong> Dil ve tema (aydınlık/karanlık mod)
                tercihiniz yalnızca tarayıcınızın yerel deposunda (localStorage)
                saklanır; sunucuya gönderilmez.
              </li>
            </ul>
          </section>

          {/* 3 */}
          <section>
            <h2 className="text-[20px] font-semibold tracking-[-0.015em] text-relate-ink mb-4">
              3. Verilerin İşlenme Amaçları
            </h2>
            <ul className="list-disc list-outside ml-5 space-y-2">
              <li>Yapay zeka asistanının size doğru ve kişiselleştirilmiş yanıtlar üretmesi.</li>
              <li>Randevu kaydı oluşturulması ve ilgili işletmenin size ulaşabilmesi.</li>
              <li>Hizmet kalitesinin iyileştirilmesi ve teknik hataların giderilmesi.</li>
              <li>Yasal yükümlülüklerin yerine getirilmesi.</li>
            </ul>
          </section>

          {/* 4 */}
          <section>
            <h2 className="text-[20px] font-semibold tracking-[-0.015em] text-relate-ink mb-4">
              4. Üçüncü Taraflarla Paylaşım
            </h2>
            <p className="mb-3">
              Verileriniz yalnızca aşağıdaki taraflarla ve amaçlarla paylaşılır:
            </p>
            <ul className="list-disc list-outside ml-5 space-y-2">
              <li>
                <strong>İlgili işletme:</strong> Randevu talebi oluşturduğunuzda ad-soyad
                ve telefon numaranız randevu kaydı için o işletmeyle paylaşılır.
              </li>
              <li>
                <strong>OpenAI (yapay zeka altyapısı):</strong> Sohbet mesajlarınız
                AI yanıtı üretmek amacıyla OpenAI API'ye iletilir. OpenAI'nin veri
                işleme politikası için{" "}
                <a
                  href="https://openai.com/policies/privacy-policy"
                  target="_blank"
                  rel="noreferrer"
                  className="text-relate-signal underline underline-offset-2 hover:opacity-80 transition-opacity"
                >
                  openai.com/policies/privacy-policy
                </a>{" "}
                adresini inceleyiniz.
              </li>
              <li>
                <strong>MongoDB Atlas (veritabanı):</strong> Randevu ve sohbet verileri
                şifreli MongoDB Atlas veritabanında saklanır.
              </li>
            </ul>
            <p className="mt-3">
              Verileriniz reklam amaçlı üçüncü taraflarla <strong>paylaşılmaz</strong> ve
              satılmaz.
            </p>
          </section>

          {/* 5 */}
          <section>
            <h2 className="text-[20px] font-semibold tracking-[-0.015em] text-relate-ink mb-4">
              5. Saklama Süresi
            </h2>
            <p>
              Sohbet geçmişi ve randevu verileri, ilgili işletmenin aktif üyeliği süresince
              ve akabinde yasal saklama yükümlülükleri çerçevesinde muhafaza edilir.
              Randevu amacıyla paylaşılan kişisel bilgiler randevu tarihinden itibaren
              en fazla <strong>2 yıl</strong> saklanır.
            </p>
          </section>

          {/* 6 */}
          <section>
            <h2 className="text-[20px] font-semibold tracking-[-0.015em] text-relate-ink mb-4">
              6. Haklarınız
            </h2>
            <p className="mb-3">
              KVKK md. 11 ve GDPR md. 15–22 kapsamında aşağıdaki haklara sahipsiniz:
            </p>
            <ul className="list-disc list-outside ml-5 space-y-2">
              <li>Kişisel verilerinizin işlenip işlenmediğini öğrenme.</li>
              <li>İşlenmişse bilgi talep etme.</li>
              <li>Eksik veya yanlış işlenen verilerin düzeltilmesini isteme.</li>
              <li>
                Belirli koşullar altında verilerinizin silinmesini veya yok edilmesini
                talep etme (unutulma hakkı).
              </li>
              <li>
                İşlemenin otomatik sistemler vasıtasıyla yapılması durumunda ortaya
                çıkan sonuca itiraz etme.
              </li>
              <li>Verilerinizin taşınabilirliğini talep etme (GDPR).</li>
            </ul>
            <p className="mt-3">
              Taleplerinizi{" "}
              <a
                href="mailto:privacy@assistantai.app"
                className="text-relate-signal underline underline-offset-2 hover:opacity-80 transition-opacity"
              >
                privacy@assistantai.app
              </a>{" "}
              adresine iletebilirsiniz. Talepler yasal süre içinde (en geç 30 gün)
              yanıtlanır.
            </p>
          </section>

          {/* 7 */}
          <section>
            <h2 className="text-[20px] font-semibold tracking-[-0.015em] text-relate-ink mb-4">
              7. Çerezler ve Yerel Depolama
            </h2>
            <p>
              Platform zorunlu çerez kullanmamaktadır. Dil ve tema tercihleriniz ile
              gizlilik bildirimi onayınız yalnızca tarayıcı <code className="bg-relate-wash px-1.5 py-0.5 rounded text-[13px]">localStorage</code>'ında
              tutulur; sunucuya aktarılmaz ve herhangi bir takip amacıyla kullanılmaz.
            </p>
          </section>

          {/* 8 */}
          <section>
            <h2 className="text-[20px] font-semibold tracking-[-0.015em] text-relate-ink mb-4">
              8. Güvenlik
            </h2>
            <p>
              Tüm veriler HTTPS üzerinden şifreli olarak iletilir. Depolama katmanında
              endüstri standardı güvenlik önlemleri uygulanmaktadır. Bununla birlikte,
              internet üzerinden hiçbir iletim yönteminin %100 güvenli olmadığını
              hatırlatırız.
            </p>
          </section>

          {/* 9 */}
          <section>
            <h2 className="text-[20px] font-semibold tracking-[-0.015em] text-relate-ink mb-4">
              9. Değişiklikler
            </h2>
            <p>
              Bu politika zaman zaman güncellenebilir. Önemli değişiklikler sayfanın
              üst kısmındaki "Son güncelleme" tarihi güncellenerek duyurulur.
              Sohbeti kullanmaya devam etmeniz güncel politikayı kabul ettiğiniz
              anlamına gelir.
            </p>
          </section>

          {/* 10 */}
          <section>
            <h2 className="text-[20px] font-semibold tracking-[-0.015em] text-relate-ink mb-4">
              10. İletişim
            </h2>
            <p>
              Gizlilik ile ilgili sorularınız veya talepleriniz için:
            </p>
            <address className="not-italic mt-3 space-y-1 text-relate-graphite">
              <p><strong>AssistantAI</strong></p>
              <p>
                E-posta:{" "}
                <a
                  href="mailto:privacy@assistantai.app"
                  className="text-relate-signal underline underline-offset-2 hover:opacity-80 transition-opacity"
                >
                  privacy@assistantai.app
                </a>
              </p>
            </address>
          </section>

        </div>
      </main>

      {/* ── Footer ── */}
      <footer className="border-t border-relate-border mt-16 py-8">
        <div className="max-w-relate mx-auto px-6 lg:px-10 text-center text-[13px] text-relate-ash">
          © {new Date().getFullYear()} AssistantAI. Tüm hakları saklıdır.
        </div>
      </footer>
    </div>
  );
}
