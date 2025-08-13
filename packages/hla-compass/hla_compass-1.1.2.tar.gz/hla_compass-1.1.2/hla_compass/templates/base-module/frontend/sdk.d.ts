/**
 * HLA-Compass SDK Type Definitions
 * This is a local mock SDK for frontend development
 * In production, modules are loaded within the platform which provides these interfaces
 */

declare module '@hla-compass/sdk' {
  // Execution status type
  export type ExecutionStatus = 'idle' | 'running' | 'completed' | 'failed';

  // Module error interface
  export interface ModuleError {
    code: string;
    message: string;
    details?: any;
  }

  // Module result wrapper
  export interface ModuleResult<T = any> {
    status: 'success' | 'error';
    data?: T;
    error?: ModuleError;
    metadata?: {
      executionTime: number;
      timestamp: string;
      version: string;
    };
  }

  // Module props interface
  export interface ModuleProps<TInput = any, TOutput = any> {
    // Input data for the module
    input: TInput;
    
    // Callback when input changes
    onInputChange: (input: TInput) => void;
    
    // Execute the module
    onExecute: () => void;
    
    // Current execution status
    executionStatus: ExecutionStatus;
    
    // Result data (when completed)
    result?: TOutput;
    
    // Error information (if failed)
    error?: ModuleError;
    
    // API client for backend calls
    api?: ModuleAPI;
    
    // Shared data from other modules
    sharedData?: Record<string, any>;
    
    // Module configuration
    config?: Record<string, any>;
  }

  // API client interface
  export interface ModuleAPI {
    // Execute backend module
    execute: (input: any) => Promise<ModuleResult>;
    
    // Get module status
    getStatus: (jobId: string) => Promise<ExecutionStatus>;
    
    // Cancel execution
    cancel: (jobId: string) => Promise<void>;
    
    // Download results
    downloadResults: (jobId: string, format: 'json' | 'csv') => Promise<Blob>;
  }

  // Data access interfaces
  export interface PeptideData {
    search: (params: {
      sequence?: string;
      min_length?: number;
      max_length?: number;
      hla_allele?: string;
      limit?: number;
    }) => Promise<Peptide[]>;
    
    get: (id: string) => Promise<Peptide | null>;
  }

  export interface Peptide {
    id: string;
    sequence: string;
    length: number;
    mass: number;
    hla_alleles?: string[];
    protein_id?: string;
    samples?: string[];
  }

  export interface ProteinData {
    search: (params: {
      gene_name?: string;
      organism?: string;
      uniprot_id?: string;
      limit?: number;
    }) => Promise<Protein[]>;
    
    get: (id: string) => Promise<Protein | null>;
  }

  export interface Protein {
    id: string;
    gene_name: string;
    uniprot_id: string;
    organism: string;
    sequence: string;
    length: number;
  }

  export interface SampleData {
    search: (params: {
      tissue_type?: string;
      disease?: string;
      patient_id?: string;
      limit?: number;
    }) => Promise<Sample[]>;
    
    get: (id: string) => Promise<Sample | null>;
  }

  export interface Sample {
    id: string;
    sample_type: string;
    tissue_type?: string;
    disease?: string;
    patient_id?: string;
    collection_date?: string;
  }

  // Storage interface
  export interface Storage {
    save: (filename: string, data: any) => Promise<string>;
    read: (filename: string) => Promise<any>;
    exists: (filename: string) => Promise<boolean>;
    delete: (filename: string) => Promise<void>;
  }

  // Module context
  export interface ModuleContext {
    jobId: string;
    userId: string;
    organizationId: string;
    executionTime: number;
    api: ModuleAPI;
    peptides: PeptideData;
    proteins: ProteinData;
    samples: SampleData;
    storage: Storage;
  }
}