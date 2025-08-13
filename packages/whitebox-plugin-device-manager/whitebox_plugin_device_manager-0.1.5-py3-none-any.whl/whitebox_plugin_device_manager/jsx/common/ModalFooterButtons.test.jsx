import { act, render, screen, cleanup } from "@testing-library/react";
import ModalFooterButtons from "./ModalFooterButtons";

afterEach(cleanup);

describe("ModalFooterButtons", () => {
  it("should render with only forward button", async () => {
    const buttonConfig = {
      text: "Execute order 66",
    };
    render(<ModalFooterButtons fwdBtn={buttonConfig} />);

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 0));
    });

    expect(await screen.findByText(buttonConfig.text)).toBeInTheDocument();
    const buttons = screen.getAllByRole("button");
    expect(buttons).toHaveLength(1);
  });

  it("should render with only back button", async () => {
    const buttonConfig = {
      text: "Cancel order 66",
    };
    render(<ModalFooterButtons bckBtn={buttonConfig} />);

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 0));
    });

    expect(await screen.findByText(buttonConfig.text)).toBeInTheDocument();
    const buttons = screen.getAllByRole("button");
    expect(buttons).toHaveLength(1);
  });
});
