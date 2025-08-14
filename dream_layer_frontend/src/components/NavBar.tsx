
import { ThemeToggle } from "./ThemeToggle";
import LanguageSelector from "./LanguageSelector";
import { useI18n } from "@/i18n/i18nContext";

const NavBar = () => {
  const { t } = useI18n();

  return (
    <div className="flex items-center justify-between border-b border-border bg-background px-4 py-2">
      <h1 className="text-lg font-medium text-primary">{t('nav.dreamLayerAI')}</h1>
      <div className="flex items-center gap-2">
        <LanguageSelector />
        <ThemeToggle />
      </div>
    </div>
  );
};

export default NavBar;
