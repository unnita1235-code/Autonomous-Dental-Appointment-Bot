import { create } from "zustand";

export interface StaffConversationItem {
  conversation_id: string;
  session_id: string;
  channel: string;
  status?: string;
  started_at?: string;
  assigned_staff_id?: string | null;
}

export interface StaffAppointmentEvent {
  conversation_id: string;
  session_id: string;
  appointment: {
    id: string;
    status: string;
    start_time: string;
  };
}

interface StaffDashboardState {
  activeConversations: StaffConversationItem[];
  handoffQueue: StaffConversationItem[];
  recentBookedAppointments: StaffAppointmentEvent[];
  addConversation: (item: StaffConversationItem) => void;
  addHandoff: (item: StaffConversationItem) => void;
  addAppointmentBooked: (item: StaffAppointmentEvent) => void;
}

export const useStaffDashboardStore = create<StaffDashboardState>((set) => ({
  activeConversations: [],
  handoffQueue: [],
  recentBookedAppointments: [],
  addConversation: (item) =>
    set((state) => ({
      activeConversations: [item, ...state.activeConversations.filter((c) => c.conversation_id !== item.conversation_id)]
    })),
  addHandoff: (item) =>
    set((state) => ({
      handoffQueue: [item, ...state.handoffQueue.filter((c) => c.conversation_id !== item.conversation_id)],
      activeConversations: state.activeConversations.map((conversation) =>
        conversation.conversation_id === item.conversation_id
          ? { ...conversation, status: item.status ?? "HUMAN_TAKEOVER" }
          : conversation
      )
    })),
  addAppointmentBooked: (item) =>
    set((state) => ({
      recentBookedAppointments: [item, ...state.recentBookedAppointments].slice(0, 50)
    }))
}));
