import { initTRPC } from "@trpc/server";

import type { Repo } from "./repo";
import { dbRepo } from "./repo.db";

export interface Context {
  repo: Repo;
  /** Engine whose recommendation rows procedures read unless the input overrides it. */
  engineId: string;
}

/** Production context. Lazy: dbRepo opens the database only inside its methods,
 *  so this needs no DATABASE_URL until a procedure actually queries. */
export function createContext(): Context {
  return { repo: dbRepo, engineId: process.env.ENGINE_ID ?? "graph_v1" };
}

const t = initTRPC.context<Context>().create();

export const router = t.router;
export const publicProcedure = t.procedure;
export const createCallerFactory = t.createCallerFactory;
