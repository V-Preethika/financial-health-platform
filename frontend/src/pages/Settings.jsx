import React, { useState } from 'react';
import { Card, Form, Switch, Button, Row, Col, message, Divider, Space, Select } from 'antd';
import { BellOutlined, LockOutlined, EyeOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

function Settings() {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [settings, setSettings] = useState({
    emailNotifications: true,
    reportReminders: true,
    riskAlerts: true,
    language: 'en',
    theme: 'light'
  });
  const navigate = useNavigate();

  const handleSettingsChange = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleSaveSettings = async () => {
    setLoading(true);
    try {
      localStorage.setItem('appSettings', JSON.stringify(settings));
      message.success('Settings saved successfully');
    } catch (error) {
      message.error('Failed to save settings');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '24px', minHeight: '100vh', backgroundColor: '#f0f2f5' }}>
      <Button 
        icon={<ArrowLeftOutlined />} 
        onClick={() => navigate('/dashboard')}
        style={{ marginBottom: '24px' }}
      >
        Back to Dashboard
      </Button>

      <Row gutter={24}>
        <Col xs={24} lg={16}>
          <Card 
            title={<strong>⚙️ Application Settings</strong>}
            style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.1)', marginBottom: '24px' }}
          >
            <Form layout="vertical">
              <div style={{ marginBottom: '24px' }}>
                <h3 style={{ marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <BellOutlined /> Notifications
                </h3>
                <Form.Item label="Email Notifications" style={{ marginBottom: '12px' }}>
                  <Switch 
                    checked={settings.emailNotifications}
                    onChange={(value) => handleSettingsChange('emailNotifications', value)}
                  />
                  <span style={{ marginLeft: '12px', color: '#666' }}>
                    Receive email updates about your assessments
                  </span>
                </Form.Item>

                <Form.Item label="Report Reminders" style={{ marginBottom: '12px' }}>
                  <Switch 
                    checked={settings.reportReminders}
                    onChange={(value) => handleSettingsChange('reportReminders', value)}
                  />
                  <span style={{ marginLeft: '12px', color: '#666' }}>
                    Get reminded to review your financial reports
                  </span>
                </Form.Item>

                <Form.Item label="Risk Alerts">
                  <Switch 
                    checked={settings.riskAlerts}
                    onChange={(value) => handleSettingsChange('riskAlerts', value)}
                  />
                  <span style={{ marginLeft: '12px', color: '#666' }}>
                    Alert me about identified financial risks
                  </span>
                </Form.Item>
              </div>

              <Divider />

              <div style={{ marginBottom: '24px' }}>
                <h3 style={{ marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <EyeOutlined /> Display
                </h3>
                <Form.Item label="Language">
                  <Select 
                    value={settings.language}
                    onChange={(value) => handleSettingsChange('language', value)}
                    options={[
                      { label: 'English', value: 'en' },
                      { label: 'Hindi', value: 'hi' }
                    ]}
                  />
                </Form.Item>

                <Form.Item label="Theme">
                  <Select 
                    value={settings.theme}
                    onChange={(value) => handleSettingsChange('theme', value)}
                    options={[
                      { label: 'Light', value: 'light' },
                      { label: 'Dark', value: 'dark' }
                    ]}
                  />
                </Form.Item>
              </div>

              <Divider />

              <div>
                <h3 style={{ marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <LockOutlined /> Security
                </h3>
                <Button 
                  type="default"
                  onClick={() => message.info('Password change feature coming soon')}
                  style={{ marginBottom: '12px' }}
                >
                  Change Password
                </Button>
                <p style={{ color: '#666', fontSize: '12px' }}>
                  Update your password to keep your account secure
                </p>
              </div>

              <Divider />

              <Form.Item>
                <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
                  <Button size="large" onClick={() => navigate('/dashboard')}>
                    Cancel
                  </Button>
                  <Button 
                    type="primary" 
                    onClick={handleSaveSettings}
                    loading={loading}
                    size="large"
                  >
                    Save Settings
                  </Button>
                </Space>
              </Form.Item>
            </Form>
          </Card>
        </Col>

        <Col xs={24} lg={8}>
          <Card 
            title={<strong>ℹ️ About</strong>}
            style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}
          >
            <div style={{ marginBottom: '16px' }}>
              <strong>Financial Health Platform</strong>
              <p style={{ color: '#666', fontSize: '12px', margin: '4px 0' }}>
                Version 1.0.0
              </p>
            </div>
            <Divider />
            <div style={{ marginBottom: '16px' }}>
              <strong>Features</strong>
              <ul style={{ color: '#666', fontSize: '12px', margin: '8px 0', paddingLeft: '20px' }}>
                <li>Financial data analysis</li>
                <li>Risk assessment</li>
                <li>Cost optimization</li>
                <li>Industry benchmarking</li>
                <li>12-month forecasting</li>
              </ul>
            </div>
            <Divider />
            <div>
              <strong>Support</strong>
              <p style={{ color: '#666', fontSize: '12px', margin: '4px 0' }}>
                Email: support@finhealth.com
              </p>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default Settings;
