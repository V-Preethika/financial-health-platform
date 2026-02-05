import React, { useState } from 'react';
import { Form, Input, Button, Card, Row, Col, message, Divider, Checkbox, Alert } from 'antd';
import { MailOutlined, LockOutlined, ArrowRightOutlined } from '@ant-design/icons';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function Login({ setIsAuthenticated }) {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const handleLogin = async (values) => {
    setError(null);
    setLoading(true);
    
    try {
      const res = await axios.post(`${API_URL}/api/auth/login`, {
        email: values.email,
        password: values.password
      }, { 
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json'
        }
      });

      localStorage.setItem('token', res.data.access_token);
      localStorage.setItem('user', JSON.stringify(res.data.user));
      
      if (setIsAuthenticated) {
        setIsAuthenticated(true);
      }
      
      message.success('Login successful!');
      navigate('/dashboard');
    } catch (error) {
      console.error('Login error:', error);
      const errorMsg = error.response?.data?.detail || 
                       error.message || 
                       'Login failed. Please check your credentials and try again.';
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
              Financial Health
            </h1>
            <p style={{ fontSize: '24px', marginBottom: '32px', opacity: 0.9 }}>
              Assessment Platform
            </p>
            <div style={{ fontSize: '16px', lineHeight: '1.8', opacity: 0.8 }}>
              <p>✓ Analyze your financial data instantly</p>
              <p>✓ Get AI-powered insights and recommendations</p>
              <p>✓ Track your business health metrics</p>
              <p>✓ Make data-driven decisions</p>
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
                Welcome Back
              </h2>
              <p style={{ textAlign: 'center', color: '#666', marginBottom: '32px' }}>
                Sign in to your account to continue
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
                onFinish={handleLogin}
                autoComplete="off"
              >
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
                  rules={[{ required: true, message: 'Please enter your password' }]}
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

                <Form.Item>
                  <Checkbox disabled={loading}>Remember me</Checkbox>
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
                    {loading ? 'Signing In...' : 'Sign In'}
                    {!loading && <ArrowRightOutlined style={{ marginLeft: '8px' }} />}
                  </Button>
                </Form.Item>
              </Form>

              <Divider style={{ margin: '24px 0' }}>OR</Divider>

              <div style={{ textAlign: 'center', marginBottom: '24px' }}>
                <p style={{ color: '#666', marginBottom: '16px' }}>
                  Don't have an account?
                </p>
                <Button
                  type="default"
                  size="large"
                  block
                  onClick={() => navigate('/signup')}
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
                  Create Account
                </Button>
              </div>

              <p style={{ textAlign: 'center', fontSize: '12px', color: '#999' }}>
                By signing in, you agree to our Terms of Service and Privacy Policy
              </p>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default Login;
