/**
 * Shared API utilities for the application
 */

export const fetcher = async (url: string) => {
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status} - ${response.statusText}`);
  }
  
  return response.json();
};

/**
 * API base URL - can be configured based on environment
 */
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

/**
 * Helper function to build full API URLs
 */
export const buildApiUrl = (endpoint: string): string => {
  return `${API_BASE_URL}${endpoint}`;
}; 