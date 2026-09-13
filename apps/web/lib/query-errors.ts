// Query error decisions shared by the pages. A NOT_FOUND subject is permanent,
// so it is neither retried nor offered a retry button.

const MAX_RETRIES = 1;

export function isNotFound(error: unknown): boolean {
  if (typeof error !== "object" || error === null || !("data" in error)) {
    return false;
  }
  const { data } = error as { data?: { code?: unknown } | null };
  return data?.code === "NOT_FOUND";
}

export function retryUnlessNotFound(failureCount: number, error: unknown): boolean {
  return !isNotFound(error) && failureCount < MAX_RETRIES;
}
