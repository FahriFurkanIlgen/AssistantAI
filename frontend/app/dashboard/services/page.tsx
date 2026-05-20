"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import toast from "react-hot-toast";

interface Service {
  name: string;
  name_tr: string;
  duration_minutes: number;
  price: number | null;
  description: string | null;
}

const EMPTY: Service = {
  name: "",
  name_tr: "",
  duration_minutes: 60,
  price: null,
  description: null,
};

export default function ServicesPage() {
  const [services, setServices] = useState<Service[]>([]);
  const [saving, setSaving] = useState(false);
  const [editIndex, setEditIndex] = useState<number | null>(null);
  const [form, setForm] = useState<Service>(EMPTY);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    api.getProfile().then((p) => setServices(p.services || []));
  }, []);

  const saveAll = async (updated: Service[]) => {
    setSaving(true);
    try {
      await api.updateProfile({ services: updated });
      setServices(updated);
      toast.success("Hizmetler kaydedildi");
    } catch {
      toast.error("Kayıt başarısız");
    } finally {
      setSaving(false);
    }
  };

  const openAdd = () => {
    setEditIndex(null);
    setForm(EMPTY);
    setShowForm(true);
  };

  const openEdit = (i: number) => {
    setEditIndex(i);
    setForm({ ...services[i] });
    setShowForm(true);
  };

  const handleSubmit = () => {
    if (!form.name_tr.trim()) {
      toast.error("Hizmet adı zorunludur");
      return;
    }
    const updated = [...services];
    const entry: Service = {
      ...form,
      name: form.name || form.name_tr, // fallback
      price: form.price ? Number(form.price) : null,
    };
    if (editIndex !== null) {
      updated[editIndex] = entry;
    } else {
      updated.push(entry);
    }
    saveAll(updated);
    setShowForm(false);
  };

  const handleDelete = (i: number) => {
    if (!confirm("Bu hizmeti silmek istediğinizden emin misiniz?")) return;
    const updated = services.filter((_, idx) => idx !== i);
    saveAll(updated);
  };

  return (
    <div className="p-4 sm:p-6 md:p-8 max-w-[720px]">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-semibold text-relate-ink">Hizmetler</h2>
          <p className="text-sm text-relate-graphite mt-1">
            AI asistan bu listeyi müşterilere sunar
          </p>
        </div>
        <button onClick={openAdd} className="btn-primary px-5 py-2.5 text-sm">
          + Hizmet Ekle
        </button>
      </div>

      {/* Form modal */}
      {showForm && (
        <div className="fixed inset-0 z-50 bg-black/30 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6">
            <h3 className="font-semibold text-relate-ink text-lg mb-5">
              {editIndex !== null ? "Hizmeti Düzenle" : "Yeni Hizmet"}
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Hizmet Adı (Türkçe) <span className="text-red-500">*</span>
                </label>
                <input
                  value={form.name_tr}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      name_tr: e.target.value,
                      name: e.target.value,
                    })
                  }
                  className="input-field"
                  placeholder="örn. Küçük Dövme"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Hizmet Adı (İngilizce)
                </label>
                <input
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  className="input-field"
                  placeholder="e.g. Small Tattoo"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Süre (dakika)
                  </label>
                  <input
                    type="number"
                    value={form.duration_minutes}
                    onChange={(e) =>
                      setForm({
                        ...form,
                        duration_minutes: parseInt(e.target.value) || 60,
                      })
                    }
                    className="input-field"
                    min={15}
                    step={15}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Fiyat (₺)
                  </label>
                  <input
                    type="number"
                    value={form.price ?? ""}
                    onChange={(e) =>
                      setForm({
                        ...form,
                        price: e.target.value
                          ? parseFloat(e.target.value)
                          : null,
                      })
                    }
                    className="input-field"
                    placeholder="—"
                    min={0}
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Açıklama
                </label>
                <textarea
                  value={form.description ?? ""}
                  onChange={(e) =>
                    setForm({ ...form, description: e.target.value || null })
                  }
                  className="input-field resize-none"
                  rows={2}
                  placeholder="Kısa açıklama (opsiyonel)"
                />
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button
                onClick={handleSubmit}
                disabled={saving}
                className="btn-primary flex-1 py-2.5"
              >
                {saving ? "Kaydediliyor..." : "Kaydet"}
              </button>
              <button
                onClick={() => setShowForm(false)}
                className="btn-secondary flex-1 py-2.5"
              >
                İptal
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Services list */}
      {services.length === 0 ? (
        <div className="text-center py-20 text-relate-graphite border border-dashed border-relate-border rounded-lg">
          <p className="text-4xl mb-3">✂️</p>
          <p className="font-medium text-relate-ink">Henüz hizmet eklenmemiş</p>
          <p className="text-sm mt-1">
            AI asistan genel randevu alır. Hizmet ekleyerek daha iyi yönlendirme
            yapın.
          </p>
          <button onClick={openAdd} className="btn-primary mt-5 px-6 py-2">
            İlk Hizmeti Ekle
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {services.map((s, i) => (
            <div key={i} className="card flex items-center gap-4">
              <div className="w-10 h-10 bg-relate-wash rounded-lg flex items-center justify-center text-lg shrink-0">
                ✂️
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-relate-ink truncate">
                  {s.name_tr}
                </p>
                <div className="flex gap-3 mt-1 text-xs text-relate-graphite">
                  <span>⏱ {s.duration_minutes} dk</span>
                  {s.price != null && (
                    <span>💰 {s.price.toLocaleString("tr-TR")} ₺</span>
                  )}
                  {s.description && (
                    <span className="truncate max-w-[200px]">
                      📝 {s.description}
                    </span>
                  )}
                </div>
              </div>
              <div className="flex gap-2 shrink-0">
                <button
                  onClick={() => openEdit(i)}
                  className="text-xs text-relate-signal hover:underline"
                >
                  Düzenle
                </button>
                <button
                  onClick={() => handleDelete(i)}
                  className="text-xs text-red-500 hover:underline"
                >
                  Sil
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
