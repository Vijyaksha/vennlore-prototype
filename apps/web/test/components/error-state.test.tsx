// @vitest-environment jsdom
import "@testing-library/jest-dom/vitest";
import { fireEvent, screen } from "@testing-library/react";
import { describe, expect, test, vi } from "vitest";

import { ErrorState } from "../../components/error-state";
import { renderWithIntl } from "./intl";

describe("ErrorState", () => {
  test("a failed load offers a retry", () => {
    const onRetry = vi.fn();
    renderWithIntl(<ErrorState onRetry={onRetry} />);

    expect(
      screen.getByText("Something went wrong loading this."),
    ).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Try again" }));
    expect(onRetry).toHaveBeenCalledOnce();
  });

  test("a subject that does not exist says so, with no retry", () => {
    renderWithIntl(<ErrorState notFound onRetry={() => {}} />);

    expect(
      screen.getByText("We couldn't find this presenter or talk."),
    ).toBeInTheDocument();
    expect(screen.queryByRole("button")).toBeNull();
  });
});
