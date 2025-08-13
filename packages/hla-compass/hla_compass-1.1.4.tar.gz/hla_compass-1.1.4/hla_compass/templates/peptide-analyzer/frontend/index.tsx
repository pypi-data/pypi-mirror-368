/**
 * Peptide Analyzer Frontend
 * A ready-to-run UI for peptide sequence analysis using Ant Design
 */

import React, { useState, useCallback, useEffect } from 'react';
import { ModuleProps } from '@hla-compass/sdk';
import {
  Card,
  Form,
  Input,
  Select,
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
  Tag,
  Progress,
  Descriptions,
  message,
  Tooltip
} from 'antd';
import {
  ExperimentOutlined,
  SearchOutlined,
  DownloadOutlined,
  InfoCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined
} from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

// Module interfaces
interface PeptideInput {
  sequence: string;
  hla_allele: string;
  limit: number;
}

interface PeptideAnalysis {
  sequence: string;
  length: number;
  molecular_weight: number;
  hydrophobicity: number;
  charge_ratio: number;
  hydrophobic_residues: number;
  charged_residues: number;
  composition: Record<string, number>;
}

interface SimilarPeptide {
  sequence: string;
  length: number;
  molecular_weight: number;
  source: string;
  similarity: number;
}

interface HLAPrediction {
  hla_allele: string;
  score: number;
  binding_class: string;
  percentile_rank: number;
}

interface PeptideOutput {
  analysis: PeptideAnalysis;
  similar_peptides: SimilarPeptide[];
  predictions: HLAPrediction;
  metadata: {
    module: string;
    version: string;
    job_id: string;
  };
}

// Common HLA alleles
const HLA_ALLELES = [
  'HLA-A*02:01',
  'HLA-A*01:01',
  'HLA-A*03:01',
  'HLA-A*24:02',
  'HLA-B*07:02',
  'HLA-B*08:01',
  'HLA-B*27:05',
  'HLA-B*35:01',
  'HLA-C*07:01',
  'HLA-C*07:02'
];

