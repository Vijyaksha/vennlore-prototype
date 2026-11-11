"use client";

import { useId, useState } from "react";
import { useTranslations } from "next-intl";

import { Button } from "@repo/ui/components/button";
import { Input } from "@repo/ui/components/input";
import { Label } from "@repo/ui/components/label";

/** A question about the whole conference, answered from its research themes. */
export function AskBox({ pending, error, onAsk }: {
  pending: boolean;
  error: string | null;
  onAsk: (question: string) => void;
}) {
  const t = useTranslations("themes");
  const id = useId();
  const [question, setQuestion] = useState("");
  const ready = question.trim().length >= 3 && !pending;

  return (
    <form
      className="flex flex-col gap-2"
      onSubmit={(event) => {
        event.preventDefault();
        if (ready) onAsk(question.trim());
      }}
    >
      <Label htmlFor={id} className="text-[15px]">{t("askLabel")}</Label>
      <div className="flex gap-2">
        <Input
          id={id}
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder={t("askPlaceholder")}
          maxLength={1000}
          className="h-9"
        />
        <Button type="submit" disabled={!ready} className="h-9">
          {pending ? t("thinking") : t("ask")}
        </Button>
      </div>
      {error !== null && <p role="alert" className="text-[13px] text-destructive">{error}</p>}
    </form>
  );
}
