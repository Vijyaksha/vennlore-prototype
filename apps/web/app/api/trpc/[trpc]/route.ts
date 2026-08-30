import { fetchRequestHandler } from "@trpc/server/adapters/fetch";

import { dbRepo } from "../../../../server/data";
import { appRouter } from "../../../../server/router";

const handler = (req: Request) =>
  fetchRequestHandler({
    endpoint: "/api/trpc",
    req,
    router: appRouter,
    createContext: () => ({ repo: dbRepo }),
  });

export { handler as GET, handler as POST };
