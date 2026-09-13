"use client";

import { useTranslations } from "next-intl";

// The picks page heading: the presenter's anchor talk titles. The separator
// is a message so each locale chooses its own.
export function AnchorHeading({ titles }: { titles: string[] }) {
  const t = useTranslations("picks");
  return (
    <h1 className="max-w-[34ch] font-serif text-[19px] leading-[1.3] font-normal text-balance">
      {titles.join(t("titleSeparator"))}
    </h1>
  );
}
