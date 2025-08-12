import React from "react";
import * as ReactDOM from "react-dom";
import * as jsxRuntime from "react/jsx-runtime";

import initManager from "./core/initializer";
import { ComponentStore } from "./core/component-store";
import Fragment from "./components/fragment";
import Link from "./components/link";
import Form from "./components/form";
import Head from "./components/head";
import {
  useDispatcherWith,
  useDispatcherWithAttr,
  useFormDispatcherWithAttr,
  useFormDispatcher,
  useIsLoading,
  useError,
} from "./core/context";
import { RouteLitManager } from "./core/manager";
import { renderApp } from "./app-factory";
import {
  withEventDispatcher,
  withValueEventDispatcher,
  withSimpleComponent,
  withInputValueEventDispatcher,
  withCallbackAttributes,
} from "./core/hoc";
import { useLinkClickHandler, useRLInlineElement, useRLCallbackAttributes } from "./core/hooks";

// Define the type for our client interface
export interface RoutelitClientType {
  manager: RouteLitManager;
  componentStore: ComponentStore;
  useDispatcherWith: typeof useDispatcherWith;
  useDispatcherWithAttr: typeof useDispatcherWithAttr;
  useFormDispatcherWithAttr: typeof useFormDispatcherWithAttr;
  useFormDispatcher: typeof useFormDispatcher;
  useIsLoading: typeof useIsLoading;
  useError: typeof useError;
  renderApp: (rootId?: string) => void;
  withEventDispatcher: typeof withEventDispatcher;
  withValueEventDispatcher: typeof withValueEventDispatcher;
  withSimpleComponent: typeof withSimpleComponent;
  withInputValueEventDispatcher: typeof withInputValueEventDispatcher;
  useLinkClickHandler: typeof useLinkClickHandler;
  useRLInlineElement: typeof useRLInlineElement;
  useRLCallbackAttributes: typeof useRLCallbackAttributes;
  withCallbackAttributes: typeof withCallbackAttributes;
}

// Check if we already have an instance in the window object
// This ensures we only ever have a single instance of these objects
let manager: RouteLitManager;
let componentStore: ComponentStore;

// Add this to the window type
declare global {
  interface Window {
    React: typeof React;
    ReactDOM: typeof ReactDOM;
    jsxRuntime: {
      jsx: typeof React.createElement;
      jsxs: typeof React.createElement;
      Fragment: typeof React.Fragment;
    };
    RoutelitClient?: RoutelitClientType;
    componentStore?: ComponentStore;
  }
}

// Only create new instances if they don't already exist in the window
if (window.RoutelitClient) {
  manager = window.RoutelitClient.manager;
  componentStore = window.RoutelitClient.componentStore;
} else {
  manager = initManager();
  componentStore = new ComponentStore();
}

const Dialog = React.lazy(() => import("./components/dialog"));
const Container = React.lazy(() => import("./components/container"));
const Expander = React.lazy(() => import("./components/expander"));
const Flex = React.lazy(() => import("./components/flex"));
const Input = React.lazy(() => import("./components/input"));
const Radio = React.lazy(() => import("./components/radio"));
const Select = React.lazy(() => import("./components/select"));
const Textarea = React.lazy(() => import("./components/textarea"));
const Checkbox = React.lazy(() => import("./components/checkbox"));
const CheckboxGroup = React.lazy(() => import("./components/checkbox-group"));
const Markdown = React.lazy(() => import("./components/markdown"));


// Register components
componentStore.register("root", withSimpleComponent("div", { className: "rl-container" }));
componentStore.register("fragment", Fragment);
componentStore.register("link", Link);
componentStore.register("dialog", Dialog);
componentStore.register("form", Form);
componentStore.register("head", Head);
componentStore.register("container", Container);
componentStore.register("markdown", Markdown);
componentStore.register("image", withSimpleComponent("img"));
componentStore.register("hr", withSimpleComponent("hr"));
componentStore.register(
  "button",
  withEventDispatcher("button", { type: "button" })
);
componentStore.register("expander", Expander);
componentStore.register("title", withSimpleComponent("h1"));
componentStore.register("header", withSimpleComponent("h2"));
componentStore.register("subheader", withSimpleComponent("h3"));
componentStore.register("flex", Flex);
componentStore.register("text-input", Input);
componentStore.register(
  "single-text-input",
  withInputValueEventDispatcher("input")
);
componentStore.register("radio", Radio);
componentStore.register("select", Select);
componentStore.register("textarea", Textarea);
componentStore.register(
  "single-textarea",
  withInputValueEventDispatcher("textarea")
);
componentStore.register("checkbox", Checkbox);
componentStore.register(
  "single-checkbox",
  withValueEventDispatcher("input", {
    type: "checkbox",
    rlValueAttr: "checked",
    rlEventValueGetter: (e: React.ChangeEvent<HTMLInputElement>) =>
      e.currentTarget.checked,
  })
);
componentStore.register("checkbox-group", CheckboxGroup);
componentStore.forceUpdate();

export {
  useDispatcherWith,
  manager,
  componentStore,
  useDispatcherWithAttr,
  useIsLoading,
  useError,
  useFormDispatcherWithAttr,
  useFormDispatcher,
  renderApp,
  withEventDispatcher,
  withValueEventDispatcher,
  withSimpleComponent,
  withInputValueEventDispatcher,
  useLinkClickHandler,
  useRLInlineElement,
  useRLCallbackAttributes,
  withCallbackAttributes,
};

const RoutelitClient: RoutelitClientType = {
  manager,
  componentStore,
  useDispatcherWith,
  useDispatcherWithAttr,
  useIsLoading,
  useError,
  useFormDispatcherWithAttr,
  useFormDispatcher,
  renderApp,
  withEventDispatcher,
  withValueEventDispatcher,
  withSimpleComponent,
  withInputValueEventDispatcher,
  useLinkClickHandler,
  useRLInlineElement,
  useRLCallbackAttributes,
  withCallbackAttributes,
};

// Expose them globally
window.React = React;
window.ReactDOM = ReactDOM;
window.jsxRuntime = {
  jsx: React.createElement,
  jsxs: React.createElement,
  Fragment: React.Fragment,
};
window.RoutelitClient = RoutelitClient;

export { React, ReactDOM, jsxRuntime, RoutelitClient };
