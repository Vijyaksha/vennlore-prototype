// @vitest-environment jsdom
import "@testing-library/jest-dom/vitest";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";

import { screen } from "@testing-library/react";
import { describe, expect, test } from "vitest";

import type { Pick, Talk } from "@repo/contracts";

import { PickCard } from "../../components/pick-card";
import { paperSource, paperUrl } from "../../lib/paper";
import { renderWithIntl } from "./intl";

const req = createRequire(import.meta.url);
const fixture = (kind: string) =>
  JSON.parse(readFileSync(req.resolve(`@repo/contracts/fixtures/valid/${kind}.json`), "utf8"));

const ANCHORS = [{ id: 0, title: "Porphyrin nanorods" }];

/** A preprint candidate: the data layer's shape for arXiv / bioRxiv / medRxiv papers. */
const paperPick = (candidate: Partial<Talk>, cross_domain = true): Pick => ({
  ...(fixture("recommendation") as Omit<Pick, "candidate">),
  candidate_id: 1600000000,
  cross_domain,
  why: "Uses transient photocurrent, like your talk.",
  shared_methods: ["transient photocurrent"],
  candidate: {
    ...(fixture("talk") as Talk),
    id: 1600000000,
    title: "Graph neural networks for exciton transport",
    external_id: "arXiv:2511.01234",
    type: "preprint:arxiv",
    units: ["arXiv:cs.LG"],
    topics: ["cs.LG"],
    start: null,
    end: null,
    session_title: null,
    building: null,
    room: null,
    presenter_ids: [],
    author_ids: [],
    publication_reference: "arXiv 2025-11-03",
    ...candidate,
  },
});

describe("paper tiles", () => {
  test("flag the archive instead of a division", () => {
    renderWithIntl(<PickCard pick={paperPick({})} anchors={ANCHORS} />);
    expect(screen.getByText("arXiv · unexpected")).toBeInTheDocument();
    expect(screen.queryByText(/arXiv:cs\.LG/)).toBeNull();
  });

  test("show the posting reference where a talk shows its session", () => {
    renderWithIntl(<PickCard pick={paperPick({})} anchors={ANCHORS} />);
    expect(screen.getByText("arXiv 2025-11-03")).toBeInTheDocument();
  });

  test("link to the paper instead of the calendar", () => {
    renderWithIntl(<PickCard pick={paperPick({})} anchors={ANCHORS} />);
    const link = screen.getByRole("link", { name: "Read paper" });
    expect(link).toHaveAttribute("href", "https://arxiv.org/abs/2511.01234");
    expect(link).toHaveAttribute("target", "_blank");
    expect(screen.queryByRole("link", { name: "Calendar" })).toBeNull();
    expect(screen.getByText("Preprint")).toBeInTheDocument();
    expect(screen.queryByText("Time TBD")).toBeNull();
  });

  test("bioRxiv and medRxiv papers link through their DOI", () => {
    renderWithIntl(
      <PickCard
        pick={paperPick(
          { type: "preprint:biorxiv", external_id: "doi:10.1101/2025.10.30.685000",
            units: ["bioRxiv:neuroscience"], publication_reference: "bioRxiv 2025-11-01" },
          false,
        )}
        anchors={ANCHORS}
      />,
    );
    expect(screen.getByText("bioRxiv · core")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Read paper" })).toHaveAttribute(
      "href", "https://doi.org/10.1101/2025.10.30.685000");
  });

  test("talk tiles are unchanged", () => {
    const talk = { ...(fixture("recommendation") as Omit<Pick, "candidate">),
                   cross_domain: false, candidate: fixture("talk") as Talk } as Pick;
    renderWithIntl(<PickCard pick={talk} anchors={ANCHORS} />);
    expect(screen.getByText("DPOLY · core")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Calendar" })).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Read paper" })).toBeNull();
  });
});

describe("paper helpers", () => {
  test("paperSource names the archive, null for programme talks", () => {
    expect(paperSource("preprint:arxiv")).toBe("arXiv");
    expect(paperSource("preprint:medrxiv")).toBe("medRxiv");
    expect(paperSource("Oral-In-person")).toBeNull();
    expect(paperSource(null)).toBeNull();
  });

  test("paperUrl resolves arXiv ids and DOIs only", () => {
    expect(paperUrl("arXiv:2511.01234")).toBe("https://arxiv.org/abs/2511.01234");
    expect(paperUrl("doi:10.1101/x")).toBe("https://doi.org/10.1101/x");
    expect(paperUrl("SMT26-3750532")).toBeNull();
    expect(paperUrl(null)).toBeNull();
  });
});
