"use client";

import { useTranslations } from "next-intl";

import { AnchorHeading } from "@/components/anchor-heading";
import { PicksGraph } from "@/components/picks-graph";
import { PickRail } from "@/components/pick-rail";
import { SearchBox } from "@/components/search-box";
import { searchErrorKind } from "@/lib/query-errors";
import { trpc } from "@/lib/trpc";

/** Free-text search: the same pick tiles as the home page, for a research description
 *  instead of a programme talk. */
export default function SearchPage() {
  const t = useTranslations("search");
  const search = trpc.search.recommend.useMutation();

  const error =
    search.error === null
      ? null
      : searchErrorKind(search.error) === "unavailable"
        ? t("unavailable")
        : searchErrorKind(search.error) === "bad_request"
          ? search.error.message
          : t("failed");

  return (
    <section>
      <div className="px-5 pt-5 pb-2">
        <h1 className="mb-4 font-serif text-[22px] leading-tight">{t("title")}</h1>
        <SearchBox
          pending={search.isPending}
          error={error}
          onSearch={(text) => search.mutate({ text })}
        />
      </div>
      {search.data !== undefined && (
        <>
          <div className="px-5 pt-5 pb-0.5">
            <p className="font-mono text-[11px] text-muted-foreground">{t("resultsFor")}</p>
            <AnchorHeading titles={search.data.anchors.map((a) => a.title)} />
          </div>
          <div className="px-5 pt-4">
            <PicksGraph recommendations={search.data.recommendations} />
          </div>
          <PickRail
            anchors={search.data.anchors.map(({ id, title }) => ({ id, title }))}
            recommendations={search.data.recommendations}
          />
        </>
      )}
    </section>
  );
}
