import { useState, useEffect } from 'react';
import { Row, Col, Card, Progress, Spin, Empty, Button, Tag, Space, message, Dropdown, Modal, Alert } from 'antd';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { PlusOutlined, ReloadOutlined, MoreOutlined, DeleteOutlined } from '@ant-design/icons';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

// Helper functions
const getHealthScoreStatus = (score) => {
  if (score >= 80) return { status: 'Excellent', color: '#52c41a' };
  if (score >= 70) return { status: 'Good', color: '#52c41a' };
  if (score >= 60) return { status: 'Fair', color: '#faad14' };
  if (score >= 50) return { status: 'Needs Attention', color: '#faad14' };
  return { status: 'Poor', color: '#ff4d4f' };
};

const getRatingColor = (rating) => {
  const colors = { 'A': '#52c41a', 'B': '#52c41a', 'C': '#faad14', 'D': '#ff4d4f' };
  return colors[rating] || '#1890ff';
};

const getRatingExplanation = (rating) => {
  const explanations = {
    'A': {
      meaning: 'Excellent',
      shortLabel: 'Strong credit access',
      description: 'Your business has excellent creditworthiness. You have strong access to credit at the best rates.',
      action: 'Maintain this performance and consider strategic investments'
    },
    'B': {
      meaning: 'Good',
      shortLabel: 'Competitive credit access',
      description: 'Your business has good creditworthiness. You can access credit at competitive rates.',
      action: 'Focus on building cash reserves to reach Rating A'
    },
    'C': {
      meaning: 'Fair',
      shortLabel: 'Limited credit access',
      description: 'Your business has fair creditworthiness. You can access credit but at higher rates.',
      action: 'Improve cash flow and reduce debt to reach Rating B'
    },
    'D': {
      meaning: 'Poor',
      shortLabel: 'High risk for borrowing',
      description: 'Your business has poor creditworthiness. Lenders view you as high-risk.',
      action: 'Improve cash collection and reduce expenses immediately'
    }
  };
  return explanations[rating] || { meaning: 'Unknown', shortLabel: 'No data', description: 'No data', action: 'Contact support' };
};

const getRiskColor = (risk) => {
  const colors = { 'Low': 'green', 'Medium': 'orange', 'High': 'red' };
  return colors[risk] || 'blue';
};

const getKeyFactors = (assessment) => {
  if (!assessment || !assessment.key_findings) return [];
  
  const findings = assessment.key_findings;
  const factors = [];
  
  // Extract key metrics
  if (findings.profit_margin !== undefined) {
    factors.push({
      label: 'Profit Margin',
      value: (findings.profit_margin * 100).toFixed(1) + '%',
      status: findings.profit_margin > 0.12 ? 'good' : findings.profit_margin > 0 ? 'fair' : 'poor'
    });
  }
  if (findings.current_ratio !== undefined) {
    factors.push({
      label: 'Current Ratio',
      value: findings.current_ratio.toFixed(2),
      status: findings.current_ratio > 1.5 ? 'good' : findings.current_ratio > 1 ? 'fair' : 'poor'
    });
  }
  if (findings.debt_to_equity !== undefined) {
    factors.push({
      label: 'Debt-to-Equity',
      value: findings.debt_to_equity.toFixed(2),
      status: findings.debt_to_equity < 1 ? 'good' : findings.debt_to_equity < 2 ? 'fair' : 'poor'
    });
  }
  if (findings.roe !== undefined) {
    factors.push({
      label: 'ROE',
      value: (findings.roe * 100).toFixed(1) + '%',
      status: findings.roe > 0.15 ? 'good' : findings.roe > 0 ? 'fair' : 'poor'
    });
  }
  
  return factors;
};

