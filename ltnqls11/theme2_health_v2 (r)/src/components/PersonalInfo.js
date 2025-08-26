import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ProgressHeader from './common/ProgressHeader';
import './PersonalInfo.css';

const PersonalInfo = ({ sessionState, updateSessionState, onNavigate, progress }) => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: sessionState.userData.email || '',
    age: sessionState.userData.age || 30,
    gender: sessionState.userData.gender || '남성',
    workExperience: sessionState.userData.workExperience || 3,
    dailyWorkHours: sessionState.userData.dailyWorkHours || 8,
    workIntensity: sessionState.userData.workIntensity || '보통',
    exerciseHabit: sessionState.userData.exerciseHabit || '전혀 안함',
    smoking: sessionState.userData.smoking || '비흡연',
    drinking: sessionState.userData.drinking || '안함',
    sleepHours: sessionState.userData.sleepHours || 7
  });

  const [customerHistory, setCustomerHistory] = useState(null);

  // 이메일 변경 시 고객 이력 확인 (시뮬레이션)
  useEffect(() => {
    if (formData.email && formData.email.includes('@')) {
      // 실제 구현에서는 API 호출
      const isReturningCustomer = Math.random() > 0.7; // 30% 확률로 재방문 고객
      
      if (isReturningCustomer) {
        setCustomerHistory({
          isReturnCustomer: true,
          visitCount: Math.floor(Math.random() * 5) + 2,
          previousVisit: {
            date: '2024-01-15',
            conditions: ['거북목', '라운드숄더'],
            painScores: { '거북목': 6, '라운드숄더': 4 }
          }
        });
      } else {
        setCustomerHistory({
          isReturnCustomer: false,
          visitCount: 1
        });
      }
    }
  }, [formData.email]);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleNext = () => {
    console.log('PersonalInfo handleNext 시작');
    
    // 유효성 검사
    if (!formData.email || !formData.email.includes('@')) {
      alert('올바른 이메일 주소를 입력해주세요.');
      return;
    }

    try {
      // 세션 상태 업데이트
      const updatedUserData = {
        ...sessionState.userData,
        ...formData,
        customerHistory: customerHistory
      };

      const updatedStepsCompleted = [...sessionState.stepsCompleted];
      updatedStepsCompleted[1] = true;

      const newSessionState = {
        ...sessionState,
        userData: updatedUserData,
        stepsCompleted: updatedStepsCompleted,
        currentStep: 2
      };

      console.log('PersonalInfo 업데이트할 세션 상태:', newSessionState);
      
      // 상태 업데이트
      updateSessionState(newSessionState);

      // 약간의 지연 후 네비게이션
      setTimeout(() => {
        onNavigate("작업환경 평가");
        navigate('/work-environment');
      }, 100);

    } catch (error) {
      console.error('PersonalInfo handleNext 오류:', error);
      alert('저장 중 오류가 발생했습니다. 다시 시도해주세요.');
    }
  };

  const isFormValid = formData.email && formData.email.includes('@');

  if (!sessionState.selectedConditions || sessionState.selectedConditions.length === 0) {
    return (
      <div className="personal-info">
        <div className="alert alert-warning">
          먼저 증상을 선택해주세요.
        </div>
      </div>
    );
  }

  return (
    <div className="personal-info">
      <div className="page-header">
        <h1 className="page-title">개인정보 입력</h1>
      </div>

      <ProgressHeader progress={progress} />

      <hr className="section-divider" />

      <section className="email-section">
        <h2>📧 이메일 주소</h2>
        <div className="form-group">
          <input
            type="email"
            className="form-control"
            placeholder="example@gmail.com"
            value={formData.email}
            onChange={(e) => handleInputChange('email', e.target.value)}
          />
        </div>

        {customerHistory && (
          <div className="customer-history">
            {customerHistory.isReturnCustomer ? (
              <div className="alert alert-success">
                👋 다시 방문해주셨군요! (총 {customerHistory.visitCount}번째 방문)
              </div>
            ) : (
              <div className="alert alert-info">
                🆕 처음 방문해주셨네요! 환영합니다.
              </div>
            )}

            {customerHistory.isReturnCustomer && customerHistory.previousVisit && (
              <div className="previous-visit-info">
                <h3>📊 이전 방문 정보</h3>
                <div className="visit-details">
                  <p><strong>마지막 방문:</strong> {customerHistory.previousVisit.date}</p>
                  <p><strong>이전 증상:</strong> {customerHistory.previousVisit.conditions.join(', ')}</p>
                  <div className="previous-pain-scores">
                    <strong>이전 통증 점수:</strong>
                    <ul>
                      {Object.entries(customerHistory.previousVisit.painScores).map(([condition, score]) => (
                        <li key={condition}>{condition}: {score}점</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </section>

      <hr className="section-divider" />

      <section className="personal-details">
        <div className="form-grid">
          <div className="form-column">
            <div className="form-group">
              <label className="form-label">나이</label>
              <input
                type="number"
                className="form-control"
                min="20"
                max="70"
                value={formData.age}
                onChange={(e) => handleInputChange('age', parseInt(e.target.value))}
              />
            </div>

            <div className="form-group">
              <label className="form-label">성별</label>
              <select
                className="form-control"
                value={formData.gender}
                onChange={(e) => handleInputChange('gender', e.target.value)}
              >
                <option value="남성">남성</option>
                <option value="여성">여성</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">개발 경력 (년)</label>
              <input
                type="number"
                className="form-control"
                min="0"
                max="30"
                value={formData.workExperience}
                onChange={(e) => handleInputChange('workExperience', parseInt(e.target.value))}
              />
            </div>

            <div className="form-group">
              <label className="form-label">일일 컴퓨터 작업시간: {formData.dailyWorkHours}시간</label>
              <input
                type="range"
                className="slider"
                min="4"
                max="16"
                value={formData.dailyWorkHours}
                onChange={(e) => handleInputChange('dailyWorkHours', parseInt(e.target.value))}
              />
            </div>

            <div className="form-group">
              <label className="form-label">작업 강도</label>
              <select
                className="form-control"
                value={formData.workIntensity}
                onChange={(e) => handleInputChange('workIntensity', e.target.value)}
              >
                <option value="가벼움">가벼움</option>
                <option value="보통">보통</option>
                <option value="높음">높음</option>
                <option value="매우 높음">매우 높음</option>
              </select>
            </div>
          </div>

          <div className="form-column">
            <div className="form-group">
              <label className="form-label">운동 습관</label>
              <select
                className="form-control"
                value={formData.exerciseHabit}
                onChange={(e) => handleInputChange('exerciseHabit', e.target.value)}
              >
                <option value="전혀 안함">전혀 안함</option>
                <option value="주 1-2회">주 1-2회</option>
                <option value="주 3-4회">주 3-4회</option>
                <option value="주 5회 이상">주 5회 이상</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">흡연</label>
              <select
                className="form-control"
                value={formData.smoking}
                onChange={(e) => handleInputChange('smoking', e.target.value)}
              >
                <option value="비흡연">비흡연</option>
                <option value="과거 흡연">과거 흡연</option>
                <option value="현재 흡연">현재 흡연</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">음주</label>
              <select
                className="form-control"
                value={formData.drinking}
                onChange={(e) => handleInputChange('drinking', e.target.value)}
              >
                <option value="안함">안함</option>
                <option value="주 1-2회">주 1-2회</option>
                <option value="주 3-4회">주 3-4회</option>
                <option value="거의 매일">거의 매일</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">평균 수면시간: {formData.sleepHours}시간</label>
              <input
                type="range"
                className="slider"
                min="4"
                max="12"
                value={formData.sleepHours}
                onChange={(e) => handleInputChange('sleepHours', parseInt(e.target.value))}
              />
            </div>
          </div>
        </div>
      </section>

      <div className="form-actions">
        {isFormValid ? (
          <button 
            className="btn btn-primary"
            onClick={handleNext}
          >
            ✅ 저장하고 다음 단계로
          </button>
        ) : (
          <div className="alert alert-warning">
            ⚠️ 이메일 주소를 올바르게 입력해주세요.
          </div>
        )}
      </div>
    </div>
  );
};

export default PersonalInfo;