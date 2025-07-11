import React from 'react';
import PikaFrameGeneratorSimple from '@/components/PikaFrameGeneratorSimple';

interface PikaPageProps {
  onTabChange: (tabId: string) => void;
}

const PikaPage: React.FC<PikaPageProps> = ({ onTabChange }) => {
  return (
    <div className="container mx-auto p-4">
      <PikaFrameGeneratorSimple />
    </div>
  );
};

export default PikaPage;