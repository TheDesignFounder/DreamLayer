import React, { useState, useEffect } from 'react';
import { usePresetStore } from '../stores/usePresetStore';
import { Preset, PresetCreateRequest } from '../types/preset';
import { CoreGenerationSettings } from '../types/generationSettings';
import { ControlNetRequest } from '../types/controlnet';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from './ui/alert-dialog';
import { Plus, Edit, Trash2, Save, X, Check } from 'lucide-react';
import { useToast } from '../hooks/use-toast';

interface PresetManagerProps {
  currentSettings: CoreGenerationSettings;
  currentControlnet?: ControlNetRequest;
  onPresetApplied?: (settings: CoreGenerationSettings, controlnet?: ControlNetRequest) => void;
}

export const PresetManager: React.FC<PresetManagerProps> = ({
  currentSettings,
  currentControlnet,
  onPresetApplied
}) => {
  const { toast } = useToast();
  const {
    presets,
    selectedPresetId,
    initializeDefaultPresets,
    createPreset,
    updatePreset,
    deletePreset,
    selectPreset,
    getSelectedPreset,
    generatePresetHash
  } = usePresetStore();

  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [editingPreset, setEditingPreset] = useState<Preset | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    description: ''
  });

  useEffect(() => {
    initializeDefaultPresets();
  }, [initializeDefaultPresets]);

  const handleCreatePreset = () => {
    if (!formData.name.trim()) {
      toast({
        title: "Error",
        description: "Preset name is required",
        variant: "destructive"
      });
      return;
    }

    const presetData: PresetCreateRequest = {
      name: formData.name.trim(),
      description: formData.description.trim() || undefined,
      settings: currentSettings,
      controlnet: currentControlnet
    };

    const newPreset = createPreset(presetData);
    selectPreset(newPreset.id);
    
    toast({
      title: "Success",
      description: `Preset "${newPreset.name}" created successfully`
    });

    setFormData({ name: '', description: '' });
    setIsCreateDialogOpen(false);
  };

  const handleEditPreset = (preset: Preset) => {
    setEditingPreset(preset);
    setFormData({
      name: preset.name,
      description: preset.description || ''
    });
    setIsEditDialogOpen(true);
  };

  const handleUpdatePreset = () => {
    if (!editingPreset || !formData.name.trim()) {
      toast({
        title: "Error",
        description: "Preset name is required",
        variant: "destructive"
      });
      return;
    }

    const updated = updatePreset(editingPreset.id, {
      name: formData.name.trim(),
      description: formData.description.trim() || undefined,
      settings: currentSettings,
      controlnet: currentControlnet
    });

    if (updated) {
      toast({
        title: "Success",
        description: `Preset "${updated.name}" updated successfully`
      });
    }

    setFormData({ name: '', description: '' });
    setEditingPreset(null);
    setIsEditDialogOpen(false);
  };

  const handleDeletePreset = (preset: Preset) => {
    if (preset.is_default) {
      toast({
        title: "Cannot Delete",
        description: "Default presets cannot be deleted",
        variant: "destructive"
      });
      return;
    }

    deletePreset(preset.id);
    toast({
      title: "Success",
      description: `Preset "${preset.name}" deleted successfully`
    });
  };

  const handleSelectPreset = (preset: Preset) => {
    selectPreset(preset.id);
    onPresetApplied?.(preset.settings, preset.controlnet);
    toast({
      title: "Preset Applied",
      description: `Applied preset "${preset.name}"`
    });
  };

  const selectedPreset = getSelectedPreset();

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Presets</h3>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button size="sm" className="flex items-center gap-2">
              <Plus className="h-4 w-4" />
              Create Preset
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Preset</DialogTitle>
              <DialogDescription>
                Save current settings as a new preset for quick access.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="preset-name">Name</Label>
                <Input
                  id="preset-name"
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="Enter preset name"
                />
              </div>
              <div>
                <Label htmlFor="preset-description">Description (Optional)</Label>
                <Textarea
                  id="preset-description"
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Enter description"
                  rows={3}
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleCreatePreset}>
                Create Preset
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <div className="space-y-2">
        {presets.map((preset) => (
          <Card key={preset.id} className={`transition-all ${selectedPresetId === preset.id ? 'ring-2 ring-primary' : ''}`}>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <CardTitle className="text-base">{preset.name}</CardTitle>
                  {preset.is_default && (
                    <Badge variant="secondary" className="text-xs">Default</Badge>
                  )}
                  <Badge variant="outline" className="text-xs">v{preset.version}</Badge>
                </div>
                <div className="flex items-center gap-1">
                  {selectedPresetId === preset.id && (
                    <Check className="h-4 w-4 text-primary" />
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleSelectPreset(preset)}
                    disabled={selectedPresetId === preset.id}
                  >
                    {selectedPresetId === preset.id ? 'Selected' : 'Select'}
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleEditPreset(preset)}
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  {!preset.is_default && (
                    <AlertDialog>
                      <AlertDialogTrigger asChild>
                        <Button variant="ghost" size="sm">
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </AlertDialogTrigger>
                      <AlertDialogContent>
                        <AlertDialogHeader>
                          <AlertDialogTitle>Delete Preset</AlertDialogTitle>
                          <AlertDialogDescription>
                            Are you sure you want to delete "{preset.name}"? This action cannot be undone.
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel>Cancel</AlertDialogCancel>
                          <AlertDialogAction onClick={() => handleDeletePreset(preset)}>
                            Delete
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  )}
                </div>
              </div>
              {preset.description && (
                <CardDescription>{preset.description}</CardDescription>
              )}
            </CardHeader>
          </Card>
        ))}
      </div>

      {/* Edit Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Preset</DialogTitle>
            <DialogDescription>
              Update preset details and save current settings.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="edit-preset-name">Name</Label>
              <Input
                id="edit-preset-name"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                placeholder="Enter preset name"
              />
            </div>
            <div>
              <Label htmlFor="edit-preset-description">Description (Optional)</Label>
              <Textarea
                id="edit-preset-description"
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Enter description"
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleUpdatePreset}>
              Update Preset
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}; 