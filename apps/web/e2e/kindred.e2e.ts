import { expect, test } from "@playwright/test";

const ANCHOR_TITLE = "Photoconductivity of Self-Assembled Porphyrin Nanorods";

test("claiming a talk from search leads to its picks rail", async ({
  page,
}) => {
  await page.goto("/");
  await expect(
    page.getByText("Find the talks that share your methods"),
  ).toBeVisible();

  await page.getByPlaceholder("Type your talk title…").fill("porphyrin");
  const result = page.getByRole("link", { name: new RegExp(ANCHOR_TITLE) });
  await expect(result).toBeVisible();

  await result.click();
  await expect(page).toHaveURL(/\/talk\/0$/);
  await expect(page.getByText("core").first()).toBeVisible();
  await expect(page.getByText("unexpected").first()).toBeVisible();
});

test("picks rail shows real engine recommendations with scores", async ({
  page,
}) => {
  await page.goto("/talk/0");
  // Core pick 2802 (Ni-DNA memristive nanowires) surfaced by the Stage-0 run.
  await expect(page.getByText(/Memristive/i).first()).toBeVisible();
  await expect(page.getByText(/\/15/).first()).toBeVisible();
});

test("calendar shows day agenda with walking transitions", async ({
  page,
}) => {
  await page.goto("/talk/0/calendar");
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
    `${baseURL}/api/trpc/agenda?input=${encodeURIComponent(
      JSON.stringify({ talkId: 0 }),
    )}`,
  );
  expect(res.ok()).toBe(true);
  const days = (await res.json()).result.data.days as {
    date: string;
    items: { id: number }[];
  }[];
  const ids = days.flatMap((d) => d.items.map((i) => i.id));
  // The 8 matches from the calibrated Stage-0 run, minus nothing.
  expect(ids.sort((a, b) => a - b)).toEqual([
    2802, 3100, 5432, 8500, 9437, 12292, 12342, 12772,
  ]);
});
