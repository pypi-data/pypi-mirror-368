import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { RouteLitManager } from '../../core/manager';
import * as serverApi from '../../core/server-api';
import * as actions from '../../core/actions';
import { TargetMutex } from '../../core/utils/mutex';

// Mock the dependencies
vi.mock('../../core/server-api', () => ({
  sendEvent: vi.fn(),
  sendEventStream: vi.fn()
}));

vi.mock('../../core/actions', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    // @ts-expect-error - we're mocking the function
    ...actual,
    prependAddressToActions: vi.fn((resp: ActionsResponse, address: number[]) => ({
      ...resp,
      actions: resp.actions.map(action => ({
        ...action,
        address: [...address, ...action.address]
      }))
    }))
  };
});

// Helper function to create async generator from array
async function* createAsyncGenerator<T>(items: T[]): AsyncGenerator<T> {
  for (const item of items) {
    yield item;
  }
}

describe('RouteLitManager', () => {
  let manager: RouteLitManager;
  const mockRootComponent: RouteLitComponent = {
    name: 'root',
    key: 'root',
    props: {},
    children: [
      {
        name: 'test',
        props: { id: 'test1' },
        key: 'test1',
      },
      {
        name: 'test2',
        props: { id: 'test2' },
        key: 'test2',
        children: [
          {
            name: 'child',
            props: { id: 'child' },
            key: 'child',
          }
        ]
      }
    ]
  };

  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
    // Ensure mutex lock resolves immediately
    vi.spyOn(TargetMutex.prototype, 'lock').mockResolvedValue(async () => {});
    
    // Save the original window.location and history
    Object.defineProperty(window, 'location', {
      value: {
        href: 'http://localhost',
        origin: 'http://localhost'
      },
      writable: true
    });

    window.history.pushState = vi.fn();
    window.history.replaceState = vi.fn();
    document.dispatchEvent = vi.fn();
    document.addEventListener = vi.fn();
    document.removeEventListener = vi.fn();
    window.addEventListener = vi.fn();
    window.removeEventListener = vi.fn();

    // Mock sendEventStream to return async generator with responses
    vi.mocked(serverApi.sendEventStream).mockImplementation((event) => {
      if (event.detail.type === 'initialize') {
        return createAsyncGenerator([{
          actions: [
            {
              type: 'set',
              address: [],
              element: { ...mockRootComponent }
            } as SetAction
          ],
          target: 'fragment' as const
        }]);
      }
      return createAsyncGenerator([{
        actions: [],
        target: 'fragment' as const
      }]);
    });

    // Initialize a new manager for each test
    manager = new RouteLitManager({});
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  describe('action batching and throttling', () => {
    it('should batch actions with the same target', async () => {
      // Create a simple manager for this test that avoids Immer issues
      const testManager = new RouteLitManager({});
      
      // Spy on the internal method instead of the mocked external one
      const applyActionsSpy = vi.spyOn(testManager, 'applyActions');
      
      // First trigger an action to set the lastExecutionTime
      const setupAction: AddAction = {
        type: 'add',
        address: [0],
        element: { name: 'setup', key: 'setup', props: {} },
        target: 'fragment'
      };
      
      testManager.batchAction(setupAction);
      expect(applyActionsSpy).toHaveBeenCalledTimes(1);
      applyActionsSpy.mockClear();
      
      const action1: AddAction = {
        type: 'add',
        address: [0],
        element: { name: 'div1', key: 'div1', props: {} },
        target: 'fragment'
      };

      const action2: AddAction = {
        type: 'add',
        address: [1],
        element: { name: 'div2', key: 'div2', props: {} },
        target: 'fragment'
      };

      // Clear any existing timers and spy calls
      vi.clearAllTimers();

      // Now the actions should be throttled since lastExecutionTime was recently set
      testManager.batchAction(action1);
      testManager.batchAction(action2);

      // Actions should not be applied immediately due to throttling
      expect(applyActionsSpy).not.toHaveBeenCalled();

      // Fast-forward time to trigger the throttled execution
      await vi.advanceTimersByTimeAsync(125); // Match THROTTLE_DELAY

      // Now the actions should be applied together in a single call
      expect(applyActionsSpy).toHaveBeenCalledTimes(1);
      
      // Cleanup
      applyActionsSpy.mockRestore();
    });

    it('should flush actions when target changes', async () => {
      // Create a simple manager for this test that avoids Immer issues
      const testManager = new RouteLitManager({});
      
      // Spy on the internal method instead of the mocked external one
      const applyActionsSpy = vi.spyOn(testManager, 'applyActions');

      const fragmentAction: AddAction = {
        type: 'add',
        address: [0],
        element: { name: 'div', key: 'div', props: {} },
        target: 'fragment'
      };

      const appAction: AddAction = {
        type: 'add',
        address: [1],
        element: { name: 'div2', key: 'div2', props: {} },
        target: 'app'
      };

      // Clear any existing timers and spy calls
      vi.clearAllTimers();
      applyActionsSpy.mockClear();

      testManager.batchAction(fragmentAction);
      
      // Wait a bit to ensure the first action is queued
      await vi.advanceTimersByTimeAsync(10);
      
      testManager.batchAction(appAction);

      // First action should be flushed immediately when target changes
      expect(applyActionsSpy).toHaveBeenCalledTimes(1);

      // Fast-forward time to trigger the throttled execution of second action
      await vi.advanceTimersByTimeAsync(125); // Match THROTTLE_DELAY

      // Second action should be applied after throttle delay
      expect(applyActionsSpy).toHaveBeenCalledTimes(2);
      
      // Cleanup
      applyActionsSpy.mockRestore();
    });

    it('should flush pending actions on terminate', async () => {
      // Create a simple manager for this test that avoids Immer issues
      const testManager = new RouteLitManager({});
      
      // Spy on the internal method instead of the mocked external one
      const applyActionsSpy = vi.spyOn(testManager, 'applyActions');

      // First trigger an action to set the lastExecutionTime
      const setupAction: AddAction = {
        type: 'add',
        address: [0],
        element: { name: 'setup', key: 'setup', props: {} },
        target: 'fragment'
      };
      
      testManager.batchAction(setupAction);
      expect(applyActionsSpy).toHaveBeenCalledTimes(1);
      applyActionsSpy.mockClear();

      const action: AddAction = {
        type: 'add',
        address: [0],
        element: { name: 'div', key: 'div', props: {} },
        target: 'fragment'
      };

      // Clear any existing timers and spy calls
      vi.clearAllTimers();

      // Now the action should be throttled since lastExecutionTime was recently set
      testManager.batchAction(action);
      
      // Action should not be applied yet
      expect(applyActionsSpy).not.toHaveBeenCalled();

      // Terminate should flush immediately without waiting for timer
      testManager.terminate();

      // Action should be flushed on terminate
      expect(applyActionsSpy).toHaveBeenCalledTimes(1);
      
      // Cleanup
      applyActionsSpy.mockRestore();
    });
  });

  describe('initialization and cleanup', () => {
    it('should register event listeners on initialize', () => {
      manager.initialize();

      expect(document.addEventListener).toHaveBeenCalledWith(
        'routelit:event',
        expect.any(Function)
      );

      expect(window.addEventListener).toHaveBeenCalledWith(
        'popstate',
        expect.any(Function)
      );
    });

    it.skip('should send initialize event and fetch initial data on initialize', async () => {
      // Clear the mock first
      vi.mocked(serverApi.sendEventStream).mockClear();

      // Call initialize
      manager.initialize();
      // Wait for asynchronous event handling
      await Promise.resolve();

      // Verify the sendEventStream was called with initialize event
      // We don't need to wait for completion, just verify it was called
      expect(serverApi.sendEventStream).toHaveBeenCalledWith(
        expect.objectContaining({
          detail: expect.objectContaining({
            type: 'initialize',
            id: 'browser-navigation'
          })
        }),
        undefined
      );
    });

    it.skip('should not initialize DOM twice', async () => {
      // Clear the mock first
      vi.mocked(serverApi.sendEventStream).mockClear();

      // Initialize twice
      manager.initialize();
      manager.initialize();
      // Allow async handling
      await Promise.resolve();

      // Verify sendEventStream was called only once with initialize event
      expect(serverApi.sendEventStream).toHaveBeenCalledTimes(1);
      expect(serverApi.sendEventStream).toHaveBeenCalledWith(
        expect.objectContaining({
          detail: expect.objectContaining({
            type: 'initialize',
            id: 'browser-navigation'
          })
        }),
        undefined
      );
    });

    it('should remove event listeners on terminate', () => {
      manager.terminate();

      expect(document.removeEventListener).toHaveBeenCalledWith(
        'routelit:event',
        expect.any(Function)
      );

      expect(window.removeEventListener).toHaveBeenCalledWith(
        'popstate',
        expect.any(Function)
      );
    });
  });

  describe('event handling', () => {
    it('should handle UI events using streaming by sending them to the server', async () => {
      const eventDetail = {
        id: 'test-id',
        type: 'click',
        someData: 'value'
      };

      const event = new CustomEvent<UIEventPayload>('routelit:event', {
        detail: eventDetail
      });

      await manager.handleEvent(event);

      expect(serverApi.sendEventStream).toHaveBeenCalledWith(event, undefined);
    });

    it('should handle multiple streaming responses', async () => {
      const responses: ActionsResponse[] = [
        { actions: [{ type: 'add', address: [0], element: { name: 'div1', key: 'div1', props: {}, address: [0] } } as AddAction], target: 'fragment' as const },
        { actions: [{ type: 'add', address: [1], element: { name: 'div2', key: 'div2', props: {}, address: [1] } } as AddAction], target: 'fragment' as const }
      ];

      vi.mocked(serverApi.sendEventStream).mockReturnValue(createAsyncGenerator(responses));

      const applyActionsSpy = vi.spyOn(manager, 'applyActions');

      const event = new CustomEvent<UIEventPayload>('routelit:event', {
        detail: { id: 'test', type: 'click' }
      });

      await manager.handleEvent(event);

      expect(applyActionsSpy).toHaveBeenCalledTimes(2);
      expect(applyActionsSpy).toHaveBeenNthCalledWith(1, responses[0]);
      expect(applyActionsSpy).toHaveBeenNthCalledWith(2, responses[1]);
    });

    it('should update loading state during streaming event handling', async () => {
      const loadingListener = vi.fn();
      manager.subscribeIsLoading(loadingListener);

      const event = new CustomEvent<UIEventPayload>('routelit:event', {
        detail: { id: 'test', type: 'click' }
      });

      // Create a promise that we can resolve manually
      let resolvePromise!: (value: ActionsResponse) => void;
      const controlledPromise = new Promise<ActionsResponse>(resolve => {
        resolvePromise = resolve;
      });

      const controlledGenerator = (async function* () {
        const response = await controlledPromise;
        yield response;
      })();

      vi.mocked(serverApi.sendEventStream).mockReturnValue(controlledGenerator);

      // Start handling the event but don't await it yet
      const handlePromise = manager.handleEvent(event);

      // Loading state should be true immediately
      expect(manager.isLoading()).toBe(true);
      expect(loadingListener).toHaveBeenCalledWith(true);

      // Reset the mock to ensure we're testing the right callback
      loadingListener.mockClear();

      // Resolve the promise with a response
      resolvePromise({ actions: [], target: 'fragment' as const });

      // Wait for the event handler to complete
      await handlePromise;

      // Loading should be false after completion
      expect(manager.isLoading()).toBe(false);
      expect(loadingListener).toHaveBeenCalledWith(false);
    });

    it('should handle errors during streaming event processing', async () => {
      const errorListener = vi.fn();
      manager.subscribeError(errorListener);

      const event = new CustomEvent<UIEventPayload>('routelit:event', {
        detail: { id: 'test', type: 'click' }
      });

      const testError = new Error('Test streaming error');
      vi.mocked(serverApi.sendEventStream).mockImplementation(async function* (): AsyncGenerator<ActionsResponse> {
        throw testError;
        yield { actions: [], target: 'fragment' as const }; // This line will never be reached, but TypeScript requires it
      });

      await manager.handleEvent(event);

      expect(manager.getError()).toBe(testError);
      expect(errorListener).toHaveBeenCalledWith(testError);
    });

    it('should handle errors during applyActions', () => {
      const errorListener = vi.fn();
      manager.subscribeError(errorListener);

      // Spy on applyActions and make it throw an error for this test
      const testError = new Error('Invalid component tree mutation');
      const applyActionsSpy = vi.spyOn(actions, 'applyActions').mockImplementation(() => {
        throw testError;
      });

      const action: AddAction = {
        type: 'add',
        address: [0],
        element: { name: 'test', key: 'test', props: {} }
      };

      manager.applyActions({
        actions: [action],
        target: 'fragment'
      });

      expect(manager.getError()).toBe(testError);
      expect(errorListener).toHaveBeenCalledWith(testError);
      
      // Restore the original implementation
      applyActionsSpy.mockRestore();
    });

    it('should handle navigation events with streaming', async () => {
      const event = new CustomEvent<NavigateEventPayload>('routelit:event', {
        detail: {
          id: 'nav-1',
          type: 'navigate',
          href: '/new-page'
        }
      });

      const response: ActionsResponse = {
        actions: [{ type: 'add', address: [0], element: { name: 'new', key: 'new', props: {}, address: [0] } } as AddAction],
        target: 'fragment' as const
      };

      vi.mocked(serverApi.sendEventStream).mockReturnValue(createAsyncGenerator([response]));

      await manager.handleEvent(event);

      expect(serverApi.sendEventStream).toHaveBeenCalledWith(event, undefined);
    });

    it('should not handle navigation events when in a fragment', async () => {
      const fragmentManager = new RouteLitManager({
        fragmentId: 'test-fragment'
      });

      const event = new CustomEvent<NavigateEventPayload>('routelit:event', {
        detail: {
          id: 'nav-1',
          type: 'navigate',
          href: '/new-page'
        }
      });

      await fragmentManager.handleEvent(event);

      expect(serverApi.sendEventStream).not.toHaveBeenCalled();
    });

    it('should handle popstate events', () => {
      // Set up window location
      window.location.href = 'http://localhost/page2';

      // Trigger popstate handler
      manager.handlePopState();

      // Check if a navigate event was dispatched
      expect(document.dispatchEvent).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'routelit:event',
          detail: expect.objectContaining({
            type: 'navigate',
            id: 'browser-navigation',
            href: 'http://localhost/page2'
          })
        })
      );
    });

    it.skip('should abort previous requests when new event is handled', () => {
      /* Test skipped: AbortController handling removed from implementation */
    });

    it('should handle individual action responses', async () => {
      const action: AddAction = {
        type: 'add',
        address: [0],
        element: { name: 'div', key: 'test', props: {}, address: [0] }
      };

      vi.mocked(serverApi.sendEventStream).mockReturnValue(createAsyncGenerator([action]));

      const applyActionsSpy = vi.spyOn(manager, 'applyActions');

      const event = new CustomEvent<UIEventPayload>('routelit:event', {
        detail: { id: 'test', type: 'click' }
      });

      await manager.handleEvent(event);

      expect(applyActionsSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          actions: [action],
          target: 'fragment'
        }),
        true
      );
    });

    it('should handle fragment ID in event handling', async () => {
      const rootManager = new RouteLitManager({});
      const fragmentManager = new RouteLitManager({
        fragmentId: 'test-fragment',
        parentManager: rootManager
      });

      const event = new CustomEvent<UIEventPayload>('routelit:event', {
        detail: { id: 'test', type: 'click' }
      });

      await fragmentManager.handleEvent(event);

      expect(serverApi.sendEventStream).toHaveBeenCalledWith(
        event,
        'test-fragment'
      );
    });
  });

  describe('component tree handling', () => {
    let parentManager: RouteLitManager;
    let childManager: RouteLitManager;
    let grandchildManager: RouteLitManager;

    beforeEach(() => {
      parentManager = new RouteLitManager({ rootComponent: mockRootComponent });
      // Initialize parent manager to ensure component tree is set up
      parentManager.initialize();
      
      childManager = new RouteLitManager({
        fragmentId: 'child',
        parentManager,
        address: [1]
      });

      grandchildManager = new RouteLitManager({
        fragmentId: 'grandchild',
        parentManager: childManager,
        address: [0]
      });
    });

    it('should get root component from parent', () => {
      const root = childManager.getRootComponent();
      expect(root).toBeDefined();
      expect(root.name).toBe('test2');
      expect(root.key).toBe('test2');
    });

    it('should get element at address through parent', () => {
      const element = RouteLitManager.getElementAtAddress(childManager.getRootComponent(), [0]);
      expect(element).toBeDefined();
      expect(element.key).toBe('child');
    });

    it('should throw error for invalid address', () => {
      expect(() => RouteLitManager.getElementAtAddress(childManager.getRootComponent(), [99])).toThrow('Component not found');
    });

    it('should handle nested fragment addresses correctly', () => {
      // Test that grandchild manager correctly builds its complete address path
      const action: AddAction = {
        type: 'add',
        address: [0],
        element: { name: 'test', key: 'test', props: {} }
      };

      const actionsResponse: ActionsResponse = {
        actions: [action],
        target: 'fragment'
      };

      grandchildManager.applyActions(actionsResponse);

      // The address should be [1] - parent's address only since child's address is relative
      expect(actions.prependAddressToActions).toHaveBeenCalledWith(
        actionsResponse,
        [1]
      );
    });

    it('should slice address when parent is also a fragment', () => {
      // Create a nested component tree
      const nestedComponent: RouteLitComponent = {
        name: 'root',
        key: 'root',
        props: {},
        children: [
          {
            name: 'level1',
            key: 'level1',
            props: {},
            children: [
              {
                name: 'level2',
                key: 'level2',
                props: {},
                children: [
                  {
                    name: 'level3',
                    key: 'level3',
                    props: {},
                    children: [
                      {
                        name: 'target',
                        key: 'target',
                        props: {}
                      }
                    ]
                  }
                ]
              }
            ]
          }
        ]
      };

      // Create a root manager with the nested component tree
      const rootManager = new RouteLitManager({ rootComponent: nestedComponent });
      rootManager.initialize();

      // Create a fragment manager with a fragment parent
      const fragmentParent = new RouteLitManager({
        fragmentId: 'parent-fragment',
        parentManager: rootManager,
        address: [0, 0, 0] // Points to level3
      });

      const fragmentChild = new RouteLitManager({
        fragmentId: 'child-fragment',
        parentManager: fragmentParent,
        address: [0] // Points to target relative to parent
      });

      const action: AddAction = {
        type: 'add',
        address: [0],
        element: { name: 'test', key: 'test', props: {} }
      };

      const actionsResponse: ActionsResponse = {
        actions: [action],
        target: 'fragment'
      };

      fragmentChild.applyActions(actionsResponse);

      // Should slice the first element of the child's address since parent is a fragment
      expect(actions.prependAddressToActions).toHaveBeenCalledWith(
        actionsResponse,
        [0, 0, 0]  // parent address only since child address is relative
      );
    });

    afterEach(() => {
      parentManager.terminate();
    });
  });

  describe('parent-child fragment relationship', () => {
    let parentManager: RouteLitManager;
    let childManager: RouteLitManager;

    beforeEach(() => {
      parentManager = new RouteLitManager({ rootComponent: mockRootComponent });
      childManager = new RouteLitManager({
        fragmentId: 'child',
        parentManager,
        address: [1]
      });
    });

    it('should delegate actions to parent manager', () => {
      const action: AddAction = {
        type: 'add',
        address: [0],
        element: { name: 'div', key: 'test', props: {} }
      };

      const actionsResponse: ActionsResponse = {
        actions: [action],
        target: 'fragment'
      };

      childManager.applyActions(actionsResponse);

      expect(actions.prependAddressToActions).toHaveBeenCalledWith(
        actionsResponse,
        [1]
      );
    });

    it('should propagate loading state from parent to child', () => {
      parentManager['_isLoading'] = true;
      expect(childManager.isLoading()).toBe(true);
    });

    it('should propagate errors from parent to child', () => {
      const error = new Error('Test error');
      parentManager['_error'] = error;
      expect(childManager.getError()).toBe(error);
    });

    it('should handle app-level actions in fragments', () => {
      const appAction: AddAction = {
        type: 'add',
        address: [0],
        element: { name: 'div', key: 'test', props: {} },
        target: 'app'
      };

      childManager.batchAction(appAction);

      // Should be delegated to parent without address prepending
      expect(actions.prependAddressToActions).not.toHaveBeenCalled();
    });
  });

  describe('subscription management', () => {
    it('should allow subscribing and unsubscribing to component tree changes', () => {
      // Create a manager with a root component
      const testManager = new RouteLitManager({ rootComponent: mockRootComponent });
      testManager.initialize();

      const listener = vi.fn();
      const unsubscribe = testManager.subscribe(listener);

      // Apply actions to trigger notification
      const setAction: SetAction = {
        type: 'set',
        address: [],
        element: { ...mockRootComponent, name: 'updated' }
      };

      // First test with actual action
      testManager.applyActions({
        actions: [setAction],
        target: 'fragment'
      });

      expect(listener).toHaveBeenCalledTimes(1);
      expect(listener).toHaveBeenLastCalledWith({ ...mockRootComponent, name: 'updated' });

      // Unsubscribe and verify no more calls
      unsubscribe();

      const setAction2: SetAction = {
        type: 'set',
        address: [],
        element: { ...mockRootComponent, name: 'updated2' }
      };

      testManager.applyActions({
        actions: [setAction2],
        target: 'fragment'
      });

      expect(listener).toHaveBeenCalledTimes(1); // No more calls after unsubscribe
    });

    it('should allow subscribing to loading state changes', () => {
      const listener = vi.fn();

      manager.subscribeIsLoading(listener);

      // Create a never-resolving generator to keep loading state true
      vi.mocked(serverApi.sendEventStream).mockReturnValue((async function* () {
        // This generator never resolves, keeping loading state true
        await new Promise(() => {});
        yield { actions: [], target: 'fragment' as const };
      })());

      // Trigger loading state change
      manager.handleEvent(new CustomEvent<UIEventPayload>('routelit:event', {
        detail: { id: 'test', type: 'click' }
      }));

      expect(listener).toHaveBeenCalledWith(true);
    });

    it('should allow subscribing to error state changes', async () => {
      const listener = vi.fn();

      manager.subscribeError(listener);

      // Make the API call fail
      const error = new Error('Test error');
      vi.mocked(serverApi.sendEventStream).mockImplementation(async function* (): AsyncGenerator<ActionsResponse> {
        throw error;
        yield { actions: [], target: 'fragment' as const }; // This line will never be reached, but TypeScript requires it
      });

      // Trigger error - now that handleEvent is async, we can await it
      await manager.handleEvent(new CustomEvent<UIEventPayload>('routelit:event', {
        detail: { id: 'test', type: 'click' }
      }));

      expect(listener).toHaveBeenCalledWith(error);
    });

    it('should propagate subscriptions from parent to child', () => {
      // Create parent manager with root component that has children
      const mockParentComponent: RouteLitComponent = {
        key: 'parent',
        name: 'parent',
        props: {},
        children: [
          {
            key: 'child1',
            name: 'child1',
            props: {},
            children: []
          },
          {
            key: 'child2',
            name: 'child2',
            props: {},
            children: []
          }
        ]
      };

      // Create parent manager with root component
      const parentManager = new RouteLitManager({ rootComponent: mockParentComponent });
      parentManager.initialize();

      // Create child manager pointing to child2 component
      const childManager = new RouteLitManager({
        fragmentId: 'child',
        parentManager,
        address: [1] // Points to child2 component
      });

      const listener = vi.fn();
      childManager.subscribe(listener);

      // Apply action to child manager itself (empty address targets the fragment root)
      const setAction: SetAction = {
        type: 'set',
        address: [], // Target the child component itself
        element: { 
          key: 'child2',
          name: 'updated-child2',
          props: {},
          children: []
        }
      };

      // Apply action to child manager
      childManager.applyActions({
        actions: [setAction],
        target: 'fragment'
      });

      // Child listener should be called
      expect(listener).toHaveBeenCalledTimes(1);
      expect(listener).toHaveBeenLastCalledWith({
        key: 'child2',
        name: 'updated-child2',
        props: {},
        children: []
      });
    });
  });

  describe('URL tracking', () => {
    it('should track last URL correctly', () => {
      const manager = new RouteLitManager({});
      
      // Initial URL should be from window.location
      expect(manager.getLastURL()).toBe('http://localhost');

      // Update URL through navigation event
      const event = new CustomEvent<NavigateEventPayload>('routelit:event', {
        detail: {
          id: 'nav-1',
          type: 'navigate',
          href: '/new-page'
        }
      });

      manager.handleEvent(event);

      // URL should be updated
      expect(manager.getLastURL()).toBe('http://localhost/new-page');
    });

    it('should handle external URLs', () => {
      const manager = new RouteLitManager({});
      
      const event = new CustomEvent<NavigateEventPayload>('routelit:event', {
        detail: {
          id: 'nav-1',
          type: 'navigate',
          href: 'https://external.com/page'
        }
      });

      manager.handleEvent(event);

      // External URL should be preserved as-is
      expect(manager.getLastURL()).toBe('https://external.com/page');
    });

    it('should inherit last URL from parent manager', () => {
      const parentManager = new RouteLitManager({});
      parentManager.handleEvent(new CustomEvent<NavigateEventPayload>('routelit:event', {
        detail: {
          id: 'nav-1',
          type: 'navigate',
          href: '/parent-page'
        }
      }));

      const childManager = new RouteLitManager({
        fragmentId: 'child',
        parentManager
      });

      // Child should inherit parent's last URL
      expect(childManager.getLastURL()).toBe('http://localhost/parent-page');
    });
  });
});
