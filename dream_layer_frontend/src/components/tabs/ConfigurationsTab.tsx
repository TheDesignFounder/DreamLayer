
import React from 'react';
import Accordion from '@/components/Accordion';
import Slider from '@/components/Slider';
import { useI18n } from '@/i18n/i18nContext';

const ConfigurationsTab = () => {
  const { t } = useI18n();

  return (
    <div className="mb-4">
      <div className="flex flex-col">
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-base font-medium">{t('configurations.systemConfigurations')}</h3>
          <button className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90">
            {t('configurations.saveSettings')}
          </button>
        </div>

        <Accordion title={t('configurations.uiSettings')} number="1" defaultOpen={true}>
          <div className="mb-4">
            <label htmlFor="uiTheme" className="mb-1 block text-sm font-medium">{t('configurations.uiTheme')}</label>
            <select id="uiTheme" className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
              <option value="system">{t('configurations.systemDefault')}</option>
              <option value="light">{t('configurations.lightMode')}</option>
              <option value="dark">{t('configurations.darkMode')}</option>
            </select>
          </div>

          <div className="mb-4">
            <label htmlFor="language" className="mb-1 block text-sm font-medium">{t('configurations.language')}</label>
            <select id="language" className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
              <option value="en">English</option>
              <option value="jp">日本語</option>
              <option value="de">Deutsch</option>
              <option value="fr">Français</option>
              <option value="es">Español</option>
            </select>
          </div>

          <div className="flex items-center mb-4">
            <input type="checkbox" id="quicksettings" className="mr-2" checked />
            <label htmlFor="quicksettings" className="text-sm">{t('configurations.showQuickSettings')}</label>
          </div>

          <div className="flex items-center mb-4">
            <input type="checkbox" id="progressInTitle" className="mr-2" checked />
            <label htmlFor="progressInTitle" className="text-sm">{t('configurations.showProgressInTitle')}</label>
          </div>
        </Accordion>

        <Accordion title={t('configurations.performanceAndResources')} number="2" defaultOpen={true}>
          <div className="mb-4">
            <label htmlFor="computeDevice" className="mb-1 block text-sm font-medium">{t('configurations.primaryComputeDevice')}</label>
            <select id="computeDevice" className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
              <option value="cuda">{t('configurations.nvidiaGpuCuda')}</option>
              <option value="rocm">{t('configurations.amdGpuRocm')}</option>
              <option value="mps">{t('configurations.appleSiliconMps')}</option>
              <option value="cpu">{t('configurations.cpu')}</option>
            </select>
          </div>

          <Slider
            min={0}
            max={100}
            defaultValue={85}
            label={t('configurations.vramUsageTarget')}
            sublabel={t('configurations.lowerToReduceMemory')}
          />

          <Slider
            min={1}
            max={16}
            defaultValue={2}
            label={t('configurations.parallelProcessing')}
            sublabel={t('configurations.higherValuesUseMoreGpu')}
          />

          <div className="flex items-center mb-4">
            <input type="checkbox" id="xformers" className="mr-2" checked />
            <label htmlFor="xformers" className="text-sm">{t('configurations.useXformers')}</label>
          </div>

          <div className="flex items-center mb-4">
            <input type="checkbox" id="medvram" className="mr-2" />
            <label htmlFor="medvram" className="text-sm">{t('configurations.optimizeForMediumLowVram')}</label>
          </div>
        </Accordion>

        <Accordion title={t('configurations.pathsAndSaving')} number="3">
          <div className="mb-4">
            <label htmlFor="outputDir" className="mb-1 block text-sm font-medium">{t('configurations.outputDirectoryLabel')}</label>
            <div className="flex">
              <input
                id="outputDir"
                type="text"
                className="flex-1 rounded-l-md border border-input bg-background px-3 py-2 text-sm"
                placeholder="/path/to/outputs"
              />
              <button className="rounded-r-md bg-secondary px-4 py-2 text-sm font-medium text-secondary-foreground">
                {t('configurations.browse')}
              </button>
            </div>
          </div>

          <div className="mb-4">
            <label htmlFor="modelsDir" className="mb-1 block text-sm font-medium">{t('configurations.modelsDirectoryLabel')}</label>
            <div className="flex">
              <input
                id="modelsDir"
                type="text"
                className="flex-1 rounded-l-md border border-input bg-background px-3 py-2 text-sm"
                placeholder="/path/to/models"
              />
              <button className="rounded-r-md bg-secondary px-4 py-2 text-sm font-medium text-secondary-foreground">
                {t('configurations.browse')}
              </button>
            </div>
          </div>

          <div className="mb-4">
            <label htmlFor="filenameFormat" className="mb-1 block text-sm font-medium">{t('configurations.filenameFormat')}</label>
            <input
              id="filenameFormat"
              type="text"
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              placeholder={t('configurations.filenameFormatPlaceholder')}
            />
            <p className="text-xs text-muted-foreground mt-1">
              {t('configurations.filenameVariables')}
            </p>
          </div>

          <div className="flex items-center mb-4">
            <input type="checkbox" id="saveMetadata" className="mr-2" checked />
            <label htmlFor="saveMetadata" className="text-sm">{t('configurations.saveGenerationParameters')}</label>
          </div>
        </Accordion>

        <Accordion title={t('configurations.updatesAndInstallation')} number="4">
          <div className="flex items-center justify-between mb-4 p-4 bg-muted rounded-md">
            <div>
              <p className="font-medium">{t('configurations.currentVersion')}</p>
              <p className="text-xs text-muted-foreground">{t('configurations.lastChecked')}</p>
            </div>
            <button className="rounded-md border border-input bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground">
              {t('configurations.checkForUpdates')}
            </button>
          </div>

          <div className="mb-4">
            <label htmlFor="updateChannel" className="mb-1 block text-sm font-medium">Update Channel:</label>
            <select id="updateChannel" className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
              <option value="stable">Stable</option>
              <option value="beta">Beta</option>
              <option value="nightly">Nightly (Experimental)</option>
            </select>
          </div>

          <div className="flex items-center mb-4">
            <input type="checkbox" id="autoUpdate" className="mr-2" />
            <label htmlFor="autoUpdate" className="text-sm">{t('configurations.enableAutomaticUpdates')}</label>
          </div>
        </Accordion>
      </div>
    </div>
  );
};

export default ConfigurationsTab;
