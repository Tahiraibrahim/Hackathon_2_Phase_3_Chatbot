"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  BarChart3,
  CheckCircle2,
  ListTodo,
  TrendingUp,
  AlertTriangle,
  Clock,
  Target,
  Zap,
} from "lucide-react";
import { taskApi, Task, Priority } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { authClient } from "@/lib/auth-client";

const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 },
};

// Productivity message based on completion rate
function getProductivityMessage(completionRate: number, totalTasks: number): { message: string; icon: React.ReactNode } {
  if (totalTasks === 0) {
    return {
      message: "Start adding tasks to track your productivity!",
      icon: <Target className="w-6 h-6 text-blue-400" />,
    };
  }
  if (completionRate >= 80) {
    return {
      message: "Outstanding! You're crushing it!",
      icon: <Zap className="w-6 h-6 text-yellow-400" />,
    };
  }
  if (completionRate >= 50) {
    return {
      message: "Keep it up! You're making great progress!",
      icon: <TrendingUp className="w-6 h-6 text-emerald-400" />,
    };
  }
  if (completionRate >= 25) {
    return {
      message: "Good start! Keep pushing forward!",
      icon: <Clock className="w-6 h-6 text-amber-400" />,
    };
  }
  return {
    message: "Time to get productive! You've got this!",
    icon: <AlertTriangle className="w-6 h-6 text-orange-400" />,
  };
}

