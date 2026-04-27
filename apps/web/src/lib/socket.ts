import { useEffect, useMemo, useRef, useState } from "react";
import { io, type Socket } from "socket.io-client";

const SOCKET_URL = process.env.NEXT_PUBLIC_SOCKET_URL ?? "http://localhost:8000";
const MAX_RECONNECT_ATTEMPTS = 8;
const BASE_RECONNECT_DELAY_MS = 500;
const MAX_RECONNECT_DELAY_MS = 10000;

export interface UseSocketResult {
  socket: Socket | null;
  isConnected: boolean;
}

const getBackoffDelay = (attempt: number): number => {
  const exponentialDelay = BASE_RECONNECT_DELAY_MS * 2 ** attempt;
  return Math.min(exponentialDelay, MAX_RECONNECT_DELAY_MS);
};

export const useSocket = (namespace = "/"): UseSocketResult => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const reconnectAttemptRef = useRef<number>(0);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const socketPath = useMemo(() => namespace, [namespace]);

  useEffect(() => {
    const instance = io(`${SOCKET_URL}${socketPath}`, {
      autoConnect: false,
      reconnection: false,
      transports: ["websocket", "polling"]
    });

    const scheduleReconnect = () => {
      if (reconnectAttemptRef.current >= MAX_RECONNECT_ATTEMPTS) {
        return;
      }

      const delay = getBackoffDelay(reconnectAttemptRef.current);
      reconnectAttemptRef.current += 1;

      reconnectTimeoutRef.current = setTimeout(() => {
        instance.connect();
      }, delay);
    };

    instance.on("connect", () => {
      reconnectAttemptRef.current = 0;
      setIsConnected(true);
    });

    instance.on("disconnect", () => {
      setIsConnected(false);
      scheduleReconnect();
    });

    instance.on("connect_error", () => {
      setIsConnected(false);
      scheduleReconnect();
    });

    setSocket(instance);
    instance.connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      instance.removeAllListeners();
      instance.disconnect();
      setSocket(null);
      setIsConnected(false);
    };
  }, [socketPath]);

  return { socket, isConnected };
};
