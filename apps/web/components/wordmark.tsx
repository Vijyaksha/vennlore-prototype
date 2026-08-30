import { APP_NAME } from "@/lib/conference";

export function Wordmark() {
  return (
    <span className="font-serif text-[22px] font-medium italic">
      {APP_NAME}
      <span className="text-primary not-italic">.</span>
    </span>
  );
}
