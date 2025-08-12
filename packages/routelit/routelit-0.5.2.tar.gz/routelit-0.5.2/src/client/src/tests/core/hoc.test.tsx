import { render, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  withSimpleComponent,
  withEventDispatcher,
  withValueEventDispatcher,
  withInputValueEventDispatcher,
  withCallbackAttributes,
} from "../../core/hoc";
import * as context from "../../core/context";

vi.mock("../../core/context", () => ({
  useFormDispatcher: vi.fn(),
  useFormDispatcherWithAttr: vi.fn(),
  useComponentStore: vi.fn(() => ({
    getComponent: vi.fn(),
    getInlineElements: vi.fn(() => null)
  })),
}));

type MockFn = {
  mockReturnValue: (value: unknown) => void;
};

type InputEvent = React.FocusEvent<HTMLInputElement> | React.KeyboardEvent<HTMLInputElement> | React.ChangeEvent<HTMLInputElement>;

describe("HOC utilities", () => {
  describe("withSimpleComponent", () => {
    it("renders component with initial props", () => {
      const TestComponent = withSimpleComponent("div", { className: "test" });
      const { container } = render(<TestComponent id="test" />);
      const div = container.querySelector("div");
      expect(div).toHaveClass("test");
    });

    it("merges props correctly", () => {
      const TestComponent = withSimpleComponent("div", { className: "test" });
      const { container } = render(<TestComponent id="test" className="override" />);
      const div = container.querySelector("div");
      expect(div).toHaveClass("override");
    });
  });

  describe("withEventDispatcher", () => {
    const mockDispatch = vi.fn();

    beforeEach(() => {
      vi.clearAllMocks();
      ((context.useFormDispatcher as unknown) as MockFn).mockReturnValue(mockDispatch);
    });

    it("dispatches event on click", () => {
      const TestButton = withEventDispatcher("button");
      const { getByRole } = render(
        <TestButton id="test" rlEventName="click" rlEventAttr="onClick" />
      );
      
      fireEvent.click(getByRole("button"));
      expect(mockDispatch).toHaveBeenCalledWith({});
    });

    it("uses custom event name and attribute", () => {
      const TestButton = withEventDispatcher("button", {
        rlEventName: "custom",
        rlEventAttr: "onCustom",
      });
      render(<TestButton id="test" rlEventName="custom" rlEventAttr="onCustom" />);
      
      expect(context.useFormDispatcher).toHaveBeenCalledWith("test", "custom");
    });
  });

  describe("withValueEventDispatcher", () => {
    const mockDispatch = vi.fn();

    beforeEach(() => {
      vi.clearAllMocks();
      ((context.useFormDispatcherWithAttr as unknown) as MockFn).mockReturnValue(mockDispatch);
    });

    it("dispatches value on change", () => {
      const TestInput = withValueEventDispatcher("input", { type: "text" });
      const { getByRole } = render(
        <TestInput 
          id="test" 
          rlEventName="change" 
          rlEventAttr="onChange" 
          rlValueAttr="value"
        />
      );
      
      fireEvent.change(getByRole("textbox"), { target: { value: "test" } });
      expect(mockDispatch).toHaveBeenCalledWith("test");
    });

    it("uses custom value getter", () => {
      const customGetter = (e: InputEvent) => e.currentTarget.value.toUpperCase();
      const TestInput = withValueEventDispatcher("input", {
        rlEventValueGetter: customGetter,
        type: "text",
      });
      const { getByRole } = render(
        <TestInput 
          id="test" 
          rlEventName="change" 
          rlEventAttr="onChange" 
          rlValueAttr="value"
        />
      );
      
      fireEvent.change(getByRole("textbox"), { target: { value: "test" } });
      expect(mockDispatch).toHaveBeenCalledWith("TEST");
    });
  });

  describe("withInputValueEventDispatcher", () => {
    const mockDispatch = vi.fn();

    beforeEach(() => {
      vi.clearAllMocks();
      ((context.useFormDispatcherWithAttr as unknown) as MockFn).mockReturnValue(mockDispatch);
    });

    it("dispatches value on blur", () => {
      const TestInput = withInputValueEventDispatcher("input", { 
        type: "text",
        defaultValue: "initial",
      });
      const { getByRole } = render(
        <TestInput 
          id="test" 
          rlOnBlurAttr="onBlur"
          rlOnKeyDownAttr="onKeyDown"
          rlValueAttr="defaultValue"
          rlEventValueGetter={(e: unknown): unknown => {
            const event = e as InputEvent;
            return event.currentTarget.value;
          }}
        />
      );
      
      fireEvent.blur(getByRole("textbox"));
      expect(mockDispatch).toHaveBeenCalledWith("initial");
    });

    it("dispatches value on Enter key", () => {
      const TestInput = withInputValueEventDispatcher("input", { 
        type: "text",
        defaultValue: "initial",
      });
      const { getByRole } = render(
        <TestInput 
          id="test" 
          rlOnBlurAttr="onBlur"
          rlOnKeyDownAttr="onKeyDown"
          rlValueAttr="defaultValue"
          rlEventValueGetter={(e: unknown): unknown => {
            const event = e as InputEvent;
            return event.currentTarget.value;
          }}
        />
      );
      
      fireEvent.keyDown(getByRole("textbox"), { key: "Enter" });
      expect(mockDispatch).toHaveBeenCalledWith("initial");
    });

    it("does not dispatch on other keys", () => {
      const TestInput = withInputValueEventDispatcher("input", { 
        type: "text",
        defaultValue: "initial",
      });
      const { getByRole } = render(
        <TestInput 
          id="test" 
          rlOnBlurAttr="onBlur"
          rlOnKeyDownAttr="onKeyDown"
          rlValueAttr="defaultValue"
          rlEventValueGetter={(e: unknown): unknown => {
            const event = e as InputEvent;
            return event.currentTarget.value;
          }}
        />
      );
      
      fireEvent.keyDown(getByRole("textbox"), { key: "a" });
      expect(mockDispatch).not.toHaveBeenCalled();
    });
  });

  describe("withCallbackAttributes", () => {
    it("converts callback strings to functions and passes them", () => {
      const Base = ({ onClick }: { onClick?: (...args: unknown[]) => unknown }) => (
        <button onClick={() => onClick?.(2)}>Btn</button>
      );
      const Wrapped = withCallbackAttributes(Base, { rlCallbackAttrs: ["onClick"] });

      const { getByRole } = render(<Wrapped onClick={"return arguments[0] * 3;" as unknown as ((...args: unknown[]) => unknown)} />);
      
      expect(() => fireEvent.click(getByRole("button"))).not.toThrow();
    });

    it("wraps input onChange string callback and logs input value", () => {
      const logSpy = vi.spyOn(console, "log").mockImplementation(() => {});
      const WrappedInput = withCallbackAttributes("input", { rlCallbackAttrs: ["onChange"], type: "text" });

      const { getByRole } = render(
        <WrappedInput onChange={"console.log(arguments[0].target.value)" as unknown as ((...args: unknown[]) => unknown)} />
      );

      const input = getByRole("textbox");
      fireEvent.change(input, { target: { value: "hello" } });

      expect(logSpy).toHaveBeenCalledWith("hello");
      logSpy.mockRestore();
    });
  });
}); 