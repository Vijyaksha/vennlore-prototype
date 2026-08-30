"use client";

import { useTranslations } from "next-intl";
import { useEffect, useState } from "react";

import { Input } from "@repo/ui/components/input";
import { Skeleton } from "@repo/ui/components/skeleton";

import { ErrorState } from "@/components/error-state";
import { SearchResults } from "@/components/search-results";
import { trpc } from "@/lib/trpc";

const DEBOUNCE_MS = 250;
const MIN_QUERY_LENGTH = 2;

export default function ClaimPage() {
  const t = useTranslations("home");
  const tCommon = useTranslations("common");
  const [input, setInput] = useState("");
  const [query, setQuery] = useState("");

  useEffect(() => {
    const handle = setTimeout(() => setQuery(input.trim()), DEBOUNCE_MS);
    return () => clearTimeout(handle);
  }, [input]);

  const enabled = query.length >= MIN_QUERY_LENGTH;
  const search = trpc.searchTalks.useQuery({ query }, { enabled });

  return (
    <section className="px-5 pt-7">
      <h1 className="max-w-[26ch] font-serif text-[26px] leading-[1.3] font-normal text-balance">
        {t("headline")}
      </h1>
      <div className="mt-6">
        <Input
          type="search"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          aria-label={t("searchLabel")}
          placeholder={t("searchPlaceholder")}
          className="h-11 rounded-[10px] border-border bg-card px-3.5 text-[15px]"
        />
      </div>
      <div className="mt-4">
        {!enabled ? (
          <p className="text-[13.5px] text-faint">{t("hint")}</p>
        ) : search.isError ? (
          <ErrorState onRetry={() => void search.refetch()} />
        ) : search.isPending ? (
          <div
            aria-label={tCommon("loading")}
            className="flex flex-col gap-2"
          >
            <Skeleton className="h-[68px] rounded-lg" />
            <Skeleton className="h-[68px] rounded-lg" />
            <Skeleton className="h-[68px] rounded-lg" />
          </div>
        ) : search.data.length === 0 ? (
          <p className="rounded-lg border border-dashed border-border px-4 py-9 text-center text-[13.5px] text-faint">
            {t("noResults", { query })}
          </p>
        ) : (
          <SearchResults results={search.data} />
        )}
      </div>
    </section>
  );
}
