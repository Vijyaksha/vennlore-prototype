/** Preprints (arXiv, bioRxiv, medRxiv) reach the app as Talk rows whose `type` is
 *  "preprint:<archive>" and whose external_id is "arXiv:<id>" or "doi:<doi>"
 *  (pipeline/src/gps_data/preprints.py). They have no slot, so cards link out. */
const SOURCES: Record<string, string> = {
  "preprint:arxiv": "arXiv",
  "preprint:biorxiv": "bioRxiv",
  "preprint:medrxiv": "medRxiv",
};

/** Archive name for a preprint candidate; null for a programme talk. */
export function paperSource(type: string | null): string | null {
  return type === null ? null : (SOURCES[type] ?? null);
}

/** Public URL of a preprint from its external id; null when it is not one. */
export function paperUrl(externalId: string | null): string | null {
  if (externalId === null) return null;
  if (externalId.startsWith("arXiv:")) return `https://arxiv.org/abs/${externalId.slice(6)}`;
  if (externalId.startsWith("doi:")) return `https://doi.org/${externalId.slice(4)}`;
  return null;
}
