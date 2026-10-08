"use client";

import * as React from "react";

import { requestOpenChat } from "@/lib/chat-events";
import { Button, type ButtonProps } from "@/components/ui/button";

/**
 * A call-to-action button that opens the existing ChatWidget.
 *
 * This intentionally reuses the existing chat architecture: it emits a
 * transient signal that the already-mounted `ChatWidget` listens for, so no
 * second chat panel, chat state, or booking flow is introduced.
 *
 * Chat state (messages, conversation, Socket.IO) remains entirely inside
 * `ChatStore` / `ChatPanel` exactly as before.
 */
export type OpenChatButtonProps = Omit<ButtonProps, "onClick" | "type"> & {
  /**
   * Invoked after the open signal has been emitted.
   *
   * Use this for follow-up UI work (for example collapsing a mobile menu).
   * `onClick` is deliberately not exposed so callers cannot accidentally
   * replace the behaviour that opens the existing chat widget.
   */
  onOpened?: () => void;
};

export function OpenChatButton({
  children,
  className,
  onOpened,
  onMouseEnter,
  onMouseLeave,
  onFocus,
  onBlur,
  ...props
}: OpenChatButtonProps): JSX.Element {
  const handleOpen = React.useCallback(() => {
    requestOpenChat();
    onOpened?.();
  }, [onOpened]);

  return (
    <Button
      type="button"
      onClick={handleOpen}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      onFocus={onFocus}
      onBlur={onBlur}
      {...props}
    >
      {children}
    </Button>
  );
}

export default OpenChatButton;