
import { ImageResult } from '@/types/generationSettings';

export const transferImages = (
  srcStore: { images: ImageResult[] },
  dstStore: { addImages: (images: ImageResult[]) => void },
  ids: string[]
) => {
  const imagesToTransfer = srcStore.images.filter(img => ids.includes(img.id));
  if (imagesToTransfer.length > 0) {
    dstStore.addImages(imagesToTransfer);
  }
};
