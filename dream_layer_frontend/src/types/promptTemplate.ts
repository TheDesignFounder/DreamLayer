export interface PromptTemplate {
  id: string;
  name: string;
  description?: string;
  prompt: string;
  negativePrompt?: string;
  category: string;
  tags: string[];
  isBuiltIn: boolean;
  createdAt: number;
  updatedAt: number;
  usageCount: number;
  settings?: {
    cfg_scale?: number;
    steps?: number;
    sampler_name?: string;
    scheduler?: string;
    width?: number;
    height?: number;
    [key: string]: any;
  };
}

export interface PromptTemplateCategory {
  id: string;
  name: string;
  description?: string;
  color?: string;
  icon?: string;
}

export const defaultCategories: PromptTemplateCategory[] = [
  { id: 'general', name: 'General', description: 'General purpose prompts', color: '#3b82f6' },
  { id: 'portrait', name: 'Portrait', description: 'People and character prompts', color: '#ef4444' },
  { id: 'landscape', name: 'Landscape', description: 'Nature and scenery prompts', color: '#10b981' },
  { id: 'art', name: 'Art Style', description: 'Artistic style prompts', color: '#f59e0b' },
  { id: 'photography', name: 'Photography', description: 'Photography and camera prompts', color: '#8b5cf6' },
  { id: 'fantasy', name: 'Fantasy', description: 'Fantasy and magical prompts', color: '#ec4899' },
  { id: 'scifi', name: 'Sci-Fi', description: 'Science fiction and futuristic prompts', color: '#06b6d4' },
  { id: 'anime', name: 'Anime', description: 'Anime and manga style prompts', color: '#f97316' },
  { id: 'custom', name: 'Custom', description: 'User-created templates', color: '#6b7280' }
];

export const builtInTemplates: PromptTemplate[] = [
  {
    id: 'portrait-professional',
    name: 'Professional Portrait',
    description: 'High-quality professional portrait photography',
    prompt: 'professional portrait photography, business headshot, studio lighting, sharp focus, high resolution, clean background',
    negativePrompt: 'blurry, low quality, amateur, candid, casual',
    category: 'portrait',
    tags: ['professional', 'business', 'studio', 'headshot'],
    isBuiltIn: true,
    createdAt: Date.now(),
    updatedAt: Date.now(),
    usageCount: 0,
    settings: {
      cfg_scale: 7,
      steps: 20,
      sampler_name: 'DPM++ 2M Karras',
      width: 512,
      height: 768
    }
  },
  {
    id: 'landscape-nature',
    name: 'Nature Landscape',
    description: 'Beautiful natural landscape photography',
    prompt: 'breathtaking landscape photography, golden hour lighting, pristine nature, dramatic sky, ultra detailed, cinematic composition',
    negativePrompt: 'people, buildings, urban, pollution, low quality',
    category: 'landscape',
    tags: ['nature', 'golden hour', 'cinematic', 'outdoor'],
    isBuiltIn: true,
    createdAt: Date.now(),
    updatedAt: Date.now(),
    usageCount: 0,
    settings: {
      cfg_scale: 8,
      steps: 25,
      sampler_name: 'DPM++ 2M Karras',
      width: 768,
      height: 512
    }
  },
  {
    id: 'art-oil-painting',
    name: 'Oil Painting Style',
    description: 'Classical oil painting artistic style',
    prompt: 'oil painting, classical art style, rich colors, textured brushstrokes, masterpiece, museum quality',
    negativePrompt: 'digital art, photography, modern, flat colors, simple',
    category: 'art',
    tags: ['oil painting', 'classical', 'traditional', 'masterpiece'],
    isBuiltIn: true,
    createdAt: Date.now(),
    updatedAt: Date.now(),
    usageCount: 0,
    settings: {
      cfg_scale: 9,
      steps: 30,
      sampler_name: 'Euler a',
      width: 512,
      height: 512
    }
  },
  {
    id: 'anime-character',
    name: 'Anime Character',
    description: 'High-quality anime character illustration',
    prompt: 'anime character, detailed face, expressive eyes, high quality illustration, vibrant colors, cel shading',
    negativePrompt: 'realistic, photography, western cartoon, low quality, blurry',
    category: 'anime',
    tags: ['anime', 'character', 'illustration', 'cel shading'],
    isBuiltIn: true,
    createdAt: Date.now(),
    updatedAt: Date.now(),
    usageCount: 0,
    settings: {
      cfg_scale: 7,
      steps: 20,
      sampler_name: 'DPM++ 2M Karras',
      width: 512,
      height: 768
    }
  },
  {
    id: 'photography-street',
    name: 'Street Photography',
    description: 'Urban street photography style',
    prompt: 'street photography, urban scene, candid moment, documentary style, natural lighting, photojournalism',
    negativePrompt: 'studio, posed, artificial lighting, staged, low quality',
    category: 'photography',
    tags: ['street', 'urban', 'candid', 'documentary'],
    isBuiltIn: true,
    createdAt: Date.now(),
    updatedAt: Date.now(),
    usageCount: 0,
    settings: {
      cfg_scale: 6,
      steps: 20,
      sampler_name: 'DPM++ 2M Karras',
      width: 768,
      height: 512
    }
  },
  {
    id: 'fantasy-magical',
    name: 'Magical Fantasy',
    description: 'Mystical fantasy scene with magic',
    prompt: 'magical fantasy scene, mystical atmosphere, glowing effects, ethereal lighting, enchanted forest, fantasy art',
    negativePrompt: 'realistic, modern, technology, ordinary, mundane',
    category: 'fantasy',
    tags: ['magic', 'mystical', 'enchanted', 'ethereal'],
    isBuiltIn: true,
    createdAt: Date.now(),
    updatedAt: Date.now(),
    usageCount: 0,
    settings: {
      cfg_scale: 8,
      steps: 25,
      sampler_name: 'Euler a',
      width: 512,
      height: 512
    }
  },
  {
    id: 'scifi-futuristic',
    name: 'Futuristic Sci-Fi',
    description: 'Futuristic science fiction scene',
    prompt: 'futuristic sci-fi scene, cyberpunk aesthetic, neon lighting, advanced technology, sleek design, concept art',
    negativePrompt: 'medieval, fantasy, primitive, low tech, rustic',
    category: 'scifi',
    tags: ['futuristic', 'cyberpunk', 'neon', 'technology'],
    isBuiltIn: true,
    createdAt: Date.now(),
    updatedAt: Date.now(),
    usageCount: 0,
    settings: {
      cfg_scale: 7,
      steps: 25,
      sampler_name: 'DPM++ 2M Karras',
      width: 768,
      height: 512
    }
  }
];