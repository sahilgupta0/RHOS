import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import ChatMessage from "../ChatMessage";
import type { ChatMessage as ChatMessageType } from "../../../types";

describe("ChatMessage Component", () => {
  const timestamp = new Date("2026-07-19T10:00:00Z");

  it("renders user patient message with correct structure", () => {
    const message: ChatMessageType = {
      id: "1",
      role: "patient",
      content: "I have joint pain",
      timestamp,
    };

    const { container } = render(<ChatMessage message={message} />);
    expect(screen.getByText("I have joint pain")).toBeInTheDocument();
    
    // User message should have flex-row-reverse class
    const mainDiv = container.firstChild as HTMLElement;
    expect(mainDiv.className).toContain("flex-row-reverse");
  });

  it("renders assistant message with agent name", () => {
    const message: ChatMessageType = {
      id: "2",
      role: "assistant",
      content: "Analyzing symptoms...",
      timestamp,
      agentName: "Triage Agent",
    };

    render(<ChatMessage message={message} />);
    expect(screen.getByText("Analyzing symptoms...")).toBeInTheDocument();
    expect(screen.getByText("Triage Agent")).toBeInTheDocument();
  });

  it("renders system message with warning styling", () => {
    const message: ChatMessageType = {
      id: "3",
      role: "system",
      content: "Please check heart rate",
      timestamp,
    };

    const { container } = render(<ChatMessage message={message} />);
    expect(screen.getByText("Please check heart rate")).toBeInTheDocument();
    
    // System message background class check
    const contentDiv = container.querySelector(".rounded-2xl") as HTMLElement;
    expect(contentDiv.className).toContain("bg-amber-50");
  });
});
