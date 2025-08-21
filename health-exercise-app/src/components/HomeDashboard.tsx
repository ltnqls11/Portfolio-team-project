import React from 'react';
import { UserInfo, ProgressData } from '../types';
import './HomeDashboard.css';

interface HomeDashboardProps {
  userInfo?: UserInfo;
  progressData?: ProgressData;
  onGetStarted: () => void;
}

const HomeDashboard: React.FC<HomeDashboardProps> = ({ userInfo, progressData, onGetStarted }) => {
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return '좋은 아침입니다!';
    if (hour < 18) return '좋은 오후입니다!';
    return '좋은 저녁입니다!';
  };

  const getMotivationalMessage = () => {
    const messages = [
      '작은 움직임이 큰 변화를 만듭니다 💪',
      '오늘도 건강한 하루를 시작해보세요 🌟',
      '꾸준함이 가장 큰 힘입니다 ✨',
      '당신의 건강을 위한 첫 걸음을 시작하세요 🚀'
    ];
    return messages[Math.floor(Math.random() * messages.length)];
  };

  return (
    <div className="home-dashboard">
      <div className="welcome-section">
        <h1 className="greeting">{getGreeting()}</h1>
        <p className="motivational-message">{getMotivationalMessage()}</p>
      </div>

      {!userInfo ? (
        <div className="get-started-section">
          <div className="welcome-card">
            <div className="card-icon">🏥</div>
            <h2>건강 관리 운동 추천</h2>
            <p>개인 맞춤형 운동 루틴과 건강 관리 가이드를 제공합니다</p>
            <button className="get-started-btn" onClick={onGetStarted}>
              시작하기
            </button>
          </div>

          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🎯</div>
              <h3>맞춤 운동 추천</h3>
              <p>증상과 작업 환경에 맞는 개인화된 운동 루틴</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🎬</div>
              <h3>운동 비디오</h3>
              <p>YouTube 기반 검증된 운동 비디오 추천</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">⏰</div>
              <h3>스마트 알림</h3>
              <p>휴식 시간과 운동 알림으로 건강한 습관 형성</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📊</div>
              <h3>진행 상황 추적</h3>
              <p>운동 진행 상황과 목표 달성 현황 확인</p>
            </div>
          </div>
        </div>
      ) : (
        <div className="user-dashboard">
          <div className="quick-stats">
            <div className="stat-card">
              <div className="stat-icon">💪</div>
              <div className="stat-content">
                <h3>오늘의 운동</h3>
                <p className="stat-value">{progressData?.completedExercises || 0} / {progressData?.totalExercises || 0}</p>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">🔥</div>
              <div className="stat-content">
                <h3>연속 운동</h3>
                <p className="stat-value">{progressData?.streak || 0}일</p>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">📈</div>
              <div className="stat-content">
                <h3>주간 목표</h3>
                <p className="stat-value">{progressData?.weeklyCompleted || 0} / {progressData?.weeklyGoal || 5}</p>
              </div>
            </div>
          </div>

          <div className="quick-actions">
            <h2>빠른 액션</h2>
            <div className="action-buttons">
              <button className="action-btn primary">
                <span className="action-icon">💪</span>
                오늘의 운동 시작
              </button>
              <button className="action-btn secondary">
                <span className="action-icon">📝</span>
                건강 정보 수정
              </button>
              <button className="action-btn secondary">
                <span className="action-icon">🎬</span>
                운동 비디오 보기
              </button>
            </div>
          </div>

          <div className="health-tips">
            <h2>오늘의 건강 팁</h2>
            <div className="tip-card">
              <div className="tip-icon">💡</div>
              <div className="tip-content">
                <h3>올바른 자세 유지하기</h3>
                <p>장시간 앉아있을 때는 30분마다 일어나서 간단한 스트레칭을 해보세요. 목과 어깨를 돌려주는 것만으로도 큰 도움이 됩니다.</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HomeDashboard;
