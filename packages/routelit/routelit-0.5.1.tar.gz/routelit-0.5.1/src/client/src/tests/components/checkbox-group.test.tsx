import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import CheckboxGroup from '../../components/checkbox-group';
import { useFormDispatcherWithAttr, useIsLoading } from '../../core/context';

// Mock the context hooks
vi.mock('../../core/context', () => ({
  useFormDispatcherWithAttr: vi.fn(),
  useIsLoading: vi.fn(),
}));

describe('CheckboxGroup Component', () => {
  const defaultProps = {
    id: 'test-checkbox-group',
    label: 'Test Checkbox Group',
    options: [
      { value: 'option1', label: 'Option 1' },
      { value: 'option2', label: 'Option 2' },
      { value: 'option3', label: 'Option 3' }
    ],
    value: ['option1']
  };

  beforeEach(() => {
    vi.mocked(useFormDispatcherWithAttr).mockReturnValue(vi.fn());
    vi.mocked(useIsLoading).mockReturnValue(false);
  });

  it('renders with label', () => {
    render(<CheckboxGroup {...defaultProps} />);
    expect(screen.getByText('Test Checkbox Group')).toBeInTheDocument();
  });

  it('shows required indicator when required prop is true', () => {
    render(<CheckboxGroup {...defaultProps} required />);
    expect(screen.getByText('*')).toBeInTheDocument();
  });

  it('renders all options correctly', () => {
    render(<CheckboxGroup {...defaultProps} />);
    expect(screen.getByLabelText('Option 1')).toBeInTheDocument();
    expect(screen.getByLabelText('Option 2')).toBeInTheDocument();
    expect(screen.getByLabelText('Option 3')).toBeInTheDocument();
  });

  it('displays caption when provided', () => {
    const propsWithCaption = {
      ...defaultProps,
      options: [
        { value: 'option1', label: 'Option 1' },
        { value: 'option2', label: 'Option 2', caption: 'Description for option 2' },
        { value: 'option3', label: 'Option 3' }
      ]
    };
    render(<CheckboxGroup {...propsWithCaption} />);
    expect(screen.getByText('Description for option 2')).toBeInTheDocument();
  });

  it('handles checkbox selection correctly', () => {
    const mockDispatch = vi.fn();
    vi.mocked(useFormDispatcherWithAttr).mockReturnValue(mockDispatch);

    render(<CheckboxGroup {...defaultProps} />);
    const option2 = screen.getByLabelText('Option 2') as HTMLInputElement;
    
    fireEvent.click(option2);
    
    expect(mockDispatch).toHaveBeenCalledWith(['option1', 'option2']);
  });

  it('handles checkbox deselection correctly', () => {
    const mockDispatch = vi.fn();
    vi.mocked(useFormDispatcherWithAttr).mockReturnValue(mockDispatch);

    render(<CheckboxGroup {...defaultProps} />);
    const option1 = screen.getByLabelText('Option 1') as HTMLInputElement;
    
    fireEvent.click(option1);
    
    expect(mockDispatch).toHaveBeenCalledWith([]);
  });

  it('applies flex direction correctly', () => {
    render(<CheckboxGroup {...defaultProps} flexDirection="row" />);
    const container = document.querySelector('.rl-form-control-group');
    expect(container).toHaveClass('rl-flex-row');
  });

  it('handles disabled state correctly', () => {
    const propsWithDisabled = {
      ...defaultProps,
      options: [
        { value: 'option1', label: 'Option 1' },
        { value: 'option2', label: 'Option 2', disabled: true },
        { value: 'option3', label: 'Option 3' }
      ]
    };
    render(<CheckboxGroup {...propsWithDisabled} />);
    const option2 = screen.getByLabelText('Option 2') as HTMLInputElement;
    expect(option2.disabled).toBe(true);
  });

  it('maintains checked state for selected options', () => {
    render(<CheckboxGroup {...defaultProps} value={['option1', 'option3']} />);
    const option1 = screen.getByLabelText('Option 1') as HTMLInputElement;
    const option3 = screen.getByLabelText('Option 3') as HTMLInputElement;
    
    expect(option1.checked).toBe(true);
    expect(option3.checked).toBe(true);
  });
}); 