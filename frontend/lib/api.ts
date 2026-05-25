import axios from "axios";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const axiosInstance = axios.create({ baseURL: BASE_URL });

// Attach token automatically
axiosInstance.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Redirect to login on 401
axiosInstance.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  },
);

// ── Restaurant types ─────────────────────────────────────────────────────────
export interface RestaurantTable {
  id: string;
  number: string;
  name?: string | null;
  capacity: number;
  section: string;
  shape: string;
  is_active: boolean;
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface DiningShift {
  id: string;
  name: string;
  start_time: string;
  end_time: string;
  is_active: boolean;
  days: string[];
}

export interface Reservation {
  id: string;
  business_id: string;
  table_id: string;
  table_ids: string[];
  table_number: string;
  table_section: string;
  combined_capacity?: number | null;
  customer_name: string;
  customer_phone: string;
  customer_email?: string | null;
  party_size: number;
  date: string;
  shift_name: string;
  shift_start: string;
  shift_end: string;
  special_requests?: string | null;
  notes?: string | null;
  status: "confirmed" | "seated" | "completed" | "cancelled" | "no_show";
  channel: string;
  created_at: string;
}

export const api = {
  register: async (data: {
    name: string;
    slug: string;
    email: string;
    password: string;
    sector: string;
    city?: string;
    phone?: string;
  }) => (await axiosInstance.post("/api/auth/register", data)).data,

  login: async (email: string, password: string) => {
    const form = new URLSearchParams();
    form.append("username", email);
    form.append("password", password);
    return (
      await axiosInstance.post("/api/auth/login", form, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      })
    ).data;
  },

  getMe: async () => (await axiosInstance.get("/api/auth/me")).data,

  // Business
  getProfile: async () =>
    (await axiosInstance.get("/api/business/profile")).data,
  updateProfile: async (data: Record<string, unknown>) =>
    (await axiosInstance.patch("/api/business/profile", data)).data,

  // Appointments
  getAppointments: async (params?: {
    start?: string;
    end?: string;
    status?: string;
  }) => (await axiosInstance.get("/api/appointments/", { params })).data,

  getAppointmentStats: async () =>
    (await axiosInstance.get("/api/appointments/stats")).data,

  cancelAppointment: async (id: string) =>
    (await axiosInstance.delete(`/api/appointments/${id}`)).data,

  updateAppointmentStatus: async (id: string, status: string) =>
    (await axiosInstance.patch(`/api/appointments/${id}/status`, { status }))
      .data,

  // Chat
  sendMessage: async (
    businessSlug: string,
    message: string,
    sessionId?: string,
    language?: string,
    imageBase64?: string,
    imageUrl?: string,
  ) =>
    (
      await axiosInstance.post(`/api/chat/${businessSlug}`, {
        message,
        session_id: sessionId,
        language: language || "tr",
        image_base64: imageBase64,
        image_url: imageUrl,
      })
    ).data,

  getWelcome: async (businessSlug: string, lang = "tr") =>
    (
      await axiosInstance.get(`/api/chat/${businessSlug}/welcome`, {
        params: { lang },
      })
    ).data,

  getPortfolio: async (businessSlug: string) =>
    (await axiosInstance.get(`/api/chat/${businessSlug}/portfolio`)).data,

  synthesizeSpeech: async (
    businessSlug: string,
    text: string,
    voice = "nova",
  ): Promise<string> => {
    const resp = await axiosInstance.post(
      `/api/chat/${businessSlug}/tts`,
      { text, voice },
      { responseType: "blob" },
    );
    return URL.createObjectURL(resp.data as Blob);
  },

  transcribeAudio: async (
    businessSlug: string,
    blob: Blob,
    language = "tr",
  ): Promise<{ text: string; language: string }> => {
    const form = new FormData();
    // .webm is the typical MediaRecorder output in Chrome/Firefox
    form.append("audio", blob, "clip.webm");
    form.append("language", language);
    const resp = await axiosInstance.post(
      `/api/chat/${businessSlug}/stt`,
      form,
      { headers: { "Content-Type": "multipart/form-data" } },
    );
    return resp.data;
  },

  getPublicBusiness: async (slug: string) =>
    (await axiosInstance.get(`/api/business/public/${slug}`)).data,

  // Google Calendar
  connectGoogle: async () =>
    (await axiosInstance.get("/api/calendar/connect")).data,

