"use client";

import {
  createContext,
  useContext,
  useState,
  useCallback,
  ReactNode,
} from "react";
import { AnimatePresence, motion } from "framer-motion";
import { CheckCircle, XCircle, AlertCircle, Info, X } from "lucide-react";

export type NotificationType = "success" | "error" | "warning" | "info";

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message?: string;
  timestamp: Date;
  read: boolean;
}

interface NotificationContextType {
  notifications: Notification[];
  unreadCount: number;
  addNotification: (
    type: NotificationType,
    title: string,
    message?: string
  ) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  clearNotification: (id: string) => void;
  clearAll: () => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(
  undefined
);

// Toast component for displaying notifications
interface ToastProps {
  notification: Notification;
  onClose: () => void;
}

function Toast({ notification, onClose }: ToastProps) {
  const icons = {
    success: <CheckCircle className="w-5 h-5 text-emerald-400" />,
    error: <XCircle className="w-5 h-5 text-red-400" />,
    warning: <AlertCircle className="w-5 h-5 text-amber-400" />,
    info: <Info className="w-5 h-5 text-blue-400" />,
  };

  const bgColors = {
    success: "from-emerald-500/20 to-emerald-600/10 border-emerald-500/30",
    error: "from-red-500/20 to-red-600/10 border-red-500/30",
    warning: "from-amber-500/20 to-amber-600/10 border-amber-500/30",
    info: "from-blue-500/20 to-blue-600/10 border-blue-500/30",
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: -20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -20, scale: 0.95 }}
      transition={{ duration: 0.2 }}
      className={`
        flex items-start gap-3 p-4 rounded-xl border backdrop-blur-xl
        bg-gradient-to-r ${bgColors[notification.type]}
        shadow-lg shadow-black/20
      `}
    >
      <div className="flex-shrink-0 mt-0.5">{icons[notification.type]}</div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-white">{notification.title}</p>
        {notification.message && (
          <p className="text-xs mt-1 text-slate-300">{notification.message}</p>
        )}
      </div>
      <button
        onClick={onClose}
        className="flex-shrink-0 p-1 rounded-lg hover:bg-white/10 transition-colors"
      >
        <X className="w-4 h-4 text-slate-400" />
      </button>
    </motion.div>
  );
}

// Toast Container for displaying active toasts
interface ToastContainerProps {
  toasts: Notification[];
  onRemoveToast: (id: string) => void;
}

function ToastContainer({ toasts, onRemoveToast }: ToastContainerProps) {
  return (
    <div className="fixed top-24 right-8 z-50 flex flex-col gap-3 max-w-sm w-full pointer-events-none">
      <AnimatePresence mode="popLayout">
        {toasts.map((toast) => (
          <div key={toast.id} className="pointer-events-auto">
            <Toast notification={toast} onClose={() => onRemoveToast(toast.id)} />
          </div>
        ))}
      </AnimatePresence>
    </div>
  );
}

interface NotificationProviderProps {
  children: ReactNode;
}

export function NotificationProvider({ children }: NotificationProviderProps) {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [activeToasts, setActiveToasts] = useState<Notification[]>([]);

  const generateId = () => `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

  const addNotification = useCallback(
    (type: NotificationType, title: string, message?: string) => {
      const notification: Notification = {
        id: generateId(),
        type,
        title,
        message,
        timestamp: new Date(),
        read: false,
      };

      // Add to notifications history
      setNotifications((prev) => [notification, ...prev].slice(0, 50)); // Keep last 50

      // Show toast
      setActiveToasts((prev) => [notification, ...prev]);

      // Auto-remove toast after 4 seconds
      setTimeout(() => {
        setActiveToasts((prev) => prev.filter((t) => t.id !== notification.id));
      }, 4000);
    },
    []
  );

  const removeToast = useCallback((id: string) => {
    setActiveToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const markAsRead = useCallback((id: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n))
    );
  }, []);

  const markAllAsRead = useCallback(() => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  }, []);

  const clearNotification = useCallback((id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  }, []);

  const clearAll = useCallback(() => {
    setNotifications([]);
  }, []);

  const unreadCount = notifications.filter((n) => !n.read).length;

  return (
    <NotificationContext.Provider
      value={{
        notifications,
        unreadCount,
        addNotification,
        markAsRead,
        markAllAsRead,
        clearNotification,
        clearAll,
      }}
    >
      {children}
      <ToastContainer toasts={activeToasts} onRemoveToast={removeToast} />
    </NotificationContext.Provider>
  );
}

/**
 * Hook to access notification context
 */
export function useNotifications(): NotificationContextType {
  const context = useContext(NotificationContext);
  if (context === undefined) {
    throw new Error(
      "useNotifications must be used within a NotificationProvider"
    );
  }
  return context;
}

/**
 * Shorthand hooks for common notification types
 */
export function useToast() {
  const { addNotification } = useNotifications();

  return {
    success: (title: string, message?: string) =>
      addNotification("success", title, message),
    error: (title: string, message?: string) =>
      addNotification("error", title, message),
    warning: (title: string, message?: string) =>
      addNotification("warning", title, message),
    info: (title: string, message?: string) =>
      addNotification("info", title, message),
  };
}
