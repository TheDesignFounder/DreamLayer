import React, { useState } from 'react';
import { ImageResult } from '@/types/imageResult';
import { AspectRatio } from '@/components/ui/aspect-ratio';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { 
  Download, 
  Copy, 
  Calendar, 
  Settings, 
  Image as ImageIcon,
  ChevronLeft,
  ChevronRight,
  X,
  Filter,
  Search
} from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface ImageHistoryGalleryProps {
  images: ImageResult[];
  onRemoveImage: (id: string) => void;
  onClearAll: () => void;
  onSendToImg2Img?: (image: ImageResult) => void;
  type: 'txt2img' | 'img2img';
}

interface ImageDetailsModalProps {
  image: ImageResult;
  isOpen: boolean;
  onClose: () => void;
  onRemove: (id: string) => void;
  onSendToImg2Img?: (image: ImageResult) => void;
}

const formatDate = (timestamp: number) => {
  return new Date(timestamp).toLocaleString();
};

const formatSettings = (settings: Record<string, any>) => {
  const exclude = ['prompt', 'negative_prompt', 'model_name', 'custom_workflow'];
  return Object.entries(settings)
    .filter(([key]) => !exclude.includes(key))
    .map(([key, value]) => ({
      key: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      value: typeof value === 'object' ? JSON.stringify(value) : String(value)
    }));
};

