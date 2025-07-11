
import { ThemeToggle } from "./ThemeToggle";
import KeyboardShortcutsHelp from './KeyboardShortcutsHelp';

const NavBar = () => {
  return (
    <div className="flex items-center justify-between border-b border-border bg-background px-4 py-2">
      <h1 className="text-lg font-medium text-primary">DreamLayer AI</h1>
      <div className="flex items-center space-x-2">
        <KeyboardShortcutsHelp />
        <ThemeToggle />
      </div>
    </div>
  );
};

export default NavBar;
