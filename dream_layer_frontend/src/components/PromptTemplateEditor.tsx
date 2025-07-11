import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Switch } from '@/components/ui/switch';
import { usePromptTemplateStore } from '@/stores/usePromptTemplateStore';
import { PromptTemplate } from '@/types/promptTemplate';
import { X, Plus, Save, Copy, Eye, EyeOff } from 'lucide-react';

interface PromptTemplateEditorProps {
  template: PromptTemplate | null;
  isOpen: boolean;
  onClose: () => void;
  onSave?: (template: PromptTemplate) => void;
}

const PromptTemplateEditor: React.FC<PromptTemplateEditorProps> = ({
  template,
  isOpen,
  onClose,
  onSave
}) => {
  const [formData, setFormData] = useState<Partial<PromptTemplate>>({
    name: '',
    description: '',
    prompt: '',
    negativePrompt: '',
    category: 'custom',
    tags: [],
    settings: {}
  });
  
  const [newTag, setNewTag] = useState('');
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  
  const { categories, addTemplate, updateTemplate } = usePromptTemplateStore();
  
  useEffect(() => {
    if (template) {
      setFormData({
        name: template.name,
        description: template.description || '',
        prompt: template.prompt,
        negativePrompt: template.negativePrompt || '',
        category: template.category,
        tags: [...template.tags],
        settings: { ...template.settings }
      });
    } else {
      setFormData({
        name: '',
        description: '',
        prompt: '',
        negativePrompt: '',
        category: 'custom',
        tags: [],
        settings: {}
      });
    }
    setErrors({});
  }, [template]);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.name?.trim()) {
      newErrors.name = 'Template name is required';
    }
    
    if (!formData.prompt?.trim()) {
      newErrors.prompt = 'Prompt is required';
    }
    
    if (!formData.category) {
      newErrors.category = 'Category is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = () => {
    if (!validateForm()) return;
    
    const templateData = {
      ...formData,
      name: formData.name!.trim(),
      prompt: formData.prompt!.trim(),
      negativePrompt: formData.negativePrompt?.trim() || '',
      description: formData.description?.trim() || '',
      category: formData.category!,
      tags: formData.tags || [],
      settings: formData.settings || {}
    };
    
    if (template) {
      updateTemplate(template.id, templateData);
    } else {
      addTemplate(templateData);
    }
    
    onSave?.(templateData as PromptTemplate);
    onClose();
  };

  const handleAddTag = () => {
    if (newTag.trim() && !formData.tags?.includes(newTag.trim())) {
      setFormData(prev => ({
        ...prev,
        tags: [...(prev.tags || []), newTag.trim()]
      }));
      setNewTag('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags?.filter(tag => tag !== tagToRemove) || []
    }));
  };

  const handleSettingChange = (key: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      settings: {
        ...prev.settings,
        [key]: value
      }
    }));
  };

  const handleKeyPress = (e: React.KeyboardEvent, action: () => void) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      action();
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {template ? 'Edit Template' : 'Create New Template'}
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-6">
          {/* Basic Information */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Basic Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="name">Template Name *</Label>
                  <Input
                    id="name"
                    placeholder="Enter template name"
                    value={formData.name || ''}
                    onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                    className={errors.name ? 'border-red-500' : ''}
                  />
                  {errors.name && <p className="text-red-500 text-xs mt-1">{errors.name}</p>}
                </div>
                
                <div>
                  <Label htmlFor="category">Category *</Label>
                  <Select
                    value={formData.category}
                    onValueChange={(value) => setFormData(prev => ({ ...prev, category: value }))}
                  >
                    <SelectTrigger className={errors.category ? 'border-red-500' : ''}>
                      <SelectValue placeholder="Select category" />
                    </SelectTrigger>
                    <SelectContent>
                      {categories.map(category => (
                        <SelectItem key={category.id} value={category.id}>
                          {category.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {errors.category && <p className="text-red-500 text-xs mt-1">{errors.category}</p>}
                </div>
              </div>
              
              <div>
                <Label htmlFor="description">Description</Label>
                <Input
                  id="description"
                  placeholder="Brief description of the template"
                  value={formData.description || ''}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                />
              </div>
            </CardContent>
          </Card>
          
          {/* Prompts */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Prompts</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="prompt">Positive Prompt *</Label>
                <Textarea
                  id="prompt"
                  placeholder="Enter the main prompt"
                  value={formData.prompt || ''}
                  onChange={(e) => setFormData(prev => ({ ...prev, prompt: e.target.value }))}
                  rows={4}
                  className={errors.prompt ? 'border-red-500' : ''}
                />
                {errors.prompt && <p className="text-red-500 text-xs mt-1">{errors.prompt}</p>}
              </div>
              
              <div>
                <Label htmlFor="negativePrompt">Negative Prompt</Label>
                <Textarea
                  id="negativePrompt"
                  placeholder="Enter negative prompt (optional)"
                  value={formData.negativePrompt || ''}
                  onChange={(e) => setFormData(prev => ({ ...prev, negativePrompt: e.target.value }))}
                  rows={3}
                />
              </div>
            </CardContent>
          </Card>
          
          {/* Tags */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Tags</CardTitle>
              <CardDescription>Add tags to help organize and search templates</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex gap-2">
                  <Input
                    placeholder="Add a tag"
                    value={newTag}
                    onChange={(e) => setNewTag(e.target.value)}
                    onKeyPress={(e) => handleKeyPress(e, handleAddTag)}
                    className="flex-1"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={handleAddTag}
                    disabled={!newTag.trim()}
                  >
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
                
                {formData.tags && formData.tags.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {formData.tags.map((tag, index) => (
                      <Badge key={index} variant="secondary" className="flex items-center gap-1">
                        {tag}
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-4 w-4 p-0 hover:bg-destructive hover:text-destructive-foreground"
                          onClick={() => handleRemoveTag(tag)}
                        >
                          <X className="h-3 w-3" />
                        </Button>
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
          
          {/* Advanced Settings */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm">Generation Settings</CardTitle>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowAdvancedSettings(!showAdvancedSettings)}
                >
                  {showAdvancedSettings ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  {showAdvancedSettings ? 'Hide' : 'Show'}
                </Button>
              </div>
              <CardDescription>
                Optional generation settings to apply with this template
              </CardDescription>
            </CardHeader>
            {showAdvancedSettings && (
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="cfg_scale">CFG Scale</Label>
                    <Input
                      id="cfg_scale"
                      type="number"
                      step="0.1"
                      min="1"
                      max="20"
                      value={formData.settings?.cfg_scale || ''}
                      onChange={(e) => handleSettingChange('cfg_scale', parseFloat(e.target.value) || undefined)}
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="steps">Steps</Label>
                    <Input
                      id="steps"
                      type="number"
                      min="1"
                      max="150"
                      value={formData.settings?.steps || ''}
                      onChange={(e) => handleSettingChange('steps', parseInt(e.target.value) || undefined)}
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="width">Width</Label>
                    <Input
                      id="width"
                      type="number"
                      step="64"
                      min="64"
                      max="2048"
                      value={formData.settings?.width || ''}
                      onChange={(e) => handleSettingChange('width', parseInt(e.target.value) || undefined)}
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="height">Height</Label>
                    <Input
                      id="height"
                      type="number"
                      step="64"
                      min="64"
                      max="2048"
                      value={formData.settings?.height || ''}
                      onChange={(e) => handleSettingChange('height', parseInt(e.target.value) || undefined)}
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="sampler">Sampler</Label>
                    <Select
                      value={formData.settings?.sampler_name || ''}
                      onValueChange={(value) => handleSettingChange('sampler_name', value || undefined)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select sampler" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="">Default</SelectItem>
                        <SelectItem value="Euler">Euler</SelectItem>
                        <SelectItem value="Euler a">Euler a</SelectItem>
                        <SelectItem value="DPM++ 2M Karras">DPM++ 2M Karras</SelectItem>
                        <SelectItem value="DPM++ SDE Karras">DPM++ SDE Karras</SelectItem>
                        <SelectItem value="DDIM">DDIM</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div>
                    <Label htmlFor="scheduler">Scheduler</Label>
                    <Select
                      value={formData.settings?.scheduler || ''}
                      onValueChange={(value) => handleSettingChange('scheduler', value || undefined)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select scheduler" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="">Default</SelectItem>
                        <SelectItem value="normal">Normal</SelectItem>
                        <SelectItem value="karras">Karras</SelectItem>
                        <SelectItem value="exponential">Exponential</SelectItem>
                        <SelectItem value="sgm_uniform">SGM Uniform</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CardContent>
            )}
          </Card>
          
          {/* Actions */}
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button onClick={handleSave}>
              <Save className="h-4 w-4 mr-2" />
              {template ? 'Update' : 'Create'} Template
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default PromptTemplateEditor;