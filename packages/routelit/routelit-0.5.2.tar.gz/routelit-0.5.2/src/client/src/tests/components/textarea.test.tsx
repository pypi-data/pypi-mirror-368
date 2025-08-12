import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Textarea from '../../components/textarea';
import { useFormDispatcherWithAttr, useIsLoading } from '../../core/context';

// Mock the context hooks
vi.mock('../../core/context', () => ({
  useFormDispatcherWithAttr: vi.fn(),
  useIsLoading: vi.fn(),
}));

describe('Textarea Component', () => {
  const defaultProps = {
    id: 'test-textarea',
    label: 'Test Textarea',
    defaultValue: 'initial value',
  };

  beforeEach(() => {
    vi.mocked(useFormDispatcherWithAttr).mockReturnValue(vi.fn());
    vi.mocked(useIsLoading).mockReturnValue(false);
  });

  it('renders with label', () => {
    render(<Textarea {...defaultProps} />);
    expect(screen.getByText('Test Textarea')).toBeInTheDocument();
  });

  it('shows required indicator when required prop is true', () => {
    render(<Textarea {...defaultProps} required />);
    expect(screen.getByText('*')).toBeInTheDocument();
  });

  it('handles textarea change on blur', () => {
    const mockDispatch = vi.fn();
    vi.mocked(useFormDispatcherWithAttr).mockReturnValue(mockDispatch);

    render(<Textarea {...defaultProps} />);
    const textarea = screen.getByRole('textbox');
    
    fireEvent.input(textarea, { target: { value: 'new value' } });
    fireEvent.blur(textarea);
    
    expect(mockDispatch).toHaveBeenCalledWith('new value');
  });

  it('handles textarea change on Enter key', () => {
    const mockDispatch = vi.fn();
    vi.mocked(useFormDispatcherWithAttr).mockReturnValue(mockDispatch);

    render(<Textarea {...defaultProps} />);
    const textarea = screen.getByRole('textbox');
    
    fireEvent.input(textarea, { target: { value: 'new value' } });
    fireEvent.keyDown(textarea, { key: 'Enter' });
    
    expect(mockDispatch).toHaveBeenCalledWith('new value');
  });

  it('does not dispatch change when value remains the same', () => {
    const mockDispatch = vi.fn();
    vi.mocked(useFormDispatcherWithAttr).mockReturnValue(mockDispatch);

    render(<Textarea {...defaultProps} defaultValue="test value" />);
    const textarea = screen.getByRole('textbox');
    
    fireEvent.input(textarea, { target: { value: 'test value' } });
    fireEvent.blur(textarea);
    
    expect(mockDispatch).not.toHaveBeenCalled();
  });

  it('handles disabled state correctly', () => {
    render(<Textarea {...defaultProps} disabled />);
    const textarea = screen.getByRole('textbox');
    expect(textarea).toBeDisabled();
  });

  it('applies additional props correctly', () => {
    render(
      <Textarea
        {...defaultProps}
        placeholder="Enter text"
        className="custom-class"
        data-testid="custom-textarea"
      />
    );
    
    const textarea = screen.getByTestId('custom-textarea');
    expect(textarea).toHaveAttribute('placeholder', 'Enter text');
    expect(textarea).toHaveClass('custom-class');
  });

  it('handles initial value correctly', () => {
    render(<Textarea {...defaultProps} defaultValue="initial value" />);
    const textarea = screen.getByRole('textbox');
    expect(textarea).toHaveValue('initial value');
  });

  it('handles multiline text correctly', () => {
    const multilineText = 'Line 1\nLine 2\nLine 3';
    render(<Textarea {...defaultProps} defaultValue={multilineText} />);
    const textarea = screen.getByRole('textbox');
    expect(textarea).toHaveValue(multilineText);
  });
}); 