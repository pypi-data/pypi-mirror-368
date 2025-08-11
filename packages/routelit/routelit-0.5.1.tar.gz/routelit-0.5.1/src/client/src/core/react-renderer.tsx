import { Suspense, useMemo, useSyncExternalStore } from "react";
import { type RouteLitManager } from "./manager";
import { type ComponentStore } from "./component-store";
import Fragment from "../components/fragment";

interface Props {
  manager: RouteLitManager;
  componentStore: ComponentStore;
}

interface RLElementProps {
  name: string;
  id: string;
  address: number[] | undefined;
  props: Record<string, unknown>;
  children: RouteLitComponent[] | undefined;
  componentStore: ComponentStore;
}

function RLElement({
  name,
  address,
  id: key,
  props,
  children,
  componentStore,
}: RLElementProps) {
  const { children: childrenProp, ...restProps } = props;
  if (name === "fragment") {
    return (
      <Fragment
        key={key as string}
        id={restProps.id as string}
        address={address}
      />
    );
  }

  const Component = componentStore.get(name);
  if (!Component) return null;

  return (
    <Suspense
      fallback={
        <div className="rl-stale">
          <span>Loading...</span>
        </div>
      }
    >
      <Component id={key} {...restProps}>
        {childrenProp ?? children?.map(renderComponentTree(componentStore))}
      </Component>
    </Suspense>
  );
}

export function FinalComponent({
  c,
  componentStore,
}: {
  c: RouteLitComponent;
  componentStore: ComponentStore;
}): React.ReactNode {
  const element = useMemo(
    () =>
      <RLElement name={c.name} id={c.key} address={c.address} props={c.props} children={c.children} componentStore={componentStore} />,
    [c.name, c.key, c.address, c.props, c.children, componentStore]
  );
  if (c.virtual) {
    return element;
  }
  const className = c.stale ? "rl-component rl-stale" : "rl-component";
  return <div className={className}>{element}</div>;
}

const renderComponentTree =
  (componentStore: ComponentStore) =>
  (c: RouteLitComponent, i: number): React.ReactNode => {
    return <FinalComponent key={c.key + i} c={c} componentStore={componentStore} />;
  };

function ReactRenderer({ manager, componentStore }: Props) {
  const rootComponent = useSyncExternalStore(
    manager.subscribe,
    manager.getRootComponent
  );
  useSyncExternalStore(componentStore.subscribe, componentStore.getVersion);
  return (
    <>{rootComponent.children?.map(renderComponentTree(componentStore))}</>
  );
}

export default ReactRenderer;
