import React, { useState, useCallback, useMemo } from 'react';
import {
  ReactFlow,
  Controls,
  Background,
  MiniMap,
  useNodesState,
  useEdgesState,
  Node,
  Edge,
  NodeTypes,
  ReactFlowProvider
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Upload, Download, ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';
import ComfyUINode from './ComfyUINode';
import { WorkflowGraph } from '@/types/workflow';
import { loadWorkflowFromFile, loadWorkflowFromUrl } from '@/utils/workflowParser';

// Custom styles for React Flow controls
const controlsStyle = `
  .react-flow-controls-enhanced .react-flow__controls-button {
    background: white !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 6px !important;
    color: #374151 !important;
    font-weight: 500 !important;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06) !important;
    transition: all 0.2s ease !important;
    width: 32px !important;
    height: 32px !important;
    margin: 2px !important;
  }
  
  .react-flow-controls-enhanced .react-flow__controls-button:hover {
    background: #f9fafb !important;
    border-color: #d1d5db !important;
    transform: translateY(-1px) !important;
  }
  
  .react-flow-controls-enhanced .react-flow__controls-button:active {
    transform: translateY(0) !important;
  }
  
  .react-flow-controls-enhanced .react-flow__controls-button svg {
    width: 16px !important;
    height: 16px !important;
  }
  
  .react-flow-controls-enhanced {
    box-shadow: none !important;
  }
  
  /* Dark mode styles */
  .dark .react-flow-controls-enhanced .react-flow__controls-button {
    background: #374151 !important;
    border-color: #4b5563 !important;
    color: #f9fafb !important;
  }
  
  .dark .react-flow-controls-enhanced .react-flow__controls-button:hover {
    background: #4b5563 !important;
    border-color: #6b7280 !important;
  }
`;

interface WorkflowViewerProps {
  initialWorkflow?: WorkflowGraph;
  className?: string;
}

const nodeTypes: NodeTypes = {
  comfyNode: ComfyUINode,
};

const WorkflowViewer: React.FC<WorkflowViewerProps> = ({ initialWorkflow, className }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>(initialWorkflow?.nodes || []);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>(initialWorkflow?.edges || []);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);

  // Handle file upload
  const handleFileUpload = useCallback(async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsLoading(true);
    try {
      const workflowGraph = await loadWorkflowFromFile(file);
      setNodes(workflowGraph.nodes);
      setEdges(workflowGraph.edges);
    } catch (error) {
      console.error('Error loading workflow:', error);
      alert('Error loading workflow file. Please check the file format.');
    } finally {
      setIsLoading(false);
    }
  }, [setNodes, setEdges]);

  // Handle node selection
  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
  }, []);

  // Stats about the workflow
  const workflowStats = useMemo(() => {
    const nodeTypes = nodes.reduce((acc, node) => {
      const type = node.data.class_type;
      acc[type] = (acc[type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return {
      totalNodes: nodes.length,
      totalEdges: edges.length,
      nodeTypes
    };
  }, [nodes, edges]);

  return (
    <div className={`h-full w-full ${className}`}>
      {/* Inject custom styles */}
      <style dangerouslySetInnerHTML={{ __html: controlsStyle }} />
      <div className="flex flex-col h-full">
        {/* Header */}
        <div className="flex-shrink-0 p-4 border-b">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold">ComfyUI Workflow Viewer</h2>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {workflowStats.totalNodes} nodes, {workflowStats.totalEdges} connections
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <input
                type="file"
                accept=".json"
                onChange={handleFileUpload}
                style={{ display: 'none' }}
                id="workflow-upload"
              />
              <Button
                variant="outline"
                onClick={() => document.getElementById('workflow-upload')?.click()}
                disabled={isLoading}
                size="sm"
              >
                <Upload className="w-4 h-4 mr-2" />
                Load Workflow
              </Button>
            </div>
          </div>
        </div>

        {/* Main content */}
        <div className="flex-1 flex">
          {/* Workflow canvas */}
          <div className="flex-1 relative">
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onNodeClick={onNodeClick}
              nodeTypes={nodeTypes}
              fitView
              fitViewOptions={{
                padding: 0.1,
                includeHiddenNodes: false
              }}
              defaultEdgeOptions={{
                style: { strokeWidth: 2 },
                type: 'default'
              }}
              proOptions={{ hideAttribution: true }}
            >
              <Background color="#aaa" gap={16} />
              <Controls 
                showZoom={true}
                showFitView={true}
                showInteractive={false}
                className="react-flow-controls-enhanced"
              />
              <MiniMap 
                nodeColor={(node) => {
                  const nodeType = node.data.class_type;
                  return nodeType ? `#${Math.abs(nodeType.split('').reduce((a, b) => {
                    a = ((a << 5) - a) + b.charCodeAt(0);
                    return a & a;
                  }, 0)).toString(16).slice(0, 6)}` : '#ddd';
                }}
                maskColor="rgba(0, 0, 0, 0.1)"
                style={{
                  backgroundColor: 'rgba(255, 255, 255, 0.8)',
                }}
              />
            </ReactFlow>
          </div>

          {/* Sidebar */}
          <div className="w-80 border-l bg-white dark:bg-gray-900 overflow-y-auto">
            <div className="p-4 space-y-4">
              {/* Workflow stats */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Workflow Statistics</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Total Nodes:</span>
                      <Badge variant="secondary">{workflowStats.totalNodes}</Badge>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Total Edges:</span>
                      <Badge variant="secondary">{workflowStats.totalEdges}</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Node types */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Node Types</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {Object.entries(workflowStats.nodeTypes).map(([type, count]) => (
                      <div key={type} className="flex justify-between items-center text-xs">
                        <span className="truncate pr-2">{type}</span>
                        <Badge variant="outline" className="text-xs">
                          {count}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Selected node details */}
              {selectedNode && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm">Selected Node</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div>
                        <p className="font-medium text-sm">{selectedNode.data.label}</p>
                        <p className="text-xs text-gray-600 dark:text-gray-400">
                          ID: {selectedNode.id}
                        </p>
                      </div>
                      <div>
                        <p className="font-medium text-xs mb-2">Inputs:</p>
                        <div className="space-y-1">
                          {Object.entries(selectedNode.data.inputs).map(([key, value]) => (
                            <div key={key} className="text-xs">
                              <span className="text-gray-600 dark:text-gray-400">{key}:</span>
                              <span className="ml-2 font-mono">
                                {typeof value === 'object' 
                                  ? JSON.stringify(value, null, 2)
                                  : String(value)
                                }
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const WorkflowViewerWithProvider: React.FC<WorkflowViewerProps> = (props) => {
  return (
    <ReactFlowProvider>
      <WorkflowViewer {...props} />
    </ReactFlowProvider>
  );
};

export default WorkflowViewerWithProvider;