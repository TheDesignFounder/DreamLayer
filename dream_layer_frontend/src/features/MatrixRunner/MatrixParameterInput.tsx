import React from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { parseParameter } from '@/utils/matrixUtils';

interface MatrixParameterInputProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder: string;
  description: string;
}

const MatrixParameterInput: React.FC<MatrixParameterInputProps> = ({
  label,
  value,
  onChange,
  placeholder,
  description
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value);
  };

  const getParsedInfo = () => {
    if (!value.trim()) return null;
    
    try {
      const parsed = parseParameter(value);
      return {
        type: parsed.type,
        count: parsed.values.length,
        values: parsed.values.slice(0, 5) // Show first 5 values
      };
    } catch (error) {
      return { error: 'Invalid format' };
    }
  };

  const parsedInfo = getParsedInfo();

  return (
    <div className="space-y-2">
      <Label htmlFor={label.toLowerCase()}>{label}</Label>
      <Input
        id={label.toLowerCase()}
        value={value}
        onChange={handleChange}
        placeholder={placeholder}
        className={parsedInfo?.error ? 'border-red-500' : ''}
      />
      
      {parsedInfo && !parsedInfo.error && (
        <div className="flex items-center gap-2 text-xs">
          <Badge variant="outline" className="text-xs">
            {parsedInfo.type}
          </Badge>
          <span className="text-muted-foreground">
            {parsedInfo.count} value{parsedInfo.count !== 1 ? 's' : ''}
          </span>
          {parsedInfo.values.length > 0 && (
            <span className="text-muted-foreground">
              ({parsedInfo.values.join(', ')}
              {parsedInfo.count > 5 && '...'})
            </span>
          )}
        </div>
      )}
      
      {parsedInfo?.error && (
        <div className="text-xs text-red-500">
          {parsedInfo.error}
        </div>
      )}
      
      <p className="text-xs text-muted-foreground">
        {description}
      </p>
    </div>
  );
};

export default MatrixParameterInput; 