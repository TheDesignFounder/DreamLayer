import React from "react";
import { Button } from "@/components/ui/button";
import ImageUploadButton from "./ImageUploadButton";

interface DualImageUploaderProps {
  imagePreview: string | null;
  maskPreview: string | null;
  onImageChange: (file: File) => void;
  onMaskChange: (file: File) => void;
  onImageClear: () => void;
  onMaskClear: () => void;
  onImageDrop: (e: React.DragEvent) => void;
  onMaskDrop: (e: React.DragEvent) => void;
  onDragOver: (e: React.DragEvent) => void;
}

const DualImageUploader: React.FC<DualImageUploaderProps> = ({
  imagePreview,
  maskPreview,
  onImageChange,
  onMaskChange,
  onImageClear,
  onMaskClear,
  onImageDrop,
  onMaskDrop,
  onDragOver,
}) => {
  const handleImageFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onImageChange(file);
    }
  };

  const handleMaskFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onMaskChange(file);
    }
  };

  return (
    <div className="grid grid-cols-2 gap-4">
      {/* Source Image */}
      <div className="space-y-2">
        {imagePreview ? (
          <div className="relative">
            <img
              src={imagePreview}
              alt="Source image"
              className="rounded-md object-cover w-full aspect-square border border-border"
            />
            <div className="absolute bottom-2 right-2 flex gap-1">
              <Button
                variant="outline"
                size="sm"
                className="bg-background/80 backdrop-blur-sm border-border text-foreground hover:bg-accent"
                onClick={onImageClear}
              >
                Clear
              </Button>
            </div>
          </div>
        ) : (
          <div
            className="p-4 border-2 border-dashed border-border rounded-md text-center flex flex-col items-center justify-center aspect-square bg-card"
            onDrop={onImageDrop}
            onDragOver={onDragOver}
          >
            <p className="text-muted-foreground mb-2">
              Drag & drop an image here
            </p>
            <p className="text-xs text-muted-foreground mb-4">
              PNG, JPG, WEBP or GIF
            </p>
            <ImageUploadButton onFileChange={handleImageFileChange}>
              Browse Files
            </ImageUploadButton>
          </div>
        )}
      </div>

      {/* Mask Image + Draw Mask Button */}
      <div className="space-y-2">
        <div className="flex flex-col items-center gap-2">
          <button
            type="button"
            className="draw-mask-btn px-3 py-1 rounded border border-primary text-primary bg-background hover:bg-primary/10 text-xs font-medium mb-2"
            style={{ minWidth: 100 }}
            onClick={() => alert("Draw Mask feature coming soon!")}
          >
            Draw Mask
          </button>
          {maskPreview ? (
            <div className="relative">
              <img
                src={maskPreview}
                alt="Mask image"
                className="rounded-md object-cover w-full aspect-square border border-border"
              />
              <div className="absolute bottom-2 right-2 flex gap-1">
                <Button
                  variant="outline"
                  size="sm"
                  className="bg-background/80 backdrop-blur-sm border-border text-foreground hover:bg-accent"
                  onClick={onMaskClear}
                >
                  Clear
                </Button>
              </div>
            </div>
          ) : (
            <div
              className="p-4 border-2 border-dashed border-border rounded-md text-center flex flex-col items-center justify-center aspect-square bg-card"
              onDrop={onMaskDrop}
              onDragOver={onDragOver}
            >
              <p className="text-muted-foreground mb-2">
                Drag & drop a mask here
              </p>
              <p className="text-xs text-muted-foreground mb-4">
                PNG, JPG, WEBP or GIF
              </p>
              <ImageUploadButton onFileChange={handleMaskFileChange}>
                Browse Files
              </ImageUploadButton>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DualImageUploader;
