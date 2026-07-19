import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import PriorityBadge from "../PriorityBadge";

describe("PriorityBadge Component", () => {
  it("returns null if priority is not provided", () => {
    const { container } = render(<PriorityBadge />);
    expect(container.firstChild).toBeNull();
  });

  it("renders priority text and maps to correct colors for HIGH", () => {
    render(<PriorityBadge priority="HIGH" />);
    const badge = screen.getByText("HIGH");
    expect(badge).toBeInTheDocument();
    expect(badge.className).toContain("bg-rose-100");
    expect(badge.className).toContain("text-rose-700");
  });

  it("renders priority text and maps to correct colors for MEDIUM", () => {
    render(<PriorityBadge priority="MEDIUM" />);
    const badge = screen.getByText("MEDIUM");
    expect(badge).toBeInTheDocument();
    expect(badge.className).toContain("bg-amber-100");
    expect(badge.className).toContain("text-amber-700");
  });

  it("renders priority text and maps to correct colors for LOW", () => {
    render(<PriorityBadge priority="LOW" />);
    const badge = screen.getByText("LOW");
    expect(badge).toBeInTheDocument();
    expect(badge.className).toContain("bg-emerald-100");
    expect(badge.className).toContain("text-emerald-700");
  });

  it("applies extra className if passed as prop", () => {
    render(<PriorityBadge priority="LOW" className="my-custom-class" />);
    const badge = screen.getByText("LOW");
    expect(badge.className).toContain("my-custom-class");
  });
});
