import { render } from "@testing-library/react";
import { NextIntlClientProvider } from "next-intl";
import type { ReactNode } from "react";

import { TIME_ZONE } from "../../lib/conference";
import messages from "../../messages/en.json";

export function renderWithIntl(ui: ReactNode) {
  return render(
    <NextIntlClientProvider locale="en" messages={messages} timeZone={TIME_ZONE}>
      {ui}
    </NextIntlClientProvider>,
  );
}
