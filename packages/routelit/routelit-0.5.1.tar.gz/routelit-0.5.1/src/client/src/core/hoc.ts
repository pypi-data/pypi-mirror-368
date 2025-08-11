import {
  createElement,
  useCallback,
  PropsWithChildren,
  ComponentProps,
} from "react";
import { useFormDispatcher, useFormDispatcherWithAttr } from "./context";
import {
  useInputChangeEvent,
  EVENT_VALUE_GETTER,
  useRLInlineElement,
  useRLCallbackAttributes,
} from "./hooks";

/**
 * HOC to wrap a component with a simple component.
 * @param Component - The component to wrap.
 * @param initialProps - The initial props to pass to the component.
 * @param initialProps.rlInlineElementsAttrs - The attributes to use for the inline elements.
 * @returns A wrapped component that passes the initial props to the component.
 * @example
 * const Container = withSimpleComponent("div", {
 *   className: "container", // actual component props are passed
 *   rlInlineElementsAttrs: ["header"], // optional, default is undefined
 * });
 */
export function withSimpleComponent<T extends React.ElementType>(
  Component: T,
  props?: Partial<ComponentProps<T> & { rlInlineElementsAttrs: string[] }>
) {
  const { rlInlineElementsAttrs, ...initialProps } = (props || {}) as Partial<
    ComponentProps<T> & { rlInlineElementsAttrs: string[] }
  >;
  return function WithSimpleComponent({
    children,
    ...props
  }: PropsWithChildren<{ id: string }> & ComponentProps<T>) {
    const maybeInlineElements = useRLInlineElement(
      props,
      rlInlineElementsAttrs
    );
    const finalProps = initialProps
      ? { ...initialProps, ...props, ...maybeInlineElements }
      : props;
    return createElement(Component, finalProps, children);
  };
}

type WithEventNameProps = PropsWithChildren<{
  rlEventName: string;
  rlEventAttr: string;
  id: string;
  rlInlineElementsAttrs?: string[];
}>;

const DEFAULT_EVENT_DISPATCHER_PROPS: Omit<WithEventNameProps, "id"> = {
  rlEventName: "click",
  rlEventAttr: "onClick",
  rlInlineElementsAttrs: undefined,
};

/**
 * HOC to dispatch an event when the component is clicked.
 * @param Component - The component to wrap.
 * @param options - The options to pass to the component.
 * @param options.rlEventName - The name of the event to dispatch to server. Default is "click".
 * @param options.rlEventAttr - The attribute to use for the event to listen on react component. Default is "onClick".
 * @param options.rlInlineElementsAttrs - The attributes to use for the inline elements.
 * @returns A wrapped component that dispatches a click event when the component is clicked.
 * @example
 * const Button = withEventDispatcher("button", {
 *   rlEventName: "click", // optional, default is "click"
 *   rlEventAttr: "onClick", // optional, default is "onClick"
 *   rlInlineElementsAttrs: ["leftIcon", "rightIcon"], // optional, default is undefined
 *   type: "button", // actual component props are passed
 * });
 */
export function withEventDispatcher<T extends React.ElementType>(
  Component: T,
  options?: Partial<typeof DEFAULT_EVENT_DISPATCHER_PROPS & ComponentProps<T>>
) {
  const {
    rlEventName: upperRlEventName,
    rlEventAttr: upperRlEventAttr,
    rlInlineElementsAttrs: upperRlInlineElementsAttrs,
    ...initialProps
  } = { ...DEFAULT_EVENT_DISPATCHER_PROPS, ...options };
  return function WithEventDispatcher({
    children,
    rlEventName = upperRlEventName,
    rlEventAttr = upperRlEventAttr,
    rlInlineElementsAttrs = upperRlInlineElementsAttrs,
    ...props
  }: WithEventNameProps) {
    const dispatch = useFormDispatcher(props.id, rlEventName);
    const maybeInlineElements = useRLInlineElement(
      props,
      rlInlineElementsAttrs
    );
    const onEvent = useCallback(() => {
      dispatch({});
    }, [dispatch]);
    return createElement(
      Component,
      {
        ...initialProps,
        ...props,
        ...maybeInlineElements,
        [rlEventAttr]: onEvent,
      },
      children
    );
  };
}

type ValueHocProps = PropsWithChildren<{
  rlEventName: string;
  rlEventAttr: string;
  rlValueAttr: string;
  id: string;
  rlEventValueGetter(ev: unknown): unknown;
  rlInlineElementsAttrs?: string[];
}>;

const DEFAULT_VALUE_EVENT_DISPATCHER_PROPS: Omit<ValueHocProps, "id"> = {
  rlEventName: "change",
  rlEventAttr: "onChange",
  rlValueAttr: "value",
  rlEventValueGetter: EVENT_VALUE_GETTER as ValueHocProps["rlEventValueGetter"],
  rlInlineElementsAttrs: undefined,
};

/**
 * HOC to dispatch a change event when the component is changed.
 * @param Component - The component to wrap.
 * @param options - The options to pass to the component.
 * @param options.rlEventName - The name of the event to dispatch to server. Default is "change".
 * @param options.rlValueAttr - The attribute to use for the value attribute to send to server. Default is "value".
 * @param options.rlEventAttr - The attribute to use for the event to listen on react component. Default is "onChange".
 * @param options.rlEventValueGetter - The function to use to get the value from the event. Default is EVENT_VALUE_GETTER.
 * @param options.rlInlineElementsAttrs - The attributes to use for the inline elements.
 * @returns A wrapped component that dispatches a change event when the component is changed.
 * @example
 * const TextInput = withValueEventDispatcher("input", {
 *   rlEventName: "change",
 *   rlEventAttr: "onChange",
 *   rlValueAttr: "value",
 *   rlEventValueGetter: (e) => e.target.value,
 *   rlInlineElementsAttrs: ["leftIcon", "rightIcon"], // optional, default is undefined
 *   type: "text", // actual component props are passed
 * });
 * @example
 * const Checkbox = withValueEventDispatcher("input", {
 *   rlEventName: "change",
 *   rlEventAttr: "onChange",
 *   rlValueAttr: "checked",
 *   rlEventValueGetter: (e) => e.target.checked,
 *   type: "checkbox",
 * });
 */
export function withValueEventDispatcher<T extends React.ElementType>(
  Component: T,
  options?: Partial<
    typeof DEFAULT_VALUE_EVENT_DISPATCHER_PROPS & ComponentProps<T>
  >
) {
  const {
    rlEventName: upperRlEventName,
    rlEventAttr: upperRlEventAttr,
    rlValueAttr: upperRlValueAttr,
    rlEventValueGetter,
    rlInlineElementsAttrs: upperRlInlineElementsAttrs,
    ...initialProps
  } = { ...DEFAULT_VALUE_EVENT_DISPATCHER_PROPS, ...options };
  return function WithValueEventDispatcher({
    children,
    rlEventName = upperRlEventName,
    rlEventAttr = upperRlEventAttr,
    rlValueAttr = upperRlValueAttr,
    rlInlineElementsAttrs = upperRlInlineElementsAttrs,
    ...props
  }: Omit<ValueHocProps, "rlEventValueGetter">) {
    const dispatchChange = useFormDispatcherWithAttr(
      props.id,
      rlEventName,
      rlValueAttr
    );
    const maybeInlineElements = useRLInlineElement(
      props,
      rlInlineElementsAttrs
    );
    const onChange = useCallback(
      (e: React.ChangeEvent<HTMLInputElement>) => {
        dispatchChange(rlEventValueGetter(e));
      },
      [dispatchChange]
    );
    return createElement(
      Component,
      {
        ...initialProps,
        ...props,
        ...maybeInlineElements,
        [rlEventAttr]: onChange,
      },
      children
    );
  };
}

export type WithInputValueEventDispatcherProps = PropsWithChildren<{
  rlOnBlurAttr: string;
  rlOnKeyDownAttr: string;
  rlValueAttr: string;
  rlEventValueGetter: (e: unknown) => unknown;
  id: string;
  rlInlineElementsAttrs?: string[];
}>;

const DEFAULT_INPUT_VALUE_EVENT_DISPATCHER_PROPS: Omit<
  WithInputValueEventDispatcherProps,
  "id"
> = {
  rlOnBlurAttr: "onBlur",
  rlOnKeyDownAttr: "onKeyDown",
  rlValueAttr: "defaultValue",
  rlEventValueGetter:
    EVENT_VALUE_GETTER as WithInputValueEventDispatcherProps["rlEventValueGetter"],
  rlInlineElementsAttrs: undefined,
};

/**
 * HOC to dispatch a change event when the component is changed.
 *  This already uses the following defaults when sending the event to backend:
 * - rlEventName: "change"
 * - rlValueAttr: "value"
 * @param Component - The component to wrap.
 * @param options - The options to pass to the component.
 * @param options.rlOnBlurAttr - The attribute to use for the onBlur event. Default is "onBlur".
 * @param options.rlOnKeyDownAttr - The attribute to use for the onKeyDown event. Default is "onKeyDown".
 * @param options.rlValueAttr - The attribute to use for the value attribute. Default is "defaultValue".
 * @param options.rlEventValueGetter - The function to use to get the value from the event. Default is EVENT_VALUE_GETTER.
 * @param options.rlInlineElementsAttrs - The attributes to use for the inline elements.
 * @returns A wrapped component that dispatches a change event when the component is changed.
 * @example
 * const TextInput = withInputValueEventDispatcher("input", {
 *   rlOnBlurAttr: "onBlur", // optional, default is "onBlur"
 *   rlOnKeyDownAttr: "onKeyDown", // optional, default is "onKeyDown"
 *   rlEventValueGetter: (e) => e.target.value, // optional, default is EVENT_VALUE_GETTER
 *   rlInlineElementsAttrs: ["leftIcon", "rightIcon"], // optional, default is undefined
 *   type: "text", // actual component props are passed
 * });
 */
export function withInputValueEventDispatcher<T extends React.ElementType>(
  Component: T,
  options?: Partial<
    typeof DEFAULT_INPUT_VALUE_EVENT_DISPATCHER_PROPS & ComponentProps<T>
  >
) {
  const {
    rlOnBlurAttr: upperRlOnBlurAttr,
    rlOnKeyDownAttr: upperRlOnKeyDownAttr,
    rlValueAttr: upperRlValueAttr,
    rlEventValueGetter,
    rlInlineElementsAttrs: upperRlInlineElementsAttrs,
    ...initialProps
  } = { ...DEFAULT_INPUT_VALUE_EVENT_DISPATCHER_PROPS, ...options };
  return function WithInputValueEventDispatcher({
    children,
    rlOnBlurAttr = upperRlOnBlurAttr,
    rlOnKeyDownAttr = upperRlOnKeyDownAttr,
    rlValueAttr = upperRlValueAttr,
    rlInlineElementsAttrs = upperRlInlineElementsAttrs,
    ...props
  }: WithInputValueEventDispatcherProps) {
    const { handleBlur, handleKeyDown } = useInputChangeEvent(
      props.id,
      props[rlValueAttr as keyof typeof props] as string,
      rlEventValueGetter as typeof EVENT_VALUE_GETTER
    );
    const maybeInlineElements = useRLInlineElement(
      props,
      rlInlineElementsAttrs
    );
    return createElement(
      Component,
      {
        ...initialProps,
        ...props,
        ...maybeInlineElements,
        [rlOnBlurAttr]: handleBlur,
        [rlOnKeyDownAttr]: handleKeyDown,
      },
      children
    );
  };
}

type WithCallbackAttributesProps = {
  rlCallbackAttrs?: string[];
};

export function withCallbackAttributes<T extends React.ElementType>(
  Component: T,
  initialOptions?: Partial<ComponentProps<T> & WithCallbackAttributesProps>
) {
  const { rlCallbackAttrs: upperRlCallbackAttrs, ...initialProps } = {
    ...initialOptions,
  };
  return function WithCallbackAttributes({ ...props }: ComponentProps<T>) {
    const callbackAttributes = useRLCallbackAttributes(
      props,
      upperRlCallbackAttrs
    );
    return createElement(Component, {
      ...initialProps,
      ...props,
      ...callbackAttributes,
    });
  };
}
