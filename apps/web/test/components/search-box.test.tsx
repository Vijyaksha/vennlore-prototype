// @vitest-environment jsdom
import "@testing-library/jest-dom/vitest";
import { fireEvent, screen } from "@testing-library/react";
import { describe, expect, test, vi } from "vitest";

import { SearchBox } from "../../components/search-box";
import { renderWithIntl } from "./intl";

const TEXT = "I study exciton transport in porphyrin films with transient photocurrent.";

describe("SearchBox", () => {
  test("submits the description once it is long enough", () => {
    const onSearch = vi.fn();
    renderWithIntl(<SearchBox pending={false} error={null} onSearch={onSearch} />);
    const box = screen.getByRole("textbox", { name: "Describe your research" });
    const button = screen.getByRole("button", { name: "Find talks and papers" });
    expect(button).toBeDisabled();
    fireEvent.change(box, { target: { value: "too short" } });
    expect(button).toBeDisabled();
    fireEvent.change(box, { target: { value: TEXT } });
    fireEvent.click(button);
    expect(onSearch).toHaveBeenCalledWith(TEXT);
  });

  test("shows progress while the search runs", () => {
    renderWithIntl(<SearchBox pending error={null} onSearch={() => {}} />);
    expect(screen.getByRole("button", { name: "Searching…" })).toBeDisabled();
  });

  test("shows the error message", () => {
    renderWithIntl(<SearchBox pending={false} error="The search service is not running." onSearch={() => {}} />);
    expect(screen.getByRole("alert")).toHaveTextContent("The search service is not running.");
  });
});
