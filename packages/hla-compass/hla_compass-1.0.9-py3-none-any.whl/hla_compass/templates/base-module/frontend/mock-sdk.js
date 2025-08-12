/**
 * Mock HLA-Compass SDK for local development
 * This provides a runtime implementation for testing
 */

// Execution status enum
export const ExecutionStatus = {
  Idle: 'idle',
  Running: 'running',
  Completed: 'completed',
  Failed: 'failed'
};

// Mock API implementation
export class ModuleAPI {
  async execute(input) {
    console.log('Mock API: Executing with input:', input);
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Return mock result
    return {
      status: 'success',
      data: {
        results: [
          { id: '1', output: 'Mock result 1', score: 0.95 },
          { id: '2', output: 'Mock result 2', score: 0.87 },
          { id: '3', output: 'Mock result 3', score: 0.92 }
        ],
        summary: {
          total_results: 3,
          statistics: {
            average_score: 0.91
          }
        }
      },
      metadata: {
        executionTime: 1234,
        timestamp: new Date().toISOString(),
        version: '1.0.0'
      }
    };
  }

  async getStatus(jobId) {
    console.log('Mock API: Getting status for job:', jobId);
    return ExecutionStatus.Completed;
  }

  async cancel(jobId) {
    console.log('Mock API: Cancelling job:', jobId);
  }

  async downloadResults(jobId, format) {
    console.log('Mock API: Downloading results for job:', jobId, 'in format:', format);
    const mockData = format === 'json' 
      ? JSON.stringify({ mock: 'data' })
      : 'id,output,score\n1,Mock result 1,0.95';
    return new Blob([mockData], { type: format === 'json' ? 'application/json' : 'text/csv' });
  }
}

// Mock data access classes
export class PeptideData {
  async search(params) {
    console.log('Mock PeptideData: Searching with params:', params);
    return [
      {
        id: 'PEP001',
        sequence: 'SIINFEKL',
        length: 8,
        mass: 963.5,
        hla_alleles: ['HLA-A*02:01'],
        protein_id: 'PROT001',
        samples: ['SAMPLE001', 'SAMPLE002']
      },
      {
        id: 'PEP002',
        sequence: 'GILGFVFTL',
        length: 9,
        mass: 978.6,
        hla_alleles: ['HLA-A*02:01'],
        protein_id: 'PROT002',
        samples: ['SAMPLE001']
      }
    ];
  }

  async get(id) {
    console.log('Mock PeptideData: Getting peptide:', id);
    return {
      id: id,
      sequence: 'SIINFEKL',
      length: 8,
      mass: 963.5,
      hla_alleles: ['HLA-A*02:01'],
      protein_id: 'PROT001',
      samples: ['SAMPLE001']
    };
  }
}

export class ProteinData {
  async search(params) {
    console.log('Mock ProteinData: Searching with params:', params);
    return [
      {
        id: 'PROT001',
        gene_name: 'OVA',
        uniprot_id: 'P01012',
        organism: 'Gallus gallus',
        sequence: 'MGSIGAASMEFCFDVFKELKVHHANENIFYCPIAIMSALAMVYLGAKDSTRTQINKVVRFDKLPGFGDSIEAQCGTSVNVHSSLRDILNQITKPNDVYSFSLASRLYAEERYPILPEYLQCVKELYRGGLEPINFQTAADQARELINSWVESQTNGIIRNVLQPSSVDSQTAMVLVNAIVFKGLWEKAFKDEDTQAMPFRVTEQESKPVQMMYQIGLFRVASMASEKMKILELPFASGTMSMLVLLPDEVSGLEQLESIINFEKLTEWTSSNVMEERKIKVYLPRMKMEEKYNLTSVLMALGMTDLFIPSANLTGISSAESLKISQAVHAAHAEINEAGREVVGSAEAGVDAASVSEEFRADHPFLFCIKHIATNAVLFFGRCVSP',
        length: 385
      }
    ];
  }

  async get(id) {
    console.log('Mock ProteinData: Getting protein:', id);
    return {
      id: id,
      gene_name: 'OVA',
      uniprot_id: 'P01012',
      organism: 'Gallus gallus',
      sequence: 'MGSIGAASMEF...',
      length: 385
    };
  }
}

export class SampleData {
  async search(params) {
    console.log('Mock SampleData: Searching with params:', params);
    return [
      {
        id: 'SAMPLE001',
        sample_type: 'tumor',
        tissue_type: 'lung',
        disease: 'NSCLC',
        patient_id: 'PT001',
        collection_date: '2024-01-15'
      }
    ];
  }

  async get(id) {
    console.log('Mock SampleData: Getting sample:', id);
    return {
      id: id,
      sample_type: 'tumor',
      tissue_type: 'lung',
      disease: 'NSCLC',
      patient_id: 'PT001',
      collection_date: '2024-01-15'
    };
  }
}

export class Storage {
  async save(filename, data) {
    console.log('Mock Storage: Saving file:', filename, 'with data:', data);
    return `http://localhost:9000/mock-bucket/${filename}`;
  }

  async read(filename) {
    console.log('Mock Storage: Reading file:', filename);
    return { mock: 'data' };
  }

  async exists(filename) {
    console.log('Mock Storage: Checking file existence:', filename);
    return true;
  }

  async delete(filename) {
    console.log('Mock Storage: Deleting file:', filename);
  }
}

// Mock module context
export const ModuleContext = {
  jobId: 'mock-job-123',
  userId: 'user-456',
  organizationId: 'org-789',
  executionTime: 0,
  api: new ModuleAPI(),
  peptides: new PeptideData(),
  proteins: new ProteinData(),
  samples: new SampleData(),
  storage: new Storage()
};

// Export as window global for webpack externals
if (typeof window !== 'undefined') {
  window.HLACompassSDK = {
    ExecutionStatus,
    ModuleAPI,
    PeptideData,
    ProteinData,
    SampleData,
    Storage,
    ModuleContext
  };
}