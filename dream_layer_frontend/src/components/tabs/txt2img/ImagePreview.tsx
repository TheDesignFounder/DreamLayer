import React, { useState } from 'react';
import { AspectRatio } from "@/components/ui/aspect-ratio";
import { Button } from "@/components/ui/button";
import { useTxt2ImgGalleryStore } from '@/stores/useTxt2ImgGalleryStore';
import { useImg2ImgGalleryStore } from '@/stores/useImg2ImgGalleryStore';
import { Download, FolderOpen, Copy, ChevronDown, ChevronLeft, ChevronRight } from 'lucide-react';
import JSZip from 'jszip';

interface ImagePreviewProps {
  onTabChange: (tabId: string) => void;
}

const LoadingAnimation = () => (
  <div className="animate-pulse space-y-4">
    <div className="h-full w-full bg-muted rounded-md flex items-center justify-center">
      <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
    </div>
  </div>
);

const ImagePreview: React.FC<ImagePreviewProps> = ({ onTabChange }) => {
  const { images, isLoading } = useTxt2ImgGalleryStore();
  const setInputImage = useImg2ImgGalleryStore(state => state.setInputImage);
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [outputSettingsExpanded, setOutputSettingsExpanded] = useState(true);
  const [thumbnailStartIndex, setThumbnailStartIndex] = useState(0);
  const [imageError, setImageError] = useState<string | null>(null);

  const currentImage = images[selectedImageIndex] || images[0];
  const maxThumbnails = 5;
  const totalPages = Math.ceil(images.length / maxThumbnails);
  const currentPage = Math.floor(thumbnailStartIndex / maxThumbnails) + 1;

  const isMatrixGrid = (image: any) => {
    return image?.id?.startsWith('matrix-grid') || 
           image?.id?.startsWith('matrix-subgrid');
  };

  const handleImageError = (error: React.SyntheticEvent<HTMLImageElement, Event>) => {
    console.error('Error loading image:', error);
    const img = error.target as HTMLImageElement;
    console.log('Failed image URL:', img.src);
    setImageError(`Failed to load image`);
  };

  const handleImageLoad = () => {
    setImageError(null);
  };

  const handleDownload = async (format: 'png' | 'zip') => {
    if (!currentImage) return;
    
    if (format === 'png') {
      try {
        const response = await fetch(currentImage.url);
        const blob = await response.blob();
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `generated-image-${currentImage.id}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        URL.revokeObjectURL(link.href);
      } catch (error) {
        console.error('Download failed:', error);
        const link = document.createElement('a');
        link.href = currentImage.url;
        link.target = '_blank';
        link.download = `generated-image-${currentImage.id}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    } else if (format === 'zip') {
      const zip = new JSZip();
      const promises = images.map(async (image, index) => {
        try {
          const response = await fetch(image.url);
          const blob = await response.blob();
          zip.file(`generated-image-${index + 1}.png`, blob);
        } catch (error) {
          console.error(`Failed to fetch image ${index + 1}:`, error);
        }
      });
      
      await Promise.all(promises);
      const zipBlob = await zip.generateAsync({type: 'blob'});
      
      const link = document.createElement('a');
      link.href = URL.createObjectURL(zipBlob);
      link.target = '_blank';
      link.download = 'generated-images.zip';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      URL.revokeObjectURL(link.href);
    }
  };

  const handleShowInFolder = async () => {
    if (!currentImage) return;
    
    try {
      let filename: string | null = null;
      
      if (isMatrixGrid(currentImage)) {
        const url = new URL(currentImage.url);
        filename = url.pathname.split('/').pop();
      } else {
        const url = new URL(currentImage.url);
        filename = url.searchParams.get('filename') || url.pathname.split('/').pop();
      }
      
      if (!filename) {
        console.error('No filename found in URL:', currentImage.url);
        return;
      }
      
      console.log('=== Show in Folder Debug ===');
      console.log('Full URL:', currentImage.url);
      console.log('Extracted filename:', filename);
      console.log('Request body:', JSON.stringify({ filename }));
      
      const response = await fetch('http://localhost:5002/api/show-in-folder', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename })
      });
      
      const result = await response.json();
      console.log(result.message);
    } catch (error) {
      console.error('Error opening folder:', error);
    }
  };

  const handleSendTo = async (destination: 'img2img' | 'inpaint' | 'extras') => {
    if (!currentImage) return;
    
    if (destination === 'img2img') {
      try {
        let filename: string | null = null;
        
        if (isMatrixGrid(currentImage)) {
          const url = new URL(currentImage.url);
          filename = url.pathname.split('/').pop();
        } else {
          const url = new URL(currentImage.url);
          filename = url.searchParams.get('filename') || url.pathname.split('/').pop();
        }
        
        if (!filename) {
          console.error('No filename found in URL:', currentImage.url);
          return;
        }

        const response = await fetch('http://localhost:5002/api/send-to-img2img', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ filename })
        });
        
        const result = await response.json();
        if (result.status === 'success') {
          const imageUrl = `http://localhost:5001/api/images/${filename}`;
          const imageBlob = await fetch(imageUrl).then(r => r.blob());
          setInputImage({
            url: imageUrl,
            file: new File([imageBlob], filename)
          });
          
          onTabChange('img2img');
        }
      } catch (error) {
        console.error('Error sending to img2img:', error);
      }
    } else if (destination === 'extras') {
      try {
        let filename: string | null = null;
        
        if (isMatrixGrid(currentImage)) {
          const url = new URL(currentImage.url);
          filename = url.pathname.split('/').pop();
        } else {
          const url = new URL(currentImage.url);
          filename = url.searchParams.get('filename') || url.pathname.split('/').pop();
        }
        
        if (!filename) {
          console.error('No filename found in URL:', currentImage.url);
          return;
        }

        const response = await fetch('http://localhost:5002/api/send-to-extras', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ filename })
        });
        
        const result = await response.json();
        if (result.status === 'success') {
          const imageUrl = `http://localhost:5001/api/images/${filename}`;
          const imageBlob = await fetch(imageUrl).then(r => r.blob());
          const file = new File([imageBlob], filename);
          
          window.sessionStorage.setItem('extrasImage', JSON.stringify({
            file: {
              name: filename,
              size: imageBlob.size,
              type: imageBlob.type
            },
            preview: imageUrl
          }));
          
          onTabChange('extras');
        }
      } catch (error) {
        console.error('Error sending to extras:', error);
      }
    } else {
      // TODO: Implement other destinations
      console.log(`Sending to ${destination}:`, currentImage);
    }
  };

  const handleCopyOutputSettings = () => {
    if (!currentImage?.settings) return;
    
    const settingsText = JSON.stringify(currentImage.settings, null, 2);
    navigator.clipboard.writeText(settingsText);
  };

  const handlePrevThumbnails = () => {
    setThumbnailStartIndex(Math.max(0, thumbnailStartIndex - maxThumbnails));
  };

  const handleNextThumbnails = () => {
    const newStartIndex = thumbnailStartIndex + maxThumbnails;
    if (newStartIndex < images.length) {
      setThumbnailStartIndex(newStartIndex);
    }
  };

  const handleThumbnailClick = (index: number) => {
    const actualIndex = thumbnailStartIndex + index;
    setSelectedImageIndex(actualIndex);
    setImageError(null);
  };

  const formatSettingsDisplay = () => {
    if (!currentImage?.settings) return 'No settings available';
    
    const settings = currentImage.settings;
    const settingsAny = settings as any;
    
    const isMatrix = isMatrixGrid(currentImage);
    
    if (isMatrix && settingsAny.isMatrixGrid) {
      let matrixInfo = `Matrix Grid Generation

Prompt: ${currentImage.prompt || 'N/A'}

Negative prompt: ${currentImage.negativePrompt || 'N/A'}

Base Settings:
Steps: ${settings.steps || 'N/A'}
Sampler: ${settings.sampler_name || 'N/A'}
CFG scale: ${settings.cfg_scale || 'N/A'}
Size: ${settings.width || 'N/A'}x${settings.height || 'N/A'}
Model: ${settings.model_name || 'N/A'}
`;

      if (settingsAny.matrixAxes) {
        matrixInfo += '\nMatrix Configuration:\n';
        
        if (settingsAny.matrixAxes.xAxis) {
          matrixInfo += `X-Axis (${settingsAny.matrixAxes.xAxis.name}): ${settingsAny.matrixAxes.xAxis.values.join(', ')}\n`;
        }
        
        if (settingsAny.matrixAxes.yAxis) {
          matrixInfo += `Y-Axis (${settingsAny.matrixAxes.yAxis.name}): ${settingsAny.matrixAxes.yAxis.values.join(', ')}\n`;
        }
        
        if (settingsAny.matrixAxes.zAxis) {
          matrixInfo += `Z-Axis (${settingsAny.matrixAxes.zAxis.name}): ${settingsAny.matrixAxes.zAxis.values.join(', ')}\n`;
        }
      }
      
      if (settingsAny.totalJobs) {
        matrixInfo += `\nTotal Jobs: ${settingsAny.totalJobs}`;
      }
      
      if (settingsAny.matrixSettings) {
        matrixInfo += `\nMatrix Options:
Draw Legend: ${settingsAny.matrixSettings.drawLegend ? 'Yes' : 'No'}
Keep Seeds Consistent: ${settingsAny.matrixSettings.keepSeedsConsistent ? 'Yes' : 'No'}
Include Sub Images: ${settingsAny.matrixSettings.includeSubImages ? 'Yes' : 'No'}
Include Sub Grids: ${settingsAny.matrixSettings.includeSubgrids ? 'Yes' : 'No'}`;
      }
      
      return matrixInfo;
    } else {
      return `Prompt: ${currentImage.prompt || 'N/A'}

Negative prompt: ${currentImage.negativePrompt || 'N/A'}

Steps: ${settings.steps || 'N/A'}
Sampler: ${settings.sampler_name || 'N/A'}
CFG scale: ${settings.cfg_scale || 'N/A'}
Seed: ${settings.seed || 'N/A'}
Size: ${settings.width || 'N/A'}x${settings.height || 'N/A'}
Model hash: ${settingsAny.model_hash || 'N/A'}
Model: ${settings.model_name || 'N/A'}
Denoising strength: ${settings.denoising_strength || 'N/A'}
Version: v1.6.0
Networks not found: add-detail-xl, Double_Exposure
Time taken: 31.1 sec.`;
    }
  };

  const renderImageContainer = () => {
    if (!currentImage) return null;

    const isMatrix = isMatrixGrid(currentImage);
    
    if (isMatrix) {
      return (
        <div className="relative w-full">
          <div 
            className="w-full overflow-x-auto overflow-y-hidden bg-card border border-border rounded-md"
            style={{ 
              height: '300px',
            }}
          >
            <div className="flex items-center justify-center h-full p-2">
              <img 
                src={currentImage.url} 
                alt="Matrix Grid" 
                className="max-w-none h-auto object-contain"
                style={{ 
                  height: '280px',
                }}
                onError={handleImageError}
                onLoad={handleImageLoad}
              />
            </div>
          </div>
          
          {imageError && (
            <div className="absolute bottom-0 left-0 right-0 bg-red-500/80 text-white p-2 text-sm text-center rounded-b-md">
              {imageError}
            </div>
          )}
          
        </div>
      );
    } else {
      return (
        <AspectRatio ratio={1} className="w-full">
          <div className="flex h-full w-full flex-col items-center justify-center rounded-md border border-border bg-card p-4">
            <div className="w-full h-full relative">
              <img 
                src={currentImage.url} 
                alt="Generated image" 
                className="w-full h-full object-cover rounded-md"
                onError={handleImageError}
                onLoad={handleImageLoad}
              />
              {imageError && (
                <div className="absolute bottom-0 left-0 right-0 bg-red-500/80 text-white p-2 text-sm text-center rounded-b-md">
                  {imageError}
                </div>
              )}
            </div>
          </div>
        </AspectRatio>
      );
    }
  };

  return (
    <div className="space-y-4">
      {isLoading ? (
        <AspectRatio ratio={1} className="w-full">
          <div className="flex h-full w-full flex-col items-center justify-center rounded-md border border-border bg-card p-4">
            <LoadingAnimation />
          </div>
        </AspectRatio>
      ) : images.length > 0 && currentImage ? (
        renderImageContainer()
      ) : (
        <AspectRatio ratio={1} className="w-full">
          <div className="flex h-full w-full flex-col items-center justify-center rounded-md border border-border bg-card p-4">
            <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-md bg-secondary">
              <svg
                viewBox="0 0 24 24"
                className="h-6 w-6 text-muted-foreground"
                fill="none"
                stroke="currentColor"
                xmlns="http://www.w3.org/2000/svg"
              >
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                <circle cx="8.5" cy="8.5" r="1.5" />
                <path d="m21 15-5-5L5 21" />
              </svg>
            </div>
            <p className="text-sm text-muted-foreground">Generated Images Will Display Here</p>
          </div>
        </AspectRatio>
      )}

      {images.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-center gap-2 px-4">
            {images.length > maxThumbnails && (
              <Button
                variant="ghost"
                size="sm"
                className="h-16 w-8 p-0 hover:bg-accent"
                onClick={handlePrevThumbnails}
                disabled={thumbnailStartIndex === 0}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
            )}

            <div className="flex gap-2">
              {images.slice(thumbnailStartIndex, thumbnailStartIndex + maxThumbnails).map((image, index) => {
                const actualIndex = thumbnailStartIndex + index;
                const isMatrix = isMatrixGrid(image);
                
                return (
                  <button
                    key={image.id}
                    onClick={() => handleThumbnailClick(index)}
                    className={`relative w-16 h-16 rounded border-2 transition-colors overflow-hidden ${
                      actualIndex === selectedImageIndex 
                        ? 'border-primary' 
                        : 'border-border hover:border-primary/50'
                    }`}
                  >
                    <img 
                      src={image.url} 
                      alt={`Generated image ${actualIndex + 1}`}
                      className={`w-full h-full ${isMatrix ? 'object-contain bg-muted' : 'object-cover'}`}
                      onError={(e) => {
                        const img = e.target as HTMLImageElement;
                        img.style.display = 'none';
                      }}
                    />
                  </button>
                );
              })}
              
              {images.slice(thumbnailStartIndex, thumbnailStartIndex + maxThumbnails).length < maxThumbnails && 
               thumbnailStartIndex + maxThumbnails >= images.length &&
               Array.from({ 
                 length: maxThumbnails - images.slice(thumbnailStartIndex, thumbnailStartIndex + maxThumbnails).length 
               }).map((_, index) => (
                <div 
                  key={`empty-${index}`}
                  className="w-16 h-16 rounded bg-muted/50"
                />
              ))}
            </div>

            {images.length > maxThumbnails && (
              <Button
                variant="ghost"
                size="sm"
                className="h-16 w-8 p-0 hover:bg-accent"
                onClick={handleNextThumbnails}
                disabled={thumbnailStartIndex + maxThumbnails >= images.length}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            )}
          </div>

          {images.length > maxThumbnails && (
            <div className="flex justify-center">
              <div className="text-xs text-muted-foreground bg-muted px-2 py-1 rounded">
                {currentPage} / {totalPages}
              </div>
            </div>
          )}
        </div>
      )}

      {images.length > 0 && currentImage && !imageError && (
        <div className="space-y-4 px-4">
          <div>
            <div className="flex items-center flex-wrap gap-2">
              <span className="text-sm font-medium">Download:</span>
              <Button 
                variant="outline" 
                size="sm" 
                className="text-xs h-8"
                onClick={() => handleDownload('png')}
              >
                <Download className="w-3 h-3 mr-1" />
                PNG
              </Button>
              {false && <Button 
                variant="outline" 
                size="sm" 
                className="text-xs h-8"
                onClick={() => handleDownload('zip')}
              >
                <Download className="w-3 h-3 mr-1" />
                ZIP
              </Button>}
              <Button 
                variant="outline" 
                size="sm" 
                className="text-xs h-8"
                onClick={handleShowInFolder}
              >
                <FolderOpen className="w-3 h-3 mr-1" />
                Show in Folder
              </Button>
            </div>
          </div>

          <div>
            <div className="flex items-center flex-wrap gap-2">
              <span className="text-sm font-medium">Send To:</span>
              <Button 
                variant="outline" 
                size="sm" 
                className="text-xs h-8"
                onClick={() => handleSendTo('img2img')}
              >
                Img2Img
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                className="text-xs h-8"
                onClick={() => handleSendTo('inpaint')}
              >
                Inpaint
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                className="text-xs h-8"
                onClick={() => handleSendTo('extras')}
              >
                Extras
              </Button>
            </div>
          </div>

          {/* Divider */}
          <div className="border-t border-border"></div>

          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-medium">Output Settings</span>
              <div className="flex items-center gap-2">
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="text-xs h-8"
                  onClick={handleCopyOutputSettings}
                >
                  <Copy className="w-3 h-3 mr-1" />
                  Copy Output Settings
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-8 w-8 p-0"
                  onClick={() => setOutputSettingsExpanded(!outputSettingsExpanded)}
                >
                  <ChevronDown className={`w-4 h-4 transition-transform ${outputSettingsExpanded ? 'rotate-180' : ''}`} />
                </Button>
              </div>
            </div>
            
            {outputSettingsExpanded && (
              <div className="bg-muted p-3 rounded-md text-xs leading-relaxed">
                {(() => {
                  const isMatrix = isMatrixGrid(currentImage);
                  const settingsAny = currentImage.settings as any;
                  
                  if (isMatrix && settingsAny?.isMatrixGrid) {
                    return (
                      <div className="space-y-3">
                        <div>
                          <div className="font-semibold mb-1">Type:</div>
                          <div className="text-muted-foreground">Matrix Grid Generation</div>
                        </div>
                        
                        <div>
                          <div className="font-semibold mb-1">Prompt:</div>
                          <div className="text-muted-foreground break-words">{currentImage.prompt || 'N/A'}</div>
                        </div>
                        
                        <div>
                          <div className="font-semibold mb-1">Negative prompt:</div>
                          <div className="text-muted-foreground break-words">{currentImage.negativePrompt || 'N/A'}</div>
                        </div>
                        
                        <div className="border-t pt-3">
                          <div className="font-semibold mb-2">Base Settings:</div>
                          <div className="space-y-2">
                            <div><strong>Steps:</strong> {currentImage.settings?.steps || 'N/A'}</div>
                            <div><strong>Sampler:</strong> {currentImage.settings?.sampler_name || 'N/A'}</div>
                            <div><strong>CFG scale:</strong> {currentImage.settings?.cfg_scale || 'N/A'}</div>
                            <div><strong>Size:</strong> {currentImage.settings?.width || 'N/A'}x{currentImage.settings?.height || 'N/A'}</div>
                            <div><strong>Model:</strong> {currentImage.settings?.model_name || 'N/A'}</div>
                            {currentImage.settings?.denoising_strength && (
                              <div><strong>Denoising strength:</strong> {currentImage.settings.denoising_strength}</div>
                            )}
                          </div>
                        </div>
                        
                        {settingsAny.matrixAxes && (
                          <div className="border-t pt-3">
                            <div className="font-semibold mb-2">Matrix Configuration:</div>
                            <div className="space-y-1">
                              {settingsAny.matrixAxes.xAxis && (
                                <div><strong>X-Axis ({settingsAny.matrixAxes.xAxis.name}):</strong> {settingsAny.matrixAxes.xAxis.values.join(', ')}</div>
                              )}
                              {settingsAny.matrixAxes.yAxis && (
                                <div><strong>Y-Axis ({settingsAny.matrixAxes.yAxis.name}):</strong> {settingsAny.matrixAxes.yAxis.values.join(', ')}</div>
                              )}
                              {settingsAny.matrixAxes.zAxis && (
                                <div><strong>Z-Axis ({settingsAny.matrixAxes.zAxis.name}):</strong> {settingsAny.matrixAxes.zAxis.values.join(', ')}</div>
                              )}
                            </div>
                          </div>
                        )}
                        
                        {settingsAny.totalJobs && (
                          <div className="border-t pt-3">
                            <div><strong>Total Jobs:</strong> {settingsAny.totalJobs}</div>
                          </div>
                        )}
                        
                        {settingsAny.matrixSettings && (
                          <div className="border-t pt-3">
                            <div className="font-semibold mb-2">Matrix Options:</div>
                            <div className="space-y-1">
                              <div><strong>Draw Legend:</strong> {settingsAny.matrixSettings.drawLegend ? 'Yes' : 'No'}</div>
                              <div><strong>Keep Seeds Consistent:</strong> {settingsAny.matrixSettings.keepSeedsConsistent ? 'Yes' : 'No'}</div>
                              <div><strong>Include Sub Images:</strong> {settingsAny.matrixSettings.includeSubImages ? 'Yes' : 'No'}</div>
                              <div><strong>Include Sub Grids:</strong> {settingsAny.matrixSettings.includeSubgrids ? 'Yes' : 'No'}</div>
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  } else {
                    return (
                      <div className="space-y-3">
                        <div>
                          <div className="font-semibold mb-1">Prompt:</div>
                          <div className="text-muted-foreground break-words">{currentImage.prompt || 'N/A'}</div>
                        </div>
                        
                        <div>
                          <div className="font-semibold mb-1">Negative prompt:</div>
                          <div className="text-muted-foreground break-words">{currentImage.negativePrompt || 'N/A'}</div>
                        </div>
                        
                        <div className="space-y-2">
                          <div><strong>Steps:</strong> {currentImage.settings?.steps || 'N/A'}</div>
                          <div><strong>Sampler:</strong> {currentImage.settings?.sampler_name || 'N/A'}</div>
                          <div><strong>CFG scale:</strong> {currentImage.settings?.cfg_scale || 'N/A'}</div>
                          <div><strong>Seed:</strong> {currentImage.settings?.seed || 'N/A'}</div>
                          <div><strong>Size:</strong> {currentImage.settings?.width || 'N/A'}x{currentImage.settings?.height || 'N/A'}</div>
                          <div><strong>Model:</strong> {currentImage.settings?.model_name || 'N/A'}</div>
                          {currentImage.settings?.denoising_strength && (
                            <div><strong>Denoising strength:</strong> {currentImage.settings.denoising_strength}</div>
                          )}
                        </div>
                      </div>
                    );
                  }
                })()}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ImagePreview; 