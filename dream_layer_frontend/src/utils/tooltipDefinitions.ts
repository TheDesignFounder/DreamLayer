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
  },

  // === CONTROLNET SETTINGS ===
  controlWeight: {
    title: "Control Weight",
    description: "Strength of the ControlNet's influence on generation. Controls how much the control input affects the final image.",
    tips: [
      "0.3-0.7: Subtle control, preserves original style",
      "0.8-1.2: Balanced control (recommended)",
      "1.3-1.8: Strong control, overrides prompt style",
      "1.9-2.0: Very strong, may cause artifacts"
    ],
    bestPractices: "Use 1.0 for most cases, increase for stronger control, decrease for subtlety"
  },

  guidanceStart: {
    title: "Guidance Start",
    description: "When ControlNet starts influencing the generation process (as fraction of total steps).",
    tips: [
      "0.0: Control from the very beginning",
      "0.1-0.3: Allow initial creativity, then apply control",
      "0.4-0.6: Late control application",
      "0.7+: Very late control, minimal influence"
    ],
    bestPractices: "Use 0.0 for strict control, 0.2 for creative freedom with guidance"
  },

  guidanceEnd: {
    title: "Guidance End", 
    description: "When ControlNet stops influencing the generation process (as fraction of total steps).",
    tips: [
      "0.8-1.0: Control throughout most of generation",
      "0.6-0.8: Stop control before final details",
      "0.4-0.6: Early control only",
      "0.2-0.4: Very brief control influence"
    ],
    bestPractices: "Use 1.0 for full control, 0.8 to allow natural finishing touches"
  },

  processorRes: {
    title: "Processor Resolution",
    description: "Resolution for ControlNet preprocessing. Higher values capture more detail but use more memory.",
    tips: [
      "256-384: Low detail, fast processing",
      "512: Standard resolution (recommended)",
      "768-1024: High detail, slower processing",
      "1024+: Maximum detail, requires lots of memory"
    ],
    bestPractices: "Use 512 for most cases, match your generation resolution"
  },

  thresholdA: {
    title: "Threshold A (Low)",
    description: "Lower threshold for edge detection. Controls sensitivity to weak edges and details.",
    tips: [
      "50-100: Detect only strong edges",
      "100-150: Balanced edge detection (recommended)",
      "150-200: Sensitive to weak edges",
      "200+: Very sensitive, may include noise"
    ],
    bestPractices: "Start with 100, increase to capture more detail"
  },

  thresholdB: {
    title: "Threshold B (High)",
    description: "Upper threshold for edge detection. Controls sensitivity to strong edges and major features.",
    tips: [
      "100-150: Conservative edge detection",
      "150-250: Balanced detection (recommended)",
      "250-300: Aggressive edge detection",
      "300+: Maximum sensitivity"
    ],
    bestPractices: "Use 200, keep it higher than Threshold A (typically 2x)"
  },

  // === UPSCALING SETTINGS ===
  upscaleFactor: {
    title: "Upscale Factor",
    description: "How much to enlarge the image during upscaling. Higher values create larger images but take more time.",
    tips: [
      "1.5-2.0: Moderate upscaling, good quality",
      "2.0-3.0: Standard upscaling for most uses",
      "3.0-4.0: High upscaling, may introduce artifacts",
      "4.0+: Maximum upscaling, very slow"
    ],
    bestPractices: "Use 2.0x for balanced quality and performance"
  },

  hiresSteps: {
    title: "Hires Steps",
    description: "Number of steps for the high-resolution pass. More steps improve detail but increase generation time.",
    tips: [
      "10-20: Fast hires pass, basic improvement",
      "20-30: Balanced detail and speed (recommended)",
      "30-40: High detail, slower generation",
      "40+: Maximum detail, very slow"
    ],
    bestPractices: "Use 20-25 steps for most high-res generations"
  },

  hiresDenoising: {
    title: "Hires Denoising Strength", 
    description: "How much the AI modifies the image during upscaling. Lower values preserve the original better.",
    tips: [
      "0.1-0.3: Minimal changes, preserve original",
      "0.4-0.6: Balanced enhancement (recommended)",
      "0.7-0.9: Significant changes, add new details",
      "0.9-1.0: Major modifications, may change composition"
    ],
    bestPractices: "Use 0.5 for natural upscaling, lower to preserve more detail"
  },

  // === BATCH AND OUTPUT SETTINGS ===
  batchSize: {
    title: "Batch Size",
    description: "Number of images generated simultaneously. Higher values are faster overall but use more VRAM.",
    tips: [
      "1-2: Low VRAM usage, slower total time",
      "3-4: Balanced performance (recommended)",
      "5-8: Higher VRAM usage, faster if you have memory",
      "8+: Maximum batch size, requires powerful GPU"
    ],
    bestPractices: "Use 4 for most GPUs, adjust based on available VRAM (8GB = 4 batch, 12GB = 6-8 batch)"
  },

  batchCount: {
    title: "Batch Count",
    description: "Number of batches to generate. Total images = Batch Size × Batch Count.",
    tips: [
      "1-2: Quick testing and iteration",
      "3-5: Generate multiple variations",
      "6-10: Comprehensive generation session",
      "10+: Large-scale generation"
    ],
    bestPractices: "Use 3-5 for exploring variations, 1-2 for quick tests"
  },

  // === INPAINTING SETTINGS ===
  maskBlur: {
    title: "Mask Blur",
    description: "Amount of blur applied to the inpainting mask edges. Higher values create smoother transitions.",
    tips: [
      "0-2: Sharp mask edges, visible boundaries",
      "3-6: Soft edges (recommended)",
      "7-12: Very soft transitions",
      "12+: Extremely soft, may affect too much area"
    ],
    bestPractices: "Use 4-6 for natural-looking inpainted areas"
  },

  onlyMaskedPadding: {
    title: "Only Masked Padding",
    description: "Pixels of context around the masked area when using 'Only Masked' mode. More context helps coherence.",
    tips: [
      "16-32: Minimal context, faster processing",
      "32-64: Balanced context (recommended)",
      "64-128: Extended context, better coherence",
      "128+: Maximum context, slower processing"
    ],
    bestPractices: "Use 32-64 pixels for good balance of speed and quality"
  }
};

// Helper function to get tooltip content
export const getTooltipContent = (key: keyof typeof tooltipDefinitions) => {
  return tooltipDefinitions[key] || null;
};