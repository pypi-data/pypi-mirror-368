// Make TypeScript recognize Jest-DOM matchers
import '@testing-library/jest-dom';
import { vi } from 'vitest';

// This file is used by Vitest to setup the testing environment
// It's referenced in the vitest.config.ts file under setupFiles

// Mock ResizeObserver
const ResizeObserverMock = vi.fn(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

vi.stubGlobal('ResizeObserver', ResizeObserverMock);

// Mock IntersectionObserver
const IntersectionObserverMock = vi.fn(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

vi.stubGlobal('IntersectionObserver', IntersectionObserverMock);

// This will be run before each test
beforeEach(() => {
  // You can add global setup code here if needed
});
