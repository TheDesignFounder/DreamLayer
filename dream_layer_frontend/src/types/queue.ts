/**
 * Types for queue-related data structures
 */

export interface QueueItem {
  id: string;
  prompt: Record<string, any>;
  number: number;
  prompt_id: string;
  extra_data?: Record<string, any>;
  outputs_to_execute?: string[];
}

export interface TaskProgress {
  prompt_id: string;
  current_step: number;
  total_steps: number;
  step_name?: string;
  percent: number;
}

export interface ProgressData {
  percent: number;
  status: 'pending' | 'running' | 'complete' | 'idle';
  queue_running: QueueItem[];
  queue_pending: QueueItem[];
  task_details: TaskProgress[];
} 