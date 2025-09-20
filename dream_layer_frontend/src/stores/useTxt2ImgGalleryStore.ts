import { create } from 'zustand';
import { ImageResult } from '@/types/imageResult';

interface Txt2ImgGalleryState {
  images: ImageResult[];
  isLoading: boolean;
  addImages: (newImages: ImageResult[]) => void;
  clearImages: () => void;
  removeImage: (id: string) => void;
  setLoading: (loading: boolean) => void;
}

export const useTxt2ImgGalleryStore = create<Txt2ImgGalleryState>((set) => ({
  images: [],
  isLoading: false,
  addImages: (newImages) => set((state) => ({
    images: [...newImages.filter(newImg => !state.images.some(img => img.url === newImg.url)), ...state.images],
    isLoading: false
  })),
  clearImages: () => set({ images: [], isLoading: false }),
  removeImage: (id) => set((state) => ({
    images: state.images.filter(img => img.id !== id)
  })),
  setLoading: (loading) => set({ isLoading: loading }),
}));
