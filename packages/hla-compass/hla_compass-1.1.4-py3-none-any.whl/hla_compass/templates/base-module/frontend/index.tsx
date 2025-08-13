/**
 * Frontend component for HLA-Compass module
 * This file is only used for modules with type: "with-ui"
 * Uses Ant Design components to align with platform styling
 */

import React, { useState, useCallback, useEffect } from 'react';
import { 
  ModuleProps 
} from '@hla-compass/sdk';
import {
  Card,
  Form,
  Input,
  InputNumber,
  Button,
  Alert,
  Spin,
  Table,
  Space,
  Typography,
  Row,
  Col,
  Statistic,
  Divider,
  message
} from 'antd';
import {
  PlayCircleOutlined,
  DownloadOutlined,
  ExperimentOutlined
} from '@ant-design/icons';

const { Title, Text } = Typography;

// Execution status constants for better type safety
const EXECUTION_STATUS = {
  IDLE: 'idle',
  RUNNING: 'running',
  COMPLETED: 'completed',
  FAILED: 'failed'
} as const;

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
 * Main module UI component using Ant Design
 */
export const ModuleUI: React.FC<ModuleProps<ModuleInput, ModuleOutput>> = ({
  input,
  onExecute,
  onInputChange,
  executionStatus,
  result,
  error
}) => {
  const [form] = Form.useForm();
  
  // Initialize form with input values
  useEffect(() => {
    if (input) {
      form.setFieldsValue(input);
    }
  }, [input, form]);

  // Handle form changes
  const handleFormChange = useCallback((changedValues: any, allValues: ModuleInput) => {
    onInputChange(allValues);
  }, [onInputChange]);

  // Handle form submission
  const handleSubmit = useCallback((values: ModuleInput) => {
    onExecute();
  }, [onExecute]);

  // Export functions
  const exportResults = useCallback((data: ModuleOutput) => {
    const dataStr = JSON.stringify(data, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `results-${Date.now()}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
    message.success('Results exported as JSON');
  }, []);

  const exportResultsCSV = useCallback((data: ModuleOutput) => {
    const csvContent = [
      ['ID', 'Output', 'Score'],
      ...data.results.map(r => [r.id, r.output, r.score.toString()])
    ].map(row => row.join(',')).join('\n');
    
    const dataUri = 'data:text/csv;charset=utf-8,'+ encodeURIComponent(csvContent);
    
    const exportFileDefaultName = `results-${Date.now()}.csv`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
    message.success('Results exported as CSV');
  }, []);

  // Table columns for results
  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 100,
    },
    {
      title: 'Output',
      dataIndex: 'output',
      key: 'output',
    },
    {
      title: 'Score',
      dataIndex: 'score',
      key: 'score',
      width: 120,
      render: (score: number) => score.toFixed(2),
    },
  ];

  // Render loading state
  if (executionStatus === EXECUTION_STATUS.RUNNING) {
    return (
      <Card>
        <Space direction="vertical" size="large" style={{ width: '100%', textAlign: 'center', padding: '40px 0' }}>
          <Spin size="large" />
          <Text>Processing your request...</Text>
        </Space>
      </Card>
    );
  }

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      {/* Input Form */}
      <Card 
        title={
          <Space>
            <ExperimentOutlined />
            <span>Module Configuration</span>
          </Space>
        }
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          onValuesChange={handleFormChange}
          initialValues={{
            peptide_sequences_text: input?.peptide_sequences?.join('\n') || '',
            hla_allele: input?.hla_allele || '',
            confidence_threshold: input?.confidence_threshold || 50
          }}
        >
          <Form.Item
            label="Example Parameter"
            name="example_param"
            rules={[{ required: true, message: 'Please enter a value' }]}
            tooltip="Enter the value to process"
          >
            <Input 
              placeholder="Enter value..." 
              size="large"
            />
          </Form.Item>

          <Form.Item
            label="Optional Parameter"
            name="optional_param"
            tooltip="Adjust processing threshold (1-1000)"
          >
            <InputNumber 
              min={1} 
              max={1000}
              style={{ width: '100%' }}
              size="large"
            />
          </Form.Item>

          <Form.Item>
            <Button 
              type="primary" 
              htmlType="submit"
              icon={<PlayCircleOutlined />}
              size="large"
              disabled={executionStatus === EXECUTION_STATUS.RUNNING}
            >
              Execute Analysis
            </Button>
          </Form.Item>
        </Form>
      </Card>

      {/* Error Display */}
      {error && (
        <Alert
          message="Execution Error"
          description={error.message}
          type="error"
          showIcon
        />
      )}

      {/* Results Display */}
      {result && executionStatus === EXECUTION_STATUS.COMPLETED && (
        <>
          {/* Summary Statistics */}
          <Card title="Summary">
            <Row gutter={16}>
              <Col span={12}>
                <Statistic 
                  title="Total Results" 
                  value={result.summary.total_results} 
                />
              </Col>
              <Col span={12}>
                <Statistic 
                  title="Average Score" 
                  value={result.summary.statistics.average_score} 
                  precision={2}
                />
              </Col>
            </Row>
          </Card>

          {/* Detailed Results Table */}
          <Card 
            title="Detailed Results"
            extra={
              <Space>
                <Button 
                  icon={<DownloadOutlined />}
                  onClick={() => exportResults(result)}
                >
                  Export JSON
                </Button>
                <Button 
                  icon={<DownloadOutlined />}
                  onClick={() => exportResultsCSV(result)}
                >
                  Export CSV
                </Button>
              </Space>
            }
          >
            <Table
              columns={columns}
              dataSource={result.results}
              rowKey="id"
              pagination={{ pageSize: 10 }}
            />
          </Card>
        </>
      )}
    </Space>
  );
};

// Export for module loader
export default ModuleUI;