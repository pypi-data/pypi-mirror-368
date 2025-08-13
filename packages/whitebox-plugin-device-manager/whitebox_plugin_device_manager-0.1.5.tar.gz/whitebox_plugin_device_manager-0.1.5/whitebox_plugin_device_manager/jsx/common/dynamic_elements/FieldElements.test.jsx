import { fireEvent, render, act, cleanup } from "@testing-library/react";
import { DEInputPassword, DEInputText } from "./FieldElements";

afterEach(cleanup);

describe("DEInputText", () => {
  describe("rendering", () => {
    it("should render", async () => {
      const config = {
        type: "text",
        name: "name-value",
        placeholder: "placeholder-value",
        required: false,
      };
      const getter = "getter-value";

      const { container } = render(
        <DEInputText config={config} getter={getter} />
      );

      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 0));
      });

      const fieldContainer = container.querySelector(".c_input_field");
      expect(fieldContainer).toBeInTheDocument();

      const input = container.querySelector("input");
      expect(input).toBeInTheDocument();
      expect(input).toHaveAttribute("name", "name-value");
      expect(input).toHaveAttribute("placeholder", "placeholder-value");
      expect(input).toHaveAttribute("value", "getter-value");
      expect(input).not.toBeRequired();

      const fieldError = container.querySelector(".c_field_error");
      expect(fieldError).not.toBeInTheDocument();
    });

    it("should render with error", async () => {
      const config = {
        type: "text",
        name: "name-value",
        placeholder: "placeholder-value",
        required: false,
      };
      const getter = "getter-value";
      const errorGetter = "error-getter-value";

      const { container } = render(
        <DEInputText
          config={config}
          getter={getter}
          errorGetter={errorGetter}
        />
      );

      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 0));
      });

      const fieldError = container.querySelector(".c_field_error");
      expect(fieldError).toBeInTheDocument();
      expect(fieldError).toHaveTextContent("error-getter-value");
    });

    it("should render with required", async () => {
      const config = {
        type: "text",
        name: "name-value",
        placeholder: "placeholder-value",
        required: true,
      };
      const getter = "getter-value";

      const { container } = render(
        <DEInputText config={config} getter={getter} />
      );

      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 0));
      });

      const input = container.querySelector("input");
      expect(input).toBeRequired();
    });
  });

  describe("interaction", () => {
    it("should call setter on input change", async () => {
      const config = {
        type: "text",
        name: "name-value",
        placeholder: "placeholder-value",
        required: false,
      };
      const getter = "getter-value";
      const setter = vi.fn();

      const { container } = render(
        <DEInputText config={config} getter={getter} setter={setter} />
      );

      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 0));
      });

      const input = container.querySelector("input");
      fireEvent.change(input, { target: { value: "new-value" } });
      expect(setter).toHaveBeenCalledWith("new-value");
    });
  });
});

describe("DEInputPassword", () => {
  describe("rendering", () => {
    it("should render", async () => {
      const config = {
        type: "password",
        name: "name-value",
        placeholder: "placeholder-value",
        required: false,
      };
      const getter = "getter-value";

      const { container } = render(
        <DEInputPassword config={config} getter={getter} />
      );

      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 0));
      });

      const fieldContainer = container.querySelector(".c_input_field");
      expect(fieldContainer).toBeInTheDocument();

      const input = container.querySelector("input");
      expect(input).toBeInTheDocument();
      expect(input).toHaveAttribute("type", "password");
    });
  });

  describe("interaction", () => {
    it("should toggle password visibility", async () => {
      const config = {
        type: "password",
        name: "name-value",
        placeholder: "placeholder-value",
        required: false,
      };
      const getter = "getter-value";

      const { container } = render(
        <DEInputPassword config={config} getter={getter} />
      );

      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 0));
      });

      const input = container.querySelector("input");
      const icon = container.querySelector("svg");

      expect(input).toHaveAttribute("type", "password");

      // TODO: Bug: The component does not toggle the password visibility in test environment
      fireEvent.click(icon);
      expect(input).toHaveAttribute("type", "text");

      fireEvent.click(icon);
      expect(input).toHaveAttribute("type", "password");
    });
  });
});
