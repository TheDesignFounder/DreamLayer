
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";
import { useAppHotkeys } from "@/hooks/useHotkeys";
import { useSaveSettings } from "@/hooks/useSaveSettings";

const queryClient = new QueryClient();

const AppWithHotkeys = () => {
  const { saveSettings } = useSaveSettings();
  
  // Register global hotkeys
  useAppHotkeys({
    onGenerate: () => {
      // Trigger generation based on current active tab
      const event = new CustomEvent('hotkey:generate');
      window.dispatchEvent(event);
    },
    onSaveSettings: () => {
      // Trigger save settings
      const event = new CustomEvent('hotkey:saveSettings');
      window.dispatchEvent(event);
      saveSettings();
    }
  });

  return (
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  );
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AppWithHotkeys />
  </QueryClientProvider>
);

export default App;
