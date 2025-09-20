import React, { useRef } from "react";

interface PopupBoxProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
}

const PopupBox: React.FC<PopupBoxProps> = ({
  isOpen,
  onClose,
  title,
  children,
}) => {
  const dialogRef = useRef<HTMLDivElement>(null);

  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (dialogRef.current && !dialogRef.current.contains(e.target as Node)) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
      role="dialog"
      aria-modal="true"
      onClick={handleOverlayClick}
    >
      <div
        ref={dialogRef}
        className="flex flex-col flex-nowrap bg-white dark:bg-[#0F172A] text-foreground dark:text-white rounded-lg shadow-lg p-6"
        onClick={(e) => e.stopPropagation()}
      >
        {title && (
          <h2 className="text-lg font-semibold text-center mb-4">
            {title}
          </h2>
        )}
        <div>{children}</div>
      </div>
    </div>
  );
};

export default PopupBox;
