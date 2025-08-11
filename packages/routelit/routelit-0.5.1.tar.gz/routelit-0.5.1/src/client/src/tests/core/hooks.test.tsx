import { renderHook, render } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { useInputChangeEvent, EVENT_VALUE_GETTER, useRLInlineElement, useRLCallbackAttributes, useLinkClickHandler } from "../../core/hooks";
import * as context from "../../core/context";

// Extend the mock to include useComponentStore for inline element tests
vi.mock("../../core/context", () => ({
  useFormDispatcherWithAttr: vi.fn(),
  useComponentStore: vi.fn()
}));

describe("Hooks", () => {
  describe("useInputChangeEvent", () => {
    const mockDispatch = vi.fn();
    const initialValue = "initial";

    beforeEach(() => {
      vi.clearAllMocks();
      (context.useFormDispatcherWithAttr as unknown as { mockReturnValue: (v: unknown) => void }).mockReturnValue(mockDispatch);
    });

    it("dispatches value on blur when value changes", () => {
      const { result } = renderHook(() => useInputChangeEvent("test", initialValue));
      
      result.current.handleBlur({
        currentTarget: { value: "new value" },
      } as React.FocusEvent<HTMLInputElement>);

      expect(mockDispatch).toHaveBeenCalledWith("new value");
    });

    it("does not dispatch on blur when value is unchanged", () => {
      const { result } = renderHook(() => useInputChangeEvent("test", initialValue));
      
      result.current.handleBlur({
        currentTarget: { value: initialValue },
      } as React.FocusEvent<HTMLInputElement>);

      expect(mockDispatch).not.toHaveBeenCalled();
    });

    it("dispatches value on Enter key when value changes", () => {
      const { result } = renderHook(() => useInputChangeEvent("test", initialValue));
      
      result.current.handleKeyDown({
        key: "Enter",
        currentTarget: { value: "new value" },
      } as React.KeyboardEvent<HTMLInputElement>);

      expect(mockDispatch).toHaveBeenCalledWith("new value");
    });

    it("does not dispatch on Enter key when value is unchanged", () => {
      const { result } = renderHook(() => useInputChangeEvent("test", initialValue));
      
      result.current.handleKeyDown({
        key: "Enter",
        currentTarget: { value: initialValue },
      } as React.KeyboardEvent<HTMLInputElement>);

      expect(mockDispatch).not.toHaveBeenCalled();
    });

    it("does not dispatch on non-Enter key press", () => {
      const { result } = renderHook(() => useInputChangeEvent("test", initialValue));
      
      result.current.handleKeyDown({
        key: "a",
        currentTarget: { value: "new value" },
      } as React.KeyboardEvent<HTMLInputElement>);

      expect(mockDispatch).not.toHaveBeenCalled();
    });

    it("uses custom value getter when provided", () => {
      const customGetter = (e: React.FocusEvent<HTMLInputElement> | React.KeyboardEvent<HTMLInputElement> | React.ChangeEvent<HTMLInputElement>) => 
        e.currentTarget.value.toUpperCase();
      const { result } = renderHook(() => 
        useInputChangeEvent("test", initialValue, customGetter)
      );
      
      result.current.handleBlur({
        currentTarget: { value: "new value" },
      } as React.FocusEvent<HTMLInputElement>);

      expect(mockDispatch).toHaveBeenCalledWith("NEW VALUE");
    });
  });

  describe("EVENT_VALUE_GETTER", () => {
    it("returns the current target value", () => {
      const event = {
        currentTarget: { value: "test value" },
      } as React.ChangeEvent<HTMLInputElement>;

      expect(EVENT_VALUE_GETTER(event)).toBe("test value");
    });
  });

  describe("useRLInlineElement", () => {
    beforeEach(() => {
      vi.clearAllMocks();
    });

    it("returns rendered inline elements for provided keys", () => {
      const fakeComponentStore = {
        get: vi.fn(() => (props: { id: string }) => <div data-testid={`inline-${props.id}`}>Inline</div>),
      } as unknown as { get: (name: string) => React.ComponentType<any> | null };

      (context.useComponentStore as unknown as { mockReturnValue: (v: unknown) => void }).mockReturnValue(fakeComponentStore);

      function Test() {
        const props = {
          header: { name: "test", key: "hdr", props: {}, children: undefined },
        } as any;
        const el = useRLInlineElement(props, ["header"] as any);
        return <div>{el?.header}</div>;
      }

      const { getByTestId } = render(<Test />);
      expect(getByTestId("inline-hdr")).toBeInTheDocument();
      expect(fakeComponentStore.get).toHaveBeenCalledWith("test");
    });

    it("returns null when no element keys provided", () => {
      const fakeComponentStore = { get: vi.fn(() => null) } as any;
      (context.useComponentStore as unknown as { mockReturnValue: (v: unknown) => void }).mockReturnValue(fakeComponentStore);

      function Test() {
        const props = {} as any;
        const el = useRLInlineElement(props, undefined);
        return <div>{el === null ? "no-el" : "has-el"}</div>;
      }

      const { getByText } = render(<Test />);
      expect(getByText("no-el")).toBeInTheDocument();
    });
  });

  describe("useRLCallbackAttributes", () => {
    it("converts string function bodies to callable functions", () => {
      const props = {
        onClick: "return arguments[0] + 1;",
      } as any;

      const { result } = renderHook(() => useRLCallbackAttributes(props, ["onClick"]));
      expect(result.current).not.toBeNull();
      const fn = (result.current as any).onClick as (x: number) => number;
      expect(fn(1)).toBe(2);
    });

    it("ignores non-string attributes", () => {
      const props = {
        onClick: 123,
      } as any;

      const { result } = renderHook(() => useRLCallbackAttributes(props, ["onClick"]));
      expect(result.current).toEqual({});
      expect((result.current as any).onClick).toBeUndefined();
    });
  });

  describe("useLinkClickHandler", () => {
    beforeEach(() => {
      vi.clearAllMocks();
    });

    it("dispatches navigate event and prevents default for internal links", () => {
      const dispatchSpy = vi.spyOn(document, "dispatchEvent").mockImplementation(() => true);
      const { result } = renderHook(() => useLinkClickHandler({ id: "link1", href: "/path", replace: false, isExternal: false }));

      const preventDefault = vi.fn();
      const stopPropagation = vi.fn();
      result.current({
        preventDefault,
        stopPropagation,
        currentTarget: { href: "/path" },
      } as unknown as React.MouseEvent<HTMLAnchorElement>);

      expect(preventDefault).toHaveBeenCalled();
      expect(stopPropagation).toHaveBeenCalled();
      expect(dispatchSpy).toHaveBeenCalledWith(expect.objectContaining({
        type: "routelit:event",
        detail: expect.objectContaining({ id: "link1", type: "navigate", href: "/path", replace: false })
      }));
    });

    it("does nothing for external links", () => {
      const dispatchSpy = vi.spyOn(document, "dispatchEvent").mockImplementation(() => true);
      const { result } = renderHook(() => useLinkClickHandler({ id: "link2", href: "https://example.com", replace: false, isExternal: true }));

      const preventDefault = vi.fn();
      const stopPropagation = vi.fn();
      result.current({
        preventDefault,
        stopPropagation,
        currentTarget: { href: "https://example.com" },
      } as unknown as React.MouseEvent<HTMLAnchorElement>);

      expect(preventDefault).not.toHaveBeenCalled();
      expect(stopPropagation).not.toHaveBeenCalled();
      expect(dispatchSpy).not.toHaveBeenCalled();
    });
  });
});
