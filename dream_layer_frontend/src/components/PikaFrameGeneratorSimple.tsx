import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Film, AlertCircle } from 'lucide-react';

const PikaFrameGeneratorSimple: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [negativePrompt, setNegativePrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerateFrame = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // For now, just show success message
      alert('Pika frame generation would happen here! API integration needed.');
      
    } catch (err) {
      setError('Failed to generate frame');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="space-y-6 p-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Pika Frame Generator</h2>
          <p className="text-muted-foreground">
            Generate stylized single frames using Pika 2.2 text-to-video API
          </p>
        </div>
        <Badge variant="outline" className="flex items-center gap-2">
          <Film className="w-4 h-4" />
          Single Frame Mode
        </Badge>
      </div>

      {/* Video Upgrade Tip */}
      <Card className="glass-morphism border-blue-200">
        <CardContent className="p-4">
          <div className="flex items-start gap-3">
            <Film className="h-5 w-5 text-blue-600 mt-0.5" />
            <div>
              <p className="font-semibold text-blue-900">💡 Future Video Upgrade</p>
              <p className="text-sm text-blue-700">
                This component extracts single frames from Pika's video generation. 
                To upgrade to full video generation, simply change <code className="bg-blue-100 px-1 rounded">video: false</code> to <code className="bg-blue-100 px-1 rounded">video: true</code> in the API call 
                and handle the video response format instead of extracting frames.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Settings Panel */}
        <Card className="glass-morphism">
          <CardHeader>
            <CardTitle>Generation Settings</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Prompt Input */}
            <div className="space-y-2">
              <Label htmlFor="prompt">Prompt *</Label>
              <Textarea
                id="prompt"
                placeholder="Describe the scene you want to generate..."
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                className="glass-morphism"
                rows={3}
              />
            </div>

            {/* Negative Prompt */}
            <div className="space-y-2">
              <Label htmlFor="negative-prompt">Negative Prompt</Label>
              <Textarea
                id="negative-prompt"
                placeholder="Describe what you want to exclude..."
                value={negativePrompt}
                onChange={(e) => setNegativePrompt(e.target.value)}
                className="glass-morphism"
                rows={2}
              />
            </div>

            {/* Motion Strength Info */}
            <div className="space-y-2">
              <Label>Motion Strength: 0.5 (for future video upgrade)</Label>
              <div className="h-2 bg-secondary rounded-full">
                <div className="h-2 bg-primary rounded-full w-1/2"></div>
              </div>
              <p className="text-xs text-muted-foreground">
                Currently unused in single-frame mode. Will control video motion when upgraded to full video generation.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Generation Panel */}
        <Card className="glass-morphism">
          <CardHeader>
            <CardTitle>Frame Generation</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Generate Button */}
            <Button
              onClick={handleGenerateFrame}
              disabled={isGenerating || !prompt.trim()}
              className="w-full"
              size="lg"
            >
              {isGenerating ? (
                <>
                  <div className="animate-spin rounded-full w-4 h-4 border-b-2 border-white mr-2" />
                  Generating Frame...
                </>
              ) : (
                <>
                  <Film className="w-4 h-4 mr-2" />
                  Generate Pika Frame
                </>
              )}
            </Button>

            {/* Error Display */}
            {error && (
              <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
                <AlertCircle className="h-4 w-4 text-red-600" />
                <span className="text-red-700">{error}</span>
              </div>
            )}

            {/* API Integration Info */}
            <Card className="bg-blue-50 border-blue-200">
              <CardContent className="p-4">
                <h4 className="font-semibold text-blue-900 mb-2">API Integration Required</h4>
                <div className="text-sm text-blue-700 space-y-1">
                  <p>• Calls Pika API with <code className="bg-blue-100 px-1 rounded">video: false</code></p>
                  <p>• Verifies exactly one frame in response</p>
                  <p>• Extracts frame to PNG format</p>
                  <p>• Exposes motion_strength parameter</p>
                </div>
              </CardContent>
            </Card>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default PikaFrameGeneratorSimple;