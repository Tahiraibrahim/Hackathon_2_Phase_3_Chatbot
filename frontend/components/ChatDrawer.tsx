"use client";

import { useState } from "react";
import { Bot, X } from "lucide-react";
import FloatingActionButton from "./ui/FloatingActionButton";
import Sheet from "./ui/Sheet";
import ChatInterface from "./ChatInterface";

interface ChatDrawerProps {
  onTaskChange?: () => void;
}

export default function ChatDrawer({ onTaskChange }: ChatDrawerProps) {
  const [isOpen, setIsOpen] = useState(false);

  const toggleDrawer = () => {
    setIsOpen(!isOpen);
  };

  return (
    <>
      <FloatingActionButton
        onClick={toggleDrawer}
        icon={isOpen ? X : Bot}
        isOpen={isOpen}
        ariaLabel={isOpen ? "Close AI Chat Assistant" : "Open AI Chat Assistant"}
      />

      <Sheet isOpen={isOpen} onClose={() => setIsOpen(false)}>
        <div className="h-full flex flex-col">
          {/* Header */}
          <div className="flex items-center gap-3 px-6 py-4 border-b border-[var(--glass-border)]">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white">AI Assistant</h2>
              <p className="text-sm text-gray-400">Ask me anything about your tasks</p>
            </div>
          </div>

          {/* ChatInterface fills remaining space */}
          <div className="flex-1 overflow-hidden">
            <ChatInterface onTaskChange={onTaskChange} />
          </div>
        </div>
      </Sheet>
    </>
  );
}
