import { fetchRequestHandler } from "@trpc/server/adapters/fetch";

import { appRouter, createContext } from "@repo/api";

const handler = (req: Request) =>
  fetchRequestHandler({
    endpoint: "/api/trpc",
    req,
    router: appRouter,
    createContext,
    // Clients see masked internal errors, so the server log keeps the real
    // one. Expected codes (NOT_FOUND, BAD_REQUEST, ...) get a single line.
    onError({ path, error }) {
      if (error.code === "INTERNAL_SERVER_ERROR") {
        console.error(`tRPC ${error.code} on ${path ?? "<no-path>"}:`, error);
      } else {
        console.error(`${error.code} ${path ?? "<no-path>"}`);
      }
    },
  });

export { handler as GET, handler as POST };
