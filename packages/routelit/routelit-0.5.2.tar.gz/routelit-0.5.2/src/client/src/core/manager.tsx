import { produce, enableMapSet, setAutoFreeze } from "immer";
import {
  applyActions,
  prependAddressToActions,
} from "./actions";
import { sendEventStream } from "./server-api";
import { TargetMutex } from "./utils/mutex";

enableMapSet();
setAutoFreeze(false);

type Handler = (args: RouteLitComponent) => void;
type IsLoadingHandler = (args: boolean) => void;
type ErrorHandler = (args: Error) => void;

interface RouteLitManagerProps {
  rootComponent?: RouteLitComponent;
  fragmentId?: string;
  parentManager?: RouteLitManager;
  address?: number[];
}

const THROTTLE_DELAY = 125; // 0.125 seconds

const ROOT_ELEMENT: RouteLitComponent = {
  key: "root",
  name: "root",
  props: {},
  children: [],
};

export class RouteLitManager {
  private listeners: Set<Handler> = new Set();
  private isLoadingListeners: Set<IsLoadingHandler> = new Set();
  private errorListeners: Set<ErrorHandler> = new Set();
  private rootComponent?: RouteLitComponent;
  private _isLoading: boolean = false;
  private _error?: Error;
  private fragmentId?: string;
  private parentManager?: RouteLitManager;
  private address?: number[];
  private lastURL?: string;
  private initialized: boolean = false;
  private actionAccumulator: Action[] = [];
  private currentTarget?: string;
  private throttleTimer?: NodeJS.Timeout;
  private lastExecutionTime: number = 0;
  private mutex?: TargetMutex;

  constructor(props: RouteLitManagerProps) {
    this.fragmentId = props.fragmentId;
    this.rootComponent = props.fragmentId
      ? undefined
      : props.rootComponent ?? ROOT_ELEMENT;
    this.parentManager = props.parentManager;
    this.address = props.address;
    this.lastURL = props.parentManager?.getLastURL() ?? window.location.href;
    this.mutex = props.fragmentId ? undefined : new TargetMutex();
  }

  getLastURL = (): string => {
    return this.parentManager?.getLastURL() ?? this.lastURL!;
  };

  handleEvent = async (e: CustomEvent<UIEventPayload>) => {
    if (e.detail.type === "navigate" && this.fragmentId) {
      // Let the upper manager handle the navigation
      return;
    }

    if (e.detail.type === "navigate") {
      const detail = e.detail as NavigateEventPayload;
      detail.lastURL = this.lastURL;
      this.lastURL = detail.href.startsWith("http")
        ? detail.href
        : window.location.origin + detail.href;
    }
    this._error = undefined;
    this._isLoading = true;
    this.notifyIsLoading();
    const rootManager = this.getRootManager();
    const eventTarget = this.fragmentId || "app";
    const unlock = await rootManager.mutex!.lock(eventTarget);
    try {
      const responseStream = sendEventStream(e, this.fragmentId);
      for await (const response of responseStream) {
        if ("type" in response) {
          this.batchAction(response);
        } else {
          this.applyActions(response);
        }
      }
    } catch (error) {
      this.handleError(error as Error);
    } finally {
      this._isLoading = false;
      this.notifyIsLoading();
      this.flushActions(true);
      unlock();
    }
    e.stopPropagation();
  };

  handleError = (e: Error) => {
    this._error = e;
    this.notifyError();
  };

  batchAction = (action: Action, shouldNotify = true) => {
    // For app-level actions in fragments, delegate immediately to parent
    if (this.fragmentId && action.target === "app") {
      // If there are actions in the accumulator, flush them before delegating to parent
      if (this.actionAccumulator.length > 0) {
        this.flushActions(shouldNotify);
      }
      this.parentManager?.batchAction(action, shouldNotify);
      return;
    }

    // Create a key for grouping actions by target
    const targetKey = action.target || "fragment";

    // If this is a new target, flush current actions first
    if (this.currentTarget && this.currentTarget !== targetKey) {
      this.flushActions(shouldNotify);
    }

    // Set the current target
    this.currentTarget = targetKey;

    // Add action to accumulator
    this.actionAccumulator.push({ ...action }); // Clone the action to avoid proxy issues

    const now = Date.now();

    // If enough time has passed since last execution, execute immediately
    if (now - this.lastExecutionTime >= THROTTLE_DELAY) {
      this.flushActions(shouldNotify);
    } else {
      // If a timer is already set, don't set another one
      if (!this.throttleTimer) {
        const remainingTime = THROTTLE_DELAY - (now - this.lastExecutionTime);
        this.throttleTimer = setTimeout(() => {
          this.flushActions(shouldNotify);
        }, remainingTime);
      }
    }
  };

  private flushActions = (shouldNotify: boolean) => {
    if (this.actionAccumulator.length === 0 || !this.currentTarget) return;

    // Clear the timer
    if (this.throttleTimer) {
      clearTimeout(this.throttleTimer);
      this.throttleTimer = undefined;
    }

    // Record the execution time
    this.lastExecutionTime = Date.now();

    // Create ActionsResponse and call applyActions
    const actionsResponse: ActionsResponse = {
      actions: [...this.actionAccumulator], // Clone the actions array
      target: this.currentTarget as "app" | "fragment",
    };

    // Clear the accumulator and target before applying actions
    this.actionAccumulator = [];
    this.currentTarget = undefined;

    // Apply the actions
    this.applyActions(actionsResponse, shouldNotify);
  };