export const ModuleUI: React.FC<ModuleProps<PeptideInput, PeptideOutput>> = ({
  input,
  onExecute,
  onInputChange,
  executionStatus,
  result,
  error
}) => {
  const [form] = Form.useForm();
  
  // Initialize form
  useEffect(() => {
    if (input) {
      form.setFieldsValue(input);
    }
  }, [input, form]);

  // Handle form changes
  const handleFormChange = useCallback((changedValues: any, allValues: PeptideInput) => {
    onInputChange(allValues);
  }, [onInputChange]);

  // Handle form submission
  const handleSubmit = useCallback((values: PeptideInput) => {
    // Validate sequence
    const sequence = values.sequence.toUpperCase().replace(/\s/g, '');
    if (!/^[ACDEFGHIKLMNPQRSTVWY]+$/.test(sequence)) {
      message.error('Sequence contains invalid amino acids');
      return;
    }
    onExecute();
  }, [onExecute]);

  // Export functions
  const exportResults = useCallback(() => {
    if (!result) return;
    
    const dataStr = JSON.stringify(result, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    const exportFileDefaultName = `peptide-analysis-${Date.now()}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
    message.success('Analysis exported successfully');
  }, [result]);

  // Render binding class tag
  const renderBindingTag = (bindingClass: string) => {
    const config = {
      'Strong Binder': { color: 'success', icon: <CheckCircleOutlined /> },
      'Weak Binder': { color: 'warning', icon: <InfoCircleOutlined /> },
      'Non-Binder': { color: 'error', icon: <CloseCircleOutlined /> }
    };
    const { color, icon } = config[bindingClass] || { color: 'default', icon: null };
    
    return (
      <Tag color={color} icon={icon}>
        {bindingClass}
      </Tag>
    );
  };

  // Table columns for similar peptides
  const columns = [
    {
      title: 'Sequence',
      dataIndex: 'sequence',
      key: 'sequence',
      render: (seq: string) => <Text code>{seq}</Text>
    },
    {
      title: 'Length',
      dataIndex: 'length',
      key: 'length',
      width: 80,
    },
    {
      title: 'MW (Da)',
      dataIndex: 'molecular_weight',
      key: 'molecular_weight',
      width: 100,
      render: (mw: number) => mw?.toFixed(1) || 'N/A'
    },
    {
      title: 'Source',
      dataIndex: 'source',
      key: 'source',
      width: 150,
    },
    {
      title: 'Similarity',
      dataIndex: 'similarity',
      key: 'similarity',
      width: 120,
      render: (similarity: number) => (
        <Progress 
          percent={similarity} 
          size="small" 
          format={percent => `${percent}%`}
        />
      ),
      sorter: (a: SimilarPeptide, b: SimilarPeptide) => a.similarity - b.similarity,
      defaultSortOrder: 'descend' as const
    }
  ];

  // Loading state
  if (executionStatus === 'running') {
    return (
      <Card>
        <Space direction="vertical" size="large" style={{ width: '100%', textAlign: 'center', padding: '40px 0' }}>
          <Spin size="large" tip="Analyzing peptide sequence..." />
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
            <span>Peptide Sequence Analysis</span>
          </Space>
        }
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          onValuesChange={handleFormChange}
          initialValues={{
            sequence: '',
            hla_allele: 'HLA-A*02:01',
            limit: 10
          }}
        >
          <Form.Item
            label="Peptide Sequence"
            name="sequence"
            rules={[
              { required: true, message: 'Please enter a peptide sequence' },
              { min: 7, message: 'Sequence must be at least 7 amino acids' },
              { max: 15, message: 'Sequence must be at most 15 amino acids' },
              { 
                pattern: /^[ACDEFGHIKLMNPQRSTVWY\s]+$/i,
                message: 'Use only standard amino acids (ACDEFGHIKLMNPQRSTVWY)'
              }
            ]}
            tooltip="Enter a peptide sequence (7-15 amino acids)"
          >
            <TextArea 
              placeholder="e.g., SIINFEKL or GILGFVFTL" 
              rows={2}
              style={{ fontFamily: 'monospace', fontSize: '16px' }}
              onChange={(e) => {
                // Convert to uppercase as user types
                e.target.value = e.target.value.toUpperCase();
              }}
            />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="HLA Allele"
                name="hla_allele"
                tooltip="Select the HLA allele for binding prediction"
              >
                <Select size="large">
                  {HLA_ALLELES.map(allele => (
                    <Select.Option key={allele} value={allele}>
                      {allele}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="Max Similar Peptides"
                name="limit"
                tooltip="Maximum number of similar peptides to retrieve"
              >
                <InputNumber 
                  min={1} 
                  max={100}
                  style={{ width: '100%' }}
                  size="large"
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item>
            <Button 
              type="primary" 
              htmlType="submit"
              icon={<SearchOutlined />}
              size="large"
              block
            >
              Analyze Peptide
            </Button>
          </Form.Item>
        </Form>
      </Card>

      {/* Error Display */}
      {error && (
        <Alert
          message="Analysis Error"
          description={error.message}
          type="error"
          showIcon
          closable
        />
      )}

      {/* Results Display */}
      {result && executionStatus === 'completed' && (() => {
        // Handle both direct result and wrapped result (from API)
        const resultData = (result as any).results || result;
        
        // Check if we have the expected structure
        if (!resultData?.analysis) {
          return (
            <Alert
              message="Analysis Complete"
              description="The analysis completed successfully but the results format is unexpected. Please check the raw results."
              type="warning"
              showIcon
              action={
                <Button size="small" onClick={() => console.log('Raw result:', result)}>
                  View Console
                </Button>
              }
            />
          );
        }
        
        return (
          <>
            {/* Sequence Analysis */}
            <Card 
              title="Sequence Analysis"
              extra={
                <Button 
                  icon={<DownloadOutlined />}
                  onClick={exportResults}
                >
                  Export Results
                </Button>
              }
            >
              <Descriptions bordered column={2}>
                <Descriptions.Item label="Sequence" span={2}>
                  <Text code style={{ fontSize: '16px' }}>
                    {resultData.analysis.sequence}
                  </Text>
                </Descriptions.Item>
                <Descriptions.Item label="Length">
                  {resultData.analysis.length} aa
                </Descriptions.Item>
                <Descriptions.Item label="Molecular Weight">
                  {resultData.analysis.molecular_weight} Da
                </Descriptions.Item>
                <Descriptions.Item label="Hydrophobicity">
                  <Progress 
                    percent={resultData.analysis.hydrophobicity} 
                    size="small"
                    strokeColor="#1890ff"
                  />
                </Descriptions.Item>
                <Descriptions.Item label="Charge Ratio">
                  <Progress 
                    percent={resultData.analysis.charge_ratio} 
                    size="small"
                    strokeColor="#52c41a"
                  />
                </Descriptions.Item>
                <Descriptions.Item label="Hydrophobic Residues">
                  {resultData.analysis.hydrophobic_residues}
                </Descriptions.Item>
                <Descriptions.Item label="Charged Residues">
                  {resultData.analysis.charged_residues}
                </Descriptions.Item>
              </Descriptions>

              {/* Amino Acid Composition */}
              <div style={{ marginTop: '20px' }}>
                <Title level={5}>Amino Acid Composition</Title>
                <Space wrap>
                  {Object.entries(resultData.analysis.composition).map(([aa, count]) => (
                    <Tag key={aa} color="blue">
                      {aa}: {count}
                    </Tag>
                  ))}
                </Space>
              </div>
            </Card>

            {/* HLA Binding Prediction */}
            <Card title="HLA Binding Prediction">
              <Row gutter={16}>
                <Col span={6}>
                  <Statistic 
                    title="HLA Allele" 
                    value={resultData.predictions.hla_allele}
                    valueStyle={{ fontSize: '16px' }}
                  />
                </Col>
                <Col span={6}>
                  <Statistic 
                    title="Binding Score" 
                    value={resultData.predictions.score}
                    suffix="/ 100"
                    precision={1}
                  />
                </Col>
                <Col span={6}>
                  <Statistic 
                    title="Percentile Rank" 
                    value={resultData.predictions.percentile_rank}
                    suffix="%"
                    precision={1}
                  />
                </Col>
                <Col span={6}>
                  <div style={{ marginTop: '4px' }}>
                    <Text type="secondary">Classification</Text>
                    <div style={{ marginTop: '8px' }}>
                      {renderBindingTag(resultData.predictions.binding_class)}
                    </div>
                  </div>
                </Col>
              </Row>
            </Card>

            {/* Similar Peptides */}
            {resultData.similar_peptides && resultData.similar_peptides.length > 0 && (
              <Card title={`Similar Peptides (${resultData.similar_peptides.length})`}>
                <Table
                  columns={columns}
                  dataSource={resultData.similar_peptides}
                  rowKey="sequence"
                  pagination={{ pageSize: 10 }}
                  size="small"
                />
              </Card>
            )}
          </>
        );
      })()}
    </Space>
  );
};

export default ModuleUI;