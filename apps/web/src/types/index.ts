export interface ResponseEnvelope<T> {
  success: boolean;
  data: T | null;
  error: string | null;
  meta: Record<string, unknown> | null;
}

export type AppointmentStatus =
  | "PENDING"
  | "CONFIRMED"
  | "COMPLETED"
  | "CANCELLED"
  | "NO_SHOW";

export type AppointmentSourceChannel = "web" | "whatsapp" | "sms" | "voice" | "staff";
export type ChannelPreference = "web" | "whatsapp" | "sms" | "voice";
export const ConversationChannel = {
  WEB: "web",
  WHATSAPP: "whatsapp",
  SMS: "sms",
  VOICE: "voice",
} as const;
export type ConversationChannel = (typeof ConversationChannel)[keyof typeof ConversationChannel];

export const ConversationStatus = {
  ACTIVE: "ACTIVE",
  WAITING_HUMAN: "WAITING_HUMAN",
  HUMAN_TAKEOVER: "HUMAN_TAKEOVER",
  COMPLETED: "COMPLETED",
  ABANDONED: "ABANDONED",
} as const;
export type ConversationStatus = (typeof ConversationStatus)[keyof typeof ConversationStatus];

export const ConversationRole = {
  USER: "user",
  ASSISTANT: "assistant",
  SYSTEM: "system",
} as const;
export type ConversationRole = (typeof ConversationRole)[keyof typeof ConversationRole];
export type StaffRole = "ADMIN" | "RECEPTIONIST" | "DENTIST";

export interface DentistBrief {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
}

export interface ServiceBrief {
  id: string;
  name: string;
  duration_minutes: number;
  price: string;
}

export interface TimeSlot {
  id: string;
  dentist_id: string;
  start_time: string;
  end_time: string;
  is_available: boolean;
  locked_by: string | null;
  locked_until: string | null;
  appointment_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface Appointment {
  id: string;
  patient_id: string;
  dentist_id: string;
  service_id: string;
  time_slot_id: string;
  start_time: string;
  status: AppointmentStatus;
  source_channel: AppointmentSourceChannel;
  deposit_required: boolean;
  deposit_paid: boolean;
  deposit_amount: string | null;
  stripe_payment_intent_id: string | null;
  cancellation_reason: string | null;
  notes: string | null;
  reminder_24h_sent: boolean;
  reminder_2h_sent: boolean;
  dentist: DentistBrief;
  service: ServiceBrief;
  time_slot: TimeSlot;
  created_at: string;
  updated_at: string;
}

export interface Patient {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  date_of_birth: string | null;
  gender: string | null;
  insurance_provider: string | null;
  insurance_member_id: string | null;
  is_returning: boolean;
  no_show_count: number;
  requires_deposit: boolean;
  channel_preference: ChannelPreference;
  notes: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ConversationContext {
  patient_name?: string;
  service_name?: string;
  preferred_date?: string;
  preferred_time?: string;
  preferred_dentist?: string;
  insurance?: string;
  phone?: string;
  is_new_patient?: boolean;
}

export interface ConversationTurn {
  id: string;
  conversation_id: string;
  role: ConversationRole;
  content: string;
  intent: string | null;
  confidence_score: number | null;
  entities_extracted: Record<string, unknown> | null;
  processing_time_ms: number | null;
  turn_index: number;
  created_at: string;
  updated_at: string;
}

export interface Conversation {
  id: string;
  patient_id: string | null;
  channel: ConversationChannel;
  session_id: string;
  status: ConversationStatus;
  assigned_staff_id: string | null;
  context: ConversationContext;
  intent_history: Array<Record<string, unknown>>;
  started_at: string;
  ended_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface BotResponse {
  conversation: Conversation;
  turn: ConversationTurn;
  reply: string;
  requires_human_handoff: boolean;
}

export interface BookingsPerDay {
  date: string;
  count: number;
}

export interface ChannelMix {
  channel: string;
  count: number;
}

export interface StatusBreakdown {
  status: string;
  count: number;
}

export interface AnalyticsSummary {
  total_appointments: number;
  total_patients: number;
  total_conversations: number;
  pending_confirmations: number;
  human_takeover_count: number;
  bot_resolution_rate: number;
  bookings_per_day: BookingsPerDay[];
  channel_mix: ChannelMix[];
  status_breakdown: StatusBreakdown[];
  period_days: number;
}

export interface IntegrationStatus {
  service: string;
  status: string;
}

export interface StaffUser {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: StaffRole;
  is_active: boolean;
  last_login: string | null;
  created_at: string;
  updated_at: string;
}
