import axios, { AxiosInstance } from "axios";
import { authClient } from "./auth-client";

// ✅ FIX: Agar URL ke aakhir mein '/' ho to usay hata do taake double slash na aye
const getBaseUrl = () => {
  const url = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
  return url.endsWith("/") ? url.slice(0, -1) : url;
};

const API_BASE_URL = getBaseUrl();

/**
 * Axios instance configured for the Task Management API
 * Now uses direct token passing instead of async interceptors
 */
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true, // Keep for backward compatibility
  timeout: 30000, // 30 seconds timeout to handle slow database cold-start
});

export type Priority = "HIGH" | "MEDIUM" | "LOW";

export interface Task {
  id: number;
  title: string;
  description: string | null;
  is_completed: boolean;
  priority: Priority;
  category: string | null;
  due_date: string | null;
  is_recurring: boolean;
  user_id: number;
}

/**
 * Helper function to extract token from browser cookies
 * Fallback mechanism when authClient.getSession() fails
 */
const getTokenFromCookie = (): string | null => {
  if (typeof window === "undefined" || typeof document === "undefined") {
    return null;
  }

  try {
    const cookies = document.cookie.split('; ');

    // Try multiple cookie name patterns
    const patterns = [
      'better-auth.session_token',
      'session_token',
      'authjs.session-token',
    ];

    for (const pattern of patterns) {
      const cookie = cookies.find(row => row.startsWith(`${pattern}=`));
      if (cookie) {
        const token = cookie.split('=')[1];
        // Decode URL-encoded token (fixes %3D and other encoding issues)
        return decodeURIComponent(token);
      }
    }

    return null;
  } catch (error) {
    console.error("Failed to parse cookies:", error);
    return null;
  }
};

/**
 * Helper function to create axios config with token
 * If token is not provided, attempts to fetch from authClient with retry logic
 * CRITICAL FALLBACK: If authClient fails, reads token directly from cookies
 */
const getConfigWithToken = async (token?: string) => {
  let finalToken: string | null | undefined = token;

  // If no token provided, try to get it from authClient with retries
  if (!finalToken) {
    let retries = 3;

    while (retries > 0 && !finalToken) {
      try {
        const session = await authClient.getSession();
        finalToken = session.data?.session?.token;

        if (!finalToken) {
          console.warn(`⚠️ No token found from authClient, retrying... (${retries} attempts left)`);
          await new Promise(resolve => setTimeout(resolve, 300)); // Wait 300ms before retry
          retries--;
        }
      } catch (error) {
        console.error("Failed to get session token from authClient:", error);
        retries--;
        if (retries > 0) {
          await new Promise(resolve => setTimeout(resolve, 300));
        }
      }
    }
  }

  // CRITICAL FALLBACK: If authClient failed, try reading from cookies directly
  if (!finalToken) {
    console.warn("⚠️ authClient.getSession() failed, attempting cookie fallback...");
    finalToken = getTokenFromCookie();

    if (finalToken) {
      console.log("✅ Token recovered from cookie fallback!");
    }
  }

  // CRITICAL: Block request if no token is available after all attempts
  if (!finalToken) {
    console.error("❌ CRITICAL: No session token available for API request after retries and cookie fallback");
    throw new Error("Authentication required. Please log in again.");
  }

  console.log("✅ API Token Present:", !!finalToken, "Length:", finalToken.length);

  return {
    headers: {
      Authorization: `Bearer ${finalToken}`,
    },
  };
};

/**
 * Response interceptor to handle 401 errors
 */
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      if (typeof window !== "undefined") {
        console.error("⚠️ 401 Unauthorized: Token rejected by backend");
        // Optional: Redirect logic here if needed
      }
    }
    return Promise.reject(error);
  }
);

/**
 * API client methods
 * All methods now accept an optional token parameter for direct token passing
 */
export const taskApi = {
  getTasks: async (token?: string, params?: { search?: string; priority?: Priority }): Promise<Task[]> => {
    const config = await getConfigWithToken(token);
    const response = await api.get<Task[]>("/api/todos", {
      ...config,
      params,
    });
    return response.data;
  },

  createTask: async (
    token: string | undefined,
    data: {
      title: string;
      description?: string;
      priority?: Priority;
      category?: string;
      due_date?: string;
      is_recurring?: boolean;
    }
  ): Promise<Task> => {
    const config = await getConfigWithToken(token);

    // Ensure priority is properly formatted (uppercase) and not undefined
    const priority = data.priority ? (data.priority.toUpperCase() as Priority) : "MEDIUM";

    const payload = {
      ...data,
      priority: priority,
    };

    console.log("📤 API Request Payload:", JSON.stringify(payload, null, 2));
    const response = await api.post<Task>("/api/todos", payload, config);
    console.log("📥 API Response:", JSON.stringify(response.data, null, 2));
    return response.data;
  },

  updateTask: async (
    id: number,
    token: string | undefined,
    data: Partial<Task>
  ): Promise<Task> => {
    const config = await getConfigWithToken(token);
    const response = await api.put<Task>(`/api/todos/${id}`, data, config);
    return response.data;
  },

  deleteTask: async (id: number, token?: string): Promise<void> => {
    const config = await getConfigWithToken(token);
    await api.delete(`/api/todos/${id}`, config);
  },
};