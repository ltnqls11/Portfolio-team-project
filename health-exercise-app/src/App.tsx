import React, { useState, useEffect } from 'react';
import { UserInfo, TabType, ProgressData } from './types';
import TabNavigation from './components/TabNavigation';
import HomeDashboard from './components/HomeDashboard';
import UserInfoForm from './components/UserInfoForm';
import ExerciseRecommendation from './components/ExerciseRecommendation';
import './App.css';

function App() {
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [activeTab, setActiveTab] = useState<TabType>('home');
  const [progressData, setProgressData] = useState<ProgressData>({
    completedExercises: 0,
    totalExercises: 0,
    streak: 0,
    lastExerciseDate: '',
    weeklyGoal: 5,
    weeklyCompleted: 0
  });

  // 로컬 스토리지에서 사용자 정보 불러오기
  useEffect(() => {
    const savedUserInfo = localStorage.getItem('userInfo');
    if (savedUserInfo) {
      setUserInfo(JSON.parse(savedUserInfo));
    }

    const savedProgress = localStorage.getItem('progressData');
    if (savedProgress) {
      setProgressData(JSON.parse(savedProgress));
    }
  }, []);

  // 사용자 정보 저장
  const saveUserInfo = (info: UserInfo) => {
    setUserInfo(info);
    localStorage.setItem('userInfo', JSON.stringify(info));
    setActiveTab('recommendation');
  };

  // 진행 상황 저장
  const saveProgressData = (progress: ProgressData) => {
    setProgressData(progress);
    localStorage.setItem('progressData', JSON.stringify(progress));
  };

  // 탭 변경 핸들러
  const handleTabChange = (tab: TabType) => {
    setActiveTab(tab);
  };

  // 시작하기 버튼 핸들러
  const handleGetStarted = () => {
    setActiveTab('input');
  };

  // 현재 탭에 따른 컴포넌트 렌더링
  const renderCurrentTab = () => {
    switch (activeTab) {
      case 'home':
        return (
          <HomeDashboard
            userInfo={userInfo}
            progressData={progressData}
            onGetStarted={handleGetStarted}
          />
        );
      case 'input':
        return (
          <UserInfoForm
            onSubmit={saveUserInfo}
            initialData={userInfo || undefined}
          />
        );
      case 'recommendation':
        return userInfo ? (
          <ExerciseRecommendation
            userInfo={userInfo}
            onBack={() => setActiveTab('home')}
          />
        ) : (
          <div className="no-data-message">
            <h2>건강 정보를 먼저 입력해주세요</h2>
            <p>맞춤 운동 추천을 받으려면 건강 정보를 입력해주세요.</p>
            <button onClick={() => setActiveTab('input')} className="primary-btn">
              건강 정보 입력하기
            </button>
          </div>
        );
      case 'videos':
        return userInfo ? (
          <div className="videos-tab">
            <h2>운동 비디오</h2>
            <p>YouTube 기반 운동 비디오를 확인할 수 있습니다.</p>
            {/* 비디오 컴포넌트 추가 예정 */}
          </div>
        ) : (
          <div className="no-data-message">
            <h2>건강 정보를 먼저 입력해주세요</h2>
            <p>맞춤 비디오 추천을 받으려면 건강 정보를 입력해주세요.</p>
            <button onClick={() => setActiveTab('input')} className="primary-btn">
              건강 정보 입력하기
            </button>
          </div>
        );
      case 'notifications':
        return (
          <div className="notifications-tab">
            <h2>알림 설정</h2>
            <p>휴식 시간과 운동 알림을 설정할 수 있습니다.</p>
            {/* 알림 설정 컴포넌트 추가 예정 */}
          </div>
        );
      case 'progress':
        return userInfo ? (
          <div className="progress-tab">
            <h2>진행 상황</h2>
            <p>운동 진행 상황과 목표 달성 현황을 확인할 수 있습니다.</p>
            {/* 진행 상황 컴포넌트 추가 예정 */}
          </div>
        ) : (
          <div className="no-data-message">
            <h2>건강 정보를 먼저 입력해주세요</h2>
            <p>진행 상황을 확인하려면 건강 정보를 입력해주세요.</p>
            <button onClick={() => setActiveTab('input')} className="primary-btn">
              건강 정보 입력하기
            </button>
          </div>
        );
      default:
        return <HomeDashboard userInfo={userInfo} progressData={progressData} onGetStarted={handleGetStarted} />;
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🏥 건강 관리 운동 추천</h1>
        <p>개인 맞춤형 운동 루틴과 건강 관리 가이드를 제공합니다</p>
      </header>

      <TabNavigation
        activeTab={activeTab}
        onTabChange={handleTabChange}
        userInfo={userInfo}
      />

      <main className="App-main">
        {renderCurrentTab()}
      </main>

      <footer className="App-footer">
        <p>&copy; 2024 건강 관리 운동 추천 앱. 건강한 하루 되세요! 💪</p>
      </footer>
    </div>
  );
}

export default App;
