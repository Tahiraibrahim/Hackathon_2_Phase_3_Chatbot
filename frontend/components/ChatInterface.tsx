"use client";

import { useEffect, useRef, useState } from "react";
import { useChat } from "ai/react";
import { motion, AnimatePresence } from "framer-motion";
import { Bot, User, Send, AlertCircle, Mic, MicOff } from "lucide-react";
import { authClient } from "@/lib/auth-client";

interface ChatInterfaceProps {
  onTaskChange?: () => void;
}

export default function ChatInterface({ onTaskChange }: ChatInterfaceProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Voice recording state
  const [isRecording, setIsRecording] = useState(false);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const [isSupported, setIsSupported] = useState(false);

  // Get session data from Better Auth
  const { data: session } = authClient.useSession();
  const sessionToken = session?.session?.token;

  /**
   * Helper function to extract token from browser cookies
   * Fallback mechanism when authClient.getSession() fails
   */
  const getTokenFromCookie = (): string | null => {
    if (typeof window === "undefined" || typeof document === "undefined") {
      return null;
    }

    try {
      const cookies = document.cookie.split('; ');

      // Try multiple cookie name patterns
      const patterns = [
        'better-auth.session_token',
        'session_token',
        'authjs.session-token',
      ];

      for (const pattern of patterns) {
        const cookie = cookies.find(row => row.startsWith(`${pattern}=`));
        if (cookie) {
          const token = cookie.split('=')[1];
          // Decode URL-encoded token (fixes %3D and other encoding issues)
          return decodeURIComponent(token);
        }
      }

      return null;
    } catch (error) {
      console.error("Failed to parse cookies:", error);
      return null;
    }
  };

  const { messages, input, handleInputChange, handleSubmit, isLoading, error } = useChat({
    api: "/api/chat",
    // Custom fetch with 30-second timeout and dynamic Authorization header
    fetch: async (input, init) => {
      // Get token dynamically
      let token: string | null | undefined = sessionToken;

      // FALLBACK: If no token from hook, try reading from cookies directly
      if (!token) {
        console.warn("⚠️ No token from session hook, attempting cookie fallback...");
        token = getTokenFromCookie();

        if (token) {
          console.log("✅ Token recovered from cookie fallback!");
        }
      }

      // BLOCK REQUEST if no token is available
      if (!token) {
        console.error("❌ CRITICAL: No authentication token available");
        throw new Error("Authentication required. Please log in again.");
      }

      console.log("✅ ChatInterface - Token Present:", !!token, "Length:", token.length);

      // Add Authorization header to the request
      const headers = new Headers(init?.headers);
      headers.set("Authorization", `Bearer ${token}`);

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 seconds

      try {
        const response = await fetch(input, {
          ...init,
          headers,
          signal: controller.signal,
        });
        clearTimeout(timeoutId);
        return response;
      } catch (error: any) {
        clearTimeout(timeoutId);

        // Provide user-friendly error messages
        if (error.name === 'AbortError') {
          throw new Error('Request timed out. The server is taking too long to respond. Please try again.');
        }

        // Handle JSON parsing errors
        if (error instanceof SyntaxError && error.message.includes('JSON')) {
          throw new Error('Network slow, incomplete response received. Please try again.');
        }

        throw error;
      }
    },
    onError: (error) => {
      console.error("Chat Error:", error);
    },
    onFinish: (message) => {
      // Check if any tools were invoked (more reliable than text parsing)
      const hasToolInvocations = (message as any).toolInvocations?.length > 0;

      if (hasToolInvocations) {
        const toolNames = (message as any).toolInvocations.map((t: any) => t.toolName);
        console.log("Tools invoked:", toolNames);

        // Check if task-related tools were called
        if (toolNames.some((name: string) =>
          name.includes("add_task") ||
          name.includes("create_task") ||
          name.includes("update_task") ||
          name.includes("delete_task")
        )) {
          console.log("Task operation detected, triggering refresh...");
          onTaskChange?.();
        }
      } else {
        // Fallback: Check message content for task operations
        const content = message.content.toLowerCase();
        if (
          content.includes("task") &&
          (content.includes("added") || content.includes("created") || content.includes("successfully"))
        ) {
          console.log("Task operation detected via content, triggering refresh...");
          onTaskChange?.();
        }
      }
    },
    initialMessages: [
      {
        id: "welcome",
        role: "assistant",
        content: "Hello! I'm your AI assistant. I can help you manage your tasks, answer questions, or just chat. What would you like to do today?",
      },
    ],
  });

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Initialize Speech Recognition
  useEffect(() => {
    const SpeechRecognition =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition;

    if (SpeechRecognition) {
      const recognitionInstance = new SpeechRecognition();
      recognitionInstance.continuous = false;
      recognitionInstance.interimResults = false;
      recognitionInstance.lang = 'en-US';

      recognitionInstance.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        handleInputChange({ target: { value: transcript } } as any);
        setIsRecording(false);
      };

      recognitionInstance.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsRecording(false);

        if (event.error === 'not-allowed') {
          alert('Microphone access denied. Please enable microphone permissions.');
        } else if (event.error === 'no-speech') {
          alert('No speech detected. Please try again.');
        }
      };

      recognitionInstance.onend = () => {
        setIsRecording(false);
      };

      recognitionRef.current = recognitionInstance;
      setIsSupported(true);
    } else {
      setIsSupported(false);
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  const toggleVoiceRecording = () => {
    if (!recognitionRef.current || !isSupported) {
      alert('Voice input is not supported in your browser.');
      return;
    }

    if (isRecording) {
      recognitionRef.current.stop();
      setIsRecording(false);
    } else {
      try {
        recognitionRef.current.start();
        setIsRecording(true);
      } catch (error) {
        console.error('Failed to start recognition:', error);
        setIsRecording(false);
      }
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className="h-full flex flex-col rounded-xl overflow-hidden shadow-2xl border border-white/10 bg-gradient-to-b from-gray-900/95 to-gray-800/95 backdrop-blur-xl"
    >
      {/* Chat Header with Glassmorphism */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="px-6 py-5 flex items-center gap-3 border-b border-white/10 backdrop-blur-xl bg-white/5"
        style={{
          boxShadow: "0 4px 24px rgba(0, 0, 0, 0.1)",
        }}
      >
        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 flex items-center justify-center shadow-lg shadow-purple-500/30">
          <Bot className="w-6 h-6 text-white" />
        </div>
        <div>
          <h3 className="text-xl font-bold text-white tracking-tight">AI Assistant</h3>
          <p className="text-xs text-gray-300 font-medium">Always here to help</p>
        </div>
      </motion.div>

      {/* Error Banner */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="bg-red-500/10 border-b border-red-500/20 px-4 py-3 flex items-center gap-2 text-red-400 text-sm"
          >
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error.message || "An error occurred"}</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4 custom-scrollbar">
        <AnimatePresence initial={false}>
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.3 }}
              className={`flex items-end gap-2 ${
                msg.role === "user" ? "flex-row-reverse" : "flex-row"
              }`}
            >
              {/* Avatar */}
              <div
                className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  msg.role === "user"
                    ? "bg-gradient-to-br from-indigo-500 to-purple-600 shadow-lg shadow-indigo-500/30"
                    : "bg-gradient-to-br from-blue-500 to-cyan-500 shadow-lg shadow-blue-500/30"
                }`}
              >
                {msg.role === "user" ? (
                  <User className="w-4 h-4 text-white" />
                ) : (
                  <Bot className="w-4 h-4 text-white" />
                )}
              </div>

              {/* Message Bubble */}
              <div
                className={`max-w-[70%] rounded-2xl px-4 py-3 ${
                  msg.role === "user" ? "user-message" : "ai-message"
                }`}
              >
                <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">
                  {msg.content}
                </p>
                <span
                  className={`text-xs mt-1 block ${
                    msg.role === "user" ? "text-white/60" : "text-gray-500"
                  }`}
                >
                  {new Date().toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </span>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Typing Indicator */}
        {isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="flex items-end gap-2"
          >
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-blue-500/30">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <div className="bg-gray-200 rounded-2xl px-4 py-3 shadow-md">
              <div className="flex gap-1">
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ repeat: Infinity, duration: 0.8, delay: 0 }}
                  className="w-2 h-2 bg-gray-600 rounded-full"
                />
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ repeat: Infinity, duration: 0.8, delay: 0.2 }}
                  className="w-2 h-2 bg-gray-600 rounded-full"
                />
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ repeat: Infinity, duration: 0.8, delay: 0.4 }}
                  className="w-2 h-2 bg-gray-600 rounded-full"
                />
              </div>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-white/10 p-4 bg-gray-900/50 backdrop-blur-sm">
        <form onSubmit={handleSubmit} className="flex items-center gap-3">
          {/* Voice Input Button */}
          {isSupported && (
            <motion.button
              type="button"
              onClick={toggleVoiceRecording}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              disabled={isLoading}
              className={`voice-button ${isRecording ? 'recording' : ''}`}
              aria-label={isRecording ? "Stop recording" : "Start voice input"}
            >
              {isRecording ? (
                <MicOff className="w-5 h-5" />
              ) : (
                <Mic className="w-5 h-5" />
              )}
            </motion.button>
          )}

          <input
            type="text"
            value={input}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            disabled={isLoading}
            className="modern-input"
          />
          <motion.button
            type="submit"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            disabled={isLoading || !input.trim()}
            className="send-button"
            aria-label="Send message"
          >
            <Send className="w-5 h-5" />
          </motion.button>
        </form>
      </div>

      {/* Custom Styles with Crucial Overrides */}
      <style jsx global>{`
        /* User Message - Deep Blue/Purple Gradient with White Text & Glow */
        .user-message {
          background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
          color: white !important;
          box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4),
            0 8px 40px rgba(79, 70, 229, 0.3) !important;
        }

        /* AI Message - Light Gray/White with Dark Text & Soft Shadow */
        .ai-message {
          background: linear-gradient(135deg, #f9fafb, #ffffff) !important;
          color: #1f2937 !important;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08),
            0 4px 20px rgba(0, 0, 0, 0.05) !important;
        }

        /* System Message - Red-tinted for errors */
        .system-message {
          background: linear-gradient(135deg, #fee2e2, #fecaca) !important;
          color: #991b1b !important;
          box-shadow: 0 2px 10px rgba(239, 68, 68, 0.15) !important;
        }

        /* Modern Input Field with Colorful Focus Effect */
        .modern-input {
          flex: 1;
          background: rgba(255, 255, 255, 0.05) !important;
          border: 2px solid rgba(255, 255, 255, 0.1) !important;
          border-radius: 1.5rem !important;
          padding: 0.875rem 1.25rem !important;
          color: white !important;
          font-size: 0.95rem !important;
          outline: none !important;
          transition: all 0.3s ease !important;
        }

        .modern-input:focus {
          background: rgba(255, 255, 255, 0.08) !important;
          border-color: #6366f1 !important;
          box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15),
            0 4px 20px rgba(99, 102, 241, 0.25) !important;
        }

        .modern-input::placeholder {
          color: rgba(255, 255, 255, 0.4) !important;
        }

        .modern-input:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        /* Send Button with Gradient & Animation */
        .send-button {
          background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
          color: white !important;
          border: none !important;
          border-radius: 50% !important;
          width: 48px !important;
          height: 48px !important;
          display: flex !important;
          align-items: center !important;
          justify-content: center !important;
          cursor: pointer !important;
          transition: all 0.2s ease !important;
          box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4) !important;
        }

        .send-button:hover:not(:disabled) {
          background: linear-gradient(135deg, #4f46e5, #4338ca) !important;
          box-shadow: 0 6px 25px rgba(99, 102, 241, 0.5) !important;
        }

        .send-button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        /* Voice Button Styles */
        .voice-button {
          background: linear-gradient(135deg, #10b981, #059669) !important;
          color: white !important;
          border: none !important;
          border-radius: 50% !important;
          width: 48px !important;
          height: 48px !important;
          display: flex !important;
          align-items: center !important;
          justify-content: center !important;
          cursor: pointer !important;
          transition: all 0.2s ease !important;
          box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4) !important;
        }

        .voice-button:hover:not(:disabled) {
          background: linear-gradient(135deg, #059669, #047857) !important;
          box-shadow: 0 6px 25px rgba(16, 185, 129, 0.5) !important;
        }

        .voice-button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .voice-button.recording {
          background: linear-gradient(135deg, #ef4444, #dc2626) !important;
          box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4) !important;
          animation: pulse-recording 1.5s ease-in-out infinite;
        }

        @keyframes pulse-recording {
          0%, 100% {
            box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
            transform: scale(1);
          }
          50% {
            box-shadow: 0 6px 30px rgba(239, 68, 68, 0.8);
            transform: scale(1.05);
          }
        }

        /* Custom Scrollbar */
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }

        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 10px;
        }

        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.15);
          border-radius: 10px;
        }

        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(255, 255, 255, 0.25);
        }

        /* Ensure text visibility */
        .user-message * {
          color: white !important;
        }

        .ai-message * {
          color: #1f2937 !important;
        }

        .system-message * {
          color: #991b1b !important;
        }
      `}</style>
    </motion.div>
  );
}
