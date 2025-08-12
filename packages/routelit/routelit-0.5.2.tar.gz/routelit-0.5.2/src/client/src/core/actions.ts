function getSingleTarget(
  rootComponent: RouteLitComponent,
  address: number[]
): RouteLitComponent {
  let target = rootComponent;
  for (let i = 0; i < address.length - 1; i++) {
    if (!target.children) {
      target.children = [];
    }
    target = target.children![address[i]];
  }
  return target;
}

export function applyAddAction(
  rootComponent: RouteLitComponent,
  action: AddAction
) {
  const target = getSingleTarget(rootComponent, action.address);
  if (!target.children) {
    target.children = [];
  }
  target.children!.splice(
    action.address.at(-1)!,
    0,
    action.element
  );
}

export function applyRemoveAction(
  rootComponent: RouteLitComponent,
  action: RemoveAction
) {
  const target = getSingleTarget(rootComponent, action.address);
  target.children!.splice(action.address.at(-1)!, 1);
}

export function applySetAction(
  rootComponent: RouteLitComponent,
  action: SetAction
) {
  // Special case: if address is empty, we're setting the root component
  if (action.address.length === 0) {
    Object.assign(rootComponent, action.element);
    if (rootComponent.stale) {
      rootComponent.stale = undefined;
    }
    return;
  }

  const targetParent = getSingleTarget(rootComponent, action.address);
  const targetIndex = action.address.at(-1)!;
  if (!targetParent.children) {
    targetParent.children = [];
  }
  const target = targetParent.children[targetIndex];

  // Immer-compatible: mutate existing object instead of replacing
  if (target && target.key === action.element.key) {
    // Preserve children if keys match
    Object.assign(target, action.element, { children: target.children });
  } else {
    // For new elements, use splice to replace in a way that's Immer-compatible
    targetParent.children.splice(targetIndex, 1, action.element);
  }

  // Remove stale flag from the updated element
  const updatedElement = targetParent.children[targetIndex];
  if (updatedElement?.stale) {
    updatedElement.stale = undefined;
  }
}

export function applyUpdateAction(
  rootComponent: RouteLitComponent,
  action: UpdateAction
) {
  const target = getSingleTarget(rootComponent, action.address);
  const element = target.children![action.address.at(-1)!];
  element.props = action.props;
  if (element.stale) {
    element.stale = undefined;
  }
}

export function applyFreshBoundaryAction(
  rootComponent: RouteLitComponent,
  action: FreshBoundaryAction
) {
  const target = getSingleTarget(rootComponent, action.address);
  const staleStartsAt = action.address[action.address.length - 1] + 1;

  // Helper function to mark leaf nodes as stale in depth-first manner
  const markLeafNodesStale = (components: RouteLitComponent[]): number => {
    let staleCount = 0;
    for (const child of components) {
      if (!child.children || child.children.length === 0) {
        // This is a leaf node (no children), mark it as stale
        child.stale = true;
        staleCount++;
      } else {
        // This has children, traverse deeper
        const childrenStaleCount = markLeafNodesStale(child.children!);
        // If all children are stale, mark the parent as stale
        if (childrenStaleCount === child.children!.length) {
          child.stale = true;
          staleCount++;
        }
      }
    }
    return staleCount;
  };

  // Mark all leaf nodes as stale starting from the specified index
  const componentsToProcess = target.children?.slice(staleStartsAt);
  if (!componentsToProcess) return;
  markLeafNodesStale(componentsToProcess);
}

export function removeStaleComponents(rootComponent: RouteLitComponent) {
  for (let i = rootComponent.children!.length - 1; i >= 0; i--) {
    const component = rootComponent.children![i];
    if (component.stale) {
      rootComponent.children!.splice(i, 1);
    } else if (component.children?.length) {
      removeStaleComponents(component);
    }
  }
}

function handleNoChangeAction(
  rootComponent: RouteLitComponent,
  action: NoChangeAction
) {
  const target = getSingleTarget(rootComponent, action.address);
  const element = target?.children?.[action.address[action.address.length - 1]];
  if (element && element.stale) {
    element.stale = undefined;
  }
}

function prependAddressToActionsArray(
  actionResponses: Action[],
  address: number[]
): Action[] {
  return actionResponses.map((action) => {
    return { ...action, address: address.concat(action.address) };
  });
}

export function prependAddressToActions(
  actionResponse: ActionsResponse,
  address: number[]
): ActionsResponse {
  return {
    ...actionResponse,
    actions: prependAddressToActionsArray(actionResponse.actions, address),
  };
}

export function applyActions(
  rootComponent: RouteLitComponent,
  actions: Action[]
) {
  actions.forEach((action) => {
    switch (action.type) {
      case "add":
        applyAddAction(rootComponent, action);
        break;
      case "remove":
        applyRemoveAction(rootComponent, action);
        break;
      case "set":
        applySetAction(rootComponent, action);
        break;
      case "update":
        applyUpdateAction(rootComponent, action);
        break;
      case "fresh_boundary":
        applyFreshBoundaryAction(rootComponent, action);
        break;
      case "last":
        removeStaleComponents(rootComponent);
        break;
      case "no_change":
        handleNoChangeAction(rootComponent, action);
        break;
    }
  });
}
