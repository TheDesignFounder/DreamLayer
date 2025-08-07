/**
 * API service for managing generation runs
 */

import { Run, RunSummary, RunsResponse, RunResponse, SaveRunResponse } from '@/types/run';

const API_BASE_URL = 'http://localhost:5000/api';

export class RunService {
  /**
   * Fetch list of generation runs
   */
  static async getRuns(limit: number = 50, offset: number = 0): Promise<RunSummary[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/runs?limit=${limit}&offset=${offset}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch runs: ${response.statusText}`);
      }

      const data: RunsResponse = await response.json();
      return data.runs || [];
    } catch (error) {
      console.error('Error fetching runs:', error);
      throw error;
    }
  }

  /**
   * Fetch a specific run by ID
   */
  static async getRun(runId: string): Promise<Run | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/runs/${runId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.status === 404) {
        return null;
      }

      if (!response.ok) {
        throw new Error(`Failed to fetch run: ${response.statusText}`);
      }

      const data: RunResponse = await response.json();
      return data.run;
    } catch (error) {
      console.error('Error fetching run:', error);
      throw error;
    }
  }

  /**
   * Save a new generation run
   */
  static async saveRun(config: Record<string, any>): Promise<string> {
    try {
      const response = await fetch(`${API_BASE_URL}/runs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      });

      if (!response.ok) {
        throw new Error(`Failed to save run: ${response.statusText}`);
      }

      const data: SaveRunResponse = await response.json();
      return data.run_id;
    } catch (error) {
      console.error('Error saving run:', error);
      throw error;
    }
  }

  /**
   * Delete a specific run
   */
  static async deleteRun(runId: string): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/runs/${runId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      return response.ok;
    } catch (error) {
      console.error('Error deleting run:', error);
      return false;
    }
  }
}
