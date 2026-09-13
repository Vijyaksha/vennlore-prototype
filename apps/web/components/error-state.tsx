"use client";

import { useTranslations } from "next-intl";

import { Button } from "@repo/ui/components/button";

// `notFound` marks a permanent miss (the configured subject does not exist):
// retrying cannot help, so no retry button is offered.
export function ErrorState({
  onRetry,
  notFound = false,
}: {
  onRetry: () => void;
  notFound?: boolean;
}) {
  const t = useTranslations("common");
  return (
    <div className="mx-5 my-7 flex flex-col items-center gap-3 rounded-lg border border-border bg-card px-4 py-9 text-center">
      <p className="text-[13.5px] text-muted-foreground">
        {notFound ? t("notFound") : t("error")}
      </p>
      {!notFound && (
        <Button
          variant="outline"
          size="sm"
          onClick={onRetry}
          className="rounded-full border-primary text-primary hover:bg-accent-soft hover:text-primary"
        >
          {t("retry")}
        </Button>
      )}
    </div>
  );
}
