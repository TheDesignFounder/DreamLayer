
import {
  FileText,
  ImageIcon,
  Settings,
  GalleryHorizontal,
  HardDrive
} from "lucide-react";
import { useI18n } from "@/i18n/i18nContext";

const TabsNav = ({ activeTab, onTabChange }: TabsNavProps) => {
  const { t } = useI18n();

  const tabs = [
    { id: "txt2img", label: t('nav.txt2img'), icon: FileText },
    { id: "img2img", label: t('nav.img2img'), icon: ImageIcon },
    { id: "extras", label: t('nav.extras'), icon: GalleryHorizontal },
    { id: "models", label: t('nav.models'), icon: HardDrive },
    { id: "pnginfo", label: t('nav.pnginfo'), icon: FileText },
    { id: "configurations", label: t('nav.configurations'), icon: Settings }
  ];

interface TabsNavProps {
  activeTab: string;
  onTabChange: (tabId: string) => void;
}

  return (
    <div className="mb-6 overflow-x-auto border-b border-border">
      <div className="flex min-w-max px-2">
        {tabs.filter(tab => tab.id !== 'pnginfo').map((tab) => (
          <button
            key={tab.id}
            className={`relative py-3 px-5 text-sm font-medium transition-colors hover:text-foreground flex items-center gap-2 ${
              tab.id === activeTab
                ? "text-primary border-b-2 border-primary"
                : "text-muted-foreground"
            }`}
            onClick={() => onTabChange(tab.id)}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>
    </div>
  );
};

export default TabsNav;
