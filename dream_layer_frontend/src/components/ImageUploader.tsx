import React from "react";
import SingleImageUploader from "./SingleImageUploader";
import DualImageUploader from "./DualImageUploader";
import { useImg2ImgGalleryStore } from "@/stores/useImg2ImgGalleryStore";
import { useState } from "react";

interface ImageUploaderProps {
  activeImg2ImgTool?: string;
}

const ImageUploader = ({
  activeImg2ImgTool = "img2img",
}: ImageUploaderProps) => {
  const {
    inputImage,
    setInputImage,
    maskFile,
    maskPreview,
    setMaskFile,
    setMaskPreview,
  } = useImg2ImgGalleryStore();
  const [maskError, setMaskError] = useState<string | null>(null);

  const handleImageChange = (file: File) => {
    const url = URL.createObjectURL(file);
    setInputImage({ url, file });
  };

  const handleMaskChange = (file: File) => {
    setMaskError(null);
    // Validate PNG
    if (file.type !== "image/png") {
      setMaskError("Only PNG files are accepted.");
      setMaskFile(null);
      setMaskPreview(null);
      return;
    }
    // Validate size <= 10MB
    if (file.size > 10 * 1024 * 1024) {
      setMaskError("File size must be 10 MB or less.");
      setMaskFile(null);
      setMaskPreview(null);
      return;
    }
    // Generate 128px thumbnail
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new window.Image();
      img.onload = () => {
        // Create canvas for 128px thumbnail
        const canvas = document.createElement("canvas");
        canvas.width = 128;
        canvas.height = 128;
        const ctx = canvas.getContext("2d");
        if (ctx) {
          ctx.fillStyle = "black";
          ctx.fillRect(0, 0, 128, 128);
          // Fit image into 128x128, preserving aspect ratio
          let w = img.width;
          let h = img.height;
          let scale = Math.min(128 / w, 128 / h);
          let nw = w * scale;
          let nh = h * scale;
          let nx = (128 - nw) / 2;
          let ny = (128 - nh) / 2;
          ctx.drawImage(img, nx, ny, nw, nh);
          setMaskPreview(canvas.toDataURL("image/png"));
        } else {
          setMaskPreview(e.target?.result as string);
        }
        setMaskFile(file);
      };
      img.onerror = () => {
        setMaskError("Failed to load image.");
        setMaskFile(null);
        setMaskPreview(null);
      };
      img.src = e.target?.result as string;
    };
    reader.onerror = () => {
      setMaskError("Failed to read file.");
      setMaskFile(null);
      setMaskPreview(null);
    };
    reader.readAsDataURL(file);
  };

  const handleImageDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file) {
      handleImageChange(file);
    }
  };

  const handleMaskDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file) {
      handleMaskChange(file);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const getButtonLabel = () => {
    switch (activeImg2ImgTool) {
      case "img2img":
        return "Send to inpaint";
      case "inpaint":
        return "Send to img2img";
      default:
        return "Send to img2img";
    }
  };

  const shouldShowButton = () => {
    return activeImg2ImgTool !== "inpaint-upload";
  };

  const handleClearImage = () => {
    if (inputImage?.url) {
      URL.revokeObjectURL(inputImage.url);
    }
    setInputImage(null);
  };

  const handleClearMask = () => {
    if (maskPreview) {
      URL.revokeObjectURL(maskPreview);
    }
    setMaskFile(null);
    setMaskPreview(null);
    setMaskError(null);
  };

  return (
    <div className="mb-4">
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-sm font-bold text-primary">0. Upload Image</h4>
        {false && shouldShowButton() && (
          <button className="text-xs rounded-md border border-input bg-background px-2 py-1 text-foreground hover:bg-accent hover:text-accent-foreground">
            {getButtonLabel()}
          </button>
        )}
      </div>
      {activeImg2ImgTool === "inpaint-upload" ||
      activeImg2ImgTool === "inpaint" ? (
        <DualImageUploader
          imagePreview={inputImage?.url || null}
          maskPreview={maskPreview}
          onImageChange={handleImageChange}
          onMaskChange={handleMaskChange}
          onImageClear={handleClearImage}
          onMaskClear={handleClearMask}
          onImageDrop={handleImageDrop}
          onMaskDrop={handleMaskDrop}
          onDragOver={handleDragOver}
        />
      ) : (
        <SingleImageUploader
          onDrop={handleImageDrop}
          onDragOver={handleDragOver}
        />
      )}
      {maskError && (
        <div className="text-red-500 text-xs mt-2">{maskError}</div>
      )}
    </div>
  );
};

export default ImageUploader;
