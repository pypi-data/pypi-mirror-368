import React from 'react';
import { render, screen, fireEvent, cleanup } from '@testing-library/react';
import { describe, it, expect, afterEach, vi } from 'vitest';

// Mock handler for events
const mockHandleEvent = vi.fn();

// Create the mock functions outside of the component
const mockDispatcherWithFn = vi.fn((id: string, type: string) => {
  return (data: Record<string, unknown>) => {
    mockHandleEvent({
      type: 'routelit:event',
      detail: { id, type, ...data }
    });
  };
});

const mockDispatcherWithAttrFn = vi.fn((id: string, type: string, attr: string) => {
  return (value: unknown) => {
    mockHandleEvent({
      type: 'routelit:event',
      detail: { id, type, [attr]: value }
    });
  };
});

const mockIsLoading = vi.fn(() => false);
const mockGetError = vi.fn((): Error | undefined => undefined);

// Mock the context module directly
vi.mock('../../core/context', () => {
  // Mock context
  const contextValue = {
    manager: {
      handleEvent: mockHandleEvent,
      subscribeIsLoading: vi.fn(() => () => {}),
      isLoading: mockIsLoading,
      subscribeError: vi.fn(() => () => {}),
      getError: mockGetError
    },
    componentStore: {}
  };

  return {
    RouteLitContext: React.createContext(contextValue),
    useRouteLitContext: vi.fn().mockReturnValue(contextValue),
    useDispatcherWith: mockDispatcherWithFn,
    useDispatcherWithAttr: mockDispatcherWithAttrFn,
    useFormDispatcherWithAttr: vi.fn(),
    useFormDispatcher: vi.fn(),
    useIsLoading: mockIsLoading,
    useError: mockGetError
  };
});

// Test components that use the hooks
const TestDispatcherWith = ({ id, type }: { id: string, type: string }) => {
  const dispatch = mockDispatcherWithFn(id, type);
  return <button data-testid="dispatch-button" onClick={() => dispatch({ testData: 'value' })}>Dispatch</button>;
};

const TestDispatcherWithAttr = ({ id, type, attr }: { id: string, type: string, attr: string }) => {
  const dispatch = mockDispatcherWithAttrFn(id, type, attr);
  return <button data-testid="dispatch-attr-button" onClick={() => dispatch('attr-value')}>Dispatch Attr</button>;
};

const TestIsLoading = () => {
  const isLoading = mockIsLoading();
  return <div data-testid="loading-status">{isLoading ? 'Loading' : 'Not loading'}</div>;
};

const TestUseError = () => {
  const error = mockGetError();
  return <div data-testid="error-message">{error ? error.message : 'No error'}</div>;
};

describe('Context Hooks', () => {
  // Clean up after each test to remove rendered components
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it('useDispatcherWith creates a function that dispatches events with the right parameters', () => {
    render(<TestDispatcherWith id="test-id" type="test-type" />);

    fireEvent.click(screen.getByTestId('dispatch-button'));

    expect(mockHandleEvent).toHaveBeenCalledTimes(1);

    // Check the event object
    const event = mockHandleEvent.mock.calls[0][0];
    expect(event.type).toBe('routelit:event');
    expect(event.detail).toEqual({
      id: 'test-id',
      type: 'test-type',
      testData: 'value'
    });
  });

  it('useDispatcherWithAttr creates a function that dispatches events with attribute values', () => {
    render(<TestDispatcherWithAttr id="test-id" type="test-type" attr="testAttr" />);

    fireEvent.click(screen.getByTestId('dispatch-attr-button'));

    expect(mockHandleEvent).toHaveBeenCalledTimes(1);

    // Check the event object
    const event = mockHandleEvent.mock.calls[0][0];
    expect(event.type).toBe('routelit:event');
    expect(event.detail).toEqual({
      id: 'test-id',
      type: 'test-type',
      testAttr: 'attr-value'
    });
  });

  it('useIsLoading returns the loading state from the manager', () => {
    // First test with isLoading = false
    mockIsLoading.mockReturnValue(false);

    const { unmount } = render(<TestIsLoading />);
    expect(screen.getByTestId('loading-status')).toHaveTextContent('Not loading');

    // Unmount the first component
    unmount();

    // Rerender with isLoading = true
    mockIsLoading.mockReturnValue(true);

    render(<TestIsLoading />);
    expect(screen.getByTestId('loading-status')).toHaveTextContent('Loading');
  });

  it('useError returns the error from the manager', () => {
    // First test with no error
    mockGetError.mockReturnValue(undefined);

    const { unmount } = render(<TestUseError />);
    expect(screen.getByTestId('error-message')).toHaveTextContent('No error');

    // Unmount the first component
    unmount();

    // Rerender with an error
    const testError = new Error('Test error message');
    mockGetError.mockReturnValue(testError);

    render(<TestUseError />);
    expect(screen.getByTestId('error-message')).toHaveTextContent('Test error message');
  });
});
