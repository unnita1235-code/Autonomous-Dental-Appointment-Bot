/**
 * Chat open/close coordination.
 *
 * The ChatWidget owns the single source of truth for whether the chat panel is
 * open. This module lets presentation-only components (for example marketing
 * call-to-action buttons) request that the existing widget open itself,
 * without duplicating chat state or creating a second chat architecture.
 *
 * This intentionally does not store any state - it is a transient signal only.
 */

export const OPEN_CHAT_EVENT = "dentalflow:open-chat";
export const CLOSE_CHAT_EVENT = "dentalflow:close-chat";

/** Request that the existing ChatWidget open its panel. */
export function requestOpenChat(): void {
  if (typeof window === "undefined") {
    return;
  }
  window.dispatchEvent(new Event(OPEN_CHAT_EVENT));
}

/** Request that the existing ChatWidget close its panel. */
export function requestCloseChat(): void {
  if (typeof window === "undefined") {
    return;
  }
  window.dispatchEvent(new Event(CLOSE_CHAT_EVENT));
}