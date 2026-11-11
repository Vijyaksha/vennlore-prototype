"use client";

import { useId, useState } from "react";
import { useTranslations } from "next-intl";

import { Button } from "@repo/ui/components/button";
import { Label } from "@repo/ui/components/label";
import { Textarea } from "@repo/ui/components/textarea";

export const MIN_QUERY_CHARS = 10;

/** Free-text search: describe your research, get talks and papers back. */
export function SearchBox({
  pending,
  error,
  onSearch,
}: {
  pending: boolean;
  error: string | null;
  onSearch: (text: string) => void;
}) {
  const t = useTranslations("search");
  const id = useId();
  const [text, setText] = useState("");
  const ready = text.trim().length >= MIN_QUERY_CHARS && !pending;

  return (
    <form
      className="flex flex-col gap-3"
      onSubmit={(event) => {
        event.preventDefault();
        if (ready) onSearch(text.trim());
      }}
    >
      <Label htmlFor={id} className="text-[15px]">
        {t("label")}
      </Label>
      <Textarea
        id={id}
        value={text}
        onChange={(event) => setText(event.target.value)}
        placeholder={t("placeholder")}
        rows={4}
        maxLength={4000}
        className="font-serif text-[15px] leading-[1.5]"
      />
      <div className="flex items-center justify-between gap-3">
        <span className="text-[12.5px] text-muted-foreground">{t("hint")}</span>
        <Button type="submit" disabled={!ready}>
          {pending ? t("searching") : t("submit")}
        </Button>
      </div>
      {error !== null && (
        <p role="alert" className="text-[13px] text-destructive">
          {error}
        </p>
      )}
    </form>
  );
}
