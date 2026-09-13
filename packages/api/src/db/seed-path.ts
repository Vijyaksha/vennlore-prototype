/** The seed file to load: SEED_PATH when set and non-blank, else the pipeline's default export. */
export function resolveSeedPath(
  env: { SEED_PATH?: string },
  defaultPath: string,
): string {
  const value = env.SEED_PATH?.trim() ?? "";
  return value === "" ? defaultPath : value;
}