  disconnectGoogle: async () =>
    (await axiosInstance.delete("/api/calendar/disconnect")).data,

  // WhatsApp Cloud API bridge
  getWhatsAppStatus: async (): Promise<{
    enabled: boolean;
    phone_number_id?: string | null;
    display_phone?: string | null;
    access_token_preview?: string | null;
    verify_token_set?: boolean;
    webhook_path?: string;
  }> => (await axiosInstance.get("/api/whatsapp/status")).data,

  sendWhatsAppTest: async (to: string, text?: string) =>
    (await axiosInstance.post("/api/whatsapp/test-send", { to, text })).data,

  // Instagram Graph API + Messenger bridge
  getInstagramStatus: async (): Promise<{
    enabled: boolean;
    ig_user_id?: string | null;
    page_id?: string | null;
    ig_username?: string | null;
    access_token_preview?: string | null;
    verify_token_set?: boolean;
    app_secret_set?: boolean;
    webhook_path?: string;
  }> => (await axiosInstance.get("/api/instagram/status")).data,

  sendInstagramTest: async (to: string, text?: string) =>
    (await axiosInstance.post("/api/instagram/test-send", { to, text })).data,

  refreshInstagramMedia: async () =>
    (await axiosInstance.post("/api/instagram/refresh-media")).data,

  getInstagramPortfolio: async (slug: string, limit = 12) =>
    (await axiosInstance.get(`/api/instagram/${slug}/portfolio`, { params: { limit } })).data,

  startInstagramOAuth: async (): Promise<{ authorize_url: string }> =>
    (await axiosInstance.post("/api/instagram/oauth/start")).data,

  // Staff
  getStaff: async () => (await axiosInstance.get("/api/staff/")).data,

  createStaff: async (data: {
    name: string;
    email: string;
    password: string;
    phone?: string;
    bio?: string;
    service_names?: string[];
    working_schedule?: Record<string, unknown>;
  }) => (await axiosInstance.post("/api/staff/", data)).data,

  updateStaff: async (
    id: string,
    data: {
      name?: string;
      phone?: string;
      bio?: string;
      service_names?: string[];
      is_active?: boolean;
    },
  ) => (await axiosInstance.patch(`/api/staff/${id}`, data)).data,

  deactivateStaff: async (id: string) =>
    (await axiosInstance.delete(`/api/staff/${id}`)).data,

  updateStaffSchedule: async (id: string, schedule: Record<string, unknown>) =>
    (await axiosInstance.patch(`/api/staff/${id}/schedule`, schedule)).data,

  connectStaffGoogle: async (staffId: string) =>
    (await axiosInstance.get(`/api/staff/${staffId}/calendar/connect`)).data,

  disconnectStaffGoogle: async (staffId: string) =>
    (await axiosInstance.delete(`/api/staff/${staffId}/calendar`)).data,

  staffLogin: async (email: string, password: string) =>
    (await axiosInstance.post("/api/auth/staff/login", { email, password })).data,

  // Demo Request (public)
  submitDemoRequest: async (data: {
    name: string;
    business_name: string;
    sector: string;
    phone: string;
    email: string;
    city?: string;
    message?: string;
  }) => (await axiosInstance.post("/api/demo-request", data)).data,

  // Knowledge base (RAG)
  listKnowledge: async () =>
    (await axiosInstance.get("/api/knowledge/")).data as {
      documents: Array<{
        id: string;
        title: string;
        source_type: string;
        filename: string | null;
        chunk_count: number;
        char_count: number;
        created_at: string;
        updated_at: string;
      }>;
    },

  getKnowledgeDoc: async (id: string) =>
    (await axiosInstance.get(`/api/knowledge/${id}`)).data,

  createKnowledgeText: async (title: string, content: string) =>
    (await axiosInstance.post("/api/knowledge/text", { title, content })).data,

  uploadKnowledgeFile: async (file: File, title?: string) => {
    const fd = new FormData();
    fd.append("file", file);
    if (title) fd.append("title", title);
    return (
      await axiosInstance.post("/api/knowledge/file", fd, {
        headers: { "Content-Type": "multipart/form-data" },
      })
    ).data;
  },

  deleteKnowledgeDoc: async (id: string) =>
    (await axiosInstance.delete(`/api/knowledge/${id}`)).data,