function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [businesses, setBusinesses] = useState([]);
  const [selectedBusiness, setSelectedBusiness] = useState(null);
  const [assessment, setAssessment] = useState(null);
  const navigate = useNavigate();

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  useEffect(() => {
    fetchBusinesses();
  }, []);

  const fetchBusinesses = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      if (!token) {
        message.error('Authentication required');
        navigate('/login');
        return;
      }
      
      const res = await axios.get(`${API_URL}/api/businesses/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Only set businesses if API returns valid data
      const businessList = res.data?.businesses || [];
      setBusinesses(businessList);
      
      // Only auto-select first business if list is not empty
      if (businessList.length > 0) {
        setSelectedBusiness(businessList[0]);
        fetchAssessment(businessList[0].id);
      } else {
        // Clear assessment if no businesses exist
        setAssessment(null);
        setSelectedBusiness(null);
      }
    } catch (error) {
      console.error('Error fetching businesses:', error);
      message.error('Failed to load businesses');
      setBusinesses([]);
      setSelectedBusiness(null);
      setAssessment(null);
    } finally {
      setLoading(false);
    }
  };

  const fetchAssessment = async (businessId) => {
    try {
      const token = localStorage.getItem('token');
      
      const res = await axios.get(`${API_URL}/api/assessments/business/${businessId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const assessmentList = res.data?.assessments || [];
      
      if (assessmentList.length > 0) {
        const latestAssessment = assessmentList[0];
        const detailRes = await axios.get(`${API_URL}/api/assessments/${latestAssessment.id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setAssessment(detailRes.data?.assessment || null);
      } else {
        setAssessment(null);
      }
    } catch (error) {
      console.error('Error fetching assessment:', error);
      setAssessment(null);
    }
  };

  const handleBusinessSelect = (business) => {
    setSelectedBusiness(business);
    fetchAssessment(business.id);
  };

  const handleDeleteBusiness = async (businessId, businessName) => {
    if (!window.confirm(`Delete "${businessName}"? This cannot be undone.`)) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        message.error('Authentication required');
        navigate('/login');
        return;
      }

      if (!businessId) {
        message.error('Invalid business ID');
        return;
      }
      
      await axios.delete(`${API_URL}/api/businesses/${businessId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      setBusinesses(prev => prev.filter(b => b.id !== businessId));
      
      if (selectedBusiness?.id === businessId) {
        setSelectedBusiness(null);
        setAssessment(null);
      }

      message.success(`"${businessName}" deleted successfully`);
    } catch (error) {
      console.error('Delete error:', error);
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to delete business';
      message.error(errorMsg);
    }
  };

  // ============ HELPER: Check if value is valid (not 0, NaN, undefined, null) ============
  const isValidMetric = (value) => {
    return value !== null && value !== undefined && !isNaN(value) && value !== 0;
  };

  // ============ HELPER: Get score interpretation ============
  const getScoreInterpretation = (score) => {
    if (score >= 80) return { text: 'Excellent', color: '#52c41a' };
    if (score >= 70) return { text: 'Good', color: '#52c41a' };
    if (score >= 60) return { text: 'Fair', color: '#faad14' };
    if (score >= 50) return { text: 'Needs Attention', color: '#faad14' };
    return { text: 'Critical', color: '#ff4d4f' };
  };

  // ============ HELPER: Get score explanation ============
  const getScoreExplanation = (score) => {
    if (score >= 80) return 'Your business is financially excellent. You\'re managing cash and debt well.';
    if (score >= 70) return 'Your business is financially stable. You\'re managing cash well.';
    if (score >= 60) return 'Your business is stable but has room for improvement.';
    if (score >= 50) return 'Your business needs attention to financial management.';
    return 'Your business faces significant financial challenges.';
  };

  // ============ HELPER: Get credit rating explanation ============
  const getCreditRatingExplanation = (rating) => {
    const explanations = {
      'A': {
        meaning: 'Excellent',
        description: 'Your business demonstrates strong financial stability with healthy profitability, manageable debt levels, and solid liquidity. Lenders view you as a low-risk borrower.',
        action: 'Maintain current financial practices. You\'re in a strong position to access credit at favorable rates.'
      },
      'B': {
        meaning: 'Good',
        description: 'Your business shows solid financial performance with acceptable profitability and debt management. You\'re generally viewed as a reliable borrower with manageable risk.',
        action: 'Focus on improving profit margins and reducing debt levels to move toward an A rating.'
      },
      'C': {
        meaning: 'Fair',
        description: 'Your business has some financial concerns. Profitability or liquidity may be below industry standards, or debt levels are elevated. Lenders may require higher interest rates.',
        action: 'Prioritize improving cash flow, reducing expenses, and paying down debt. Review the recommendations below.'
      },
      'D': {
        meaning: 'Poor',
        description: 'Your business faces significant financial challenges. Low profitability, high debt, or weak liquidity are major concerns. Accessing credit will be difficult and expensive.',
        action: 'Take immediate action: reduce expenses, improve cash collection, and consider debt restructuring. Seek professional financial advice.'
      }
    };
    return explanations[rating] || explanations['D'];
  };

  // ============ HELPER: Get risk color ============
  const getRiskColor = (level) => {
    switch (level) {
      case 'Low': return 'green';
      case 'Medium': return 'orange';
      case 'High': return 'red';
      default: return 'blue';
    }
  };

  // ============ HELPER: Get rating color ============
  const getRatingColor = (rating) => {
    switch (rating) {
      case 'A': return 'green';
      case 'B': return 'blue';
      case 'C': return 'orange';
      case 'D': return 'red';
      default: return 'gray';
    }
  };

  // Show loading spinner while fetching
  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <Spin size="large" tip="Loading your businesses..." />
      </div>
    );
  }

  // Show empty state when no businesses exist
  if (!businesses || businesses.length === 0) {
    return (
      <div style={{ padding: '48px 24px', textAlign: 'center', minHeight: '100vh', backgroundColor: '#f0f2f5' }}>
        <Empty 
          description="No businesses found" 
          style={{ marginBottom: '24px' }}
        />
        <p style={{ color: '#666', marginBottom: '24px', fontSize: '16px' }}>
          Get started by creating your first business assessment
        </p>
        <Button 
          type="primary" 
          size="large" 
          icon={<PlusOutlined />}
          onClick={() => navigate('/assessment')}
          style={{ borderRadius: '6px', height: '48px', fontSize: '16px' }}
        >
          Create Your First Assessment
        </Button>
      </div>
    );
  }

  return (
    <div style={{ padding: '24px', minHeight: '100vh', backgroundColor: '#f0f2f5' }}>
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '8px' }}>
          Financial Health Dashboard
        </h1>
        <p style={{ color: '#666', fontSize: '16px' }}>
          Monitor your business financial metrics and performance
        </p>
      </div>

      <Card style={{ marginBottom: '24px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
        <Row justify="space-between" align="middle" style={{ marginBottom: '16px' }}>
          <Col>
            <strong style={{ fontSize: '16px' }}>Your Businesses</strong>
          </Col>
          <Col>
            <Space>
              <Button 
                icon={<ReloadOutlined />} 
                onClick={fetchBusinesses}
              >
                Refresh
              </Button>
              <Button 
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => navigate('/assessment')}
              >
                New Assessment
              </Button>
            </Space>
          </Col>
        </Row>
        <Row gutter={16}>
          {businesses.map(business => {
            // Menu items for the 3-dot dropdown
            const menuItems = [
              {
                key: 'delete',
                label: 'Delete',
                icon: <DeleteOutlined />,
                danger: true,
                onClick: () => {
                  Modal.confirm({
                    title: 'Delete Business',
                    content: `Are you sure you want to delete "${business.business_name}"? This action cannot be undone.`,
                    okText: 'Delete',
                    okType: 'danger',
                    cancelText: 'Cancel',
                    onOk() {
                      handleDeleteBusiness(business.id, business.business_name);
                    }
                  });
                }
              }
            ];

            return (
              <Col key={business.id} xs={24} sm={12} lg={6}>
                <Card 
                  hoverable
                  onClick={() => handleBusinessSelect(business)}
                  style={{ 
                    cursor: 'pointer',
                    border: selectedBusiness?.id === business.id ? '2px solid #1890ff' : '1px solid #d9d9d9',
                    borderRadius: '8px',
                    position: 'relative'
                  }}
                >
                  {/* 3-dot menu in top-right corner */}
                  <div style={{
                    position: 'absolute',
                    top: '8px',
                    right: '8px',
                    zIndex: 10
                  }}>
                    <Dropdown 
                      menu={{ items: menuItems }}
                      trigger={['click']}
                      placement="bottomRight"
                    >
                      <Button 
                        type="text" 
                        size="small"
                        icon={<MoreOutlined />}
                        onClick={(e) => e.stopPropagation()}
                        style={{ color: '#666' }}
                      />
                    </Dropdown>
                  </div>

                  {/* Business card content */}
                  <div style={{ fontWeight: 'bold', marginBottom: '8px', fontSize: '16px', paddingRight: '32px' }}>
                    {business.business_name}
                  </div>
                  <Tag color="blue" style={{ marginBottom: '8px' }}>
                    {business.business_type}
                  </Tag>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    {business.industry}
                  </div>
                </Card>
              </Col>
            );
          })}
        </Row>
      </Card>

      {assessment ? (
        <>
          <Row gutter={16} style={{ marginBottom: '24px' }}>
            <Col xs={24} sm={12} lg={6}>
              <Card style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.1)', borderRadius: '8px', height: '100%' }}>
                <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', justifyContent: 'center', minHeight: '180px' }}>
                  <div style={{ fontSize: '11px', color: '#999', marginBottom: '12px', fontWeight: '600', letterSpacing: '0.5px', textTransform: 'uppercase' }}>
                    Health Score
                  </div>
                  <div style={{ 
                    fontSize: '48px', 
                    fontWeight: '700',
                    color: getHealthScoreStatus(assessment.financial_health_score).color,
                    marginBottom: '12px',
                    lineHeight: '1'
                  }}>
                    {assessment.financial_health_score}
                  </div>
                  <Progress 
                    percent={assessment.financial_health_score}
                    strokeColor={getHealthScoreStatus(assessment.financial_health_score).color}
                    format={() => null}
                    style={{ marginBottom: '12px' }}
                  />
                  <div style={{ fontSize: '13px', fontWeight: '500', color: '#333' }}>
                    {getHealthScoreStatus(assessment.financial_health_score).status}
                  </div>
                </div>
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.1)', borderRadius: '8px', height: '100%' }}>
                <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', justifyContent: 'center', minHeight: '180px' }}>
                  <div style={{ fontSize: '11px', color: '#999', marginBottom: '12px', fontWeight: '600', letterSpacing: '0.5px', textTransform: 'uppercase' }}>
                    Credit Rating
                  </div>
                  <div style={{ 
                    fontSize: '48px', 
                    fontWeight: '700',
                    color: getRatingColor(assessment.creditworthiness_rating),
                    marginBottom: '12px',
                    lineHeight: '1'
                  }}>
                    {assessment.creditworthiness_rating}
                  </div>
                  <div style={{ fontSize: '13px', fontWeight: '500', color: '#333', marginBottom: '8px' }}>
                    {getRatingExplanation(assessment.creditworthiness_rating).meaning}
                  </div>
                  <div style={{ fontSize: '12px', color: '#666', lineHeight: '1.4' }}>
                    {getRatingExplanation(assessment.creditworthiness_rating).shortLabel}
                  </div>
                </div>
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.1)', borderRadius: '8px', height: '100%' }}>
                <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', justifyContent: 'center', minHeight: '180px' }}>
                  <div style={{ fontSize: '11px', color: '#999', marginBottom: '12px', fontWeight: '600', letterSpacing: '0.5px', textTransform: 'uppercase' }}>
                    Risk Level
                  </div>
                  <Tag 
                    color={getRiskColor(assessment.risk_level)}
                    style={{ fontSize: '14px', padding: '6px 12px', marginBottom: '12px', alignSelf: 'center' }}
                  >
                    {assessment.risk_level}
                  </Tag>
                  <div style={{ fontSize: '13px', fontWeight: '500', color: '#333' }}>
                    {assessment.risk_level === 'Low' ? 'Stable' : 
                     assessment.risk_level === 'Medium' ? 'Monitor' : 'Critical'}
                  </div>
                </div>
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.1)', borderRadius: '8px', height: '100%' }}>
                <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', justifyContent: 'center', minHeight: '180px' }}>
                  <div style={{ fontSize: '11px', color: '#999', marginBottom: '12px', fontWeight: '600', letterSpacing: '0.5px', textTransform: 'uppercase' }}>
                    Profit Margin
                  </div>
                  <div style={{ 
                    fontSize: '48px', 
                    fontWeight: '700',
                    color: assessment.key_findings?.profit_margin > 0 ? '#52c41a' : '#ff4d4f',
                    marginBottom: '12px',
                    lineHeight: '1'
                  }}>
                    {(assessment.key_findings?.profit_margin * 100).toFixed(1)}%
                  </div>
                  <Progress 
                    percent={Math.min(Math.abs(assessment.key_findings?.profit_margin * 100), 100)}
                    strokeColor={assessment.key_findings?.profit_margin > 0 ? '#52c41a' : '#ff4d4f'}
                    format={() => null}
                  />
                </div>
              </Card>
            </Col>
          </Row>

          {/* What This Rating Means - Detailed Explanation Section */}
          <Card 
            style={{ marginBottom: '24px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)', backgroundColor: '#fafafa', borderLeft: `4px solid ${getRatingColor(assessment.creditworthiness_rating)}` }}
          >
            <Row gutter={24}>
              <Col xs={24} md={12}>
                <div>
                  <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '12px', color: '#1a1a1a' }}>
                    What This Rating Means
                  </h3>
                  <p style={{ fontSize: '14px', lineHeight: '1.6', color: '#333', marginBottom: '0' }}>
                    {getRatingExplanation(assessment.creditworthiness_rating).description}
                  </p>
                </div>
              </Col>
              <Col xs={24} md={12}>
                <div>
                  <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '12px', color: '#1a1a1a' }}>
                    Recommended Action
                  </h3>
                  <p style={{ fontSize: '14px', lineHeight: '1.6', color: '#333', marginBottom: '0' }}>
                    {getRatingExplanation(assessment.creditworthiness_rating).action}
                  </p>
                </div>
              </Col>
            </Row>
          </Card>

          <Card 
            title={<strong>🔍 Factors Affecting Your Credit Rating</strong>}
            style={{ marginBottom: '24px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}
          >
            <Row gutter={16}>
              {getKeyFactors(assessment).map((factor, idx) => (
                <Col xs={24} sm={12} lg={6} key={idx}>
                  <div style={{ 
                    padding: '12px', 
                    backgroundColor: '#fafafa', 
                    borderRadius: '8px',
                    borderLeft: `4px solid ${
                      factor.status === 'good' ? '#52c41a' : 
                      factor.status === 'fair' ? '#faad14' : 
                      '#ff4d4f'
                    }`
                  }}>
                    <div style={{ fontWeight: 'bold', fontSize: '12px', marginBottom: '4px', color: '#1890ff' }}>
                      {factor.label}
                    </div>
                    <div style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '4px' }}>
                      {factor.value}
                    </div>
                    <div style={{ fontSize: '11px', color: '#666', lineHeight: '1.4' }}>
                      {factor.explanation}
                    </div>
                  </div>
                </Col>
              ))}
            </Row>
          </Card>

          <Row gutter={16} style={{ marginBottom: '24px' }}>
            <Col xs={24} lg={12}>
              <Card 
                title={<strong>📈 Revenue Forecast (12 Months)</strong>}
                style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}
              >
                {assessment.forecast?.revenue_forecast && assessment.forecast.revenue_forecast.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={assessment.forecast.revenue_forecast}>
                      <defs>
                        <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#1890ff" stopOpacity={0.8}/>
                          <stop offset="95%" stopColor="#1890ff" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis />
                      <Tooltip />
                      <Area type="monotone" dataKey="value" stroke="#1890ff" fillOpacity={1} fill="url(#colorRevenue)" name="Revenue" />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : (
                  <Empty description="No forecast data available" />
                )}
              </Card>
            </Col>
            <Col xs={24} lg={12}>
              <Card 
                title={<strong>📊 Key Financial Ratios</strong>}
                style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}
              >
                {assessment.key_findings && Object.keys(assessment.key_findings).length > 0 ? (
                  <Row gutter={16}>
                    {Object.entries(assessment.key_findings).slice(0, 4).map(([key, value]) => (
                      <Col xs={24} sm={12} key={key}>
                        <div style={{ marginBottom: '16px' }}>
                          <div style={{ fontWeight: 'bold', fontSize: '12px', marginBottom: '4px' }}>
                            {key.replace(/_/g, ' ').toUpperCase()}
                          </div>
                          <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#1890ff', marginBottom: '4px' }}>
                            {typeof value === 'number' ? value.toFixed(2) : value}
                          </div>
                          <Progress 
                            percent={Math.min(Math.abs(value) * 50, 100)} 
                            strokeColor={value > 0 ? '#52c41a' : '#ff4d4f'}
                            size="small"
                          />
                        </div>
                      </Col>
                    ))}
                  </Row>
                ) : (
                  <Empty description="No financial ratios available" />
                )}
              </Card>
            </Col>
          </Row>

          <Card 
            title={<strong>⚠️ Identified Risks</strong>}
            style={{ marginBottom: '24px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}
          >
            {assessment.risks?.identified_risks && assessment.risks.identified_risks.length > 0 ? (
              <Row gutter={16}>
                {assessment.risks.identified_risks.map((risk, idx) => (
                  <Col xs={24} sm={12} lg={8} key={idx}>
                    <Card 
                      style={{ 
                        borderLeft: `4px solid ${getRiskColor(risk.severity)}`,
                        borderRadius: '8px'
                      }}
                    >
                      <Tag color={getRiskColor(risk.severity)} style={{ marginBottom: '8px' }}>
                        {risk.severity}
                      </Tag>
                      <div style={{ fontWeight: 'bold', marginBottom: '8px', fontSize: '14px' }}>
                        {risk.type}
                      </div>
                      <div style={{ fontSize: '12px', color: '#666' }}>
                        {risk.description.substring(0, 80)}...
                      </div>
                    </Card>
                  </Col>
                ))}
              </Row>
            ) : (
              <div style={{ textAlign: 'center', padding: '24px', color: '#52c41a' }}>
                ✓ No significant risks identified
              </div>
            )}
          </Card>

          <Card 
            title={<strong>💡 Cost Optimization Suggestions</strong>}
            style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}
          >
            {assessment.recommendations && assessment.recommendations.length > 0 ? (
              assessment.recommendations.map((rec, idx) => (
                <div key={idx} style={{ marginBottom: '16px', padding: '12px', backgroundColor: '#fafafa', borderRadius: '8px', borderLeft: '4px solid #1890ff' }}>
                  <div style={{ fontWeight: 'bold', marginBottom: '4px', color: '#1890ff' }}>
                    {rec.category}
                  </div>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    {rec.suggestion}
                  </div>
                </div>
              ))
            ) : (
              <Empty description="No recommendations available" />
            )}
          </Card>
        </>
      ) : (
        <Card style={{ textAlign: 'center', padding: '48px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
          <Empty 
            description="No assessment data for this business" 
            style={{ marginBottom: '24px' }}
          />
          <p style={{ color: '#666', marginBottom: '24px' }}>
            Create an assessment to analyze your financial data
          </p>
          <Button 
            type="primary" 
            size="large"
            icon={<PlusOutlined />}
            onClick={() => navigate('/assessment')}
            style={{ borderRadius: '6px', height: '48px', fontSize: '16px' }}
          >
            Create Assessment
          </Button>
        </Card>
      )}
    </div>
  );
}

export default Dashboard;
