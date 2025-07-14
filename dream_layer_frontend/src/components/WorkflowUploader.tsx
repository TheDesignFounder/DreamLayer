import React, { useEffect } from 'react';
import demoWorkflow from '../data/demo-workflow.json';

// Type definitions for ComfyUI workflow
interface WorkflowNodeInput {
  name: string;
  type: string;
  link?: number;
}

interface WorkflowNodeOutput {
  name: string;
  type: string;
  links?: number[];
  slot_index?: number;
}

interface WorkflowNode {
  id: number;
  type: string;
  pos?: [number, number];
  size?: [number, number];
  inputs?: WorkflowNodeInput[];
  outputs?: WorkflowNodeOutput[];
  properties?: Record<string, unknown>;
  widgets_values?: (string | number | boolean)[];
  title?: string;
}

interface WorkflowLink {
  [0]: number; // link ID
  [1]: number; // source node ID
  [2]: number; // source output index
  [3]: number; // target node ID
  [4]: number; // target input index
  [5]: string; // connection type
}

interface WorkflowData {
  nodes: WorkflowNode[];
  links: WorkflowLink[];
}

interface WorkflowUploaderProps {
  onWorkflowLoaded: (data: WorkflowData) => void;
}

export const WorkflowUploader: React.FC<WorkflowUploaderProps> = ({ onWorkflowLoaded }) => {
  // Load demo workflow on component mount
  useEffect(() => {
    onWorkflowLoaded(demoWorkflow as unknown as WorkflowData);
  }, [onWorkflowLoaded]);
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const jsonData = JSON.parse(e.target?.result as string) as WorkflowData;
          onWorkflowLoaded(jsonData);
        } catch (error) {
          console.error('Error parsing workflow JSON', error);
          alert('Failed to parse workflow JSON. Please check the file format.');
        }
      };
      reader.readAsText(file);
    }
  };

  const loadDemo = () => {
    onWorkflowLoaded(demoWorkflow as unknown as WorkflowData);
  };

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={loadDemo}
        className="inline-flex items-center gap-2 rounded-md bg-secondary px-3 py-2 text-sm font-medium text-secondary-foreground hover:bg-secondary/80 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polygon points="5,3 19,12 5,21"/>
        </svg>
        Demo
      </button>
      <label className="cursor-pointer inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
          <polyline points="14,2 14,8 20,8"/>
        </svg>
        Upload JSON
        <input
          type="file"
          accept=".json"
          onChange={handleFileUpload}
          className="hidden"
        />
      </label>
    </div>
  );
};

export type { WorkflowData, WorkflowNode, WorkflowLink, WorkflowNodeInput, WorkflowNodeOutput };