import React, { useState } from "react";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger
} from "@/components/ui/accordion";
import { useI18n } from "@/i18n/i18nContext";

// Import component modules
import FaceRestorationSettings from "@/components/advanced-settings/FaceRestorationSettings";
import HiresFixSettings from "@/components/advanced-settings/HiresFixSettings";
import ImageRefinerSettings from "@/components/advanced-settings/ImageRefinerSettings";
import PromptTesterSettings from "@/components/advanced-settings/PromptTesterSettings";
import SDXLStyleSettings from "@/components/advanced-settings/SDXLStyleSettings";
import SDUpscalerSettings from "@/components/advanced-settings/SDUpscalerSettings";
import InpaintingMaskSettings from "@/components/advanced-settings/InpaintingMaskSettings";
import TilingSettings from "@/components/advanced-settings/TilingSettings";

interface AdvancedSettingsProps {
  showHiresFix?: boolean;
  showImg2ImgSpecific?: boolean;
  activeImg2ImgTool?: string;
  // Face Restoration Props
  restoreFaces?: boolean;
  onRestoreFacesChange?: (enabled: boolean) => void;
  faceRestorationModel?: string;
  onFaceRestorationModelChange?: (model: string) => void;
  codeformerWeight?: number;
  onCodeformerWeightChange?: (weight: number) => void;
  gfpganWeight?: number;
  onGfpganWeightChange?: (weight: number) => void;
  // Tiling Props
  tiling?: boolean;
  onTilingChange?: (enabled: boolean) => void;
  tileSize?: number;
  onTileSizeChange?: (size: number) => void;
  overlap?: number;
  onOverlapChange?: (overlap: number) => void;
  hiresFix?: boolean;
  onHiresFixChange?: (enabled: boolean) => void;
  refinerEnabled?: boolean;
  onRefinerEnabledChange?: (enabled: boolean) => void;
  refinerModel?: string;
  onRefinerModelChange?: (model: string) => void;
  refinerSwitchAt?: number;
  onRefinerSwitchAtChange?: (value: number) => void;
}

