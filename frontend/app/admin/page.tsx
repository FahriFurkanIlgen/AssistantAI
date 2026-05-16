"use client";
import { useState, useEffect, useCallback } from "react";
import toast from "react-hot-toast";
import { adminApi } from "@/lib/api";

/* ─── Types ─────────────────────────────────────────────── */
interface DemoRequest {
  id: string;
  name: string;
  business_name: string;
  sector: string;
  phone: string;
  email: string;
  city?: string;
  message?: string;
  status: "pending" | "contacted" | "converted" | "rejected";
  notes?: string;
  created_at: string;
}

interface Business {
  id: string;
  name: string;
  slug: string;
  email: string;
  sector?: string;
  city?: string;
  is_active: boolean;
  created_at: string;
}

/* ─── Helpers ────────────────────────────────────────────── */
const STATUS_LABELS: Record<string, string> = {
  pending: "Bekliyor",
  contacted: "İletişime Geçildi",
  converted: "Dönüştürüldü",
  rejected: "Reddedildi",
};

const STATUS_BADGE: Record<string, string> = {
  pending: "badge badge-amber",
  contacted: "badge badge-azure",
  converted: "badge badge-emerald",
  rejected: "badge badge-coral",
};

function fmt(dt: string) {
  return new Date(dt).toLocaleDateString("tr-TR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

/* ─── Main page ──────────────────────────────────────────── */
export default function AdminPage() {
  const [tab, setTab] = useState<"demos" | "businesses">("demos");
  const [adminKey, setAdminKey] = useState("");

  const [demos, setDemos] = useState<DemoRequest[]>([]);
  const [demosLoading, setDemosLoading] = useState(false);

  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [bizLoading, setBizLoading] = useState(false);

  // Inline edit state for demos
  const [editDemo, setEditDemo] = useState<Record<string, { status?: string; notes?: string }>>({});

  // New business modal
  const [showNewBiz, setShowNewBiz] = useState(false);
  const [newBiz, setNewBiz] = useState({
    name: "",
    slug: "",
    email: "",
    password: "",
    sector: "tattoo",
    city: "",
    phone: "",
  });

  // Edit business modal
  const [editBiz, setEditBiz] = useState<Business | null>(null);
  const [editBizPatch, setEditBizPatch] = useState<Record<string, string | boolean>>({});

  useEffect(() => {
    const k = localStorage.getItem("admin_key") || "";
    setAdminKey(k);
  }, []);

  /* ── Fetch demos ── */
  const loadDemos = useCallback(async () => {
    if (!adminKey) return;
    setDemosLoading(true);
    try {
      const data = await adminApi.getDemoRequests(adminKey);
      setDemos(data);
    } catch (e: any) {
      toast.error(e.response?.data?.detail || "Demo talepleri yüklenemedi");
    } finally {
      setDemosLoading(false);
    }
  }, [adminKey]);

  /* ── Fetch businesses ── */
  const loadBusinesses = useCallback(async () => {
    if (!adminKey) return;
    setBizLoading(true);
    try {
      const data = await adminApi.getBusinesses(adminKey);
      setBusinesses(data);
    } catch (e: any) {
      toast.error(e.response?.data?.detail || "İşletmeler yüklenemedi");
    } finally {
      setBizLoading(false);
    }
  }, [adminKey]);

  useEffect(() => {
    if (adminKey) {
      loadDemos();
      loadBusinesses();
    }
  }, [adminKey, loadDemos, loadBusinesses]);

  /* ── Update demo status/notes ── */
  const saveDemo = async (id: string) => {
    const patch = editDemo[id];
    if (!patch) return;
    try {
      await adminApi.updateDemoRequest(adminKey, id, patch);
      toast.success("Kaydedildi");
      setEditDemo((prev) => {
        const next = { ...prev };
        delete next[id];
        return next;
      });
      loadDemos();
    } catch (e: any) {
      toast.error(e.response?.data?.detail || "Kaydedilemedi");
    }
  };

  /* ── Delete demo ── */
  const deleteDemo = async (id: string) => {
    if (!confirm("Bu talebi silmek istediğinize emin misiniz?")) return;
    try {
      await adminApi.deleteDemoRequest(adminKey, id);
      toast.success("Silindi");
      loadDemos();
    } catch (e: any) {
      toast.error(e.response?.data?.detail || "Silinemedi");
    }
  };

  /* ── Impersonate ── */
  const impersonate = async (biz: Business) => {
    try {
      const data = await adminApi.impersonate(adminKey, biz.id);
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("business_slug", data.slug || biz.slug);
      localStorage.setItem("business_id", data.business_id || biz.id);
      localStorage.setItem("business_name", data.business_name || biz.name);
      toast.success(`${biz.name} olarak giriş yapılıyor…`);
      window.open("/dashboard", "_blank");
    } catch (e: any) {
      toast.error(e.response?.data?.detail || "Giriş yapılamadı");
    }
  };

  /* ── Create business ── */
  const createBusiness = async () => {
    try {
      await adminApi.createBusiness(adminKey, newBiz);
      toast.success("İşletme oluşturuldu");
      setShowNewBiz(false);
      setNewBiz({ name: "", slug: "", email: "", password: "", sector: "tattoo", city: "", phone: "" });
      loadBusinesses();
    } catch (e: any) {
      toast.error(e.response?.data?.detail || "Oluşturulamadı");
    }
  };

  /* ── Update business ── */
  const updateBusiness = async () => {
    if (!editBiz) return;
    try {
      await adminApi.updateBusiness(adminKey, editBiz.id, editBizPatch);
      toast.success("Güncellendi");
      setEditBiz(null);
      setEditBizPatch({});
      loadBusinesses();
    } catch (e: any) {
      toast.error(e.response?.data?.detail || "Güncellenemedi");
    }
  };

  /* ─────────────────────────────────────────────────────── */
  return (
    <main className="max-w-[1200px] mx-auto px-6 py-8">
      {/* Tabs */}
      <div className="flex items-center gap-1 mb-6 p-1 bg-relate-wash rounded-xl w-fit">
        {(["demos", "businesses"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-1.5 rounded-lg text-[14px] font-medium transition-colors ${
              tab === t
                ? "bg-white text-relate-ink shadow-relate-sm"
                : "text-relate-graphite hover:text-relate-ink"
            }`}
          >
            {t === "demos" ? "Demo Talepleri" : "İşletmeler"}
          </button>
        ))}
      </div>

      {/* ── Demo Requests Tab ── */}
      {tab === "demos" && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-[18px] text-relate-ink tracking-tight">
              Demo Talepleri
              <span className="ml-2 badge badge-azure">{demos.length}</span>
            </h2>
            <button onClick={loadDemos} className="btn-outline text-[13px]" disabled={demosLoading}>
              {demosLoading ? "Yükleniyor…" : "Yenile"}
            </button>
          </div>

          {demos.length === 0 && !demosLoading && (
            <p className="text-relate-graphite text-[14px]">Henüz demo talebi yok.</p>
          )}

          <div className="space-y-3">
            {demos.map((d) => {
              const patch = editDemo[d.id] || {};
              const currentStatus = patch.status ?? d.status;
              const currentNotes = patch.notes ?? d.notes ?? "";
              const dirty = editDemo[d.id] != null;
              return (
                <div key={d.id} className="card !p-5 flex flex-col gap-3">
                  <div className="flex flex-wrap items-start justify-between gap-2">
                    <div>
                      <p className="font-semibold text-[15px] text-relate-ink">{d.name}</p>
                      <p className="text-[13px] text-relate-graphite">{d.business_name} · {d.sector}</p>
                      <p className="text-[13px] text-relate-graphite">{d.phone} · {d.email}{d.city ? ` · ${d.city}` : ""}</p>
                      {d.message && (
                        <p className="text-[12px] text-relate-slate mt-1 italic">"{d.message}"</p>
                      )}
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      <span className={STATUS_BADGE[d.status]}>{STATUS_LABELS[d.status]}</span>
                      <span className="text-[11px] text-relate-slate">{fmt(d.created_at)}</span>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-end gap-3">
                    <div>
                      <label className="block text-[11px] text-relate-graphite mb-1">Durum</label>
                      <select
                        value={currentStatus}
                        onChange={(e) =>
                          setEditDemo((prev) => ({
                            ...prev,
                            [d.id]: { ...(prev[d.id] || {}), status: e.target.value },
                          }))
                        }
                        className="input-field !py-1 !text-[13px] w-44"
                      >
                        {Object.entries(STATUS_LABELS).map(([v, l]) => (
                          <option key={v} value={v}>{l}</option>
                        ))}
                      </select>
                    </div>
                    <div className="flex-1 min-w-[160px]">
                      <label className="block text-[11px] text-relate-graphite mb-1">Not</label>
                      <input
                        value={currentNotes}
                        onChange={(e) =>
                          setEditDemo((prev) => ({
                            ...prev,
                            [d.id]: { ...(prev[d.id] || {}), notes: e.target.value },
                          }))
                        }
                        placeholder="Dahili not…"
                        className="input-field !py-1 !text-[13px]"
                      />
                    </div>
                    {dirty && (
                      <button onClick={() => saveDemo(d.id)} className="btn-primary !py-1 text-[13px]">
                        Kaydet
                      </button>
                    )}
                    <button
                      onClick={() => deleteDemo(d.id)}
                      className="btn-ghost text-[13px] text-relate-coral hover:text-relate-coral/70"
                    >
                      Sil
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ── Businesses Tab ── */}
      {tab === "businesses" && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-[18px] text-relate-ink tracking-tight">
              İşletmeler
              <span className="ml-2 badge badge-azure">{businesses.length}</span>
            </h2>
            <div className="flex gap-2">
              <button onClick={loadBusinesses} className="btn-outline text-[13px]" disabled={bizLoading}>
                {bizLoading ? "Yükleniyor…" : "Yenile"}
              </button>
              <button onClick={() => setShowNewBiz(true)} className="btn-primary text-[13px]">
                + Yeni İşletme
              </button>
            </div>
          </div>

          {businesses.length === 0 && !bizLoading && (
            <p className="text-relate-graphite text-[14px]">Henüz işletme yok.</p>
          )}

          <div className="space-y-3">
            {businesses.map((b) => (
              <div key={b.id} className="card !p-5 flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="font-semibold text-[15px] text-relate-ink">{b.name}</p>
                  <p className="text-[13px] text-relate-graphite">
                    /{b.slug} · {b.email}
                    {b.sector ? ` · ${b.sector}` : ""}
                    {b.city ? ` · ${b.city}` : ""}
                  </p>
                  <p className="text-[11px] text-relate-slate mt-0.5">{fmt(b.created_at)}</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className={b.is_active ? "badge badge-emerald" : "badge badge-coral"}>
                    {b.is_active ? "Aktif" : "Pasif"}
                  </span>
                  <button
                    onClick={() => {
                      setEditBiz(b);
                      setEditBizPatch({});
                    }}
                    className="btn-outline text-[13px]"
                  >
                    Düzenle
                  </button>
                  <button
                    onClick={() => impersonate(b)}
                    className="btn-primary text-[13px]"
                  >
                    Giriş Yap
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── New Business Modal ── */}
      {showNewBiz && (
        <div className="fixed inset-0 bg-relate-ink/30 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="card-feature !p-7 w-full max-w-[440px]">
            <h3 className="font-semibold text-[18px] text-relate-ink mb-5">Yeni İşletme Ekle</h3>
            <div className="space-y-3">
              {(["name", "slug", "email", "password", "phone", "city"] as const).map((field) => (
                <div key={field}>
                  <label className="block text-[12px] font-medium text-relate-graphite mb-1 capitalize">{field}</label>
                  <input
                    type={field === "password" ? "password" : "text"}
                    value={newBiz[field]}
                    onChange={(e) => setNewBiz((p) => ({ ...p, [field]: e.target.value }))}
                    className="input-field !text-[13px]"
                  />
                </div>
              ))}
              <div>
                <label className="block text-[12px] font-medium text-relate-graphite mb-1">Sektör</label>
                <select
                  value={newBiz.sector}
                  onChange={(e) => setNewBiz((p) => ({ ...p, sector: e.target.value }))}
                  className="input-field !text-[13px]"
                >
                  <option value="tattoo">Dövme</option>
                  <option value="doctor">Klinik</option>
                  <option value="beauty">Güzellik</option>
                  <option value="general">Diğer</option>
                </select>
              </div>
            </div>
            <div className="flex gap-2 mt-5">
              <button onClick={createBusiness} className="btn-primary flex-1">Oluştur</button>
              <button onClick={() => setShowNewBiz(false)} className="btn-outline flex-1">İptal</button>
            </div>
          </div>
        </div>
      )}

      {/* ── Edit Business Modal ── */}
      {editBiz && (
        <div className="fixed inset-0 bg-relate-ink/30 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="card-feature !p-7 w-full max-w-[440px]">
            <h3 className="font-semibold text-[18px] text-relate-ink mb-1">{editBiz.name}</h3>
            <p className="text-[13px] text-relate-graphite mb-5">Değiştirmek istediğiniz alanları doldurun.</p>
            <div className="space-y-3">
              {(["name", "email", "city"] as const).map((field) => (
                <div key={field}>
                  <label className="block text-[12px] font-medium text-relate-graphite mb-1 capitalize">{field}</label>
                  <input
                    value={(editBizPatch[field] as string) ?? (editBiz as any)[field] ?? ""}
                    onChange={(e) => setEditBizPatch((p) => ({ ...p, [field]: e.target.value }))}
                    className="input-field !text-[13px]"
                  />
                </div>
              ))}
              <div>
                <label className="block text-[12px] font-medium text-relate-graphite mb-1">Yeni Şifre</label>
                <input
                  type="password"
                  value={(editBizPatch.password as string) ?? ""}
                  onChange={(e) => setEditBizPatch((p) => ({ ...p, password: e.target.value }))}
                  placeholder="Değiştirmek için girin"
                  className="input-field !text-[13px]"
                />
              </div>
              <div className="flex items-center gap-2 mt-1">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={(editBizPatch.is_active as boolean) ?? editBiz.is_active}
                  onChange={(e) => setEditBizPatch((p) => ({ ...p, is_active: e.target.checked }))}
                  className="w-4 h-4 accent-relate-signal"
                />
                <label htmlFor="is_active" className="text-[13px] text-relate-ink">Aktif</label>
              </div>
            </div>
            <div className="flex gap-2 mt-5">
              <button onClick={updateBusiness} className="btn-primary flex-1">Kaydet</button>
              <button onClick={() => { setEditBiz(null); setEditBizPatch({}); }} className="btn-outline flex-1">İptal</button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
