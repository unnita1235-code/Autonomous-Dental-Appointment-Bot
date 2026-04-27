"use client";

import { useEffect, useRef, useState } from "react";
import { io, type Socket } from "socket.io-client";

import { useStaffDashboardStore } from "@/store/useStaffDashboardStore";

const SOCKET_URL = process.env.NEXT_PUBLIC_SOCKET_URL ?? "http://localhost:8000";

interface UseStaffSocketResult {
  isConnected: boolean;
}

export const useStaffSocket = (): UseStaffSocketResult => {
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef<Socket | null>(null);
  const addConversation = useStaffDashboardStore((state) => state.addConversation);
  const addHandoff = useStaffDashboardStore((state) => state.addHandoff);
  const addAppointmentBooked = useStaffDashboardStore((state) => state.addAppointmentBooked);

  useEffect(() => {
    let isMounted = true;
    const init = async (): Promise<void> => {
      const tokenResponse = await fetch("/api/auth/socket-token", { cache: "no-store" });
      const tokenPayload = (await tokenResponse.json()) as {
        success: boolean;
        data?: { token: string };
      };
      if (!tokenResponse.ok || !tokenPayload.success || !tokenPayload.data?.token) {
        return;
      }
      const token = tokenPayload.data.token;
      const sessionId = crypto.randomUUID();
      const socket = io(`${SOCKET_URL}`, {
        transports: ["websocket", "polling"],
        auth: {
          token,
          role: "staff",
          session_id: sessionId,
          channel: "web"
        }
      });
      if (!isMounted) {
        socket.disconnect();
        return;
      }
      socketRef.current = socket;
      socket.on("connect", () => {
        setIsConnected(true);
        socket.emit("join_staff_room", { token });
      });
      socket.on("disconnect", () => setIsConnected(false));
      socket.on("new_conversation", (payload) => {
        addConversation(payload);
      });
      socket.on("handoff_triggered", (payload) => {
        addHandoff(payload);
      });
      socket.on("appointment_booked", (payload) => {
        addAppointmentBooked(payload);
      });
    };
    void init();
    return () => {
      isMounted = false;
      const socket = socketRef.current;
      socket?.removeAllListeners();
      socket?.disconnect();
      socketRef.current = null;
    };
  }, [addAppointmentBooked, addConversation, addHandoff]);

  return { isConnected };
};
