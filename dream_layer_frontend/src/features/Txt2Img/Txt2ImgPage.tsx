import React, { useState, useEffect } from 'react';
import Accordion from '@/components/Accordion';
import PromptInput from '@/components/PromptInput';
import RenderSettings from '@/components/RenderSettings';
import SizingSettings from '@/components/SizingSettings';
import OutputQuantity from '@/components/OutputQuantity';
import GenerationID from '@/components/GenerationID';
import AdvancedSettings from '@/components/AdvancedSettings';
import ExternalExtensions from '@/components/ExternalExtensions';
import ImagePreview from '@/components/tabs/txt2img/ImagePreview';
import CheckpointBrowser from '@/components/checkpoint/CheckpointBrowser';
import LoraBrowser from '@/components/lora/LoraBrowser';
import CustomWorkflowBrowser from '@/components/custom-workflow/CustomWorkflowBrowser';
import MatrixSettings from '@/components/MatrixSettings';
import { useIsMobile } from '@/hooks/use-mobile';
import { Copy } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useTxt2ImgGalleryStore } from '@/stores/useTxt2ImgGalleryStore';
import { Txt2ImgCoreSettings, defaultTxt2ImgSettings, MatrixSettings as MatrixSettingsType, MatrixJob, MatrixParameter, defaultMatrixSettings, ImageResult } from '@/types/generationSettings';
import { useMatrixStore } from '@/stores/useMatrixStore';
import { generateMatrixGrid } from '@/utils/matrixGridGenerator';
import useControlNetStore from '@/stores/useControlNetStore';
import { ControlNetRequest } from '@/types/controlnet';
import useLoraStore from '@/stores/useLoraStore';
import { LoraRequest } from '@/types/lora';

interface Txt2ImgPageProps {
  selectedModel: string;
  onTabChange: (tabId: string) => void;
}

