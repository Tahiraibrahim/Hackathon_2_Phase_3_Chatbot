"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  ReactNode,
} from "react";
import { useRouter } from "next/navigation";

interface User {
  username: string;
  email?: string;
  userId?: number;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string, userData?: Partial<User>) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * Decode JWT token payload without verifying signature
 * This extracts the user information from the token
 */
function decodeJWT(token: string): Record<string, unknown> | null {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return null;

    const payload = parts[1];
    // Base64 URL decode
    const base64 = payload.replace(/-/g, "+").replace(/_/g, "/");
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
        .join("")
    );

    return JSON.parse(jsonPayload);
  } catch {
    console.error("Failed to decode JWT token");
    return null;
  }
}

/**
 * Extract user information from JWT payload
 */
function extractUserFromToken(token: string): User | null {
  const payload = decodeJWT(token);
  if (!payload) return null;

  // Try common JWT claim names for username
  const username =
    (payload.username as string) ||
    (payload.name as string) ||
    (payload.full_name as string) ||
    (payload.sub as string) ||
    (payload.email as string)?.split("@")[0] ||
    null;

  if (!username) return null;

  return {
    username,
    email: payload.email as string | undefined,
    userId: (payload.user_id as number) || (payload.sub as number) || undefined,
  };
}

/**
 * Check if token is expired
 */
function isTokenExpired(token: string): boolean {
  const payload = decodeJWT(token);
  if (!payload || !payload.exp) return false;

  const expiry = (payload.exp as number) * 1000; // Convert to milliseconds
  return Date.now() >= expiry;
}

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // Initialize auth state from localStorage
  useEffect(() => {
    const initAuth = () => {
      const token = localStorage.getItem("authToken");
      const storedName = localStorage.getItem("userName");

      if (token) {
        // Check if token is expired
        if (isTokenExpired(token)) {
          localStorage.removeItem("authToken");
          localStorage.removeItem("userName");
          setUser(null);
        } else {
          // Try to extract user from token
          const tokenUser = extractUserFromToken(token);
          if (tokenUser) {
            setUser(tokenUser);
          } else if (storedName) {
            // Fallback to stored username
            setUser({ username: storedName });
          }
        }
      }

      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = useCallback((token: string, userData?: Partial<User>) => {
    localStorage.setItem("authToken", token);

    // Try to extract user from token first
    let userInfo = extractUserFromToken(token);

    // If we have additional userData, merge it
    if (userData) {
      userInfo = {
        username: userData.username || userInfo?.username || "User",
        email: userData.email || userInfo?.email,
        userId: userData.userId || userInfo?.userId,
      };
    }

    // Store username in localStorage for compatibility
    if (userInfo?.username) {
      localStorage.setItem("userName", userInfo.username);
    }

    setUser(userInfo);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("authToken");
    localStorage.removeItem("userName");
    setUser(null);
    router.push("/login");
  }, [router]);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

/**
 * Hook to access auth context
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

/**
 * Get the display name for the user
 * Returns "Guest" if no user is logged in
 */
export function useDisplayName(): string {
  const { user } = useAuth();
  return user?.username || "Guest";
}
