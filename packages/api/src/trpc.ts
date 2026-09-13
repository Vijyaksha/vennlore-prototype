import { initTRPC } from "@trpc/server";

import type { Repo } from "./repo.db";

export interface Context {
  repo: Repo;
}

const t = initTRPC.context<Context>().create();

export const router = t.router;
export const publicProcedure = t.procedure;
export const createCallerFactory = t.createCallerFactory;
