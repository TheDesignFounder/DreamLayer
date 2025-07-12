import React, { useState, useEffect } from 'react';
import WorkflowViewer from '@/components/workflow/WorkflowViewer';
import { WorkflowGraph } from '@/types/workflow';
import { parseComfyUIWorkflow } from '@/utils/workflowParser';
import { Button } from '@/components/ui/button';

const FALLBACK_WORKFLOW_DATA = {
  prompt: {
    "1": {
      "class_type": "CheckpointLoaderSimple",
      "inputs": {
        "ckpt_name": "demo_model.safetensors"
      }
    },
    "2": {
      "class_type": "CLIPTextEncode",
      "inputs": {
        "clip": ["1", 1],
        "text": "a beautiful landscape, highly detailed, 8k resolution"
      }
    },
    "3": {
      "class_type": "CLIPTextEncode",
      "inputs": {
        "clip": ["1", 1],
        "text": "blurry, low quality, deformed, bad anatomy"
      }
    },
    "4": {
      "class_type": "EmptyLatentImage",
      "inputs": {
        "width": 512,
        "height": 512,
        "batch_size": 1
      }
    },
    "5": {
      "class_type": "KSampler",
      "inputs": {
        "model": ["1", 0],
        "positive": ["2", 0],
        "negative": ["3", 0],
        "latent_image": ["4", 0],
        "seed": 42,
        "steps": 20,
        "cfg": 7.0,
        "sampler_name": "euler",
        "scheduler": "normal",
        "denoise": 1.0
      }
    },
    "6": {
      "class_type": "VAEDecode",
      "inputs": {
        "samples": ["5", 0],
        "vae": ["1", 2]
      }
    },
    "7": {
      "class_type": "SaveImage",
      "inputs": {
        "filename_prefix": "demo_output",
        "images": ["6", 0]
      }
    }
  }
};

const Graph: React.FC = () => {
  const [demoWorkflow, setDemoWorkflow] = useState<WorkflowGraph | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Load demo workflow on component mount
    const loadDemoWorkflow = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Create a fallback demo workflow
        const createFallbackWorkflow = () => {
          return parseComfyUIWorkflow(FALLBACK_WORKFLOW_DATA);
        };

        let workflowGraph;
        
        try {
          // Try to load the demo workflow from the backend
          const response = await fetch('http://localhost:5002/api/demo-workflow');
          
          if (response.ok) {
            const workflowData = await response.json();
            workflowGraph = parseComfyUIWorkflow(workflowData);
            console.log('Loaded demo workflow from backend');
          } else {
            throw new Error('Backend not available');
          }
        } catch (backendError) {
          console.log('Backend unavailable, using fallback demo workflow:', backendError);
          workflowGraph = createFallbackWorkflow();
        }
        
        setDemoWorkflow(workflowGraph);
      } catch (err) {
        console.error('Error loading demo workflow:', err);
        // Even if there's an error, create a fallback workflow
        try {
          const fallbackWorkflow = parseComfyUIWorkflow(FALLBACK_WORKFLOW_DATA);
          setDemoWorkflow(fallbackWorkflow);
        } catch (fallbackErr) {
          console.error('Even fallback failed:', fallbackErr);
          setError('Failed to load demo workflow. You can upload your own workflow file.');
        }
      } finally {
        setLoading(false);
      }
    };

    loadDemoWorkflow();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-2 text-gray-600 dark:text-gray-400">Loading demo workflow...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
          <Button onClick={() => window.location.reload()}>
            Reload Page
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto p-4 h-screen">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm h-full">
          {demoWorkflow ? (
            <WorkflowViewer 
              initialWorkflow={demoWorkflow}
              className="h-full"
            />
          ) : (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  No workflow loaded. Please upload a workflow file.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Graph;