import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './Sidebar.css';

const Sidebar = ({ currentMenu, menuOptions, onMenuSelect, progress, systemStatus }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuRoutes = {
    "홈": "/home",
    "증상 선택": "/condition-selection",
    "개인정보 입력": "/personal-info",
    "작업환경 평가": "/work-environment",
    "개인 운동 설문": "/exercise-survey",
    "운동 추천": "/exercise-recommendation",
    "휴식 알리미 설정": "/notification-setup",
    "운동 관리": "/exercise-management"
  };

  const handleMenuClick = (menu) => {
    const route = menuRoutes[menu];
    if (route) {
      navigate(route);
      onMenuSelect(menu);
    }
  };

  const getCurrentMenuFromPath = () => {
    const currentPath = location.pathname;
    for (const [menu, route] of Object.entries(menuRoutes)) {
      if (route === currentPath) {
        return menu;
      }
    }
    return "홈";
  };

  const activeMenu = getCurrentMenuFromPath();

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2>💻 VDT 관리 시스템</h2>
      </div>

      <nav className="sidebar-nav">
        <h3>메뉴 선택</h3>
        <ul className="nav-list">
          {menuOptions.map((menu, index) => (
            <li key={menu} className="nav-item">
              <button
                className={`nav-link ${activeMenu === menu ? 'active' : ''}`}
                onClick={() => handleMenuClick(menu)}
              >
                {menu}
              </button>
            </li>
          ))}
        </ul>
      </nav>

      <div className="sidebar-divider"></div>

      <div className="system-status">
        <h3>⚙️ 시스템 상태</h3>
        <div className="status-list">
          <div className={`status-item ${systemStatus.youtubeSearch ? 'success' : 'error'}`}>
            <span className="status-icon">
              {systemStatus.youtubeSearch ? '✅' : '❌'}
            </span>
            <span className="status-text">YouTube 검색</span>
          </div>
          
          <div className={`status-item ${systemStatus.aiRecommendation ? 'success' : 'error'}`}>
            <span className="status-icon">
              {systemStatus.aiRecommendation ? '✅' : '❌'}
            </span>
            <span className="status-text">AI 추천</span>
          </div>
          
          <div className={`status-item ${systemStatus.dataStorage ? 'success' : 'warning'}`}>
            <span className="status-icon">
              {systemStatus.dataStorage ? '✅' : '⚠️'}
            </span>
            <span className="status-text">데이터 저장</span>
          </div>
          
          <div className={`status-item ${systemStatus.adsRecommendation ? 'success' : 'warning'}`}>
            <span className="status-icon">
              {systemStatus.adsRecommendation ? '✅' : '⚠️'}
            </span>
            <span className="status-text">광고/제품 추천</span>
          </div>
        </div>
      </div>

      <div className="progress-section">
        <div className="progress">
          <div 
            className="progress-bar" 
            style={{ width: `${progress.percentage}%` }}
          ></div>
        </div>
        <div className="progress-text">
          {progress.completed}/{progress.total} 단계 완료 ({Math.round(progress.percentage)}%)
        </div>
      </div>
    </div>
  );
};

export default Sidebar;