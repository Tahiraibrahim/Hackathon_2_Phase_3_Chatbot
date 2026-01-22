"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { User, Mail, Calendar, Award, Edit3, Shield } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

export default function ProfilePage() {
  const { user } = useAuth();
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <User className="w-8 h-8 text-indigo-400" />
          Profile
        </h1>
        <p className="mt-2" style={{ color: "var(--foreground-muted)" }}>
          Manage your account information.
        </p>
      </motion.div>

      {/* User Profile Card */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.2, duration: 0.5 }}
        className="glass-card p-8"
      >
        <div className="flex flex-col md:flex-row items-center md:items-start gap-8">
          {/* Avatar Section */}
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.4, type: "spring", stiffness: 200, damping: 15 }}
            className="relative"
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
          >
            <div className="w-32 h-32 rounded-full bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center shadow-2xl shadow-indigo-500/30 ring-4 ring-indigo-500/20">
              <span className="text-5xl font-bold text-white">
                {user?.username?.charAt(0).toUpperCase() || "U"}
              </span>
            </div>
            {/* Glow effect */}
            <div className="absolute inset-0 rounded-full bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 blur-xl opacity-30 -z-10" />
          </motion.div>

          {/* User Info Section */}
          <div className="flex-1 text-center md:text-left">
            {/* Name */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5, duration: 0.5 }}
              className="mb-6"
            >
              <h2 className="text-3xl font-bold text-white mb-2">
                {user?.username || "User"}
              </h2>
              {/* Pro User Badge */}
              <motion.span
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.7, duration: 0.3 }}
                className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-semibold bg-gradient-to-r from-amber-500/20 to-orange-500/20 text-amber-400 border border-amber-500/30"
              >
                <Award className="w-4 h-4" />
                Pro User
              </motion.span>
            </motion.div>

            {/* Info Grid */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.5 }}
              className="grid grid-cols-1 sm:grid-cols-2 gap-4"
            >
              {/* Email */}
              <div className="flex items-center gap-3 p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
                  <Mail className="w-5 h-5 text-white" />
                </div>
                <div>
                  <p className="text-xs font-medium" style={{ color: "var(--foreground-muted)" }}>
                    Email
                  </p>
                  <p className="text-white font-medium">
                    {user?.email || `${user?.username?.toLowerCase() || "user"}@example.com`}
                  </p>
                </div>
              </div>

              {/* Member Since */}
              <div className="flex items-center gap-3 p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center">
                  <Calendar className="w-5 h-5 text-white" />
                </div>
                <div>
                  <p className="text-xs font-medium" style={{ color: "var(--foreground-muted)" }}>
                    Member Since
                  </p>
                  <p className="text-white font-medium">2024</p>
                </div>
              </div>

              {/* Role */}
              <div className="flex items-center gap-3 p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center">
                  <Shield className="w-5 h-5 text-white" />
                </div>
                <div>
                  <p className="text-xs font-medium" style={{ color: "var(--foreground-muted)" }}>
                    Account Type
                  </p>
                  <p className="text-white font-medium">Pro Account</p>
                </div>
              </div>
            </motion.div>

            {/* Edit Profile Button */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8, duration: 0.5 }}
              className="mt-6"
            >
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl font-semibold text-white bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 shadow-lg shadow-indigo-500/25 transition-all duration-300"
              >
                <Edit3 className="w-5 h-5" />
                Edit Profile
              </motion.button>
            </motion.div>
          </div>
        </div>
      </motion.div>

      {/* Account Stats Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.5 }}
        className="glass-card p-6"
      >
        <h3 className="text-lg font-semibold text-white mb-4">Account Overview</h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="text-center p-4 rounded-xl bg-slate-800/30 border border-slate-700/30">
            <p className="text-3xl font-bold text-indigo-400">Pro</p>
            <p className="text-sm mt-1" style={{ color: "var(--foreground-muted)" }}>
              Subscription
            </p>
          </div>
          <div className="text-center p-4 rounded-xl bg-slate-800/30 border border-slate-700/30">
            <p className="text-3xl font-bold text-emerald-400">Active</p>
            <p className="text-sm mt-1" style={{ color: "var(--foreground-muted)" }}>
              Status
            </p>
          </div>
          <div className="text-center p-4 rounded-xl bg-slate-800/30 border border-slate-700/30">
            <p className="text-3xl font-bold text-purple-400">Unlimited</p>
            <p className="text-sm mt-1" style={{ color: "var(--foreground-muted)" }}>
              Tasks
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
