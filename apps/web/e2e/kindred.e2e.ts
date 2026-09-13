import { expect, test } from "@playwright/test";

const ANCHOR_TITLE = "Photoconductivity of Self-Assembled Porphyrin Nanorods";

test("opening the site shows the anchor talk's picks rail — no search", async ({
  page,
}) => {
  await page.goto("/");
  await expect(page.getByText(ANCHOR_TITLE)).toBeVisible();
  await expect(page.getByText("core").first()).toBeVisible();
  await expect(page.getByText("unexpected").first()).toBeVisible();
  // The claim-search screen is gone: no search box anywhere.
  await expect(page.getByRole("searchbox")).toHaveCount(0);
});

test("picks rail shows real engine recommendations with scores", async ({
  page,
}) => {
  await page.goto("/");
  // Core pick 2802 (Ni-DNA memristive nanowires) surfaced by the Stage-0 run.
  await expect(page.getByText(/Memristive/i).first()).toBeVisible();
  await expect(page.getByText(/%/).first()).toBeVisible();
});

test("bottom nav flips between the two screens", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("link", { name: "Calendar" }).click();
  await expect(page).toHaveURL(/\/calendar$/);
  await expect(
    page.getByText("rooms & walking times illustrative"),
  ).toBeVisible();
  await page.getByRole("link", { name: "Picks" }).click();
  await expect(page).toHaveURL(/\/$/);
});

test("calendar shows day agenda with walking transitions", async ({
  page,
}) => {
  await page.goto("/calendar");
  await expect(
    page.getByText("rooms & walking times illustrative"),
  ).toBeVisible();

  // Tue Mar 17 holds two picks in different Convention Center clusters,
  // so a 15-minute walk segment must appear between them.
  await page.getByRole("button", { name: /17/ }).click();
  await expect(page.getByText(/15 min walk/).first()).toBeVisible();
});

test("agenda API groups all matched picks into conference days", async ({
  request,
  baseURL,
}) => {
  const res = await request.get(
    `${baseURL}/api/trpc/presenter.agenda?input=${encodeURIComponent(
      JSON.stringify({ talkId: 0 }),
    )}`,
  );
  expect(res.ok()).toBe(true);
  const days = (await res.json()).result.data.days as {
    date: string;
    items: { id: number }[];
  }[];
  const ids = days.flatMap((d) => d.items.map((i) => i.id));
  // Every matched pick for the (untimed) anchor is on the agenda, exactly once,
  // whatever the seeded run produced. Ids are not pinned: reruns are stochastic.
  const picks = await request.get(
    `${baseURL}/api/trpc/presenter.picks?input=${encodeURIComponent(
      JSON.stringify({ talkId: 0 }),
    )}`,
  );
  expect(picks.ok()).toBe(true);
  const matched = ((await picks.json()).result.data.recommendations as {
    candidateId: number;
  }[]).map((r) => r.candidateId);
  expect(matched.length).toBeGreaterThan(0);
  expect(ids.sort((a, b) => a - b)).toEqual(matched.sort((a, b) => a - b));
});
