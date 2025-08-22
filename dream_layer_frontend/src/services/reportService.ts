export interface BatchReportRequest {
  images: ImageReportData[];
  config: GenerationConfig;
  report_name?: string;
}

export interface ImageReportData {
  id: string;
  filename: string;
  url: string;
  prompt: string;
  negativePrompt?: string;
  timestamp: number;
  settings: GenerationSettings;
}

export interface GenerationSettings {
  model: string;
  sampler: string;
  steps: number;
  cfg_scale: number;
  seed: number;
  width: number;
  height: number;
  [key: string]: any;
}

export interface GenerationConfig {
  session_id?: string;
  generation_date?: string;
  total_images?: number;
  [key: string]: any;
}

export interface BatchReportResponse {
  status: string;
  message?: string;
  download_url?: string;
}

const EXTRAS_API_BASE_URL = import.meta.env.VITE_EXTRAS_API_BASE_URL || 'http://localhost:5003';

export const generateBatchReport = async (
  images: ImageReportData[],
  config: GenerationConfig,
  reportName?: string
): Promise<Blob> => {
  try {
    console.log('🔄 Generating batch report with', images.length, 'images');
    
    const requestData: BatchReportRequest = {
      images,
      config,
      report_name: reportName
    };
    
    const response = await fetch(`${EXTRAS_API_BASE_URL}/api/batch-report/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: 'Unknown error' }));
      throw new Error(errorData.message || `Failed to generate report: ${response.statusText}`);
    }
    
    // The response should be a blob (ZIP file)
    const blob = await response.blob();
    console.log('✅ Batch report generated successfully, size:', blob.size, 'bytes');
    
    return blob;
  } catch (error) {
    console.error('❌ Error generating batch report:', error);
    throw error;
  }
};

export const downloadBatchReport = (blob: Blob, filename?: string) => {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename || `report_${new Date().toISOString().split('T')[0]}.zip`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
  console.log('📥 Batch report downloaded');
};