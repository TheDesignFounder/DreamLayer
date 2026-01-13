import { create } from 'zustand';
import { VideoResult } from '@/types/generationSettings';

interface Img2VidGalleryState {
  videos: VideoResult[];
  isLoading: boolean;
  currentVideoIndex: number;

  addVideos: (videos: VideoResult[]) => void;
  removeVideo: (id: string) => void;
  clearVideos: () => void;
  setLoading: (isLoading: boolean) => void;
  setCurrentVideoIndex: (index: number) => void;
  loadFromDatabase: () => Promise<void>;
  deleteFromDatabase: (id: string) => Promise<void>;
}

const DB_NAME = 'img2vid_gallery';
const DB_VERSION = 1;
const STORE_NAME = 'videos';

// IndexedDB helper functions
const openDB = (): Promise<IDBDatabase> => {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);

    request.onupgradeneeded = (event) => {
      const db = (event.target as IDBOpenDBRequest).result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        const objectStore = db.createObjectStore(STORE_NAME, { keyPath: 'id' });
        objectStore.createIndex('timestamp', 'timestamp', { unique: false });
      }
    };
  });
};

const saveVideoToDB = async (video: VideoResult): Promise<void> => {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORE_NAME], 'readwrite');
    const store = transaction.objectStore(STORE_NAME);
    const request = store.put(video);

    request.onsuccess = () => resolve();
    request.onerror = () => reject(request.error);
  });
};

const loadVideosFromDB = async (): Promise<VideoResult[]> => {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORE_NAME], 'readonly');
    const store = transaction.objectStore(STORE_NAME);
    const request = store.getAll();

    request.onsuccess = () => {
      const videos = request.result as VideoResult[];
      // Sort by timestamp descending (newest first)
      videos.sort((a, b) => b.timestamp - a.timestamp);
      resolve(videos);
    };
    request.onerror = () => reject(request.error);
  });
};

const deleteVideoFromDB = async (id: string): Promise<void> => {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORE_NAME], 'readwrite');
    const store = transaction.objectStore(STORE_NAME);
    const request = store.delete(id);

    request.onsuccess = () => resolve();
    request.onerror = () => reject(request.error);
  });
};

export const useImg2VidGalleryStore = create<Img2VidGalleryState>((set, get) => ({
  videos: [],
  isLoading: false,
  currentVideoIndex: 0,

  addVideos: async (newVideos) => {
    // Save to IndexedDB
    for (const video of newVideos) {
      try {
        await saveVideoToDB(video);
      } catch (error) {
        console.error('Error saving video to DB:', error);
      }
    }

    set((state) => ({
      videos: [
        ...newVideos.filter(newVid => !state.videos.some(vid => vid.url === newVid.url)),
        ...state.videos
      ],
      isLoading: false,
      currentVideoIndex: 0
    }));
  },

  removeVideo: async (id) => {
    try {
      await deleteVideoFromDB(id);
    } catch (error) {
      console.error('Error deleting video from DB:', error);
    }

    set((state) => {
      const newVideos = state.videos.filter(vid => vid.id !== id);
      return {
        videos: newVideos,
        currentVideoIndex: Math.min(state.currentVideoIndex, newVideos.length - 1)
      };
    });
  },

  clearVideos: () => set({ videos: [], currentVideoIndex: 0 }),

  setLoading: (isLoading) => set({ isLoading }),

  setCurrentVideoIndex: (index) => set({ currentVideoIndex: index }),

  loadFromDatabase: async () => {
    try {
      const videos = await loadVideosFromDB();
      set({ videos });
    } catch (error) {
      console.error('Error loading videos from database:', error);
    }
  },

  deleteFromDatabase: async (id) => {
    try {
      await deleteVideoFromDB(id);
      set((state) => ({
        videos: state.videos.filter(vid => vid.id !== id)
      }));
    } catch (error) {
      console.error('Error deleting video from database:', error);
    }
  }
}));
