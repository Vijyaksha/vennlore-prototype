"use client";

import Link from "next/link";

export interface SearchResult {
  id: number;
  title: string;
  sessionTitle: string | null;
}

export function SearchResults({ results }: { results: SearchResult[] }) {
  return (
    <ul className="flex flex-col gap-2">
      {results.map((result) => (
        <li key={result.id}>
          <Link
            href={`/talk/${result.id}`}
            className="block rounded-lg border border-border bg-card px-4 py-3.5 transition-colors hover:border-primary focus-visible:border-primary focus-visible:outline-none"
          >
            <span className="block text-[15px] leading-snug font-medium text-balance">
              {result.title}
            </span>
            {result.sessionTitle !== null && (
              <span className="mt-1 block font-mono text-[11.5px] text-faint">
                {result.sessionTitle}
              </span>
            )}
          </Link>
        </li>
      ))}
    </ul>
  );
}
