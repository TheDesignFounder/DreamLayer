import React from 'react';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger
} from "@/components/ui/accordion";
import { useI18n } from '@/i18n/i18nContext';
import { Checkbox } from "@/components/ui/checkbox";
import ImageUploader from '@/components/ImageUploader';
import AdvancedSettings from '@/components/AdvancedSettings';
import ExternalExtensions from '@/components/ExternalExtensions';
import SubTabContent from './SubTabContent';

interface SettingsAccordionProps {
  activeSubTab: string;
  batchCount: number;
  setBatchCount: (count: number) => void;
  batchSize: number;
  setBatchSize: (size: number) => void;
}

const SettingsAccordion: React.FC<SettingsAccordionProps> = ({
  activeSubTab,
  batchCount,
  setBatchCount,
  batchSize,
  setBatchSize
}) => {
  const { t } = useI18n();

  const getSectionTitle = () => {
    switch (activeSubTab) {
      case "checkpoints":
        return t('generation.customWorkflowManagement');
      case "lora":
        return t('generation.loraBrowser');
      default:
        return t('generation.coreGenerationSettings');
    }
  };


  const getSectionNumber = () => {
    if (activeSubTab === "checkpoints" || activeSubTab === "lora") {
      return "1";
    }
    return "2";
  };

  return (
    <Accordion type="multiple" className="space-y-4">
      {activeSubTab !== "checkpoints" && activeSubTab !== "lora" && (
        <AccordionItem value="section-1" className="border border-border rounded-md overflow-hidden bg-card">
          <AccordionTrigger className="px-4 py-3 font-medium bg-card hover:bg-accent">
            <span className="flex items-center text-foreground">
              <span className="mr-2 text-foreground">1.</span>
              Image Input
            </span>
          </AccordionTrigger>
          <AccordionContent className="px-4 py-3 bg-card">
            <div className="bg-card">
              <ImageUploader />
            </div>
          </AccordionContent>
        </AccordionItem>
      )}

      <AccordionItem value="section-2" className="border border-border rounded-md overflow-hidden bg-card">
        <AccordionTrigger className="px-4 py-3 font-medium bg-card hover:bg-accent">
          <span className="flex items-center text-foreground">
            <span className="mr-2 text-foreground">{getSectionNumber()}.</span>
            {getSectionTitle()}
          </span>
        </AccordionTrigger>
        <AccordionContent className="px-4 py-3 bg-card">
          <SubTabContent
            activeSubTab={activeSubTab}
            batchCount={batchCount}
            setBatchCount={setBatchCount}
            batchSize={batchSize}
            setBatchSize={setBatchSize}
          />
        </AccordionContent>
      </AccordionItem>

      {activeSubTab !== "checkpoints" && activeSubTab !== "lora" && (
        <AccordionItem value="section-3" className="border border-border rounded-md overflow-hidden bg-card">
          <AccordionTrigger className="px-4 py-3 font-medium bg-card hover:bg-accent">
            <span className="flex items-center text-foreground">
              <span className="mr-2 text-foreground">3.</span>
              Advanced Optional Settings
            </span>
          </AccordionTrigger>
          <AccordionContent className="px-4 py-3 bg-card">
            <AdvancedSettings />
          </AccordionContent>
        </AccordionItem>
      )}

      {activeSubTab !== "checkpoints" && activeSubTab !== "lora" && (
        <AccordionItem value="section-4" className="border border-border rounded-md overflow-hidden bg-card">
          <AccordionTrigger className="px-4 py-3 font-medium bg-card hover:bg-accent">
            <span className="flex items-center text-foreground">
              <span className="mr-2 text-foreground">4.</span>
              External Extensions & Add-ons
            </span>
          </AccordionTrigger>
          <AccordionContent className="px-4 py-3 bg-card">
            <ExternalExtensions />
          </AccordionContent>
        </AccordionItem>
      )}
    </Accordion>
  );
};

export default SettingsAccordion;
