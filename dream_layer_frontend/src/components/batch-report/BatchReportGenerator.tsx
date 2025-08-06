import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { generateBatchReport, downloadBatchReport, ImageReportData, GenerationConfig } from '@/services/reportService';
import { toast } from '@/hooks/use-toast';
import { Download, FileArchive, Loader2 } from 'lucide-react';

interface BatchReportGeneratorProps {
  images: ImageReportData[];
  config?: GenerationConfig;
}

const BatchReportGenerator: React.FC<BatchReportGeneratorProps> = ({ images, config = {} }) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [reportName, setReportName] = useState('');
  const [includeConfig, setIncludeConfig] = useState(true);
  const [includeReadme, setIncludeReadme] = useState(true);
  const [selectedImages, setSelectedImages] = useState<Set<string>>(new Set());
  
  // Update selected images when images prop changes
  React.useEffect(() => {
    // Auto-select all images when they become available
    setSelectedImages(new Set(images.map(img => img.id)));
  }, [images]);

  const handleSelectAll = () => {
    if (selectedImages.size === images.length) {
      setSelectedImages(new Set());
    } else {
      setSelectedImages(new Set(images.map(img => img.id)));
    }
  };

  const handleGenerateReport = async () => {
    if (selectedImages.size === 0) {
      toast({
        title: "No images selected",
        description: "Please select at least one image to include in the report.",
        variant: "destructive",
      });
      return;
    }

    setIsGenerating(true);

    try {
      // Filter selected images
      const selectedImageData = images.filter(img => selectedImages.has(img.id));

      // Prepare config
      const reportConfig: GenerationConfig = {
        ...config,
        generation_date: new Date().toISOString(),
        total_images: selectedImageData.length,
        include_config: includeConfig,
        include_readme: includeReadme,
      };

      // Generate the report
      const blob = await generateBatchReport(selectedImageData, reportConfig, reportName);

      // Download the report
      const filename = reportName ? `${reportName}.zip` : undefined;
      downloadBatchReport(blob, filename);

      toast({
        title: "Report generated successfully",
        description: `${selectedImageData.length} images included in the report.`,
      });
    } catch (error) {
      console.error('Error generating report:', error);
      toast({
        title: "Error generating report",
        description: error instanceof Error ? error.message : "An unknown error occurred",
        variant: "destructive",
      });
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileArchive className="h-5 w-5" />
          Batch Report Generator
        </CardTitle>
        <CardDescription>
          Generate a comprehensive report bundle containing selected images, metadata, and configuration.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="report-name">Report Name (Optional)</Label>
          <Input
            id="report-name"
            type="text"
            placeholder="report_2024_01_01"
            value={reportName}
            onChange={(e) => setReportName(e.target.value)}
            disabled={isGenerating}
          />
          <p className="text-sm text-muted-foreground">
            Leave empty for automatic timestamp-based naming
          </p>
        </div>

        <div className="space-y-3">
          <div className="flex items-center space-x-2">
            <Checkbox
              id="include-config"
              checked={includeConfig}
              onCheckedChange={(checked) => setIncludeConfig(checked as boolean)}
              disabled={isGenerating}
            />
            <Label htmlFor="include-config" className="cursor-pointer">
              Include generation configuration (config.json)
            </Label>
          </div>

          <div className="flex items-center space-x-2">
            <Checkbox
              id="include-readme"
              checked={includeReadme}
              onCheckedChange={(checked) => setIncludeReadme(checked as boolean)}
              disabled={isGenerating}
            />
            <Label htmlFor="include-readme" className="cursor-pointer">
              Include README file with usage instructions
            </Label>
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label>Selected Images ({selectedImages.size}/{images.length})</Label>
            <Button
              variant="outline"
              size="sm"
              onClick={handleSelectAll}
              disabled={isGenerating}
            >
              {selectedImages.size === images.length ? 'Deselect All' : 'Select All'}
            </Button>
          </div>
          
          <div className="text-sm text-muted-foreground">
            <p>The report will include:</p>
            <ul className="list-disc list-inside mt-1 space-y-1">
              <li>results.csv - Metadata for all selected images</li>
              <li>grids/ - Directory with all selected images</li>
              {includeConfig && <li>config.json - Complete generation configuration</li>}
              {includeReadme && <li>README.txt - Usage instructions and schema information</li>}
            </ul>
          </div>
        </div>

        <Button
          onClick={handleGenerateReport}
          disabled={isGenerating || selectedImages.size === 0}
          className="w-full"
        >
          {isGenerating ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Generating Report...
            </>
          ) : (
            <>
              <Download className="mr-2 h-4 w-4" />
              Generate Batch Report
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
};

export default BatchReportGenerator;