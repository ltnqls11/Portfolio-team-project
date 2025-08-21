import React, { useState } from 'react';
import { UserInfo } from './types';
import UserInfoForm from './components/UserInfoForm';
import ExerciseRecommendation from './components/ExerciseRecommendation';
import './App.css';

function App() {
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [currentStep, setCurrentStep] = useState<'form' | 'recommendation'>('form');

  const handleUserInfoSubmit = (info: UserInfo) => {
    setUserInfo(info);
    setCurrentStep('recommendation');
  };

  const handleBackToForm = () => {
    setCurrentStep('form');
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🏥 건강 관리 운동 추천</h1>
        <p>개인 맞춤형 운동 루틴과 건강 관리 가이드를 제공합니다</p>
      </header>

      <main className="App-main">
        {currentStep === 'form' ? (
          <UserInfoForm onSubmit={handleUserInfoSubmit} />
        ) : (
          userInfo && (
            <ExerciseRecommendation 
              userInfo={userInfo} 
              onBack={handleBackToForm} 
            />
          )
        )}
      </main>

      <footer className="App-footer">
        <p>&copy; 2024 건강 관리 운동 추천 앱. 건강한 하루 되세요! 💪</p>
      </footer>
    </div>
  );
}

export default App;
