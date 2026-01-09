import React, { useState } from 'react';
import { Upload, MessageSquare, Image as ImageIcon, Loader2, Eye, EyeOff, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { toast } from '@/hooks/use-toast';

interface Img2TxtPageProps {}

const Img2TxtPage: React.FC<Img2TxtPageProps> = () => {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [customPrompt, setCustomPrompt] = useState<string>('Analyze and describe the image in detail including objects, scene, colors, mood, and composition');
  const [generatedText, setGeneratedText] = useState<string>('');
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [apiKeyDialogOpen, setApiKeyDialogOpen] = useState<boolean>(false);
  const [geminiApiKey, setGeminiApiKey] = useState<string>('');
  const [showApiKey, setShowApiKey] = useState<boolean>(false);
  const [isSubmittingKey, setIsSubmittingKey] = useState<boolean>(false);

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

  const handleSubmitApiKey = async () => {
    if (!geminiApiKey.trim()) {
      toast({
        title: "Invalid API Key",
        description: "Please enter a valid Gemini API key.",
        variant: "destructive",
      });
      return;
    }

    setIsSubmittingKey(true);
    try {
      const response = await fetch('http://localhost:5002/api/add-api-key', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          alias: 'GEMINI_API_KEY',
          'api-key': geminiApiKey,
        }),
      });

      const data = await response.json();

      if (data.status === 'success') {
        toast({
          title: "Success",
          description: "Gemini API key has been added successfully! Refreshing...",
        });
        setGeminiApiKey('');
        setApiKeyDialogOpen(false);

        // Trigger refresh after closing modal
        setTimeout(() => {
          localStorage.setItem('activeTab', 'img2txt');
          window.location.reload();
        }, 1000);
      } else {
        throw new Error(data.message || 'Failed to add API key');
      }
    } catch (error) {
      toast({
        title: "Failed to add API key",
        description: error instanceof Error ? error.message : "An unknown error occurred",
        variant: "destructive",
      });
    } finally {
      setIsSubmittingKey(false);
    }
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
      <div className="w-full max-w-6xl space-y-4">
        <div className="flex items-center justify-between mb-[18px]">
          <h3 className="text-base font-medium">Image to Text Analysis</h3>
          <div className="flex gap-2">
            <Dialog open={apiKeyDialogOpen} onOpenChange={setApiKeyDialogOpen}>
              <DialogTrigger asChild>
                <Button
                  variant="outline"
                  className="rounded-md border border-input bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground"
                >
                  Add Gemini API Key
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[600px]">
                <DialogHeader>
                  <DialogTitle className="text-center">Google Gemini API Key</DialogTitle>
                </DialogHeader>
                <p className="text-sm text-muted-foreground text-center -mt-2 mb-0">
                  Press the Refresh button to select the models in the dropdown
                </p>
                <div className="flex flex-col items-center justify-center space-y-4 py-2">
                  <div className="flex flex-col sm:flex-row sm:items-center gap-2 w-full">
                    <label className="w-full sm:w-48 text-sm font-medium whitespace-nowrap">
                      Gemini - Google AI
                      <a
                        href="https://ai.google.dev/gemini-api/docs/api-key"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="ml-1 text-xs text-blue-600 underline"
                      >
                        (Docs)
                      </a>
                    </label>
                    <div className="relative w-full sm:flex-1">
                      <input
                        type={showApiKey ? 'text' : 'password'}
                        placeholder="Enter Gemini API Key"
                        className="w-full py-2 pr-10 pl-3 border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring bg-background text-foreground"
                        value={geminiApiKey}
                        onChange={(e) => setGeminiApiKey(e.target.value)}
                      />
                      <button
                        type="button"
                        className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                        onClick={() => setShowApiKey(!showApiKey)}
                        tabIndex={-1}
                      >
                        {showApiKey ? (
                          <EyeOff className="h-4 w-4" />
                        ) : (
                          <Eye className="h-4 w-4" />
                        )}
                      </button>
                    </div>
                    <Button
                      onClick={handleSubmitApiKey}
                      disabled={!geminiApiKey.trim() || isSubmittingKey}
                      className="w-full sm:w-24 bg-blue-600 text-white hover:bg-blue-700"
                    >
                      {isSubmittingKey ? 'Submitting...' : 'Submit'}
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
            <Button
              variant="outline"
              onClick={() => {
                localStorage.setItem('activeTab', 'img2txt');
                window.location.reload();
              }}
              className="rounded-md border border-input bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Image Upload Section */}
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium text-foreground">
                  Image Input
                </CardTitle>
                <Button
                  onClick={handleGenerateText}
                  disabled={!selectedImage || isGenerating}
                  className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
                >
                  {isGenerating ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    'Generate Analysis'
                  )}
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Upload Area */}
                <div
                  className="border-2 border-dashed border-border rounded-lg p-6 text-center hover:border-primary/50 transition-colors cursor-pointer mt-1"
                  onDrop={handleDrop}
                  onDragOver={handleDragOver}
                  onClick={() => document.getElementById('image-upload')?.click()}
                >
                  {imagePreview ? (
                    <div className="space-y-3">
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
                      <Upload className="w-10 h-10 mx-auto text-muted-foreground" />
                      <p className="text-sm font-medium">Drop an image here or click to browse</p>
                      <p className="text-xs text-muted-foreground">
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
                    Enter Prompt For Image Analysis
                  </label>
                  <Textarea
                    value={customPrompt}
                    onChange={(e) => setCustomPrompt(e.target.value)}
                    rows={3}
                    className="mt-4"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Generated Text Section */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-foreground">
                Generated Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {isGenerating ? (
                  <div className="flex items-center justify-center p-6 text-muted-foreground text-sm">
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Analyzing image with Gemini AI...
                  </div>
                ) : generatedText ? (
                  <div className="space-y-4">
                    <div className="p-3 bg-muted rounded-lg">
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
                  <div className="text-center p-6 text-muted-foreground">
                    <MessageSquare className="w-10 h-10 mx-auto mb-3 opacity-50" />
                    <p className="text-sm">Upload an image and click "Generate Text" to see the AI analysis</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Img2TxtPage;
