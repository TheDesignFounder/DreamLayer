# Undo/Redo System Implementation

## Overview

This implementation provides a comprehensive undo/redo system for the DreamLayer frontend, allowing users to revert and reapply changes to prompts, sliders, and other UI controls across both txt2img and img2img workflows.

## Features

### 🏗️ Core Components

1. **`useHistoryReducer`** - Base hook for managing history state
2. **`useGenerationHistory`** - Specialized hook for txt2img generation settings
3. **`useImg2ImgHistory`** - Specialized hook for img2img generation settings
4. **`UndoRedoControls`** - UI component with undo/redo buttons
5. **Keyboard Shortcuts** - Ctrl+Z (undo) and Ctrl+Y (redo)
6. **State Management** - Max 25 history states with automatic cleanup

### 🎯 Key Features

- **Debounced Updates**: Rapid changes are debounced (150ms) to prevent excessive history entries
- **Keyboard Shortcuts**: Standard Ctrl+Z/Ctrl+Y shortcuts work globally
- **Visual Feedback**: UI buttons show enabled/disabled state
- **History Counter**: Shows current number of history states
- **Mobile Support**: Responsive design with separate mobile controls
- **Type Safety**: Full TypeScript support with proper interfaces

## Implementation Details

### History Management

The system uses a reducer pattern with three arrays:
- `past`: Previous states (max 25)
- `present`: Current state
- `future`: States available for redo

```typescript
interface HistoryState<T> {
  past: T[];
  present: T;
  future: T[];
}
```

### Debouncing Strategy

Rapid changes (like typing or dragging sliders) are debounced to create meaningful history entries:

```typescript
// 150ms debounce prevents every keystroke from creating history
const debouncedSetState = useCallback((updates) => {
  // Clear existing timeout
  if (debounceTimeoutRef.current) {
    clearTimeout(debounceTimeoutRef.current);
  }
  
  // Set new timeout
  debounceTimeoutRef.current = setTimeout(() => {
    history.setState(newState);
  }, 150);
}, [history]);
```

### Keyboard Shortcuts

Global keyboard event listeners handle Ctrl+Z and Ctrl+Y:

```typescript
useEffect(() => {
  const handleKeyDown = (event: KeyboardEvent) => {
    if (event.ctrlKey || event.metaKey) {
      if (event.key === 'z' && !event.shiftKey) {
        event.preventDefault();
        undo();
      } else if (event.key === 'y' || (event.key === 'z' && event.shiftKey)) {
        event.preventDefault();
        redo();
      }
    }
  };
  
  document.addEventListener('keydown', handleKeyDown);
  return () => document.removeEventListener('keydown', handleKeyDown);
}, [undo, redo]);
```

## Usage Examples

### Basic Usage (txt2img)

```typescript
const MyComponent = () => {
  const history = useGenerationHistory(defaultSettings);
  
  const handlePromptChange = (prompt: string) => {
    history.updatePrompt(prompt);
  };
  
  return (
    <div>
      <UndoRedoControls
        canUndo={history.canUndo}
        canRedo={history.canRedo}
        onUndo={history.undo}
        onRedo={history.redo}
        historySize={history.historySize}
      />
      
      <PromptInput
        value={history.state.prompt}
        onChange={handlePromptChange}
      />
    </div>
  );
};
```

### Img2img Usage

```typescript
const Img2ImgComponent = () => {
  const history = useImg2ImgHistory(defaultCoreSettings);
  
  // All the same methods available plus img2img-specific ones
  const handleDenoisingChange = (strength: number) => {
    history.updateDenoisingStrength(strength);
  };
  
  return (
    <div>
      <UndoRedoControls {...history} />
      <DenoisingSlider
        value={history.state.denoising_strength}
        onChange={handleDenoisingChange}
      />
    </div>
  );
};
```

## API Reference

### `useHistoryReducer<T>`

Base hook for managing history state.

#### Parameters
- `initialState: T` - Initial state value
- `enableKeyboardShortcuts: boolean = true` - Enable Ctrl+Z/Ctrl+Y shortcuts

#### Returns
- `state: T` - Current state value
- `setState: (newState: T) => void` - Set new state (creates history entry)
- `undo: () => void` - Go back one state
- `redo: () => void` - Go forward one state
- `canUndo: boolean` - Whether undo is possible
- `canRedo: boolean` - Whether redo is possible
- `clear: (newState?: T) => void` - Clear history
- `historySize: number` - Total number of history states

### `useGenerationHistory`

Specialized hook for txt2img generation settings.

