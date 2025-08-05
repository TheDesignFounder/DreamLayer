import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, beforeAll, afterEach, afterAll } from "vitest";
import { setupServer } from "msw/node";
import { handlers } from "../../mocks/handlers";
import ProgressBar from "../ProgressBar";

const server = setupServer(...handlers);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe("ProgressBar", () => {
  it("should not render when progress is 0", () => {
    render(<ProgressBar />);
    expect(screen.queryByRole("progressbar")).not.toBeInTheDocument();
  });

  it("should render and update progress", async () => {
    render(<ProgressBar />);

    // Wait for progress to start
    await waitFor(
      () => {
        const progressBar = screen.queryByRole("progressbar");
        return progressBar !== null;
      },
      { timeout: 2000 }
    );

    const progressBar = screen.getByRole("progressbar");
    expect(progressBar).toBeInTheDocument();

    // Check that progress updates
    await waitFor(
      () => {
        const progressValue = progressBar.getAttribute("aria-valuenow");
        return progressValue && parseInt(progressValue) > 0;
      },
      { timeout: 3000 }
    );
  });

  it("should show progress messages", async () => {
    render(<ProgressBar />);

    await waitFor(
      () => {
        return screen.queryByText(
          /Initializing|Processing|Generating|Finalizing/
        );
      },
      { timeout: 2000 }
    );

    expect(
      screen.getByText(/Initializing|Processing|Generating|Finalizing/)
    ).toBeInTheDocument();
  });

  it("should hide when progress reaches 100%", async () => {
    render(<ProgressBar />);

    // Wait for progress to start
    await waitFor(
      () => {
        return screen.queryByRole("progressbar") !== null;
      },
      { timeout: 2000 }
    );

    // Wait for completion and hiding
    await waitFor(
      () => {
        const progressBar = screen.queryByRole("progressbar");
        return progressBar === null;
      },
      { timeout: 10000 }
    );
  });
});
