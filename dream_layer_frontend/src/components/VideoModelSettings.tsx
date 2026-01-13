import React, { useEffect } from 'react';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import { Input } from '@/components/ui/input';
import { Volume2, VolumeX } from 'lucide-react';

interface VideoModelSettingsProps {
  model: 'luma' | 'runway';
  // Luma settings
  lumaModel?: string;
  aspectRatio?: string;
  loop?: boolean;
  resolution?: '180p' | '360p' | '540p' | '720p' | '1080p' | '4k';
  // Runway settings
  runwayMode?: 'text2vid' | 'img2vid';
  runwayModel?: string;
  ratio?: string;
  duration?: number;
  seed?: number;
  audio?: boolean;
  inputImage?: string;
  // Callbacks
  onModelChange: (model: 'luma' | 'runway') => void;
  onLumaModelChange?: (model: string) => void;
  onAspectRatioChange?: (ratio: string) => void;
  onLoopChange?: (loop: boolean) => void;
  onResolutionChange?: (resolution: string) => void;
  onRunwayModeChange?: (mode: 'text2vid' | 'img2vid') => void;
  onRunwayModelChange?: (model: string) => void;
  onRatioChange?: (ratio: string) => void;
  onDurationChange?: (duration: number) => void;
  onSeedChange?: (seed: number) => void;
  onAudioChange?: (audio: boolean) => void;
  onInputImageChange?: (image: string) => void;
  onCreditsCalculated?: (credits: number) => void;
}

