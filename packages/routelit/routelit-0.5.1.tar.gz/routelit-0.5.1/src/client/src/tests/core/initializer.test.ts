import { describe, it, expect, vi } from 'vitest';
import initManager from '../../core/initializer';
import { RouteLitManager } from '../../core/manager';

// Mock the RouteLitManager
vi.mock('../../core/manager', () => ({
  RouteLitManager: vi.fn(),
}));

describe('initManager', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should initialize manager with empty configuration', () => {
    const result = initManager();

    expect(RouteLitManager).toHaveBeenCalledWith({});
    expect(result).toBeInstanceOf(RouteLitManager);
  });

  it('should return a new manager instance each time', () => {
    const result1 = initManager();
    const result2 = initManager();

    expect(RouteLitManager).toHaveBeenCalledTimes(2);
    expect(result1).not.toBe(result2);
  });
}); 