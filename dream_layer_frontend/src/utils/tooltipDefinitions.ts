// Tooltip definitions for all sliders and settings
export const tooltipDefinitions = {
  // === SAMPLING SETTINGS ===
  samplingSteps: {
    title: "Sampling Steps",
    description: "Number of denoising steps to perform. More steps = higher quality but slower generation.",
    tips: [
      "15-25 steps: Fast drafts and testing",
      "25-35 steps: Balanced quality and speed", 
      "35-50 steps: High quality, detailed results",
      "50+ steps: Diminishing returns, very slow"
    ],
    bestPractices: "Use sampler-specific optimal ranges for best results"
  },
  
  cfgScale: {
    title: "CFG Scale (Classifier-Free Guidance)",
    description: "Controls how closely the image follows your prompt. Higher values stick closer to the prompt.",
    tips: [
      "1-5: Very loose interpretation, more artistic freedom",
      "6-10: Balanced following of prompt", 
      "11-15: Strict adherence to prompt",
      "16-20: Very strict, may cause artifacts",
      "20+: Often produces oversaturated/distorted results"
    ],
    bestPractices: "Start with 7-10 for most prompts, adjust based on results"
  },
  
  denoisingStrength: {
    title: "Denoising Strength",
    description: "How much the AI changes the input image. Lower values preserve more of the original image.",
    tips: [
      "0.1-0.3: Minimal changes, preserve original",
      "0.4-0.7: Balanced transformation (recommended)",
      "0.8-1.0: Major changes, may lose original features"
    ],
    bestPractices: "Use 0.5-0.7 for most img2img tasks"
  },
  
  // === SIZING SETTINGS ===
  width: {
    title: "Image Width",
    description: "Width of the generated image in pixels. Must be divisible by 64.",
    tips: [
      "512px: Standard SD 1.5 resolution",
      "768px: Higher detail, more VRAM needed",
      "1024px: SDXL standard, requires powerful GPU",
      "1536px+: Ultra-high resolution, very slow"
    ],
    bestPractices: "Use 512x512 for SD 1.5, 1024x1024 for SDXL"
  },
  
  height: {
    title: "Image Height", 
    description: "Height of the generated image in pixels. Must be divisible by 64.",
    tips: [
      "512px: Standard SD 1.5 resolution",
      "768px: Higher detail, more VRAM needed", 
      "1024px: SDXL standard, requires powerful GPU",
      "1536px+: Ultra-high resolution, very slow"
    ],
    bestPractices: "Keep aspect ratio reasonable (1:1, 4:3, 16:9, etc.)"
  },
  
  // === FACE RESTORATION ===
  codeformerWeight: {
    title: "CodeFormer Weight",
    description: "Controls the strength of CodeFormer face restoration. Higher values apply more correction.",
    tips: [
      "0.0-0.3: Subtle face improvements",
      "0.4-0.7: Balanced restoration (recommended)",
      "0.8-1.0: Strong correction, may look artificial"
    ],
    bestPractices: "Use 0.5-0.7 for natural-looking face restoration"
  },
  
  gfpganWeight: {
    title: "GFPGAN Weight",
    description: "Controls the strength of GFPGAN face restoration. Higher values apply more correction.",
    tips: [
      "0.0-0.3: Subtle face improvements",
      "0.4-0.7: Balanced restoration (recommended)", 
      "0.8-1.0: Strong correction, may look artificial"
    ],
    bestPractices: "Use 0.5-0.7 for natural-looking face restoration"
  },
  
  // === TILING SETTINGS ===
  tileSize: {
    title: "Tile Size",
    description: "Size of each tile when generating seamless patterns. Larger tiles use more memory.",
    tips: [
      "64-256px: Small tiles, less memory, more seams",
      "256-512px: Balanced size (recommended)",
      "512-768px: Large tiles, better quality, more memory",
      "768px+: Very large, may cause memory issues"
    ],
    bestPractices: "Use 512px for best balance of quality and memory usage"
  },
  
  tileOverlap: {
    title: "Tile Overlap",
    description: "Overlap between tiles to reduce seams. Higher overlap uses more memory but reduces artifacts.",
    tips: [
      "0-32px: Minimal overlap, visible seams possible",
      "32-64px: Good balance (recommended)",
      "64-128px: High overlap, fewer seams, more memory",
      "128px+: Very high overlap, diminishing returns"
    ],
    bestPractices: "Use 64px overlap for seamless patterns"
  },
  
  // === ADVANCED SETTINGS ===
  refinerSwitchAt: {
    title: "Refiner Switch At",
    description: "When to switch from base model to refiner model during generation (as fraction of total steps).",
    tips: [
      "0.6-0.7: Early switch, more refiner influence",
      "0.7-0.8: Balanced switch (recommended)",
      "0.8-0.9: Late switch, preserve base model style",
      "0.9-1.0: Very late switch, minimal refiner effect"
    ],
    bestPractices: "Use 0.8 for most cases, adjust based on desired refinement level"
  }
};

// Helper function to get tooltip content
export const getTooltipContent = (key: keyof typeof tooltipDefinitions) => {
  return tooltipDefinitions[key] || null;
};