const AdvancedSettings = ({
  showHiresFix = true,
  showImg2ImgSpecific = false,
  activeImg2ImgTool = "img2img",
  // Face Restoration Props
  restoreFaces = false,
  onRestoreFacesChange,
  faceRestorationModel = "codeformer",
  onFaceRestorationModelChange,
  codeformerWeight = 0.5,
  onCodeformerWeightChange,
  gfpganWeight = 0.5,
  onGfpganWeightChange,
  // Tiling Props
  tiling = false,
  onTilingChange,
  tileSize = 256,
  onTileSizeChange,
  overlap = 0,
  onOverlapChange,
  hiresFix = false,
  onHiresFixChange,
  refinerEnabled = false,
  onRefinerEnabledChange,
  refinerModel,
  onRefinerModelChange,
  refinerSwitchAt,
  onRefinerSwitchAtChange
}: AdvancedSettingsProps) => {
  const { t } = useI18n();
  // Hires.fix State
  const [upscaleMethod, setUpscaleMethod] = useState("upscale-by");
  const [upscaleFactor, setUpscaleFactor] = useState(2.5);
  const [hiresSteps, setHiresSteps] = useState(15);
  const [denoisingStrength, setDenoisingStrength] = useState(0.5);
  const [resizeWidth, setResizeWidth] = useState(4000);
  const [resizeHeight, setResizeHeight] = useState(4000);
  const [selectedUpscaler, setSelectedUpscaler] = useState("4x-ultrasharp");

  // Image Refiner State
  const [selectedRefiner, setSelectedRefiner] = useState("none");
  const [refineSwitchAt, setRefineSwitchAt] = useState(0.8);

  return (
    <div className="space-y-0">
      <Accordion type="multiple" className="space-y-[18px]">
        <AccordionItem value="fix-human-faces" className="border border-border rounded-md overflow-hidden">
          <div className="flex items-center py-3 px-3">
            <div className="flex items-center flex-1">
              <Checkbox
                id="restore-faces"
                className="mr-3"
                checked={restoreFaces}
                onCheckedChange={(checked) => onRestoreFacesChange?.(checked === true)}
              />
              <label htmlFor="restore-faces" className="text-[#2563EB] font-medium">
                {t('advanced.restoreFaces')}
              </label>
            </div>
            <AccordionTrigger className="p-0 flex-0">
            </AccordionTrigger>
          </div>
          <AccordionContent className="pt-0 px-3 pb-3">
            <FaceRestorationSettings
              faceRestorationModel={faceRestorationModel}
              setFaceRestorationModel={onFaceRestorationModelChange || (() => {})}
              codeformerWeight={codeformerWeight}
              setCodeformerWeight={onCodeformerWeightChange || (() => {})}
              gfpganWeight={gfpganWeight}
              setGfpganWeight={onGfpganWeightChange || (() => {})}
            />
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="pattern-mode" className="border border-border rounded-md overflow-hidden">
          <div className="flex items-center py-3 px-3">
            <div className="flex items-center flex-1">
              <Checkbox
                id="pattern-mode"
                className="mr-3"
                checked={tiling}
                onCheckedChange={(checked) => onTilingChange?.(checked === true)}
              />
              <label htmlFor="pattern-mode" className="text-[#2563EB] font-medium">
                Tiling - Pattern Mode
              </label>
            </div>
            <AccordionTrigger className="p-0 flex-0">
            </AccordionTrigger>
          </div>
          <AccordionContent className="pt-0 px-3 pb-3">
            <TilingSettings
              tileSize={tileSize}
              setTileSize={onTileSizeChange}
              overlap={overlap}
              setOverlap={onOverlapChange}
            />
          </AccordionContent>
        </AccordionItem>

        {showHiresFix && (
          <AccordionItem value="hires-fix" className="border border-border rounded-md overflow-hidden">
            <div className="flex items-center py-3 px-3">
              <div className="flex items-center flex-1">
                <Checkbox id="hires-fix" className="mr-3" checked={hiresFix} onCheckedChange={(checked) => onHiresFixChange?.(checked === true)} />
                <label htmlFor="hires-fix" className="text-[#2563EB] font-medium">
                  Hires.fix - High-Resolution Refinement
                </label>
              </div>
              <AccordionTrigger className="p-0 flex-0">
              </AccordionTrigger>
            </div>
            <AccordionContent className="pt-0 px-3 pb-3">
              <HiresFixSettings
                upscaleMethod={upscaleMethod}
                setUpscaleMethod={setUpscaleMethod}
                upscaleFactor={upscaleFactor}
                setUpscaleFactor={setUpscaleFactor}
                hiresSteps={hiresSteps}
                setHiresSteps={setHiresSteps}
                denoisingStrength={denoisingStrength}
                setDenoisingStrength={setDenoisingStrength}
                resizeWidth={resizeWidth}
                setResizeWidth={setResizeWidth}
                resizeHeight={resizeHeight}
                setResizeHeight={setResizeHeight}
                selectedUpscaler={selectedUpscaler}
                setSelectedUpscaler={setSelectedUpscaler}
              />
            </AccordionContent>
          </AccordionItem>
        )}

        {showImg2ImgSpecific && (
          <AccordionItem value="sd-upscaler" className="border border-border rounded-md overflow-hidden">
            <div className="flex items-center py-3 px-3">
              <div className="flex items-center flex-1">
                <Checkbox id="sd-upscaler" className="mr-3" />
                <label htmlFor="sd-upscaler" className="text-[#2563EB] font-medium">
                  SD Upscaler
                </label>
              </div>
              <AccordionTrigger className="p-0 flex-0">
              </AccordionTrigger>
            </div>
            <AccordionContent className="pt-0 px-3 pb-3">
              <SDUpscalerSettings />
            </AccordionContent>
          </AccordionItem>
        )}

        {showImg2ImgSpecific && activeImg2ImgTool !== "img2img" && (
          <AccordionItem value="inpainting-mask" className="border border-border rounded-md overflow-hidden">
            <div className="flex items-center py-3 px-3">
              <div className="flex items-center flex-1">
                <Checkbox id="inpainting-mask" className="mr-3" />
                <label htmlFor="inpainting-mask" className="text-[#2563EB] font-medium">
                  Inpainting Mask Settings
                </label>
              </div>
              <AccordionTrigger className="p-0 flex-0">
              </AccordionTrigger>
            </div>
            <AccordionContent className="pt-0 px-3 pb-3">
              <InpaintingMaskSettings />
            </AccordionContent>
          </AccordionItem>
        )}

        <AccordionItem value="image-refiner" className="border border-border rounded-md overflow-hidden">
          <div className="flex items-center py-3 px-3">
            <div className="flex items-center flex-1">
              <Checkbox id="image-refiner" className="mr-3" checked={refinerEnabled} onCheckedChange={(checked) => onRefinerEnabledChange?.(checked === true)} />
              <label htmlFor="image-refiner" className="text-[#2563EB] font-medium">
                Image Refiner
              </label>
            </div>
            <AccordionTrigger className="p-0 flex-0">
            </AccordionTrigger>
          </div>
          <AccordionContent className="pt-0 px-3 pb-3">
            <ImageRefinerSettings
              selectedRefiner={refinerModel || 'none'}
              setSelectedRefiner={onRefinerModelChange || (() => {})}
              refineSwitchAt={refinerSwitchAt || 0.8}
              setRefineSwitchAt={onRefinerSwitchAtChange || (() => {})}
            />
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="prompt-tester" className="border border-border rounded-md overflow-hidden hidden">
          <div className="flex items-center py-3 px-3">
            <div className="flex items-center flex-1">
              <Checkbox id="prompt-tester" className="mr-3" />
              <label htmlFor="prompt-tester" className="text-[#2563EB] font-medium">
                Script - Prompt Tester
              </label>
            </div>
            <AccordionTrigger className="p-0 flex-0">
            </AccordionTrigger>
          </div>
          <AccordionContent className="pt-0 px-3 pb-3">
            <PromptTesterSettings />
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="sdxl-style" className="border border-border rounded-md overflow-hidden hidden">
          <div className="flex items-center py-3 px-3">
            <div className="flex items-center flex-1">
              <Checkbox id="sdxl" className="mr-3" />
              <label htmlFor="sdxl" className="text-[#2563EB] font-medium">
                Enable SDXL Style Selector
              </label>
            </div>
            <AccordionTrigger className="p-0 flex-0">
            </AccordionTrigger>
          </div>
          <AccordionContent className="pt-0 px-3 pb-3">
            <SDXLStyleSettings />
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  );
};

export default AdvancedSettings;
