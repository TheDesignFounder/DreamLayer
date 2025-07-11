
import { Link, useLocation } from "react-router-dom";
import { ThemeToggle } from "./ThemeToggle";
import { Button } from "./ui/button";
import { Network } from "lucide-react";

const NavBar = () => {
  const location = useLocation();

  return (
    <div className="flex items-center justify-between border-b border-border bg-background px-4 py-2">
      <div className="flex items-center space-x-4">
        <Link to="/" className="text-lg font-medium text-primary hover:text-primary/80">
          DreamLayer AI
        </Link>
        <nav className="flex items-center space-x-2">
          <Button
            variant={location.pathname === "/graph" ? "default" : "ghost"}
            size="sm"
            asChild
          >
            <Link to="/graph" className="flex items-center space-x-1">
              <Network className="h-4 w-4" />
              <span>Graph Viewer</span>
            </Link>
          </Button>
        </nav>
      </div>
      <ThemeToggle />
    </div>
  );
};

export default NavBar;
