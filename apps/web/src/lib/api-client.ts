import axios, { AxiosError, AxiosInstance } from "axios";
import type {
  CreateSessionRequest,
  CreateSessionResponse,
  Session,
  SessionReport,
  PaginatedResponse,
} from "@titan/shared-types";

// ─── API Configuration ─────────────────────────────────────────
const isServer = typeof window === "undefined";
const API_BASE_URL = isServer
  ? (process.env.INTERNAL_API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000")
  : ""; // Browser uses relative path to route through Next.js proxy

const API_TIMEOUT = parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT ?? "30000");
const RETRY_MAX_ATTEMPTS = 3;
const RETRY_DELAY_MS = 1000;

const displayBaseUrl = API_BASE_URL || (typeof window !== "undefined" ? window.location.origin : "http://localhost:8000");

console.log("[API Config] Base URL:", isServer ? API_BASE_URL : `Relative (Proxy to ${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"})`);
console.log("[API Config] Timeout:", API_TIMEOUT + "ms");

// ─── Error Types ───────────────────────────────────────────────
export class APIError extends Error {
  constructor(
    public status: number | undefined,
    public code: string,
    public details: any,
    message: string
  ) {
    super(message);
    this.name = "APIError";
  }
}

// ─── Axios Client Factory ──────────────────────────────────────
function createApiClient(): AxiosInstance {
  const client = axios.create({
    baseURL: API_BASE_URL,
    timeout: API_TIMEOUT,
    headers: {
      "Content-Type": "application/json",
      "X-Client-Version": "1.0.0",
    },
  });

  // ─── Request Interceptor ─────────────────────────────────────
  client.interceptors.request.use(
    (config) => {
      // Log request details in development
      if (process.env.NODE_ENV === "development") {
        console.debug("[API Request]", {
          method: config.method?.toUpperCase(),
          url: config.url,
          baseURL: config.baseURL,
        });
      }
      return config;
    },
    (error) => {
      console.error("[API Request Error]", error);
      return Promise.reject(error);
    }
  );

  // ─── Response Interceptor ────────────────────────────────────
  client.interceptors.response.use(
    (response) => {
      if (process.env.NODE_ENV === "development") {
        console.debug("[API Response]", {
          status: response.status,
          url: response.config.url,
          dataSize: JSON.stringify(response.data).length + " bytes",
        });
      }
      return response;
    },
    async (error: AxiosError<any>) => {
      // ─── Retry Logic for Transient Failures ───────────────────
      const config = error.config;
      if (config) {
        const currentRetry = (config as any).__retryCount || 0;
        
        const isNetworkError = error.code === "ERR_NETWORK" || !error.response;
        const isTimeoutError = error.code === "ECONNABORTED";
        const isServerError = error.response && error.response.status >= 500 && error.response.status !== 501;
        
        const isTransient = isNetworkError || isTimeoutError || isServerError;
        
        if (isTransient && currentRetry < RETRY_MAX_ATTEMPTS) {
          (config as any).__retryCount = currentRetry + 1;
          const delayMs = RETRY_DELAY_MS * Math.pow(2, currentRetry); // 1s, 2s, 4s
          
          console.warn(
            `[API Client] Transient error detected (${error.message || error.code}). ` +
            `Retrying request to ${config.url} in ${delayMs}ms... (Attempt ${currentRetry + 1}/${RETRY_MAX_ATTEMPTS})`
          );
          
          await new Promise((resolve) => setTimeout(resolve, delayMs));
          return client(config);
        }
      }

      // Network/timeout errors (no response)
      if (!error.response) {
        if (error.code === "ECONNABORTED") {
          const apiError = new APIError(
            undefined,
            "TIMEOUT",
            error,
            `Request timeout after ${API_TIMEOUT}ms. The backend server may be offline or unreachable at ${displayBaseUrl}`
          );
          console.error("[API Timeout Error]", apiError.message);
          return Promise.reject(apiError);
        }

        if (error.code === "ERR_NETWORK") {
          const apiError = new APIError(
            undefined,
            "NETWORK_ERROR",
            error,
            `Network error: Unable to connect to ${displayBaseUrl}. Please check if the backend server is running.`
          );
          console.error("[API Network Error]", apiError.message);
          return Promise.reject(apiError);
        }

        const apiError = new APIError(
          undefined,
          error.code || "UNKNOWN_ERROR",
          error,
          `Network error: ${error.message}`
        );
        console.error("[API Error]", apiError.message);
        return Promise.reject(apiError);
      }

      // HTTP error responses (with status code)
      const status = error.response.status;
      const detail = error.response.data?.detail || error.response.data?.message;
      const errorCode = error.response.data?.code || "HTTP_ERROR";

      let message = `Server error (${status})`;

      if (status === 400) {
        message = `Validation error: ${detail || "Invalid request data"}`;
      } else if (status === 401) {
        message = "Authentication required. Please log in.";
      } else if (status === 403) {
        message = "Access denied. You do not have permission.";
      } else if (status === 404) {
        message = `Endpoint not found: ${error.config?.url}. The backend API may not have the required endpoints.`;
      } else if (status === 422) {
        message = `Validation failed: ${detail || "Request data did not match expected format"}`;
      } else if (status === 500) {
        message = `Server error: ${detail || "An internal error occurred. Please try again later."}`;
      } else if (status === 503) {
        message = "Service unavailable. The backend server is temporarily offline.";
      } else if (detail) {
        message = detail;
      }

      const apiError = new APIError(status, errorCode, error.response.data, message);
      console.error("[API HTTP Error]", {
        status,
        code: errorCode,
        message,
        url: error.config?.url,
      });

      return Promise.reject(apiError);
    }
  );

  return client;
}

const apiClient = createApiClient();

// ─── Sessions API ──────────────────────────────────────────────
export const sessionsApi = {
  create: async (data: CreateSessionRequest): Promise<CreateSessionResponse> => {
    try {
      const response = await apiClient.post<CreateSessionResponse>("/api/v1/sessions", data);
      return response.data;
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      throw new APIError(500, "UNKNOWN", error, "Failed to create session");
    }
  },

  list: async (page = 1, pageSize = 20): Promise<PaginatedResponse<Session>> => {
    try {
      const response = await apiClient.get<PaginatedResponse<Session>>("/api/v1/sessions", {
        params: { page, page_size: pageSize },
      });
      return response.data;
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      throw new APIError(500, "UNKNOWN", error, "Failed to fetch sessions");
    }
  },

  get: async (id: string): Promise<Session> => {
    try {
      const response = await apiClient.get<Session>(`/api/v1/sessions/${id}`);
      return response.data;
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      throw new APIError(500, "UNKNOWN", error, `Failed to fetch session ${id}`);
    }
  },

  getReport: async (id: string): Promise<SessionReport> => {
    try {
      const response = await apiClient.get<SessionReport>(`/api/v1/sessions/${id}/report`);
      return response.data;
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      throw new APIError(500, "UNKNOWN", error, `Failed to fetch report for session ${id}`);
    }
  },
};

// ─── Health API ────────────────────────────────────────────────
export const healthApi = {
  check: async (): Promise<{ status: string; version: string }> => {
    try {
      const response = await apiClient.get<{ status: string; version: string }>("/api/v1/health");
      return response.data;
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      throw new APIError(500, "UNKNOWN", error, "Failed to check API health");
    }
  },
};

export default apiClient;
