"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Settings, Bell, Layout, Trash2, AlertTriangle } from "lucide-react";

// Toggle Switch Component
function ToggleSwitch({
  enabled,
  onToggle,
  label,
  description,
  icon: Icon,
}: {
  enabled: boolean;
  onToggle: () => void;
  label: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
}) {
  return (
    <div className="flex items-center justify-between p-4 rounded-xl bg-slate-800/30 border border-slate-700/30 hover:border-slate-600/50 transition-all duration-300">
      <div className="flex items-center gap-4">
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
          <Icon className="w-5 h-5 text-white" />
        </div>
        <div>
          <p className="text-white font-medium">{label}</p>
          <p className="text-sm" style={{ color: "var(--foreground-muted)" }}>
            {description}
          </p>
        </div>
      </div>
      <motion.button
        onClick={onToggle}
        className={`relative w-14 h-8 rounded-full transition-colors duration-300 ${
          enabled
            ? "bg-gradient-to-r from-indigo-500 to-purple-600"
            : "bg-slate-700"
        }`}
        whileTap={{ scale: 0.95 }}
      >
        <motion.div
          className="absolute top-1 w-6 h-6 rounded-full bg-white shadow-lg"
          animate={{ left: enabled ? "calc(100% - 28px)" : "4px" }}
          transition={{ type: "spring", stiffness: 500, damping: 30 }}
        />
      </motion.button>
    </div>
  );
}

export default function SettingsPage() {
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [compactMode, setCompactMode] = useState(false);

  const handleDeleteAccount = () => {
    const confirmed = window.confirm(
      "Are you sure you want to delete your account? This action cannot be undone."
    );
    if (confirmed) {
      alert("Account deletion would be processed here.");
    }
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <Settings className="w-8 h-8 text-indigo-400" />
          Settings
        </h1>
        <p className="mt-2" style={{ color: "var(--foreground-muted)" }}>
          Customize your TaskFlow experience.
        </p>
      </motion.div>

      {/* Preferences Panel */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.2, duration: 0.5 }}
        className="glass-card p-6"
      >
        <h2 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
          <span className="w-1.5 h-6 rounded-full bg-gradient-to-b from-indigo-500 to-purple-600" />
          Preferences
        </h2>

        <div className="space-y-4">
          {/* Email Notifications Toggle */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3, duration: 0.5 }}
          >
            <ToggleSwitch
              enabled={emailNotifications}
              onToggle={() => setEmailNotifications(!emailNotifications)}
              label="Email Notifications"
              description="Receive email updates about your tasks and activity"
              icon={Bell}
            />
          </motion.div>

          {/* Compact Mode Toggle */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4, duration: 0.5 }}
          >
            <ToggleSwitch
              enabled={compactMode}
              onToggle={() => setCompactMode(!compactMode)}
              label="Compact Mode"
              description="Use a more condensed view for task lists"
              icon={Layout}
            />
          </motion.div>
        </div>
      </motion.div>

      {/* Danger Zone */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5, duration: 0.5 }}
        className="rounded-2xl p-6 border-2 border-red-500/30 bg-red-500/5 backdrop-blur-md"
      >
        <h2 className="text-lg font-semibold text-red-400 mb-2 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5" />
          Danger Zone
        </h2>
        <p className="text-sm mb-6" style={{ color: "var(--foreground-muted)" }}>
          Irreversible and destructive actions. Please proceed with caution.
        </p>

        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-xl bg-red-500/10 border border-red-500/20">
          <div>
            <p className="text-white font-medium">Delete Account</p>
            <p className="text-sm" style={{ color: "var(--foreground-muted)" }}>
              Permanently delete your account and all associated data.
            </p>
          </div>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleDeleteAccount}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold text-white bg-red-600 hover:bg-red-700 shadow-lg shadow-red-500/25 transition-all duration-300 whitespace-nowrap"
          >
            <Trash2 className="w-4 h-4" />
            Delete Account
          </motion.button>
        </div>
      </motion.div>

      {/* Additional Info Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6, duration: 0.5 }}
        className="glass-card p-6"
      >
        <h3 className="text-lg font-semibold text-white mb-4">About</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
          <div className="p-3 rounded-lg bg-slate-800/30 border border-slate-700/30">
            <p style={{ color: "var(--foreground-muted)" }}>Version</p>
            <p className="text-white font-medium">1.0.0</p>
          </div>
          <div className="p-3 rounded-lg bg-slate-800/30 border border-slate-700/30">
            <p style={{ color: "var(--foreground-muted)" }}>Theme</p>
            <p className="text-white font-medium">Cyberpunk Dark</p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
