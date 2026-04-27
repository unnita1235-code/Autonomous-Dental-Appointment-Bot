"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { MessageCircle } from "lucide-react";
import ChatPanel from "./ChatPanel";

export default function ChatWidget(): JSX.Element {
  const [isOpen, setIsOpen] = useState<boolean>(false);

  return (
    <div className="fixed bottom-4 right-4 z-50 sm:bottom-6 sm:right-6">
      <AnimatePresence>
        {isOpen ? (
          <motion.div
            key="chat-panel"
            initial={{ opacity: 0, y: 24, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 16, scale: 0.98 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
            className="fixed inset-0 overflow-hidden bg-white shadow-2xl sm:inset-auto sm:bottom-24 sm:right-6 sm:h-[560px] sm:w-[380px] sm:rounded-2xl"
          >
            <ChatPanel onClose={() => setIsOpen(false)} onMinimize={() => setIsOpen(false)} />
          </motion.div>
        ) : null}
      </AnimatePresence>

      <button
        type="button"
        onClick={() => setIsOpen(true)}
        aria-label="Open patient chat"
        className="inline-flex h-14 w-14 items-center justify-center rounded-full bg-primary text-white shadow-lg transition hover:bg-primary-hover"
      >
        <MessageCircle className="h-6 w-6" />
      </button>
    </div>
  );
}