  searchKnowledge: async (query: string, top_k = 4) =>
    (await axiosInstance.post("/api/knowledge/search", { query, top_k })).data as {
      results: Array<{
        score: number;
        text: string;
        document_id: string;
        document_title: string;
      }>;
    },

  listKnowledgeGaps: async (status?: string) =>
    (
      await axiosInstance.get("/api/knowledge/gaps/list", {
        params: status ? { status } : undefined,
      })
    ).data as {
      gaps: Array<{
        id: string;
        question: string;
        language: string;
        best_score: number;
        hit_count: number;
        status: string;
        created_at: string;
        last_seen_at: string;
      }>;
    },

  updateKnowledgeGap: async (id: string, status: "open" | "resolved" | "dismissed") =>
    (await axiosInstance.patch(`/api/knowledge/gaps/${id}`, { status })).data,

  deleteKnowledgeGap: async (id: string) =>
    (await axiosInstance.delete(`/api/knowledge/gaps/${id}`)).data,

  getKnowledgeFactsPreview: async () =>
    (await axiosInstance.get("/api/knowledge/facts/preview")).data as { facts: string },

  // Customer memory layer
  listCustomers: async () =>
    (await axiosInstance.get("/api/customers/")).data as {
      customers: Array<{
        id: string;
        name: string;
        phone: string;
        phone_display: string | null;
        email: string | null;
        language_preference: string;
        total_appointments: number;
        total_conversations: number;
        tags: string[];
        last_seen_at: string | null;
        last_summary_at: string | null;
        created_at: string;
      }>;
    },

  getCustomerByPhone: async (phone: string) =>
    (await axiosInstance.get(`/api/customers/by-phone/${encodeURIComponent(phone)}`))
      .data as {
      customer: null | {
        id: string;
        name: string;
        phone: string;
        phone_display: string | null;
        email: string | null;
        language_preference: string;
        total_appointments: number;
        total_conversations: number;
        tags: string[];
        memory_summary: string | null;
        preferences: {
          preferred_staff: string | null;
          preferred_staff_id: string | null;
          preferred_times: string | null;
          favorite_services: string[];
          allergies: string | null;
          notes: string | null;
        };
        last_seen_at: string | null;
        last_summary_at: string | null;
        created_at: string;
      };
      recent_appointments?: Array<{
        id: string;
        service_name: string;
        start_time: string;
        status: string;
      }>;
    },

  updateCustomer: async (
    id: string,
    data: {
      name?: string;
      email?: string | null;
      language_preference?: string;
      tags?: string[];
      memory_summary?: string | null;
      preferences?: {
        preferred_staff?: string | null;
        preferred_staff_id?: string | null;
        preferred_times?: string | null;
        favorite_services?: string[];
        allergies?: string | null;
        notes?: string | null;
      };
    },
  ) => (await axiosInstance.patch(`/api/customers/${id}`, data)).data,

  resetCustomerMemory: async (id: string) =>
    (await axiosInstance.delete(`/api/customers/${id}/memory`)).data,

  // ── Restaurant: tables & shifts ─────────────────────────────────────────
  getRestaurantConfig: async () =>
    (await axiosInstance.get("/api/tables/restaurant-config")).data,

  updateRestaurantConfig: async (data: {
    enabled?: boolean;
    reservation_duration?: number;
    max_party_size?: number;
    reservation_window_days?: number;
  }) => (await axiosInstance.patch("/api/tables/restaurant-config", data)).data,

  getTables: async () => (await axiosInstance.get("/api/tables")).data as RestaurantTable[],

  createTable: async (data: Omit<RestaurantTable, "id">) =>
    (await axiosInstance.post("/api/tables", data)).data as RestaurantTable,

  updateTable: async (id: string, data: Omit<RestaurantTable, "id">) =>
    (await axiosInstance.patch(`/api/tables/${id}`, data)).data as RestaurantTable,

  deleteTable: async (id: string) =>
    (await axiosInstance.delete(`/api/tables/${id}`)).data,

  saveTableLayout: async (items: { id: string; x: number; y: number; width: number; height: number }[]) =>
    (await axiosInstance.post("/api/tables/layout", items)).data,

  getShifts: async () => (await axiosInstance.get("/api/tables/shifts")).data as DiningShift[],

  createShift: async (data: Omit<DiningShift, "id">) =>
    (await axiosInstance.post("/api/tables/shifts", data)).data as DiningShift,

