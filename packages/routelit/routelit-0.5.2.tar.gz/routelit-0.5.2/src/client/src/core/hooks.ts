import { createElement, ComponentProps, useRef, useMemo } from "react";
import { useFormDispatcherWithAttr, useComponentStore } from "./context";
import { FinalComponent } from "./react-renderer";
import { type ComponentStore } from "./component-store";

type InputEventTarget =
  | HTMLInputElement
  | HTMLTextAreaElement
  | { value: string };

type InputHookResult<T extends InputEventTarget> = {
  handleBlur: (e: React.FocusEvent<T>) => void;
  handleKeyDown: (e: React.KeyboardEvent<T>) => void;
};

export const EVENT_VALUE_GETTER = (
  e:
    | React.FocusEvent<HTMLInputElement | HTMLTextAreaElement>
    | React.KeyboardEvent<HTMLInputElement | HTMLTextAreaElement>
    | React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
) => e.currentTarget.value;

/**
 * Hook to handle input change events.
 * @param id - The id of the input.
 * @param value - The value of the input.
 * @param valueGetter - The function to use to get the value from the event. Default is EVENT_VALUE_GETTER.
 * @returns A hook to handle input change events.
 * @example
 * const { handleBlur, handleKeyDown } = useInputChangeEvent("input_id", "input_value");
 * return <input onBlur={handleBlur} onKeyDown={handleKeyDown} />;
 */
export function useInputChangeEvent<
  T extends HTMLInputElement | HTMLTextAreaElement
>(
  id: string,
  value: string,
  valueGetter: (
    e: React.FocusEvent<T> | React.KeyboardEvent<T> | React.ChangeEvent<T>
  ) => string = EVENT_VALUE_GETTER
): InputHookResult<T> {
  const dispatchChange = useFormDispatcherWithAttr(id, "change", "value");
  const lastValueRef = useRef(value);

  function handleChange(newValue: string) {
    if (newValue !== lastValueRef.current) {
      lastValueRef.current = newValue;
      dispatchChange(newValue);
    }
  }

  const handleBlur = (e: React.FocusEvent<T>) => {
    handleChange(valueGetter(e));
  };

  const handleKeyDown = (e: React.KeyboardEvent<T>) => {
    if (e.key === "Enter") {
      handleChange(valueGetter(e));
    }
  };

  return { handleBlur, handleKeyDown };
}

function getInlineElements<T extends React.ElementType>(
  props: Partial<ComponentProps<T>>,
  elementKeys: (keyof ComponentProps<T>)[] | undefined,
  componentStore: ComponentStore
): Record<keyof ComponentProps<T>, React.ReactElement<unknown>> | null {
  const elements = {} as Record<
    keyof ComponentProps<T>,
    React.ReactElement<unknown>
  >;
  if (!elementKeys || elementKeys.length === 0) return null;
  for (const key of elementKeys) {
    if (!props[key]) continue;
    const element = createElement(FinalComponent, {
      c: props[key],
      componentStore,
    });
    elements[key] = element;
  }
  return elements;
}

/**
 * A hook that can be used to get the inline elements of a component.
 * @param props - The props of the component.
 * @param elementKeys - The keys of the elements to get.
 * @returns The inline elements of the component.
 * @example
 * const inlineElements = useRLInlineElement(props, ["input", "button"]);
 * return <div>{inlineElements.input}{inlineElements.button}</div>;
 */
export function useRLInlineElement<T extends React.ElementType>(
  props: Partial<ComponentProps<T>>,
  elementKeys: (keyof ComponentProps<T>)[] | undefined
): Record<keyof ComponentProps<T>, React.ReactElement<unknown>> | null {
  const componentStore = useComponentStore();
  return useMemo(
    () => getInlineElements(props, elementKeys, componentStore),
    [props, elementKeys, componentStore]
  );
}

function getCallbackAttributes<T extends React.ElementType>(
  props: Partial<ComponentProps<T>>,
  rlCallbackAttrs: string[] | undefined
): Record<keyof ComponentProps<T>, (...args: unknown[]) => unknown> | null {
  if (!rlCallbackAttrs || rlCallbackAttrs.length === 0) return null;
  const attributes = {} as Record<
    keyof ComponentProps<T>,
    (...args: unknown[]) => unknown
  >;
  for (const attr of rlCallbackAttrs) {
    if (typeof props[attr] !== "string" || !props[attr]) continue;
    attributes[attr as keyof ComponentProps<T>] = new Function(
      props[attr] as string
    ) as (...args: unknown[]) => unknown;
  }
  return attributes;
}

/**
 * A hook that can be used to get the callback attributes of a component.
 * where the callback string is converted to a function that is passed to the component.
 * @param props - The props of the component.
 * @param rlCallbackAttrs - The attributes to get.
 * @returns The callback attributes of the component.
 * @example
 * // assumes props.onClick is a function body string like "console.log('click event', arguments[0]);"
 * const callbackAttributes = useRLCallbackAttributes(props, ["onClick"]);
 * return <button onClick={callbackAttributes.onClick}>Clickable</button>;
 */
export function useRLCallbackAttributes<T extends React.ElementType>(
  props: Partial<ComponentProps<T>>,
  rlCallbackAttrs: string[] | undefined
): Record<keyof ComponentProps<T>, (...args: unknown[]) => unknown> | null {
  return useMemo(
    () => getCallbackAttributes(props, rlCallbackAttrs),
    [props, rlCallbackAttrs]
  );
}

/**
 * A hook that can be used to handle a link click event.
 * @param id - The id of the component.
 * @param href - The href of the link.
 * @param replace - Whether to replace the current history entry.
 * @param isExternal - Whether the link is external.
 * @returns A function that can be used to handle a link click event.
 * @example
 * const handleClick = useLinkClickHandler({ id: "link", href: "/", replace: false, isExternal: false });
 * return <a href="/" onClick={handleClick}>Clickable</a>;
 */
export function useLinkClickHandler({
  id,
  href,
  replace,
  isExternal,
}: LinkHandlerProps): React.MouseEventHandler<HTMLAnchorElement> {
  const handleClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    if (isExternal) {
      return;
    }
    e.preventDefault();
    e.stopPropagation();
    const event = new CustomEvent<NavigateEventPayload>("routelit:event", {
      detail: {
        id: id!,
        type: "navigate",
        href: href!,
        replace: replace,
      },
    });
    document.dispatchEvent(event);
  };
  return handleClick;
}
