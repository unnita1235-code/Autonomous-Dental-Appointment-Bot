// Chat components
export { default as ChatWidget } from "./chat/ChatWidget";
export { default as ChatPanel } from "./chat/ChatPanel";
export { default as ChatMessage } from "./chat/ChatMessage";
export { default as SlotPicker } from "./chat/SlotPicker";
export { default as QuickReplies } from "./chat/QuickReplies";
export { default as BookingConfirmation } from "./chat/BookingConfirmation";
export { useChatStore } from "./chat/ChatStore";

// New chat components
export { ConversationBubble, MessageGroup, bubbleVariants } from "./chat/ConversationBubble";
export { ChatComposer, composerVariants, chatInputVariants, useVoiceRecording } from "./chat/ChatComposer";

// UI primitives
export { Button, buttonVariants } from "./ui/button";
export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent, cardVariants } from "./ui/card";
export { Input, inputVariants } from "./ui/input";
export { Badge, badgeVariants } from "./ui/badge";
export { Avatar, avatarVariants } from "./ui/avatar";
export { Fab, fabVariants } from "./ui/fab";
export { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider } from "./ui/tooltip";
export { Separator, separatorVariants } from "./ui/separator";
export { Sheet, SheetClose, SheetContent, SheetDescription, SheetHeader, SheetOverlay, SheetPortal, SheetTitle, SheetTrigger } from "./ui/sheet";
export { Chip, chipVariants } from "./ui/chip";
export { Select, SelectGroup, SelectValue, SelectTrigger, SelectContent, SelectLabel, SelectItem, SelectSeparator, SelectScrollUpButton, SelectScrollDownButton } from "./ui/select";
export { EmptyState, emptyStateVariants, EmptyAppointments, EmptyPatients, EmptyConversations, EmptyNotifications, EmptySearch, EmptyAIRecommendations } from "./ui/EmptyState";
export { Skeleton, Spinner, Pulse, LoadingOverlay, SkeletonCard, SkeletonList, SkeletonTable, SkeletonDashboard, SkeletonChat, skeletonVariants, spinnerVariants, pulseVariants, loadingOverlayVariants } from "./ui/LoadingState";
export { ErrorState, errorStateVariants, NetworkError, ServerError, NotFoundError, AuthError, PermissionError, FormValidationError } from "./ui/ErrorState";
export { MobileBottomNav, bottomNavVariants, navItemVariants, patientNavItems, staffNavItems } from "./ui/MobileBottomNav";

// AI components
export { AIIndicator, AIStatusDot, AISparkle, aiIndicatorVariants, aiStatusDotVariants, aiSparkleVariants } from "./ai/AIIndicator";
export { AIRecommendationCard, aiRecommendationCardVariants } from "./ai/AIRecommendationCard";
export { AIActivityItem, TimelineItem, activityItemVariants, timelineItemVariants } from "./ai/AIActivityItem";

// Dashboard components
export { MetricCard, metricCardVariants, trendVariants } from "./dashboard/MetricCard";
export { AppointmentCard, AppointmentCardCompact, appointmentCardVariants } from "./dashboard/AppointmentCard";

// Patient components
export { PatientSummaryCard, PatientCardCompact, patientSummaryVariants } from "./patient/PatientSummaryCard";
export { PatientDashboardShell } from "./patient/PatientDashboardShell";

// Branding components
export { DentalFlowLogo, DentalFlowAvatar, DentalFlowWordmark, DentalFlowFavicon, logoVariants, wordmarkVariants } from "./branding";

// Design system
export * from "@/lib/design-system";