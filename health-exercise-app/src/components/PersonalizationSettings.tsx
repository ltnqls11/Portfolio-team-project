import React, { useState, useEffect } from 'react';
import './PersonalizationSettings.css';

interface PersonalizationSettings {
  theme: 'light' | 'dark' | 'auto';
  notifications: {
    enabled: boolean;
    breakInterval: number;
    exerciseReminders: boolean;
    stretchReminders: boolean;
    soundEnabled: boolean;
  };
  preferences: {
    language: 'ko' | 'en';
    difficulty: 'beginner' | 'intermediate' | 'advanced';
    exerciseDuration: number;
    weeklyGoal: number;
  };
  accessibility: {
    highContrast: boolean;
    largeText: boolean;
    reducedMotion: boolean;
  };
}

interface PersonalizationSettingsProps {
  settings: PersonalizationSettings;
  onSave: (settings: PersonalizationSettings) => void;
  onClose: () => void;
}

const PersonalizationSettings: React.FC<PersonalizationSettingsProps> = ({
  settings,
  onSave,
  onClose
}) => {
  const [currentSettings, setCurrentSettings] = useState<PersonalizationSettings>(settings);
  const [activeTab, setActiveTab] = useState<'notifications' | 'preferences' | 'accessibility'>('notifications');

  const handleSettingChange = (category: keyof PersonalizationSettings, key: string, value: any) => {
    setCurrentSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value
      }
    }));
  };

  const handleSave = () => {
    onSave(currentSettings);
    onClose();
  };

  const renderNotificationsTab = () => (
    <div className="settings-section">
      <h3>알림 설정</h3>
      
      <div className="setting-item">
        <div className="setting-info">
          <h4>알림 활성화</h4>
          <p>휴식 시간과 운동 알림을 받습니다</p>
        </div>
        <label className="toggle-switch">
          <input
            type="checkbox"
            checked={currentSettings.notifications.enabled}
            onChange={(e) => handleSettingChange('notifications', 'enabled', e.target.checked)}
          />
          <span className="toggle-slider" />
        </label>
      </div>

      <div className="setting-item">
        <div className="setting-info">
          <h4>휴식 간격</h4>
          <p>몇 분마다 휴식 알림을 받을지 설정합니다</p>
        </div>
        <select
          value={currentSettings.notifications.breakInterval}
          onChange={(e) => handleSettingChange('notifications', 'breakInterval', parseInt(e.target.value))}
          disabled={!currentSettings.notifications.enabled}
        >
          <option value={30}>30분</option>
          <option value={45}>45분</option>
          <option value={60}>60분</option>
          <option value={90}>90분</option>
        </select>
      </div>

      <div className="setting-item">
        <div className="setting-info">
          <h4>운동 알림</h4>
          <p>정기적인 운동 알림을 받습니다</p>
        </div>
        <label className="toggle-switch">
          <input
            type="checkbox"
            checked={currentSettings.notifications.exerciseReminders}
            onChange={(e) => handleSettingChange('notifications', 'exerciseReminders', e.target.checked)}
            disabled={!currentSettings.notifications.enabled}
          />
          <span className="toggle-slider" />
        </label>
      </div>

      <div className="setting-item">
        <div className="setting-info">
          <h4>스트레칭 알림</h4>
          <p>정기적인 스트레칭 알림을 받습니다</p>
        </div>
        <label className="toggle-switch">
          <input
            type="checkbox"
            checked={currentSettings.notifications.stretchReminders}
            onChange={(e) => handleSettingChange('notifications', 'stretchReminders', e.target.checked)}
            disabled={!currentSettings.notifications.enabled}
          />
          <span className="toggle-slider" />
        </label>
      </div>

      <div className="setting-item">
        <div className="setting-info">
          <h4>알림 소리</h4>
          <p>알림 시 소리를 재생합니다</p>
        </div>
        <label className="toggle-switch">
          <input
            type="checkbox"
            checked={currentSettings.notifications.soundEnabled}
            onChange={(e) => handleSettingChange('notifications', 'soundEnabled', e.target.checked)}
            disabled={!currentSettings.notifications.enabled}
          />
          <span className="toggle-slider" />
        </label>
      </div>
    </div>
  );

  const renderPreferencesTab = () => (
    <div className="settings-section">
      <h3>사용자 선호도</h3>
      
      <div className="setting-item">
        <div className="setting-info">
          <h4>언어</h4>
          <p>앱에서 사용할 언어를 선택합니다</p>
        </div>
        <select
          value={currentSettings.preferences.language}
          onChange={(e) => handleSettingChange('preferences', 'language', e.target.value)}
        >
          <option value="ko">한국어</option>
          <option value="en">English</option>
        </select>
      </div>

      <div className="setting-item">
        <div className="setting-info">
          <h4>운동 난이도</h4>
          <p>선호하는 운동 난이도를 선택합니다</p>
        </div>
        <select
          value={currentSettings.preferences.difficulty}
          onChange={(e) => handleSettingChange('preferences', 'difficulty', e.target.value)}
        >
          <option value="beginner">초급</option>
          <option value="intermediate">중급</option>
          <option value="advanced">고급</option>
        </select>
      </div>

      <div className="setting-item">
        <div className="setting-info">
          <h4>운동 시간</h4>
          <p>한 번에 운동할 시간을 설정합니다</p>
        </div>
        <select
          value={currentSettings.preferences.exerciseDuration}
          onChange={(e) => handleSettingChange('preferences', 'exerciseDuration', parseInt(e.target.value))}
        >
          <option value={5}>5분</option>
          <option value={10}>10분</option>
          <option value={15}>15분</option>
          <option value={20}>20분</option>
          <option value={30}>30분</option>
        </select>
      </div>

      <div className="setting-item">
        <div className="setting-info">
          <h4>주간 목표</h4>
          <p>일주일에 운동할 횟수를 설정합니다</p>
        </div>
        <select
          value={currentSettings.preferences.weeklyGoal}
          onChange={(e) => handleSettingChange('preferences', 'weeklyGoal', parseInt(e.target.value))}
        >
          <option value={3}>3회</option>
          <option value={5}>5회</option>
          <option value={7}>7회</option>
        </select>
      </div>
    </div>
  );

  const renderAccessibilityTab = () => (
    <div className="settings-section">
      <h3>접근성</h3>
      
      <div className="setting-item">
        <div className="setting-info">
          <h4>고대비 모드</h4>
          <p>텍스트와 배경의 대비를 높입니다</p>
        </div>
        <label className="toggle-switch">
          <input
            type="checkbox"
            checked={currentSettings.accessibility.highContrast}
            onChange={(e) => handleSettingChange('accessibility', 'highContrast', e.target.checked)}
          />
          <span className="toggle-slider" />
        </label>
      </div>

      <div className="setting-item">
        <div className="setting-info">
          <h4>큰 글씨</h4>
          <p>텍스트 크기를 크게 표시합니다</p>
        </div>
        <label className="toggle-switch">
          <input
            type="checkbox"
            checked={currentSettings.accessibility.largeText}
            onChange={(e) => handleSettingChange('accessibility', 'largeText', e.target.checked)}
          />
          <span className="toggle-slider" />
        </label>
      </div>

      <div className="setting-item">
        <div className="setting-info">
          <h4>모션 감소</h4>
          <p>애니메이션 효과를 줄입니다</p>
        </div>
        <label className="toggle-switch">
          <input
            type="checkbox"
            checked={currentSettings.accessibility.reducedMotion}
            onChange={(e) => handleSettingChange('accessibility', 'reducedMotion', e.target.checked)}
          />
          <span className="toggle-slider" />
        </label>
      </div>
    </div>
  );

  return (
    <div className="personalization-modal">
      <div className="modal-header">
        <h2>개인화 설정</h2>
        <button className="close-button" onClick={onClose}>×</button>
      </div>

      <div className="modal-tabs">
        <button
          className={`tab-button ${activeTab === 'notifications' ? 'active' : ''}`}
          onClick={() => setActiveTab('notifications')}
        >
          ⏰ 알림
        </button>
        <button
          className={`tab-button ${activeTab === 'preferences' ? 'active' : ''}`}
          onClick={() => setActiveTab('preferences')}
        >
          ⚙️ 선호도
        </button>
        <button
          className={`tab-button ${activeTab === 'accessibility' ? 'active' : ''}`}
          onClick={() => setActiveTab('accessibility')}
        >
          ♿ 접근성
        </button>
      </div>

      <div className="modal-content">
        {activeTab === 'notifications' && renderNotificationsTab()}
        {activeTab === 'preferences' && renderPreferencesTab()}
        {activeTab === 'accessibility' && renderAccessibilityTab()}
      </div>

      <div className="modal-footer">
        <button className="btn-secondary" onClick={onClose}>
          취소
        </button>
        <button className="btn-primary" onClick={handleSave}>
          저장
        </button>
      </div>
    </div>
  );
};

export default PersonalizationSettings;
