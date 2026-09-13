import { createTRPCReact } from "@trpc/react-query";

import type { AppRouter } from "@repo/api";

// Explicit annotation keeps the inferred type portable (TS2883 otherwise).
export const trpc: ReturnType<typeof createTRPCReact<AppRouter>> =
  createTRPCReact<AppRouter>();
