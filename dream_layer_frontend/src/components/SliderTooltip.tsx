import React from 'react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { HelpCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface SliderTooltipProps {
  content: {
    title: string;
    description: string;
    tips?: string[];
    bestPractices?: string;
  };
  side?: 'top' | 'right' | 'bottom' | 'left';
  className?: string;
}

export const SliderTooltip: React.FC<SliderTooltipProps> = ({
  content,
  side = 'top',
  className
}) => {
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <HelpCircle 
            className={cn("h-4 w-4 text-blue-500 cursor-help hover:text-blue-600 transition-colors", className)}
          />
        </TooltipTrigger>
        <TooltipContent side={side} className="max-w-80 p-4">
          <div className="space-y-3">
            <div className="font-semibold text-blue-600 dark:text-blue-400">{content.title}</div>
            <div className="text-sm text-gray-700 dark:text-gray-300">{content.description}</div>
            
            {content.tips && content.tips.length > 0 && (
              <div>
                <div className="font-medium text-green-600 dark:text-green-400 mb-2">Tips:</div>
                <ul className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
                  {content.tips.map((tip, index) => (
                    <li key={index} className="flex items-start">
                      <span className="text-green-500 mr-2 flex-shrink-0">•</span>
                      <span>{tip}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {content.bestPractices && (
              <div className="border-t border-gray-200 dark:border-gray-600 pt-2 mt-2">
                <div className="font-medium text-yellow-600 dark:text-yellow-400 mb-1">Best Practice:</div>
                <div className="text-xs text-gray-600 dark:text-gray-400">{content.bestPractices}</div>
              </div>
            )}
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};