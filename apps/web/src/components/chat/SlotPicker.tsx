"use client";

import { format } from "date-fns";
import type { SlotOption } from "./ChatStore";

interface SlotPickerProps {
  slots: SlotOption[];
  onSelect: (slot: SlotOption) => void;
}

export default function SlotPicker({ slots, onSelect }: SlotPickerProps): JSX.Element {
  return (
    <div className="mt-2 space-y-2">
      {slots.slice(0, 3).map((slot) => {
        const start = new Date(slot.start_time);
        return (
          <div key={slot.id} className="rounded-xl border border-slate-200 bg-white p-3 shadow-sm">
            <div className="text-sm font-semibold text-slate-800">
              {format(start, "EEEE, MMM d")}
            </div>
            <div className="mt-1 text-sm text-slate-600">{format(start, "h:mm a")}</div>
            <div className="mt-2 text-xs text-muted">Dr. {slot.dentist_name}</div>
            <div className="text-xs text-muted">{slot.service_name}</div>
            <button
              type="button"
              onClick={() => onSelect(slot)}
              className="mt-3 inline-flex h-8 items-center rounded-md bg-primary px-3 text-xs font-semibold text-white transition hover:bg-primary-hover"
            >
              Select
            </button>
          </div>
        );
      })}
    </div>
  );
}
