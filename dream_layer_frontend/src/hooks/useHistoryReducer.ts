import { useReducer, useCallback, useRef, useEffect } from 'react';

interface HistoryState<T> {
  past: T[];
  present: T;
  future: T[];
}

interface HistoryAction<T> {
  type: 'UNDO' | 'REDO' | 'SET' | 'CLEAR';
  payload?: T;
}

const MAX_HISTORY_SIZE = 25;

function historyReducer<T>(state: HistoryState<T>, action: HistoryAction<T>): HistoryState<T> {
  const { past, present, future } = state;

  switch (action.type) {
    case 'UNDO':
      if (past.length === 0) return state;
      
      const previous = past[past.length - 1];
      const undoPast = past.slice(0, past.length - 1);
      
      return {
        past: undoPast,
        present: previous,
        future: [present, ...future]
      };

    case 'REDO':
      if (future.length === 0) return state;
      
      const next = future[0];
      const newFuture = future.slice(1);
      
      return {
        past: [...past, present],
        present: next,
        future: newFuture
      };

    case 'SET':
      if (!action.payload) return state;
      
      // Don't add to history if the new state is the same as current
      if (JSON.stringify(action.payload) === JSON.stringify(present)) {
        return state;
      }
      
      const newPast = [...past, present];
      
      // Limit history size
      if (newPast.length > MAX_HISTORY_SIZE) {
        newPast.shift(); // Remove oldest entry
      }
      
      return {
        past: newPast,
        present: action.payload,
        future: []
      };

    case 'CLEAR':
      return {
        past: [],
        present: action.payload || present,
        future: []
      };

    default:
      return state;
  }
}

export interface UseHistoryReducerReturn<T> {
  state: T;
  setState: (newState: T) => void;
  undo: () => void;
  redo: () => void;
  canUndo: boolean;
  canRedo: boolean;
  clear: (newState?: T) => void;
  historySize: number;
}

export function useHistoryReducer<T>(
  initialState: T,
  enableKeyboardShortcuts: boolean = true
): UseHistoryReducerReturn<T> {
  const [historyState, dispatch] = useReducer(historyReducer<T>, {
    past: [],
    present: initialState,
    future: []
  });

  const keyboardHandlerRef = useRef<(event: KeyboardEvent) => void | null>(null);

  const setState = useCallback((newState: T) => {
    dispatch({ type: 'SET', payload: newState });
  }, []);

  const undo = useCallback(() => {
    dispatch({ type: 'UNDO' });
  }, []);

  const redo = useCallback(() => {
    dispatch({ type: 'REDO' });
  }, []);

  const clear = useCallback((newState?: T) => {
    dispatch({ type: 'CLEAR', payload: newState });
  }, []);

  const canUndo = historyState.past.length > 0;
  const canRedo = historyState.future.length > 0;
  const historySize = historyState.past.length + 1 + historyState.future.length;

  // Keyboard shortcuts
  useEffect(() => {
    if (!enableKeyboardShortcuts) return;

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

    keyboardHandlerRef.current = handleKeyDown;
    document.addEventListener('keydown', handleKeyDown);

    return () => {
      if (keyboardHandlerRef.current) {
        document.removeEventListener('keydown', keyboardHandlerRef.current);
      }
    };
  }, [undo, redo, enableKeyboardShortcuts]);

  return {
    state: historyState.present,
    setState,
    undo,
    redo,
    canUndo,
    canRedo,
    clear,
    historySize
  };
}

export default useHistoryReducer;
