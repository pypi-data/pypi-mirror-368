import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import TextInput from '../../components/input';
import { useFormDispatcherWithAttr, useIsLoading } from '../../core/context';

// Mock the context hooks
vi.mock('../../core/context', () => ({
  useFormDispatcherWithAttr: vi.fn(),
  useIsLoading: vi.fn(),
}));

describe('TextInput Component', () => {
  const defaultProps = {
    id: 'test-input',
    label: 'Test Input',
    defaultValue: 'initial value',
  };

  beforeEach(() => {
    vi.mocked(useFormDispatcherWithAttr).mockReturnValue(vi.fn());
    vi.mocked(useIsLoading).mockReturnValue(false);
  });

  it('renders with label', () => {
    render(<TextInput {...defaultProps} />);
    expect(screen.getByText('Test Input')).toBeInTheDocument();
  });

  it('shows required indicator when required prop is true', () => {
    render(<TextInput {...defaultProps} required />);
    expect(screen.getByText('*')).toBeInTheDocument();
  });

  it('handles input change on blur', () => {
    const mockDispatch = vi.fn();
    vi.mocked(useFormDispatcherWithAttr).mockReturnValue(mockDispatch);

    render(<TextInput {...defaultProps} />);
    const input = screen.getByRole('textbox');
    
    fireEvent.input(input, { target: { value: 'new value' } });
    fireEvent.blur(input);
    
    expect(mockDispatch).toHaveBeenCalledWith('new value');
  });

  it('handles input change on Enter key', () => {
    const mockDispatch = vi.fn();
    vi.mocked(useFormDispatcherWithAttr).mockReturnValue(mockDispatch);

    render(<TextInput {...defaultProps} />);
    const input = screen.getByRole('textbox');
    
    fireEvent.input(input, { target: { value: 'new value' } });
    fireEvent.keyDown(input, { key: 'Enter' });
    
    expect(mockDispatch).toHaveBeenCalledWith('new value');
  });

  it('does not dispatch change when value remains the same', () => {
    const mockDispatch = vi.fn();
    vi.mocked(useFormDispatcherWithAttr).mockReturnValue(mockDispatch);

    render(<TextInput {...defaultProps} defaultValue="test value" />);
    const input = screen.getByRole('textbox');
    
    fireEvent.input(input, { target: { value: 'test value' } });
    fireEvent.blur(input);
    
    expect(mockDispatch).not.toHaveBeenCalled();
  });

  it('handles disabled state correctly', () => {
    render(<TextInput {...defaultProps} disabled />);
    const input = screen.getByRole('textbox');
    expect(input).toBeDisabled();
  });

  it('handles different input types', () => {
    render(<TextInput {...defaultProps} type="email" />);
    const input = screen.getByRole('textbox');
    expect(input).toHaveAttribute('type', 'email');
  });

  it('applies additional props correctly', () => {
    render(
      <TextInput
        {...defaultProps}
        placeholder="Enter text"
        className="custom-class"
        data-testid="custom-input"
      />
    );
    
    const input = screen.getByTestId('custom-input');
    expect(input).toHaveAttribute('placeholder', 'Enter text');
    expect(input).toHaveClass('custom-class');
  });

  it('handles initial value correctly', () => {
    render(<TextInput {...defaultProps} defaultValue="initial value" />);
    const input = screen.getByRole('textbox');
    expect(input).toHaveValue('initial value');
  });
}); 