import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import App from "./App.jsx";

describe("frontend workspace", () => {
  it("renders the application heading", () => {
    render(<App />);

    expect(
      screen.getByRole("heading", { name: "Jira Weekly Status Reports" })
    ).toBeTruthy();
    expect(screen.getByText(/up to 20 risk entries/)).toBeTruthy();
  });
});
