import React, { useState, useEffect } from 'react';
import { Layout, Menu, Dropdown, Avatar, Button, Space, message, Divider } from 'antd';
import { DashboardOutlined, FileTextOutlined, BarChartOutlined, UserOutlined, LogoutOutlined, SettingOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const { Header } = Layout;

function Navigation() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }
  }, []);

  const menuItems = [
    {
      key: 'dashboard',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
      onClick: () => navigate('/dashboard')
    },
    {
      key: 'assessment',
      icon: <BarChartOutlined />,
      label: 'Assessment',
      onClick: () => navigate('/assessment')
    },
    {
      key: 'reports',
      icon: <FileTextOutlined />,
      label: 'Reports',
      onClick: () => navigate('/reports')
    }
  ];

  // Logout handler - clears auth and redirects
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    message.success('Logged out successfully');
    navigate('/login');
  };

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'Profile',
      onClick: () => navigate('/profile')
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: 'Settings',
      onClick: () => navigate('/settings')
    },
    {
      type: 'divider'
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
      danger: true,
      onClick: handleLogout
    }
  ];

  return (
    <Header
      style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: '0 24px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        height: '64px'
      }}
    >
      {/* Left Section: Logo + Navigation Menu */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '24px', flex: 1 }}>
        <div style={{ color: 'white', fontSize: '20px', fontWeight: 'bold', whiteSpace: 'nowrap' }}>
          💰 FinHealth
        </div>
        <Menu 
          theme="dark" 
          mode="horizontal" 
          items={menuItems}
          style={{
            background: 'transparent',
            border: 'none',
            flex: 1
          }}
        />
      </div>

      {/* Right Section: User Profile Dropdown */}
      <Dropdown 
        menu={{ items: userMenuItems }} 
        placement="bottomRight"
        trigger={['click']}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            cursor: 'pointer',
            padding: '8px 12px',
            borderRadius: '6px',
            transition: 'background-color 0.3s ease',
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            '&:hover': {
              backgroundColor: 'rgba(255, 255, 255, 0.2)'
            }
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.2)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
          }}
        >
          {/* Avatar */}
          <Avatar 
            size={40}
            style={{ 
              background: '#fff', 
              color: '#667eea',
              flexShrink: 0
            }}
            icon={<UserOutlined />}
          />

          {/* User Info */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2px', minWidth: '0' }}>
            <div 
              style={{ 
                fontSize: '14px', 
                fontWeight: '600',
                color: 'white',
                lineHeight: '1.2',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap'
              }}
            >
              {user?.full_name || 'User'}
            </div>
            <div 
              style={{ 
                fontSize: '12px', 
                color: 'rgba(255, 255, 255, 0.8)',
                lineHeight: '1.2',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap'
              }}
            >
              {user?.email || 'user@example.com'}
            </div>
          </div>
        </div>
      </Dropdown>
    </Header>
  );
}

export default Navigation;
