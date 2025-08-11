# Routelit React client

![Routelit](https://wsrv.nl/?url=res.cloudinary.com/rolangom/image/upload/v1747976918/routelit/routelit_c2otsv.png&w=300&h=300)

This is the react client for the Routelit. It is not supposed to be used alone, but rather as part of the python Routelit library. And just if you want to build custom components.

Routelit is an agnostic library for building data and web applications in python over http.

This library contains core and basic components.

## Core components

- container
- dialog
- form
- fragment
- image
- link
- markdown
- headings
- checkbox (with label)
- single-checkbox
- checkbox_group
- radio (group)
- select
- textarea (with label)
- single-textarea
- text_input (with label)
- single-text-input
- button
- expander
- heading
- title
- header
- subheader

### Public API (exports from `src/lib.ts`)

- This section documents everything you can import from `src/lib.ts` (and what is exposed on `window`).

#### Globals

- **`React`**: Re-exported and also attached to `window.React` for non-bundled environments.
- **`ReactDOM`**: Re-exported and also attached to `window.ReactDOM`.
- **`jsxRuntime`**: Re-exported and attached to `window.jsxRuntime` with `jsx`, `jsxs`, and `Fragment` for JSX runtime needs.
- **`RoutelitClient`**: Singleton attached to `window.RoutelitClient` that aggregates the most common API surface.
  - Example:
    ```ts
    const { manager, componentStore, renderApp } = window.RoutelitClient!;
    renderApp("root");
    ```

#### Singletons

- **`manager`** (`RouteLitManager`): Central event/state manager. Handles `routelit:event` dispatch, navigation, throttled action batching, and subscriptions to loading and error state.
- **`componentStore`** (`ComponentStore`): Registry used by the renderer and components. Pre-registered with the core components listed above; you can extend it with `componentStore.register(name, Component)` and then use that `name` from the server.

#### Rendering

- **`renderApp(rootId?: string)`**: Mounts the app (default element id is `root`).

#### Hooks (context-aware)

- **`useDispatcherWith(id, type)`**: Returns a `(data: Record<string, unknown>) => void` that dispatches a custom Routelit event `{ id, type, ...data }`.
- **`useDispatcherWithAttr(id, type, attr)`**: Returns a `(value: unknown) => void` that dispatches `{ id, type, [attr]: value }`.
- **`useFormDispatcher(id, type)`**: Like `useDispatcherWith`, but includes the current `formId` in the payload. Useful inside form controls.
- **`useFormDispatcherWithAttr(id, type, attr)`**: Like `useDispatcherWithAttr`, but includes `formId`.
- **`useIsLoading()`**: Returns a boolean reflecting combined loading state (fragment or app-level).
- **`useError()`**: Returns the last `Error` (if any) bubbled from the manager chain.

#### Hooks (UI utilities)

- **`useLinkClickHandler({ id, href, replace, isExternal })`**: Returns an anchor `onClick` handler that dispatches a `navigate` event. Prevents default for internal links; lets external links proceed.
- **`useRLInlineElement(props, elementKeys)`**: Converts inline element descriptors on `props` to rendered elements using the `ComponentStore` (e.g., slots like `leftIcon`, `rightIcon`).
- **`useRLCallbackAttributes(props, rlCallbackAttrs)`**: Converts string function bodies found on `props` at the listed attribute names into real callbacks and returns them. Note: only use with trusted input.

#### Higher-order components (HOCs)

- **`withSimpleComponent(Component, props?)`**: Wraps any element/component, merging optional `props` and mapping any `rlInlineElementsAttrs` into real inline elements.
  - Example:
    ```ts
    const Title = withSimpleComponent("h1", { className: "title" });
    ```
- **`withEventDispatcher(Component, options?)`**: Attaches an event handler that dispatches a Routelit event (defaults: `rlEventName="click"`, `rlEventAttr="onClick"`). Works well for buttons.
  - Example:
    ```ts
    const Button = withEventDispatcher("button", { type: "button" });
    // <Button id="save">Save</Button>
    ```
- **`withValueEventDispatcher(Component, options?)`**: Attaches a value-change handler that dispatches `{ [rlValueAttr]: value }` (defaults: `change`/`onChange`/`value`).
  - Examples:
    ```ts
    const TextInput = withValueEventDispatcher("input", { type: "text" });
    const Checkbox = withValueEventDispatcher("input", {
      type: "checkbox",
      rlValueAttr: "checked",
      rlEventValueGetter: (e) => e.currentTarget.checked,
    });
    ```
- **`withInputValueEventDispatcher(Component, options?)`**: For text inputs/textareas; dispatches a `change` with `value` on `onBlur` or when pressing Enter. Defaults wire up `onBlur`/`onKeyDown` and read from `defaultValue`.
  - Example:
    ```ts
    const TextArea = withInputValueEventDispatcher("textarea");
    ```
- **`withCallbackAttributes(Component, { rlCallbackAttrs? })`**: Converts string callbacks on the listed attribute names into real functions and forwards them to the wrapped component.

