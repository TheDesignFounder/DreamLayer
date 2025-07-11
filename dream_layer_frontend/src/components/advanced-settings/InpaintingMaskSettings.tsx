import React, { useState } from "react";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import Slider from "@/components/Slider";

const InpaintingMaskSettings = () => {
  const [maskBlur, setMaskBlur] = useState(4);
  const [maskMode, setMaskMode] = useState("inpaint-masked");
  const [maskedContent, setMaskedContent] = useState("fill");
  const [maskedContentMode, setMaskedContentMode] = useState("whole-picture");
  const [onlyMaskedPadding, setOnlyMaskedPadding] = useState(32);

  return (
    <div className="space-y-6 mt-2">
      <Slider
        min={1}
        max={64}
        defaultValue={maskBlur}
        label="a) Mask Blur | <span class='text-gray-500'>Optimal Level: 4-8</span>"
        onChange={setMaskBlur}
        step={1}
        tooltipKey="maskBlur"
      />
      
      <div className="space-y-3">
        <label className="text-sm font-medium">b) Mask Mode</label>
        <RadioGroup value={maskMode} onValueChange={setMaskMode} className="flex flex-wrap gap-4">
          <div className="flex items-center space-x-2 border rounded-lg p-3 min-w-[140px]">
            <RadioGroupItem value="inpaint-masked" id="inpaint-masked" />
            <Label htmlFor="inpaint-masked" className="cursor-pointer">Inpaint Masked</Label>
          </div>
          <div className="flex items-center space-x-2 border rounded-lg p-3 min-w-[140px]">
            <RadioGroupItem value="inpaint-not-masked" id="inpaint-not-masked" />
            <Label htmlFor="inpaint-not-masked" className="cursor-pointer">Inpaint Not Masked</Label>
          </div>
        </RadioGroup>
      </div>
      
      <div className="space-y-3">
        <label className="text-sm font-medium">c) Masked Content</label>
        <RadioGroup value={maskedContent} onValueChange={setMaskedContent} className="flex flex-wrap gap-3">
          <div className="flex items-center space-x-2 border rounded-lg p-3 min-w-[100px]">
            <RadioGroupItem value="fill" id="fill" />
            <Label htmlFor="fill" className="cursor-pointer">Fill</Label>
          </div>
          <div className="flex items-center space-x-2 border rounded-lg p-3 min-w-[100px]">
            <RadioGroupItem value="original" id="original" />
            <Label htmlFor="original" className="cursor-pointer">Original</Label>
          </div>
          <div className="flex items-center space-x-2 border rounded-lg p-3 min-w-[120px]">
            <RadioGroupItem value="latent-noise" id="latent-noise" />
            <Label htmlFor="latent-noise" className="cursor-pointer">Latent Noise</Label>
          </div>
          <div className="flex items-center space-x-2 border rounded-lg p-3 min-w-[130px]">
            <RadioGroupItem value="latent-nothing" id="latent-nothing" />
            <Label htmlFor="latent-nothing" className="cursor-pointer">Latent Nothing</Label>
          </div>
        </RadioGroup>
      </div>
      
      <div className="space-y-3">
        <label className="text-sm font-medium">d) Masked Content</label>
        <RadioGroup value={maskedContentMode} onValueChange={setMaskedContentMode} className="flex flex-wrap gap-4">
          <div className="flex items-center space-x-2 border rounded-lg p-3 min-w-[140px]">
            <RadioGroupItem value="whole-picture" id="whole-picture" />
            <Label htmlFor="whole-picture" className="cursor-pointer">Whole Picture</Label>
          </div>
          <div className="flex items-center space-x-2 border rounded-lg p-3 min-w-[140px]">
            <RadioGroupItem value="only-masked" id="only-masked" />
            <Label htmlFor="only-masked" className="cursor-pointer">Only Masked</Label>
          </div>
        </RadioGroup>
      </div>
      
      <Slider
        min={0}
        max={128}
        defaultValue={onlyMaskedPadding}
        label="e) Only Masked Padding, Pixel | <span class='text-gray-500'>Optimal Level: 32px</span>"
        onChange={setOnlyMaskedPadding}
        step={1}
        tooltipKey="onlyMaskedPadding"
      />
    </div>
  );
};

export default InpaintingMaskSettings;
