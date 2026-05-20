import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Kullanım Şartları — AssistantAI",
  description:
    "AssistantAI hizmetinin kullanımına ilişkin koşullar, sorumluluklar ve sınırlamalar.",
};

const LAST_UPDATED = "20 Mayıs 2026";

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-relate-canvas text-relate-ink">
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

      <main className="max-w-[780px] mx-auto px-6 lg:px-0 py-16">
        <h1 className="text-[32px] sm:text-[40px] font-semibold tracking-[-0.022em] text-relate-ink mb-3">
          Kullanım Şartları
        </h1>
        <p className="text-relate-ash text-[15px] mb-12">
          Son güncelleme: {LAST_UPDATED}
        </p>

        <div className="space-y-10 text-[15px] leading-[1.75] text-relate-graphite">
          <section>
            <h2 className="text-[20px] font-semibold tracking-[-0.015em] text-relate-ink mb-4">
              1. Taraflar ve Kapsam
            </h2>
            <p>
              Bu Kullanım Şartları (&quot;Şartlar&quot;), <strong>AssistantAI</strong>{" "}
              (&quot;Platform&quot;, &quot;biz&quot;) tarafından sunulan yapay zeka destekli
              sohbet ve randevu asistanı hizmetinin işletme (Business) sahipleri ile
              son kullanıcılar tarafından kullanımına ilişkin koşulları düzenler.
              Hizmete erişerek bu Şartları kabul etmiş sayılırsınız.
            </p>
          </section>

          <section>
            <h2 className="text-[20px] font-semibold tracking-[-0.015em] text-relate-ink mb-4">
              2. Hesap ve Yetkilendirme
            </h2>
            <ul className="list-disc pl-6 space-y-2">
              <li>
                İşletme hesabı açan kişi, ilgili işletme adına sözleşme yapmaya
                yetkili olduğunu beyan eder.
              </li>
              <li>
                Hesap bilgilerinin (e-posta, şifre, API anahtarları) gizliliğinden
                ve hesap üzerinden gerçekleştirilen tüm işlemlerden hesap sahibi
                sorumludur.
              </li>
              <li>
                Hesabınızın yetkisiz kullanıldığını fark ettiğinizde derhal{" "}
                <a href="mailto:support@assistantai.app" className="text-relate-signal underline underline-offset-2 hover:opacity-80">
                  support@assistantai.app
                </a>{" "}
                adresine bildirmelisiniz.
              </li>
            </ul>
          </section>

          <section>
            <h2 className="text-[20px] font-semibold tracking-[-0.015em] text-relate-ink mb-4">
              3. Kabul Edilebilir Kullanım
            </h2>
            <p>Platformu kullanırken aşağıdakileri yapmamayı kabul edersiniz:</p>
            <ul className="list-disc pl-6 space-y-2 mt-3">
              <li>Yasalara aykırı, yanıltıcı, dolandırıcılığa yönelik veya
                üçüncü kişilerin haklarını ihlal eden içerik üretmek.</li>
              <li>Hizmeti otomatik araçlarla (bot/scraper) makul sınırların
                üzerinde sorgulamak, tersine mühendislik yapmak.</li>
              <li>Spam, kitlesel mesajlaşma veya istenmeyen iletişim için
                kullanmak.</li>
              <li>Sağlık, hukuk veya finansal alanlarda lisanslı uzman tavsiyesi
                yerine geçecek şekilde son kullanıcıyı yanıltmak.</li>
              <li>Modelin güvenlik kontrollerini aşmaya yönelik prompt enjeksiyonu
                veya manipülasyon denemeleri.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-[20px] font-semibold tracking-[-0.015em] text-relate-ink mb-4">
              4. Müşteri İçeriği
            </h2>
            <p>
              İşletme, bilgi tabanına yüklediği belgeler, fiyat listeleri, hizmet
              bilgileri ve ayarlar üzerindeki tüm fikri mülkiyet haklarını korur.
              Platforma, bu içerikleri yalnızca hizmeti sağlamak amacıyla işleme,
              saklama ve son kullanıcıya iletme yönünde sınırlı, geri alınabilir
              lisans vermiş olursunuz.
            </p>
            <p className="mt-3">
              İşletme; yüklediği içeriğin doğruluğundan, güncelliğinden ve üçüncü
              kişilerin haklarını ihlal etmediğinden sorumludur.
            </p>
          </section>

          <section>
            <h2 className="text-[20px] font-semibold tracking-[-0.015em] text-relate-ink mb-4">
              5. AI Çıktılarının Niteliği
            </h2>
            <p>
              Asistanın ürettiği yanıtlar, yüklenen bilgi tabanı ve büyük dil
              modeli tarafından oluşturulur. Çıktılar yer yer eksik, hatalı veya
              güncel olmayabilir. Kritik kararlar (tıbbi, hukuki, finansal) için
              ilgili uzmana danışılmalıdır. AssistantAI, AI çıktılarının
              doğruluğuna ilişkin örtülü veya açık herhangi bir garanti vermez.
            </p>
          </section>

          <section>
            <h2 className="text-[20px] font-semibold tracking-[-0.015em] text-relate-ink mb-4">
              6. Ücretlendirme ve Plan
            </h2>
            <p>
              Aktif planınızın özellikleri, kullanım limitleri ve fiyatlandırması
              hesap panelinde görünür. Plan değişiklikleri yeni dönemden itibaren
              geçerli olur. Ödeme gecikmesi durumunda hizmet askıya alınabilir;
              30 günlük gecikme sonrası hesap kapatılabilir.
            </p>
          </section>

          <section>
            <h2 className="text-[20px] font-semibold tracking-[-0.015em] text-relate-ink mb-4">
              7. Hizmet Seviyesi
            </h2>
            <p>
              Hizmeti &quot;olduğu gibi&quot; sunarız; üretim ortamında %99,5 hedef
              uptime gözetiriz ancak kesintisiz çalışacağına ilişkin garanti
              vermeyiz. Planlı bakım pencereleri{" "}
              <Link href="/status" className="text-relate-signal underline underline-offset-2 hover:opacity-80">
                durum sayfasında
              </Link>{" "}
              duyurulur.
            </p>
          </section>

          <section>
            <h2 className="text-[20px] font-semibold tracking-[-0.015em] text-relate-ink mb-4">
              8. Sorumluluk Sınırlandırması
            </h2>
            <p>
              Uygulanan yasanın izin verdiği azami ölçüde, AssistantAI&apos;ın toplam
              sorumluluğu, talep tarihinden önceki 12 ay içinde ilgili işletmenin
              ödediği toplam ücret ile sınırlıdır. Dolaylı, arızi, özel veya cezai
              zararlardan (kâr kaybı, veri kaybı, itibar kaybı dahil) sorumlu
              tutulmayız.
            </p>
          </section>

          <section>
            <h2 className="text-[20px] font-semibold tracking-[-0.015em] text-relate-ink mb-4">
              9. Fesih
            </h2>
            <p>
              İşletme, dilediği zaman hesabını ayarlar üzerinden kapatabilir. Bu
              Şartları ihlal eden veya platforma zarar veren kullanımlarda
              AssistantAI hesabı önceden bildirimde bulunarak veya derhal askıya
              alma/sonlandırma hakkını saklı tutar. Fesihten sonra veri saklama
              süreleri{" "}
              <Link href="/privacy-policy" className="text-relate-signal underline underline-offset-2 hover:opacity-80">
                Gizlilik Politikası
              </Link>
              &apos;nda açıklanmıştır.
            </p>
          </section>

          <section>
            <h2 className="text-[20px] font-semibold tracking-[-0.015em] text-relate-ink mb-4">
              10. Değişiklikler
            </h2>
            <p>
              Bu Şartları zaman zaman güncelleyebiliriz. Esaslı değişiklikler
              e-posta veya hesap paneli üzerinden duyurulur. Bildirim sonrası
              hizmeti kullanmaya devam etmeniz güncel Şartları kabul ettiğiniz
              anlamına gelir.
            </p>
          </section>

          <section>
            <h2 className="text-[20px] font-semibold tracking-[-0.015em] text-relate-ink mb-4">
              11. Uygulanacak Hukuk
            </h2>
            <p>
              Bu Şartlar Türkiye Cumhuriyeti hukukuna tabidir. Doğacak
              uyuşmazlıklarda İstanbul Merkez (Çağlayan) Mahkemeleri ve İcra
              Daireleri yetkilidir.
            </p>
          </section>

          <section>
            <h2 className="text-[20px] font-semibold tracking-[-0.015em] text-relate-ink mb-4">
              12. İletişim
            </h2>
            <p>
              Sorularınız için{" "}
              <Link href="/contact" className="text-relate-signal underline underline-offset-2 hover:opacity-80">
                iletişim sayfası
              </Link>
              ,{" "}
              <a href="mailto:legal@assistantai.app" className="text-relate-signal underline underline-offset-2 hover:opacity-80">
                legal@assistantai.app
              </a>{" "}
              veya{" "}
              <a href="tel:+905454999667" className="text-relate-signal underline underline-offset-2 hover:opacity-80 num-mono">
                +90 545 499 96 67
              </a>
              .
            </p>
          </section>
        </div>
      </main>

      <footer className="border-t border-relate-border mt-16 py-8">
        <div className="max-w-relate mx-auto px-6 lg:px-10 text-center text-[13px] text-relate-ash">
          © {new Date().getFullYear()} AssistantAI. Tüm hakları saklıdır.
        </div>
      </footer>
    </div>
  );
}
