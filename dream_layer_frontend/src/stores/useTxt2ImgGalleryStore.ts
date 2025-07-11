import { create } from 'zustand';
import { ImageResult } from '@/types/imageResult';
import { useImageHistoryStore } from './useImageHistoryStore';

interface Txt2ImgGalleryState {
  images: ImageResult[];
  isLoading: boolean;
  addImages: (newImages: ImageResult[]) => void;
  clearImages: () => void;
  removeImage: (id: string) => void;
  setLoading: (loading: boolean) => void;
}

export const useTxt2ImgGalleryStore = create<Txt2ImgGalleryState>((set, get) => ({
  images: [],
  isLoading: false,
  addImages: (newImages) => {
    set((state) => ({
      images: [...newImages, ...state.images],
      isLoading: false
    }));
    
    // Add to history store
    const { addTxt2ImgToHistory } = useImageHistoryStore.getState();
    addTxt2ImgToHistory(newImages);
  },
  clearImages: () => set({ images: [], isLoading: false }),
  removeImage: (id) => set((state) => ({
    images: state.images.filter(img => img.id !== id)
  })),
  setLoading: (loading) => set({ isLoading: loading }),
}));
