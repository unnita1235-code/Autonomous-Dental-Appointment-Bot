"use client";

import { format } from "date-fns";
import { Check } from "lucide-react";

import { cn } from "@/lib/design-system";
import type { SlotOption } from "./ChatStore";

interface SlotPickerProps {
  slots: SlotOption[];
  onSelect: (slot: SlotOption) => void;
  selectedSlotId?: string;
}

export default function SlotPicker({ slots, onSelect, selectedSlotId }: SlotPickerProps): JSX.Element {
  return (
    <div className="mt-2 space-y-2">
      {slots.slice(0, 3).map((slot) => {
        const start = new Date(slot.start_time);
        const isSelected = selectedSlotId === slot.id;

        return (
          <button
            key={slot.id}
            type="button"
            onClick={() => onSelect(slot)}
            className={cn(
              "relative w-full min-h-[48px] px-4 py-3 rounded-xl",
              "transition-all duration-200",
              "focus-visible:ring-2 focus-visible:ring-patient-primary focus-visible:ring-offset-2",
              isSelected
                ? "bg-patient-primary text-patient-on-primary shadow-md"
                : "bg-patient-surface-lowest text-patient-on-surface border border-patient-outline-variant hover:bg-patient-surface-variant hover:border-patient-primary/50"
            )}
          >
            <div className="flex items-center justify-between">
              <div className="flex flex-col gap-1">
                <span className="text-sm font-semibold">
                  {format(start, "EEEE, MMM d")}
                </span>
                <span className="text-sm font-medium">
                  {format(start, "h:mm a")}
                </span>
                <span className="text-xs opacity-80">Dr. {slot.dentist_name}</span>
                <span className="text-xs opacity-70">{slot.service_name}</span>
              </div>
              {isSelected && (
                <div className="flex-shrink-0 flex items-center justify-center w-8 h-8 rounded-full bg-patient-on-primary/20">
                  <Check className="h-4 w-4" />
                </div>
              )}
            </div>
          </button>
        );
      })}
    </div>
  );
}