import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Sidebar.css';

const Sidebar = ({ collapsed, onToggle }) => {
  const location = useLocation();

  const menuItems = [
    {
      path: '/dashboard',
      icon: '📊',
      label: '대시보드',
      description: '전체 현황'
    },
    {
      path: '/projects',
      icon: '📁',
      label: '프로젝트 관리',
      description: '프로젝트 목록'
    },
    {
      path: '/bloggers',
      icon: '👥',
      label: '블로거 관리',
      description: '수집된 블로거'
    },
    {
      path: '/settings',
      icon: '⚙️',
      label: '설정',
      description: '시스템 설정'
    }
  ];

  return (
    <div className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      {/* 로고 및 브랜드 */}
      <div className="sidebar-header">
        <div className="brand">
          <div className="brand-icon">🤖</div>
          {!collapsed && (
            <div className="brand-text">
              <div className="brand-title">BloggerRPA</div>
              <div className="brand-subtitle">마케팅 자동화</div>
            </div>
          )}
        </div>
        <button className="sidebar-toggle" onClick={onToggle}>
          {collapsed ? '→' : '←'}
        </button>
      </div>

      {/* 네비게이션 메뉴 */}
      <nav className="sidebar-nav">
        <ul className="nav-list">
          {menuItems.map((item) => (
            <li key={item.path} className="nav-item">
              <Link
                to={item.path}
                className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
              >
                <span className="nav-icon">{item.icon}</span>
                {!collapsed && (
                  <div className="nav-text">
                    <span className="nav-label">{item.label}</span>
                    <span className="nav-description">{item.description}</span>
                  </div>
                )}
              </Link>
            </li>
          ))}
        </ul>
      </nav>

      {/* 하단 정보 */}
      {!collapsed && (
        <div className="sidebar-footer">
          <div className="system-info">
            <div className="info-item">
              <span className="info-label">버전</span>
              <span className="info-value">v2.0.0</span>
            </div>
            <div className="info-item">
              <span className="info-label">상태</span>
              <span className="info-value status-online">온라인</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Sidebar;