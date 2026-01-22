"use client";

import { motion } from "framer-motion";
import { Check, Trash2, Pencil, Calendar, Tag, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { Task, Priority } from "@/lib/api";

interface TaskCardProps {
  task: Task;
  index: number;
  onToggleComplete: (task: Task) => void;
  onDelete: (taskId: number) => void;
  onStartEdit: (task: Task) => void;
  editingTaskId: number | null;
  editedTitle: string;
  onEditedTitleChange: (title: string) => void;
  onSaveEdit: (taskId: number) => void;
  onCancelEdit: () => void;
}

const priorityConfig = {
  HIGH: {
    textColor: "text-white",
    bgColor: "bg-red-500/90",
    borderColor: "border-red-400/50",
    glowColor: "hover:shadow-red-500/20",
    icon: AlertCircle,
  },
  MEDIUM: {
    textColor: "text-white",
    bgColor: "bg-amber-500/90",
    borderColor: "border-amber-400/50",
    glowColor: "hover:shadow-amber-500/20",
    icon: Tag,
  },
  LOW: {
    textColor: "text-white",
    bgColor: "bg-emerald-500/90",
    borderColor: "border-emerald-400/50",
    glowColor: "hover:shadow-emerald-500/20",
    icon: Tag,
  },
};

export default function TaskCard({
  task,
  index,
  onToggleComplete,
  onDelete,
  onStartEdit,
  editingTaskId,
  editedTitle,
  onEditedTitleChange,
  onSaveEdit,
  onCancelEdit,
}: TaskCardProps) {
  const priorityStyle = priorityConfig[task.priority] || priorityConfig["MEDIUM"];
  const PriorityIcon = priorityStyle.icon;

  const formatDate = (dateString: string | null) => {
    if (!dateString) return null;
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  const isOverdue = (dateString: string | null) => {
    if (!dateString || task.is_completed) return false;
    return new Date(dateString) < new Date();
  };

  return (
    <motion.div
      key={task.id}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ delay: index * 0.05, duration: 0.3 }}
      whileHover={{
        scale: 1.02,
        y: -4,
        transition: { duration: 0.2 }
      }}
      className={cn(
        "group glass-card-solid p-5 transition-all duration-300",
        "hover:border-blue-500/30",
        "hover:shadow-xl hover:shadow-blue-500/10",
        priorityStyle.glowColor,
        task.is_completed && "opacity-60"
      )}
    >

      <div className="flex items-start gap-4">
        {/* Checkbox */}
        <motion.button
          onClick={() => onToggleComplete(task)}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          className={cn(
            "flex-shrink-0 mt-1 h-6 w-6 rounded-md border-2 flex items-center justify-center",
            "transition-all duration-300 focus:outline-none",
            task.is_completed
              ? "bg-emerald-500 border-emerald-400"
              : "border-slate-500 hover:border-blue-400 hover:bg-slate-700/50"
          )}
        >
          {task.is_completed && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 500, damping: 15 }}
            >
              <Check className="h-3.5 w-3.5 text-white" />
            </motion.div>
          )}
        </motion.button>

        {/* Task Content */}
        <div className="flex-1 min-w-0">
          {editingTaskId === task.id ? (
            <div className="space-y-3">
              <input
                type="text"
                value={editedTitle}
                onChange={(e) => onEditedTitleChange(e.target.value)}
                className="input-dark w-full"
                autoFocus
              />
              <div className="flex gap-2">
                <motion.button
                  onClick={() => onSaveEdit(task.id)}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="btn-primary px-4 py-2 text-sm"
                >
                  Save
                </motion.button>
                <motion.button
                  onClick={onCancelEdit}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="btn-secondary px-4 py-2 text-sm"
                >
                  Cancel
                </motion.button>
              </div>
            </div>
          ) : (
            <>
              {/* Title */}
              <h3
                className={cn(
                  "text-base font-semibold transition-all duration-300 mb-1",
                  task.is_completed
                    ? "line-through text-slate-500"
                    : "text-white"
                )}
              >
                {task.title}
              </h3>

              {/* Description */}
              {task.description && (
                <p
                  className={cn(
                    "text-sm mb-3 transition-all duration-300",
                    task.is_completed ? "text-slate-600" : "text-slate-400"
                  )}
                >
                  {task.description}
                </p>
              )}

              {/* Metadata Row - Priority Badges as Pills */}
              <div className="flex flex-wrap items-center gap-2 mt-3">
                {/* Priority Badge - Pill Style */}
                <span
                  className={cn(
                    "inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold",
                    priorityStyle.bgColor,
                    priorityStyle.textColor
                  )}
                >
                  <PriorityIcon className="w-3 h-3" />
                  {task.priority}
                </span>

                {/* Category Badge */}
                {task.category && (
                  <span className="badge-info inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium">
                    <Tag className="w-3 h-3" />
                    {task.category}
                  </span>
                )}

                {/* Due Date Badge */}
                {task.due_date && (
                  <span
                    className={cn(
                      "inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium",
                      isOverdue(task.due_date)
                        ? "badge-danger"
                        : "badge-neutral"
                    )}
                  >
                    <Calendar className="w-3 h-3" />
                    {formatDate(task.due_date)}
                    {isOverdue(task.due_date) && " (Overdue)"}
                  </span>
                )}
              </div>
            </>
          )}
        </div>

        {/* Action Buttons */}
        {editingTaskId !== task.id && (
          <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            {/* Edit Button */}
            <motion.button
              onClick={() => onStartEdit(task)}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              className={cn(
                "flex-shrink-0 p-2 text-slate-500 hover:text-blue-400 rounded-lg",
                "transition-all duration-200 focus:outline-none",
                "hover:bg-blue-500/10"
              )}
              title="Edit task"
            >
              <Pencil className="h-4 w-4" />
            </motion.button>

            {/* Delete Button */}
            <motion.button
              onClick={() => onDelete(task.id)}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              className={cn(
                "flex-shrink-0 p-2 text-slate-500 hover:text-red-400 rounded-lg",
                "transition-all duration-200 focus:outline-none",
                "hover:bg-red-500/10"
              )}
              title="Delete task"
            >
              <Trash2 className="h-4 w-4" />
            </motion.button>
          </div>
        )}
      </div>
    </motion.div>
  );
}
