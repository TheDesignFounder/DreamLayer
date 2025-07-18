import { useReducer, useCallback, useRef, useEffect } from 'react';

type HistoryState<T> = {
  past: T[];
  present: T;
  future: T[];
};

type HistoryAction<T> =
  | { type: 'SET'; payload: T }
  | { type: 'UNDO' }
  | { type: 'REDO' }
  | { type: 'RESET'; payload: T };

const MAX_HISTORY_SIZE = 25;

function historyReducer<T>(state: HistoryState<T>, action: HistoryAction<T>): HistoryState<T> {
  switch (action.type) {
    case 'SET': {
      const { past, present } = state;
      const newPast = [...past, present].slice(-MAX_HISTORY_SIZE);
      
      return {
        past: newPast,
        present: action.payload,
        future: []
      };
    }
    
    case 'UNDO': {
      const { past, present, future } = state;
      
      if (past.length === 0) {
        return state;
      }
      
      const newPresent = past[past.length - 1];
      const newPast = past.slice(0, -1);
      
      return {
        past: newPast,
        present: newPresent,
        future: [present, ...future]
      };
    }
    
    case 'REDO': {
      const { past, present, future } = state;
      
      if (future.length === 0) {
        return state;
      }
      
      const newPresent = future[0];
      const newFuture = future.slice(1);
      
      return {
        past: [...past, present].slice(-MAX_HISTORY_SIZE),
        present: newPresent,
        future: newFuture
      };
    }
    
    case 'RESET': {
      return {
        past: [],
        present: action.payload,
        future: []
      };
    }
    
    default:
      return state;
  }
}

export function useHistoryReducerWithDebounce<T>(initialState: T, debounceMs: number = 500) {
  const [state, dispatch] = useReducer(historyReducer<T>, {
    past: [],
    present: initialState,
    future: []
  });
  
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pendingValueRef = useRef<T | null>(null);
  const lastSavedValueRef = useRef<T>(initialState);
  
  const commitToHistory = useCallback((value: T) => {
    // Only commit if value actually changed from last saved
    if (JSON.stringify(value) !== JSON.stringify(lastSavedValueRef.current)) {
      dispatch({ type: 'SET', payload: value });
      lastSavedValueRef.current = value;
    }
  }, []);
  
  const set = useCallback((newState: T | ((prev: T) => T)) => {
    const nextState = typeof newState === 'function' 
      ? (newState as (prev: T) => T)(pendingValueRef.current || state.present)
      : newState;
    
    pendingValueRef.current = nextState;
    
    // Clear existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    
    // Set new timeout
    timeoutRef.current = setTimeout(() => {
      if (pendingValueRef.current !== null) {
        commitToHistory(pendingValueRef.current);
        pendingValueRef.current = null;
      }
    }, debounceMs);
    
    // Update state immediately for UI responsiveness
    dispatch({ type: 'SET', payload: nextState });
  }, [state.present, commitToHistory, debounceMs]);
  
  const undo = useCallback(() => {
    // Cancel any pending updates
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    pendingValueRef.current = null;
    
    dispatch({ type: 'UNDO' });
    lastSavedValueRef.current = state.past[state.past.length - 1] || initialState;
  }, [state.past, initialState]);
  
  const redo = useCallback(() => {
    // Cancel any pending updates
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    pendingValueRef.current = null;
    
    dispatch({ type: 'REDO' });
    lastSavedValueRef.current = state.future[0] || state.present;
  }, [state.future, state.present]);
  
  const reset = useCallback((newState: T) => {
    // Cancel any pending updates
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    pendingValueRef.current = null;
    
    dispatch({ type: 'RESET', payload: newState });
    lastSavedValueRef.current = newState;
  }, []);
  
  const canUndo = state.past.length > 0;
  const canRedo = state.future.length > 0;
  
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && !e.shiftKey) {
        if (e.key === 'z' || e.key === 'Z') {
          e.preventDefault();
          if (canUndo) undo();
        } else if (e.key === 'y' || e.key === 'Y') {
          e.preventDefault();
          if (canRedo) redo();
        }
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [canUndo, canRedo, undo, redo]);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);
  
  return {
    state: state.present,
    set,
    undo,
    redo,
    reset,
    canUndo,
    canRedo,
    history: state
  };
}