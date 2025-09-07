import { useTxt2ImgGalleryStore } from '@/stores/useTxt2ImgGalleryStore';
import { useImg2ImgGalleryStore } from '@/stores/useImg2ImgGalleryStore';
import { useExtrasGalleryStore } from '@/stores/useExtrasGalleryStore';

/**
 * Centralized gallery sync utility to ensure data persistence across tabs
 */
export class GallerySync {
  private static readonly BACKEND_URL = 'http://localhost:5002';

  /**
   * Sync all gallery data to backend
   */
  static async syncToBackend(): Promise<boolean> {
    try {
      // Get fresh state from all stores
      const txt2imgImages = useTxt2ImgGalleryStore.getState().images;
      const img2imgImages = useImg2ImgGalleryStore.getState().images;
      const extrasImages = useExtrasGalleryStore.getState().images;

      const galleryData = {
        txt2img: txt2imgImages,
        img2img: img2imgImages,
        extras: extrasImages
      };

      console.log('🔄 Syncing all gallery data to backend:', {
        txt2imgCount: txt2imgImages.length,
        img2imgCount: img2imgImages.length,
        extrasCount: extrasImages.length,
        totalImages: txt2imgImages.length + img2imgImages.length + extrasImages.length
      });

      const response = await fetch(`${this.BACKEND_URL}/api/gallery-data`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(galleryData)
      });

      if (response.ok) {
        console.log('✅ Gallery data synced successfully to backend');
        return true;
      } else {
        console.error('❌ Failed to sync gallery data:', response.statusText);
        return false;
      }
    } catch (error) {
      console.error('❌ Error syncing gallery data:', error);
      return false;
    }
  }

  /**
   * Fetch gallery data from backend and update all stores
   */
  static async syncFromBackend(): Promise<boolean> {
    try {
      const response = await fetch(`${this.BACKEND_URL}/api/gallery-data`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });

      if (response.ok) {
        const backendData = await response.json();
        
        // Update all stores with backend data (without triggering loading states)
        const txt2imgStore = useTxt2ImgGalleryStore.getState();
        const img2imgStore = useImg2ImgGalleryStore.getState();
        const extrasStore = useExtrasGalleryStore.getState();

        // Only update if backend has more recent data
        if (backendData.txt2img && Array.isArray(backendData.txt2img)) {
          txt2imgStore.addImages(backendData.txt2img.filter((img: any) => 
            !txt2imgStore.images.some(existing => existing.id === img.id)
          ));
        }

        if (backendData.img2img && Array.isArray(backendData.img2img)) {
          img2imgStore.addImages(backendData.img2img.filter((img: any) => 
            !img2imgStore.images.some(existing => existing.id === img.id)
          ));
        }

        if (backendData.extras && Array.isArray(backendData.extras)) {
          extrasStore.addImages(backendData.extras.filter((img: any) => 
            !extrasStore.images.some(existing => existing.id === img.id)
          ));
        }

        console.log('✅ Gallery data synced from backend to stores');
        return true;
      } else {
        console.warn('Could not fetch gallery data from backend');
        return false;
      }
    } catch (error) {
      console.error('❌ Error fetching gallery data from backend:', error);
      return false;
    }
  }

  /**
   * Add image to appropriate store and sync to backend
   */
  static async addImageAndSync(type: 'txt2img' | 'img2img' | 'extras', images: any[]): Promise<void> {
    // Add to appropriate store first
    switch (type) {
      case 'txt2img':
        useTxt2ImgGalleryStore.getState().addImages(images);
        break;
      case 'img2img':
        useImg2ImgGalleryStore.getState().addImages(images);
        break;
      case 'extras':
        useExtrasGalleryStore.getState().addImages(images);
        break;
    }

    // Wait a bit for state to update, then sync to backend
    setTimeout(async () => {
      await this.syncToBackend();
    }, 100);
  }

  /**
   * Clear all data (for after download)
   */
  static async clearAll(): Promise<void> {
    // Clear all stores
    useTxt2ImgGalleryStore.getState().clearImages();
    useImg2ImgGalleryStore.getState().clearImages();
    useExtrasGalleryStore.getState().clearImages();

    // Clear backend
    await fetch(`${this.BACKEND_URL}/api/gallery-data`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        txt2img: [],
        img2img: [],
        extras: []
      })
    });

    console.log('🧹 All gallery data cleared');
  }

  /**
   * Check if backend is fresh (empty) and sync frontend accordingly
   * This ensures fresh starts after service restarts
   */
  static async ensureFreshStart(): Promise<void> {
    try {
      // Check backend status
      const response = await fetch(`${this.BACKEND_URL}/api/reports/status`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });

      if (response.ok) {
        const backendStatus = await response.json();
        
        // If backend has no images but frontend stores have data, clear frontend
        const frontendTotal = 
          useTxt2ImgGalleryStore.getState().images.length +
          useImg2ImgGalleryStore.getState().images.length +
          useExtrasGalleryStore.getState().images.length;

        if (backendStatus.total_images === 0 && frontendTotal > 0) {
          console.log('🧹 Backend is fresh but frontend has old data - clearing frontend stores');
          useTxt2ImgGalleryStore.getState().clearImages();
          useImg2ImgGalleryStore.getState().clearImages();
          useExtrasGalleryStore.getState().clearImages();
          console.log('✅ Frontend stores cleared for fresh start');
        }
      }
    } catch (error) {
      console.warn('Could not check backend status for fresh start sync:', error);
    }
  }
}
