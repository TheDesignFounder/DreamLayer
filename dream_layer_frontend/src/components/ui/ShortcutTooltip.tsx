import React, { useState, useRef, useEffect } from 'react';

interface ShortcutTooltipProps {
  content: string;
  children: React.ReactElement;
  delay?: number;
}

export const ShortcutTooltip: React.FC<ShortcutTooltipProps> = ({
  content,
  children,
  delay = 100,
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout>();

  const showTooltip = () => {
    timeoutRef.current = setTimeout(() => {
      setIsVisible(true);
    }, delay);
  };

  const hideTooltip = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    setIsVisible(false);
  };

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return (
    <div
      className="relative inline-block"
      onMouseEnter={showTooltip}
      onMouseLeave={hideTooltip}
    >
      {children}
      {isVisible && (
        <div
          className="absolute z-[9999] px-3 py-2 text-sm font-medium text-white bg-gray-800 rounded-lg shadow-lg border border-gray-700 whitespace-nowrap"
          style={{
            left: '50%',
            top: '-45px',
            transform: 'translateX(-50%)',
            pointerEvents: 'none'
          }}
        >
          {content}
          <div
            className="absolute w-3 h-3 bg-gray-800 transform rotate-45 left-1/2 -translate-x-1/2 top-full border-r border-b border-gray-700"
            style={{ marginTop: '-1px' }}
          ></div>
        </div>
      )}
    </div>
  );
};

export default ShortcutTooltip;
