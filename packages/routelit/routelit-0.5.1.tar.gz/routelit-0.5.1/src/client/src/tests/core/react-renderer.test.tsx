import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach, type Mock } from 'vitest';
import ReactRenderer from '../../core/react-renderer';
import { type RouteLitManager } from '../../core/manager';
import { type ComponentStore } from '../../core/component-store';

// Mock the Fragment component
vi.mock('../../components/fragment', () => ({
  default: ({ children, id }: { children: React.ReactNode; id: string }) => (
    <div data-testid={`fragment-${id}`}>
      {children}
    </div>
  ),
}));

// Mock console.log to avoid noise in tests
const originalConsoleLog = console.log;
beforeEach(() => {
  console.log = vi.fn();
});

afterEach(() => {
  console.log = originalConsoleLog;
});

describe('ReactRenderer', () => {
  let mockManager: {
    subscribe: Mock;
    getRootComponent: Mock;
  };
  let mockComponentStore: {
    get: Mock;
    subscribe: Mock;
    getVersion: Mock;
  };

  // Create stable references to avoid infinite loops
  const stableRootComponent = {
    name: 'root',
    key: 'root',
    props: {},
    children: []
  };

  beforeEach(() => {
    vi.clearAllMocks();
    
    mockManager = {
      subscribe: vi.fn(() => {
        // Don't call the callback immediately to avoid infinite loops
        return () => {};
      }),
      getRootComponent: vi.fn(() => stableRootComponent), // Use stable reference
    };

    mockComponentStore = {
      get: vi.fn(),
      subscribe: vi.fn(() => {
        // Don't call the callback immediately to avoid infinite loops
        return () => {};
      }),
      getVersion: vi.fn(() => 1), // Return stable version
    };
  });

  it('renders nothing when root component has no children', () => {
    mockManager.getRootComponent.mockReturnValue({
      name: 'root',
      key: 'root',
      props: {},
      children: []
    });
    
    const { container } = render(
      <ReactRenderer 
        manager={mockManager as unknown as RouteLitManager} 
        componentStore={mockComponentStore as unknown as ComponentStore} 
      />
    );
    
    expect(container.firstChild).toBeNull();
  });

  it('renders components with Suspense wrapper', () => {
    const mockComponent = vi.fn(() => <div>Test Component</div>);
    mockComponentStore.get.mockReturnValue(mockComponent);
    
    mockManager.getRootComponent.mockReturnValue({
      name: 'root',
      key: 'root',
      props: {},
      children: [
        {
          name: 'test-component',
          key: 'test-1',
          props: {},
          children: undefined,
          stale: false,
        }
      ]
    });
    
    render(
      <ReactRenderer 
        manager={mockManager as unknown as RouteLitManager} 
        componentStore={mockComponentStore as unknown as ComponentStore} 
      />
    );
    
    const component = screen.getByText('Test Component');
    expect(component).toBeInTheDocument();
    expect(component.closest('.rl-component')).toBeInTheDocument();
  });

  it('renders fragment components without Suspense', () => {
    mockManager.getRootComponent.mockReturnValue({
      name: 'root',
      key: 'root',
      props: {},
      children: [
        {
          name: 'fragment',
          key: 'fragment-1',
          props: { id: 'test-fragment' },
          children: [],
        }
      ]
    });
    
    render(
      <ReactRenderer 
        manager={mockManager as unknown as RouteLitManager} 
        componentStore={mockComponentStore as unknown as ComponentStore} 
      />
    );

    const fragment = screen.getByTestId('fragment-test-fragment');
    expect(fragment).toBeInTheDocument();
  });

  it('renders stale components with rl-stale class', () => {
    const mockComponent = vi.fn(() => <div>Stale Component</div>);
    mockComponentStore.get.mockReturnValue(mockComponent);
    
    mockManager.getRootComponent.mockReturnValue({
      name: 'root',
      key: 'root',
      props: {},
      children: [
        {
          name: 'test-component',
          key: 'test-1',
          props: {},
          children: undefined,
          stale: true,
        }
      ]
    });
    
    render(
      <ReactRenderer 
        manager={mockManager as unknown as RouteLitManager} 
        componentStore={mockComponentStore as unknown as ComponentStore} 
      />
    );
    
    const component = screen.getByText('Stale Component');
    const wrapper = component.closest('.rl-component');
    expect(wrapper).toHaveClass('rl-stale');
  });

  it('renders virtual components without rl-component wrapper', () => {
    const mockComponent = vi.fn(() => <div>Virtual Component</div>);
    mockComponentStore.get.mockReturnValue(mockComponent);
    
    mockManager.getRootComponent.mockReturnValue({
      name: 'root',
      key: 'root',
      props: {},
      children: [
        {
          name: 'test-component',
          key: 'test-1',
          props: {},
          children: undefined,
          virtual: true,
        }
      ]
    });
    
    render(
      <ReactRenderer 
        manager={mockManager as unknown as RouteLitManager} 
        componentStore={mockComponentStore as unknown as ComponentStore} 
      />
    );
    
    const component = screen.getByText('Virtual Component');
    expect(component.closest('.rl-component')).toBeNull();
  });

  it('shows loading state in Suspense fallback', async () => {
    const LazyComponent = React.lazy(() => Promise.resolve({
      default: () => <div>Loaded Component</div>
    }));
    mockComponentStore.get.mockReturnValue(LazyComponent);
    
    mockManager.getRootComponent.mockReturnValue({
      name: 'root',
      key: 'root',
      props: {},
      children: [
        {
          name: 'lazy-component',
          key: 'lazy-1',
          props: {},
          children: undefined,
        }
      ]
    });
    
    render(
      <ReactRenderer 
        manager={mockManager as unknown as RouteLitManager} 
        componentStore={mockComponentStore as unknown as ComponentStore} 
      />
    );
    
    // Loading state should be visible initially
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('subscribes to manager and component store', () => {
    // This test just verifies that the component can render without infinite loops
    // The actual subscription behavior is tested through the component's ability to render
    expect(() => {
      render(
        <ReactRenderer 
          manager={mockManager as unknown as RouteLitManager} 
          componentStore={mockComponentStore as unknown as ComponentStore} 
        />
      );
    }).not.toThrow();

    // Verify subscriptions were called
    expect(mockManager.subscribe).toHaveBeenCalledTimes(1);
    expect(mockComponentStore.subscribe).toHaveBeenCalledTimes(1);
  });

  it('passes children prop correctly', () => {
    const ParentComponent = vi.fn(({ children }: { children: React.ReactNode }) => (
      <div data-testid="parent">{children}</div>
    ));
    const ChildComponent = vi.fn(() => <div>Child</div>);
    
    mockComponentStore.get.mockImplementation((name: string) => {
      if (name === 'parent') return ParentComponent;
      if (name === 'child') return ChildComponent;
      return null;
    });
    
    mockManager.getRootComponent.mockReturnValue({
      name: 'root',
      key: 'root',
      props: {},
      children: [
        {
          name: 'parent',
          key: 'parent-1',
          props: {},
          children: [
            {
              name: 'child',
              key: 'child-1',
              props: {},
            }
          ],
        }
      ]
    });
    
    const { unmount } = render(
      <ReactRenderer 
        manager={mockManager as unknown as RouteLitManager} 
        componentStore={mockComponentStore as unknown as ComponentStore} 
      />
    );
    
    const parent = screen.getByTestId('parent');
    expect(parent).toContainHTML('Child');
    expect(ParentComponent).toHaveBeenCalledTimes(1);
    expect(ChildComponent).toHaveBeenCalledTimes(1);

    // Test cleanup
    unmount();
  });
}); 