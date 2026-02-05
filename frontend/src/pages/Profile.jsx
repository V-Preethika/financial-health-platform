import React, { useState, useEffect } from 'react';
import { Card, Form, Input, Button, Row, Col, message, Spin, Avatar, Divider, Space, Tag } from 'antd';
import { UserOutlined, MailOutlined, PhoneOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function Profile() {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      const parsedUser = JSON.parse(userData);
      setUser(parsedUser);
      form.setFieldsValue({
        full_name: parsedUser.full_name,
        email: parsedUser.email,
        phone: parsedUser.phone || ''
      });
    }
  }, [form]);

  const handleUpdateProfile = async (values) => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      
      const response = await axios.put(
        `${API_URL}/api/auth/profile`,
        {
          full_name: values.full_name,
          phone: values.phone
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      const updatedUser = {
        ...user,
        full_name: values.full_name,
        phone: values.phone
      };
      
      localStorage.setItem('user', JSON.stringify(updatedUser));
      setUser(updatedUser);
      message.success('Profile updated successfully');
    } catch (error) {
      console.error('Error updating profile:', error);
      message.error(error.response?.data?.detail || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return <Spin />;
  }

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
        <Col xs={24} sm={24} lg={8}>
          <Card style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.1)', textAlign: 'center' }}>
            <Avatar 
              size={120}
              style={{ background: '#667eea', marginBottom: '16px' }}
              icon={<UserOutlined />}
            />
            <h2 style={{ marginBottom: '8px' }}>{user.full_name}</h2>
            <p style={{ color: '#666', marginBottom: '16px' }}>{user.email}</p>
            <Tag color="blue">Active User</Tag>
            <Divider />
            <div style={{ textAlign: 'left' }}>
              <div style={{ marginBottom: '12px' }}>
                <strong>Email:</strong>
                <p style={{ color: '#666', margin: '4px 0' }}>{user.email}</p>
              </div>
              <div style={{ marginBottom: '12px' }}>
                <strong>Phone:</strong>
                <p style={{ color: '#666', margin: '4px 0' }}>{user.phone || 'Not provided'}</p>
              </div>
              <div>
                <strong>Member Since:</strong>
                <p style={{ color: '#666', margin: '4px 0' }}>
                  {user.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                </p>
              </div>
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={24} lg={16}>
          <Card 
            title={<strong>Edit Profile</strong>}
            style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}
          >
            <Form
              form={form}
              layout="vertical"
              onFinish={handleUpdateProfile}
            >
              <Form.Item
                name="full_name"
                label={<strong>Full Name</strong>}
                rules={[{ required: true, message: 'Please enter your full name' }]}
              >
                <Input 
                  prefix={<UserOutlined />}
                  placeholder="Enter your full name"
                  size="large"
                />
              </Form.Item>

              <Form.Item
                name="email"
                label={<strong>Email</strong>}
              >
                <Input 
                  prefix={<MailOutlined />}
                  placeholder="Your email"
                  disabled
                  size="large"
                />
              </Form.Item>

              <Form.Item
                name="phone"
                label={<strong>Phone Number</strong>}
              >
                <Input 
                  prefix={<PhoneOutlined />}
                  placeholder="Enter your phone number"
                  size="large"
                />
              </Form.Item>

              <Form.Item>
                <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
                  <Button size="large" onClick={() => navigate('/dashboard')}>
                    Cancel
                  </Button>
                  <Button 
                    type="primary" 
                    htmlType="submit" 
                    loading={loading}
                    size="large"
                  >
                    Save Changes
                  </Button>
                </Space>
              </Form.Item>
            </Form>
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default Profile;
