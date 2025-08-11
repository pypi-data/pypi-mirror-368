import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import Expander from '../../components/expander';

describe('Expander Component', () => {
  const defaultProps = {
    title: 'Expandable Section',
    open: false,
    children: <div>Expanded content</div>,
  };

  it('renders with title', () => {
    render(<Expander {...defaultProps} />);
    expect(screen.getByText('Expandable Section')).toBeInTheDocument();
  });

  it('renders as a details element', () => {
    render(<Expander {...defaultProps} />);
    const details = screen.getByText('Expandable Section').closest('details');
    expect(details).toBeInTheDocument();
    expect(details?.tagName).toBe('DETAILS');
  });

  it('renders summary element with title', () => {
    render(<Expander {...defaultProps} />);
    const summary = screen.getByText('Expandable Section').closest('summary');
    expect(summary).toBeInTheDocument();
    expect(summary?.tagName).toBe('SUMMARY');
  });

  it('renders children content', () => {
    render(<Expander {...defaultProps} />);
    expect(screen.getByText('Expanded content')).toBeInTheDocument();
  });

  it('is closed by default when open prop is false', () => {
    render(<Expander {...defaultProps} open={false} />);
    const details = screen.getByText('Expandable Section').closest('details');
    expect(details).not.toHaveAttribute('open');
  });

  it('is open when open prop is true', () => {
    render(<Expander {...defaultProps} open={true} />);
    const details = screen.getByText('Expandable Section').closest('details');
    expect(details).toHaveAttribute('open');
  });

  it('handles different title text', () => {
    render(
      <Expander
        title="Custom Title"
        open={false}
        children={<div>Content</div>}
      />
    );
    expect(screen.getByText('Custom Title')).toBeInTheDocument();
  });

  it('handles complex children content', () => {
    const complexChildren = (
      <div>
        <h3>Section Header</h3>
        <p>This is a paragraph with some text.</p>
        <ul>
          <li>List item 1</li>
          <li>List item 2</li>
        </ul>
      </div>
    );

    render(
      <Expander
        title="Complex Content"
        open={true}
        children={complexChildren}
      />
    );

    expect(screen.getByText('Complex Content')).toBeInTheDocument();
    expect(screen.getByText('Section Header')).toBeInTheDocument();
    expect(screen.getByText('This is a paragraph with some text.')).toBeInTheDocument();
    expect(screen.getByText('List item 1')).toBeInTheDocument();
    expect(screen.getByText('List item 2')).toBeInTheDocument();
  });

  it('handles empty children', () => {
    render(
      <Expander
        title="Empty Content"
        open={false}
        children={null}
      />
    );
    
    expect(screen.getByText('Empty Content')).toBeInTheDocument();
    const details = screen.getByText('Empty Content').closest('details');
    expect(details).toBeInTheDocument();
  });

  it('handles string children', () => {
    render(
      <Expander
        title="String Content"
        open={true}
        children="Simple string content"
      />
    );
    
    expect(screen.getByText('String Content')).toBeInTheDocument();
    expect(screen.getByText('Simple string content')).toBeInTheDocument();
  });

  it('handles multiple children elements', () => {
    const multipleChildren = [
      <div key="1">First child</div>,
      <div key="2">Second child</div>,
      <div key="3">Third child</div>,
    ];

    render(
      <Expander
        title="Multiple Children"
        open={true}
        children={multipleChildren}
      />
    );

    expect(screen.getByText('Multiple Children')).toBeInTheDocument();
    expect(screen.getByText('First child')).toBeInTheDocument();
    expect(screen.getByText('Second child')).toBeInTheDocument();
    expect(screen.getByText('Third child')).toBeInTheDocument();
  });

  it('maintains proper HTML structure', () => {
    render(<Expander {...defaultProps} />);
    
    const details = screen.getByText('Expandable Section').closest('details');
    const summary = screen.getByText('Expandable Section').closest('summary');
    
    expect(details).toBeInTheDocument();
    expect(summary).toBeInTheDocument();
    expect(summary?.parentElement).toBe(details);
  });
}); 