"use client";

import { useTranslations } from "next-intl";

import { Skeleton } from "@repo/ui/components/skeleton";

import { AskBox } from "@/components/ask-box";
import { ErrorState } from "@/components/error-state";
import { ThemeCard } from "@/components/theme-card";
import { searchErrorKind } from "@/lib/query-errors";
import { trpc } from "@/lib/trpc";

/** Research themes across the conference, and questions answered from them. */
export default function ThemesPage() {
  const t = useTranslations("themes");
  const themes = trpc.themes.list.useQuery(undefined, { retry: false });
  const ask = trpc.themes.ask.useMutation();

  const message = (error: unknown) =>
    searchErrorKind(error) === "unavailable" ? t("unavailable")
      : searchErrorKind(error) === "bad_request" ? (error as Error).message : t("failed");

  return (
    <section className="flex flex-col gap-6 px-5 pt-5 pb-6">
      <div className="flex flex-col gap-2">
        <h1 className="font-serif text-[22px] leading-tight">{t("title")}</h1>
        <p className="text-[13.5px] text-muted-foreground">{t("intro")}</p>
      </div>

      <AskBox pending={ask.isPending} error={ask.error ? message(ask.error) : null}
        onAsk={(question) => ask.mutate({ question })} />

      {ask.data !== undefined && (
        <div className="flex flex-col gap-3">
          <div className="border-l-2 border-primary pl-3">
            <p className="font-mono text-[11px] text-muted-foreground">{t("answerTitle")}</p>
            <p className="font-serif text-[15px] leading-[1.55]">{ask.data.answer ?? t("noAnswer")}</p>
          </div>
          <p className="font-mono text-[11px] text-muted-foreground">{t("related")}</p>
          <div className="grid gap-3 md:grid-cols-2">
            {ask.data.themes.map((theme) => <ThemeCard key={theme.id} theme={theme} />)}
          </div>
        </div>
      )}

      <div className="flex flex-col gap-3">
        <h2 className="font-mono text-[11px] text-muted-foreground">{t("all")}</h2>
        {themes.isError ? (
          <ErrorState notFound={false} onRetry={() => void themes.refetch()} />
        ) : themes.isPending ? (
          <div className="grid gap-3 md:grid-cols-2">
            <Skeleton className="h-40 rounded-lg" />
            <Skeleton className="h-40 rounded-lg" />
          </div>
        ) : (
          <div className="grid gap-3 md:grid-cols-2">
            {themes.data.themes.map((theme) => <ThemeCard key={theme.id} theme={theme} />)}
          </div>
        )}
      </div>
    </section>
  );
}
