import React from 'react';
import { X, Copy, Check } from 'lucide-react';
import { Run } from '@/types/run';

interface RunConfigModalProps {
  run: Run | null;
  isOpen: boolean;
  onClose: () => void;
}

const RunConfigModal: React.FC<RunConfigModalProps> = ({ run, isOpen, onClose }) => {
  const [copied, setCopied] = React.useState(false);

  if (!isOpen || !run) return null;

  const configString = JSON.stringify(run.config, null, 2);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(configString);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp).toLocaleString();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-100';
      case 'failed':
        return 'text-red-600 bg-red-100';
      case 'running':
        return 'text-blue-600 bg-blue-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black bg-opacity-50"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative bg-background rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border">
          <div>
            <h2 className="text-xl font-semibold text-foreground">Run Configuration</h2>
            <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
              <span>Run ID: {run.id}</span>
              <span>•</span>
              <span>{formatTimestamp(run.timestamp)}</span>
              <span>•</span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(run.status)}`}>
                {run.status}
              </span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-muted rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          <div className="space-y-6">
            {/* Basic Info */}
            <div>
              <h3 className="text-lg font-medium text-foreground mb-3">Basic Information</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium text-muted-foreground">Model:</span>
                  <span className="ml-2 text-foreground">{run.config.model || 'N/A'}</span>
                </div>
                <div>
                  <span className="font-medium text-muted-foreground">VAE:</span>
                  <span className="ml-2 text-foreground">{run.config.vae || 'N/A'}</span>
                </div>
                <div>
                  <span className="font-medium text-muted-foreground">Sampler:</span>
                  <span className="ml-2 text-foreground">{run.config.sampler}</span>
                </div>
                <div>
                  <span className="font-medium text-muted-foreground">Steps:</span>
                  <span className="ml-2 text-foreground">{run.config.steps}</span>
                </div>
                <div>
                  <span className="font-medium text-muted-foreground">CFG Scale:</span>
                  <span className="ml-2 text-foreground">{run.config.cfg_scale}</span>
                </div>
                <div>
                  <span className="font-medium text-muted-foreground">Seed:</span>
                  <span className="ml-2 text-foreground">{run.config.seed}</span>
                </div>
                <div>
                  <span className="font-medium text-muted-foreground">Dimensions:</span>
                  <span className="ml-2 text-foreground">{run.config.width} × {run.config.height}</span>
                </div>
                <div>
                  <span className="font-medium text-muted-foreground">Batch:</span>
                  <span className="ml-2 text-foreground">{run.config.batch_size} × {run.config.batch_count}</span>
                </div>
              </div>
            </div>

            {/* Prompts */}
            <div>
              <h3 className="text-lg font-medium text-foreground mb-3">Prompts</h3>
              <div className="space-y-3">
                <div>
                  <span className="font-medium text-muted-foreground text-sm">Positive Prompt:</span>
                  <p className="mt-1 p-3 bg-muted rounded-lg text-sm">{run.config.prompt || 'N/A'}</p>
                </div>
                <div>
                  <span className="font-medium text-muted-foreground text-sm">Negative Prompt:</span>
                  <p className="mt-1 p-3 bg-muted rounded-lg text-sm">{run.config.negative_prompt || 'N/A'}</p>
                </div>
              </div>
            </div>

            {/* LoRAs */}
            {run.config.loras && run.config.loras.length > 0 && (
              <div>
                <h3 className="text-lg font-medium text-foreground mb-3">LoRAs</h3>
                <div className="space-y-2">
                  {run.config.loras.map((lora, index) => (
                    <div key={index} className="flex items-center gap-2 p-2 bg-muted rounded-lg">
                      <span className="text-sm font-medium">{lora.name}</span>
                      <span className="text-xs text-muted-foreground">(strength: {lora.strength})</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* ControlNets */}
            {run.config.controlnets && run.config.controlnets.length > 0 && (
              <div>
                <h3 className="text-lg font-medium text-foreground mb-3">ControlNets</h3>
                <div className="space-y-2">
                  {run.config.controlnets.map((controlnet, index) => (
                    <div key={index} className="flex items-center gap-2 p-2 bg-muted rounded-lg">
                      <span className="text-sm font-medium">{controlnet.name}</span>
                      <span className="text-xs text-muted-foreground">(strength: {controlnet.strength})</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Full Config JSON */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-medium text-foreground">Full Configuration (JSON)</h3>
                <button
                  onClick={handleCopy}
                  className="flex items-center gap-2 px-3 py-1 text-sm bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
                >
                  {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  {copied ? 'Copied!' : 'Copy'}
                </button>
              </div>
              <pre className="p-4 bg-muted rounded-lg text-xs overflow-x-auto max-h-64 overflow-y-auto">
                {configString}
              </pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RunConfigModal; 