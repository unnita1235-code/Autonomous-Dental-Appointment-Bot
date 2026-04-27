import axios, { AxiosError, type AxiosResponse } from "axios";

export interface ApiEnvelope<T> {
  success: boolean;
  data: T | null;
  error: string | null;
  meta: Record<string, unknown> | null;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const AUTH_TOKEN_KEY = "jwt_token";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json"
  }
});

apiClient.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = window.localStorage.getItem(AUTH_TOKEN_KEY);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }

  return config;
});

apiClient.interceptors.response.use(
  <T>(response: AxiosResponse<ApiEnvelope<T>>) => {
    const envelope = response.data;

    if (!envelope.success) {
      return Promise.reject(new Error(envelope.error ?? "Request failed"));
    }

    return envelope.data as T;
  },
  (error: AxiosError<ApiEnvelope<unknown>>) => {
    if (typeof window !== "undefined" && error.response?.status === 401) {
      window.localStorage.removeItem(AUTH_TOKEN_KEY);
      window.location.href = "/login";
    }

    const errorMessage =
      error.response?.data?.error ?? error.message ?? "Unexpected API error";

    return Promise.reject(new Error(errorMessage));
  }
);

export { API_BASE_URL, AUTH_TOKEN_KEY };
