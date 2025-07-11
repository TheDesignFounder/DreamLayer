
import { 
  FileText, 
  ImageIcon, 
  Settings, 
  GalleryHorizontal,
  History
} from "lucide-react";

const tabs = [
  { id: "txt2img", label: "Txt2Img", icon: FileText },
  { id: "img2img", label: "Img2Img", icon: ImageIcon },
  { id: "extras", label: "Extras", icon: GalleryHorizontal },
  { id: "history", label: "History", icon: History },
  { id: "pnginfo", label: "PNG Info", icon: FileText },
  { id: "configurations", label: "Configurations", icon: Settings }
];

interface TabsNavProps {
  activeTab: string;
  onTabChange: (tabId: string) => void;
}

const TabsNav = ({ activeTab, onTabChange }: TabsNavProps) => {
  return (
    <div className="mb-6 overflow-x-auto border-b border-border glass-morphism rounded-t-lg">
      <div className="flex min-w-max px-2">
        {tabs.filter(tab => tab.id !== 'pnginfo').map((tab) => (
          <button
            key={tab.id}
            className={`relative py-3 px-5 text-sm font-medium transition-all duration-300 hover:text-foreground flex items-center gap-2 rounded-t-lg hover:bg-primary/10 hover:scale-105 ${
              tab.id === activeTab
                ? "text-primary border-b-2 border-primary bg-primary/5"
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
