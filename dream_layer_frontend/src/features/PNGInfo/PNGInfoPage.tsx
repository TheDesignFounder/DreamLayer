
import React from 'react';
import Accordion from '@/components/Accordion';
import { useI18n } from '@/i18n/i18nContext';

const PNGInfoPage = () => {
  const { t } = useI18n();

  return (
    <div className="flex justify-center">
      <div className="w-full max-w-4xl">
        {/* Centered Content */}
        <div className="space-y-4">
          <div className="flex flex-col">
            <div className="mb-3 flex items-center justify-between">
              <h3 className="text-base font-medium">{t('pnginfo.pngInfoExtraction')}</h3>
              <button className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90">
                {t('pnginfo.extractInfo')}
              </button>
            </div>

            <Accordion title={t('pnginfo.imageUpload')} number="1" defaultOpen={true}>
              <div className="mb-4 p-4 border-2 border-dashed border-border rounded-md text-center">
                <p className="text-muted-foreground mb-2">{t('pnginfo.dragDropPng')}</p>
                <p className="text-xs text-muted-foreground mb-4">{t('pnginfo.onlyPngWithData')}</p>
                <button className="rounded-md bg-secondary px-4 py-2 text-sm font-medium text-secondary-foreground">
                  {t('pnginfo.browseFiles')}
                </button>
              </div>
            </Accordion>

            <Accordion title={t('pnginfo.extractedInfo')} number="2" defaultOpen={true}>
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium mb-1">{t('pnginfo.prompt')}</h4>
                  <div className="rounded-md bg-muted p-3 text-sm min-h-[100px] whitespace-pre-wrap">
                    <p className="text-muted-foreground italic">{t('pnginfo.promptInfoWillAppear')}</p>
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-medium mb-1">{t('pnginfo.negativePrompt')}</h4>
                  <div className="rounded-md bg-muted p-3 text-sm min-h-[80px] whitespace-pre-wrap">
                    <p className="text-muted-foreground italic">{t('pnginfo.negativePromptInfoWillAppear')}</p>
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-medium mb-1">{t('pnginfo.generationSettings')}</h4>
                  <div className="rounded-md bg-muted p-3 text-sm">
                    <p className="text-muted-foreground italic">{t('pnginfo.settingsInfoWillAppear')}</p>
                  </div>
                </div>
              </div>

              <div className="mt-4 flex gap-2">
                <button className="rounded-md border border-input bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground">
                  {t('pnginfo.copyToClipboard')}
                </button>
                <button className="rounded-md border border-input bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground">
                  {t('pnginfo.sendToTxt2Img')}
                </button>
                <button className="rounded-md border border-input bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground">
                  {t('pnginfo.sendToImg2Img')}
                </button>
              </div>
            </Accordion>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PNGInfoPage;
