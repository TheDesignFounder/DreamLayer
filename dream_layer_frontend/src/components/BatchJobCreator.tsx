import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Switch } from '@/components/ui/switch';
import { useBatchProcessingStore } from '@/stores/useBatchProcessingStore';
import { BatchJob } from '@/types/batchProcessing';
import { Plus, X, Copy, Settings, Wand2 } from 'lucide-react';

interface BatchJobCreatorProps {
  currentPrompt?: string;
  currentNegativePrompt?: string;
  currentSettings?: Record<string, any>;
  type: 'txt2img' | 'img2img';
  inputImage?: string;
}

interface PromptVariation {
  id: string;
  prompt: string;
  weight?: number;
}

interface SettingVariation {
  id: string;
  name: string;
  settings: Record<string, any>;
}

const BatchJobCreator: React.FC<BatchJobCreatorProps> = ({
  currentPrompt = '',
  currentNegativePrompt = '',
  currentSettings = {},
  type,
  inputImage
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [jobName, setJobName] = useState('');
  const [basePrompt, setBasePrompt] = useState(currentPrompt);
  const [baseNegativePrompt, setBaseNegativePrompt] = useState(currentNegativePrompt);
  const [totalImages, setTotalImages] = useState(10);
  
  // Prompt variations
  const [promptVariations, setPromptVariations] = useState<PromptVariation[]>([]);
  const [newPromptVariation, setNewPromptVariation] = useState('');
  
  // Settings variations
  const [settingVariations, setSettingVariations] = useState<SettingVariation[]>([]);
  const [useSettingVariations, setUseSettingVariations] = useState(false);
  
  // Advanced options
  const [generateVariations, setGenerateVariations] = useState(false);
  const [variationCount, setVariationCount] = useState(5);
  
  const { addJob, addToQueue, startProcessing } = useBatchProcessingStore();

  const addPromptVariation = () => {
    if (newPromptVariation.trim()) {
      const variation: PromptVariation = {
        id: `variation-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        prompt: newPromptVariation.trim(),
        weight: 1.0
      };
      setPromptVariations(prev => [...prev, variation]);
      setNewPromptVariation('');
    }
  };

  const removePromptVariation = (id: string) => {
    setPromptVariations(prev => prev.filter(v => v.id !== id));
  };

  const addSettingVariation = () => {
    const variation: SettingVariation = {
      id: `setting-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name: `Variation ${settingVariations.length + 1}`,
      settings: { ...currentSettings }
    };
    setSettingVariations(prev => [...prev, variation]);
  };

  const removeSettingVariation = (id: string) => {
    setSettingVariations(prev => prev.filter(v => v.id !== id));
  };

  const updateSettingVariation = (id: string, key: string, value: any) => {
    setSettingVariations(prev => prev.map(variation =>
      variation.id === id
        ? { ...variation, settings: { ...variation.settings, [key]: value } }
        : variation
    ));
  };

  const generatePromptVariations = () => {
    const variations: PromptVariation[] = [];
    const adjectives = ['beautiful', 'stunning', 'magnificent', 'ethereal', 'dramatic'];
    const styles = ['photorealistic', 'artistic', 'cinematic', 'detailed', 'vibrant'];
    
    for (let i = 0; i < variationCount; i++) {
      const adjective = adjectives[Math.floor(Math.random() * adjectives.length)];
      const style = styles[Math.floor(Math.random() * styles.length)];
      const variation: PromptVariation = {
        id: `auto-${Date.now()}-${i}`,
        prompt: `${basePrompt}, ${adjective}, ${style}`,
        weight: 1.0
      };
      variations.push(variation);
    }
    
    setPromptVariations(variations);
  };

  const createBatchJob = () => {
    if (!jobName.trim()) {
      alert('Please enter a job name');
      return;
    }

    const job: Omit<BatchJob, 'id' | 'createdAt' | 'status' | 'progress' | 'results' | 'completedImages'> = {
      name: jobName.trim(),
      type,
      settings: {
        ...currentSettings,
        prompt: basePrompt,
        negative_prompt: baseNegativePrompt
      },
      inputImage,
      totalImages,
      error: undefined
    };

    const jobId = addJob(job);
    const createdJob = useBatchProcessingStore.getState().getJob(jobId);
    
    if (createdJob) {
      const prompts = promptVariations.length > 0 
        ? promptVariations.map(v => v.prompt)
        : [basePrompt];
      
      const settings = useSettingVariations && settingVariations.length > 0
        ? settingVariations.map(v => v.settings)
        : [currentSettings];

      addToQueue(createdJob, prompts, settings);
    }

    // Reset form
    setJobName('');
    setPromptVariations([]);
    setSettingVariations([]);
    setNewPromptVariation('');
    setUseSettingVariations(false);
    setGenerateVariations(false);
    
    setIsOpen(false);
  };

  const previewVariations = () => {
    const prompts = promptVariations.length > 0 ? promptVariations : [{ prompt: basePrompt }];
    const settings = useSettingVariations && settingVariations.length > 0 ? settingVariations : [{ settings: currentSettings }];
    
    return prompts.length * settings.length;
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <Plus className="h-4 w-4 mr-2" />
          Create Batch
        </Button>
      </DialogTrigger>
      
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Create Batch Job - {type.toUpperCase()}</DialogTitle>
        </DialogHeader>
        
        <div className="space-y-6">
          {/* Basic Settings */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Basic Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="jobName">Job Name *</Label>
                  <Input
                    id="jobName"
                    placeholder="Enter job name"
                    value={jobName}
                    onChange={(e) => setJobName(e.target.value)}
                  />
                </div>
                
                <div>
                  <Label htmlFor="totalImages">Total Images</Label>
                  <Input
                    id="totalImages"
                    type="number"
                    min="1"
                    max="100"
                    value={totalImages}
                    onChange={(e) => setTotalImages(parseInt(e.target.value) || 1)}
                  />
                </div>
              </div>
              
              <div>
                <Label htmlFor="basePrompt">Base Prompt</Label>
                <Textarea
                  id="basePrompt"
                  placeholder="Enter base prompt"
                  value={basePrompt}
                  onChange={(e) => setBasePrompt(e.target.value)}
                  rows={3}
                />
              </div>
              
              <div>
                <Label htmlFor="baseNegativePrompt">Base Negative Prompt</Label>
                <Textarea
                  id="baseNegativePrompt"
                  placeholder="Enter base negative prompt"
                  value={baseNegativePrompt}
                  onChange={(e) => setBaseNegativePrompt(e.target.value)}
                  rows={2}
                />
              </div>
            </CardContent>
          </Card>
          
          {/* Prompt Variations */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-sm">Prompt Variations</CardTitle>
                  <CardDescription>Create different prompt variations for diverse results</CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex items-center space-x-2">
                    <Switch
                      id="generateVariations"
                      checked={generateVariations}
                      onCheckedChange={setGenerateVariations}
                    />
                    <Label htmlFor="generateVariations" className="text-xs">Auto-generate</Label>
                  </div>
                  {generateVariations && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={generatePromptVariations}
                    >
                      <Wand2 className="h-4 w-4 mr-2" />
                      Generate {variationCount}
                    </Button>
                  )}
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {generateVariations && (
                <div className="flex items-center gap-2">
                  <Label htmlFor="variationCount" className="text-xs">Count:</Label>
                  <Input
                    id="variationCount"
                    type="number"
                    min="1"
                    max="20"
                    value={variationCount}
                    onChange={(e) => setVariationCount(parseInt(e.target.value) || 5)}
                    className="w-20"
                  />
                </div>
              )}
              
              {!generateVariations && (
                <div className="flex gap-2">
                  <Input
                    placeholder="Add prompt variation"
                    value={newPromptVariation}
                    onChange={(e) => setNewPromptVariation(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && addPromptVariation()}
                  />
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={addPromptVariation}
                    disabled={!newPromptVariation.trim()}
                  >
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
              )}
              
              {promptVariations.length > 0 && (
                <div className="space-y-2">
                  <Label className="text-xs">Variations ({promptVariations.length}):</Label>
                  <div className="space-y-2 max-h-32 overflow-y-auto">
                    {promptVariations.map((variation) => (
                      <div key={variation.id} className="flex items-center gap-2 p-2 border rounded">
                        <span className="text-xs flex-1 truncate">{variation.prompt}</span>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-6 w-6 p-0"
                          onClick={() => removePromptVariation(variation.id)}
                        >
                          <X className="h-3 w-3" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
          
          {/* Settings Variations */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-sm">Settings Variations</CardTitle>
                  <CardDescription>Create different setting combinations</CardDescription>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="useSettingVariations"
                    checked={useSettingVariations}
                    onCheckedChange={setUseSettingVariations}
                  />
                  <Label htmlFor="useSettingVariations" className="text-xs">Enable</Label>
                </div>
              </div>
            </CardHeader>
            {useSettingVariations && (
              <CardContent className="space-y-4">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={addSettingVariation}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add Setting Variation
                </Button>
                
                {settingVariations.length > 0 && (
                  <div className="space-y-3">
                    {settingVariations.map((variation) => (
                      <Card key={variation.id} className="p-3">
                        <div className="flex items-center justify-between mb-2">
                          <Label className="text-xs font-medium">{variation.name}</Label>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 w-6 p-0"
                            onClick={() => removeSettingVariation(variation.id)}
                          >
                            <X className="h-3 w-3" />
                          </Button>
                        </div>
                        <div className="grid grid-cols-2 gap-2">
                          <div>
                            <Label className="text-xs">CFG Scale</Label>
                            <Input
                              type="number"
                              step="0.1"
                              value={variation.settings.cfg_scale || 7}
                              onChange={(e) => updateSettingVariation(variation.id, 'cfg_scale', parseFloat(e.target.value))}
                              className="h-8 text-xs"
                            />
                          </div>
                          <div>
                            <Label className="text-xs">Steps</Label>
                            <Input
                              type="number"
                              value={variation.settings.steps || 20}
                              onChange={(e) => updateSettingVariation(variation.id, 'steps', parseInt(e.target.value))}
                              className="h-8 text-xs"
                            />
                          </div>
                        </div>
                      </Card>
                    ))}
                  </div>
                )}
              </CardContent>
            )}
          </Card>
          
          {/* Preview */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Preview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-4 text-sm">
                <div>
                  <span className="text-muted-foreground">Total combinations:</span>
                  <Badge variant="outline" className="ml-2">
                    {previewVariations()}
                  </Badge>
                </div>
                <div>
                  <span className="text-muted-foreground">Total images:</span>
                  <Badge variant="outline" className="ml-2">
                    {totalImages}
                  </Badge>
                </div>
                <div>
                  <span className="text-muted-foreground">Estimated time:</span>
                  <Badge variant="outline" className="ml-2">
                    {Math.round(totalImages * 3 / 60)}min
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
          
          {/* Actions */}
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setIsOpen(false)}>
              Cancel
            </Button>
            <Button onClick={createBatchJob} disabled={!jobName.trim()}>
              Create Batch Job
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default BatchJobCreator;