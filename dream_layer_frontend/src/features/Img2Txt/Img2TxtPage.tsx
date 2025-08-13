import React, { useState } from 'react';
import { Upload, MessageSquare, Image as ImageIcon, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { toast } from '@/hooks/use-toast';

interface Img2TxtPageProps {}

const Img2TxtPage: React.FC<Img2TxtPageProps> = () => {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [customPrompt, setCustomPrompt] = useState<string>('');
  const [generatedText, setGeneratedText] = useState<string>('');
  const [isGenerating, setIsGenerating] = useState<boolean>(false);

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedImage(file);
      setGeneratedText(''); // Clear previous results
      
      // Create preview URL
      const url = URL.createObjectURL(file);
      setImagePreview(url);
    }
  };

  const handleDrop = (event: React.DragEvent) => {
    event.preventDefault();
    const file = event.dataTransfer.files?.[0];
    if (file && file.type.startsWith('image/')) {
      setSelectedImage(file);
      setGeneratedText('');
      
      const url = URL.createObjectURL(file);
      setImagePreview(url);
    }
  };

  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault();
  };

  const clearImage = () => {
    if (imagePreview) {
      URL.revokeObjectURL(imagePreview);
    }
    setSelectedImage(null);
    setImagePreview(null);
    setGeneratedText('');
  };

  const convertImageToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  };

  const handleGenerateText = async () => {
    if (!selectedImage) {
      toast({
        title: "No image selected",
        description: "Please upload an image first.",
        variant: "destructive",
      });
      return;
    }

    setIsGenerating(true);
    try {
      // Convert image to base64
      const base64Image = await convertImageToBase64(selectedImage);

      // Prepare request data
      const requestData = {
        input_image: base64Image,
        prompt: customPrompt || undefined,
        model: "gemini-2.5-pro-preview-05-06",
        seed: 42
      };

      // Send request to img2txt server
      const response = await fetch('http://localhost:5007/api/img2txt', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      const data = await response.json();

      if (data.status === 'success') {
        setGeneratedText(data.generated_text || data.comfy_response?.text_output || 'No text generated');
        toast({
          title: "Analysis Complete",
          description: "Image has been analyzed successfully!",
        });
      } else {
        throw new Error(data.message || 'Failed to analyze image');
      }
    } catch (error) {
      console.error('Error generating text:', error);
      toast({
        title: "Generation Failed",
        description: error instanceof Error ? error.message : "An unknown error occurred",
        variant: "destructive",
      });
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="flex justify-center">
      <div className="w-full max-w-6xl space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold">Image to Text Analysis</h2>
          <Button 
            onClick={handleGenerateText} 
            disabled={!selectedImage || isGenerating}
            className="min-w-[120px]"
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <MessageSquare className="w-4 h-4 mr-2" />
                Generate Text
              </>
            )}
          </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Image Upload Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ImageIcon className="w-5 h-5" />
                Image Input
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Upload Area */}
                <div
                  className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary/50 transition-colors cursor-pointer"
                  onDrop={handleDrop}
                  onDragOver={handleDragOver}
                  onClick={() => document.getElementById('image-upload')?.click()}
                >
                  {imagePreview ? (
                    <div className="space-y-4">
                      <img
                        src={imagePreview}
                        alt="Selected"
                        className="max-w-full max-h-64 mx-auto rounded-lg shadow-sm"
                      />
                      <div className="flex gap-2 justify-center">
                        <Button variant="outline" size="sm" onClick={clearImage}>
                          Clear Image
                        </Button>
                        <Button variant="outline" size="sm" onClick={() => document.getElementById('image-upload')?.click()}>
                          Change Image
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <Upload className="w-12 h-12 mx-auto text-muted-foreground" />
                      <p className="text-lg font-medium">Drop an image here or click to browse</p>
                      <p className="text-sm text-muted-foreground">
                        Supports JPG, PNG, GIF and other image formats
                      </p>
                    </div>
                  )}
                </div>

                <input
                  id="image-upload"
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="hidden"
                />

                {/* Custom Prompt */}
                <div className="space-y-2">
                  <label className="text-sm font-medium">
                    Custom Analysis Prompt (Optional)
                  </label>
                  <Textarea
                    placeholder="Enter custom instructions for image analysis (leave empty for default analysis)"
                    value={customPrompt}
                    onChange={(e) => setCustomPrompt(e.target.value)}
                    rows={3}
                  />
                  <p className="text-xs text-muted-foreground">
                    Default: Analyze and describe the image in detail including objects, scene, colors, mood, and composition.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Generated Text Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="w-5 h-5" />
                Generated Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {isGenerating ? (
                  <div className="flex items-center justify-center p-8 text-muted-foreground">
                    <Loader2 className="w-6 h-6 mr-2 animate-spin" />
                    Analyzing image with Gemini AI...
                  </div>
                ) : generatedText ? (
                  <div className="space-y-4">
                    <div className="p-4 bg-muted rounded-lg">
                      <pre className="whitespace-pre-wrap text-sm">{generatedText}</pre>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => navigator.clipboard.writeText(generatedText)}
                      >
                        Copy Text
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setGeneratedText('')}
                      >
                        Clear
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="text-center p-8 text-muted-foreground">
                    <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>Upload an image and click "Generate Text" to see the AI analysis</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Info Section */}
        <Card>
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div>
                <h4 className="font-semibold mb-2">How it works</h4>
                <p className="text-muted-foreground">
                  Upload any image and our Gemini AI will analyze it, providing detailed descriptions of objects, scenes, composition, and artistic elements.
                </p>
              </div>
              <div>
                <h4 className="font-semibold mb-2">Custom Prompts</h4>
                <p className="text-muted-foreground">
                  Customize the analysis by providing specific instructions. Ask about style, colors, emotions, or technical aspects.
                </p>
              </div>
              <div>
                <h4 className="font-semibold mb-2">Powered by</h4>
                <p className="text-muted-foreground">
                  Google Gemini 2.5 Pro - Advanced multimodal AI with sophisticated visual understanding capabilities.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Img2TxtPage;
