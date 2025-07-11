import { ComfyUIWorkflow, ReactFlowNode, ReactFlowEdge, WorkflowGraph } from '@/types/workflow';

// Node type to color mapping for visual categorization
const NODE_COLORS = {
  'CheckpointLoaderSimple': '#ff6b6b',
  'LoraLoader': '#4ecdc4',
  'CLIPTextEncode': '#45b7d1',
  'VAEDecode': '#96ceb4',
  'VAEEncode': '#feca57',
  'KSampler': '#ff9ff3',
  'SaveImage': '#54a0ff',
  'LoadImage': '#5f27cd',
  'EmptyLatentImage': '#00d2d3',
  'LatentUpscale': '#ff6348',
  'ControlNetLoader': '#2ed573',
  'ControlNetApply': '#1e90ff',
  'default': '#ddd'
};

// Get color for node type
function getNodeColor(classType: string): string {
  return NODE_COLORS[classType as keyof typeof NODE_COLORS] || NODE_COLORS.default;
}

// Calculate node positions using a simple grid layout
function calculateNodePosition(index: number, totalNodes: number): { x: number; y: number } {
  const nodesPerRow = Math.ceil(Math.sqrt(totalNodes));
  const row = Math.floor(index / nodesPerRow);
  const col = index % nodesPerRow;
  
  return {
    x: col * 300 + 50,
    y: row * 200 + 50
  };
}

// Extract connection information from node inputs
function extractConnections(nodeId: string, inputs: Record<string, any>): Array<{ source: string; outputIndex: number; inputKey: string }> {
  const connections: Array<{ source: string; outputIndex: number; inputKey: string }> = [];
  
  for (const [inputKey, value] of Object.entries(inputs)) {
    if (Array.isArray(value) && value.length === 2 && typeof value[0] === 'string' && typeof value[1] === 'number') {
      connections.push({
        source: value[0],
        outputIndex: value[1],
        inputKey: inputKey
      });
    }
  }
  
  return connections;
}

// Parse ComfyUI workflow JSON to ReactFlow format
export function parseComfyUIWorkflow(workflow: ComfyUIWorkflow): WorkflowGraph {
  const nodes: ReactFlowNode[] = [];
  const edges: ReactFlowEdge[] = [];
  
  const nodeIds = Object.keys(workflow.prompt);
  
  // Create nodes
  nodeIds.forEach((nodeId, index) => {
    const comfyNode = workflow.prompt[nodeId];
    const position = calculateNodePosition(index, nodeIds.length);
    
    // Create a clean display of inputs (excluding connections)
    const displayInputs: Record<string, any> = {};
    Object.entries(comfyNode.inputs).forEach(([key, value]) => {
      if (!Array.isArray(value) || value.length !== 2 || typeof value[0] !== 'string') {
        displayInputs[key] = value;
      }
    });
    
    const node: ReactFlowNode = {
      id: nodeId,
      type: 'comfyNode',
      position,
      data: {
        label: comfyNode.class_type,
        class_type: comfyNode.class_type,
        inputs: displayInputs
      }
    };
    
    nodes.push(node);
  });
  
  // Create edges
  nodeIds.forEach((nodeId) => {
    const comfyNode = workflow.prompt[nodeId];
    const connections = extractConnections(nodeId, comfyNode.inputs);
    
    connections.forEach((connection) => {
      const edgeId = `${connection.source}-${nodeId}-${connection.inputKey}-${connection.outputIndex}`;
      const edge: ReactFlowEdge = {
        id: edgeId,
        source: connection.source,
        target: nodeId,
        label: `${connection.inputKey}[${connection.outputIndex}]`
      };
      
      edges.push(edge);
    });
  });
  
  return { nodes, edges };
}

// Load workflow from JSON file
export async function loadWorkflowFromFile(file: File): Promise<WorkflowGraph> {
  const text = await file.text();
  const workflow: ComfyUIWorkflow = JSON.parse(text);
  return parseComfyUIWorkflow(workflow);
}

// Load workflow from URL
export async function loadWorkflowFromUrl(url: string): Promise<WorkflowGraph> {
  const response = await fetch(url);
  const workflow: ComfyUIWorkflow = await response.json();
  return parseComfyUIWorkflow(workflow);
}

// Export node colors for use in components
export { NODE_COLORS, getNodeColor };