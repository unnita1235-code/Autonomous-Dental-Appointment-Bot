"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { Mic, Paperclip, Send, X, Smile, Image, FileText, Mic2 } from "lucide-react";

import { cn } from "@/lib/design-system";
import { Button } from "@/components/ui/button";

/* ============================================================
   Types
   ============================================================ */

export interface ChatComposerProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: (value: string) => void;
  onAttachFile?: () => void;
  onRecordVoice?: () => void;
  onEmojiClick?: () => void;
  disabled?: boolean;
  loading?: boolean;
  placeholder?: string;
  maxLength?: number;
  showAttachments?: boolean;
  showVoice?: boolean;
  showEmoji?: boolean;
  autoFocus?: boolean;
  variant?: "patient" | "staff";
  className?: string;
}

const composerVariants = cva(
  "flex items-end gap-2 w-full transition-all duration-200",
  {
    variants: {
      variant: {
        patient: "bg-patient-surface-lowest rounded-full p-1.5 shadow-elevation-1",
        staff: "bg-staff-surface rounded-xl p-2 shadow-elevation-0 border border-staff-border",
      },
    },
    defaultVariants: {
      variant: "patient",
    },
  }
);

const inputVariants = cva(
  "min-w-0 flex-1 bg-transparent border-none outline-none resize-none text-body-md leading-relaxed",
  {
    variants: {
      variant: {
        patient: "min-h-[44px] max-h-[120px] px-3 py-2 text-patient-on-surface placeholder-patient-on-surface-variant",
        staff: "min-h-[32px] max-h-[100px] px-2 py-1.5 text-sm text-staff-on-surface placeholder-staff-on-surface-muted",
      },
    },
    defaultVariants: {
      variant: "patient",
    },
  }
);

const actionButtonVariants = cva(
  "flex-shrink-0 flex items-center justify-center rounded-full transition-all duration-200",
  {
    variants: {
      variant: {
        patient: "w-10 h-10 text-patient-on-surface-variant hover:bg-patient-surface-variant hover:text-patient-primary",
        staff: "w-9 h-9 text-staff-on-surface-muted hover:bg-staff-surface-variant hover:text-staff-primary",
      },
      active: {
        true: "bg-patient-primary/10 text-patient-primary",
        false: "",
      },
    },
    defaultVariants: {
      variant: "patient",
      active: false,
    },
  }
);

const sendButtonVariants = cva(
  "flex-shrink-0 flex items-center justify-center rounded-full shadow-sm transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed",
  {
    variants: {
      variant: {
        patient: "w-10 h-10 bg-patient-primary text-patient-on-primary hover:bg-patient-primary-hover active:scale-95",
        staff: "w-9 h-9 bg-staff-primary text-staff-on-primary hover:bg-staff-primary-hover active:scale-95",
      },
    },
    defaultVariants: {
      variant: "patient",
    },
  }
);

const attachmentPreviewVariants = cva(
  "flex items-center gap-2 px-3 py-2 rounded-xl bg-patient-surface-lowest border border-patient-outline-variant",
  {
    variants: {
      variant: {
        patient: "",
        staff: "bg-staff-surface border-staff-border",
      },
    },
    defaultVariants: {
      variant: "patient",
    },
  }
);

interface AttachmentPreview {
  id: string;
  type: "image" | "file" | "audio";
  name: string;
  url: string;
  thumbnailUrl?: string;
  size?: number;
}

/* ============================================================
   ChatComposer Component
   ============================================================ */

