import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Markdown from '../../components/markdown';

// Mock react-markdown
vi.mock('react-markdown', () => {
  return {
    default: ({ children, rehypePlugins }: { children: string, rehypePlugins: unknown[] }) => {
      return <div data-testid="mock-markdown" data-plugins={rehypePlugins.length}>
        {children}
      </div>
    }
  };
});

// Mock rehype-raw
vi.mock('rehype-raw', () => {
  return {
    default: 'mock-rehype-raw'
  };
});

describe('Markdown Component', () => {
  it('renders markdown content', () => {
    const markdownText = '# Hello\n\nThis is **bold**';
    render(<Markdown body={markdownText} />);

    const content = screen.getByTestId('mock-markdown');
    expect(content).toBeInTheDocument();
    // Check for text content without exact whitespace matching
    expect(content).toHaveTextContent('Hello');
    expect(content).toHaveTextContent('This is **bold**');
  });

  it('does not use rehype-raw by default', () => {
    render(<Markdown body="Some markdown" />);

    const content = screen.getByTestId('mock-markdown');
    expect(content).toHaveAttribute('data-plugins', '0');
  });

  it('uses rehype-raw when allowUnsafeHtml is true', () => {
    render(<Markdown body="Some markdown with <b>HTML</b>" allowUnsafeHtml={true} />);

    const content = screen.getByTestId('mock-markdown');
    expect(content).toHaveAttribute('data-plugins', '1');
  });
});
