"use client";

import { useTranslations } from "next-intl";

import { Skeleton } from "@repo/ui/components/skeleton";

import { AnchorHeading } from "@/components/anchor-heading";
import { ErrorState } from "@/components/error-state";
import { PickRail } from "@/components/pick-rail";
import { SUBJECT } from "@/lib/conference";
import { isNotFound, retryUnlessNotFound } from "@/lib/query-errors";
import { trpc } from "@/lib/trpc";

export default function PicksPage() {
  const t = useTranslations("common");
  const picks = trpc.presenter.picks.useQuery(SUBJECT, {
    retry: retryUnlessNotFound,
  });

  if (picks.isError) {
    return (
      <ErrorState
        notFound={isNotFound(picks.error)}
        onRetry={() => void picks.refetch()}
      />
    );
  }

  if (picks.isPending) {
    return (
      <div aria-label={t("loading")}>
        <div className="px-5 pt-5">
          <Skeleton className="h-6 w-72 max-w-full rounded-md" />
        </div>
        <div className="no-scrollbar grid auto-cols-[min(76vw,310px)] grid-flow-col gap-3.5 overflow-x-auto px-5 pt-[18px] pb-3.5">
          <Skeleton className="min-h-[430px] rounded-lg" />
          <Skeleton className="min-h-[430px] rounded-lg" />
          <Skeleton className="min-h-[430px] rounded-lg" />
        </div>
      </div>
    );
  }

  const { anchors, recommendations } = picks.data;

  return (
    <section>
      <div className="px-5 pt-5 pb-0.5">
        <AnchorHeading titles={anchors.map((anchor) => anchor.title)} />
      </div>
      <PickRail
        anchors={anchors.map(({ id, title }) => ({ id, title }))}
        recommendations={recommendations}
      />
    </section>
  );
}
