import React, { useState, useEffect, useCallback, memo } from 'react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Card, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { 
    MatrixSettings as MatrixSettingsType, 
    MatrixParameter, 
    MATRIX_PARAMETERS, 
    defaultMatrixSettings, 
    CoreGenerationSettings,
    MatrixParameterName
} from '@/types/generationSettings';

interface MatrixSettingsProps {
  onSettingsChange: (settings: MatrixSettingsType) => void;
}

interface ParameterRowProps {
  label: string;
  axis: 'xAxis' | 'yAxis' | 'zAxis';
  parameter: MatrixParameter;
  onParameterUpdate: (axis: 'xAxis' | 'yAxis' | 'zAxis', updates: Partial<MatrixParameter>) => void;
  usedParameters: string[];
}

const ParameterRow = memo<ParameterRowProps>(({ 
  label, 
  axis, 
  parameter,
  onParameterUpdate,
  usedParameters
}) => {
  const [localValue, setLocalValue] = useState(parameter.values);

  useEffect(() => {
    setLocalValue(parameter.values);
  }, [parameter.values]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setLocalValue(newValue);
    onParameterUpdate(axis, { values: newValue });
  };

  const handleParameterChange = (value: MatrixParameterName) => {
    onParameterUpdate(axis, { 
      name: value, 
      enabled: value !== 'Nothing',
      values: value !== 'Nothing' ? parameter.values : ''
    });
  };

  const handleTypeChange = (value: 'range' | 'list') => {
    onParameterUpdate(axis, { type: value });
  };

  return (
    <div className="grid grid-cols-12 gap-3 items-center mb-3">
      <div className="col-span-2 text-sm font-medium text-muted-foreground">{label}</div>
      <div className="col-span-3">
        <Select 
          value={parameter.name} 
          onValueChange={handleParameterChange}
        >
          <SelectTrigger className="w-full">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {MATRIX_PARAMETERS.map((param) => {
              const isCurrentlySelected = param === parameter.name;
              const isUsedElsewhere = usedParameters.includes(param);
              
              if (isCurrentlySelected || !isUsedElsewhere) {
                return (
                  <SelectItem key={param} value={param}>
                    {param}
                  </SelectItem>
                );
              }
              return null;
            })}
          </SelectContent>
        </Select>
      </div>
      <div className="col-span-2">
        <Select
          value={parameter.type}
          onValueChange={handleTypeChange}
          disabled={parameter.name === 'Nothing'}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="list">List</SelectItem>
            <SelectItem value="range">Range</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="col-span-5">
        <Input
          placeholder={
            parameter.type === 'range' 
              ? "e.g., 1-8" 
              : "e.g., 1, 2, 4, 8"
          }
          value={localValue}
          onChange={handleInputChange}
          disabled={parameter.name === 'Nothing'}
          className="text-sm"
        />
      </div>
    </div>
  );
});

ParameterRow.displayName = 'ParameterRow';

const MatrixSettings: React.FC<MatrixSettingsProps> = ({
  onSettingsChange
}) => {
  const [matrixSettings, setMatrixSettings] = useState<MatrixSettingsType>(defaultMatrixSettings);

  const updateMatrixSettings = useCallback((updates: Partial<MatrixSettingsType>) => {
    const newSettings = { ...matrixSettings, ...updates };
    setMatrixSettings(newSettings);
    onSettingsChange(newSettings);
  }, [matrixSettings, onSettingsChange]);

  const updateParameter = useCallback((axis: 'xAxis' | 'yAxis' | 'zAxis', updates: Partial<MatrixParameter>) => {
    const newParameter = { ...matrixSettings[axis], ...updates };
    updateMatrixSettings({ [axis]: newParameter });
  }, [matrixSettings, updateMatrixSettings]);

  const getUsedParameters = (currentAxis: 'xAxis' | 'yAxis' | 'zAxis'): string[] => {
    const used: string[] = [];
    if (currentAxis !== 'xAxis' && matrixSettings.xAxis.name !== 'Nothing') {
      used.push(matrixSettings.xAxis.name);
    }
    if (currentAxis !== 'yAxis' && matrixSettings.yAxis.name !== 'Nothing') {
      used.push(matrixSettings.yAxis.name);
    }
    if (currentAxis !== 'zAxis' && matrixSettings.zAxis?.name !== 'Nothing') {
      used.push(matrixSettings.zAxis.name);
    }
    return used;
  };

  return (
    <Card className="bg-transparent border-none shadow-none">
      <CardContent className="p-0">
        <ParameterRow
          label="X type"
          axis="xAxis"
          parameter={matrixSettings.xAxis}
          onParameterUpdate={updateParameter}
          usedParameters={getUsedParameters('xAxis')}
        />
        <ParameterRow
          label="Y type"
          axis="yAxis"
          parameter={matrixSettings.yAxis}
          onParameterUpdate={updateParameter}
          usedParameters={getUsedParameters('yAxis')}
        />
        <ParameterRow
          label="Z type"
          axis="zAxis"
          parameter={matrixSettings.zAxis}
          onParameterUpdate={updateParameter}
          usedParameters={getUsedParameters('zAxis')}
        />

        <Separator className="my-4" />

        <div className="grid grid-cols-2 gap-x-6 gap-y-4">
          <div className="flex items-center space-x-2">
            <Checkbox
              id="draw-legend"
              checked={matrixSettings.drawLegend}
              onCheckedChange={(checked) => updateMatrixSettings({ drawLegend: !!checked })}
            />
            <label htmlFor="draw-legend" className="text-sm">
              Draw legend
            </label>
          </div>
          <div className="flex items-center space-x-2">
            <Checkbox
              id="include-sub-images"
              checked={matrixSettings.includeSubImages}
              onCheckedChange={(checked) => updateMatrixSettings({ includeSubImages: !!checked })}
            />
            <label htmlFor="include-sub-images" className="text-sm">
              Include Sub Images
            </label>
          </div>
          <div className="flex items-center space-x-2">
            <Checkbox
              id="include-sub-grids"
              checked={matrixSettings.includeSubgrids}
              onCheckedChange={(checked) => updateMatrixSettings({ includeSubgrids: !!checked })}
            />
            <label htmlFor="include-sub-grids" className="text-sm">
              Include Sub Grids
            </label>
          </div>
          <div className="flex items-center space-x-2">
            <Checkbox
              id="keep-seeds"
              checked={matrixSettings.keepSeedsForRows}
              onCheckedChange={(checked) => updateMatrixSettings({ keepSeedsForRows: !!checked })}
            />
            <label htmlFor="keep-seeds" className="text-sm">
              Keep -1 for seeds
            </label>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default MatrixSettings; 