#### Additional Methods
- `updatePrompt: (prompt: string) => void`
- `updateNegativePrompt: (prompt: string) => void`
- `updateSampler: (sampler: string) => void`
- `updateSteps: (steps: number) => void`
- `updateCfgScale: (cfg: number) => void`
- `updateWidth: (width: number) => void`
- `updateHeight: (height: number) => void`
- `updateSeed: (seed: number) => void`
- `updateModel: (model: string) => void`
- `updateBatchSize: (size: number) => void`
- `updateBatchCount: (count: number) => void`
- `updateScheduler: (scheduler: string) => void`
- `updateRandomSeed: (random: boolean) => void`
- `updateSettings: (updates: Partial<Settings>) => void`
- `resetToDefault: (defaultSettings: Settings) => void`

### `useImg2ImgHistory`

Same as `useGenerationHistory` but for img2img settings, with additional methods:
- `updateDenoisingStrength: (strength: number) => void`
- `updateInputImage: (image: string) => void`

### `UndoRedoControls`

UI component with undo/redo buttons.

#### Props
- `canUndo: boolean` - Whether undo button is enabled
- `canRedo: boolean` - Whether redo button is enabled
- `onUndo: () => void` - Undo callback
- `onRedo: () => void` - Redo callback
- `historySize: number` - Number of history states
- `className?: string` - Additional CSS classes

## Testing

### E2E Test Suite

The implementation includes a comprehensive E2E test suite that can be run directly in the browser:

1. Open DreamLayer frontend
2. Open Developer Tools (F12)
3. Paste the test script from `src/tests/e2e/undo-redo-browser.js`
4. Run `runUndoRedoTests()`

### Test Scenarios

The test suite covers:

1. **Basic Prompt Undo/Redo**
   - Type text in prompt field
   - Press Ctrl+Z to undo
   - Verify field is blank
   - Press Ctrl+Y to redo
   - Verify text is restored

2. **Negative Prompt Undo/Redo**
   - Same as above but for negative prompt field

3. **Multiple Changes Undo/Redo**
   - Make multiple sequential changes
   - Test multiple undo/redo operations
   - Verify correct state at each step

4. **Undo/Redo Button Click**
   - Test UI buttons (if available)
   - Verify same behavior as keyboard shortcuts

5. **History Counter**
   - Verify history counter updates correctly
   - Test that it shows current state count

## Performance Considerations

### Memory Management
- History is automatically limited to 25 states
- Oldest states are removed when limit is exceeded
- Deep comparison prevents duplicate history entries

### Debouncing
- 150ms debounce prevents excessive history entries
- Pending updates are merged before creating history
- Cleanup on component unmount prevents memory leaks

### Keyboard Event Handling
- Global event listeners are properly cleaned up
- Event propagation is prevented for handled shortcuts
- Compatible with both Ctrl (Windows/Linux) and Cmd (Mac)

## Browser Compatibility

- **Modern Browsers**: Full support (Chrome 60+, Firefox 55+, Safari 12+, Edge 79+)
- **Mobile**: Touch-friendly UI with separate mobile controls
- **Keyboard Shortcuts**: Work on both Windows/Linux (Ctrl) and Mac (Cmd)
- **Accessibility**: Proper ARIA labels and keyboard navigation

## Customization

### Theming
The UndoRedoControls component uses CSS variables and can be themed:

```css
.undo-redo-controls {
  --button-bg: var(--background);
  --button-hover: var(--accent);
  --button-disabled: var(--muted);
}
```

### History Limit
The maximum history size can be adjusted in `useHistoryReducer`:

```typescript
const MAX_HISTORY_SIZE = 50; // Increase from default 25
```

### Debounce Timing
The debounce delay can be adjusted for different use cases:

```typescript
const DEBOUNCE_DELAY = 300; // Increase from default 150ms
```

## Best Practices

1. **Use Specific Update Methods**: Use `updatePrompt()` instead of `updateSettings({ prompt })` for better performance
2. **Batch Related Changes**: Group related changes together when possible
3. **Debounce User Input**: Let the system handle debouncing automatically
4. **Test Edge Cases**: Test with rapid changes, empty values, and limit conditions
5. **Accessibility**: Ensure keyboard shortcuts don't conflict with other features

## Future Enhancements

Potential improvements for future versions:

1. **Persistent History**: Save history to localStorage
2. **Branch History**: Support for branching undo/redo trees
3. **History Visualization**: Timeline view of changes
4. **Selective Undo**: Undo specific types of changes
5. **Collaborative History**: Shared history across multiple users
6. **Performance Optimization**: Virtual history for very large datasets

## Troubleshooting

### Common Issues

1. **Undo/Redo Not Working**
   - Check that keyboard shortcuts are enabled
   - Verify component is properly mounted
   - Check browser console for errors

2. **History Not Updating**
   - Ensure debounce delay has passed
   - Check that state actually changed
   - Verify proper event handling

3. **Memory Issues**
   - Check history limit settings
   - Ensure proper cleanup on unmount
   - Monitor history size in production

### Debug Mode

Enable debug logging by setting:

```typescript
const DEBUG_HISTORY = true;
```

This will log all history operations to the console.
