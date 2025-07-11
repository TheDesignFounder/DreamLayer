import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Copy, Download, Shuffle, AlertCircle, CheckCircle2, Film } from 'lucide-react';
import { usePikaStore, usePikaActions, usePikaSettings, usePikaGenerationState } from '@/stores/usePikaStore';
import { generatePikaFrame, formatPikaError } from '@/services/pikaService';
import { PikaError, PikaResolution, getAspectRatioDisplayName } from '@/types/pika';
import { cn } from '@/lib/utils';

const PikaFrameGenerator: React.FC = () => {
  const settings = usePikaSettings();
  const { isGenerating, progress, error } = usePikaGenerationState();
  const actions = usePikaActions();
  const frames = usePikaStore((state) => state.frames);
  
  const [localProgress, setLocalProgress] = useState(0);

  const handleGenerateFrame = async () => {
    if (isGenerating) return;
    
    if (!settings.prompt_text.trim()) {
      actions.setError('Please enter a prompt text');
      return;
    }

    try {
      actions.setGenerating(true);
      actions.setError(null);
      actions.setProgress(0);
      setLocalProgress(0);

      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setLocalProgress(prev => {
          const newProgress = Math.min(prev + 10, 90);
          actions.setProgress(newProgress);
          return newProgress;
        });
      }, 500);

      console.log('🎬 Starting Pika frame generation...');

      const result = await generatePikaFrame({
        prompt_text: settings.prompt_text,
        negative_prompt: settings.negative_prompt,
        seed: settings.seed,
        resolution: settings.resolution,
        duration: settings.duration,
        aspect_ratio: settings.aspect_ratio,
        motion_strength: settings.motion_strength,
        video: false, // CRITICAL: Single frame extraction
      });

      clearInterval(progressInterval);
      actions.setProgress(100);
      
      // Add the generated frame to the store
      actions.addFrame(result);
      
      console.log('✅ Pika frame generated successfully:', result);
      
    } catch (err) {
      console.error('❌ Pika frame generation failed:', err);
      
      if (err && typeof err === 'object' && 'type' in err) {
        actions.setError(formatPikaError(err as PikaError));
      } else {
        actions.setError(err instanceof Error ? err.message : 'Unknown error occurred');
      }
    } finally {
      actions.setGenerating(false);
      setLocalProgress(0);
    }
  };

  const handleCopyPrompt = () => {
    const combinedPrompt = `Prompt: ${settings.prompt_text}\nNegative Prompt: ${settings.negative_prompt}`;
    navigator.clipboard.writeText(combinedPrompt);
  };

  const handleDownloadFrame = (frameUrl: string, frameId: string) => {
    const link = document.createElement('a');
    link.href = frameUrl;
    link.download = `pika-frame-${frameId}.png`;
    link.click();
  };

  const resolutionOptions: { value: PikaResolution; label: string }[] = [
    { value: '720p', label: '720p (1280x720)' },
    { value: '1080p', label: '1080p (1920x1080)' },
    { value: '1440p', label: '1440p (2560x1440)' },
    { value: '4K', label: '4K (3840x2160)' },
  ];

  const commonAspectRatios = [
    { value: 1.7778, label: '16:9 (Widescreen)' },
    { value: 1.3333, label: '4:3 (Standard)' },
    { value: 1.0, label: '1:1 (Square)' },
    { value: 0.5625, label: '9:16 (Vertical)' },
    { value: 2.4, label: '21:9 (Ultrawide)' },
  ];

  return (
    <div className="space-y-6">
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
      <Alert className="glass-morphism">
        <Film className="h-4 w-4" />
        <AlertDescription>
          <strong>💡 Future Video Upgrade:</strong> This component extracts single frames from Pika's video generation. 
          To upgrade to full video generation, simply change <code>video: false</code> to <code>video: true</code> in the API call 
          and handle the video response format instead of extracting frames.
        </AlertDescription>
      </Alert>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Settings Panel */}
        <Card className="glass-morphism">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              Generation Settings
              <Button 
                variant="outline" 
                size="sm"
                onClick={actions.resetSettings}
                className="text-xs"
              >
                Reset
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Prompt Input */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="prompt">Prompt *</Label>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleCopyPrompt}
                  className="text-xs"
                >
                  <Copy className="w-3 h-3 mr-1" />
                  Copy
                </Button>
              </div>
              <Textarea
                id="prompt"
                placeholder="Describe the scene you want to generate..."
                value={settings.prompt_text}
                onChange={(e) => actions.setPrompt(e.target.value)}
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
                value={settings.negative_prompt}
                onChange={(e) => actions.setNegativePrompt(e.target.value)}
                className="glass-morphism"
                rows={2}
              />
            </div>

            {/* Seed */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="seed">Seed</Label>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={actions.generateRandomSeed}
                  className="text-xs"
                >
                  <Shuffle className="w-3 h-3 mr-1" />
                  Random
                </Button>
              </div>
              <Input
                id="seed"
                type="number"
                value={settings.seed}
                onChange={(e) => actions.setSeed(parseInt(e.target.value) || 0)}
                className="glass-morphism"
              />
            </div>

            {/* Resolution */}
            <div className="space-y-2">
              <Label>Resolution</Label>
              <Select 
                value={settings.resolution} 
                onValueChange={(value) => actions.setResolution(value as PikaResolution)}
              >
                <SelectTrigger className="glass-morphism">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {resolutionOptions.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Aspect Ratio */}
            <div className="space-y-2">
              <Label>Aspect Ratio: {getAspectRatioDisplayName(settings.aspect_ratio)}</Label>
              <div className="space-y-2">
                <Slider
                  value={[settings.aspect_ratio]}
                  onValueChange={(value) => actions.setAspectRatio(value[0])}
                  min={0.4}
                  max={2.5}
                  step={0.1}
                  className="glass-morphism"
                />
                <div className="flex gap-1 flex-wrap">
                  {commonAspectRatios.map((ratio) => (
                    <Button
                      key={ratio.value}
                      variant="outline"
                      size="sm"
                      onClick={() => actions.setAspectRatio(ratio.value)}
                      className="text-xs"
                    >
                      {ratio.label}
                    </Button>
                  ))}
                </div>
              </div>
            </div>

            {/* Motion Strength (for future video upgrade) */}
            <div className="space-y-2">
              <Label>Motion Strength: {settings.motion_strength.toFixed(2)}</Label>
              <Slider
                value={[settings.motion_strength]}
                onValueChange={(value) => actions.setMotionStrength(value[0])}
                min={0}
                max={1}
                step={0.1}
                className="glass-morphism"
              />
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
              disabled={isGenerating || !settings.prompt_text.trim()}
              className="w-full cyber-button"
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

            {/* Progress */}
            {isGenerating && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Progress</span>
                  <span>{Math.round(progress)}%</span>
                </div>
                <Progress value={progress} className="glass-morphism" />
              </div>
            )}

            {/* Error Display */}
            {error && (
              <Alert variant="destructive" className="glass-morphism">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {/* Generated Frames */}
            {frames.length > 0 && (
              <div className="space-y-3">
                <h3 className="font-semibold">Generated Frames ({frames.length})</h3>
                <div className="grid gap-3">
                  {frames.slice(0, 5).map((frame) => (
                    <Card key={frame.id} className="glass-morphism">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium">
                            Frame {frame.id.split('-').pop()}
                          </span>
                          <div className="flex gap-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleDownloadFrame(frame.frame_url, frame.id)}
                              className="text-xs"
                            >
                              <Download className="w-3 h-3" />
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => actions.removeFrame(frame.id)}
                              className="text-xs"
                            >
                              Remove
                            </Button>
                          </div>
                        </div>
                        <div className="aspect-video bg-muted rounded-lg overflow-hidden">
                          <img 
                            src={frame.frame_url} 
                            alt={frame.prompt}
                            className="w-full h-full object-cover"
                            onError={(e) => {
                              (e.target as HTMLImageElement).src = '/placeholder-frame.png';
                            }}
                          />
                        </div>
                        <p className="text-xs text-muted-foreground mt-2 truncate">
                          {frame.prompt}
                        </p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
                
                {frames.length > 5 && (
                  <p className="text-xs text-muted-foreground text-center">
                    ... and {frames.length - 5} more frames
                  </p>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default PikaFrameGenerator;