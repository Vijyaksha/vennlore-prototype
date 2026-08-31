"use client";

import { useTranslations } from "next-intl";

import { Skeleton } from "@repo/ui/components/skeleton";

import { ErrorState } from "@/components/error-state";
import { PickRail } from "@/components/pick-rail";
import { ANCHOR_TALK_ID } from "@/lib/conference";
import { trpc } from "@/lib/trpc";

export default function PicksPage() {
  const t = useTranslations("common");
  const picks = trpc.picks.useQuery({ talkId: ANCHOR_TALK_ID });

  if (picks.isError) {
    return <ErrorState onRetry={() => void picks.refetch()} />;
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

  return (
    <section>
      <div className="px-5 pt-5 pb-0.5">
        <h1 className="max-w-[34ch] font-serif text-[19px] leading-[1.3] font-normal text-balance">
          {picks.data.talk.title}
        </h1>
      </div>
      <PickRail core={picks.data.core} unexpected={picks.data.unexpected} />
    </section>
  );
}
