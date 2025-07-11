import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useImageHistoryStore } from '@/stores/useImageHistoryStore';
import { useImg2ImgGalleryStore } from '@/stores/useImg2ImgGalleryStore';
import ImageHistoryGallery from '@/components/ImageHistoryGallery';
import { ImageResult } from '@/types/imageResult';
import { 
  Image as ImageIcon, 
  Download, 
  Settings, 
  Trash2,
  BarChart3,
  Calendar,
  FileImage
} from 'lucide-react';

interface HistoryPageProps {
  onTabChange: (tabId: string) => void;
}

const HistoryPage: React.FC<HistoryPageProps> = ({ onTabChange }) => {
  const [activeTab, setActiveTab] = useState('txt2img');
  
  const {
    txt2imgHistory,
    img2imgHistory,
    removeFromHistory,
    clearHistory,
    clearAllHistory,
    getHistoryCount,
    setMaxHistorySize,
    maxHistorySize
  } = useImageHistoryStore();
  
  const { setInputImage } = useImg2ImgGalleryStore();
  
  const historyCount = getHistoryCount();

  const handleSendToImg2Img = async (image: ImageResult) => {
    try {
      // Convert image URL to blob and create file
      const response = await fetch(image.url);
      const blob = await response.blob();
      const filename = `history-image-${image.id}.png`;
      
      setInputImage({
        url: image.url,
        file: new File([blob], filename, { type: 'image/png' })
      });
      
      // Switch to img2img tab
      onTabChange('img2img');
    } catch (error) {
      console.error('Error sending image to img2img:', error);
    }
  };

  const handleExportHistory = () => {
    const allHistory = {
      txt2img: txt2imgHistory,
      img2img: img2imgHistory,
      exported_at: new Date().toISOString(),
      total_images: historyCount.total
    };
    
    const dataStr = JSON.stringify(allHistory, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = `image-history-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getStorageSize = () => {
    try {
      const data = localStorage.getItem('image-history-storage');
      if (data) {
        return (new Blob([data]).size / 1024 / 1024).toFixed(2) + ' MB';
      }
    } catch (error) {
      console.error('Error calculating storage size:', error);
    }
    return 'Unknown';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Image History</h1>
          <p className="text-muted-foreground">
            Manage and explore your generated images
          </p>
        </div>
        
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExportHistory}>
            <Download className="h-4 w-4 mr-2" />
            Export History
          </Button>
          <Button 
            variant="destructive" 
            onClick={clearAllHistory}
            disabled={historyCount.total === 0}
          >
            <Trash2 className="h-4 w-4 mr-2" />
            Clear All
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Images</CardTitle>
            <ImageIcon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{historyCount.total}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Text to Image</CardTitle>
            <FileImage className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{historyCount.txt2img}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Image to Image</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{historyCount.img2img}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Storage Used</CardTitle>
            <Settings className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{getStorageSize()}</div>
            <p className="text-xs text-muted-foreground">
              Max: {maxHistorySize} images
            </p>
          </CardContent>
        </Card>
      </div>

      {/* History Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="txt2img" className="relative">
            Text to Image
            {historyCount.txt2img > 0 && (
              <Badge variant="secondary" className="ml-2">
                {historyCount.txt2img}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="img2img" className="relative">
            Image to Image
            {historyCount.img2img > 0 && (
              <Badge variant="secondary" className="ml-2">
                {historyCount.img2img}
              </Badge>
            )}
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="txt2img" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <FileImage className="h-5 w-5 mr-2" />
                Text to Image History
              </CardTitle>
              <CardDescription>
                Images generated from text prompts
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ImageHistoryGallery
                images={txt2imgHistory}
                onRemoveImage={(id) => removeFromHistory('txt2img', id)}
                onClearAll={() => clearHistory('txt2img')}
                onSendToImg2Img={handleSendToImg2Img}
                type="txt2img"
              />
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="img2img" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <BarChart3 className="h-5 w-5 mr-2" />
                Image to Image History
              </CardTitle>
              <CardDescription>
                Images generated from image inputs
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ImageHistoryGallery
                images={img2imgHistory}
                onRemoveImage={(id) => removeFromHistory('img2img', id)}
                onClearAll={() => clearHistory('img2img')}
                onSendToImg2Img={handleSendToImg2Img}
                type="img2img"
              />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default HistoryPage;