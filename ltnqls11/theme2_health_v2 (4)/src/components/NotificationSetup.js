import React, { useState } from 'react';
import ProgressHeader from './common/ProgressHeader';
import './NotificationSetup.css';

const NotificationSetup = ({ sessionState, updateSessionState, onNavigate, progress }) => {
  const [notificationConfig, setNotificationConfig] = useState({
    type: '이메일 (Gmail)',
    slackWebhook: '',
    workStart: '09:00',
    workEnd: '18:00',
    customInterval: calculateRestTime(sessionState.userData?.workIntensity || '보통')
  });

  const [testResults, setTestResults] = useState({
    email: null,
    slack: null
  });

  function calculateRestTime(workIntensity) {
    const intensityMap = {
      "가벼움": 30,
      "보통": 25,
      "높음": 20,
      "매우 높음": 15
    };
    return intensityMap[workIntensity] || 25;
  }

  const handleInputChange = (field, value) => {
    setNotificationConfig(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleTestEmail = async () => {
    // 이메일 테스트 시뮬레이션
    setTestResults(prev => ({ ...prev, email: 'testing' }));
    
    setTimeout(() => {
      const success = Math.random() > 0.3; // 70% 성공률
      setTestResults(prev => ({ 
        ...prev, 
        email: success ? 'success' : 'failed' 
      }));
    }, 2000);
  };

  const handleTestSlack = async () => {
    if (!notificationConfig.slackWebhook) {
      setTestResults(prev => ({ ...prev, slack: 'failed' }));
      return;
    }

    // Slack 테스트 시뮬레이션
    setTestResults(prev => ({ ...prev, slack: 'testing' }));
    
    setTimeout(() => {
      const success = Math.random() > 0.2; // 80% 성공률
      setTestResults(prev => ({ 
        ...prev, 
        slack: success ? 'success' : 'failed' 
      }));
    }, 1500);
  };

  const handleActivateNotifications = () => {
    const config = {
      ...notificationConfig,
      email: sessionState.userData.email,
      userData: sessionState.userData,
      conditions: sessionState.selectedConditions,
      painScores: sessionState.userData.painScores,
      createdAt: new Date().toISOString()
    };

    // 세션 상태 업데이트
    const updatedStepsCompleted = [...sessionState.stepsCompleted];
    updatedStepsCompleted[5] = true;

    updateSessionState({
      stepsCompleted: updatedStepsCompleted,
      notificationConfig: config
    });

    // 로컬 스토리지에 설정 저장 (실제 구현에서는 서버로 전송)
    localStorage.setItem('vdt_notification_config', JSON.stringify(config));
  };

  const userEmail = sessionState.userData?.email;
  const workIntensity = sessionState.userData?.workIntensity || '보통';
  const recommendedInterval = calculateRestTime(workIntensity);

  if (!userEmail) {
    return (
      <div className="notification-setup">
        <div className="page-header">
          <h1 className="page-title">휴식 알리미 설정</h1>
        </div>
        <div className="alert alert-warning">
          📧 이메일 주소가 입력되지 않았습니다. '개인정보 입력' 단계에서 이메일을 입력해주세요.
        </div>
        <div className="alert alert-info">
          💡 이메일 주소는 운동 알림을 받기 위해 필요합니다.
        </div>
      </div>
    );
  }

  return (
    <div className="notification-setup">
      <div className="page-header">
        <h1 className="page-title">휴식 알리미 설정</h1>
      </div>

      <ProgressHeader progress={progress} />

      <hr className="section-divider" />

      <section className="email-info">
        <div className="alert alert-info">
          📧 설정된 이메일: <strong>{userEmail}</strong>
        </div>
      </section>

      <section className="notification-type">
        <h2>📱 알림 방식 선택</h2>
        <div className="form-group">
          <label className="form-label">알림 방식</label>
          <select
            className="form-control"
            value={notificationConfig.type}
            onChange={(e) => handleInputChange('type', e.target.value)}
          >
            <option value="이메일 (Gmail)">이메일 (Gmail)</option>
            <option value="Slack">Slack</option>
            <option value="둘 다">둘 다</option>
          </select>
        </div>

        {(notificationConfig.type === 'Slack' || notificationConfig.type === '둘 다') && (
          <div className="slack-config">
            <h3>💬 Slack 설정</h3>
            <div className="form-group">
              <label className="form-label">Slack Webhook URL</label>
              <input
                type="url"
                className="form-control"
                placeholder="https://hooks.slack.com/services/..."
                value={notificationConfig.slackWebhook}
                onChange={(e) => handleInputChange('slackWebhook', e.target.value)}
              />
            </div>
            
            <div className="test-section">
              <button 
                className="btn btn-secondary"
                onClick={handleTestSlack}
                disabled={testResults.slack === 'testing'}
              >
                {testResults.slack === 'testing' ? '테스트 중...' : '🧪 Slack 테스트'}
              </button>
              
              {testResults.slack === 'success' && (
                <div className="alert alert-success">✅ Slack 알림 테스트 성공!</div>
              )}
              {testResults.slack === 'failed' && (
                <div className="alert alert-error">❌ Slack 알림 테스트 실패</div>
              )}
            </div>
          </div>
        )}

        {(notificationConfig.type === '이메일 (Gmail)' || notificationConfig.type === '둘 다') && (
          <div className="email-config">
            <h3>📧 이메일 설정</h3>
            <div className="alert alert-info">
              Gmail 알림이 {userEmail}로 전송됩니다.
            </div>
            
            <div className="test-section">
              <button 
                className="btn btn-secondary"
                onClick={handleTestEmail}
                disabled={testResults.email === 'testing'}
              >
                {testResults.email === 'testing' ? '테스트 중...' : '🧪 이메일 테스트'}
              </button>
              
              {testResults.email === 'success' && (
                <div className="alert alert-success">✅ 이메일 알림 테스트 성공!</div>
              )}
              {testResults.email === 'failed' && (
                <div className="alert alert-error">❌ 이메일 알림 테스트 실패</div>
              )}
            </div>
          </div>
        )}
      </section>

      <hr className="section-divider" />

      <section className="work-schedule">
        <h2>⏰ 근무 시간 및 휴식 설정</h2>
        
        <div className="schedule-grid">
          <div className="form-group">
            <label className="form-label">업무 시작 시간</label>
            <input
              type="time"
              className="form-control"
              value={notificationConfig.workStart}
              onChange={(e) => handleInputChange('workStart', e.target.value)}
            />
          </div>

          <div className="form-group">
            <label className="form-label">업무 종료 시간</label>
            <input
              type="time"
              className="form-control"
              value={notificationConfig.workEnd}
              onChange={(e) => handleInputChange('workEnd', e.target.value)}
            />
          </div>
        </div>

        <div className="rest-interval-section">
          <div className="alert alert-info">
            🎯 권장 휴식 간격: {recommendedInterval}분 (작업 강도: {workIntensity})
          </div>
          
          <div className="form-group">
            <label className="form-label">
              휴식 간격 조정: {notificationConfig.customInterval}분
            </label>
            <input
              type="range"
              className="slider"
              min="15"
              max="120"
              step="5"
              value={notificationConfig.customInterval}
              onChange={(e) => handleInputChange('customInterval', parseInt(e.target.value))}
            />
            <div className="slider-labels">
              <span>15분</span>
              <span>60분</span>
              <span>120분</span>
            </div>
          </div>
        </div>
      </section>

      <hr className="section-divider" />

      <section className="notification-preview">
        <h2>📋 알림 미리보기</h2>
        <div className="preview-card">
          <h4>설정 요약</h4>
          <div className="preview-content">
            <p><strong>📧 받는 사람:</strong> {userEmail}</p>
            <p><strong>⏰ 알림 시간:</strong> {notificationConfig.workStart} ~ {notificationConfig.workEnd}</p>
            <p><strong>🔄 알림 간격:</strong> {notificationConfig.customInterval}분마다</p>
            <p><strong>📱 알림 방식:</strong> {notificationConfig.type}</p>
            <p><strong>💡 알림 내용:</strong> 개인 맞춤 운동 루틴 및 스트레칭 가이드</p>
          </div>
        </div>

        <div className="sample-notification">
          <h4>📬 알림 예시</h4>
          <div className="notification-sample">
            <div className="notification-header">
              <strong>🏃‍♂️ VDT 관리 시스템 - 휴식 알리미</strong>
            </div>
            <div className="notification-body">
              <p>안녕하세요! 휴식 시간입니다. 💪</p>
              <p><strong>추천 운동:</strong></p>
              <ul>
                {sessionState.selectedConditions?.map(condition => (
                  <li key={condition}>{condition} 맞춤 스트레칭 (2분)</li>
                ))}
              </ul>
              <p>건강한 개발 생활을 응원합니다!</p>
            </div>
          </div>
        </div>
      </section>

      <div className="form-actions">
        <button 
          className="btn btn-primary btn-large"
          onClick={handleActivateNotifications}
        >
          🚀 알리미 활성화
        </button>
      </div>

      {sessionState.stepsCompleted?.[5] && (
        <div className="completion-section">
          <div className="alert alert-success">
            🎉 <strong>모든 설정이 완료되었습니다!</strong>
          </div>
          <div className="completion-actions">
            <button 
              className="btn btn-primary"
              onClick={() => {
                onNavigate("운동 관리");
                window.location.href = '/exercise-management';
              }}
            >
              📊 운동기록 확인하기
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationSetup;