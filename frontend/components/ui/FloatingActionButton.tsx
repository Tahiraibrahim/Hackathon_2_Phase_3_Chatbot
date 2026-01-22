"use client";

import { motion, AnimatePresence } from "framer-motion";
import { LucideIcon } from "lucide-react";

interface FloatingActionButtonProps {
  onClick: () => void;
  icon: LucideIcon;
  ariaLabel: string;
  isOpen?: boolean;
}

export default function FloatingActionButton({
  onClick,
  icon: Icon,
  ariaLabel,
  isOpen = false,
}: FloatingActionButtonProps) {
  return (
    <motion.button
      onClick={onClick}
      aria-label={ariaLabel}
      whileHover={{ scale: 1.1, rotate: isOpen ? 0 : 5 }}
      whileTap={{ scale: 0.95 }}
      animate={{
        rotate: isOpen ? 90 : 0,
      }}
      transition={{ duration: 0.3 }}
      className="fixed bottom-24 right-8 w-16 h-16 lg:w-18 lg:h-18 rounded-full shadow-2xl flex items-center justify-center transition-all duration-300"
      style={{
        background: isOpen
          ? "linear-gradient(135deg, #ef4444 0%, #dc2626 100%)"
          : "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        backdropFilter: "blur(16px)",
        border: "1px solid rgba(255, 255, 255, 0.1)",
        boxShadow: isOpen
          ? "0 8px 32px rgba(239, 68, 68, 0.4)"
          : "0 8px 32px rgba(102, 126, 234, 0.4)",
        zIndex: 55,
      }}
    >
      <AnimatePresence mode="wait">
        <motion.div
          key={isOpen ? "close" : "open"}
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          exit={{ scale: 0, rotate: 180 }}
          transition={{ duration: 0.2 }}
        >
          <Icon className="w-8 h-8 text-white" />
        </motion.div>
      </AnimatePresence>
    </motion.button>
  );
}
