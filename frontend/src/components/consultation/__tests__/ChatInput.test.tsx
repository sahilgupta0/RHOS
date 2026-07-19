import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import ChatInput from "../ChatInput";

describe("ChatInput Component", () => {
  it("renders input field and send button", () => {
    const handleSend = vi.fn();
    render(<ChatInput onSend={handleSend} />);

    expect(screen.getByPlaceholderText("Type symptoms or speak...")).toBeInTheDocument();
    expect(screen.getByRole("button")).toBeInTheDocument();
  });

  it("submits typed text and clears input", () => {
    const handleSend = vi.fn();
    render(<ChatInput onSend={handleSend} />);

    const input = screen.getByPlaceholderText("Type symptoms or speak...");
    const form = input.closest("form")!;

    fireEvent.change(input, { target: { value: "Patient has high fever" } });
    fireEvent.submit(form);

    expect(handleSend).toHaveBeenCalledWith("Patient has high fever");
    expect(input).toHaveValue("");
  });

  it("does not call onSend if input is empty", () => {
    const handleSend = vi.fn();
    render(<ChatInput onSend={handleSend} />);

    const input = screen.getByPlaceholderText("Type symptoms or speak...");
    const form = input.closest("form")!;

    fireEvent.change(input, { target: { value: "   " } });
    fireEvent.submit(form);

    expect(handleSend).not.toHaveBeenCalled();
  });

  it("triggers speech dictation callback on mic click", () => {
    const handleSend = vi.fn();
    const handleSpeechToggle = vi.fn();
    render(
      <ChatInput
        onSend={handleSend}
        onSpeechToggle={handleSpeechToggle}
        isListening={false}
      />
    );

    const micBtn = screen.getByTitle("Start dictation");
    fireEvent.click(micBtn);

    expect(handleSpeechToggle).toHaveBeenCalledOnce();
  });

  it("triggers image upload callback on file change", () => {
    const handleSend = vi.fn();
    const handleImageUpload = vi.fn();
    const { container } = render(<ChatInput onSend={handleSend} onImageUpload={handleImageUpload} />);

    const uploadBtn = screen.getByTitle("Attach clinical image");
    expect(uploadBtn).toBeInTheDocument();

    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    const file = new File(["dummy content"], "xray.png", { type: "image/png" });

    fireEvent.change(fileInput, { target: { files: [file] } });

    expect(handleImageUpload).toHaveBeenCalledWith(file);
  });
});
