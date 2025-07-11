import React from 'react';
import { Handle, Position } from '@xyflow/react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { getNodeColor } from '@/utils/workflowParser';

interface ComfyUINodeProps {
  data: {
    label: string;
    class_type: string;
    inputs: Record<string, any>;
  };
  selected?: boolean;
}

const ComfyUINode: React.FC<ComfyUINodeProps> = ({ data, selected }) => {
  const { label, class_type, inputs } = data;
  const nodeColor = getNodeColor(class_type);
  
  return (
    <Card 
      className={`min-w-[200px] max-w-[300px] shadow-lg transition-all duration-200 ${
        selected ? 'ring-2 ring-blue-500' : ''
      }`}
      style={{
        borderLeftColor: nodeColor,
        borderLeftWidth: '4px'
      }}
    >
      {/* Input handle */}
      <Handle
        type="target"
        position={Position.Left}
        style={{
          background: nodeColor,
          borderColor: nodeColor,
          width: 8,
          height: 8
        }}
      />
      
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium text-gray-900 dark:text-gray-100">
          {label}
        </CardTitle>
        <Badge 
          variant="secondary" 
          className="text-xs w-fit"
          style={{
            backgroundColor: nodeColor + '20',
            color: nodeColor
          }}
        >
          {class_type}
        </Badge>
      </CardHeader>
      
      <CardContent className="pt-0">
        <div className="space-y-2">
          {Object.entries(inputs).map(([key, value]) => (
            <div key={key} className="flex justify-between items-center text-xs">
              <span className="text-gray-600 dark:text-gray-400 truncate pr-2">
                {key}:
              </span>
              <span
                className="text-gray-900 dark:text-gray-100 font-mono text-right max-w-[120px] truncate"
                title={typeof value === 'object' ? JSON.stringify(value) : undefined}
              >
                {typeof value === 'object'
                  ? '[object]'
                  : String(value).slice(0, 20) + (String(value).length > 20 ? '...' : '')
                }
              </span>
            </div>
          ))}
        </div>
      </CardContent>
      
      {/* Output handle */}
      <Handle
        type="source"
        position={Position.Right}
        style={{
          background: nodeColor,
          borderColor: nodeColor,
          width: 8,
          height: 8
        }}
      />
    </Card>
  );
};

export default ComfyUINode;