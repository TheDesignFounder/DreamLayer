import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { AlertCircle, Download, FileText, FolderOpen, CheckCircle, RefreshCw } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useImg2ImgGalleryStore } from '@/stores/useImg2ImgGalleryStore';
import { useTxt2ImgGalleryStore } from '@/stores/useTxt2ImgGalleryStore';
import { useExtrasGalleryStore } from '@/stores/useExtrasGalleryStore';
import { GallerySync } from '@/utils/gallerySync';

interface ReportGenerationResult {
  status: 'success' | 'error';
  message: string;
  report_path?: string;
  report_filename?: string;
  total_images?: number;
  csv_validation?: {
    valid: boolean;
    required_columns: string[];
    actual_columns: string[];
    missing_columns: string[];
    row_count: number;
  };
  path_validation?: {
    valid: boolean;
    total_csv_paths: number;
    valid_paths: number;
    missing_paths: string[];
  };
  bundle_size_bytes?: number;
  generation_types?: string[];
}

export const ReportGenerator: React.FC = () => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<ReportGenerationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [backendImageCount, setBackendImageCount] = useState(0);
  const [backendTxt2imgCount, setBackendTxt2imgCount] = useState(0);
  const [backendImg2imgCount, setBackendImg2imgCount] = useState(0);
  const [backendExtrasCount, setBackendExtrasCount] = useState(0);
  const [backendGenerationTypes, setBackendGenerationTypes] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const txt2imgImages = useTxt2ImgGalleryStore((state) => state.images);
  const img2imgImages = useImg2ImgGalleryStore((state) => state.images);
  const extrasImages = useExtrasGalleryStore((state) => state.images);

  const frontendTotalImages = txt2imgImages.length + img2imgImages.length + extrasImages.length;
  
  // Use backend count if frontend stores are empty (page refresh scenario)
  const totalImages = frontendTotalImages > 0 ? frontendTotalImages : backendImageCount;
  
  // Determine generation types (frontend or backend)
  const getGenerationTypes = () => {
    if (frontendTotalImages > 0) {
      const types = [];
      if (txt2imgImages.length > 0) types.push('txt2img');
      if (img2imgImages.length > 0) types.push('img2img');
      if (extrasImages.length > 0) types.push('extras');
      return types;
    } else {
      return backendGenerationTypes;
    }
  };
  
  const generationTypes = getGenerationTypes();
  
  // Format generation type display
  const getGenerationTypeDisplay = () => {
    if (generationTypes.length === 0) return '0';
    if (generationTypes.length === 1) {
      return generationTypes[0] === 'txt2img' ? 'Txt2Img' : 
             generationTypes[0] === 'img2img' ? 'Img2Img' : 'Extras';
    }
    return 'Multiple';
  };

  // Fetch backend image count on component mount
  const fetchBackendImageCount = async (skipLoading = false) => {
    try {
      if (!skipLoading) setIsLoading(true);
      
      // Use dedicated status endpoint to get current backend image count
      const response = await fetch('http://localhost:5002/api/reports/status', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });

      if (response.ok) {
        const result = await response.json();
        const newCount = result.total_images || 0;
        const txt2imgCount = result.txt2img_count || 0;
        const img2imgCount = result.img2img_count || 0;
        const extrasCount = result.extras_count || 0;
        const types = result.generation_types || [];
        setBackendImageCount(newCount);
        setBackendTxt2imgCount(txt2imgCount);
        setBackendImg2imgCount(img2imgCount);
        setBackendExtrasCount(extrasCount);
        setBackendGenerationTypes(types);
        console.log(`📊 Backend has ${newCount} images available for reports (${txt2imgCount} txt2img, ${img2imgCount} img2img, ${extrasCount} extras)`);
      } else {
        console.warn('Could not fetch backend image count');
        setBackendImageCount(0);
        setBackendTxt2imgCount(0);
        setBackendImg2imgCount(0);
        setBackendExtrasCount(0);
        setBackendGenerationTypes([]);
      }
    } catch (error) {
      console.error('Error fetching backend image count:', error);
      setBackendImageCount(0);
      setBackendTxt2imgCount(0);
      setBackendImg2imgCount(0);
      setBackendGenerationTypes([]);
    } finally {
      if (!skipLoading) setIsLoading(false);
    }
  };

  useEffect(() => {
    const initializeApp = async () => {
      // Ensure fresh start if backend is empty but frontend has old data
      await GallerySync.ensureFreshStart();
      // Then fetch current backend count
      fetchBackendImageCount();
    };
    
    initializeApp();
  }, []);

  // Refetch when component becomes visible (user switches to Reports tab)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        console.log('🔍 Reports tab became visible, refreshing data...');
        fetchBackendImageCount(true);
      }
    };

    const handleFocus = () => {
      console.log('🔍 Window focused, refreshing Reports data...');
      fetchBackendImageCount(true);
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('focus', handleFocus);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('focus', handleFocus);
    };
  }, []);

  // Also refetch when frontend stores change (after new generations)
  useEffect(() => {
    if (frontendTotalImages > 0 && frontendTotalImages !== backendImageCount) {
      // Frontend has different count than backend, refetch backend count
      console.log(`🔄 Frontend count (${frontendTotalImages}) differs from backend (${backendImageCount}), refreshing...`);
      setTimeout(() => {
        fetchBackendImageCount(true); // Skip loading state for refresh
      }, 1000); // Give time for sync to complete
    }
  }, [frontendTotalImages, backendImageCount]);

  // Additional effect to listen to individual store changes for more responsive updates
  useEffect(() => {
    if (txt2imgImages.length > 0 || img2imgImages.length > 0 || extrasImages.length > 0) {
      console.log(`🔄 Store change detected: txt2img=${txt2imgImages.length}, img2img=${img2imgImages.length}, extras=${extrasImages.length}`);
      setTimeout(() => {
        fetchBackendImageCount(true);
      }, 1500); // Slightly longer delay for cross-tab scenarios
    }
  }, [txt2imgImages.length, img2imgImages.length, extrasImages.length]);


  const updateGalleryData = async () => {
    try {
      const galleryData = {
        txt2img: txt2imgImages,
        img2img: img2imgImages,
        extras: extrasImages
      };

      const response = await fetch('http://localhost:5002/api/gallery-data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(galleryData)
      });

      if (!response.ok) {
        throw new Error(`Failed to update gallery data: ${response.statusText}`);
      }

      console.log('Gallery data updated successfully');
    } catch (error) {
      console.error('Failed to update gallery data:', error);
      throw error;
    }
  };

  const generateReport = async () => {
    if (totalImages === 0) {
      setError('No images available to generate report. Please generate some images first.');
      return;
    }

    setIsGenerating(true);
    setProgress(0);
    setError(null);
    setResult(null);

    try {
      // Step 1: Update gallery data (20%) - only if frontend has data
      setProgress(20);
      if (frontendTotalImages > 0) {
        await updateGalleryData();
      } else {
        console.log('Using existing backend data for report generation');
      }

      // Step 2: Generate report (80%)
      setProgress(50);
      const response = await fetch('http://localhost:5002/api/reports/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          filename: `dreamlayer_report_${new Date().toISOString().slice(0, 19).replace(/[:-]/g, '')}.zip`
        })
      });

      setProgress(80);
      const data: ReportGenerationResult = await response.json();

      if (response.ok && data.status === 'success') {
        setProgress(100);
        setResult(data);
      } else {
        throw new Error(data.message || 'Failed to generate report');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setIsGenerating(false);
      if (!result) {
        setProgress(0);
      }
    }
  };

  const downloadReport = async () => {
    if (result?.report_filename) {
      const downloadUrl = `http://localhost:5002/api/reports/download/${result.report_filename}`;
      window.open(downloadUrl, '_blank');
      
      // Clear session after download
      await clearSession();
    }
  };

  const clearSession = async () => {
    try {
      console.log('🧹 Clearing session after report download...');
      
      // Use centralized sync to clear all data
      await GallerySync.clearAll();
      
      // Reset local state
      setResult(null);
      setError(null);
      setProgress(0);
      setBackendImageCount(0);
      setBackendTxt2imgCount(0);
      setBackendImg2imgCount(0);
      setBackendExtrasCount(0);
      setBackendGenerationTypes([]);
      
      // Refresh backend count to confirm it's 0
      await fetchBackendImageCount(true);
      
      console.log('✅ Session cleared successfully');
    } catch (error) {
      console.error('❌ Error clearing session:', error);
    }
  };

  const formatFileSize = (bytes: number): string => {
    const units = ['B', 'KB', 'MB', 'GB'];
    let size = bytes;
    let unitIndex = 0;
    
    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }
    
    return `${size.toFixed(1)} ${units[unitIndex]}`;
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 justify-between">
          <div className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Report Generator
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => fetchBackendImageCount()}
            disabled={isLoading}
            className="ml-auto"
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          </Button>
        </CardTitle>
        <CardDescription>
          Generate a comprehensive report bundle containing all your generated images, metadata, and configuration.
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Status Overview */}
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center p-3 bg-muted rounded-lg">
            <div className="text-2xl font-bold text-primary">
              {isLoading ? '...' : totalImages}
            </div>
            <div className="text-sm text-muted-foreground">
              Total Images
              {frontendTotalImages > 0 && backendImageCount > 0 && frontendTotalImages !== backendImageCount && (
                <div className="text-xs text-orange-600">
                  Frontend: {frontendTotalImages}, Backend: {backendImageCount}
                </div>
              )}
            </div>
          </div>
          <div className="text-center p-3 bg-muted rounded-lg">
            <div className="text-2xl font-bold text-primary">
              {isLoading ? '...' : getGenerationTypeDisplay()}
            </div>
            <div className="text-sm text-muted-foreground">Generation Types</div>
          </div>
        </div>

        {/* Generation Types */}
        <div className="flex gap-2 flex-wrap">
          {frontendTotalImages > 0 ? (
            <>
              {txt2imgImages.length > 0 && (
                <Badge variant="secondary">
                  Txt2Img ({txt2imgImages.length})
                </Badge>
              )}
              {img2imgImages.length > 0 && (
                <Badge variant="secondary">
                  Img2Img ({img2imgImages.length})
                </Badge>
              )}
              {extrasImages.length > 0 && (
                <Badge variant="secondary">
                  Extras ({extrasImages.length})
                </Badge>
              )}
            </>
          ) : backendImageCount > 0 ? (
            <>
              {backendTxt2imgCount > 0 && (
                <Badge variant="secondary">
                  Txt2Img ({backendTxt2imgCount})
                </Badge>
              )}
              {backendImg2imgCount > 0 && (
                <Badge variant="secondary">
                  Img2Img ({backendImg2imgCount})
                </Badge>
              )}
              {backendExtrasCount > 0 && (
                <Badge variant="secondary">
                  Extras ({backendExtrasCount})
                </Badge>
              )}
            </>
          ) : (
            <Badge variant="outline">
              {isLoading ? 'Loading...' : 'No images generated'}
            </Badge>
          )}
        </div>

        {/* Progress Bar */}
        {isGenerating && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Generating report...</span>
              <span>{progress}%</span>
            </div>
            <Progress value={progress} className="w-full" />
          </div>
        )}

        {/* Error Display */}
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Success Result */}
        {result && result.status === 'success' && (
          <div className="space-y-4">
            <Alert>
              <CheckCircle className="h-4 w-4" />
              <AlertDescription>
                Report generated successfully! The bundle contains {result.total_images} images across {result.generation_types?.length} generation types.
              </AlertDescription>
            </Alert>

            {/* Report Details */}
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <strong>File Size:</strong> {result.bundle_size_bytes ? formatFileSize(result.bundle_size_bytes) : 'Unknown'}
              </div>
              <div>
                <strong>Generation Types:</strong> {result.generation_types?.join(', ') || 'None'}
              </div>
              <div>
                <strong>CSV Validation:</strong> {result.csv_validation?.valid ? '✅ Valid' : '❌ Invalid'}
              </div>
              <div>
                <strong>Path Validation:</strong> {result.path_validation?.valid ? '✅ All paths resolved' : '❌ Missing paths'}
              </div>
            </div>

            {/* Download Button */}
            <Button 
              onClick={downloadReport} 
              className="w-full"
              size="lg"
            >
              <Download className="h-4 w-4 mr-2" />
              Download Report Bundle
            </Button>
          </div>
        )}

        {/* Generate Button */}
        <Button 
          onClick={generateReport} 
          disabled={isGenerating || totalImages === 0 || isLoading}
          className="w-full"
          size="lg"
        >
          {isGenerating ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Generating Report...
            </>
          ) : (
            <>
              <FolderOpen className="h-4 w-4 mr-2" />
              Generate Report Bundle
            </>
          )}
        </Button>

        {/* Report Contents Info */}
        <div className="text-xs text-muted-foreground space-y-1">
          <p><strong>Report Contents:</strong></p>
          <ul className="ml-4 space-y-1">
            <li>• <code>results.csv</code> - Complete image metadata with standardized schema</li>
            <li>• <code>config.json</code> - Current system configuration and settings</li>
            <li>• <code>grids/</code> - Organized image collections by generation type</li>
            <li>• <code>README.md</code> - Human-readable report documentation</li>
          </ul>
          <p className="mt-2">All paths in the CSV are deterministic and resolve to files within the ZIP bundle.</p>
        </div>
      </CardContent>
    </Card>
  );
};

export default ReportGenerator;