const ImageDetailsModal: React.FC<ImageDetailsModalProps> = ({
  image,
  isOpen,
  onClose,
  onRemove,
  onSendToImg2Img
}) => {
  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = image.url;
    link.download = `image-${image.id}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleCopyPrompt = () => {
    const text = `Prompt: ${image.prompt}${image.negativePrompt ? `\nNegative: ${image.negativePrompt}` : ''}`;
    navigator.clipboard.writeText(text);
  };

  const settings = image.settings ? formatSettings(image.settings) : [];

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-hidden">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <span>Image Details</span>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </DialogTitle>
        </DialogHeader>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Image Display */}
          <div className="space-y-4">
            <AspectRatio ratio={1} className="bg-muted rounded-lg overflow-hidden">
              <img 
                src={image.url} 
                alt="Generated image"
                className="w-full h-full object-cover"
              />
            </AspectRatio>
            
            <div className="flex gap-2">
              <Button onClick={handleDownload} size="sm" className="flex-1">
                <Download className="h-4 w-4 mr-2" />
                Download
              </Button>
              <Button onClick={handleCopyPrompt} variant="outline" size="sm" className="flex-1">
                <Copy className="h-4 w-4 mr-2" />
                Copy Prompt
              </Button>
              {onSendToImg2Img && (
                <Button 
                  onClick={() => onSendToImg2Img(image)} 
                  variant="outline" 
                  size="sm"
                  className="flex-1"
                >
                  <ImageIcon className="h-4 w-4 mr-2" />
                  To Img2Img
                </Button>
              )}
            </div>
          </div>
          
          {/* Metadata */}
          <ScrollArea className="h-[500px]">
            <div className="space-y-4">
              {/* Basic Info */}
              <div>
                <h4 className="font-medium mb-2 flex items-center">
                  <Calendar className="h-4 w-4 mr-2" />
                  Generation Info
                </h4>
                <div className="text-sm text-muted-foreground space-y-1">
                  <p><span className="font-medium">Created:</span> {formatDate(image.timestamp)}</p>
                  <p><span className="font-medium">ID:</span> {image.id}</p>
                  {image.settings?.model_name && (
                    <p><span className="font-medium">Model:</span> {image.settings.model_name}</p>
                  )}
                </div>
              </div>
              
              <Separator />
              
              {/* Prompts */}
              <div>
                <h4 className="font-medium mb-2">Prompts</h4>
                <div className="space-y-3">
                  <div>
                    <Badge variant="outline" className="mb-1">Positive</Badge>
                    <p className="text-sm bg-muted p-2 rounded">{image.prompt}</p>
                  </div>
                  {image.negativePrompt && (
                    <div>
                      <Badge variant="outline" className="mb-1">Negative</Badge>
                      <p className="text-sm bg-muted p-2 rounded">{image.negativePrompt}</p>
                    </div>
                  )}
                </div>
              </div>
              
              <Separator />
              
              {/* Settings */}
              {settings.length > 0 && (
                <div>
                  <h4 className="font-medium mb-2 flex items-center">
                    <Settings className="h-4 w-4 mr-2" />
                    Generation Settings
                  </h4>
                  <div className="space-y-2">
                    {settings.map(({ key, value }, index) => (
                      <div key={index} className="flex justify-between text-sm">
                        <span className="font-medium">{key}:</span>
                        <span className="text-muted-foreground">{value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </ScrollArea>
        </div>
        
        <div className="flex justify-end gap-2 pt-4 border-t">
          <Button 
            variant="destructive" 
            size="sm"
            onClick={() => {
              onRemove(image.id);
              onClose();
            }}
          >
            Delete Image
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

const ImageHistoryGallery: React.FC<ImageHistoryGalleryProps> = ({
  images,
  onRemoveImage,
  onClearAll,
  onSendToImg2Img,
  type
}) => {
  const [selectedImage, setSelectedImage] = useState<ImageResult | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<'newest' | 'oldest' | 'model'>('newest');
  const [filterModel, setFilterModel] = useState<string>('all');

  // Get unique models for filter
  const models = Array.from(new Set(
    images
      .map(img => img.settings?.model_name)
      .filter(Boolean)
  ));

  // Filter and sort images
  const filteredImages = images
    .filter(image => {
      const matchesSearch = image.prompt.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (image.negativePrompt?.toLowerCase().includes(searchQuery.toLowerCase()) ?? false);
      const matchesModel = filterModel === 'all' || image.settings?.model_name === filterModel;
      return matchesSearch && matchesModel;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'newest':
          return b.timestamp - a.timestamp;
        case 'oldest':
          return a.timestamp - b.timestamp;
        case 'model':
          return (a.settings?.model_name || '').localeCompare(b.settings?.model_name || '');
        default:
          return b.timestamp - a.timestamp;
      }
    });

  const handleImageClick = (image: ImageResult) => {
    setSelectedImage(image);
  };

  if (images.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-muted-foreground">
        <ImageIcon className="h-12 w-12 mb-2" />
        <p>No images generated yet</p>
        <p className="text-sm">Generated images will appear here</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium">
          Image History ({images.length} images)
        </h3>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={onClearAll}
          disabled={images.length === 0}
        >
          Clear All
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-2">
        <div className="flex-1">
          <Input
            placeholder="Search prompts..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full"
          />
        </div>
        <Select value={sortBy} onValueChange={(value: any) => setSortBy(value)}>
          <SelectTrigger className="w-32">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="newest">Newest</SelectItem>
            <SelectItem value="oldest">Oldest</SelectItem>
            <SelectItem value="model">Model</SelectItem>
          </SelectContent>
        </Select>
        <Select value={filterModel} onValueChange={setFilterModel}>
          <SelectTrigger className="w-36">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Models</SelectItem>
            {models.map(model => (
              <SelectItem key={model} value={model}>{model}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Image Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
        {filteredImages.map((image) => (
          <div
            key={image.id}
            className="group relative cursor-pointer"
            onClick={() => handleImageClick(image)}
          >
            <AspectRatio ratio={1} className="bg-muted rounded-lg overflow-hidden">
              <img
                src={image.url}
                alt={`Generated: ${image.prompt.slice(0, 50)}...`}
                className="w-full h-full object-cover transition-transform group-hover:scale-105"
              />
              
              {/* Overlay */}
              <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors" />
              
              {/* Quick actions */}
              <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <Button
                  size="sm"
                  variant="secondary"
                  className="h-6 w-6 p-0"
                  onClick={(e) => {
                    e.stopPropagation();
                    onRemoveImage(image.id);
                  }}
                >
                  <X className="h-3 w-3" />
                </Button>
              </div>
              
              {/* Info overlay */}
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <p className="text-white text-xs truncate">
                  {image.prompt.slice(0, 40)}...
                </p>
                <p className="text-white/70 text-xs">
                  {formatDate(image.timestamp).split(',')[0]}
                </p>
              </div>
            </AspectRatio>
          </div>
        ))}
      </div>

      {/* No results */}
      {filteredImages.length === 0 && searchQuery && (
        <div className="text-center py-8 text-muted-foreground">
          <p>No images match your search</p>
        </div>
      )}

      {/* Image Details Modal */}
      {selectedImage && (
        <ImageDetailsModal
          image={selectedImage}
          isOpen={!!selectedImage}
          onClose={() => setSelectedImage(null)}
          onRemove={onRemoveImage}
          onSendToImg2Img={onSendToImg2Img}
        />
      )}
    </div>
  );
};

export default ImageHistoryGallery;