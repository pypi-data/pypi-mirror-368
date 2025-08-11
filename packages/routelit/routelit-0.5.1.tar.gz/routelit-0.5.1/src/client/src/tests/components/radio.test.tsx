import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import RadioGroup from '../../components/radio';
import { useFormDispatcherWithAttr, useIsLoading } from '../../core/context';

// Mock the context hooks
vi.mock('../../core/context', () => ({
  useFormDispatcherWithAttr: vi.fn(),
  useIsLoading: vi.fn(),
}));

describe('RadioGroup Component', () => {
  const defaultProps = {
    id: 'test-radio-group',
    label: 'Test Radio Group',
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
    render(<RadioGroup {...defaultProps} />);
    expect(screen.getByText('Test Radio Group')).toBeInTheDocument();
  });

  it('shows required indicator when required prop is true', () => {
    render(<RadioGroup {...defaultProps} required />);
    expect(screen.getByText('*')).toBeInTheDocument();
  });

  it('renders all options correctly', () => {
    render(<RadioGroup {...defaultProps} />);
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
    render(<RadioGroup {...propsWithCaption} />);
    expect(screen.getByText('Description for option 2')).toBeInTheDocument();
  });

  it('handles option selection correctly', () => {
    const mockDispatch = vi.fn();
    vi.mocked(useFormDispatcherWithAttr).mockReturnValue(mockDispatch);

    render(<RadioGroup {...defaultProps} />);
    const option2 = screen.getByLabelText('Option 2') as HTMLInputElement;
    
    fireEvent.click(option2);
    
    expect(mockDispatch).toHaveBeenCalledWith('option2');
  });

  it('applies flex direction correctly', () => {
    render(<RadioGroup {...defaultProps} flexDirection="row" />);
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
    render(<RadioGroup {...propsWithDisabled} />);
    const option2 = screen.getByLabelText('Option 2') as HTMLInputElement;
    expect(option2.disabled).toBe(true);
  });

  it('handles simple string options correctly', () => {
    const simpleProps = {
      ...defaultProps,
      options: ['option1', 'option2', 'option3']
    };

    render(<RadioGroup {...simpleProps} />);
    expect(screen.getByLabelText('option1')).toBeInTheDocument();
    expect(screen.getByLabelText('option2')).toBeInTheDocument();
    expect(screen.getByLabelText('option3')).toBeInTheDocument();
  });
}); 