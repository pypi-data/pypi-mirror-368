interface RouteLitComponent {
  key: string;
  /**
   * The name or type of the component. It could be a html tag name or a custom component name.
   */
  name: string;
  props: Record<string, unknown>;
  children?: RouteLitComponent[];
  address?: number[];
  stale?: boolean;
  virtual?: boolean;
}

type ActionType =
  | "add"
  | "remove"
  | "update"
  | "set"
  | "fresh_boundary"
  | "last";

type IAction = {
  type: string;
  /**
   * The address is the sequence of indices to the array tree of elements in the session state
   * from the root to the target element.
   */
  address: number[];
  target?: "app" | "fragment";
};

type AddAction = IAction & {
  type: "add";
  element: RouteLitComponent;
};

type SetAction = IAction & {
  type: "set";
  element: RouteLitComponent;
};

type RemoveAction = IAction & {
  type: "remove";
};

type UpdateAction = IAction & {
  type: "update";
  props: Record<string, unknown>;
};

type FreshBoundaryAction = IAction & {
  type: "fresh_boundary";
};

type LastAction = IAction & {
  type: "last";
};

type NoChangeAction = IAction & {
  type: "no_change";
};

type Action =
  | AddAction
  | SetAction
  | RemoveAction
  | UpdateAction
  | FreshBoundaryAction
  | LastAction
  | NoChangeAction;

type ActionsResponse = {
  actions: Action[];
  target: "app" | "fragment";
};

interface UIEventPayload {
  type: string;
  id: string;
  formId?: string;
  [key: string]: unknown;
}

interface NavigateEventPayload extends UIEventPayload {
  type: "navigate";
  href: string;
  lastURL?: string;
  isExternal?: boolean;
  replace?: boolean;
  target?: "_blank" | "_self";
}

interface InitializeEventPayload extends UIEventPayload {
  type: "initialize";
}

interface ChangeEventPayload extends UIEventPayload {
  value: string | number;
}

interface LinkHandlerProps {
  id: string;
  href: string;
  replace?: boolean;
  isExternal?: boolean;
}
