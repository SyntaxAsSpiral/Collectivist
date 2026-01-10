export interface Collection {
  id: string
  name: string
  path: string
  collection_type: string
  categories: string[]
  last_scan?: string
  status: 'idle' | 'analyzing' | 'running' | 'error'
}

export interface PipelineRun {
  run_id: string
  status: 'queued' | 'running' | 'completed' | 'failed'
  collection_id: string
  started_at: string
  completed_at?: string
  error?: string
}

export interface PipelineRunRequest {
  skip_analyze?: boolean
  skip_scan?: boolean
  skip_describe?: boolean
  skip_readme?: boolean
  skip_process_new?: boolean
  auto_file?: boolean
  confidence_threshold?: number
  workflow_mode?: 'manual' | 'scheduled' | 'organic'
}

export interface LLMConfig {
  provider: string
  api_key?: string
  base_url?: string
  model?: string
  temperature?: number
  max_tokens?: number
}

export interface LLMProvider {
  name: string
  base_url: string
  models: string[]
  requires_api_key: boolean
  description: string
}

export interface ScheduleConfig {
  enabled: boolean
  interval_days: number
  operations: string[]
  auto_file: boolean
  confidence_threshold: number
}

export interface PipelineEvent {
  stage: string
  current_item?: string
  progress_current: number
  progress_total: number
  percent: number
  message: string
  level: 'info' | 'warn' | 'error' | 'success'
  timestamp: string
}