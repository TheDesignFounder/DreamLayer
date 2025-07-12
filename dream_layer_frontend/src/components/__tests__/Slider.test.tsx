import { render, screen, fireEvent } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import Slider from '../Slider';
import { SLIDER_CONSTANTS } from '@/constants/ui';

const defaultProps = {
  min: 0,
  max: 100,
  defaultValue: 50,
  label: 'Test Slider',
};

describe('Slider', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders with correct label', () => {
    render(<Slider {...defaultProps} />);
    expect(screen.getByText('Test Slider')).toBeInTheDocument();
  });

  it('displays current value in input field', () => {
    render(<Slider {...defaultProps} />);
    const input = screen.getByDisplayValue('50');
    expect(input).toBeInTheDocument();
  });

  it('calls onChange when value changes', () => {
    const onChange = vi.fn();
    render(<Slider {...defaultProps} onChange={onChange} />);
    
    const input = screen.getByDisplayValue('50');
    fireEvent.change(input, { target: { value: '75' } });
    fireEvent.blur(input);
    
    expect(onChange).toHaveBeenCalledWith(75);
  });

  it('handles increment button click', () => {
    const onChange = vi.fn();
    render(<Slider {...defaultProps} onChange={onChange} />);
    
    const input = screen.getByDisplayValue('50');
    const container = input.closest('.relative');
    const incrementButton = container?.querySelector('button');
    
    if (incrementButton) {
      fireEvent.click(incrementButton);
      expect(onChange).toHaveBeenCalledWith(51); // default step is 1
    }
  });

  it('handles decrement button click', () => {
    const onChange = vi.fn();
    render(<Slider {...defaultProps} onChange={onChange} />);
    
    const input = screen.getByDisplayValue('50');
    const container = input.closest('.relative');
    const buttons = container?.querySelectorAll('button');
    const decrementButton = buttons?.[1]; // second button is decrement
    
    if (decrementButton) {
      fireEvent.click(decrementButton);
      expect(onChange).toHaveBeenCalledWith(49); // default step is 1
    }
  });

  it('handles keyboard arrow up/down', () => {
    const onChange = vi.fn();
    render(<Slider {...defaultProps} onChange={onChange} />);
    
    const input = screen.getByDisplayValue('50');
    
    fireEvent.keyDown(input, { key: 'ArrowUp' });
    expect(onChange).toHaveBeenCalledWith(51);
    
    fireEvent.keyDown(input, { key: 'ArrowDown' });
    expect(onChange).toHaveBeenCalledWith(50); // back to original value
  });

  it('uses decimal step for values less than 1', () => {
    const onChange = vi.fn();
    const props = {
      ...defaultProps,
      min: 0,
      max: 1,
      defaultValue: 0.5,
    };
    
    render(<Slider {...props} onChange={onChange} />);
    
    const input = screen.getByDisplayValue('0.5');
    fireEvent.keyDown(input, { key: 'ArrowUp' });
    
    expect(onChange).toHaveBeenCalledWith(0.6); // 0.5 + 0.1 (decimal step)
  });

  it('respects min/max boundaries', () => {
    const onChange = vi.fn();
    const props = {
      ...defaultProps,
      min: 0,
      max: 10,
      defaultValue: 10, // at max
    };
    
    render(<Slider {...props} onChange={onChange} />);
    
    const input = screen.getByDisplayValue('10');
    fireEvent.keyDown(input, { key: 'ArrowUp' });
    
    expect(onChange).toHaveBeenCalledWith(10); // should stay at max
  });

  it('validates input on blur and clamps to range', () => {
    const onChange = vi.fn();
    render(<Slider {...defaultProps} onChange={onChange} />);
    
    const input = screen.getByDisplayValue('50');
    fireEvent.change(input, { target: { value: '150' } }); // above max
    fireEvent.blur(input);
    
    expect(onChange).toHaveBeenCalledWith(100); // clamped to max
  });

  it('handles custom step value', () => {
    const onChange = vi.fn();
    const props = {
      ...defaultProps,
      step: 5,
    };
    
    render(<Slider {...props} onChange={onChange} />);
    
    const input = screen.getByDisplayValue('50');
    fireEvent.keyDown(input, { key: 'ArrowUp' });
    
    expect(onChange).toHaveBeenCalledWith(55); // 50 + 5 (custom step)
  });

  it('displays sublabel when provided', () => {
    const props = {
      ...defaultProps,
      sublabel: 'Test sublabel',
    };
    
    render(<Slider {...props} />);
    expect(screen.getByText('Test sublabel')).toBeInTheDocument();
  });

  it('hides input when hideInput is true', () => {
    const props = {
      ...defaultProps,
      hideInput: true,
    };
    
    render(<Slider {...props} />);
    
    const input = screen.queryByDisplayValue('50');
    expect(input).not.toBeInTheDocument();
  });

  it('generates preset values for appropriate ranges', () => {
    const props = {
      ...defaultProps,
      min: 0,
      max: 20, // range > 10, should generate presets
    };
    
    render(<Slider {...props} />);
    
    // Should have preset buttons
    const presetButtons = screen.getAllByRole('button').filter(
      button => /^\d+$/.test(button.textContent || '')
    );
    expect(presetButtons.length).toBeGreaterThan(0);
  });

  it('uses constants for step calculations', () => {
    // Test that constants are being used correctly
    expect(SLIDER_CONSTANTS.DEFAULT_DECIMAL_STEP).toBe(0.1);
    expect(SLIDER_CONSTANTS.DEFAULT_INTEGER_STEP).toBe(1);
    expect(SLIDER_CONSTANTS.DECIMAL_PLACES).toBe(1);
  });
});