import { create } from "zustand";

interface AppState {
  clinicName: string;
  setClinicName: (clinicName: string) => void;
}

export const useAppStore = create<AppState>((set) => ({
  clinicName: "Dental Clinic",
  setClinicName: (clinicName: string) => set({ clinicName })
}));
