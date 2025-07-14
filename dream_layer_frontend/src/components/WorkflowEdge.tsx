import React, { type FC } from 'react';
import {
  getBezierPath,
  EdgeLabelRenderer,
  BaseEdge,
  type EdgeProps,
  type Edge,
} from '@xyflow/react';

const WorkflowEdge: FC<EdgeProps<Edge<{ 
  sourceLabel?: string | null; 
  targetLabel?: string | null; 
}>>> = ({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
}) => {
  const [edgePath] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  return (
    <>
      <BaseEdge 
        id={id} 
        path={edgePath} 
        style={{ 
          stroke: 'hsl(var(--muted-foreground))',
          strokeWidth: 2 
        }} 
      />
      {/* Only render labels if they exist for original workflow connections */}
      {data?.sourceLabel && data?.targetLabel && (
        <EdgeLabelRenderer>
          {/* Source Label */}
          <div
            style={{
              position: 'absolute',
              transform: `translate(-50%, -50%) translate(${sourceX}px,${sourceY}px)`,
              background: 'transparent',
              color: 'hsl(var(--muted-foreground))',
              fontSize: '10px',
              fontWeight: 600,
            }}
            className="nodrag nopan"
          >
          </div>
          
          {/* Target Label */}
          <div
            style={{
              position: 'absolute',
              transform: `translate(-50%, -50%) translate(${targetX}px,${targetY}px)`,
              background: 'transparent',
              color: 'hsl(var(--muted-foreground))',
              fontSize: '10px',
              fontWeight: 600,
            }}
            className="nodrag nopan"
          >
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  );
};

export default WorkflowEdge;
