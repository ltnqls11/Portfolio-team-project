import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Home from './components/Home';
import ConditionSelection from './components/ConditionSelection';
import PersonalInfo from './components/PersonalInfo';
import WorkEnvironment from './components/WorkEnvironment';
import ExerciseSurvey from './components/ExerciseSurvey';
import ExerciseRecommendation from './components/ExerciseRecommendation';
import NotificationSetup from './components/NotificationSetup';
import ExerciseManagement from './components/ExerciseManagement';
import './App.css';

// 라우트 변경 감지를 위한 컴포넌트
function RouteChangeHandler({ onRouteChange }) {
  const location = useLocation();
  
  useEffect(() => {
    onRouteChange(location.pathname);
  }, [location, onRouteChange]);
  
  return null;
}

function App() {
  // localStorage에서 세션 상태 복원
  const getInitialSessionState = () => {
    try {
      const savedState = localStorage.getItem('vdt_session_state');
      if (savedState) {
        return JSON.parse(savedState);
      }
    } catch (error) {
      console.error('세션 상태 복원 실패:', error);
    }
    
    // 기본 상태 반환
    return {
      userData: {},
      selectedConditions: [],
      assessmentComplete: false,
      currentStep: 0,
      stepsCompleted: [false, false, false, false, false, false],
      exerciseSchedule: {},
      subjectiveStatus: "",
      menuSelection: "홈",
      nextMenu: null,
      userId: `user_${new Date().toISOString().replace(/[:.]/g, '_')}`
    };
  };

  // 세션 상태 관리 (Streamlit의 st.session_state와 동일한 역할)
  const [sessionState, setSessionState] = useState(getInitialSessionState());

  const [currentMenu, setCurrentMenu] = useState("홈");

  // 메뉴 옵션들
  const menuOptions = [
    "홈", 
    "증상 선택", 
    "개인정보 입력", 
    "작업환경 평가", 
    "개인 운동 설문", 
    "운동 추천", 
    "휴식 알리미 설정", 
    "운동 관리"
  ];

  // 세션 상태 업데이트 함수
  const updateSessionState = (updates) => {
    const newState = {
      ...sessionState,
      ...updates
    };
    setSessionState(newState);
    
    // localStorage에 상태 저장
    try {
      localStorage.setItem('vdt_session_state', JSON.stringify(newState));
      console.log('세션 상태 저장됨:', newState);
    } catch (error) {
      console.error('세션 상태 저장 실패:', error);
    }
  };

  // 다음 메뉴로 이동
  const navigateToMenu = (menu) => {
    console.log('메뉴 이동:', menu);
    setCurrentMenu(menu);
    updateSessionState({ menuSelection: menu });
    
    // 메뉴에 따른 라우팅 처리
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
    
    if (menuRoutes[menu]) {
      window.history.pushState(null, '', menuRoutes[menu]);
    }
  };

  // 라우트 변경 시 메뉴 상태 업데이트
  const handleRouteChange = (pathname) => {
    const routeToMenu = {
      "/home": "홈",
      "/condition-selection": "증상 선택",
      "/personal-info": "개인정보 입력",
      "/work-environment": "작업환경 평가",
      "/exercise-survey": "개인 운동 설문",
      "/exercise-recommendation": "운동 추천",
      "/notification-setup": "휴식 알리미 설정",
      "/exercise-management": "운동 관리"
    };
    
    if (routeToMenu[pathname]) {
      setCurrentMenu(routeToMenu[pathname]);
      updateSessionState({ menuSelection: routeToMenu[pathname] });
    }
  };

  // 진행률 계산
  const getProgress = () => {
    const completedSteps = sessionState.stepsCompleted.slice(0, 6).filter(Boolean).length;
    return {
      completed: completedSteps,
      total: 6,
      percentage: (completedSteps / 6) * 100
    };
  };

  // 시스템 상태 확인
  const getSystemStatus = () => {
    return {
      youtubeSearch: true, // 시뮬레이션으로 활성화
      aiRecommendation: true, // 시뮬레이션으로 활성화
      dataStorage: true, // 로컬 스토리지 사용으로 활성화
      adsRecommendation: true // 광고 기능 활성화
    };
  };

  return (
    <Router>
      <div className="app">
        <RouteChangeHandler onRouteChange={handleRouteChange} />
        <Sidebar 
          currentMenu={currentMenu}
          menuOptions={menuOptions}
          onMenuSelect={navigateToMenu}
          progress={getProgress()}
          systemStatus={getSystemStatus()}
        />
        
        <main className="main-content">
          <div className="container">
            <Routes>
              <Route path="/" element={<Navigate to="/home" replace />} />
              <Route 
                path="/home" 
                element={
                  <Home 
                    onNavigate={navigateToMenu}
                  />
                } 
              />
              <Route 
                path="/condition-selection" 
                element={
                  <ConditionSelection 
                    sessionState={sessionState}
                    updateSessionState={updateSessionState}
                    onNavigate={navigateToMenu}
                    progress={getProgress()}
                  />
                } 
              />
              <Route 
                path="/personal-info" 
                element={
                  <PersonalInfo 
                    sessionState={sessionState}
                    updateSessionState={updateSessionState}
                    onNavigate={navigateToMenu}
                    progress={getProgress()}
                  />
                } 
              />
              <Route 
                path="/work-environment" 
                element={
                  <WorkEnvironment 
                    sessionState={sessionState}
                    updateSessionState={updateSessionState}
                    onNavigate={navigateToMenu}
                    progress={getProgress()}
                  />
                } 
              />
              <Route 
                path="/exercise-survey" 
                element={
                  <ExerciseSurvey 
                    sessionState={sessionState}
                    updateSessionState={updateSessionState}
                    onNavigate={navigateToMenu}
                    progress={getProgress()}
                  />
                } 
              />
              <Route 
                path="/exercise-recommendation" 
                element={
                  <ExerciseRecommendation 
                    sessionState={sessionState}
                    updateSessionState={updateSessionState}
                    onNavigate={navigateToMenu}
                    progress={getProgress()}
                  />
                } 
              />
              <Route 
                path="/notification-setup" 
                element={
                  <NotificationSetup 
                    sessionState={sessionState}
                    updateSessionState={updateSessionState}
                    onNavigate={navigateToMenu}
                    progress={getProgress()}
                  />
                } 
              />
              <Route 
                path="/exercise-management" 
                element={
                  <ExerciseManagement 
                    sessionState={sessionState}
                    updateSessionState={updateSessionState}
                  />
                } 
              />
            </Routes>
          </div>
        </main>
      </div>
    </Router>
  );
}

export default App;