import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { PromptTemplate, PromptTemplateCategory, defaultCategories, builtInTemplates } from '@/types/promptTemplate';

interface PromptTemplateState {
  templates: PromptTemplate[];
  categories: PromptTemplateCategory[];
  selectedCategory: string;
  searchQuery: string;
  sortBy: 'name' | 'recent' | 'popular';
  
  // Actions
  addTemplate: (template: Omit<PromptTemplate, 'id' | 'createdAt' | 'updatedAt' | 'usageCount'>) => void;
  updateTemplate: (id: string, updates: Partial<PromptTemplate>) => void;
  deleteTemplate: (id: string) => void;
  duplicateTemplate: (id: string, newName?: string) => void;
  incrementUsage: (id: string) => void;
  
  // Category management
  addCategory: (category: Omit<PromptTemplateCategory, 'id'>) => void;
  updateCategory: (id: string, updates: Partial<PromptTemplateCategory>) => void;
  deleteCategory: (id: string) => void;
  
  // UI state
  setSelectedCategory: (category: string) => void;
  setSearchQuery: (query: string) => void;
  setSortBy: (sort: 'name' | 'recent' | 'popular') => void;
  
  // Getters
  getTemplatesByCategory: (category: string) => PromptTemplate[];
  getFilteredTemplates: () => PromptTemplate[];
  getTemplate: (id: string) => PromptTemplate | undefined;
  getPopularTemplates: (limit?: number) => PromptTemplate[];
  getRecentTemplates: (limit?: number) => PromptTemplate[];
  
  // Import/Export
  exportTemplates: () => string;
  importTemplates: (data: string) => void;
  resetToDefaults: () => void;
}

