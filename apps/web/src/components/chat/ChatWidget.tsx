"use client";

import * as React from "react";
import { AnimatePresence, motion } from "framer-motion";
import { cn } from "@/lib/design-system";
import { DentalFlowAvatar } from "@/components/branding";
import { AISparkle } from "@/components/ai/AIIndicator";
import { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider } from "@/components/ui/tooltip";
import { OPEN_CHAT_EVENT, CLOSE_CHAT_EVENT } from "@/lib/chat-events";
import ChatPanel from "./ChatPanel";

export default function ChatWidget(): JSX.Element {
  const [isOpen, setIsOpen] = React.useState<boolean>(false);
  const [showTooltip, setShowTooltip] = React.useState(false);
  const launcherRef = React.useRef<HTMLButtonElement | null>(null);
  const panelRef = React.useRef<HTMLDivElement | null>(null);
  const shouldRestoreFocusRef = React.useRef<boolean>(false);

  // Focus is only restored once the panel has actually unmounted, so keyboard
  // users are never left inside a panel that is animating out.
  const setPanelNode = React.useCallback((node: HTMLDivElement | null) => {
    panelRef.current = node;
    if (node === null && shouldRestoreFocusRef.current) {
      shouldRestoreFocusRef.current = false;
      launcherRef.current?.focus();
    }
  }, []);

  // Single source of truth for opening/closing stays here.
  const openChat = React.useCallback((): void => {
    shouldRestoreFocusRef.current = true;
    setIsOpen(true);
  }, []);

  const closeChat = React.useCallback((): void => {
    setIsOpen(false);
  }, []);

  // Allow presentation-only components to open this widget without creating a
  // second chat instance. State ownership stays here.
  React.useEffect(() => {
    window.addEventListener(OPEN_CHAT_EVENT, openChat);
    window.addEventListener(CLOSE_CHAT_EVENT, closeChat);

    return () => {
      window.removeEventListener(OPEN_CHAT_EVENT, openChat);
      window.removeEventListener(CLOSE_CHAT_EVENT, closeChat);
    };
  }, [openChat, closeChat]);

  // Move focus into the panel when it opens.
  React.useEffect(() => {
    if (isOpen) {
      panelRef.current?.focus();
    }
  }, [isOpen]);

  // Escape closes the panel from anywhere inside it.
  React.useEffect(() => {
    if (!isOpen) {
      return;
    }

    const handleKeyDown = (event: KeyboardEvent): void => {
      if (event.key === "Escape") {
        closeChat();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, closeChat]);

  return (
    <TooltipProvider>
      <div className="fixed bottom-4 right-4 z-50 sm:bottom-6 sm:right-6">
        <Tooltip open={showTooltip} onOpenChange={setShowTooltip}>
          <TooltipTrigger asChild>
            <button
              ref={launcherRef}
              type="button"
              onClick={openChat}
              onMouseEnter={() => setShowTooltip(true)}
              onMouseLeave={() => setShowTooltip(false)}
              aria-expanded={isOpen}
              aria-controls={isOpen ? "dentalflow-chat-panel" : undefined}
              aria-label="Open DentalFlow AI chat"
              className={cn(
                "relative inline-flex h-14 w-14 items-center justify-center rounded-full",
                "bg-patient-primary text-patient-on-primary shadow-elevation-2",
                "transition-all duration-200 hover:bg-patient-primary-hover hover:shadow-elevation-3",
                "active:scale-95 focus-visible:ring-4 focus-visible:ring-patient-primary/20"
              )}
            >
              <DentalFlowAvatar
                size="lg"
                variant="primary"
                online={true}
                fallback="AI"
                className="relative"
              >
                <AISparkle size="xs" className="absolute -bottom-1 -right-1" animated={true} />
              </DentalFlowAvatar>
            </button>
          </TooltipTrigger>
          <TooltipContent side="left" align="center" className="max-w-xs">
            <p className="text-sm font-medium">Chat with DentalFlow AI</p>
          </TooltipContent>
        </Tooltip>

        <AnimatePresence>
          {isOpen ? (
            <motion.div
              key="chat-panel"
              id="dentalflow-chat-panel"
              ref={setPanelNode}
              tabIndex={-1}
              role="dialog"
              aria-modal="false"
              aria-label="DentalFlow AI chat"
              initial={{ opacity: 0, y: 24, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 16, scale: 0.98 }}
              transition={{ duration: 0.2, ease: "easeOut" }}
              className="fixed inset-0 overflow-hidden bg-patient-surface-lowest shadow-elevation-4 sm:inset-auto sm:bottom-24 sm:right-6 sm:h-[580px] sm:w-[380px] sm:rounded-3xl"
            >
              <ChatPanel onClose={closeChat} onMinimize={closeChat} />
            </motion.div>
          ) : null}
        </AnimatePresence>
      </div>
    </TooltipProvider>
  );
}