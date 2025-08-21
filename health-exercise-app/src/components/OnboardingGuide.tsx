import React, { useState, useEffect } from 'react';
import './OnboardingGuide.css';

interface OnboardingGuideProps {
  isVisible: boolean;
  onComplete: () => void;
  onSkip: () => void;
}

interface OnboardingStep {
  id: number;
  title: string;
  description: string;
  image: string;
  position: 'top' | 'center' | 'bottom';
  target?: string;
}

const OnboardingGuide: React.FC<OnboardingGuideProps> = ({ isVisible, onComplete, onSkip }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);

  const onboardingSteps: OnboardingStep[] = [
    {
      id: 1,
      title: '건강 정보 입력',
      description: '증상과 작업 환경을 알려주시면 맞춤 운동을 추천해드려요',
      image: '📝',
      position: 'center'
    },
    {
      id: 2,
      title: '맞춤 운동 추천',
      description: 'AI가 분석한 개인 맞춤 운동 루틴을 확인하세요',
      image: '💪',
      position: 'center'
    },
    {
      id: 3,
      title: '운동 비디오 시청',
      description: 'YouTube 기반 검증된 운동 비디오로 정확한 동작을 배우세요',
      image: '🎬',
      position: 'center'
    },
    {
      id: 4,
      title: '스마트 알림',
      description: '휴식 시간과 운동 알림으로 건강한 습관을 만들어보세요',
      image: '⏰',
      position: 'center'
    },
    {
      id: 5,
      title: '진행 상황 추적',
      description: '운동 진행률과 목표 달성 현황을 한눈에 확인하세요',
      image: '📊',
      position: 'center'
    }
  ];

  useEffect(() => {
    if (isVisible) {
      setIsAnimating(true);
      setTimeout(() => setIsAnimating(false), 300);
    }
  }, [isVisible, currentStep]);

  const nextStep = () => {
    if (currentStep < onboardingSteps.length - 1) {
      setIsAnimating(true);
      setTimeout(() => {
        setCurrentStep(currentStep + 1);
        setIsAnimating(false);
      }, 150);
    } else {
      onComplete();
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setIsAnimating(true);
      setTimeout(() => {
        setCurrentStep(currentStep - 1);
        setIsAnimating(false);
      }, 150);
    }
  };

  const handleSkip = () => {
    onSkip();
  };

  if (!isVisible) return null;

  const currentStepData = onboardingSteps[currentStep];
  const progress = ((currentStep + 1) / onboardingSteps.length) * 100;

  return (
    <div className="onboarding-overlay">
      <div className="onboarding-backdrop" onClick={handleSkip} />
      
      <div className={`onboarding-modal ${isAnimating ? 'animating' : ''}`}>
        {/* 진행률 바 */}
        <div className="onboarding-progress">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${progress}%` }}
            />
          </div>
          <span className="progress-text">
            {currentStep + 1} / {onboardingSteps.length}
          </span>
        </div>

        {/* 스킵 버튼 */}
        <button className="skip-button" onClick={handleSkip}>
          건너뛰기
        </button>

        {/* 메인 콘텐츠 */}
        <div className="onboarding-content">
          <div className="step-image">
            <span className="step-emoji">{currentStepData.image}</span>
          </div>
          
          <h2 className="step-title">{currentStepData.title}</h2>
          <p className="step-description">{currentStepData.description}</p>
        </div>

        {/* 네비게이션 */}
        <div className="onboarding-navigation">
          <button 
            className={`nav-button prev ${currentStep === 0 ? 'disabled' : ''}`}
            onClick={prevStep}
            disabled={currentStep === 0}
          >
            이전
          </button>
          
          <div className="step-indicators">
            {onboardingSteps.map((_, index) => (
              <button
                key={index}
                className={`step-dot ${index === currentStep ? 'active' : ''}`}
                onClick={() => setCurrentStep(index)}
              />
            ))}
          </div>
          
          <button 
            className="nav-button next"
            onClick={nextStep}
          >
            {currentStep === onboardingSteps.length - 1 ? '시작하기' : '다음'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default OnboardingGuide;
