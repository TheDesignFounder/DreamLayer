import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import PromptInput from '../PromptInput';

// Mock the service call to avoid network requests in tests
vi.mock('@/services/modelService', () => ({
  fetchRandomPrompt: vi.fn().mockResolvedValue('mocked random prompt')
}));

describe('PromptInput Required Field Validation', () => {
  const defaultProps = {
    label: 'Test Prompt',
    value: '',
    onChange: vi.fn(),
    maxLength: 500,
    placeholder: 'Enter test prompt'
  };

  it('should show red ring for empty required field', () => {
    render(
      <PromptInput 
        {...defaultProps}
        required={true}
        value=""
      />
    );

    const textarea = screen.getByRole('textbox');
    
    // Check that the red ring classes are applied when required and empty
    expect(textarea).toHaveClass('ring-2', 'ring-red-500');
  });

  it('should not show red ring when required field has content', () => {
    render(
      <PromptInput 
        {...defaultProps}
        required={true}
        value="some content"
      />
    );

    const textarea = screen.getByRole('textbox');
    
    // Check that red ring classes are NOT applied when field has content
    expect(textarea).not.toHaveClass('ring-2', 'ring-red-500');
  });

  it('should not show red ring for optional empty field', () => {
    render(
      <PromptInput 
        {...defaultProps}
        required={false}
        value=""
      />
    );

    const textarea = screen.getByRole('textbox');
    
    // Check that red ring classes are NOT applied for optional fields
    expect(textarea).not.toHaveClass('ring-2', 'ring-red-500');
  });

  it('should show asterisk (*) for required fields', () => {
    render(
      <PromptInput 
        {...defaultProps}
        required={true}
        label="Required Field"
      />
    );

    // Check that asterisk appears for required fields
    expect(screen.getByText('*')).toBeInTheDocument();
    expect(screen.getByText('Required Field')).toBeInTheDocument();
  });

  it('should not show asterisk for optional fields', () => {
    render(
      <PromptInput 
        {...defaultProps}
        required={false}
        label="Optional Field"
      />
    );

    // Check that asterisk does NOT appear for optional fields
    expect(screen.queryByText('*')).not.toBeInTheDocument();
    expect(screen.getByText('Optional Field')).toBeInTheDocument();
  });

  it('should update validation when value changes', () => {
    const { rerender } = render(
      <PromptInput 
        {...defaultProps}
        required={true}
        value=""
      />
    );

    const textarea = screen.getByRole('textbox');
    
    // Initially empty and required - should have red ring
    expect(textarea).toHaveClass('ring-2', 'ring-red-500');

    // Rerender with content
    rerender(
      <PromptInput 
        {...defaultProps}
        required={true}
        value="new content"
      />
    );

    // Now with content - should not have red ring
    expect(textarea).not.toHaveClass('ring-2', 'ring-red-500');
  });

  it('should handle whitespace-only values as empty', () => {
    render(
      <PromptInput 
        {...defaultProps}
        required={true}
        value="   "  // Only whitespace
      />
    );

    const textarea = screen.getByRole('textbox');
    
    // Whitespace-only should be treated as empty for required validation
    expect(textarea).toHaveClass('ring-2', 'ring-red-500');
  });
});

/* 
 * Note: To run these tests, you would need to set up:
 * 1. Vitest or Jest as the test runner
 * 2. @testing-library/react for React component testing
 * 3. @testing-library/jest-dom for additional matchers
 * 
 * Example commands:
 * npm install --save-dev vitest @testing-library/react @testing-library/jest-dom
 * npm run test
 */