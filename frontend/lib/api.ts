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

export const api = {
  // Auth
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

  cancelAppointment: async (id: string) =>
    (await axiosInstance.delete(`/api/appointments/${id}`)).data,

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

  // Google Calendar
  connectGoogle: async () =>
    (await axiosInstance.get("/api/calendar/connect")).data,

  disconnectGoogle: async () =>
    (await axiosInstance.delete("/api/calendar/disconnect")).data,
};

export default axiosInstance;
