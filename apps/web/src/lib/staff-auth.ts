const STAFF_JWT_COOKIE = "staff_jwt";

const base64Decode = (value: string): string => {
  if (typeof atob === "function") {
    return atob(value);
  }
  return Buffer.from(value, "base64").toString("utf-8");
};

const decodeJwtPayload = (token: string): Record<string, unknown> | null => {
  const parts = token.split(".");
  if (parts.length !== 3) {
    return null;
  }

  try {
    const base64 = parts[1].replace(/-/g, "+").replace(/_/g, "/");
    const padded = `${base64}${"=".repeat((4 - (base64.length % 4)) % 4)}`;
    const decoded = base64Decode(padded);
    const payload = JSON.parse(decoded) as Record<string, unknown>;
    return payload;
  } catch {
    return null;
  }
};

const isJwtExpired = (token: string): boolean => {
  const payload = decodeJwtPayload(token);
  if (!payload) {
    return true;
  }

  const exp = payload.exp;
  if (typeof exp !== "number") {
    return true;
  }
  return Date.now() >= exp * 1000;
};

export { STAFF_JWT_COOKIE, decodeJwtPayload, isJwtExpired };
