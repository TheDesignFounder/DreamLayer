import { useReducer, useCallback, useRef, useEffect, useState } from 'react';

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

export function useHistoryReducer<T>(initialState: T) {
  const [state, dispatch] = useReducer(historyReducer<T>, {
    past: [],
    present: initialState,
    future: []
  });
  
  const [currentValue, setCurrentValue] = useState<T>(initialState);
  const isSettingRef = useRef(false);
  const debounceTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const lastCommittedRef = useRef<T>(initialState);
  
  const commitToHistory = useCallback((value: T) => {
    if (JSON.stringify(value) !== JSON.stringify(lastCommittedRef.current)) {
      dispatch({ type: 'SET', payload: value });
      lastCommittedRef.current = value;
    }
  }, []);
  
  const set = useCallback((newState: T | ((prev: T) => T)) => {
    isSettingRef.current = true;
    const nextState = typeof newState === 'function' 
      ? (newState as (prev: T) => T)(currentValue)
      : newState;
    
    setCurrentValue(nextState);
    
    // Clear existing timeout
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current);
    }
    
    // Set new timeout to commit after user stops typing
    debounceTimeoutRef.current = setTimeout(() => {
      commitToHistory(nextState);
      isSettingRef.current = false;
    }, 300);
  }, [commitToHistory, currentValue]);
  
  const undo = useCallback(() => {
    // Cancel any pending commits
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current);
      debounceTimeoutRef.current = null;
    }
    dispatch({ type: 'UNDO' });
    if (state.past.length > 0) {
      const previousValue = state.past[state.past.length - 1];
      setCurrentValue(previousValue);
      lastCommittedRef.current = previousValue;
    }
  }, [state.past]);
  
  const redo = useCallback(() => {
    // Cancel any pending commits
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current);
      debounceTimeoutRef.current = null;
    }
    dispatch({ type: 'REDO' });
    if (state.future.length > 0) {
      const nextValue = state.future[0];
      setCurrentValue(nextValue);
      lastCommittedRef.current = nextValue;
    }
  }, [state.future]);
  
  const reset = useCallback((newState: T) => {
    // Cancel any pending commits
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current);
      debounceTimeoutRef.current = null;
    }
    dispatch({ type: 'RESET', payload: newState });
    setCurrentValue(newState);
    lastCommittedRef.current = newState;
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
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current);
      }
    };
  }, []);
  
  return {
    state: currentValue,
    set,
    undo,
    redo,
    reset,
    canUndo,
    canRedo,
    history: state,
    isSettingRef
  };
}