import { createTRPCReact } from "@trpc/react-query";

import type { AppRouter } from "../server/router";

// Explicit annotation keeps the inferred type portable (TS2883 otherwise).
export const trpc: ReturnType<typeof createTRPCReact<AppRouter>> =
  createTRPCReact<AppRouter>();
