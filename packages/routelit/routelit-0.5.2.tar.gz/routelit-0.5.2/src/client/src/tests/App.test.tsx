import { render, screen } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import React from 'react';
import App from '../App';

// Mock the lib module
vi.mock('../lib', () => ({
  manager: {
    initialize: vi.fn(),
    terminate: vi.fn(),
  },
  componentStore: {},
}));

// Mock the context module
vi.mock('../core/context', () => {
  return {
    RouteLitContext: {
      Provider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
    }
  };
});

// Mock ReactRenderer
vi.mock('../core/react-renderer', () => {
  return {
    default: () => <div data-testid="react-renderer">Mocked React Renderer</div>,
  };
});

// Import the mocked manager after mocking
import { manager } from '../lib';

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders ReactRenderer component', () => {
    render(<App />);

    expect(screen.getByTestId('react-renderer')).toBeInTheDocument();
  });

  it('initializes manager on mount', () => {
    render(<App />);

    expect(manager.initialize).toHaveBeenCalledTimes(1);
  });

  it('terminates manager on unmount', () => {
    const { unmount } = render(<App />);

    unmount();

    expect(manager.terminate).toHaveBeenCalledTimes(1);
  });
});
