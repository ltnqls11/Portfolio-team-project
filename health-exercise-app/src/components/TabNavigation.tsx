import React from 'react';
import { TabType } from '../types';
import './TabNavigation.css';

interface TabNavigationProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
  userInfo?: any; // 사용자 정보가 있으면 일부 탭 활성화
}

const TabNavigation: React.FC<TabNavigationProps> = ({ activeTab, onTabChange, userInfo }) => {
  const tabs = [
    { id: 'home' as TabType, label: '🏠 홈', icon: '🏠' },
    { id: 'input' as TabType, label: '📝 건강 정보', icon: '📝' },
    { id: 'recommendation' as TabType, label: '💪 운동 추천', icon: '💪', requiresUserInfo: true },
    { id: 'videos' as TabType, label: '🎬 운동 비디오', icon: '🎬', requiresUserInfo: true },
    { id: 'notifications' as TabType, label: '⏰ 알림 설정', icon: '⏰' },
    { id: 'progress' as TabType, label: '📊 진행 상황', icon: '📊', requiresUserInfo: true }
  ];

  return (
    <nav className="tab-navigation">
      <div className="tab-container">
        {tabs.map((tab) => {
          const isDisabled = tab.requiresUserInfo && !userInfo;
          const isActive = activeTab === tab.id;
          
          return (
            <button
              key={tab.id}
              className={`tab-button ${isActive ? 'active' : ''} ${isDisabled ? 'disabled' : ''}`}
              onClick={() => !isDisabled && onTabChange(tab.id)}
              disabled={isDisabled}
              title={isDisabled ? '먼저 건강 정보를 입력해주세요' : tab.label}
            >
              <span className="tab-icon">{tab.icon}</span>
              <span className="tab-label">{tab.label}</span>
              {isActive && <div className="active-indicator" />}
            </button>
          );
        })}
      </div>
    </nav>
  );
};

export default TabNavigation;