const ChatComposer = React.forwardRef<HTMLFormElement, ChatComposerProps>(
  (
    {
      value,
      onChange,
      onSubmit,
      onAttachFile,
      onRecordVoice,
      onEmojiClick,
      disabled = false,
      loading = false,
      placeholder = "Type a message...",
      maxLength = 4000,
      showAttachments = true,
      showVoice = true,
      showEmoji = true,
      autoFocus = false,
      variant = "patient",
      className,
      ...props
    },
    ref
  ) => {
    const textareaRef = React.useRef<HTMLTextAreaElement>(null);
    const [attachments, setAttachments] = React.useState<AttachmentPreview[]>([]);
    const [showAttachmentPreview, setShowAttachmentPreview] = React.useState(false);
    const [isRecording, setIsRecording] = React.useState(false);

    const prefersReducedMotion = React.useMemo(
      () => typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches,
      []
    );

    const handleSubmit = (e: React.FormEvent) => {
      e.preventDefault();
      const trimmed = value.trim();
      if (!trimmed && attachments.length === 0) return;
      if (loading) return;
      onSubmit(trimmed);
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSubmit(e);
      }
    };

    const handleAttachFile = () => {
      onAttachFile?.();
    };

    const handleVoiceStart = () => {
      if (onRecordVoice) {
        setIsRecording(true);
        onRecordVoice();
      }
    };

    const handleVoiceEnd = () => {
      setIsRecording(false);
    };

    const removeAttachment = (id: string) => {
      setAttachments((prev) => prev.filter((a) => a.id !== id));
    };

    const formatFileSize = (bytes: number) => {
      if (bytes < 1024) return `${bytes} B`;
      if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
      return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    };

    return (
      <form
        ref={ref}
        onSubmit={handleSubmit}
        className={cn(composerVariants({ variant }), className)}
        {...props}
      >
        {/* Attachment Preview Bar */}
        {(attachments.length > 0 || showAttachmentPreview) && (
          <div
            className={cn(
              "absolute bottom-full left-0 right-0 mb-2 animate-in slide-in-from-bottom-2 fade-in",
              prefersReducedMotion && "animate-none"
            )}
            role="region"
            aria-label="Attachments"
          >
            <div className={cn("flex flex-wrap gap-2 px-2", variant === "patient" && "pb-1")}>
              {attachments.map((attachment) => (
                <div
                  key={attachment.id}
                  className={cn(attachmentPreviewVariants({ variant }))}
                >
                  {attachment.type === "image" && attachment.thumbnailUrl && (
                    <img
                      src={attachment.thumbnailUrl}
                      alt={attachment.name}
                      className="w-12 h-12 rounded-lg object-cover flex-shrink-0"
                    />
                  )}
                  {attachment.type !== "image" && (
                    <div className="w-12 h-12 rounded-lg bg-patient-primary-container/50 flex items-center justify-center flex-shrink-0">
                      {attachment.type === "audio" ? (
                        <Mic2 className="h-5 w-5 text-patient-primary" />
                      ) : (
                        <FileText className="h-5 w-5 text-patient-primary" />
                      )}
                    </div>
                  )}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{attachment.name}</p>
                    {attachment.size && (
                      <p className="text-[11px] text-patient-on-surface-variant">{formatFileSize(attachment.size)}</p>
                    )}
                  </div>
                  <button
                    type="button"
                    onClick={() => removeAttachment(attachment.id)}
                    className="p-1 rounded-lg text-patient-on-surface-variant hover:text-staff-error hover:bg-staff-error-container/20 transition-colors"
                    aria-label={`Remove ${attachment.name}`}
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Main Composer Row */}
        <div className="flex min-w-0 items-end gap-2">
          {/* Emoji Button */}
          {showEmoji && (
            <button
              type="button"
              onClick={() => onEmojiClick?.()}
              disabled={disabled || loading}
              className={cn(actionButtonVariants({ variant, active: false }))}
              aria-label="Add emoji"
            >
              <Smile className="h-5 w-5" />
            </button>
          )}

          {/* Attachment Button */}
          {showAttachments && (
            <button
              type="button"
              onClick={handleAttachFile}
              disabled={disabled || loading}
              className={cn(actionButtonVariants({ variant, active: attachments.length > 0 }))}
              aria-label="Attach file"
            >
              <Paperclip className="h-5 w-5" />
            </button>
          )}

          {/* Voice Recording Button */}
          {showVoice && (
            <button
              type="button"
              onMouseDown={handleVoiceStart}
              onMouseUp={handleVoiceEnd}
              onMouseLeave={handleVoiceEnd}
              onTouchStart={handleVoiceStart}
              onTouchEnd={handleVoiceEnd}
              disabled={disabled || loading}
              className={cn(
                actionButtonVariants({ variant, active: isRecording }),
                isRecording && "animate-pulse bg-staff-error/10 text-staff-error"
              )}
              aria-label={isRecording ? "Stop recording" : "Record voice message"}
              aria-pressed={isRecording}
            >
              {isRecording ? (
                <Mic2 className="h-5 w-5" />
              ) : (
                <Mic className="h-5 w-5" />
              )}
            </button>
          )}

          {/* Text Input */}
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={disabled || loading}
            placeholder={placeholder}
            maxLength={maxLength}
            className={cn(inputVariants({ variant }))}
            rows={1}
            autoFocus={autoFocus}
            aria-label="Message"
            aria-multiline="true"
            style={{
              minHeight: variant === "patient" ? "44px" : "32px",
              maxHeight: variant === "patient" ? "120px" : "100px",
            }}
          />

          {/* Character Count */}
          {maxLength && value.length > maxLength * 0.8 && (
            <span className="flex-shrink-0 text-[10px] text-patient-on-surface-variant px-1">
              {value.length}/{maxLength}
            </span>
          )}

          {/* Send Button */}
          <Button
            type="submit"
            disabled={disabled || loading || (!value.trim() && attachments.length === 0)}
            loading={loading}
            variant={variant === "patient" ? "primary" : "primary-staff"}
            size="icon"
            className={cn(sendButtonVariants({ variant }))}
            aria-label="Send message"
          >
            <Send className={cn("h-5 w-5", variant === "staff" && "h-4 w-4")} />
          </Button>
        </div>
      </form>
    );
  }
);
ChatComposer.displayName = "ChatComposer";

/* ============================================================
   Voice Recording Hook (for more complex recording logic)
   ============================================================ */

function useVoiceRecording(onResult: (blob: Blob, duration: number) => void) {
  const [isRecording, setIsRecording] = React.useState(false);
  const [duration, setDuration] = React.useState(0);
  const mediaRecorderRef = React.useRef<MediaRecorder | null>(null);
  const chunksRef = React.useRef<Blob[]>([]);
  const intervalRef = React.useRef<ReturnType<typeof setInterval> | null>(null);

  const startRecording = React.useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      chunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        onResult(blob, duration);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorderRef.current.start(100);
      setIsRecording(true);
      setDuration(0);

      intervalRef.current = setInterval(() => {
        setDuration((d) => d + 100);
      }, 100);
    } catch (error) {
      console.error("Failed to start recording:", error);
    }
  }, [duration, onResult]);

  const stopRecording = React.useCallback(() => {
    mediaRecorderRef.current?.stop();
    setIsRecording(false);
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  React.useEffect(() => {
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
      mediaRecorderRef.current?.stream?.getTracks?.().forEach((t) => t.stop());
    };
  }, []);

  return { isRecording, duration, startRecording, stopRecording };
}

export { ChatComposer, composerVariants, inputVariants as chatInputVariants, useVoiceRecording };