import { fetchRequestHandler } from "@trpc/server/adapters/fetch";

import { appRouter, dbRepo } from "@repo/api";

const handler = (req: Request) =>
  fetchRequestHandler({
    endpoint: "/api/trpc",
    req,
    router: appRouter,
    createContext: () => ({ repo: dbRepo }),
  });

export { handler as GET, handler as POST };
