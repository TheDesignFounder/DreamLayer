export interface ReportBundleRequest {
  run_ids?: string[];  // Empty array means all runs
}

export interface ReportBundleResponse {
  status: 'success' | 'error';
  message?: string;
  file_path?: string;
}

export interface ReportBundleValidationRequest {
  csv_content: string;
}

export interface ReportBundleValidationResponse {
  status: 'success' | 'error';
  valid: boolean;
  message?: string;
}

export interface ReportBundleState {
  generating: boolean;
  error: string | null;
  downloadUrl: string | null;
}

export interface ReportBundleActions {
  generateReport: (runIds?: string[]) => Promise<void>;
  downloadReport: () => Promise<void>;
  validateSchema: (csvContent: string) => Promise<boolean>;
  clearError: () => void;
} 