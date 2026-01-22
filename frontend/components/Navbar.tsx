"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Bell,
  Search,
  ChevronDown,
  Plus,
  Check,
  Trash2,
  CheckCircle,
  XCircle,
  AlertCircle,
  Info,
} from "lucide-react";
import { useAuth, useDisplayName } from "@/context/AuthContext";
import { useNotifications, Notification, NotificationType } from "@/context/NotificationContext";

interface NavbarProps {
  onSearch?: (query: string) => void;
}

// Format relative time
function formatRelativeTime(date: Date): string {
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);

  if (seconds < 60) return "Just now";
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  return date.toLocaleDateString();
}

// Notification icon based on type
function NotificationIcon({ type }: { type: NotificationType }) {
  const icons = {
    success: <CheckCircle className="w-4 h-4 text-emerald-400" />,
    error: <XCircle className="w-4 h-4 text-red-400" />,
    warning: <AlertCircle className="w-4 h-4 text-amber-400" />,
    info: <Info className="w-4 h-4 text-blue-400" />,
  };
  return icons[type];
}

export default function Navbar({ onSearch }: NavbarProps) {
  const displayName = useDisplayName();
  const { notifications, unreadCount, markAsRead, markAllAsRead, clearNotification } =
    useNotifications();
  const [searchQuery, setSearchQuery] = useState("");
  const [showNotifications, setShowNotifications] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowNotifications(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Debounce search functionality
  useEffect(() => {
    const timer = setTimeout(() => {
      if (onSearch) {
        onSearch(searchQuery);
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [searchQuery, onSearch]);

  const handleSearchChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      setSearchQuery(e.target.value);
    },
    []
  );

  const handleBellClick = () => {
    setShowNotifications((prev) => !prev);
  };

  const handleNotificationClick = (notification: Notification) => {
    if (!notification.read) {
      markAsRead(notification.id);
    }
  };

  return (
    <motion.nav
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className="fixed top-0 left-64 right-0 h-20 bg-slate-900/80 backdrop-blur-xl border-b z-40"
      style={{ borderColor: "var(--glass-border)" }}
    >
      <div className="h-full px-8 flex items-center justify-between">
        {/* Search Bar */}
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.5 }}
          className="flex items-center gap-3 px-4 py-2.5 rounded-xl w-96 transition-all duration-300"
          style={{
            background: "var(--input-bg)",
            border: "1px solid var(--input-border)",
          }}
        >
          <Search
            className="w-5 h-5"
            style={{ color: "var(--input-placeholder)" }}
          />
          <input
            type="text"
            placeholder="Search tasks..."
            value={searchQuery}
            onChange={handleSearchChange}
            className="flex-1 bg-transparent outline-none"
            style={{ color: "var(--input-text)" }}
          />
          <kbd
            className="hidden sm:inline-flex items-center gap-1 px-2 py-1 text-xs rounded"
            style={{
              color: "var(--input-placeholder)",
              background: "var(--background)",
              border: "1px solid var(--input-border)",
            }}
          >
            /
          </kbd>
        </motion.div>

        {/* Right Section */}
        <div className="flex items-center gap-4">
          {/* Add Task Button - Prominent */}
          <motion.button
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.25, duration: 0.5 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-white font-medium transition-all duration-300 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 shadow-lg shadow-blue-500/25"
          >
            <Plus className="w-4 h-4" />
            <span className="hidden sm:inline">Add Task</span>
          </motion.button>

          {/* Notifications */}
          <div className="relative" ref={dropdownRef}>
            <motion.button
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.3, duration: 0.5 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleBellClick}
              className="relative p-2.5 rounded-xl transition-all duration-300"
              style={{
                background: "var(--input-bg)",
                border: `1px solid ${showNotifications ? "var(--accent-primary)" : "var(--input-border)"}`,
              }}
            >
              <Bell
                className="w-5 h-5"
                style={{ color: "var(--foreground-muted)" }}
              />
              {unreadCount > 0 && (
                <motion.span
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", stiffness: 500, damping: 15 }}
                  className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full text-white text-xs flex items-center justify-center font-bold"
                >
                  {unreadCount > 9 ? "9+" : unreadCount}
                </motion.span>
              )}
            </motion.button>

            {/* Notifications Dropdown */}
            <AnimatePresence>
              {showNotifications && (
                <motion.div
                  initial={{ opacity: 0, y: 10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 10, scale: 0.95 }}
                  transition={{ duration: 0.2 }}
                  className="absolute right-0 mt-2 w-80 max-h-96 overflow-hidden rounded-xl shadow-xl"
                  style={{
                    background: "var(--glass-bg)",
                    backdropFilter: "blur(16px)",
                    border: "1px solid var(--glass-border)",
                  }}
                >
                  {/* Header */}
                  <div
                    className="flex items-center justify-between px-4 py-3"
                    style={{ borderBottom: "1px solid var(--glass-border)" }}
                  >
                    <h3 className="font-semibold text-white">Notifications</h3>
                    {unreadCount > 0 && (
                      <button
                        onClick={markAllAsRead}
                        className="text-xs text-blue-400 hover:text-blue-300 transition-colors flex items-center gap-1"
                      >
                        <Check className="w-3 h-3" />
                        Mark all read
                      </button>
                    )}
                  </div>

                  {/* Notifications List */}
                  <div className="max-h-72 overflow-y-auto">
                    {notifications.length === 0 ? (
                      <div className="px-4 py-8 text-center">
                        <Bell
                          className="w-8 h-8 mx-auto mb-2"
                          style={{ color: "var(--input-placeholder)" }}
                        />
                        <p
                          className="text-sm"
                          style={{ color: "var(--input-placeholder)" }}
                        >
                          No notifications yet
                        </p>
                      </div>
                    ) : (
                      notifications.slice(0, 10).map((notification) => (
                        <motion.div
                          key={notification.id}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          className={`
                            flex items-start gap-3 px-4 py-3 cursor-pointer
                            transition-colors duration-200
                            ${
                              notification.read
                                ? "bg-transparent"
                                : "bg-blue-500/5"
                            }
                            hover:bg-white/5
                          `}
                          style={{
                            borderBottom: "1px solid var(--glass-border)",
                          }}
                          onClick={() => handleNotificationClick(notification)}
                        >
                          <div className="flex-shrink-0 mt-0.5">
                            <NotificationIcon type={notification.type} />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p
                              className={`text-sm ${notification.read ? "text-slate-300" : "text-white font-medium"}`}
                            >
                              {notification.title}
                            </p>
                            {notification.message && (
                              <p
                                className="text-xs mt-0.5 truncate"
                                style={{ color: "var(--input-placeholder)" }}
                              >
                                {notification.message}
                              </p>
                            )}
                            <p
                              className="text-xs mt-1"
                              style={{ color: "var(--input-placeholder)" }}
                            >
                              {formatRelativeTime(notification.timestamp)}
                            </p>
                          </div>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              clearNotification(notification.id);
                            }}
                            className="flex-shrink-0 p-1 rounded hover:bg-white/10 transition-colors"
                          >
                            <Trash2
                              className="w-3 h-3"
                              style={{ color: "var(--input-placeholder)" }}
                            />
                          </button>
                          {!notification.read && (
                            <div className="flex-shrink-0 w-2 h-2 rounded-full bg-blue-500 mt-1.5" />
                          )}
                        </motion.div>
                      ))
                    )}
                  </div>

                  {/* Footer */}
                  {notifications.length > 10 && (
                    <div
                      className="px-4 py-2 text-center"
                      style={{ borderTop: "1px solid var(--glass-border)" }}
                    >
                      <p
                        className="text-xs"
                        style={{ color: "var(--input-placeholder)" }}
                      >
                        +{notifications.length - 10} more notifications
                      </p>
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* User Profile */}
          <motion.div
            initial={{ x: 50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.4, duration: 0.5 }}
            className="flex items-center gap-3 px-3 py-2 rounded-xl transition-all duration-300 cursor-pointer hover:bg-slate-800/50"
            style={{ border: "1px solid var(--glass-border)" }}
          >
            {/* Avatar */}
            <div className="relative">
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-semibold text-sm">
                {displayName.charAt(0).toUpperCase()}
              </div>
              <div className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-emerald-500 rounded-full border-2 border-slate-900"></div>
            </div>

            {/* User Info */}
            <div className="hidden md:block">
              <p className="text-sm font-medium text-white">{displayName}</p>
              <p className="text-xs" style={{ color: "var(--input-placeholder)" }}>
                Online
              </p>
            </div>

            <ChevronDown
              className="w-4 h-4"
              style={{ color: "var(--input-placeholder)" }}
            />
          </motion.div>
        </div>
      </div>

      {/* Bottom Border Accent */}
      <motion.div
        initial={{ scaleX: 0 }}
        animate={{ scaleX: 1 }}
        transition={{ delay: 0.5, duration: 0.8 }}
        className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-blue-600 to-indigo-600 origin-left"
      />
    </motion.nav>
  );
}
