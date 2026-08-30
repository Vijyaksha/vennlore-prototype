import { getRequestConfig } from "next-intl/server";

import { TIME_ZONE } from "../lib/conference";

// Single-locale app: no locale routing, English messages, conference-local
// times everywhere.
export default getRequestConfig(async () => ({
  locale: "en",
  messages: (await import("../messages/en.json")).default,
  timeZone: TIME_ZONE,
}));
