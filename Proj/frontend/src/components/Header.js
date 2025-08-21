import React, { useState } from 'react';
import './Header.css';

const Header = ({ user }) => {
  const [showUserMenu, setShowUserMenu] = useState(false);

  return (
    <header className="header">
      <div className="header-content">
        {/* 검색 영역 */}
        <div className="header-search">
          <div className="search-box">
            <span className="search-icon">🔍</span>
            <input 
              type="text" 
              placeholder="프로젝트, 블로거 검색..." 
              className="search-input"
            />
          </div>
        </div>

        {/* 우측 메뉴 */}
        <div className="header-actions">
          {/* 알림 */}
          <button className="header-btn notification-btn">
            <span className="icon">🔔</span>
            <span className="badge">3</span>
          </button>

          {/* 도움말 */}
          <button className="header-btn help-btn">
            <span className="icon">❓</span>
          </button>

          {/* 사용자 메뉴 */}
          <div className="user-menu">
            <button 
              className="user-btn"
              onClick={() => setShowUserMenu(!showUserMenu)}
            >
              <div className="user-avatar">
                <span>{user.name.charAt(0)}</span>
              </div>
              <div className="user-info">
                <span className="user-name">{user.name}</span>
                <span className="user-role">{user.role}</span>
              </div>
              <span className="dropdown-arrow">▼</span>
            </button>

            {showUserMenu && (
              <div className="user-dropdown">
                <div className="dropdown-item">
                  <span className="item-icon">👤</span>
                  <span>프로필</span>
                </div>
                <div className="dropdown-item">
                  <span className="item-icon">⚙️</span>
                  <span>설정</span>
                </div>
                <div className="dropdown-divider"></div>
                <div className="dropdown-item logout">
                  <span className="item-icon">🚪</span>
                  <span>로그아웃</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;