import React, { useState, useEffect } from 'react';
import { Card, Button, Select, Space, Table, Spin, message, Empty } from 'antd';
import { DownloadOutlined, FileTextOutlined } from '@ant-design/icons';
import axios from 'axios';

function Reports() {
  const [loading, setLoading] = useState(false);
  const [businesses, setBusinesses] = useState([]);
  const [selectedBusiness, setSelectedBusiness] = useState(null);
  const [assessments, setAssessments] = useState([]);
  const [downloadingId, setDownloadingId] = useState(null);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  useEffect(() => {
    fetchBusinesses();
  }, []);

  const fetchBusinesses = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await axios.get(`${API_URL}/api/businesses/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setBusinesses(res.data?.businesses || []);
    } catch (error) {
      console.error('Error fetching businesses:', error);
      message.error('Failed to load businesses');
    }
  };

  const handleBusinessSelect = async (businessId) => {
    setSelectedBusiness(businessId);
    try {
      const token = localStorage.getItem('token');
      const res = await axios.get(`${API_URL}/api/assessments/business/${businessId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAssessments(res.data?.assessments || []);
    } catch (error) {
      console.error('Error fetching assessments:', error);
      setAssessments([]);
    }
  };

  const handleDownloadPDF = async (assessmentId, businessName) => {
    setDownloadingId(assessmentId);
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        message.error('Not authenticated. Please log in.');
        return;
      }
      
      // Request PDF from backend
      const response = await axios.get(
        `${API_URL}/api/assessments/${assessmentId}/download-pdf`,
        {
          headers: { Authorization: `Bearer ${token}` },
          responseType: 'blob'
        }
      );

      // Verify response is actually a PDF
      const contentType = response.headers['content-type'];
      if (!contentType || !contentType.includes('application/pdf')) {
        console.error('Invalid Content-Type:', contentType);
        console.error('Response data:', response.data);
        message.error('Server returned invalid PDF. Check backend logs.');
        return;
      }

      // Create blob and trigger download
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `Assessment_${businessName}_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      message.success('PDF downloaded successfully');
    } catch (error) {
      // Log detailed error information
      console.error('Download error:', error);
      console.error('Status:', error.response?.status);
      console.error('Status Text:', error.response?.statusText);
      console.error('Data:', error.response?.data);
      console.error('Headers:', error.response?.headers);
      
      // Show specific error message based on error type
      if (error.response?.status === 404) {
        message.error('Assessment not found. Create one first.');
      } else if (error.response?.status === 401) {
        message.error('Session expired. Please log in again.');
      } else if (error.response?.status === 403) {
        message.error('You do not have permission to download this assessment.');
      } else if (error.response?.status === 500) {
        message.error('Server error. Check backend logs for details.');
      } else if (error.code === 'ERR_NETWORK') {
        message.error('Network error. Is the backend running on port 8000?');
      } else if (error.message === 'Network Error') {
        message.error('Cannot connect to backend. Is it running?');
      } else {
        message.error(`Failed to download PDF: ${error.response?.data?.detail || error.message}`);
      }
    } finally {
      setDownloadingId(null);
    }
  };

  const columns = [
    {
      title: 'Health Score',
      dataIndex: 'financial_health_score',
      key: 'score',
      render: (score) => `${score}/100`
    },
    {
      title: 'Rating',
      dataIndex: 'creditworthiness_rating',
      key: 'rating'
    },
    {
      title: 'Risk Level',
      dataIndex: 'risk_level',
      key: 'risk'
    },
    {
      title: 'Generated',
      dataIndex: 'created_at',
      key: 'date',
      render: (date) => new Date(date).toLocaleDateString()
    },
    {
      title: 'Action',
      key: 'action',
      render: (_, record) => (
        <Button
          type="primary"
          icon={<DownloadOutlined />}
          size="small"
          loading={downloadingId === record.id}
          onClick={() => {
            const business = businesses.find(b => b.id === selectedBusiness);
            handleDownloadPDF(record.id, business?.business_name || 'Report');
          }}
        >
          Download PDF
        </Button>
      )
    }
  ];

  return (
    <div style={{ padding: '24px' }}>
      <h1 style={{ marginBottom: '24px' }}>Financial Reports</h1>

      <Card style={{ marginBottom: '24px' }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <label style={{ marginRight: '8px' }}>Select Business:</label>
            <Select
              placeholder="Choose a business"
              value={selectedBusiness}
              onChange={handleBusinessSelect}
              options={businesses.map(b => ({
                label: b.business_name,
                value: b.id
              }))}
              style={{ width: '300px' }}
            />
          </div>
        </Space>
      </Card>

      <Card title="Available Assessments">
        {selectedBusiness ? (
          assessments.length > 0 ? (
            <Table
              columns={columns}
              dataSource={assessments}
              rowKey="id"
              pagination={false}
              loading={loading}
            />
          ) : (
            <Empty description="No assessments found for this business" />
          )
        ) : (
          <Empty description="Select a business to view assessments" />
        )}
      </Card>
    </div>
  );
}

export default Reports;
