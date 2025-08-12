/// <reference path="../../types.d.ts" />
import {
  applyAddAction,
  applyRemoveAction,
  applyUpdateAction,
  applyActions,
  prependAddressToActions,
  applyFreshBoundaryAction,
  removeStaleComponents
} from '../../core/actions';

describe('Actions', () => {
  describe('applyAddAction', () => {
    it('should add a component at the specified address', () => {
      const rootComponent: RouteLitComponent = {
        name: 'root',
        key: 'root',
        props: {},
        children: [
          {
            name: 'parent',
            key: 'parent',
            props: {},
            children: [
              {
                name: 'child1',
                key: 'child1',
                props: {},
              }
            ]
          }
        ]
      };

      const newComponent: RouteLitComponent = {
        name: 'newChild',
        key: 'newChild',
        props: { id: 'new' },
      };

      const addAction: AddAction = {
        type: 'add',
        address: [0, 1],
        element: newComponent
      };

      applyAddAction(rootComponent, addAction);

      // Check that the new component was added at the right position
      expect(rootComponent.children![0].children?.length).toBe(2);
      expect(rootComponent.children![0].children?.[1]).toEqual(newComponent);
    });

    it('should initialize children array if it does not exist', () => {
      const rootComponent: RouteLitComponent = {
        name: 'root',
        key: 'root',
        props: {},
        children: [
          {
            name: 'parent',
            key: 'parent',
            props: {}
            // No children array initially
          }
        ]
      };

      const newComponent: RouteLitComponent = {
        name: 'firstChild',
        key: 'firstChild',
        props: { id: 'new' },
      };

      const addAction: AddAction = {
        type: 'add',
        address: [0, 0],
        element: newComponent
      };

      applyAddAction(rootComponent, addAction);

      // Check that children array was initialized and component was added
      expect(rootComponent.children![0].children).toBeDefined();
      expect(rootComponent.children![0].children?.length).toBe(1);
      expect(rootComponent.children![0].children?.[0]).toEqual(newComponent);
    });
  });

  describe('applyRemoveAction', () => {
    it('should remove a component at the specified address', () => {
      const rootComponent: RouteLitComponent = {
        name: 'root',
        key: 'root',
        props: {},
        children: [
          {
            name: 'parent',
            key: 'parent',
            props: {},
            children: [
              {
                name: 'child1',
                key: 'child1',
                props: {},
              },
              {
                name: 'child2',
                key: 'child2',
                props: {},
              }
            ]
          }
        ]
      };

      const removeAction: RemoveAction = {
        type: 'remove',
        address: [0, 0]
      };

      applyRemoveAction(rootComponent, removeAction);

      // Check that the component was removed
      expect(rootComponent.children![0].children?.length).toBe(1);
      expect(rootComponent.children![0].children?.[0].key).toBe('child2');
    });
  });

  describe('applyUpdateAction', () => {
    it('should update props of a component at the specified address', () => {
      const rootComponent: RouteLitComponent = {
        name: 'root',
        key: 'root',
        props: {},
        children: [
          {
            name: 'child',
            key: 'child',
            props: { id: 'old' },
          }
        ]
      };

      const updateAction: UpdateAction = {
        type: 'update',
        address: [0],
        props: { id: 'updated', newProp: 'value' }
      };

      applyUpdateAction(rootComponent, updateAction);

      // Check that the props were updated
      expect(rootComponent.children![0].props).toEqual({ id: 'updated', newProp: 'value' });
    });

    it('should clear stale flag when updating props', () => {
      const rootComponent: RouteLitComponent = {
        name: 'root',
        key: 'root',
        props: {},
        children: [
          {
            name: 'child',
            key: 'child',
            props: { id: 'old' },
            stale: true
          }
        ]
      };

      const updateAction: UpdateAction = {
        type: 'update',
        address: [0],
        props: { id: 'updated' }
      };

      applyUpdateAction(rootComponent, updateAction);

      expect(rootComponent.children![0].stale).toBeUndefined();
    });
  });

  describe('applyFreshBoundaryAction', () => {
    it('should mark leaf nodes as stale after the boundary', () => {
      const rootComponent: RouteLitComponent = {
        name: 'root',
        key: 'root',
        props: {},
        children: [
          {
            name: 'parent',
            key: 'parent',
            props: {},
            children: [
              {
                name: 'child1',
                key: 'child1',
                props: {},
              },
              {
                name: 'child2',
                key: 'child2',
                props: {},
                children: []
              }
            ]
          }
        ]
      };

      const freshBoundaryAction: FreshBoundaryAction = {
        type: 'fresh_boundary',
        address: [0, 0]
      };

      applyFreshBoundaryAction(rootComponent, freshBoundaryAction);

      // Check that nodes after the boundary are marked as stale
      expect(rootComponent.children![0].children![1].stale).toBe(true);
    });

    it('should mark parent as stale if all children are stale', () => {
      const rootComponent: RouteLitComponent = {
        name: 'root',
        key: 'root',
        props: {},
        children: [
          {
            name: 'parent',
            key: 'parent',
            props: {},
            children: [
              {
                name: 'container',
                key: 'container',
                props: {},
                children: [
                  {
                    name: 'child1',
                    key: 'child1',
                    props: {},
                  },
                  {
                    name: 'child2',
                    key: 'child2',
                    props: {},
                  }
                ]
              }
            ]
          }
        ]
      };

      const freshBoundaryAction: FreshBoundaryAction = {
        type: 'fresh_boundary',
        address: [0, -1]
      };

      applyFreshBoundaryAction(rootComponent, freshBoundaryAction);

      // Check that container is marked stale since all its children are stale
      expect(rootComponent.children![0].children![0].stale).toBe(true);
      expect(rootComponent.children![0].children![0].children![0].stale).toBe(true);
      expect(rootComponent.children![0].children![0].children![1].stale).toBe(true);
    });
  });

  describe('removeStaleComponents', () => {
    it('should remove all stale components', () => {
      const rootComponent: RouteLitComponent = {
        name: 'root',
        key: 'root',
        props: {},
        children: [
          {
            name: 'fresh',
            key: 'fresh',
            props: {},
          },
          {
            name: 'stale',
            key: 'stale',
            props: {},
            stale: true
          },
          {
            name: 'parent',
            key: 'parent',
            props: {},
            children: [
              {
                name: 'staleChild',
                key: 'staleChild',
                props: {},
                stale: true
              }
            ]
          }
        ]
      };

      removeStaleComponents(rootComponent);

      // Check that stale components were removed
      expect(rootComponent.children?.length).toBe(2);
      expect(rootComponent.children![0].key).toBe('fresh');
      expect(rootComponent.children![1].children?.length).toBe(0);
    });
  });

  describe('applyActions', () => {
    it('should apply multiple actions in sequence', () => {
      const rootComponent: RouteLitComponent = {
        name: 'root',
        key: 'root',
        props: {},
        children: [
          {
            name: 'initial',
            key: 'initial',
            props: { id: 'initial' },
          }
        ]
      };

      const addAction: AddAction = {
        type: 'add',
        address: [1],
        element: {
          name: 'new',
          key: 'new',
          props: { id: 'new' },
        }
      };

      const updateAction: UpdateAction = {
        type: 'update',
        address: [0],
        props: { id: 'updated' }
      };

      const actions: Action[] = [addAction, updateAction];

      applyActions(rootComponent, actions);

      // Check that both actions were applied
      expect(rootComponent.children?.length).toBe(2);
      expect(rootComponent.children![0].props.id).toBe('updated');
      expect(rootComponent.children![1].key).toBe('new');
    });

    it('should handle no_change action by clearing stale flag', () => {
      const rootComponent: RouteLitComponent = {
        name: 'root',
        key: 'root',
        props: {},
        children: [
          {
            name: 'child',
            key: 'child',
            props: {},
            stale: true
          }
        ]
      };

      const noChangeAction: NoChangeAction = {
        type: 'no_change',
        address: [0]
      };

      applyActions(rootComponent, [noChangeAction]);

      expect(rootComponent.children![0].stale).toBeUndefined();
    });
  });

  describe('prependAddressToActions', () => {
    it('should prepend the given address to all action addresses', () => {
      const addAction: AddAction = {
        type: 'add',
        address: [0],
        element: { name: 'div', key: 'test', props: {} }
      };

      const updateAction: UpdateAction = {
        type: 'update',
        address: [1],
        props: { id: 'updated' }
      };

      const actionsResponse: ActionsResponse = {
        actions: [addAction, updateAction],
        target: 'fragment'
      };

      const address = [2, 3];

      const result = prependAddressToActions(actionsResponse, address);

      // Check that addresses were properly prepended
      expect(result.actions[0].address).toEqual([2, 3, 0]);
      expect(result.actions[1].address).toEqual([2, 3, 1]);

      // Check that the original response was not modified
      expect(actionsResponse.actions[0].address).toEqual([0]);
      expect(actionsResponse.actions[1].address).toEqual([1]);
    });
  });
});
