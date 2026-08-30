"use client";

import { useTranslations } from "next-intl";

// The honest empty core slot: when fewer than two core matches cleared the
// bar, the rail says so instead of padding with weaker picks.
export function EmptySlot({ hasCore }: { hasCore: boolean }) {
  const t = useTranslations("picks");
  return (
    <div className="flex min-h-[430px] snap-center items-center justify-center rounded-lg border border-dashed border-border p-6 text-center text-[13.5px] text-faint">
      {hasCore ? t("noSecondCore") : t("noCore")}
    </div>
  );
}
