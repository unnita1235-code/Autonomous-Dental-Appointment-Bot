"use client";

import type { QuickReplyOption } from "./ChatStore";

interface QuickRepliesProps {
  options: QuickReplyOption[];
  onSelect: (value: string) => void;
}

export default function QuickReplies({ options, onSelect }: QuickRepliesProps): JSX.Element {
  return (
    <div className="mt-2 flex flex-wrap gap-2">
      {options.map((option) => (
        <button
          key={option.id}
          type="button"
          onClick={() => onSelect(option.value)}
          className="rounded-full border border-primary/25 bg-white px-3 py-1.5 text-xs font-medium text-primary transition hover:border-primary hover:bg-primary/5"
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}
