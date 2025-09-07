import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { ImageResult } from '@/types/generationSettings';

interface ExtrasGalleryState {
  images: ImageResult[];
  isLoading: boolean;
  addImages: (newImages: ImageResult[]) => void;
  clearImages: () => void;
  removeImage: (id: string) => void;
  setLoading: (loading: boolean) => void;
}

export const useExtrasGalleryStore = create<ExtrasGalleryState>()(
  persist(
    (set) => ({
      images: [],
      isLoading: false,
      addImages: (newImages) => set((state) => ({
        images: [...newImages, ...state.images],
        isLoading: false
      })),
      clearImages: () => set({ images: [], isLoading: false }),
      removeImage: (id) => set((state) => ({
        images: state.images.filter(img => img.id !== id)
      })),
      setLoading: (loading) => set({ isLoading: loading }),
    }),
    {
      name: 'extras-gallery-storage',
      partialize: (state) => ({ images: state.images }), // Only persist images, not loading state
    }
  )
);