export const usePromptTemplateStore = create<PromptTemplateState>()(
  persist(
    (set, get) => ({
      templates: [...builtInTemplates],
      categories: [...defaultCategories],
      selectedCategory: 'all',
      searchQuery: '',
      sortBy: 'recent',
      
      addTemplate: (templateData) => {
        const newTemplate: PromptTemplate = {
          ...templateData,
          id: `template-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          createdAt: Date.now(),
          updatedAt: Date.now(),
          usageCount: 0,
          isBuiltIn: false
        };
        
        set((state) => ({
          templates: [newTemplate, ...state.templates]
        }));
      },
      
      updateTemplate: (id, updates) => {
        set((state) => ({
          templates: state.templates.map(template =>
            template.id === id
              ? { ...template, ...updates, updatedAt: Date.now() }
              : template
          )
        }));
      },
      
      deleteTemplate: (id) => {
        set((state) => ({
          templates: state.templates.filter(template => template.id !== id)
        }));
      },
      
      duplicateTemplate: (id, newName) => {
        const template = get().getTemplate(id);
        if (!template) return;
        
        const duplicatedTemplate: PromptTemplate = {
          ...template,
          id: `template-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          name: newName || `${template.name} (Copy)`,
          createdAt: Date.now(),
          updatedAt: Date.now(),
          usageCount: 0,
          isBuiltIn: false
        };
        
        set((state) => ({
          templates: [duplicatedTemplate, ...state.templates]
        }));
      },
      
      incrementUsage: (id) => {
        set((state) => ({
          templates: state.templates.map(template =>
            template.id === id
              ? { ...template, usageCount: template.usageCount + 1, updatedAt: Date.now() }
              : template
          )
        }));
      },
      
      addCategory: (categoryData) => {
        const newCategory: PromptTemplateCategory = {
          ...categoryData,
          id: `category-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
        };
        
        set((state) => ({
          categories: [...state.categories, newCategory]
        }));
      },
      
      updateCategory: (id, updates) => {
        set((state) => ({
          categories: state.categories.map(category =>
            category.id === id ? { ...category, ...updates } : category
          )
        }));
      },
      
      deleteCategory: (id) => {
        // Don't delete built-in categories
        const category = get().categories.find(c => c.id === id);
        if (!category || ['general', 'portrait', 'landscape', 'art', 'photography', 'fantasy', 'scifi', 'anime', 'custom'].includes(id)) {
          return;
        }
        
        set((state) => ({
          categories: state.categories.filter(category => category.id !== id),
          // Move templates in deleted category to 'custom'
          templates: state.templates.map(template =>
            template.category === id ? { ...template, category: 'custom' } : template
          )
        }));
      },
      
      setSelectedCategory: (category) => set({ selectedCategory: category }),
      setSearchQuery: (query) => set({ searchQuery: query }),
      setSortBy: (sort) => set({ sortBy: sort }),
      
      getTemplatesByCategory: (category) => {
        const { templates } = get();
        if (category === 'all') return templates;
        return templates.filter(template => template.category === category);
      },
      
      getFilteredTemplates: () => {
        const { templates, selectedCategory, searchQuery, sortBy } = get();
        
        let filtered = templates;
        
        // Filter by category
        if (selectedCategory !== 'all') {
          filtered = filtered.filter(template => template.category === selectedCategory);
        }
        
        // Filter by search query
        if (searchQuery) {
          const query = searchQuery.toLowerCase();
          filtered = filtered.filter(template =>
            template.name.toLowerCase().includes(query) ||
            template.description?.toLowerCase().includes(query) ||
            template.prompt.toLowerCase().includes(query) ||
            template.tags.some(tag => tag.toLowerCase().includes(query))
          );
        }
        
        // Sort
        switch (sortBy) {
          case 'name':
            filtered.sort((a, b) => a.name.localeCompare(b.name));
            break;
          case 'recent':
            filtered.sort((a, b) => b.updatedAt - a.updatedAt);
            break;
          case 'popular':
            filtered.sort((a, b) => b.usageCount - a.usageCount);
            break;
        }
        
        return filtered;
      },
      
      getTemplate: (id) => {
        return get().templates.find(template => template.id === id);
      },
      
      getPopularTemplates: (limit = 10) => {
        return get().templates
          .filter(template => template.usageCount > 0)
          .sort((a, b) => b.usageCount - a.usageCount)
          .slice(0, limit);
      },
      
      getRecentTemplates: (limit = 10) => {
        return get().templates
          .sort((a, b) => b.updatedAt - a.updatedAt)
          .slice(0, limit);
      },
      
      exportTemplates: () => {
        const { templates, categories } = get();
        const userTemplates = templates.filter(t => !t.isBuiltIn);
        const userCategories = categories.filter(c => !defaultCategories.find(dc => dc.id === c.id));
        
        return JSON.stringify({
          templates: userTemplates,
          categories: userCategories,
          exportedAt: new Date().toISOString(),
          version: '1.0'
        }, null, 2);
      },
      
      importTemplates: (data) => {
        try {
          const parsed = JSON.parse(data);
          const { templates: importedTemplates, categories: importedCategories } = parsed;
          
          if (importedTemplates && Array.isArray(importedTemplates)) {
            // Generate new IDs to avoid conflicts
            const newTemplates = importedTemplates.map(t => ({
              ...t,
              id: `template-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
              isBuiltIn: false,
              createdAt: Date.now(),
              updatedAt: Date.now()
            }));
            
            set((state) => ({
              templates: [...newTemplates, ...state.templates]
            }));
          }
          
          if (importedCategories && Array.isArray(importedCategories)) {
            const newCategories = importedCategories.map(c => ({
              ...c,
              id: `category-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
            }));
            
            set((state) => ({
              categories: [...state.categories, ...newCategories]
            }));
          }
        } catch (error) {
          console.error('Failed to import templates:', error);
          throw new Error('Invalid template data format');
        }
      },
      
      resetToDefaults: () => {
        set({
          templates: [...builtInTemplates],
          categories: [...defaultCategories],
          selectedCategory: 'all',
          searchQuery: '',
          sortBy: 'recent'
        });
      }
    }),
    {
      name: 'prompt-template-storage',
      version: 1,
      partialize: (state) => ({
        templates: state.templates,
        categories: state.categories,
        selectedCategory: state.selectedCategory,
        sortBy: state.sortBy
      })
    }
  )
);