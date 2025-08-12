import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Select from '../../components/select';
import { useFormDispatcherWithAttr, useIsLoading } from '../../core/context';

// Mock the context hooks
vi.mock('../../core/context', () => ({
  useFormDispatcherWithAttr: vi.fn(),
  useIsLoading: vi.fn(),
}));

describe('Select Component', () => {
  const defaultProps = {
    id: 'test-select',
    label: 'Test Select',
    options: [
      { value: 'option1', label: 'Option 1' },
      { value: 'option2', label: 'Option 2' },
      { value: 'option3', label: 'Option 3' }
    ],
    value: 'option1'
  };

  beforeEach(() => {
    vi.mocked(useFormDispatcherWithAttr).mockReturnValue(vi.fn());
    vi.mocked(useIsLoading).mockReturnValue(false);
  });

  it('renders with label', () => {
    render(<Select {...defaultProps} />);
    expect(screen.getByText('Test Select')).toBeInTheDocument();
  });

  it('shows required indicator when required prop is true', () => {
    render(<Select {...defaultProps} required />);
    expect(screen.getByText('*')).toBeInTheDocument();
  });

  it('renders all options correctly', () => {
    render(<Select {...defaultProps} />);
    expect(screen.getByText('Option 1')).toBeInTheDocument();
    expect(screen.getByText('Option 2')).toBeInTheDocument();
    expect(screen.getByText('Option 3')).toBeInTheDocument();
  });

  it('handles option selection correctly', () => {
    const mockDispatch = vi.fn();
    vi.mocked(useFormDispatcherWithAttr).mockReturnValue(mockDispatch);

    render(<Select {...defaultProps} />);
    const select = screen.getByRole('combobox');
    
    fireEvent.change(select, { target: { value: 'option2' } });
    
    expect(mockDispatch).toHaveBeenCalledWith('option2');
  });

  it('handles disabled state correctly', () => {
    render(<Select {...defaultProps} disabled />);
    const select = screen.getByRole('combobox');
    expect(select).toBeDisabled();
  });

  it('handles disabled options correctly', () => {
    const propsWithDisabledOption = {
      ...defaultProps,
      options: [
        { value: 'option1', label: 'Option 1' },
        { value: 'option2', label: 'Option 2', disabled: true },
        { value: 'option3', label: 'Option 3' }
      ]
    };
    render(<Select {...propsWithDisabledOption} />);
    const options = screen.getByRole('combobox').getElementsByTagName('option');
    expect(options[1].disabled).toBe(true);
  });

  it('does not dispatch change when value remains the same', () => {
    const mockDispatch = vi.fn();
    vi.mocked(useFormDispatcherWithAttr).mockReturnValue(mockDispatch);

    render(<Select {...defaultProps} value="option1" />);
    const select = screen.getByRole('combobox');
    
    fireEvent.change(select, { target: { value: 'option1' } });
    
    expect(mockDispatch).not.toHaveBeenCalled();
  });
}); 