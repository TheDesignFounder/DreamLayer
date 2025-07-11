import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { usePromptTemplateStore } from '@/stores/usePromptTemplateStore';
import { PromptTemplate } from '@/types/promptTemplate';
import { 
  BookOpen, 
  Search, 
  Filter, 
  Star, 
  Clock, 
  Plus,
  Copy,
  Edit,
  Trash2,
  Download,
  Eye,
  Settings
} from 'lucide-react';

interface PromptTemplateSelectorProps {
  onSelectTemplate: (template: PromptTemplate) => void;
  currentPrompt?: string;
  currentNegativePrompt?: string;
}

interface TemplatePreviewProps {
  template: PromptTemplate;
  onSelect: (template: PromptTemplate) => void;
  onEdit: (template: PromptTemplate) => void;
  onDelete: (id: string) => void;
  onDuplicate: (id: string) => void;
}

const TemplatePreview: React.FC<TemplatePreviewProps> = ({
  template,
  onSelect,
  onEdit,
  onDelete,
  onDuplicate
}) => {
  const [showActions, setShowActions] = useState(false);
  const { incrementUsage } = usePromptTemplateStore();

  const handleSelect = () => {
    incrementUsage(template.id);
    onSelect(template);
  };

  const getCategoryColor = (category: string) => {
    const colors = {
      general: 'bg-blue-100 text-blue-800',
      portrait: 'bg-red-100 text-red-800',
      landscape: 'bg-green-100 text-green-800',
      art: 'bg-yellow-100 text-yellow-800',
      photography: 'bg-purple-100 text-purple-800',
      fantasy: 'bg-pink-100 text-pink-800',
      scifi: 'bg-cyan-100 text-cyan-800',
      anime: 'bg-orange-100 text-orange-800',
      custom: 'bg-gray-100 text-gray-800'
    };
    return colors[category] || colors.custom;
  };

  return (
    <Card 
      className="group cursor-pointer hover:shadow-md transition-shadow"
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-sm font-medium">{template.name}</CardTitle>
            <CardDescription className="text-xs mt-1">
              {template.description || 'No description'}
            </CardDescription>
          </div>
          <div className="flex items-center gap-1">
            <Badge className={`text-xs ${getCategoryColor(template.category)}`}>
              {template.category}
            </Badge>
            {template.isBuiltIn && (
              <Badge variant="outline" className="text-xs">Built-in</Badge>
            )}
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="pt-0">
        <div className="space-y-2">
          {/* Prompt preview */}
          <div className="text-xs text-muted-foreground">
            <p className="line-clamp-2">{template.prompt}</p>
          </div>
          
          {/* Tags */}
          {template.tags.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {template.tags.slice(0, 3).map((tag, index) => (
                <Badge key={index} variant="secondary" className="text-xs">
                  {tag}
                </Badge>
              ))}
              {template.tags.length > 3 && (
                <Badge variant="secondary" className="text-xs">
                  +{template.tags.length - 3}
                </Badge>
              )}
            </div>
          )}
          
          {/* Stats */}
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1">
                <Star className="h-3 w-3" />
                <span>{template.usageCount}</span>
              </div>
              <div className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                <span>{new Date(template.updatedAt).toLocaleDateString()}</span>
              </div>
            </div>
            
            {/* Actions */}
            <div className={`flex items-center gap-1 transition-opacity ${showActions ? 'opacity-100' : 'opacity-0'}`}>
              <Button
                size="sm"
                variant="ghost"
                className="h-6 w-6 p-0"
                onClick={handleSelect}
              >
                <Eye className="h-3 w-3" />
              </Button>
              <Button
                size="sm"
                variant="ghost"
                className="h-6 w-6 p-0"
                onClick={() => onDuplicate(template.id)}
              >
                <Copy className="h-3 w-3" />
              </Button>
              {!template.isBuiltIn && (
                <>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="h-6 w-6 p-0"
                    onClick={() => onEdit(template)}
                  >
                    <Edit className="h-3 w-3" />
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="h-6 w-6 p-0 text-destructive"
                    onClick={() => onDelete(template.id)}
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

const PromptTemplateSelector: React.FC<PromptTemplateSelectorProps> = ({
  onSelectTemplate,
  currentPrompt = '',
  currentNegativePrompt = ''
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<PromptTemplate | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  
  const {
    categories,
    selectedCategory,
    searchQuery,
    sortBy,
    setSelectedCategory,
    setSearchQuery,
    setSortBy,
    getFilteredTemplates,
    deleteTemplate,
    duplicateTemplate,
    addTemplate,
    updateTemplate,
    exportTemplates,
    importTemplates
  } = usePromptTemplateStore();

  const filteredTemplates = getFilteredTemplates();

  const handleSelectTemplate = (template: PromptTemplate) => {
    onSelectTemplate(template);
    setIsOpen(false);
  };

  const handleCreateTemplate = () => {
    if (currentPrompt.trim()) {
      addTemplate({
        name: 'New Template',
        prompt: currentPrompt,
        negativePrompt: currentNegativePrompt,
        category: 'custom',
        tags: [],
        isBuiltIn: false,
        description: 'Template created from current prompt'
      });
    }
  };

  const handleExport = () => {
    const data = exportTemplates();
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `prompt-templates-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const data = e.target?.result as string;
          importTemplates(data);
        } catch (error) {
          console.error('Failed to import templates:', error);
        }
      };
      reader.readAsText(file);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <BookOpen className="h-4 w-4 mr-2" />
          Templates
        </Button>
      </DialogTrigger>
      
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-hidden">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <span>Prompt Templates</span>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleCreateTemplate}
                disabled={!currentPrompt.trim()}
              >
                <Plus className="h-4 w-4 mr-2" />
                Save Current
              </Button>
              <Button variant="outline" size="sm" onClick={handleExport}>
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
              <Button variant="outline" size="sm" asChild>
                <label>
                  <input
                    type="file"
                    accept=".json"
                    onChange={handleImport}
                    className="sr-only"
                  />
                  <Settings className="h-4 w-4 mr-2" />
                  Import
                </label>
              </Button>
            </div>
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4">
          {/* Filters */}
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <Input
                placeholder="Search templates..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full"
              />
            </div>
            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger className="w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                {categories.map(category => (
                  <SelectItem key={category.id} value={category.id}>
                    {category.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={sortBy} onValueChange={(value: any) => setSortBy(value)}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="recent">Recent</SelectItem>
                <SelectItem value="popular">Popular</SelectItem>
                <SelectItem value="name">Name</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          {/* Templates Grid */}
          <ScrollArea className="h-[400px]">
            {filteredTemplates.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <BookOpen className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No templates found</p>
                <p className="text-sm">Try adjusting your search or filters</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {filteredTemplates.map((template) => (
                  <TemplatePreview
                    key={template.id}
                    template={template}
                    onSelect={handleSelectTemplate}
                    onEdit={setEditingTemplate}
                    onDelete={deleteTemplate}
                    onDuplicate={duplicateTemplate}
                  />
                ))}
              </div>
            )}
          </ScrollArea>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default PromptTemplateSelector;