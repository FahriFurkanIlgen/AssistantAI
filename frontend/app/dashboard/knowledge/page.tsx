"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import toast from "react-hot-toast";

interface KnowledgeDoc {
  id: string;
  title: string;
  source_type: string;
  filename: string | null;
  chunk_count: number;
  char_count: number;
  created_at: string;
  updated_at: string;
}

interface SearchHit {
  score: number;
  text: string;
  document_id: string;
  document_title: string;
}

interface KnowledgeGap {
  id: string;
  question: string;
  language: string;
  best_score: number;
  hit_count: number;
  status: string;
  created_at: string;
  last_seen_at: string;
}

export default function KnowledgePage() {
  const [docs, setDocs] = useState<KnowledgeDoc[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // text form
  const [textTitle, setTextTitle] = useState("");
  const [textContent, setTextContent] = useState("");

  // file form
  const [fileTitle, setFileTitle] = useState("");
  const [file, setFile] = useState<File | null>(null);

  // viewer
  const [viewDoc, setViewDoc] = useState<{ title: string; content: string } | null>(null);

  // search test
  const [query, setQuery] = useState("");
  const [hits, setHits] = useState<SearchHit[] | null>(null);
  const [searching, setSearching] = useState(false);

  // gaps + facts
  const [gaps, setGaps] = useState<KnowledgeGap[]>([]);
  const [factsPreview, setFactsPreview] = useState<string>("");
  const [showFacts, setShowFacts] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const [data, gapsData, facts] = await Promise.all([
        api.listKnowledge(),
        api.listKnowledgeGaps(),
        api.getKnowledgeFactsPreview(),
      ]);
      setDocs(data.documents);
      setGaps(gapsData.gaps);
      setFactsPreview(facts.facts);
    } catch {
      toast.error("Belgeler yÃ¼klenemedi");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const submitText = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!textTitle.trim() || !textContent.trim()) {
      toast.error("BaÅŸlÄ±k ve iÃ§erik zorunludur");
      return;
    }
    setSaving(true);
    try {
      await api.createKnowledgeText(textTitle.trim(), textContent);
      toast.success("Belge eklendi ve dizine iÅŸlendi");
      setTextTitle("");
      setTextContent("");
      await load();
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail || "KayÄ±t baÅŸarÄ±sÄ±z";
      toast.error(msg);
    } finally {
      setSaving(false);
    }
  };

  const submitFile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      toast.error("Dosya seÃ§in");
      return;
    }
    setSaving(true);
    try {
      await api.uploadKnowledgeFile(file, fileTitle.trim() || undefined);
      toast.success("Dosya yÃ¼klendi");
      setFile(null);
      setFileTitle("");
      (document.getElementById("kb-file-input") as HTMLInputElement | null)?.value &&
        ((document.getElementById("kb-file-input") as HTMLInputElement).value = "");
      await load();
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail || "YÃ¼kleme baÅŸarÄ±sÄ±z";
      toast.error(msg);
    } finally {
      setSaving(false);
    }
  };

  const remove = async (id: string) => {
    if (!confirm("Bu belgeyi silmek istediÄŸinizden emin misiniz?")) return;
    try {
      await api.deleteKnowledgeDoc(id);
      toast.success("Belge silindi");
      setDocs((d) => d.filter((x) => x.id !== id));
    } catch {
      toast.error("Silinemedi");
    }
  };

  const openView = async (id: string) => {
    try {
      const d = await api.getKnowledgeDoc(id);
      setViewDoc({ title: d.title, content: d.raw_content });
    } catch {
      toast.error("Belge aÃ§Ä±lamadÄ±");
    }
  };

  const runSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setSearching(true);
    setHits(null);
    try {
      const data = await api.searchKnowledge(query.trim());
      setHits(data.results);
    } catch {
      toast.error("Arama baÅŸarÄ±sÄ±z");
    } finally {
      setSearching(false);
    }
  };

  const answerGap = (gap: KnowledgeGap) => {
    setTextTitle(`Cevap: ${gap.question.slice(0, 60)}`);
    setTextContent(`Soru: ${gap.question}\nCevap: `);
    // scroll to text form
    document
      .getElementById("kb-text-form")
      ?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const resolveGap = async (id: string) => {
    try {
      await api.updateKnowledgeGap(id, "resolved");
      setGaps((g) => g.filter((x) => x.id !== id));
      toast.success("Ã‡Ã¶zÃ¼ldÃ¼ olarak iÅŸaretlendi");
    } catch {
      toast.error("Ä°ÅŸlem baÅŸarÄ±sÄ±z");
    }
  };

  const dismissGap = async (id: string) => {
    try {
      await api.updateKnowledgeGap(id, "dismissed");
      setGaps((g) => g.filter((x) => x.id !== id));
    } catch {
      toast.error("Ä°ÅŸlem baÅŸarÄ±sÄ±z");
    }
  };

  return (
    <div className="p-8 max-w-[960px]">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-relate-ink">Bilgi BankasÄ±</h2>
        <p className="text-sm text-relate-graphite mt-1">
          AI asistanÄ±, mÃ¼ÅŸteri randevu dÄ±ÅŸÄ± bir ÅŸey sorduÄŸunda burada yÃ¼klediÄŸiniz
          belgelerden cevap Ã¼retir. SSS, fiyat listesi, iade politikasÄ±, bakÄ±m
          Ã¶nerileri, konum/park bilgisi gibi her ÅŸeyi ekleyebilirsiniz.
        </p>
      </div>

      {/* â”€â”€ AI'Ä±n bildiÄŸi gerÃ§ekler (live preview) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
      <div className="mb-6 bg-white rounded-2xl border border-relate-border">
        <button
          onClick={() => setShowFacts((s) => !s)}
          className="w-full flex items-center justify-between px-5 py-3 text-left"
        >
          <div>
            <p className="font-semibold text-relate-ink text-[14px]">
              ğŸ¤– AI'Ä±n iÅŸletmeniz hakkÄ±nda bildiÄŸi temel gerÃ§ekler
            </p>
            <p className="text-[12px] text-relate-graphite mt-0.5">
              Bu blok her sohbette otomatik olarak asistana verilir. Bilgiler
              ayarlarÄ±nÄ±zdan gelir (ad, adres, telefon, Ã§alÄ±ÅŸma saatleri,
              hizmetler/fiyatlar). Eksik bir ÅŸey varsa Ayarlar veya Hizmetler
              ekranÄ±ndan gÃ¼ncelleyin.
            </p>
          </div>
          <span className="text-relate-graphite text-sm shrink-0 ml-3">
            {showFacts ? "Gizle" : "GÃ¶ster"}
          </span>
        </button>
        {showFacts && (
          <pre className="px-5 pb-4 text-[12px] text-relate-ink whitespace-pre-wrap font-mono border-t border-relate-border pt-3">
            {factsPreview || "(HenÃ¼z veri yok)"}
          </pre>
        )}
      </div>

      {/* â”€â”€ Bilgi aÃ§Ä±klarÄ± (cevaplanamayan sorular) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
      {gaps.length > 0 && (
        <div className="mb-6 bg-amber-50 border border-amber-200 rounded-2xl p-5">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h3 className="font-semibold text-amber-900">
                âš ï¸ CevaplayamadÄ±ÄŸÄ± sorular ({gaps.length})
              </h3>
              <p className="text-[12px] text-amber-800 mt-0.5">
                AI bu sorulara gÃ¼venle cevap veremedi. Bilgi bankanÄ±za ekleyin,
                bir daha aynÄ± durum yaÅŸanmasÄ±n.
              </p>
            </div>
          </div>
          <div className="space-y-2">
            {gaps.map((g) => (
              <div
                key={g.id}
                className="flex items-center justify-between bg-white rounded-lg border border-amber-100 px-4 py-3"
              >
                <div className="min-w-0">
                  <p className="text-sm text-relate-ink truncate">
                    â€œ{g.question}â€
                  </p>
                  <p className="text-[11px] text-relate-graphite mt-0.5">
                    {g.hit_count}Ã— soruldu â€¢ en yÃ¼ksek benzerlik{" "}
                    {g.best_score.toFixed(2)} â€¢{" "}
                    {new Date(g.last_seen_at).toLocaleString("tr-TR")}
                  </p>
                </div>
                <div className="flex items-center gap-3 shrink-0 ml-3">
                  <button
                    onClick={() => answerGap(g)}
                    className="text-[13px] text-relate-signal hover:underline font-medium"
                  >
                    Cevap ekle
                  </button>
                  <button
                    onClick={() => resolveGap(g.id)}
                    className="text-[13px] text-emerald-700 hover:underline"
                  >
                    Ã‡Ã¶zÃ¼ldÃ¼
                  </button>
                  <button
                    onClick={() => dismissGap(g.id)}
                    className="text-[13px] text-relate-graphite hover:underline"
                  >
                    Yoksay
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* â”€â”€ Add forms â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
      <div className="grid md:grid-cols-2 gap-6 mb-10">
        {/* Text form */}
        <form
          id="kb-text-form"
          onSubmit={submitText}
          className="bg-white rounded-2xl p-5 border border-relate-border"
        >
          <h3 className="font-semibold text-relate-ink mb-4">Metin olarak ekle</h3>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                BaÅŸlÄ±k
              </label>
              <input
                value={textTitle}
                onChange={(e) => setTextTitle(e.target.value)}
                placeholder="Ã¶rn. SÄ±kÃ§a Sorulan Sorular"
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Ä°Ã§erik
              </label>
              <textarea
                value={textContent}
                onChange={(e) => setTextContent(e.target.value)}
                rows={8}
                placeholder={"Soru: Park yeriniz var mÄ±?\nCevap: Evet, binanÄ±n altÄ±nda Ã¼cretsiz otopark mevcut.\n\nÄ°ade politikasÄ±: ..."}
                className="input-field font-mono text-[13px]"
              />
              <p className="text-[11px] text-relate-graphite mt-1">
                {textContent.length.toLocaleString("tr-TR")} karakter
              </p>
            </div>
            <button
              type="submit"
              disabled={saving}
              className="btn-primary px-5 py-2.5 text-sm w-full"
            >
              {saving ? "Kaydediliyorâ€¦" : "Belgeyi ekle"}
            </button>
          </div>
        </form>

        {/* File form */}
        <form
          onSubmit={submitFile}
          className="bg-white rounded-2xl p-5 border border-relate-border"
        >
          <h3 className="font-semibold text-relate-ink mb-4">Dosya yÃ¼kle</h3>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                BaÅŸlÄ±k (opsiyonel)
              </label>
              <input
                value={fileTitle}
                onChange={(e) => setFileTitle(e.target.value)}
                placeholder="BoÅŸ bÄ±rakÄ±rsanÄ±z dosya adÄ± kullanÄ±lÄ±r"
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Dosya
              </label>
              <input
                id="kb-file-input"
                type="file"
                accept=".txt,.md,.pdf,.csv,text/plain,text/markdown,application/pdf"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="block w-full text-sm text-relate-graphite file:mr-3 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-relate-wash file:text-relate-ink hover:file:bg-gray-200"
              />
              <p className="text-[11px] text-relate-graphite mt-1">
                Desteklenenler: .txt, .md, .pdf, .csv â€¢ Maks 2 MB
              </p>
            </div>
            <button
              type="submit"
              disabled={saving || !file}
              className="btn-primary px-5 py-2.5 text-sm w-full"
            >
              {saving ? "YÃ¼kleniyorâ€¦" : "YÃ¼kle ve dizinle"}
            </button>
          </div>
        </form>
      </div>

      {/* â”€â”€ Document list â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
      <div className="mb-10">
        <h3 className="font-semibold text-relate-ink mb-3">YÃ¼klÃ¼ belgeler</h3>
        {loading ? (
          <p className="text-sm text-relate-graphite">YÃ¼kleniyorâ€¦</p>
        ) : docs.length === 0 ? (
          <div className="bg-white rounded-2xl p-6 border border-relate-border text-center">
            <p className="text-sm text-relate-graphite">
              HenÃ¼z belge yok. YukarÄ±daki formla ilk belgenizi ekleyin.
            </p>
          </div>
        ) : (
          <div className="bg-white rounded-2xl border border-relate-border divide-y divide-relate-border">
            {docs.map((d) => (
              <div
                key={d.id}
                className="flex items-center justify-between px-5 py-3"
              >
                <div className="min-w-0">
                  <p className="font-medium text-relate-ink truncate">
                    {d.title}
                  </p>
                  <p className="text-[12px] text-relate-graphite mt-0.5">
                    {d.source_type === "file" ? "ğŸ“ " : "ğŸ“ "}
                    {d.filename || "Metin"} â€¢ {d.chunk_count} parÃ§a â€¢{" "}
                    {d.char_count.toLocaleString("tr-TR")} karakter â€¢{" "}
                    {new Date(d.created_at).toLocaleDateString("tr-TR")}
                  </p>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <button
                    onClick={() => openView(d.id)}
                    className="text-[13px] text-relate-signal hover:underline"
                  >
                    GÃ¶rÃ¼ntÃ¼le
                  </button>
                  <button
                    onClick={() => remove(d.id)}
                    className="text-[13px] text-red-600 hover:underline"
                  >
                    Sil
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* â”€â”€ Search debug â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
      <div>
        <h3 className="font-semibold text-relate-ink mb-3">Arama testi</h3>
        <p className="text-sm text-relate-graphite mb-3">
          AI'Ä±n mÃ¼ÅŸteri sorusunu sorduÄŸunda gÃ¶receÄŸi pasajlarÄ± test edin.
        </p>
        <form onSubmit={runSearch} className="flex gap-2 mb-4">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ã¶rn. iade politikanÄ±z nedir?"
            className="input-field flex-1"
          />
          <button
            type="submit"
            disabled={searching || !query.trim()}
            className="btn-primary px-5 py-2.5 text-sm"
          >
            {searching ? "AranÄ±yorâ€¦" : "Ara"}
          </button>
        </form>
        {hits !== null && (
          <div className="space-y-2">
            {hits.length === 0 ? (
              <p className="text-sm text-relate-graphite">
                EÅŸleÅŸen pasaj bulunamadÄ±.
              </p>
            ) : (
              hits.map((h, i) => (
                <div
                  key={i}
                  className="bg-white rounded-2xl border border-relate-border p-4"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[12px] font-medium text-relate-graphite">
                      {h.document_title}
                    </span>
                    <span className="text-[11px] text-relate-graphite">
                      benzerlik {h.score.toFixed(3)}
                    </span>
                  </div>
                  <p className="text-sm text-relate-ink whitespace-pre-wrap">
                    {h.text}
                  </p>
                </div>
              ))
            )}
          </div>
        )}
      </div>

      {/* â”€â”€ Viewer modal â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
      {viewDoc && (
        <div
          className="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4"
          onClick={() => setViewDoc(null)}
        >
          <div
            className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[80vh] flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="px-5 py-4 border-b border-relate-border flex items-center justify-between">
              <h3 className="font-semibold text-relate-ink truncate">
                {viewDoc.title}
              </h3>
              <button
                onClick={() => setViewDoc(null)}
                className="text-relate-graphite hover:text-relate-ink text-xl leading-none"
              >
                Ã—
              </button>
            </div>
            <pre className="p-5 overflow-auto text-[13px] text-relate-ink whitespace-pre-wrap font-sans">
              {viewDoc.content}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
