import { useState, useEffect } from "react";
import Slider from "./Slider";

interface OutputQuantityProps {
  batchSize: number;
  batchCount: number;
  onChange: (batchSize: number, batchCount: number) => void;
}

const OutputQuantity: React.FC<OutputQuantityProps> = ({
  batchSize,
  batchCount,
  onChange
}) => {
  const handleBatchSizeChange = (newSize: number) => {
    onChange(newSize, batchCount);
  };

  const handleBatchCountChange = (newCount: number) => {
    onChange(batchSize, newCount);
  };

  const getBatchCountLabel = () => {
    return `a) Batch Count | <span style='color: #64748B;'>Optimal Level: 1–3</span>`;
  };

  const getBatchSizeLabel = () => {
    return `a) Batch Size | <span style='color: #64748B;'>Optimal Level: 4–7</span>`;
  };

  return (
    <div className="space-y-4">
      <div className="hidden"><Slider
        min={1}
        max={25}
        defaultValue={25}
        label={getBatchCountLabel()}
        onChange={handleBatchCountChange}
      /></div>
      
      <Slider
        min={1}
        max={8}
        defaultValue={4}
        label={getBatchSizeLabel()}
        onChange={handleBatchSizeChange}
        tooltipKey="batchSize"
      />
    </div>
  );
};

export default OutputQuantity;
