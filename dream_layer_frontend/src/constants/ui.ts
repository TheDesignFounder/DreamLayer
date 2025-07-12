// UI Constants for consistent styling and sizing
export const UI_CONSTANTS = {
  // Modal dimensions
  MODAL_MAX_WIDTH: 'max-w-4xl',
  MODAL_MAX_HEIGHT: 'max-h-[90vh]',
  
  // Scroll area dimensions
  SCROLL_AREA_HEIGHT: 'h-[500px]',
  
  // Text truncation lengths
  PROMPT_PREVIEW_LENGTH: 50,
  PROMPT_TRUNCATE_LENGTH: 40,
  
  // Select component widths
  SELECT_WIDTH_SMALL: 'w-32',
  SELECT_WIDTH_MEDIUM: 'w-36',
  
  // Input widths
  INPUT_WIDTH_DEFAULT: 'w-16',
} as const;

// Slider specific constants
export const SLIDER_CONSTANTS = {
  DEFAULT_DECIMAL_STEP: 0.1,
  DEFAULT_INTEGER_STEP: 1,
  DECIMAL_PLACES: 1,
  PRESET_RANGE_THRESHOLD: 10,
  PRESET_SMALL_RANGE_THRESHOLD: 2,
  PRESET_PERCENTAGES: [0.25, 0.5, 0.75] as const,
} as const;