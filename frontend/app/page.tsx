import Link from "next/link";

export default function HomePage() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-brand-50 via-white to-purple-50">
      <div className="max-w-3xl mx-auto text-center px-6 py-20">
        {/* Logo / Brand */}
        <div className="inline-flex items-center justify-center w-16 h-16 bg-brand-600 rounded-2xl mb-8 shadow-lg">
          <span className="text-white text-3xl">🤖</span>
        </div>

        <h1 className="text-5xl font-bold text-gray-900 mb-4">
          Assistant<span className="text-brand-600">AI</span>
        </h1>
        <p className="text-xl text-gray-600 mb-2">
          Yapay zeka destekli akıllı randevu sistemi
        </p>
        <p className="text-gray-500 mb-10">
          Müşterileriniz 7/24 randevu alabilsin. Google Takvim ile senkronize,
          tamamen otomatik.
        </p>

        {/* Sector badges */}
        <div className="flex flex-wrap justify-center gap-3 mb-12">
          {[
            "🎨 Dövme Stüdyoları",
            "🏥 Klinikler",
            "💅 Güzellik Merkezleri",
            "✂️ Kuaförler",
          ].map((sector) => (
            <span
              key={sector}
              className="px-4 py-2 bg-white border border-gray-200 rounded-full text-sm font-medium text-gray-700 shadow-sm"
            >
              {sector}
            </span>
          ))}
        </div>

        {/* CTA */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/register"
            className="btn-primary text-base px-8 py-3 rounded-xl shadow-md"
          >
            Ücretsiz Başla
          </Link>
          <Link
            href="/login"
            className="btn-secondary text-base px-8 py-3 rounded-xl"
          >
            Giriş Yap
          </Link>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mt-20">
          {[
            {
              icon: "🤖",
              title: "GPT-4o Asistan",
              desc: "Müşterileri anlayan, Türkçe ve İngilizce konuşabilen zeki chatbot",
            },
            {
              icon: "📅",
              title: "Google Takvim",
              desc: "Randevular otomatik takvime eklenir, çakışma olmaz",
            },
            {
              icon: "📊",
              title: "Dashboard",
              desc: "Tüm randevularınızı tek ekrandan yönetin",
            },
          ].map((f) => (
            <div
              key={f.title}
              className="card text-center hover:shadow-md transition-shadow"
            >
              <div className="text-3xl mb-3">{f.icon}</div>
              <h3 className="font-semibold text-gray-900 mb-1">{f.title}</h3>
              <p className="text-sm text-gray-500">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