  updateShift: async (id: string, data: Omit<DiningShift, "id">) =>
    (await axiosInstance.patch(`/api/tables/shifts/${id}`, data)).data as DiningShift,

  deleteShift: async (id: string) =>
    (await axiosInstance.delete(`/api/tables/shifts/${id}`)).data,

  // ── Restaurant: reservations ─────────────────────────────────────────────
  getReservations: async (params?: { date?: string; shift_name?: string; status?: string }) =>
    (await axiosInstance.get("/api/reservations", { params })).data as Reservation[],

  createReservation: async (data: {
    table_id: string;
    customer_name: string;
    customer_phone: string;
    customer_email?: string;
    party_size: number;
    date: string;
    shift_name: string;
    shift_start: string;
    shift_end: string;
    special_requests?: string;
    notes?: string;
  }) => (await axiosInstance.post("/api/reservations", data)).data as Reservation,

  updateReservation: async (id: string, data: { status?: string; notes?: string; special_requests?: string; table_id?: string; table_number?: string; table_section?: string }) =>
    (await axiosInstance.patch(`/api/reservations/${id}`, data)).data as Reservation,

  deleteReservation: async (id: string) =>
    (await axiosInstance.delete(`/api/reservations/${id}`)).data,

  getReservationStats: async (date?: string) =>
    (await axiosInstance.get("/api/reservations/stats/summary", { params: date ? { date } : undefined })).data,
};

// ── Public (unauthenticated) reservation API ─────────────────────────────────
export const publicReservationApi = {
  getConfig: async (slug: string) =>
    (await axios.get(`${BASE_URL}/api/reservations/public/${slug}/config`)).data as {
      business_name: string;
      logo_url?: string | null;
      phone?: string | null;
      address?: string | null;
      shifts: { id: string; name: string; start_time: string; end_time: string; days: string[] }[];
      sections: string[];
      max_party_size: number;
      reservation_window_days: number;
    },

  getAvailability: async (slug: string, params: { date: string; shift_name: string; party_size: number; section?: string }) =>
    (await axios.get(`${BASE_URL}/api/reservations/public/${slug}/availability`, { params })).data as {
      shift_start: string;
      shift_end: string;
      available_tables: { id: string; number: string; capacity: number; section: string; shape: string }[];
      combinations: {
        tables: { id: string; number: string; capacity: number; section: string; shape: string }[];
        combined_capacity: number;
        table_ids: string[];
        label: string;
      }[];
    },

  createReservation: async (slug: string, data: {
    table_id?: string;
    table_ids?: string[];
    customer_name: string;
    customer_phone: string;
    customer_email?: string;
    party_size: number;
    date: string;
    shift_name: string;
    shift_start: string;
    shift_end: string;
    special_requests?: string;
  }) => (await axios.post(`${BASE_URL}/api/reservations/public/${slug}`, data)).data as Reservation,
};

export const adminApi = {
  getDemoRequests: async (key: string) =>
    (await axios.get(`${BASE_URL}/api/admin/demo-requests`, { headers: { "x-admin-key": key } })).data,

  updateDemoRequest: async (key: string, id: string, data: { status?: string; notes?: string }) =>
    (await axios.patch(`${BASE_URL}/api/admin/demo-requests/${id}`, data, { headers: { "x-admin-key": key } })).data,

  deleteDemoRequest: async (key: string, id: string) =>
    (await axios.delete(`${BASE_URL}/api/admin/demo-requests/${id}`, { headers: { "x-admin-key": key } })).data,

  getBusinesses: async (key: string) =>
    (await axios.get(`${BASE_URL}/api/admin/businesses`, { headers: { "x-admin-key": key } })).data,

  createBusiness: async (key: string, data: object) =>
    (await axios.post(`${BASE_URL}/api/admin/businesses`, data, { headers: { "x-admin-key": key } })).data,

  updateBusiness: async (key: string, id: string, data: object) =>
    (await axios.patch(`${BASE_URL}/api/admin/businesses/${id}`, data, { headers: { "x-admin-key": key } })).data,

  impersonate: async (key: string, id: string) =>
    (await axios.post(`${BASE_URL}/api/admin/businesses/${id}/impersonate`, {}, { headers: { "x-admin-key": key } })).data,
};

export default axiosInstance;