const VideoModelSettings: React.FC<VideoModelSettingsProps> = ({
  model,
  lumaModel = 'ray-2',
  aspectRatio = '16:9',
  loop = true,
  resolution = '1080p',
  runwayMode = 'text2vid',
  runwayModel = 'veo3.1',
  ratio = '1280:720',
  duration = 6,
  seed = -1,
  audio = false,
  inputImage,
  onModelChange,
  onLumaModelChange,
  onAspectRatioChange,
  onLoopChange,
  onResolutionChange,
  onRunwayModeChange,
  onRunwayModelChange,
  onRatioChange,
  onDurationChange,
  onSeedChange,
  onAudioChange,
  onInputImageChange,
  onCreditsCalculated,
}) => {
  // Calculate Runway credits whenever settings change
  useEffect(() => {
    if (model === 'runway' && onCreditsCalculated) {
      const calculateCredits = () => {
        let creditsPerSecond = 20; // Default for veo3.1 without audio

        // Determine credits per second based on model and audio
        if (runwayModel === 'veo3.1') {
          creditsPerSecond = audio ? 40 : 20;
        } else if (runwayModel === 'veo3.1_fast') {
          creditsPerSecond = audio ? 15 : 10;
        } else if (runwayModel === 'veo3') {
          creditsPerSecond = audio ? 40 : 20;
        } else if (runwayModel === 'gen4_turbo') {
          creditsPerSecond = 5; // No audio option for gen4
        } else if (runwayModel === 'gen3a_turbo') {
          creditsPerSecond = 5; // No audio option for gen3a
        } else if (runwayModel === 'gen4_aleph') {
          creditsPerSecond = 15; // No audio option for gen4_aleph
        }

        const totalCredits = creditsPerSecond * (duration || 6);
        return totalCredits;
      };

      onCreditsCalculated(calculateCredits());
    }
  }, [model, runwayModel, duration, audio, onCreditsCalculated]);

  return (
    <div className="space-y-4">
      {/* Luma-specific settings */}
      {model === 'luma' && (
        <>
          <div className="space-y-2">
            <Label htmlFor="luma-model">Luma Model</Label>
            <Select value={lumaModel} onValueChange={onLumaModelChange}>
              <SelectTrigger id="luma-model">
                <SelectValue placeholder="Select Luma model" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ray-2">Ray 2</SelectItem>
                <SelectItem value="ray-flash-2">Ray 2 Flash (Faster)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="aspect-ratio">Aspect Ratio</Label>
            <Select value={aspectRatio} onValueChange={onAspectRatioChange}>
              <SelectTrigger id="aspect-ratio">
                <SelectValue placeholder="Select aspect ratio" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="16:9">16:9 (Landscape)</SelectItem>
                <SelectItem value="9:16">9:16 (Portrait)</SelectItem>
                <SelectItem value="4:3">4:3</SelectItem>
                <SelectItem value="3:4">3:4</SelectItem>
                <SelectItem value="21:9">21:9 (Ultrawide)</SelectItem>
                <SelectItem value="9:21">9:21</SelectItem>
                <SelectItem value="1:1">1:1 (Square)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="resolution">Resolution Quality</Label>
            <Select value={resolution} onValueChange={onResolutionChange}>
              <SelectTrigger id="resolution">
                <SelectValue placeholder="Select resolution" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="4k">4K (Ultra HD)</SelectItem>
                <SelectItem value="1080p">1080p (Full HD)</SelectItem>
                <SelectItem value="720p">720p (HD)</SelectItem>
                <SelectItem value="540p">540p</SelectItem>
                <SelectItem value="360p">360p</SelectItem>
                <SelectItem value="180p">180p</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-center space-x-2">
            <Switch
              id="loop"
              checked={loop}
              onCheckedChange={onLoopChange}
            />
            <Label htmlFor="loop" className="cursor-pointer">Enable Loop</Label>
          </div>
        </>
      )}

      {/* Runway-specific settings */}
      {model === 'runway' && (
        <>
          <div className="space-y-2">
            <Label htmlFor="runway-model">Runway Model</Label>
            <Select value={runwayModel} onValueChange={onRunwayModelChange}>
              <SelectTrigger id="runway-model">
                <SelectValue placeholder="Select Runway model" />
              </SelectTrigger>
              <SelectContent>
                {runwayMode === 'text2vid' ? (
                  <>
                    <SelectItem value="veo3.1">Veo 3.1 (20 credits/sec)</SelectItem>
                    <SelectItem value="veo3.1_fast">Veo 3.1 Fast (10 credits/sec)</SelectItem>
                    <SelectItem value="veo3">Veo 3 (20 credits/sec)</SelectItem>
                  </>
                ) : (
                  <>
                    <SelectItem value="gen4_turbo">Gen-4 Turbo (5 credits/sec)</SelectItem>
                    <SelectItem value="gen3a_turbo">Gen-3 Alpha Turbo (5 credits/sec)</SelectItem>
                    <SelectItem value="veo3.1">Veo 3.1 (20 credits/sec)</SelectItem>
                    <SelectItem value="veo3.1_fast">Veo 3.1 Fast (10 credits/sec)</SelectItem>
                    <SelectItem value="veo3">Veo 3 (20 credits/sec)</SelectItem>
                  </>
                )}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="ratio">Video Ratio</Label>
            <Select value={ratio} onValueChange={onRatioChange}>
              <SelectTrigger id="ratio">
                <SelectValue placeholder="Select ratio" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1280:720">1280:720 (16:9 Landscape)</SelectItem>
                <SelectItem value="720:1280">720:1280 (9:16 Portrait)</SelectItem>
                <SelectItem value="1920:1080">1920:1080 (16:9 HD)</SelectItem>
                <SelectItem value="1080:1920">1080:1920 (9:16 HD)</SelectItem>
                {runwayMode === 'img2vid' && (
                  <>
                    <SelectItem value="1104:832">1104:832 (4:3 Landscape)</SelectItem>
                    <SelectItem value="832:1104">832:1104 (3:4 Portrait)</SelectItem>
                    <SelectItem value="960:960">960:960 (1:1 Square)</SelectItem>
                    <SelectItem value="1584:672">1584:672 (21:9 Ultrawide)</SelectItem>
                  </>
                )}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="duration">Duration: {duration}s</Label>
            <Select value={String(duration)} onValueChange={(value) => onDurationChange?.(parseInt(value))}>
              <SelectTrigger id="duration">
                <SelectValue placeholder="Select duration" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="4">4 seconds</SelectItem>
                <SelectItem value="6">6 seconds</SelectItem>
                <SelectItem value="8">8 seconds</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="seed">Seed</Label>
            <Input
              id="seed"
              type="number"
              value={seed}
              onChange={(e) => onSeedChange?.(parseInt(e.target.value) || -1)}
              placeholder="-1 for random"
            />
            <p className="text-xs text-muted-foreground">Use -1 for random seed</p>
          </div>

          {/* Audio toggle - only for veo models */}
          {(runwayModel === 'veo3.1' || runwayModel === 'veo3.1_fast' || runwayModel === 'veo3') && (
            <div className="space-y-2">
              <Label>Audio Generation</Label>
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-muted-foreground">{audio ? 'On' : 'Off'}</span>
                <button
                  type="button"
                  onClick={() => onAudioChange?.(!audio)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 ${
                    audio ? 'bg-primary' : 'bg-gray-200'
                  }`}
                  aria-label="Toggle audio generation"
                >
                  <span className="sr-only">Toggle audio generation</span>
                  <span
                    className={`${
                      audio ? 'translate-x-6' : 'translate-x-1'
                    } inline-block h-4 w-4 transform rounded-full bg-white transition-transform`}
                  />
                  {audio && (
                    <span className="absolute right-1.5 top-1/2 -translate-y-1/2">
                      <Volume2 className="h-3 w-3 text-white" />
                    </span>
                  )}
                  {!audio && (
                    <span className="absolute left-1.5 top-1/2 -translate-y-1/2">
                      <VolumeX className="h-3 w-3 text-gray-500" />
                    </span>
                  )}
                </button>
              </div>
              <p className="text-xs text-muted-foreground">Costs 2x credits (40 vs 20 credits/sec for veo3.1)</p>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default VideoModelSettings;
