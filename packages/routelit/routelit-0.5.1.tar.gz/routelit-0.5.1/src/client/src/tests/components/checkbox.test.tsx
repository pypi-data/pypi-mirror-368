import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Checkbox from '../../components/checkbox';
import { useFormDispatcherWithAttr, useIsLoading } from '../../core/context';

// Mock the context hooks
vi.mock('../../core/context', () => ({
  useFormDispatcherWithAttr: vi.fn(),
  useIsLoading: vi.fn(),
}));

describe('Checkbox Component', () => {
  beforeEach(() => {
    vi.mocked(useFormDispatcherWithAttr).mockReturnValue(vi.fn());
    vi.mocked(useIsLoading).mockReturnValue(false);
  });

  it('renders with label', () => {
    render(<Checkbox id="test" label="Test Checkbox" checked={false} />);
    expect(screen.getByLabelText('Test Checkbox')).toBeInTheDocument();
  });

  it('shows required indicator when required prop is true', () => {
    render(<Checkbox id="test" label="Test Checkbox" checked={false} required />);
    expect(screen.getByText('*')).toBeInTheDocument();
  });

  it('does not show required indicator when required prop is false', () => {
    render(<Checkbox id="test" label="Test Checkbox" checked={false} />);
    expect(screen.queryByText('*')).not.toBeInTheDocument();
  });

  it('handles checked state correctly', () => {
    render(<Checkbox id="test" label="Test Checkbox" checked={true} />);
    const checkbox = screen.getByLabelText('Test Checkbox') as HTMLInputElement;
    expect(checkbox.checked).toBe(true);
  });

  it('handles disabled state correctly', () => {
    render(<Checkbox id="test" label="Test Checkbox" checked={false} disabled />);
    const checkbox = screen.getByLabelText('Test Checkbox') as HTMLInputElement;
    expect(checkbox.disabled).toBe(true);
  });

  it('calls onChange handler when clicked', () => {
    const mockDispatch = vi.fn();
    vi.mocked(useFormDispatcherWithAttr).mockReturnValue(mockDispatch);

    render(<Checkbox id="test" label="Test Checkbox" checked={false} />);
    const checkbox = screen.getByLabelText('Test Checkbox');
    
    fireEvent.click(checkbox);
    expect(mockDispatch).toHaveBeenCalledWith(true);
  });

  it('applies additional props correctly', () => {
    render(
      <Checkbox
        id="test"
        label="Test Checkbox"
        checked={false}
        data-testid="custom-checkbox"
        className="custom-class"
      />
    );
    
    const checkbox = screen.getByTestId('custom-checkbox');
    expect(checkbox).toHaveClass('custom-class');
  });
}); 