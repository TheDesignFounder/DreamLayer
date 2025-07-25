
import {
  FileText,
  ImageIcon,
  Settings,
  GalleryHorizontal,
  HardDrive
} from "lucide-react";

const tabs = [
  { id: "txt2img", label: "Txt2Img", icon: FileText },
  { id: "img2img", label: "Img2Img", icon: ImageIcon },
  { id: "extras", label: "Extras", icon: GalleryHorizontal },
  { id: "models", label: "Models", icon: HardDrive },
  { id: "pnginfo", label: "PNG Info", icon: FileText },
  { id: "configurations", label: "Configurations", icon: Settings }
];

interface TabsNavProps {
  activeTab: string;
  onTabChange: (tabId: string) => void;
}

const TabsNav = ({ activeTab, onTabChange }: TabsNavProps) => {
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
