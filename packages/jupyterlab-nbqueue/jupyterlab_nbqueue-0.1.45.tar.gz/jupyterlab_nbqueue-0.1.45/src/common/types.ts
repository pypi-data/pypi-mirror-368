/**
 * Job submission interfaces for API validation
 */

/** File metadata for notebook submissions */
export interface NotebookFile {
  /** Name of the notebook file */
  name: string;
  /** Full path to the notebook file */
  path: string;
}

/** Job submission request payload */
export interface JobSubmissionRequest {
  /** Notebook file metadata */
  notebook_file: NotebookFile;
  /** Container image to use for the job */
  image: string;
  /** Conda environment specification */
  conda_env: string;
  /** Output path for job results */
  output_path: string;
  /** CPU allocation for the job */
  cpu: string | number;
  /** Memory/RAM allocation for the job */
  ram: string | number;
}

/** Job submission response from the API */
export interface JobSubmissionResponse {
  /** Whether the job submission was successful */
  success: boolean;
  /** Unique identifier for the created job */
  job_id: string;
  /** Output from kubectl command */
  kubectl_output: string;
  /** Error message if submission failed */
  error_message?: string;
  /** Additional message field for compatibility */
  message?: string;
  /** Index signature for compatibility with ReadonlyJSONObject */
  [key: string]: any;
}

/**
 * Workflow management interfaces
 */

/** Individual workflow item */
export interface WorkflowItem {
  /** Name/key of the workflow */
  name: string;
  /** Current status of the workflow */
  status: string;
}

/** Response from workflows list endpoint */
export type WorkflowsResponse = WorkflowItem[];

/** Generic API error response */
export interface ApiErrorResponse {
  /** Error message describing what went wrong */
  error: string;
}

/**
 * Existing monitoring/logging interfaces
 */

export interface Summary {
  id: string;
  podName: string;
  usage: number;
  cost: number;
  project: string;
  lastUpdate: string;
  year: number;
  month: number;
  user_efs_cost: number;
  user_efs_gb: number;
  project_efs_cost: number;
  project_efs_gb: number;
}

export interface Detail {
  id: string;
  podName: string;
  creationTimestamp: string;
  deletionTimestamp: string;
  cpuLimit: string;
  memoryLimit: string;
  gpuLimit: string;
  volumes: string;
  namespace: string;
  notebook_duration: string;
  session_cost: number;
  instance_id: string;
  instance_type: string;
  region: string;
  pricing_type: string;
  cost: string;
  instanceRAM: number;
  instanceCPU: number;
  instanceGPU: number;
  instanceId: string;
}

export interface Logs {
  summary: Summary[];
  details: Detail[];
}

/**
 * Validation utilities for API requests
 */

/** Validates that a NotebookFile has the required fields */
export function validateNotebookFile(file: any): file is NotebookFile {
  return file && 
         typeof file.name === 'string' && 
         typeof file.path === 'string' &&
         file.name.endsWith('.ipynb');
}

/** Validates that a JobSubmissionRequest has all required fields */
export function validateJobSubmissionRequest(request: any): request is JobSubmissionRequest {
  if (!request) return false;
  
  const requiredFields = ['notebook_file', 'output_path', 'cpu', 'ram'];
  for (const field of requiredFields) {
    if (!request[field]) return false;
  }
  
  // Validate notebook_file structure
  if (!validateNotebookFile(request.notebook_file)) return false;
  
  // Validate CPU is a valid number
  const cpu = parseFloat(String(request.cpu));
  if (isNaN(cpu) || cpu <= 0) return false;
  
  // Validate RAM format (number optionally followed by unit)
  const ramPattern = /^\d+(\.\d+)?(Gi|G|Mi|M)?$/;
  if (!ramPattern.test(String(request.ram).trim())) return false;
  
  return true;
}

/** Type guard to check if response is a successful job submission */
export function isJobSubmissionSuccess(response: any): response is JobSubmissionResponse {
  return response && 
         typeof response.success === 'boolean' &&
         typeof response.job_id === 'string' &&
         typeof response.kubectl_output === 'string';
}
