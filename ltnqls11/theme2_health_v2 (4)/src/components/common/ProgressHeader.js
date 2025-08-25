import React from 'react';
import './ProgressHeader.css';

const ProgressHeader = ({ progress }) => {
  const steps = [
    "증상 선택", 
    "개인정보 입력", 
    "작업환경 평가", 
    "개인 운동 설문", 
    "운동 추천", 
    "휴식 알리미 설정"
  ];

  return (
    <div className="progress-header-section">
      <h3 className="progress-title">진행 상황</h3>
      
      <div className="progress-container">
        <div className="progress-bar-container">
          <div className="progress">
            <div 
              className="progress-bar" 
              style={{ width: `${progress.percentage}%` }}
            ></div>
          </div>
        </div>
        
        <div className="progress-stats">
          <div className="progress-stat">
            <div className="progress-stat-value">{progress.completed}/{progress.total}</div>
            <div className="progress-stat-label">완료 단계</div>
          </div>
          
          <div className="progress-stat">
            <div className="progress-stat-value">{Math.round(progress.percentage)}%</div>
            <div className="progress-stat-label">진행률</div>
          </div>
        </div>
      </div>

      <div className="steps-indicator">
        {steps.map((step, index) => (
          <div 
            key={step} 
            className={`step-item ${index < progress.completed ? 'completed' : ''} ${index === progress.completed ? 'current' : ''}`}
          >
            <div className="step-number">
              {index < progress.completed ? '✓' : index + 1}
            </div>
            <div className="step-label">{step}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProgressHeader;