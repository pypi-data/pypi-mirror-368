import { createContext, useContext, useCallback, useSyncExternalStore } from "react";
import { type ComponentStore } from "./component-store";
import { type RouteLitManager } from "./manager";
import { useFormId } from "../components/form";

type RouteLitContextType = {
  manager: RouteLitManager;
  componentStore: ComponentStore;
  parentManager?: RouteLitManager;
};

export const RouteLitContext = createContext<RouteLitContextType>({
  manager: undefined as unknown as RouteLitManager,
  componentStore: undefined as unknown as ComponentStore,
  parentManager: undefined as unknown as RouteLitManager,
});

export function useRouteLitContext() {
  const context = useContext(RouteLitContext);
  if (!context) {
    throw new Error(
      "useRouteLitContext must be used within a RouteLitContext.Provider"
    );
  }
  return context;
}

export function useComponentStore() {
  const { componentStore } = useRouteLitContext();
  return componentStore;
}

export function useDispatcher() {
  const { manager } = useRouteLitContext();
  return (event: CustomEvent<UIEventPayload>) => {
    manager.handleEvent(event);
  };
}

/**
 * A hook that can be used to dispatch a routelit custom event to the parent manager.
 * This is useful for components like buttons or any other with a custom payload.
 * @param id - The id of the component to dispatch the event to.
 * @param type - The type of the event to dispatch.
 * @returns A callback function that can be used to dispatch the event.
 * @example
 * const onClick = useDispatcherWith(id, "click");
 * return <button onClick={() => onClick({})}>Clickable</button>;
 */
export function useDispatcherWith(id: string, type: string) {
  const { manager } = useRouteLitContext();
  const callback = useCallback(
    (data: Record<string, unknown>) => {
      manager.handleEvent(
        new CustomEvent<UIEventPayload>("routelit:event", {
          detail: { id, type, ...data },
        })
      );
    },
    [manager, id, type]
  );
  return callback;
}

/**
 * A hook that can be used to dispatch a routelit custom event to the parent manager.
 * This is useful for components like checkboxes or any other with a custom attribute.
 * @param id - The id of the component to dispatch the event to.
 * @param type - The type of the event to dispatch.
 * @param attr - The attribute to dispatch the event to.
 * @returns A callback function that can be used to dispatch the event.
 */
export function useDispatcherWithAttr(id: string, type: string, attr: string) {
  const { manager } = useRouteLitContext();
  const callback = useCallback(
    (value: unknown) => {
      manager.handleEvent(
        new CustomEvent<UIEventPayload>("routelit:event", {
          detail: { id, type, [attr]: value },
        })
      );
    },
    [manager, id, type, attr]
  );
  return callback;
}

/**
 * A hook that can be used to dispatch a routelit custom event to the parent manager.
 * This is useful for form components like inputs, selects, checkboxes, etc.
 * @param id - The id of the component to dispatch the event to.
 * @param type - The type of the event to dispatch.
 * @returns A callback function that can be used to dispatch the event.
 * @example
 * const onClick = useFormDispatcher(id, "submit");
 * return <button onClick={() => onClick({})}>Submit</button>;
 */
export function useFormDispatcher(id: string, type: string) {
  const { manager } = useRouteLitContext();
  const formId = useFormId();
  const callback = useCallback((data: Record<string, unknown>) => {
    manager.handleEvent(new CustomEvent<UIEventPayload>("routelit:event", { detail: { id, type, formId, ...data } }));
  }, [manager, id, type, formId]);
  return callback;
}

/**
 * A hook that can be used to dispatch a routelit custom event to the parent manager.
 * This is useful for form components like inputs, selects, checkboxes, etc.
 * @param id - The id of the component to dispatch the event to.
 * @param type - The type of the event to dispatch.
 * @param attr - The attribute to dispatch the event to.
 * @returns A callback function that can be used to dispatch the event.
 * @example
 * const onChange = useFormDispatcherWithAttr(id, "change", "value");
 * return <input onBlur={(e) => onChange(e.target.value)} />;
 */
export function useFormDispatcherWithAttr(id: string, type: string, attr: string) {
  const { manager } = useRouteLitContext();
  const formId = useFormId();
  const callback = useCallback((value: unknown) => {
    manager.handleEvent(new CustomEvent<UIEventPayload>("routelit:event", { detail: { id, type, formId, [attr]: value } }));
  }, [manager, id, type, formId, attr]);
  return callback;
}

export function useIsLoading(): boolean {
  const { manager } = useRouteLitContext();
  return useSyncExternalStore(
    manager.subscribeIsLoading,
    manager.isLoading,
  );
}

export function useError(): Error | undefined {
  const { manager } = useRouteLitContext();
  return useSyncExternalStore(
    manager.subscribeError,
    manager.getError,
  );
}
