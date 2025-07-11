import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { ImageResult } from '@/types/imageResult';

interface ImageHistoryState {
  txt2imgHistory: ImageResult[];
  img2imgHistory: ImageResult[];
  maxHistorySize: number;
  
  // Actions
  addTxt2ImgToHistory: (images: ImageResult[]) => void;
  addImg2ImgToHistory: (images: ImageResult[]) => void;
  removeFromHistory: (type: 'txt2img' | 'img2img', id: string) => void;
  clearHistory: (type: 'txt2img' | 'img2img') => void;
  clearAllHistory: () => void;
  setMaxHistorySize: (size: number) => void;
  
  // Getters
  getTxt2ImgHistory: () => ImageResult[];
  getImg2ImgHistory: () => ImageResult[];
  getAllHistory: () => { type: 'txt2img' | 'img2img'; images: ImageResult[] }[];
  getHistoryCount: () => { txt2img: number; img2img: number; total: number };
}

export const useImageHistoryStore = create<ImageHistoryState>()(
  persist(
    (set, get) => ({
      txt2imgHistory: [],
      img2imgHistory: [],
      maxHistorySize: 500, // Default max history size
      
      addTxt2ImgToHistory: (images) => set((state) => {
        const newHistory = [...images, ...state.txt2imgHistory];
        // Keep only the most recent images within limit
        const trimmedHistory = newHistory.slice(0, state.maxHistorySize);
        return { txt2imgHistory: trimmedHistory };
      }),
      
      addImg2ImgToHistory: (images) => set((state) => {
        const newHistory = [...images, ...state.img2imgHistory];
        // Keep only the most recent images within limit
        const trimmedHistory = newHistory.slice(0, state.maxHistorySize);
        return { img2imgHistory: trimmedHistory };
      }),
      
      removeFromHistory: (type, id) => set((state) => {
        if (type === 'txt2img') {
          return {
            txt2imgHistory: state.txt2imgHistory.filter(img => img.id !== id)
          };
        } else {
          return {
            img2imgHistory: state.img2imgHistory.filter(img => img.id !== id)
          };
        }
      }),
      
      clearHistory: (type) => set((state) => {
        if (type === 'txt2img') {
          return { txt2imgHistory: [] };
        } else {
          return { img2imgHistory: [] };
        }
      }),
      
      clearAllHistory: () => set({
        txt2imgHistory: [],
        img2imgHistory: []
      }),
      
      setMaxHistorySize: (size) => set((state) => {
        // Trim existing history if new size is smaller
        const trimmedTxt2Img = state.txt2imgHistory.slice(0, size);
        const trimmedImg2Img = state.img2imgHistory.slice(0, size);
        return {
          maxHistorySize: size,
          txt2imgHistory: trimmedTxt2Img,
          img2imgHistory: trimmedImg2Img
        };
      }),
      
      getTxt2ImgHistory: () => get().txt2imgHistory,
      getImg2ImgHistory: () => get().img2imgHistory,
      
      getAllHistory: () => {
        const state = get();
        return [
          { type: 'txt2img' as const, images: state.txt2imgHistory },
          { type: 'img2img' as const, images: state.img2imgHistory }
        ];
      },
      
      getHistoryCount: () => {
        const state = get();
        return {
          txt2img: state.txt2imgHistory.length,
          img2img: state.img2imgHistory.length,
          total: state.txt2imgHistory.length + state.img2imgHistory.length
        };
      }
    }),
    {
      name: 'image-history-storage',
      version: 1,
      // Only persist the history data, not functions
      partialize: (state) => ({
        txt2imgHistory: state.txt2imgHistory,
        img2imgHistory: state.img2imgHistory,
        maxHistorySize: state.maxHistorySize
      })
    }
  )
);