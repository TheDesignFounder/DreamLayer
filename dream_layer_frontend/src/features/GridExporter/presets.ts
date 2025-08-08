export interface GridPreset {
  id: string;
  name: string;
  description: string;
  settings: {
    rows?: number;
    cols?: number;
    fontSize: number;
    margin: number;
    labelColumns?: string[];
    cellSize?: [number, number];
    exportFormat?: string;
    backgroundColor?: [number, number, number];
  };
}

export const gridPresets: GridPreset[] = [
  {
    id: 'default',
    name: 'Default',
    description: 'Standard grid with automatic layout',
    settings: {
      fontSize: 16,
      margin: 10,
      cellSize: [256, 256],
      exportFormat: 'png',
      backgroundColor: [255, 255, 255]
    }
  },
  {
    id: 'compact',
    name: 'Compact',
    description: 'Tight spacing for more images',
    settings: {
      fontSize: 12,
      margin: 5,
      cellSize: [200, 200],
      exportFormat: 'png',
      backgroundColor: [255, 255, 255]
    }
  },
  {
    id: 'large',
    name: 'Large',
    description: 'Bigger images with more spacing',
    settings: {
      fontSize: 20,
      margin: 20,
      cellSize: [400, 400],
      exportFormat: 'png',
      backgroundColor: [255, 255, 255]
    }
  },
  {
    id: 'presentation',
    name: 'Presentation',
    description: '3x3 grid perfect for slideshows',
    settings: {
      rows: 3,
      cols: 3,
      fontSize: 18,
      margin: 15,
      cellSize: [300, 300],
      exportFormat: 'png',
      backgroundColor: [255, 255, 255]
    }
  },
  {
    id: 'comparison',
    name: 'Comparison',
    description: '2x2 grid for side-by-side comparisons',
    settings: {
      rows: 2,
      cols: 2,
      fontSize: 16,
      margin: 12,
      cellSize: [350, 350],
      exportFormat: 'png',
      backgroundColor: [255, 255, 255]
    }
  },
  {
    id: 'gallery',
    name: 'Gallery',
    description: '4x4 grid for showcasing multiple images',
    settings: {
      rows: 4,
      cols: 4,
      fontSize: 14,
      margin: 8,
      cellSize: [250, 250],
      exportFormat: 'png',
      backgroundColor: [255, 255, 255]
    }
  },
  {
    id: 'wide',
    name: 'Wide',
    description: 'Wide format for landscape images',
    settings: {
      rows: 2,
      cols: 5,
      fontSize: 16,
      margin: 10,
      cellSize: [280, 280],
      exportFormat: 'png',
      backgroundColor: [255, 255, 255]
    }
  },
  {
    id: 'tall',
    name: 'Tall',
    description: 'Tall format for portrait images',
    settings: {
      rows: 5,
      cols: 2,
      fontSize: 16,
      margin: 10,
      cellSize: [280, 280],
      exportFormat: 'png',
      backgroundColor: [255, 255, 255]
    }
  },
  {
    id: 'web-optimized',
    name: 'Web Optimized',
    description: 'Optimized for web with JPEG format',
    settings: {
      fontSize: 14,
      margin: 8,
      cellSize: [200, 200],
      exportFormat: 'jpg',
      backgroundColor: [255, 255, 255]
    }
  },
  {
    id: 'print-ready',
    name: 'Print Ready',
    description: 'High resolution for printing',
    settings: {
      fontSize: 18,
      margin: 15,
      cellSize: [400, 400],
      exportFormat: 'tiff',
      backgroundColor: [255, 255, 255]
    }
  },
  {
    id: 'dark-theme',
    name: 'Dark Theme',
    description: 'Dark background for modern UI',
    settings: {
      fontSize: 16,
      margin: 10,
      cellSize: [256, 256],
      exportFormat: 'png',
      backgroundColor: [30, 30, 30]
    }
  },
  {
    id: 'minimal',
    name: 'Minimal',
    description: 'Clean minimal design',
    settings: {
      fontSize: 12,
      margin: 20,
      cellSize: [300, 300],
      exportFormat: 'png',
      backgroundColor: [248, 248, 248]
    }
  },
  {
    id: 'social-media',
    name: 'Social Media',
    description: 'Optimized for social media sharing',
    settings: {
      rows: 3,
      cols: 3,
      fontSize: 14,
      margin: 10,
      cellSize: [240, 240],
      exportFormat: 'jpg',
      backgroundColor: [255, 255, 255]
    }
  },
  {
    id: 'portfolio',
    name: 'Portfolio',
    description: 'Professional portfolio layout',
    settings: {
      rows: 2,
      cols: 3,
      fontSize: 16,
      margin: 15,
      cellSize: [320, 320],
      exportFormat: 'png',
      backgroundColor: [255, 255, 255]
    }
  },
  {
    id: 'thumbnail',
    name: 'Thumbnail',
    description: 'Small thumbnails for quick preview',
    settings: {
      rows: 6,
      cols: 6,
      fontSize: 8,
      margin: 3,
      cellSize: [120, 120],
      exportFormat: 'png',
      backgroundColor: [255, 255, 255]
    }
  },
  {
    id: 'hero',
    name: 'Hero',
    description: 'Large hero-style layout',
    settings: {
      rows: 1,
      cols: 3,
      fontSize: 20,
      margin: 25,
      cellSize: [500, 500],
      exportFormat: 'png',
      backgroundColor: [255, 255, 255]
    }
  }
];

export const getPresetById = (id: string): GridPreset | undefined => {
  return gridPresets.find(preset => preset.id === id);
};

export const getPresetsByCategory = () => {
  return {
    basic: gridPresets.slice(0, 8),
    advanced: gridPresets.slice(8, 12),
    specialized: gridPresets.slice(12)
  };
}; 