export interface ComfyUINode {
  class_type: string;
  inputs: Record<string, any>;
}

export interface ComfyUIWorkflow {
  prompt: Record<string, ComfyUINode>;
}

export interface ReactFlowNode {
  id: string;
  type: string;
  position: { x: number; y: number };
  data: {
    label: string;
    class_type: string;
    inputs: Record<string, any>;
  };
}

export interface ReactFlowEdge {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string;
  targetHandle?: string;
  label?: string;
}

export interface WorkflowGraph {
  nodes: ReactFlowNode[];
  edges: ReactFlowEdge[];
}