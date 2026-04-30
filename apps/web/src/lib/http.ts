export const parseJsonResponse = async <T>(response: Response): Promise<T | null> => {
  const raw = await response.text();
  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
};
