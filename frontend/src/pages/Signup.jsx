import React, { useState } from 'react';
import { Form, Input, Button, Card, Row, Col, message, Divider, Checkbox, Alert } from 'antd';
import { MailOutlined, LockOutlined, UserOutlined, ShopOutlined, ArrowRightOutlined, LoadingOutlined } from '@ant-design/icons';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function Signup({ setIsAuthenticated }) {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const handleSignup = async (values) => {
    setError(null);
    
    if (values.password !== values.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);
    
    try {
      let retries = 3;
      let lastError = null;
      
      while (retries > 0) {
        try {
          const res = await axios.post(`${API_URL}/api/auth/register`, {
            email: values.email,
            password: values.password,
            full_name: values.fullName,
            company_name: values.companyName
          }, { 
            timeout: 60000,
            headers: {
              'Content-Type': 'application/json'
            }
          });

          localStorage.setItem('token', res.data.access_token);
          localStorage.setItem('user', JSON.stringify(res.data.user));
          
          if (setIsAuthenticated) {
            setIsAuthenticated(true);
          }
          
          message.success('Account created successfully!');
          navigate('/dashboard');
          return;
        } catch (error) {
          lastError = error;
          retries--;
          
          if (retries > 0) {
            await new Promise(resolve => setTimeout(resolve, 1000));
          }
        }
      }
      
      const errorMsg = lastError?.response?.data?.detail || 
                       lastError?.message || 
                       'Signup failed. Please try again.';
      setError(errorMsg);
      message.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px'
    }}>
      <Row gutter={32} style={{ width: '100%', maxWidth: '1200px' }}>
        <Col xs={24} md={12} style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <div style={{ color: 'white' }}>
            <h1 style={{ fontSize: '48px', fontWeight: 'bold', marginBottom: '16px' }}>
              Get Started Today
            </h1>
            <p style={{ fontSize: '24px', marginBottom: '32px', opacity: 0.9 }}>
              Join thousands of businesses
            </p>
            <div style={{ fontSize: '16px', lineHeight: '1.8', opacity: 0.8 }}>
              <p>✓ Free financial health assessment</p>
              <p>✓ AI-powered insights in minutes</p>
              <p>✓ Secure data encryption</p>
              <p>✓ 24/7 support</p>
            </div>
          </div>
        </Col>

        <Col xs={24} md={12}>
          <Card
            style={{
              borderRadius: '16px',
              boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
              border: 'none',
              overflow: 'hidden'
            }}
          >
            <div style={{ padding: '40px' }}>
              <h2 style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '8px', textAlign: 'center' }}>
                Create Account
              </h2>
              <p style={{ textAlign: 'center', color: '#666', marginBottom: '32px' }}>
                Start your financial health journey
              </p>

              {error && (
                <Alert
                  message="Error"
                  description={error}
                  type="error"
                  showIcon
                  closable
                  onClose={() => setError(null)}
                  style={{ marginBottom: '16px' }}
                />
              )}

              <Form
                form={form}
                layout="vertical"
                onFinish={handleSignup}
                autoComplete="off"
              >
                <Form.Item
                  name="fullName"
                  rules={[{ required: true, message: 'Please enter your full name' }]}
                >
                  <Input
                    prefix={<UserOutlined style={{ color: '#667eea' }} />}
                    placeholder="Full name"
                    size="large"
                    disabled={loading}
                    style={{
                      borderRadius: '8px',
                      border: '1px solid #e0e0e0',
                      fontSize: '14px'
                    }}
                  />
                </Form.Item>

                <Form.Item
                  name="companyName"
                  rules={[{ required: true, message: 'Please enter your company name' }]}
                >
                  <Input
                    prefix={<ShopOutlined style={{ color: '#667eea' }} />}
                    placeholder="Company name"
                    size="large"
                    disabled={loading}
                    style={{
                      borderRadius: '8px',
                      border: '1px solid #e0e0e0',
                      fontSize: '14px'
                    }}
                  />
                </Form.Item>

                <Form.Item
                  name="email"
                  rules={[
                    { required: true, message: 'Please enter your email' },
                    { type: 'email', message: 'Please enter a valid email' }
                  ]}
                >
                  <Input
                    prefix={<MailOutlined style={{ color: '#667eea' }} />}
                    placeholder="Email address"
                    size="large"
                    disabled={loading}
                    style={{
                      borderRadius: '8px',
                      border: '1px solid #e0e0e0',
                      fontSize: '14px'
                    }}
                  />
                </Form.Item>

                <Form.Item
                  name="password"
                  rules={[
                    { required: true, message: 'Please enter your password' },
                    { min: 6, message: 'Password must be at least 6 characters' }
                  ]}
                >
                  <Input.Password
                    prefix={<LockOutlined style={{ color: '#667eea' }} />}
                    placeholder="Password"
                    size="large"
                    disabled={loading}
                    style={{
                      borderRadius: '8px',
                      border: '1px solid #e0e0e0',
                      fontSize: '14px'
                    }}
                  />
                </Form.Item>

                <Form.Item
                  name="confirmPassword"
                  rules={[{ required: true, message: 'Please confirm your password' }]}
                >
                  <Input.Password
                    prefix={<LockOutlined style={{ color: '#667eea' }} />}
                    placeholder="Confirm password"
                    size="large"
                    disabled={loading}
                    style={{
                      borderRadius: '8px',
                      border: '1px solid #e0e0e0',
                      fontSize: '14px'
                    }}
                  />
                </Form.Item>

                <Form.Item>
                  <Checkbox disabled={loading}>
                    I agree to the Terms of Service and Privacy Policy
                  </Checkbox>
                </Form.Item>

                <Form.Item>
                  <Button
                    type="primary"
                    htmlType="submit"
                    size="large"
                    loading={loading}
                    block
                    style={{
                      borderRadius: '8px',
                      height: '48px',
                      fontSize: '16px',
                      fontWeight: 'bold',
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      border: 'none'
                    }}
                  >
                    {loading ? 'Creating Account...' : 'Create Account'}
                    {!loading && <ArrowRightOutlined style={{ marginLeft: '8px' }} />}
                  </Button>
                </Form.Item>
              </Form>

              <Divider style={{ margin: '24px 0' }}>OR</Divider>

              <div style={{ textAlign: 'center' }}>
                <p style={{ color: '#666', marginBottom: '16px' }}>
                  Already have an account?
                </p>
                <Button
                  type="default"
                  size="large"
                  block
                  onClick={() => navigate('/login')}
                  disabled={loading}
                  style={{
                    borderRadius: '8px',
                    height: '48px',
                    fontSize: '16px',
                    fontWeight: 'bold',
                    border: '2px solid #667eea',
                    color: '#667eea'
                  }}
                >
                  Sign In
                </Button>
              </div>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default Signup;
