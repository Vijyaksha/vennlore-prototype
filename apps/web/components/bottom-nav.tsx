"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslations } from "next-intl";

import { cn } from "@repo/ui/lib/utils";

export function BottomNav({ talkId }: { talkId: number }) {
  const t = useTranslations("nav");
  const pathname = usePathname();
  const onCalendar = pathname.endsWith("/calendar");
  const base = `/talk/${talkId}`;

  const pill = (href: string, label: string, active: boolean) => (
    <Link
      href={href}
      aria-current={active ? "page" : undefined}
      className={cn(
        "rounded-full border border-border px-6 py-2 text-[13.5px] font-medium text-muted-foreground",
        "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary",
        active && "border-primary bg-accent-soft text-foreground",
      )}
    >
      {label}
    </Link>
  );

  return (
    <nav
      aria-label={t("label")}
      className="fixed right-0 bottom-0 left-0 flex justify-center gap-2 border-t border-border bg-background px-4 pt-2.5 pb-[calc(10px+env(safe-area-inset-bottom))]"
    >
      {pill(base, t("picks"), !onCalendar)}
      {pill(`${base}/calendar`, t("calendar"), onCalendar)}
    </nav>
  );
}
