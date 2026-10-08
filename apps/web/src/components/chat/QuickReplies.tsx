"use client";

import type { QuickReplyOption } from "./ChatStore";

import { Chip } from "@/components/ui/chip";

interface QuickRepliesProps {
  options: QuickReplyOption[];
  onSelect: (value: string) => void;
}

export default function QuickReplies({ options, onSelect }: QuickRepliesProps): JSX.Element {
  return (
    <div className="mt-2 flex flex-wrap gap-2">
      {options.map((option) => (
        <Chip
          key={option.id}
          variant="patient"
          size="sm"
          onClick={() => onSelect(option.value)}
        >
          {option.label}
        </Chip>
      ))}
    </div>
  );
}