  applyActions = (actionsResp: ActionsResponse, shouldNotify = true) => {
    if (this.fragmentId) {
      const shouldNotifyRoot = actionsResp.target === "app";
      // If the actions are for the app, we don't need to prepend the address
      const actionsWithAddress = shouldNotifyRoot
        ? actionsResp
        : prependAddressToActions(actionsResp, this.getCompleteAddressPath());
      this.getRootManager().applyActions(actionsWithAddress, shouldNotifyRoot);
      if (shouldNotify && !shouldNotifyRoot) this.notifyListeners();
      return;
    }

    if (actionsResp.actions.length === 0) return;

    try {
      const rootComponentCopy = produce(this.rootComponent!, (draft) => {
        applyActions(draft, actionsResp.actions);
      });
      this.rootComponent = rootComponentCopy;
      if (shouldNotify) this.notifyListeners();
    } catch (error) {
      console.error("Error applying actions:", error);
      this.handleError(error as Error);
    }
  };

  private initializeDOM = () => {
    if (this.initialized) return;
    const initializeEvent = new CustomEvent<InitializeEventPayload>(
      "routelit:event",
      {
        detail: {
          id: "browser-navigation",
          type: "initialize",
        },
      }
    );
    this.handleEvent(initializeEvent);
    this.initialized = true;
  };

  initialize = () => {
    this.initializeDOM();
    document.addEventListener(
      "routelit:event",
      this.handleEvent as unknown as EventListener
    );
    window.addEventListener("popstate", this.handlePopState as EventListener);
  };

  handlePopState = () => {
    const currentUrl = window.location.href;
    const navigateEvent = new CustomEvent<NavigateEventPayload>(
      "routelit:event",
      {
        detail: {
          type: "navigate",
          id: "browser-navigation",
          href: currentUrl,
          lastURL: this.lastURL,
        },
      }
    );
    document.dispatchEvent(navigateEvent);
  };

  terminate = () => {
    // Flush any pending actions before terminating
    if (this.actionAccumulator.length > 0) {
      this.flushActions(true);
    }

    // Clear the timer
    if (this.throttleTimer) {
      clearTimeout(this.throttleTimer);
      this.throttleTimer = undefined;
    }

    // Clear the accumulator
    this.actionAccumulator = [];
    this.currentTarget = undefined;

    document.removeEventListener(
      "routelit:event",
      this.handleEvent as unknown as EventListener
    );
    window.removeEventListener(
      "popstate",
      this.handlePopState as EventListener
    );
  };

  /**
   * Get the root manager (the one without a parent)
   */
  private getRootManager = (): RouteLitManager => {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    let current: RouteLitManager = this;
    while (current.parentManager) {
      current = current.parentManager;
    }
    return current;
  };

  /**
   * Build the complete address path from the root manager to this fragment
   */
  private getCompleteAddressPath = (): number[] => {
    const addressPath: number[] = [];
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    let current: RouteLitManager = this;

    while (current.parentManager && current.address) {
      // If we are in a fragment, and the parent manager is also a fragment,
      //  we need to remove the first element of the address,
      //  so the fragment position in address is not duplicated
      const address = current.parentManager.fragmentId
        ? current.address.slice(1)
        : current.address;
      addressPath.unshift(...address);
      current = current.parentManager;
    }
    return addressPath;
  };

  getRootComponent = (): RouteLitComponent => {
    if (this.parentManager && this.address) {
      return RouteLitManager.getElementAtAddress(
        this.getRootManager().rootComponent!,
        this.getCompleteAddressPath()
      );
    }
    return this.rootComponent!;
  };

  isLoading = (): boolean => {
    return this.parentManager?.isLoading() || this._isLoading;
  };

  getError = (): Error | undefined => {
    return this.parentManager?.getError() ?? this._error;
  };

  static getElementAtAddress = (
    rootComponent: RouteLitComponent,
    address: number[]
  ): RouteLitComponent => {
    const element = address.reduce(
      (acc, curr) => acc?.children?.[curr] as RouteLitComponent,
      rootComponent
    );
    if (!element) {
      throw new Error("Component not found at address: " + address.join(","));
    }
    return element;
  };

  subscribe = (listener: Handler): (() => void) => {
    const unsubscribeParent = this.parentManager?.subscribe(listener);
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
      unsubscribeParent?.();
    };
  };

  subscribeIsLoading = (listener: IsLoadingHandler): (() => void) => {
    const unsubscribeParent = this.parentManager?.subscribeIsLoading(listener);
    this.isLoadingListeners.add(listener);
    return () => {
      this.isLoadingListeners.delete(listener);
      unsubscribeParent?.();
    };
  };

  subscribeError = (listener: ErrorHandler): (() => void) => {
    const unsubscribeParent = this.parentManager?.subscribeError(listener);
    this.errorListeners.add(listener);
    return () => {
      this.errorListeners.delete(listener);
      unsubscribeParent?.();
    };
  };

  private notifyListeners = () => {
    const rootComponent = this.getRootComponent();
    for (const listener of this.listeners) {
      listener(rootComponent);
    }
  };

  private notifyIsLoading = () => {
    const isLoading = this.isLoading();
    for (const listener of this.isLoadingListeners) {
      listener(isLoading);
    }
  };

  private notifyError = () => {
    const error = this.getError();
    for (const listener of this.errorListeners) {
      listener(error!);
    }
  };
}
