import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import Fragment from '../../components/fragment';
import ReactRenderer from '../../core/react-renderer';
import { RouteLitManager } from '../../core/manager';

// Mock the context module completely
vi.mock('../../core/context', () => {
  const contextValue = { manager: {}, componentStore: {} };

  return {
    RouteLitContext: {
      Provider: ({ children }: { children: React.ReactNode }) => {
        return <div data-testid="context-provider">{children}</div>;
      },
    },
    useRouteLitContext: vi.fn().mockReturnValue(contextValue)
  };
});

// Mock dependencies
vi.mock('../../core/react-renderer', () => {
  return {
    default: vi.fn(() => <div data-testid="mock-renderer">Mocked Renderer</div>)
  };
});

vi.mock('../../core/manager', () => {
  return {
    RouteLitManager: vi.fn()
  };
});

describe('Fragment Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(RouteLitManager).mockImplementation(() => ({
      initialize: vi.fn(),
      terminate: vi.fn(),
      handleEvent: vi.fn(),
      handleError: vi.fn(),
      applyActions: vi.fn(),
      handlePopState: vi.fn(),
      getComponentsTree: vi.fn(() => []),
      isLoading: vi.fn(() => false),
      getError: vi.fn(() => undefined),
      getAtAddress: vi.fn(() => []),
      subscribe: vi.fn(() => () => {}),
      subscribeIsLoading: vi.fn(() => () => {}),
      subscribeError: vi.fn(() => () => {}),
      getLastURL: vi.fn(() => 'http://localhost')
    } as unknown as RouteLitManager));
  });

  it('renders a ReactRenderer with the correct props', () => {
    render(<Fragment id="test-fragment" />);

    expect(screen.getByTestId('mock-renderer')).toBeInTheDocument();
    expect(RouteLitManager).toHaveBeenCalledWith(
      expect.objectContaining({
        fragmentId: 'test-fragment',
        address: undefined
      })
    );
    expect(ReactRenderer).toHaveBeenCalled();
  });

  it('passes address to the RouteLitManager when provided', () => {
    const mockAddress = [1, 2, 3];
    render(<Fragment id="test-fragment" address={mockAddress} />);

    expect(RouteLitManager).toHaveBeenCalledWith(
      expect.objectContaining({
        fragmentId: 'test-fragment',
        address: mockAddress
      })
    );
  });

  it('only creates a new RouteLitManager when props change', () => {
    const { rerender } = render(<Fragment id="test-fragment" />);

    expect(RouteLitManager).toHaveBeenCalledTimes(1);

    // Rerender with the same props
    rerender(<Fragment id="test-fragment" />);

    // Should not create a new manager
    expect(RouteLitManager).toHaveBeenCalledTimes(1);

    // Rerender with different props
    rerender(<Fragment id="different-id" />);

    // Should create a new manager
    expect(RouteLitManager).toHaveBeenCalledTimes(2);
  });
});
