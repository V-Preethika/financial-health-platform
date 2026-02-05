import React, { useState } from 'react';
import { Form, Button, Upload, Select, Card, Steps, message, Spin, Row, Col, Statistic, Tag, Divider, Drawer, Progress, Space, Tooltip, Badge } from 'antd';
import { InboxOutlined, ArrowLeftOutlined, DownloadOutlined, PrinterOutlined, ShareAltOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function Assessment() {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [file, setFile] = useState(null);
  const [businessId, setBusinessId] = useState(null);
  const [assessmentResult, setAssessmentResult] = useState(null);
  const [language, setLanguage] = useState('en');
  const [detailsDrawer, setDetailsDrawer] = useState(false);
  const [selectedRisk, setSelectedRisk] = useState(null);
  const navigate = useNavigate();

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const businessTypes = [
    { label: 'Manufacturing', value: 'manufacturing' },
    { label: 'Retail', value: 'retail' },
    { label: 'Agriculture', value: 'agriculture' },
    { label: 'Services', value: 'services' },
    { label: 'Logistics', value: 'logistics' },
    { label: 'E-commerce', value: 'ecommerce' }
  ];

  const languages = [
    { label: 'English', value: 'en' },
    { label: 'Hindi', value: 'hi' }
  ];

  const handleFileUpload = (file) => {
    setFile(file);
    return false;
  };

  const handleSubmit = async (values) => {
    if (!file) {
      message.error('Please upload a file');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        message.error('Authentication required. Please login again.');
        return;
      }

      const headers = {
        Authorization: `Bearer ${token}`
      };

      const businessRes = await axios.post(`${API_URL}/api/businesses/`, {
        business_name: values.businessName || 'Business',
        business_type: values.businessType,
        industry: values.industry || 'General',
        annual_revenue: values.revenue || 0,
        employee_count: values.employees || 0
      }, { headers });

      const newBusinessId = businessRes.data.business_id;
      setBusinessId(newBusinessId);

      const formData = new FormData();
      formData.append('file', file);
      formData.append('fiscal_year', new Date().getFullYear().toString());

      await axios.post(`${API_URL}/api/upload/financial-data/${newBusinessId}`, formData, {
        headers: {
          ...headers,
          'Content-Type': 'multipart/form-data'
        }
      });

      const assessmentRes = await axios.post(
        `${API_URL}/api/assessments/create/${newBusinessId}?language=${language}`,
        {},
        { headers }
      );

      setAssessmentResult(assessmentRes.data.assessment);
      setCurrentStep(1);
      message.success('Assessment completed successfully!');
    } catch (error) {
      console.error('Error:', error);
      message.error(error.response?.data?.detail || 'Failed to complete assessment');
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    setCurrentStep(0);
    setFile(null);
    setAssessmentResult(null);
    form.resetFields();
    navigate('/dashboard');
  };

  const getRiskColor = (level) => {
    switch (level) {
      case 'Low': return 'green';
      case 'Medium': return 'orange';
      case 'High': return 'red';
      default: return 'blue';
    }
  };

  const getRatingColor = (rating) => {
    switch (rating) {
      case 'A': return 'green';
      case 'B': return 'blue';
      case 'C': return 'orange';
      case 'D': return 'red';
      default: return 'gray';
    }
  };

  const getHealthScoreStatus = (score) => {
    if (score >= 80) return { status: 'Excellent', color: '#52c41a' };
    if (score >= 70) return { status: 'Good', color: '#1890ff' };
    if (score >= 60) return { status: 'Fair', color: '#faad14' };
    return { status: 'Poor', color: '#ff4d4f' };
  };

  const handleDownloadReport = () => {
    const reportData = JSON.stringify(assessmentResult, null, 2);
    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(reportData));
    element.setAttribute('download', `assessment_${businessId}.json`);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    message.success('Report downloaded!');
  };

  const handlePrint = () => {
    window.print();
  };

  const steps = [
    { title: 'Business Info', description: 'Enter details' },
    { title: 'Results', description: 'View assessment' }
  ];

  return (
    <div style={{ padding: '24px', minHeight: '100vh', backgroundColor: '#f0f2f5' }}>
      <Button 
        icon={<ArrowLeftOutlined />} 
        onClick={() => navigate('/dashboard')}
        style={{ marginBottom: '24px' }}
      >
        Back to Dashboard
      </Button>
      
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '8px' }}>
          Financial Assessment
        </h1>
        <p style={{ color: '#666', fontSize: '16px' }}>
          Upload your financial documents and get instant insights
        </p>
      </div>

      <Card style={{ marginBottom: '24px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
        <Steps current={currentStep} items={steps} />
      </Card>

      <div>
        {currentStep === 0 ? (
          <Card style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
            <Form form={form} layout="vertical" onFinish={handleSubmit}>
              <Row gutter={24}>
                <Col xs={24} sm={12}>
                  <Form.Item
                    name="businessName"
                    label={<strong>Business Name</strong>}
                  >
                    <input 
                      type="text" 
                      placeholder="Enter business name" 
                      style={{ 
                        padding: '10px 12px', 
                        width: '100%', 
                        border: '1px solid #d9d9d9', 
                        borderRadius: '6px',
                        fontSize: '14px'
                      }} 
                    />
                  </Form.Item>
                </Col>
                <Col xs={24} sm={12}>
                  <Form.Item
                    name="businessType"
                    label={<strong>Business Type</strong>}
                    rules={[{ required: true, message: 'Please select business type' }]}
                  >
                    <Select 
                      placeholder="Select business type" 
                      options={businessTypes}
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={24}>
                <Col xs={24} sm={12}>
                  <Form.Item
                    name="industry"
                    label={<strong>Industry</strong>}
                  >
                    <input 
                      type="text" 
                      placeholder="e.g., Technology, Healthcare" 
                      style={{ 
                        padding: '10px 12px', 
                        width: '100%', 
                        border: '1px solid #d9d9d9', 
                        borderRadius: '6px',
                        fontSize: '14px'
                      }} 
                    />
                  </Form.Item>
                </Col>
                <Col xs={24} sm={12}>
                  <Form.Item
                    name="language"
                    label={<strong>Report Language</strong>}
                  >
                    <Select 
                      placeholder="Select language" 
                      options={languages}
                      value={language}
                      onChange={setLanguage}
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={24}>
                <Col xs={24} sm={12}>
                  <Form.Item
                    name="revenue"
                    label={<strong>Annual Revenue (Optional)</strong>}
                  >
                    <input 
                      type="number" 
                      placeholder="0" 
                      style={{ 
                        padding: '10px 12px', 
                        width: '100%', 
                        border: '1px solid #d9d9d9', 
                        borderRadius: '6px',
                        fontSize: '14px'
                      }} 
                    />
                  </Form.Item>
                </Col>
                <Col xs={24} sm={12}>
                  <Form.Item
                    name="employees"
                    label={<strong>Employee Count (Optional)</strong>}
                  >
                    <input 
                      type="number" 
                      placeholder="0" 
                      style={{ 
                        padding: '10px 12px', 
                        width: '100%', 
                        border: '1px solid #d9d9d9', 
                        borderRadius: '6px',
                        fontSize: '14px'
                      }} 
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Divider />

              <Form.Item
                name="documents"
                label={<strong>Upload Financial Documents</strong>}
                rules={[{ required: true, message: 'Please upload documents' }]}
              >
                <Upload.Dragger
                  name="file"
                  beforeUpload={handleFileUpload}
                  accept=".csv,.xlsx,.pdf"
                >
                  <p style={{ fontSize: '48px', marginBottom: '8px' }}>
                    <InboxOutlined style={{ color: '#1890ff' }} />
                  </p>
                  <p style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '4px' }}>
                    Click or drag files to upload
                  </p>
                  <p style={{ color: '#666', fontSize: '14px' }}>
                    Supported formats: CSV, XLSX, PDF
                  </p>
                  {file && (
                    <p style={{ color: '#52c41a', marginTop: '12px', fontSize: '14px' }}>
                      ✓ {file.name} selected
                    </p>
                  )}
                </Upload.Dragger>
              </Form.Item>

              <Form.Item>
                <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
                  <Button size="large" style={{ borderRadius: '6px' }}>
                    Cancel
                  </Button>
                  <Button 
                    type="primary" 
                    htmlType="submit" 
                    loading={loading} 
                    size="large"
                    style={{ borderRadius: '6px', minWidth: '200px' }}
                  >
                    Analyze Financial Data
                  </Button>
                </Space>
              </Form.Item>
            </Form>
          </Card>
        ) : (
          <Spin spinning={loading}>
            {assessmentResult && (
              <div>
                <Card style={{ marginBottom: '24px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
                  <Row justify="space-between" align="middle">
                    <Col>
                      <Button 
                        icon={<ArrowLeftOutlined />} 
                        onClick={handleBack}
                        size="large"
                        style={{ borderRadius: '6px' }}
                      >
                        Back to Upload
                      </Button>
                    </Col>
                    <Col>
                      <Space>
                        <Tooltip title="Download Report">
                          <Button 
                            icon={<DownloadOutlined />} 
                            onClick={handleDownloadReport}
                            style={{ borderRadius: '6px' }}
                          >
                            Download
                          </Button>
                        </Tooltip>
                        <Tooltip title="Print Report">
                          <Button 
                            icon={<PrinterOutlined />} 
                            onClick={handlePrint}
                            style={{ borderRadius: '6px' }}
                          >
                            Print
                          </Button>
                        </Tooltip>
                      </Space>
                    </Col>
                  </Row>
                </Card>

                <Row gutter={16} style={{ marginBottom: '24px' }}>
                  <Col xs={24} sm={12} lg={6}>
                    <Card style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.1)', borderRadius: '8px' }}>
                      <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '12px', color: '#666', marginBottom: '8px', fontWeight: 'bold' }}>
                          FINANCIAL HEALTH SCORE
                        </div>
                        <div style={{ 
                          fontSize: '48px', 
                          fontWeight: 'bold',
                          color: getHealthScoreStatus(assessmentResult.financial_health_score).color,
                          marginBottom: '8px'
                        }}>
                          {assessmentResult.financial_health_score}
                        </div>
                        <Progress 
                          type="circle" 
                          percent={assessmentResult.financial_health_score}
                          strokeColor={getHealthScoreStatus(assessmentResult.financial_health_score).color}
                          width={80}
                        />
                        <div style={{ marginTop: '12px', fontSize: '14px', fontWeight: 'bold' }}>
                          {getHealthScoreStatus(assessmentResult.financial_health_score).status}
                        </div>
                      </div>
                    </Card>
                  </Col>
                  <Col xs={24} sm={12} lg={6}>
                    <Card style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.1)', borderRadius: '8px' }}>
                      <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '12px', color: '#666', marginBottom: '8px', fontWeight: 'bold' }}>
                          CREDITWORTHINESS
                        </div>
                        <Badge 
                          count={assessmentResult.creditworthiness?.rating}
                          style={{ 
                            backgroundColor: getRatingColor(assessmentResult.creditworthiness?.rating),
                            fontSize: '32px',
                            width: '80px',
                            height: '80px',
                            lineHeight: '80px',
                            borderRadius: '50%'
                          }}
                        />
                        <div style={{ marginTop: '12px', fontSize: '14px', color: '#666' }}>
                          Rating
                        </div>
                      </div>
                    </Card>
                  </Col>
                  <Col xs={24} sm={12} lg={6}>
                    <Card style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.1)', borderRadius: '8px' }}>
                      <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '12px', color: '#666', marginBottom: '8px', fontWeight: 'bold' }}>
                          RISK LEVEL
                        </div>
                        <Tag 
                          color={getRiskColor(assessmentResult.risks?.risk_level)}
                          style={{ fontSize: '18px', padding: '8px 16px', marginBottom: '12px' }}
                        >
                          {assessmentResult.risks?.risk_level}
                        </Tag>
                        <div style={{ fontSize: '14px', color: '#666' }}>
                          {assessmentResult.risks?.risk_level === 'Low' ? '✓ Stable' : 
                           assessmentResult.risks?.risk_level === 'Medium' ? '⚠ Monitor' : '✗ Critical'}
                        </div>
                      </div>
                    </Card>
                  </Col>
                  <Col xs={24} sm={12} lg={6}>
                    <Card style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.1)', borderRadius: '8px' }}>
                      <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '12px', color: '#666', marginBottom: '8px', fontWeight: 'bold' }}>
                          PROFIT MARGIN
                        </div>
                        <div style={{ 
                          fontSize: '36px', 
                          fontWeight: 'bold',
                          color: assessmentResult.key_findings?.profit_margin > 0 ? '#52c41a' : '#ff4d4f',
                          marginBottom: '8px'
                        }}>
                          {(assessmentResult.key_findings?.profit_margin * 100).toFixed(1)}%
                        </div>
                        <Progress 
                          percent={Math.min(Math.abs(assessmentResult.key_findings?.profit_margin * 100), 100)}
                          strokeColor={assessmentResult.key_findings?.profit_margin > 0 ? '#52c41a' : '#ff4d4f'}
                        />
                      </div>
                    </Card>
                  </Col>
                </Row>

                <Card 
                  title={<strong>⚠️ Identified Risks</strong>}
                  style={{ marginBottom: '24px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}
                >
                  {assessmentResult.risks?.identified_risks?.length > 0 ? (
                    <Row gutter={16}>
                      {assessmentResult.risks.identified_risks.map((risk, idx) => (
                        <Col xs={24} sm={12} lg={8} key={idx}>
                          <Card 
                            hoverable
                            onClick={() => {
                              setSelectedRisk(risk);
                              setDetailsDrawer(true);
                            }}
                            style={{ borderLeft: `4px solid ${getRiskColor(risk.severity)}` }}
                          >
                            <Tag color={getRiskColor(risk.severity)} style={{ marginBottom: '8px' }}>
                              {risk.severity}
                            </Tag>
                            <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>
                              {risk.type}
                            </div>
                            <div style={{ fontSize: '12px', color: '#666' }}>
                              {risk.description.substring(0, 60)}...
                            </div>
                          </Card>
                        </Col>
                      ))}
                    </Row>
                  ) : (
                    <div style={{ textAlign: 'center', padding: '24px', color: '#52c41a' }}>
                      <CheckCircleOutlined style={{ fontSize: '32px', marginRight: '8px' }} />
                      No significant risks identified
                    </div>
                  )}
                </Card>

                <Card 
                  title={<strong>💡 Cost Optimization Suggestions</strong>}
                  style={{ marginBottom: '24px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}
                >
                  {assessmentResult.cost_optimizations?.map((opt, idx) => (
                    <div key={idx} style={{ marginBottom: '16px', padding: '16px', backgroundColor: '#fafafa', borderRadius: '8px', borderLeft: '4px solid #1890ff' }}>
                      <div style={{ fontWeight: 'bold', marginBottom: '8px', color: '#1890ff' }}>
                        {opt.category}
                      </div>
                      <div style={{ marginBottom: '8px' }}>
                        <strong>{opt.suggestion}</strong>
                      </div>
                      <div style={{ fontSize: '12px', color: '#666', marginBottom: '8px' }}>
                        {opt.action}
                      </div>
                      <Tag color="green">Potential Savings: {opt.potential_savings}</Tag>
                    </div>
                  ))}
                </Card>

                <Card 
                  title={<strong>📊 Industry Benchmarks</strong>}
                  style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}
                >
                  <Row gutter={16}>
                    {assessmentResult.benchmarks && Object.entries(assessmentResult.benchmarks).map(([key, value]) => (
                      <Col xs={24} sm={12} lg={6} key={key}>
                        <Card style={{ textAlign: 'center' }}>
                          <div style={{ fontSize: '12px', color: '#666', marginBottom: '8px', fontWeight: 'bold' }}>
                            {key.replace(/_/g, ' ').toUpperCase()}
                          </div>
                          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#1890ff' }}>
                            {typeof value === 'number' ? value.toFixed(2) : value}
                          </div>
                        </Card>
                      </Col>
                    ))}
                  </Row>
                </Card>
              </div>
            )}
          </Spin>
        )}
      </div>

      <Drawer
        title="Risk Details"
        placement="right"
        onClose={() => setDetailsDrawer(false)}
        open={detailsDrawer}
      >
        {selectedRisk && (
          <div>
            <div style={{ marginBottom: '16px' }}>
              <strong>Type:</strong> {selectedRisk.type}
            </div>
            <div style={{ marginBottom: '16px' }}>
              <strong>Severity:</strong>
              <Tag color={getRiskColor(selectedRisk.severity)} style={{ marginLeft: '8px' }}>
                {selectedRisk.severity}
              </Tag>
            </div>
            <div>
              <strong>Description:</strong>
              <p style={{ marginTop: '8px', color: '#666' }}>
                {selectedRisk.description}
              </p>
            </div>
          </div>
        )}
      </Drawer>
    </div>
  );
}

export default Assessment;
