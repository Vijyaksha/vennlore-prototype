import type { Metadata } from "next";
import { IBM_Plex_Mono, IBM_Plex_Sans, IBM_Plex_Serif } from "next/font/google";
import { NextIntlClientProvider } from "next-intl";
import { getLocale } from "next-intl/server";

import "./globals.css";
import { cn } from "@/lib/utils";
import { APP_NAME, MEETING_LABEL } from "@/lib/conference";
import { BottomNav } from "@/components/bottom-nav";
import { Wordmark } from "@/components/wordmark";
import { Providers } from "./providers";

const plexSans = IBM_Plex_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  style: ["normal", "italic"],
  variable: "--font-plex-sans",
});
const plexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-plex-mono",
});
const plexSerif = IBM_Plex_Serif({
  subsets: ["latin"],
  weight: ["400", "500"],
  style: ["normal", "italic"],
  variable: "--font-plex-serif",
});

export const metadata: Metadata = {
  title: APP_NAME,
  description: `Find the talks that share your methods at ${MEETING_LABEL}.`,
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const locale = await getLocale();
  return (
    <html
      lang={locale}
      className={cn(
        "font-sans",
        plexSans.variable,
        plexMono.variable,
        plexSerif.variable,
      )}
    >
      <body className="text-[15px] leading-normal antialiased">
        <NextIntlClientProvider>
          <Providers>
            <div className="mx-auto flex min-h-dvh max-w-[980px] flex-col">
              <header className="flex items-baseline justify-between border-b border-border px-5 pt-[18px] pb-3.5">
                <Wordmark />
                <span className="font-mono text-[10.5px] tracking-[0.08em] text-faint uppercase">
                  {MEETING_LABEL}
                </span>
              </header>
              <main className="flex-1 pb-[92px]">{children}</main>
              <BottomNav />
            </div>
          </Providers>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
