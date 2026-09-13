// Query error decisions shared by the pages. A NOT_FOUND subject is permanent,
// so it is neither retried nor offered a retry button. BAD_REQUEST is permanent
// too: the input failed validation, so the same call fails the same way.

const MAX_RETRIES = 1;
const PERMANENT_CODES = new Set(["NOT_FOUND", "BAD_REQUEST"]);

function code(error: unknown): unknown {
  if (typeof error !== "object" || error === null || !("data" in error)) {
    return undefined;
  }
  const { data } = error as { data?: { code?: unknown } | null };
  return data?.code;
}

export function isNotFound(error: unknown): boolean {
  return code(error) === "NOT_FOUND";
}

export function retryUnlessNotFound(failureCount: number, error: unknown): boolean {
  return !PERMANENT_CODES.has(code(error) as string) && failureCount < MAX_RETRIES;
}
