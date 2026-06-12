import axios from "axios";
import type {
  CreateSessionRequest,
  CreateSessionResponse,
  Session,
  SessionReport,
  PaginatedResponse,
} from "@titan/shared-types";

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000",
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// ─── Interceptors ──────────────────────────────────────────────
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ?? error.message ?? "An unknown error occurred";
    return Promise.reject(new Error(message));
  }
);

// ─── Sessions API ──────────────────────────────────────────────
export const sessionsApi = {
  create: async (data: CreateSessionRequest): Promise<CreateSessionResponse> => {
    const response = await apiClient.post<CreateSessionResponse>("/api/v1/sessions", data);
    return response.data;
  },

  list: async (page = 1, pageSize = 20): Promise<PaginatedResponse<Session>> => {
    const response = await apiClient.get<PaginatedResponse<Session>>("/api/v1/sessions", {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },

  get: async (id: string): Promise<Session> => {
    const response = await apiClient.get<Session>(`/api/v1/sessions/${id}`);
    return response.data;
  },

  getReport: async (id: string): Promise<SessionReport> => {
    const response = await apiClient.get<SessionReport>(`/api/v1/sessions/${id}/report`);
    return response.data;
  },
};

// ─── Health API ────────────────────────────────────────────────
export const healthApi = {
  check: async (): Promise<{ status: string; version: string }> => {
    const response = await apiClient.get<{ status: string; version: string }>("/api/v1/health");
    return response.data;
  },
};

export default apiClient;
