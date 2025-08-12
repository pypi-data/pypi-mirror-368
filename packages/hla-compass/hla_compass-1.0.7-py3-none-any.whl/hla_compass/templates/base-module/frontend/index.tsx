/**
 * Frontend component for HLA-Compass module
 * This file is only used for modules with type: "with-ui"
 */

import React, { useState, useCallback, useEffect } from 'react';
import { 
  ModuleProps, 
  ModuleResult, 
  ExecutionStatus 
} from '@hla-compass/sdk';
import styles from './styles.module.css';

// Module-specific types
interface ModuleInput {
  example_param: string;
  optional_param?: number;
}

interface ModuleOutput {
  results: Array<{
    id: string;
    output: string;
    score: number;
  }>;
  summary: {
    total_results: number;
    statistics: {
      average_score: number;
    };
  };
}

/**
 * Main module UI component
 */
export const ModuleUI: React.FC<ModuleProps<ModuleInput, ModuleOutput>> = ({
  input,
  onExecute,
  onInputChange,
  executionStatus,
  result,
  error
}) => {
  // Local state for form inputs
  const [formData, setFormData] = useState<ModuleInput>({
    example_param: input?.example_param || '',
    optional_param: input?.optional_param || 100
  });

  // Update parent when form changes
  useEffect(() => {
    onInputChange(formData);
  }, [formData, onInputChange]);

  // Handle form submission
  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    onExecute();
  }, [onExecute]);

  // Handle input changes
  const handleInputChange = useCallback((
    field: keyof ModuleInput,
    value: string | number
  ) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  }, []);

  // Render loading state
  if (executionStatus === ExecutionStatus.Running) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <div className={styles.spinner} />
          <p>Processing your request...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      {/* Input Form */}
      <div className={styles.inputSection}>
        <h2>Module Input</h2>
        <form onSubmit={handleSubmit}>
          <div className={styles.formGroup}>
            <label htmlFor="example_param">
              Example Parameter *
              <span className={styles.tooltip}>
                Enter the value to process
              </span>
            </label>
            <input
              id="example_param"
              type="text"
              value={formData.example_param}
              onChange={(e) => handleInputChange('example_param', e.target.value)}
              placeholder="Enter value..."
              required
              className={styles.input}
            />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="optional_param">
              Optional Parameter
              <span className={styles.tooltip}>
                Adjust processing threshold (1-1000)
              </span>
            </label>
            <input
              id="optional_param"
              type="number"
              min="1"
              max="1000"
              value={formData.optional_param}
              onChange={(e) => handleInputChange('optional_param', parseInt(e.target.value))}
              className={styles.input}
            />
          </div>

          <button 
            type="submit" 
            className={styles.submitButton}
            disabled={!formData.example_param || executionStatus === ExecutionStatus.Running}
          >
            Execute Analysis
          </button>
        </form>
      </div>

      {/* Error Display */}
      {error && (
        <div className={styles.error}>
          <h3>Error</h3>
          <p>{error.message}</p>
        </div>
      )}

      {/* Results Display */}
      {result && executionStatus === ExecutionStatus.Completed && (
        <div className={styles.resultsSection}>
          <h2>Results</h2>
          
          {/* Summary */}
          <div className={styles.summary}>
            <h3>Summary</h3>
            <div className={styles.summaryGrid}>
              <div className={styles.summaryItem}>
                <span className={styles.label}>Total Results:</span>
                <span className={styles.value}>{result.summary.total_results}</span>
              </div>
              <div className={styles.summaryItem}>
                <span className={styles.label}>Average Score:</span>
                <span className={styles.value}>
                  {result.summary.statistics.average_score.toFixed(2)}
                </span>
              </div>
            </div>
          </div>

          {/* Detailed Results */}
          <div className={styles.results}>
            <h3>Detailed Results</h3>
            <div className={styles.resultsList}>
              {result.results.map((item) => (
                <div key={item.id} className={styles.resultItem}>
                  <div className={styles.resultHeader}>
                    <span className={styles.resultId}>#{item.id}</span>
                    <span className={styles.resultScore}>
                      Score: {item.score.toFixed(2)}
                    </span>
                  </div>
                  <div className={styles.resultOutput}>
                    {item.output}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Export Options */}
          <div className={styles.exportSection}>
            <button 
              className={styles.exportButton}
              onClick={() => exportResults(result)}
            >
              Export Results (JSON)
            </button>
            <button 
              className={styles.exportButton}
              onClick={() => exportResultsCSV(result)}
            >
              Export Results (CSV)
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

// Helper functions
function exportResults(result: ModuleOutput) {
  const dataStr = JSON.stringify(result, null, 2);
  const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
  
  const exportFileDefaultName = `results-${Date.now()}.json`;
  
  const linkElement = document.createElement('a');
  linkElement.setAttribute('href', dataUri);
  linkElement.setAttribute('download', exportFileDefaultName);
  linkElement.click();
}

function exportResultsCSV(result: ModuleOutput) {
  const csvContent = [
    ['ID', 'Output', 'Score'],
    ...result.results.map(r => [r.id, r.output, r.score.toString()])
  ].map(row => row.join(',')).join('\n');
  
  const dataUri = 'data:text/csv;charset=utf-8,'+ encodeURIComponent(csvContent);
  
  const exportFileDefaultName = `results-${Date.now()}.csv`;
  
  const linkElement = document.createElement('a');
  linkElement.setAttribute('href', dataUri);
  linkElement.setAttribute('download', exportFileDefaultName);
  linkElement.click();
}

// Export for module loader
export default ModuleUI;