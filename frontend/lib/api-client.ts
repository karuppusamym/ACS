/**
 * Centralized API client for making HTTP requests
 * Automatically handles authentication, error handling, and base URL configuration
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ApiError {
  message: string;
  status: number;
  detail?: string;
}

export class ApiClientError extends Error {
  status: number;
  detail?: string;

  constructor(message: string, status: number, detail?: string) {
    super(message);
    this.name = "ApiClientError";
    this.status = status;
    this.detail = detail;
  }
}

interface RequestOptions extends RequestInit {
  skipAuth?: boolean;
}

/**
 * Make an authenticated API request
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { skipAuth, ...fetchOptions } = options;

  const url = `${API_BASE_URL}${endpoint}`;

  // Set default headers
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...fetchOptions.headers,
  };

  // Add authentication token from localStorage (fallback for existing code)
  // Note: Cookie-based auth is now preferred and handled automatically
  if (!skipAuth) {
    const token = localStorage.getItem("access_token");
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }

  // Make request
  const response = await fetch(url, {
    ...fetchOptions,
    headers,
    credentials: "include", // Include cookies for authentication
  });

  // Handle non-OK responses
  if (!response.ok) {
    let errorMessage = `HTTP Error ${response.status}`;
    let errorDetail: string | undefined;

    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || errorMessage;
      errorDetail = errorData.detail;
    } catch {
      // If response is not JSON, use status text
      errorMessage = response.statusText || errorMessage;
    }

    throw new ApiClientError(errorMessage, response.status, errorDetail);
  }

  // Parse response
  const contentType = response.headers.get("content-type");
  if (contentType && contentType.includes("application/json")) {
    return response.json();
  }

  return null as T;
}

/**
 * API client methods
 */
export const apiClient = {
  // Generic methods
  get: <T>(endpoint: string, options?: RequestOptions) =>
    apiRequest<T>(endpoint, { ...options, method: "GET" }),

  post: <T>(endpoint: string, data?: any, options?: RequestOptions) =>
    apiRequest<T>(endpoint, {
      ...options,
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    }),

  put: <T>(endpoint: string, data?: any, options?: RequestOptions) =>
    apiRequest<T>(endpoint, {
      ...options,
      method: "PUT",
      body: data ? JSON.stringify(data) : undefined,
    }),

  patch: <T>(endpoint: string, data?: any, options?: RequestOptions) =>
    apiRequest<T>(endpoint, {
      ...options,
      method: "PATCH",
      body: data ? JSON.stringify(data) : undefined,
    }),

  delete: <T>(endpoint: string, options?: RequestOptions) =>
    apiRequest<T>(endpoint, { ...options, method: "DELETE" }),

  // Auth methods
  auth: {
    login: async (username: string, password: string) => {
      const formData = new URLSearchParams();
      formData.append("username", username);
      formData.append("password", password);

      const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData,
        credentials: "include",
      });

      if (!response.ok) {
        const error = await response.json();
        throw new ApiClientError(
          error.detail || "Login failed",
          response.status,
          error.detail
        );
      }

      return response.json();
    },

    logout: () => apiClient.post("/api/v1/auth/logout"),

    signup: (data: { username: string; email: string; password: string }) =>
      apiClient.post("/api/v1/auth/signup", data, { skipAuth: true }),

    getCurrentUser: () => apiClient.get("/api/v1/auth/me"),
  },

  // Database connections
  connections: {
    list: () => apiClient.get("/api/v1/connection/connections"),

    create: (data: any) => apiClient.post("/api/v1/connection/connect", data),

    getMetadata: (connectionName: string) =>
      apiClient.get(`/api/v1/connection/metadata/${connectionName}`),
  },

  // Chat sessions
  sessions: {
    list: () => apiClient.get("/api/v1/chat/sessions"),

    create: (data: { name?: string; connection_id?: number }) =>
      apiClient.post("/api/v1/chat/sessions", data),

    get: (sessionId: number) =>
      apiClient.get(`/api/v1/chat/sessions/${sessionId}`),

    delete: (sessionId: number) =>
      apiClient.delete(`/api/v1/chat/sessions/${sessionId}`),

    getMessages: (sessionId: number) =>
      apiClient.get(`/api/v1/chat/sessions/${sessionId}/messages`),

    sendMessage: (sessionId: number, content: string) =>
      apiClient.post(`/api/v1/chat/sessions/${sessionId}/messages`, {
        role: "user",
        content,
      }),
  },

  // Semantic models
  semantic: {
    list: (connectionId: number) =>
      apiClient.get(`/api/v1/semantic/${connectionId}/models`),

    create: (connectionId: number, data: any) =>
      apiClient.post(`/api/v1/semantic/${connectionId}/models`, data),

    get: (connectionId: number, modelId: number) =>
      apiClient.get(`/api/v1/semantic/${connectionId}/models/${modelId}`),

    update: (connectionId: number, modelId: number, data: any) =>
      apiClient.put(`/api/v1/semantic/${connectionId}/models/${modelId}`, data),

    delete: (connectionId: number, modelId: number) =>
      apiClient.delete(`/api/v1/semantic/${connectionId}/models/${modelId}`),
  },

  // Process mining
  process: {
    upload: async (file: File) => {
      const formData = new FormData();
      formData.append("file", file);

      const token = localStorage.getItem("access_token");
      const headers: HeadersInit = {};
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      const response = await fetch(`${API_BASE_URL}/api/v1/process/upload`, {
        method: "POST",
        headers,
        body: formData,
        credentials: "include",
      });

      if (!response.ok) {
        const error = await response.json();
        throw new ApiClientError(
          error.detail || "Upload failed",
          response.status
        );
      }

      return response.json();
    },

    analyze: (data: any) => apiClient.post("/api/v1/process/analyze", data),
  },

  // Admin
  admin: {
    listUsers: (skip?: number, limit?: number) => {
      const params = new URLSearchParams();
      if (skip !== undefined) params.append("skip", skip.toString());
      if (limit !== undefined) params.append("limit", limit.toString());
      return apiClient.get(`/api/v1/admin/users?${params}`);
    },

    getLLMConfigs: () => apiClient.get("/api/v1/admin/llm-configs"),

    createLLMConfig: (data: any) =>
      apiClient.post("/api/v1/admin/llm-configs", data),

    testLLMConfig: (configId: number) =>
      apiClient.post(`/api/v1/admin/llm-configs/${configId}/test`),
  },
};

export default apiClient;
