import { fetchRequestHandler } from "@trpc/server/adapters/fetch";

import { appRouter, createContext } from "@repo/api";

const handler = (req: Request) =>
  fetchRequestHandler({
    endpoint: "/api/trpc",
    req,
    router: appRouter,
    createContext,
    // Clients see masked internal errors; the server log keeps the real one.
    onError({ path, error }) {
      console.error(`tRPC error on ${path ?? "<no-path>"}:`, error);
    },
  });

export { handler as GET, handler as POST };