export default function AnalyticsPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();

  // Get session token from Better Auth - Direct token passing
  const { data: session } = authClient.useSession();
  const sessionToken = session?.session?.token;

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      const token = localStorage.getItem("authToken");
      if (!token) {
        router.push("/login");
        return;
      }
    }
    if (!authLoading) {
      fetchTasks();
    }
  }, [authLoading, isAuthenticated, router]);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const data = await taskApi.getTasks(sessionToken);
      setTasks(data);
    } catch (err) {
      console.error("Failed to fetch tasks for analytics:", err);
    } finally {
      setLoading(false);
    }
  };

  // Calculate analytics
  const totalTasks = tasks.length;
  const completedTasks = tasks.filter((t) => t.is_completed).length;
  const pendingTasks = totalTasks - completedTasks;
  const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  // Count by priority
  const highPriorityCount = tasks.filter((t) => t.priority === "HIGH").length;
  const mediumPriorityCount = tasks.filter((t) => t.priority === "MEDIUM").length;
  const lowPriorityCount = tasks.filter((t) => t.priority === "LOW").length;

  // Completed by priority
  const highCompleted = tasks.filter((t) => t.priority === "HIGH" && t.is_completed).length;
  const mediumCompleted = tasks.filter((t) => t.priority === "MEDIUM" && t.is_completed).length;
  const lowCompleted = tasks.filter((t) => t.priority === "LOW" && t.is_completed).length;

  const productivityInfo = getProductivityMessage(completionRate, totalTasks);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="relative">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <BarChart3 className="w-8 h-8 text-indigo-400" />
          Analytics
        </h1>
        <p className="mt-2" style={{ color: "var(--foreground-muted)" }}>
          Track your productivity and task insights.
        </p>
      </motion.div>

      {/* Productivity Message Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1, duration: 0.5 }}
        className="glass-card p-6"
      >
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg">
            {productivityInfo.icon}
          </div>
          <div>
            <p className="text-lg font-semibold text-white">{productivityInfo.message}</p>
            <p className="text-sm" style={{ color: "var(--foreground-muted)" }}>
              {totalTasks > 0
                ? `You've completed ${completedTasks} out of ${totalTasks} tasks`
                : "Add your first task to get started"}
            </p>
          </div>
        </div>
      </motion.div>

      {/* Main Stats Cards */}
      <motion.div
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6"
        variants={containerVariants}
        initial="hidden"
        animate="show"
      >
        {/* Total Tasks */}
        <motion.div
          variants={itemVariants}
          whileHover={{ scale: 1.02, y: -4 }}
          className="glass-card-solid p-6 card-elevated transition-all duration-300 hover:shadow-blue-500/10 hover:shadow-xl"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium" style={{ color: "var(--foreground-muted)" }}>
                Total Tasks
              </p>
              <motion.p
                key={totalTasks}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-4xl font-bold text-white mt-2"
              >
                {totalTasks}
              </motion.p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg">
              <ListTodo className="w-6 h-6 text-white" />
            </div>
          </div>
        </motion.div>

        {/* Completed Tasks */}
        <motion.div
          variants={itemVariants}
          whileHover={{ scale: 1.02, y: -4 }}
          className="glass-card-solid p-6 card-elevated transition-all duration-300 hover:shadow-emerald-500/10 hover:shadow-xl"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium" style={{ color: "var(--foreground-muted)" }}>
                Completed
              </p>
              <motion.p
                key={completedTasks}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-4xl font-bold text-white mt-2"
              >
                {completedTasks}
              </motion.p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-lg">
              <CheckCircle2 className="w-6 h-6 text-white" />
            </div>
          </div>
        </motion.div>

        {/* Pending Tasks */}
        <motion.div
          variants={itemVariants}
          whileHover={{ scale: 1.02, y: -4 }}
          className="glass-card-solid p-6 card-elevated transition-all duration-300 hover:shadow-amber-500/10 hover:shadow-xl"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium" style={{ color: "var(--foreground-muted)" }}>
                Pending
              </p>
              <motion.p
                key={pendingTasks}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-4xl font-bold text-white mt-2"
              >
                {pendingTasks}
              </motion.p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center shadow-lg">
              <Clock className="w-6 h-6 text-white" />
            </div>
          </div>
        </motion.div>

        {/* Completion Rate */}
        <motion.div
          variants={itemVariants}
          whileHover={{ scale: 1.02, y: -4 }}
          className="glass-card-solid p-6 card-elevated transition-all duration-300 hover:shadow-purple-500/10 hover:shadow-xl"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium" style={{ color: "var(--foreground-muted)" }}>
                Completion Rate
              </p>
              <motion.p
                key={completionRate}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-4xl font-bold text-white mt-2"
              >
                {completionRate}%
              </motion.p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center shadow-lg">
              <TrendingUp className="w-6 h-6 text-white" />
            </div>
          </div>
        </motion.div>
      </motion.div>

      {/* Completion Progress Bar */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3, duration: 0.5 }}
        className="glass-card p-6"
      >
        <h2 className="text-lg font-semibold text-white mb-4">Overall Progress</h2>
        <div className="relative">
          {/* Progress Bar Background */}
          <div className="w-full h-4 rounded-full bg-slate-700/50 overflow-hidden">
            {/* Progress Bar Fill */}
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${completionRate}%` }}
              transition={{ delay: 0.5, duration: 1, ease: "easeOut" }}
              className="h-full rounded-full bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 shadow-lg shadow-emerald-500/30"
            />
          </div>
          {/* Progress Labels */}
          <div className="flex justify-between mt-2 text-sm" style={{ color: "var(--foreground-muted)" }}>
            <span>0%</span>
            <span className="text-emerald-400 font-medium">{completionRate}% Complete</span>
            <span>100%</span>
          </div>
        </div>
      </motion.div>

      {/* Priority Breakdown */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.5 }}
        className="glass-card p-6"
      >
        <h2 className="text-lg font-semibold text-white mb-6">Tasks by Priority</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* High Priority */}
          <div className="p-4 rounded-xl" style={{ background: "rgba(239, 68, 68, 0.1)", border: "1px solid rgba(239, 68, 68, 0.3)" }}>
            <div className="flex items-center justify-between mb-3">
              <span className="text-red-400 font-semibold">High Priority</span>
              <span className="text-2xl font-bold text-white">{highPriorityCount}</span>
            </div>
            <div className="w-full h-2 rounded-full bg-slate-700/50 overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: highPriorityCount > 0 ? `${(highCompleted / highPriorityCount) * 100}%` : "0%" }}
                transition={{ delay: 0.6, duration: 0.8, ease: "easeOut" }}
                className="h-full rounded-full bg-red-500"
              />
            </div>
            <p className="mt-2 text-sm" style={{ color: "var(--foreground-muted)" }}>
              {highCompleted} of {highPriorityCount} completed
            </p>
          </div>

          {/* Medium Priority */}
          <div className="p-4 rounded-xl" style={{ background: "rgba(245, 158, 11, 0.1)", border: "1px solid rgba(245, 158, 11, 0.3)" }}>
            <div className="flex items-center justify-between mb-3">
              <span className="text-amber-400 font-semibold">Medium Priority</span>
              <span className="text-2xl font-bold text-white">{mediumPriorityCount}</span>
            </div>
            <div className="w-full h-2 rounded-full bg-slate-700/50 overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: mediumPriorityCount > 0 ? `${(mediumCompleted / mediumPriorityCount) * 100}%` : "0%" }}
                transition={{ delay: 0.7, duration: 0.8, ease: "easeOut" }}
                className="h-full rounded-full bg-amber-500"
              />
            </div>
            <p className="mt-2 text-sm" style={{ color: "var(--foreground-muted)" }}>
              {mediumCompleted} of {mediumPriorityCount} completed
            </p>
          </div>

          {/* Low Priority */}
          <div className="p-4 rounded-xl" style={{ background: "rgba(34, 197, 94, 0.1)", border: "1px solid rgba(34, 197, 94, 0.3)" }}>
            <div className="flex items-center justify-between mb-3">
              <span className="text-emerald-400 font-semibold">Low Priority</span>
              <span className="text-2xl font-bold text-white">{lowPriorityCount}</span>
            </div>
            <div className="w-full h-2 rounded-full bg-slate-700/50 overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: lowPriorityCount > 0 ? `${(lowCompleted / lowPriorityCount) * 100}%` : "0%" }}
                transition={{ delay: 0.8, duration: 0.8, ease: "easeOut" }}
                className="h-full rounded-full bg-emerald-500"
              />
            </div>
            <p className="mt-2 text-sm" style={{ color: "var(--foreground-muted)" }}>
              {lowCompleted} of {lowPriorityCount} completed
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
