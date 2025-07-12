import React, { useState, useCallback, useMemo, useEffect } from 'react';
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
import styles from './WorkflowViewer.module.css';

/**
 * Utility to summarize/truncate large or deeply nested JSON values.
 * If the value is a primitive, returns as string.
 * If the value is an object/array, returns a summarized string if too large/deep.
 */
function summarizeValue(value: any, maxLength = 80, maxDepth = 2, depth = 0): string {
  if (value === null || typeof value !== "object") {
    return String(value);
  }
  if (depth >= maxDepth) {
    return Array.isArray(value) ? `[Array(${value.length})]` : "{...}";
  }
  let str = JSON.stringify(value);
  if (str.length > maxLength) {
    if (Array.isArray(value)) {
      return `[Array(${value.length})]`;
    }
    return "{...}";
  }
  return str;
}

type InputValueDisplayProps = {
  inputKey: string;
  value: any;
};

const InputValueDisplay: React.FC<InputValueDisplayProps> = ({ inputKey, value }) => {
  const [expanded, setExpanded] = useState(false);

  const isObject = value !== null && typeof value === "object";
  const summarized = summarizeValue(value);

  return (
    <div className="text-xs">
      <span className="text-gray-600 dark:text-gray-400">{inputKey}:</span>
      <span className="ml-2 font-mono">
        {isObject ? (
          <>
            {expanded ? (
              <pre className="whitespace-pre-wrap text-xs">{JSON.stringify(value, null, 2)}</pre>
            ) : (
              <span>{summarized}</span>
            )}
            <button
              className="ml-2 text-blue-500 underline cursor-pointer text-xs hover:text-blue-700"
              onClick={() => setExpanded((e) => !e)}
            >
              {expanded ? "Collapse" : "Expand"}
            </button>
          </>
        ) : (
          String(value)
        )}
      </span>
    </div>
  );
};


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

  // Clear selectedNode whenever nodes change to prevent referencing removed nodes
  useEffect(() => {
    setSelectedNode(null);
  }, [nodes]);

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
                className={styles.controlsEnhanced}
              />
              <MiniMap 
                nodeColor={(node) => {
                  const nodeType = node.data.class_type;
                  return nodeType ? `#${Math.abs(nodeType.split('').reduce((a, b) => {
                    a = ((a << 5) - a) + b.charCodeAt(0);
                    return a;
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
                            <InputValueDisplay key={key} inputKey={key} value={value} />
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