const Txt2ImgPage: React.FC<Txt2ImgPageProps> = ({ selectedModel, onTabChange }) => {
  const [activeSubTab, setActiveSubTab] = useState("generation");
  const [coreSettings, setCoreSettings] = useState<Txt2ImgCoreSettings>({
    ...defaultTxt2ImgSettings,
    model_name: selectedModel
  });
  const [customWorkflow, setCustomWorkflow] = useState<any | null>(null);
  const [matrixSettings, setMatrixSettings] = useState<MatrixSettingsType>(defaultMatrixSettings);

  const {
    jobs,
    currentJobIndex,
    isPaused,
    setInitialState,
    advanceJob,
    setPaused,
    updateJobStatus,
    reset: resetMatrixStore
  } = useMatrixStore();

  const isMobile = useIsMobile();
  const addImages = useTxt2ImgGalleryStore(state => state.addImages);
  const setLoading = useTxt2ImgGalleryStore(state => state.setLoading);
  const controlNetConfig = useControlNetStore(state => state.controlNetConfig);
  const { setControlNetConfig } = useControlNetStore();
  const loraConfig = useLoraStore(state => state.loraConfig);

  const isGenerating = !isPaused && jobs.length > 0 && currentJobIndex < jobs.length;
  const hasActiveMatrixJob = jobs.length > 0;

  useEffect(() => {
    updateCoreSettings({ model_name: selectedModel });
  }, [selectedModel]);

  // --- Matrix Generation Helper Functions ---

  const parseParameterValues = (parameter: MatrixParameter): any[] => {
    if (parameter.name === 'Nothing' || !parameter.values?.trim()) {
      console.log(`Parameter ${parameter.name} is Nothing or has no values`);
      return [];
    }
    
    const str = parameter.values.trim();
    console.log(`Parsing parameter ${parameter.name} with values: "${str}", type: ${parameter.type}`);
    
    if (parameter.type === 'range' && str.includes('-')) {
      const [start, end] = str.split('-').map(s => Number(s.trim()));
      if (!isNaN(start) && !isNaN(end) && start <= end) {
        const result = Array.from({ length: end - start + 1 }, (_, i) => start + i);
        console.log(`Range result for ${parameter.name}:`, result);
        return result;
      }
    }
    
    const result = str.split(',').map(v => {
      const trimmed = v.trim();
      const num = Number(trimmed);
      return isNaN(num) ? trimmed : num;
    }).filter(v => v !== '');
    
    console.log(`List result for ${parameter.name}:`, result);
    return result;
  };

  const applyParameterToSettings = (settings: Txt2ImgCoreSettings, paramName: string, value: any) => {
    console.log(`Applying parameter ${paramName} = ${value} to settings`);
    
    switch (paramName) {
      case 'Seed': 
        if (matrixSettings.keepSeedsForRows) {
          console.log('Keep -1 for seeds is enabled, keeping original seed');
          settings.seed = -1;
          settings.random_seed = true;
        } else {
          console.log('Keep -1 for seeds is disabled, using specific seed:', value);
          settings.seed = Number(value); 
          settings.random_seed = false;
        }
        break;
      case 'Steps': settings.steps = Number(value); break;
      case 'CFG Scale': settings.cfg_scale = Number(value); break;
      case 'Sampler': settings.sampler_name = String(value); break;
      case 'Denoising': settings.denoising_strength = Number(value); break;
      case 'Clip skip': settings.clip_skip = Number(value); break;
      case 'Hires steps': settings.hires_fix_hires_steps = Number(value); break;
    }
  };

  const generateMatrixJobs = (): MatrixJob[] => {
    console.log('=== generateMatrixJobs START ===');
    console.log('Current matrixSettings:', matrixSettings);
    
    const xValues = parseParameterValues(matrixSettings.xAxis);
    const yValues = parseParameterValues(matrixSettings.yAxis);
    const zValues = parseParameterValues(matrixSettings.zAxis);
    
    console.log('Parsed values:', { xValues, yValues, zValues });
    
    if (xValues.length === 0 && yValues.length === 0 && zValues.length === 0) {
      console.log('No values found, returning empty jobs array');
      return [];
    }

    const jobs: MatrixJob[] = [];
    const xVals = xValues.length > 0 ? xValues : [null];
    const yVals = yValues.length > 0 ? yValues : [null];
    const zVals = zValues.length > 0 ? zValues : [null];
    
    console.log('Final values to iterate:', { xVals, yVals, zVals });
    
    let jobIndex = 0;
    for (const zVal of zVals) {
      for (const yVal of yVals) {
        for (const xVal of xVals) {
          const jobSettings = { ...coreSettings };
          if (xVal !== null) applyParameterToSettings(jobSettings, matrixSettings.xAxis.name, xVal);
          if (yVal !== null) applyParameterToSettings(jobSettings, matrixSettings.yAxis.name, yVal);
          if (zVal !== null) applyParameterToSettings(jobSettings, matrixSettings.zAxis.name, zVal);
          
          const job = { 
            id: `job-${jobIndex++}`, 
            settings: jobSettings, 
            xValue: xVal, 
            yValue: yVal, 
            zValue: zVal, 
            status: 'pending' as const
          };
          jobs.push(job);
          console.log(`Created job ${job.id}:`, { xValue: xVal, yValue: yVal, zValue: zVal });
        }
      }
    }
    
    console.log(`=== generateMatrixJobs END: Created ${jobs.length} jobs ===`);
    return jobs;
  };

  const executeSingleGeneration = async (settings: Txt2ImgCoreSettings, options: { isMatrixJob: boolean; matrixInfo?: any }): Promise<ImageResult[]> => {
    console.log('executeSingleGeneration called:', { isMatrixJob: options.isMatrixJob, matrixInfo: options.matrixInfo });
    
    if (!options.isMatrixJob) setLoading(true);

    try {
      const requestData = { 
        ...settings, 
        custom_workflow: customWorkflow, 
        ...(controlNetConfig && { controlnet: controlNetConfig }), 
        ...(loraConfig?.enabled && { lora: loraConfig }) 
      };
      
      console.log('Sending request to backend:', requestData);
      
      const response = await fetch('http://localhost:5001/api/txt2img', { 
        method: 'POST', 
        headers: { 'Content-Type': 'application/json' }, 
        body: JSON.stringify(requestData) 
      });
      
      console.log('Response received:', response.status, response.ok);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Backend error:', errorText);
        throw new Error(`Failed to generate image: ${errorText}`);
      }
      
      const data = await response.json();
      console.log('Response data:', data);
      
      if (!data.comfy_response?.generated_images) {
        console.error('No generated_images in response:', data);
        throw new Error('No images were generated');
      }

      const images: ImageResult[] = await Promise.all(
        data.comfy_response.generated_images.map(async (img: any) => {
          let finalUrl = img.url;
          
          if (!options.isMatrixJob) {
            try {
              console.log('🔄 Saving single image to server for persistence:', img.url);
              
              const imageResponse = await fetch(img.url);
              const imageBlob = await imageResponse.blob();
              
              const reader = new FileReader();
              const base64Data = await new Promise<string>((resolve) => {
                reader.onloadend = () => resolve(reader.result as string);
                reader.readAsDataURL(imageBlob);
              });
              
              const saveResponse = await fetch('http://localhost:5002/api/save-single-image', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                  imageData: base64Data,
                  originalFilename: img.url.split('/').pop()
                })
              });
              
              if (saveResponse.ok) {
                const saveResult = await saveResponse.json();
                finalUrl = saveResult.url;
                console.log('✅ Single image saved to server:', finalUrl);
              } else {
                console.warn('⚠️ Failed to save single image to server, using original URL');
              }
            } catch (error) {
              console.warn('⚠️ Error saving single image to server:', error);
            }
          }
          
          return {
            id: `${Date.now()}-${Math.random()}`, 
            url: finalUrl, 
            prompt: settings.prompt, 
            negativePrompt: settings.negative_prompt, 
            timestamp: Date.now(), 
            settings: { ...settings }, 
            matrixInfo: options.matrixInfo,
          };
        })
      );

      console.log('Generated images:', images.length, images);
      
      if (!options.isMatrixJob) {
        console.log('Adding images to gallery (single mode)');
        addImages(images);
      }
      
      return images;

    } catch (error) {
      console.error('executeSingleGeneration error:', error);
      throw error;
    } finally {
      if (!options.isMatrixJob) setLoading(false);
    }
  };

  const handleGenerate = async () => {
    console.log('=== GENERATE BUTTON CLICKED ===');
    
    if (jobs.length > 0 && currentJobIndex < jobs.length) {
      console.log('Matrix already in progress, ignoring generate');
      return;
    }
    
    const newJobs = generateMatrixJobs();
    console.log('Generated jobs count:', newJobs.length);
    
    if (newJobs.length > 0) {
      console.log('Starting matrix mode');
      setLoading(true);
      setInitialState(newJobs);
    } else {
      console.log('Starting single mode');
      await executeSingleGeneration(coreSettings, { isMatrixJob: false });
    }
  };
  
  const handleInterrupt = async () => {
    await fetch('http://localhost:5001/api/txt2img/interrupt', { method: 'POST' });
    resetMatrixStore();
    setLoading(false);
  };

  const handlePause = async () => {
    console.log('⏸️ Pausing Matrix generation...');
    
    try {
      await fetch('http://localhost:5001/api/txt2img/interrupt', { method: 'POST' });
      console.log('✅ Backend interrupted successfully');
    } catch (error) {
      console.warn('⚠️ Failed to interrupt backend:', error);
    }
    
    const currentJob = jobs[currentJobIndex];
    if (currentJob && currentJob.status === 'running') {
      updateJobStatus(currentJobIndex, 'pending');
    }
    
    setPaused(true);
  };
  
  // --- Core Effects ---
  
  useEffect(() => {
    console.log('Matrix job runner effect triggered:', { 
      isGenerating, 
      isPaused, 
      currentJobIndex, 
      totalJobs: jobs.length 
    });
    
    if (!isGenerating || isPaused || currentJobIndex >= jobs.length) {
      console.log('Effect early return:', { isGenerating, isPaused, currentJobIndex, jobsLength: jobs.length });
      return;
    }
    
    let active = true;
    const runJob = async () => {
      const job = jobs[currentJobIndex];
      console.log(`Running job ${currentJobIndex}:`, job);
      
      if (!job) {
        console.log(`Job ${currentJobIndex} does not exist`);
        if (active) {
          setTimeout(() => advanceJob(), 100);
        }
        return;
      }
      
      if (job.status === 'completed') {
        console.log(`Job ${currentJobIndex} already completed, advancing...`);
        if (active) {
          setTimeout(() => advanceJob(), 100);
        }
        return;
      }
      
      if (job.status === 'failed') {
        console.log(`Job ${currentJobIndex} failed, skipping...`);
        if (active) {
          setTimeout(() => advanceJob(), 100);
        }
        return;
      }
      
      if (job.status === 'running') {
        console.log(`Job ${currentJobIndex} was running but paused, resetting to pending`);
        updateJobStatus(currentJobIndex, 'pending');
        return;
      }
      
      if (job.status === 'pending') {
        console.log(`Starting job ${currentJobIndex}`);
        updateJobStatus(currentJobIndex, 'running');
        
        try {
          const resultImages = await executeSingleGeneration(job.settings, { 
            isMatrixJob: true, 
            matrixInfo: { xValue: job.xValue, yValue: job.yValue, zValue: job.zValue } 
          });
          
          console.log(`Job ${currentJobIndex} completed with ${resultImages.length} images`);
          
          if (active) {
            updateJobStatus(currentJobIndex, 'completed', { result: resultImages });
            setTimeout(() => advanceJob(), 200);
          }
        } catch (error) {
          console.error(`Job ${currentJobIndex} failed:`, error);
          if (active) {
            updateJobStatus(currentJobIndex, 'failed', { error });
            setTimeout(() => advanceJob(), 200);
          }
        }
      }
    };
    
    const timeoutId = setTimeout(() => {
      if (active) {
        runJob();
      }
    }, 100);
    
    return () => { 
      active = false; 
      clearTimeout(timeoutId);
    };
  }, [currentJobIndex, isPaused, isGenerating, jobs.length]);

  useEffect(() => {
    const allJobsFinished = jobs.length > 0 && currentJobIndex >= jobs.length;
    console.log('Grid generation effect:', { allJobsFinished, jobsLength: jobs.length, currentJobIndex });
    
    if (allJobsFinished) {
      console.log('All matrix jobs finished. Generating grid...');
      
      const completedJobs = jobs.filter(job => job.status === 'completed' && job.result);
      console.log('Completed jobs with results:', completedJobs);
      
      if (completedJobs.length === 0) {
        console.error('No completed jobs found for grid generation');
        resetMatrixStore();
        setLoading(false);
        return;
      }

      if (matrixSettings.includeSubImages) {
        console.log('Adding individual images to gallery (Include Sub Images enabled)');
        const allIndividualImages = completedJobs.flatMap(job => job.result || []);
        if (allIndividualImages.length > 0) {
          addImages(allIndividualImages);
        }
      }

      const hasZAxis = completedJobs.some(job => job.zValue !== null);
      if (matrixSettings.includeSubgrids && hasZAxis) {
        console.log('Generating sub-grids for each Z value (Include Sub Grids enabled)');
        
        const zValues = [...new Set(completedJobs.map(job => job.zValue).filter(v => v !== null))];
        
        zValues.forEach(async (zValue) => {
          const zFilteredJobs = completedJobs.filter(job => job.zValue === zValue);
          
          try {
            const subGridImageUrl = await generateMatrixGrid(zFilteredJobs, {
              ...matrixSettings,
              zAxis: { ...matrixSettings.zAxis, name: 'Nothing', enabled: false }
            });
            
            addImages([{
              id: `matrix-subgrid-z${zValue}-${Date.now()}`,
              url: subGridImageUrl,
              prompt: `${coreSettings.prompt} (${matrixSettings.zAxis?.name}: ${zValue})`,
              negativePrompt: coreSettings.negative_prompt,
              timestamp: Date.now(),
              settings: { ...coreSettings },
            }]);
          } catch (error) {
            console.error(`Failed to generate sub-grid for Z=${zValue}:`, error);
          }
        });
      }

      generateMatrixGrid(completedJobs, matrixSettings)
        .then(gridImageUrl => {
          console.log('Main grid generated successfully');
          
          const matrixSpecificSettings = {
            ...coreSettings,
            isMatrixGrid: true,
            matrixAxes: {
              xAxis: matrixSettings.xAxis?.name !== 'Nothing' ? {
                name: matrixSettings.xAxis?.name,
                values: [...new Set(completedJobs.map(job => job.xValue).filter(v => v !== null))].sort()
              } : null,
              yAxis: matrixSettings.yAxis?.name !== 'Nothing' ? {
                name: matrixSettings.yAxis?.name,
                values: [...new Set(completedJobs.map(job => job.yValue).filter(v => v !== null))].sort()
              } : null,
              zAxis: matrixSettings.zAxis?.name !== 'Nothing' ? {
                name: matrixSettings.zAxis?.name,
                values: [...new Set(completedJobs.map(job => job.zValue).filter(v => v !== null))].sort()
              } : null,
            },
            totalJobs: completedJobs.length,
            matrixSettings: {
              drawLegend: matrixSettings.drawLegend,
              keepSeedsConsistent: matrixSettings.keepSeedsConsistent,
              includeSubImages: matrixSettings.includeSubImages,
              includeSubgrids: matrixSettings.includeSubgrids
            }
          };
          
          addImages([{
            id: `matrix-grid-${Date.now()}`, 
            url: gridImageUrl, 
            prompt: `Matrix Grid: ${coreSettings.prompt}`,
            negativePrompt: coreSettings.negative_prompt, 
            timestamp: Date.now(), 
            settings: matrixSpecificSettings,
          }]);
        })
        .catch(error => {
          console.error("Failed to generate matrix grid:", error);
        })
        .finally(() => {
          console.log('Resetting matrix store and loading state');
          resetMatrixStore();
          setLoading(false);
        });
    }
  }, [currentJobIndex, jobs.length, jobs, matrixSettings, coreSettings, addImages, resetMatrixStore, setLoading]);

  // --- Other handlers and components ---
  
  const updateCoreSettings = (updates: Partial<Txt2ImgCoreSettings>) => setCoreSettings(prev => ({ ...prev, ...updates }));
  const handlePromptChange = (value: string, isNegative: boolean = false) => updateCoreSettings(isNegative ? { negative_prompt: value } : { prompt: value });
  const handleBatchSettingsChange = (batchSize: number, batchCount: number) => updateCoreSettings({ batch_size: batchSize, batch_count: batchCount });
  const handleSamplingSettingsChange = (sampler: string, scheduler: string, steps: number, cfg: number) => updateCoreSettings({ sampler_name: sampler, scheduler: scheduler, steps: steps, cfg_scale: cfg });
  const handleSizeSettingsChange = (width: number, height: number) => updateCoreSettings({ width, height });
  const handleSeedChange = (seed: number, random: boolean = true) => updateCoreSettings({ seed, random_seed: random });
  const handleSubTabChange = (tabId: string) => setActiveSubTab(tabId);
  const handleControlNetChange = (config: ControlNetRequest | null) => setControlNetConfig(config?.enabled ? config : null);
  const handleRestoreFacesChange = (enabled: boolean) => updateCoreSettings({ restore_faces: enabled });
  const handleFaceRestorationModelChange = (model: string) => updateCoreSettings({ face_restoration_model: model });
  const handleCodeformerWeightChange = (weight: number) => updateCoreSettings({ codeformer_weight: weight });
  const handleGfpganWeightChange = (weight: number) => updateCoreSettings({ gfpgan_weight: weight });
  const handleMatrixSettingsChange = (settings: MatrixSettingsType) => {
    console.log('Matrix settings changed:', settings);
    setMatrixSettings(settings);
  };
  const handleTilingChange = (enabled: boolean) => updateCoreSettings({ tiling: enabled });
  const handleTileSizeChange = (size: number) => updateCoreSettings({ tile_size: size });
  const handleTileOverlapChange = (overlap: number) => updateCoreSettings({ tile_overlap: overlap });
  const handleHiresFixChange = (enabled: boolean) => updateCoreSettings({ hires_fix: enabled });
  const handleRefinerEnabledChange = (enabled: boolean) => updateCoreSettings({ refiner_enabled: enabled });
  const handleRefinerModelChange = (model: string) => updateCoreSettings({ refiner_model: model });
  const handleRefinerSwitchAtChange = (value: number) => updateCoreSettings({ refiner_switch_at: value });
  const handleCopyPrompts = () => {
    const promptTextarea = document.querySelector('textarea[placeholder="Enter your prompt here"]') as HTMLTextAreaElement;
    const negativePromptTextarea = document.querySelector('textarea[placeholder="Enter negative prompt here"]') as HTMLTextAreaElement;
    if (promptTextarea && negativePromptTextarea) navigator.clipboard.writeText(`Prompt: ${promptTextarea.value}\nNegative Prompt: ${negativePromptTextarea.value}`);
  };

  const ActionButtons = () => {
    const hasUnfinishedJobs = jobs.length > 0 && currentJobIndex < jobs.length;
    
    return (
      <div className="flex flex-col space-y-2">
        <div className="flex space-x-2">
          {!hasUnfinishedJobs ? (
            <Button 
              className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90" 
              onClick={handleGenerate}
            >
              Generate
            </Button>
          ) : isGenerating ? (
            <Button 
              className="rounded-md bg-yellow-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-yellow-700" 
              onClick={handlePause}
            >
              Pause
            </Button>
          ) : (
            <Button 
              className="rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-green-700" 
              onClick={() => setPaused(false)}
            >
              Resume
            </Button>
          )}
          
          {hasUnfinishedJobs && (
            <Button variant="destructive" onClick={handleInterrupt}>
              Interrupt
            </Button>
          )}
        </div>

        {hasUnfinishedJobs && (
          <div className="flex items-center space-x-2 text-sm text-muted-foreground">
            <div className="flex items-center space-x-1">
              <span>Progress:</span>
              <span className="font-medium text-foreground">
                {Math.min(currentJobIndex + (isGenerating ? 1 : 0), jobs.length)}/{jobs.length}
              </span>
              <span>jobs</span>
            </div>
            
            {isPaused && (
              <div className="flex items-center space-x-1 text-yellow-600">
                <span>⏸️</span>
                <span>Paused</span>
              </div>
            )}
            
            {isGenerating && (
              <div className="flex items-center space-x-1 text-blue-600">
                <span>🔄</span>
                <span>Generating...</span>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  const MobileImagePreview = () => (<div className="my-4 w-full"><ImagePreview onTabChange={onTabChange} /></div>);

  const SubTabNavigation = () => {
    const tabs = [{ id: "generation", label: "Generation" }, { id: "checkpoints", label: "Custom Workflow" }, { id: "lora", label: "Lora" }];
    return (<div className="flex flex-wrap gap-3">{tabs.map(tab => (<button key={tab.id} onClick={() => handleSubTabChange(tab.id)} className={cn("px-6 py-2.5 rounded-full text-sm font-medium transition-all duration-200 border focus:outline-none focus:ring-2 focus:ring-offset-2", activeSubTab === tab.id ? "bg-blue-600 text-white shadow-md hover:bg-blue-700 focus:ring-blue-500 border-blue-600" : "bg-transparent text-gray-600 hover:bg-gray-50 border-gray-200 hover:border-gray-300 dark:text-gray-400 dark:border-gray-600 dark:hover:bg-gray-800/50 dark:hover:border-gray-500")}>{tab.label}</button>))}</div>);
  };

  const getAccordionTitle = () => {
    switch (activeSubTab) {
      case "checkpoints": return "Custom Workflow Management";
      case "lora": return "LoRA Browser";
      default: return "Core Generation Settings";
    }
  };

  const renderActiveSubTabContent = () => {
    switch (activeSubTab) {
      case "checkpoints": return <CustomWorkflowBrowser onWorkflowChange={setCustomWorkflow} currentWorkflow={customWorkflow} />;
      case "lora": return <LoraBrowser />;
      default: return (<>
        <div className="flex items-center justify-between mb-4">
          <h4 className="text-sm font-bold text-[#2563EB]">1. Prompt Input</h4>
          <Button onClick={handleCopyPrompts} variant="outline" size="sm" className="text-xs px-2 py-1 h-auto flex items-center gap-1"><Copy className="h-3.5 w-3.5" />Copy Prompts</Button>
        </div>
        <PromptInput label="a) Prompt" maxLength={500} placeholder="Enter your prompt here" value={coreSettings.prompt} onChange={(value) => handlePromptChange(value)} />
        <PromptInput label="b) Negative Prompt" negative={true} maxLength={500} placeholder="Enter negative prompt here" value={coreSettings.negative_prompt} onChange={(value) => handlePromptChange(value, true)} />
        <RenderSettings showResizeMode={false} sampler={coreSettings.sampler_name} scheduler={coreSettings.scheduler} steps={coreSettings.steps} cfg={coreSettings.cfg_scale} onChange={handleSamplingSettingsChange} />
        <h4 className="mb-2 mt-6 text-sm font-bold text-[#2563EB]">3. Sizing</h4>
        <SizingSettings width={coreSettings.width} height={coreSettings.height} onChange={handleSizeSettingsChange} />
        <h4 className="mb-2 mt-6 text-sm font-bold text-[#2563EB]">4. Output Quantity: {coreSettings.batch_count * coreSettings.batch_size}</h4>
        <OutputQuantity batchCount={coreSettings.batch_count} batchSize={coreSettings.batch_size} onChange={handleBatchSettingsChange} />
        <div className="flex items-center justify-between mt-6 mb-2">
          <h4 className="text-sm font-bold text-[#2563EB]">5. Seed</h4>
          <div className="flex space-x-2">
            <button className="text-xs rounded-md border border-input bg-background px-2 py-1 hover:bg-accent hover:text-accent-foreground" onClick={() => handleSeedChange(-1, true)}>Randomize Seed</button>
            <button className="text-xs rounded-md border border-input bg-background px-2 py-1 hover:bg-accent hover:text-accent-foreground" onClick={() => handleSeedChange(coreSettings.seed, false)}>Reuse Past Seed</button>
          </div>
        </div>
        <GenerationID seed={coreSettings.seed} random={coreSettings.random_seed} onChange={handleSeedChange} />
        <div className="mt-8">
          <h4 className="mb-4 text-sm font-bold text-[#2563EB]">6. Matrix Generation</h4>
          <MatrixSettings onSettingsChange={handleMatrixSettingsChange} />
        </div>
      </>);
    }
  };

  return (
    <div className={`mb-4 ${isMobile ? 'grid grid-cols-1' : 'grid gap-6 md:grid-cols-[1.8fr_1fr]'}`}>
      <div className="space-y-4">
        <div className="flex flex-col">
          <div className="mb-[18px] flex flex-col space-y-2 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
            <h3 className="text-base font-medium">Generation Settings</h3><ActionButtons />
          </div>
          {isMobile && <MobileImagePreview />}
          <div className="mb-[18px]"><SubTabNavigation /></div>
          <Accordion title={getAccordionTitle()} number="1" defaultOpen={true}>{renderActiveSubTabContent()}</Accordion>
          {activeSubTab === "generation" && (<>
            <Accordion title="Advanced Optional Settings" number="2">
              <AdvancedSettings restoreFaces={coreSettings.restore_faces} onRestoreFacesChange={handleRestoreFacesChange} faceRestorationModel={coreSettings.face_restoration_model} onFaceRestorationModelChange={handleFaceRestorationModelChange} codeformerWeight={coreSettings.codeformer_weight} onCodeformerWeightChange={handleCodeformerWeightChange} gfpganWeight={coreSettings.gfpgan_weight} onGfpganWeightChange={handleGfpganWeightChange} tiling={coreSettings.tiling} onTilingChange={handleTilingChange} tileSize={coreSettings.tile_size} onTileSizeChange={handleTileSizeChange} overlap={coreSettings.tile_overlap} onOverlapChange={handleTileOverlapChange} hiresFix={coreSettings.hires_fix} onHiresFixChange={handleHiresFixChange} refinerEnabled={coreSettings.refiner_enabled} onRefinerEnabledChange={handleRefinerEnabledChange} refinerModel={coreSettings.refiner_model} onRefinerModelChange={handleRefinerModelChange} refinerSwitchAt={coreSettings.refiner_switch_at} onRefinerSwitchAtChange={handleRefinerSwitchAtChange} />
            </Accordion>
            <Accordion title="External Extensions & Add-ons" number="3">
              <ExternalExtensions isImg2ImgTab={false} onControlNetChange={handleControlNetChange} />
            </Accordion>
          </>)}
        </div>
      </div>
      {!isMobile && (<div><ImagePreview onTabChange={onTabChange} /></div>)}
    </div>
  );
};

export default Txt2ImgPage;
