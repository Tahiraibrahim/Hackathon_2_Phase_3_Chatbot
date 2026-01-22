"use client";

import { useState, useEffect, FormEvent, useCallback } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Plus,
  X,
  ListTodo,
  CheckCircle2,
  Clock,
  TrendingUp,
  Filter,
  ChevronDown,
  Sparkles,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { taskApi, Task, Priority } from "@/lib/api";
import TaskCard from "@/components/TaskCard";
import Navbar from "@/components/Navbar";
import ChatDrawer from "@/components/ChatDrawer";
import { useAuth, useDisplayName } from "@/context/AuthContext";
import { useToast } from "@/context/NotificationContext";
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

export default function DashboardPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [filteredTasks, setFilteredTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<Priority>("MEDIUM");
  const [category, setCategory] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [editingTaskId, setEditingTaskId] = useState<number | null>(null);
  const [editedTitle, setEditedTitle] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [priorityFilter, setPriorityFilter] = useState<Priority | "All">("All");
  const [showFilterDropdown, setShowFilterDropdown] = useState(false);
  const router = useRouter();

  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const displayName = useDisplayName();
  const toast = useToast();

  // Get session token from Better Auth - Direct token passing
  const { data: session } = authClient.useSession();
  const sessionToken = session?.session?.token;

  // Check authentication on mount
  useEffect(() => {
    if (authLoading) return;

    if (!isAuthenticated) {
      // Fallback check
      const token = localStorage.getItem("authToken");
      // Agar user authenticated nahi hai, login pe bhejo
      router.push("/login");
    }
  }, [authLoading, isAuthenticated, router]);

  // Fetch tasks when session token becomes available
  useEffect(() => {
    if (authLoading) return;
    if (!isAuthenticated) return;
    if (!sessionToken) return;

    // Session token is now available, fetch tasks
    fetchTasks();
  }, [authLoading, isAuthenticated, sessionToken]);

  // Filter tasks based on search and priority
  useEffect(() => {
    const query = searchQuery.toLowerCase().trim();
    const priorityMatch = priorityFilter === "All" ? null : priorityFilter;

    const filtered = tasks.filter((task) => {
      const matchesSearch =
        query === "" ||
        task.title.toLowerCase().includes(query) ||
        (task.description && task.description.toLowerCase().includes(query)) ||
        (task.category && task.category.toLowerCase().includes(query));

      const matchesPriority = priorityMatch === null || task.priority === priorityMatch;

      return matchesSearch && matchesPriority;
    });

    setFilteredTasks(filtered);
  }, [tasks, searchQuery, priorityFilter]);

  const fetchTasks = async () => {
    // Prevent API call if session token is undefined
    if (!sessionToken) {
      console.warn("⚠️ fetchTasks called without session token");
      return;
    }

    try {
      setLoading(true);
      const data = await taskApi.getTasks(sessionToken);
      setTasks(data);
      setError("");
    } catch (err) {
      console.error("Fetch Error:", err);
      setError("Failed to load tasks. Ensure you are logged in and your token is valid.");
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query);
  }, []);

  const handleCreateTask = async (e: FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    setSubmitting(true);
    try {
      console.log("🔍 Form State - Priority:", priority);
      console.log("🔍 Form State - Title:", title);
      console.log("🔍 Form State - Full State:", { title, description, priority, category, dueDate });

      const taskData = {
        title: title.trim(),
        description: description.trim() || undefined,
        priority: priority,
        category: category.trim() || undefined,
        due_date: dueDate || undefined,
      };

      console.log("📤 Sending to API:", taskData);
      const newTask = await taskApi.createTask(sessionToken, taskData);
      console.log("✅ Task created with priority:", newTask.priority);

      setTasks([newTask, ...tasks]);
      setTitle("");
      setDescription("");
      setPriority("MEDIUM");
      setCategory("");
      setDueDate("");
      setError("");
      toast.success("Task created", `"${newTask.title}" has been added.`);
    } catch (err) {
      console.error("❌ Task creation error:", err);
      setError("Failed to create task.");
      toast.error("Error", "Failed to create task");
    } finally {
      setSubmitting(false);
    }
  };

  const handleToggleComplete = async (task: Task) => {
    try {
      const updatedTask = await taskApi.updateTask(task.id, sessionToken, {
        is_completed: !task.is_completed,
      });
      setTasks(tasks.map((t) => (t.id === task.id ? updatedTask : t)));

      if (updatedTask.is_completed) {
        toast.success("Completed", `"${task.title}" marked as complete.`);
      }
    } catch (err) {
      toast.error("Error", "Could not update task status.");
    }
  };

  const handleDeleteTask = async (taskId: number) => {
    try {
      await taskApi.deleteTask(taskId, sessionToken);
      setTasks(tasks.filter((t) => t.id !== taskId));
      toast.success("Deleted", "Task has been removed.");
    } catch (err) {
      toast.error("Error", "Could not delete task.");
    }
  };

  const handleStartEdit = (task: Task) => {
    setEditingTaskId(task.id);
    setEditedTitle(task.title);
  };

  const handleSaveEdit = async (taskId: number) => {
    if (!editedTitle.trim()) return;

    try {
      const updatedTask = await taskApi.updateTask(taskId, sessionToken, {
        title: editedTitle.trim(),
      });
      setTasks(tasks.map((t) => (t.id === taskId ? updatedTask : t)));
      setEditingTaskId(null);
      setEditedTitle("");
      toast.success("Updated", "Task title updated.");
    } catch (err) {
      toast.error("Error", "Could not save changes.");
    }
  };

  const handleCancelEdit = () => {
    setEditingTaskId(null);
    setEditedTitle("");
  };

  // Stats calculation
  const totalTasks = tasks.length;
  const completedTasks = tasks.filter((t) => t.is_completed).length;
  const pendingTasks = totalTasks - completedTasks;
  const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  if (authLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <>
      <Navbar onSearch={handleSearch} />

      {/* Main Content */}
      <div className="pt-20 min-h-screen p-6 lg:p-8">
        <div className="w-full space-y-8 overflow-y-auto">
        
        {/* Header Section */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col md:flex-row items-center justify-between gap-4"
        >
          <div>
            <h1 className="text-3xl font-bold text-white flex items-center gap-3">
              <Sparkles className="w-8 h-8 text-blue-400" />
              Dashboard
            </h1>
            <p className="mt-2" style={{ color: 'var(--foreground-muted)' }}>
              Welcome back, <span className="text-white font-medium">{displayName}</span>!
            </p>
          </div>
        </motion.div>

        {/* Error Message */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="badge-danger px-4 py-3 rounded-xl text-sm flex items-center justify-between"
            >
              <span>{error}</span>
              <button onClick={() => setError("")} className="hover:opacity-80">
                <X className="h-4 w-4" />
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Stats Row */}
        <motion.div
          className="grid grid-cols-1 md:grid-cols-3 gap-6"
          variants={containerVariants}
          initial="hidden"
          animate="show"
        >
          {/* Total */}
          <motion.div variants={itemVariants} className="glass-card-solid p-6 card-elevated transition-all duration-300 hover:scale-105 hover:shadow-lg hover:shadow-blue-500/50">
            <div className="flex justify-between">
              <div>
                <p className="text-sm font-medium opacity-70">Total Tasks</p>
                <p className="text-4xl font-bold text-white mt-2">{totalTasks}</p>
              </div>
              <div className="w-14 h-14 rounded-xl bg-blue-600 flex items-center justify-center">
                <ListTodo className="w-7 h-7 text-white" />
              </div>
            </div>
          </motion.div>

          {/* Completed */}
          <motion.div variants={itemVariants} className="glass-card-solid p-6 card-elevated transition-all duration-300 hover:scale-105 hover:shadow-lg hover:shadow-emerald-500/50">
            <div className="flex justify-between">
              <div>
                <p className="text-sm font-medium opacity-70">Completed</p>
                <p className="text-4xl font-bold text-white mt-2">{completedTasks}</p>
              </div>
              <div className="w-14 h-14 rounded-xl bg-emerald-600 flex items-center justify-center">
                <CheckCircle2 className="w-7 h-7 text-white" />
              </div>
            </div>
            <div className="mt-4 text-sm text-emerald-400 font-semibold">{completionRate}% done</div>
          </motion.div>

          {/* Pending */}
          <motion.div variants={itemVariants} className="glass-card-solid p-6 card-elevated transition-all duration-300 hover:scale-105 hover:shadow-lg hover:shadow-amber-500/50">
            <div className="flex justify-between">
              <div>
                <p className="text-sm font-medium opacity-70">Pending</p>
                <p className="text-4xl font-bold text-white mt-2">{pendingTasks}</p>
              </div>
              <div className="w-14 h-14 rounded-xl bg-amber-600 flex items-center justify-center">
                <Clock className="w-7 h-7 text-white" />
              </div>
            </div>
          </motion.div>
        </motion.div>

        {/* Create Task Form */}
        <motion.div className="glass-card p-8">
          <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
            <Plus className="w-5 h-5 text-blue-400" /> Create New Task
          </h2>
          <form onSubmit={handleCreateTask} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="md:col-span-2">
                <label className="block text-sm font-medium mb-2 opacity-70">Title *</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="input-dark w-full"
                  placeholder="Task title"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2 opacity-70">Priority</label>
                <select
                  value={priority}
                  onChange={(e) => {
                    const newPriority = e.target.value as Priority;
                    console.log("🔄 Priority changed from", priority, "to", newPriority);
                    setPriority(newPriority);
                  }}
                  className="select-dark w-full"
                >
                  <option value="HIGH">High</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="LOW">Low</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2 opacity-70">Category</label>
                <input
                  type="text"
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="input-dark w-full"
                  placeholder="Work, Personal"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2 opacity-70">Due Date</label>
                <input
                  type="date"
                  value={dueDate}
                  onChange={(e) => setDueDate(e.target.value)}
                  className="input-dark w-full"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium mb-2 opacity-70">Description</label>
                <textarea
                  rows={3}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="textarea-dark w-full"
                  placeholder="Optional description"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={submitting || !title.trim()}
              className="w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-4 rounded-xl transition-all"
            >
              {submitting ? "Adding..." : "Add Task"}
            </button>
          </form>
        </motion.div>

        {/* Task List */}
        <motion.div className="glass-card p-8">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-white">Your Tasks ({filteredTasks.length})</h2>
            <div className="relative">
                <button 
                    onClick={() => setShowFilterDropdown(!showFilterDropdown)}
                    className="flex items-center gap-2 text-sm bg-white/5 px-3 py-2 rounded-lg hover:bg-white/10"
                >
                    <Filter className="w-4 h-4" /> 
                    {priorityFilter === "All" ? "All" : priorityFilter}
                    <ChevronDown className="w-4 h-4" />
                </button>
                {showFilterDropdown && (
                    <div className="absolute right-0 mt-2 w-32 bg-gray-800 rounded-lg shadow-xl overflow-hidden z-10 border border-white/10">
                        {["All", "HIGH", "MEDIUM", "LOW"].map((opt) => (
                            <button
                                key={opt}
                                onClick={() => { setPriorityFilter(opt as any); setShowFilterDropdown(false); }}
                                className="w-full text-left px-4 py-2 text-sm hover:bg-white/10"
                            >
                                {opt}
                            </button>
                        ))}
                    </div>
                )}
            </div>
          </div>

          {loading ? (
             <div className="flex justify-center py-10"><div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500"></div></div>
          ) : filteredTasks.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-16 opacity-70"
            >
              <div className="w-16 h-16 mx-auto mb-4 rounded-full glass-card-solid flex items-center justify-center">
                <ListTodo className="w-8 h-8" style={{ color: 'var(--input-placeholder)' }} />
              </div>
              <p>No tasks found.</p>
              {(searchQuery.trim() || priorityFilter !== "All") && (
                <button
                  onClick={() => {
                    setSearchQuery("");
                    setPriorityFilter("All");
                  }}
                  className="mt-4 text-sm text-blue-400 hover:text-blue-300"
                >
                  Clear filters
                </button>
              )}
            </motion.div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
               <AnimatePresence mode="popLayout">
                {filteredTasks.map((task, index) => (
                  <TaskCard
                    key={task.id}
                    task={task}
                    index={index}
                    onToggleComplete={handleToggleComplete}
                    onDelete={handleDeleteTask}
                    onStartEdit={handleStartEdit}
                    editingTaskId={editingTaskId}
                    editedTitle={editedTitle}
                    onEditedTitleChange={setEditedTitle}
                    onSaveEdit={handleSaveEdit}
                    onCancelEdit={handleCancelEdit}
                  />
                ))}
              </AnimatePresence>
            </div>
          )}
        </motion.div>

        </div>
      </div>

      {/* AI Chat Drawer */}
      <ChatDrawer onTaskChange={fetchTasks} />
    </>
  );
}