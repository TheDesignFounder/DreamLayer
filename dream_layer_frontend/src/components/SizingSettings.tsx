import React, { useState } from 'react';
import { Slider as ShadcnSlider } from "@/components/ui/slider";
import Slider from "@/components/Slider";
import { useI18n } from "@/i18n/i18nContext";

interface SizingSettingsProps {
  width: number;
  height: number;
  onChange: (width: number, height: number) => void;
}

const SizingSettings: React.FC<SizingSettingsProps> = ({
  width,
  height,
  onChange
}) => {
  const { t } = useI18n();
  const handleWidthChange = (newWidth: number) => {
    onChange(newWidth, height);
  };

  const handleHeightChange = (newHeight: number) => {
    onChange(width, newHeight);
  };

  return (
    <div className="grid grid-cols-2 gap-4">
      <div>
        <label className="text-sm font-medium">{t('txt2img.width')}</label>
        <input
          type="number"
          className="mt-1 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          min={64}
          max={2048}
          step={64}
          value={width}
          onChange={(e) => handleWidthChange(parseInt(e.target.value))}
        />
      </div>
      <div>
        <label className="text-sm font-medium">{t('txt2img.height')}</label>
        <input
          type="number"
          className="mt-1 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          min={64}
          max={2048}
          step={64}
          value={height}
          onChange={(e) => handleHeightChange(parseInt(e.target.value))}
        />
      </div>
    </div>
  );
};

export default SizingSettings;
