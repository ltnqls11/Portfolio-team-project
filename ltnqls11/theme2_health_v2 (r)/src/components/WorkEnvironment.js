import React, { useState } from 'react';
import ProgressHeader from './common/ProgressHeader';
import './WorkEnvironment.css';

const WorkEnvironment = ({ sessionState, updateSessionState, onNavigate, progress }) => {
  const [formData, setFormData] = useState({
    deskHeight: sessionState.userData.deskHeight || '적절함',
    chairSupport: sessionState.userData.chairSupport || '보통',
    chairSittingStyle: sessionState.userData.chairSittingStyle || '등을 완전히 붙이고 앉음',
    monitorHeight: sessionState.userData.monitorHeight || '눈높이와 같음',
    keyboardType: sessionState.userData.keyboardType || '일반 키보드',
    mouseType: sessionState.userData.mouseType || '일반 마우스',
    monitorDistanceLevel: sessionState.userData.monitorDistanceLevel || '적당하다 (50-70cm)',
    wristRest: sessionState.userData.wristRest || '없음',
    lightingCondition: sessionState.userData.lightingCondition || '적절함'
  });

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const calculateEnvironmentScore = () => {
    let score = 0;
    
    if (formData.deskHeight === "적절함") score += 15;
    
    if (formData.chairSupport === "매우 좋음") score += 15;
    else if (formData.chairSupport === "좋음") score += 12;
    else if (formData.chairSupport === "보통") score += 8;
    
    if (formData.chairSittingStyle === "등을 완전히 붙이고 앉음") score += 15;
    
    if (formData.monitorHeight === "눈높이와 같음") score += 15;
    else if (formData.monitorHeight === "눈높이보다 낮음") score += 8;
    
    if (formData.keyboardType.includes("인체공학")) score += 10;
    else if (formData.keyboardType === "기계식") score += 8;
    
    if (formData.mouseType === "인체공학적") score += 10;
    
    if (formData.monitorDistanceLevel.startsWith("적당하다")) score += 8;
    
    if (formData.wristRest === "있음") score += 7;
    
    if (formData.lightingCondition === "적절함") score += 7;
    
    return score;
  };

  const handleNext = () => {
    const envScore = calculateEnvironmentScore();
    
    const updatedUserData = {
      ...sessionState.userData,
      ...formData,
      envScore: envScore
    };

    const updatedStepsCompleted = [...sessionState.stepsCompleted];
    updatedStepsCompleted[2] = true;

    updateSessionState({
      userData: updatedUserData,
      stepsCompleted: updatedStepsCompleted,
      currentStep: 3
    });

    onNavigate("개인 운동 설문");
    // React Router로 직접 이동
    window.location.href = '/exercise-survey';
  };

  const envScore = calculateEnvironmentScore();
  const getScoreColor = (score) => {
    if (score >= 80) return 'var(--accent-green)';
    if (score >= 60) return 'var(--accent-orange)';
    return 'var(--accent-red)';
  };

  const getScoreStatus = (score) => {
    if (score >= 80) return '우수';
    if (score >= 60) return '보통';
    return '개선 필요';
  };

  if (!sessionState.selectedConditions || sessionState.selectedConditions.length === 0) {
    return (
      <div className="work-environment">
        <div className="alert alert-warning">
          먼저 증상을 선택해주세요.
        </div>
      </div>
    );
  }

  return (
    <div className="work-environment">
      <div className="page-header">
        <h1 className="page-title">작업환경 평가</h1>
      </div>

      <ProgressHeader progress={progress} />

      <hr className="section-divider" />

      <section className="environment-assessment">
        <div className="assessment-intro">
          <h2>🖥️ 현재 작업환경을 평가해주세요</h2>
          <p>정확한 평가를 위해 현재 사용 중인 작업환경에 대해 솔직하게 답변해주세요.</p>
        </div>

        <div className="form-grid">
          <div className="form-section">
            <h3>🪑 책상 및 의자</h3>
            
            <div className="form-group">
              <label className="form-label">책상 높이</label>
              <select
                className="form-control"
                value={formData.deskHeight}
                onChange={(e) => handleInputChange('deskHeight', e.target.value)}
              >
                <option value="너무 높음">너무 높음</option>
                <option value="적절함">적절함</option>
                <option value="너무 낮음">너무 낮음</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">의자 지지력</label>
              <select
                className="form-control"
                value={formData.chairSupport}
                onChange={(e) => handleInputChange('chairSupport', e.target.value)}
              >
                <option value="매우 좋음">매우 좋음</option>
                <option value="좋음">좋음</option>
                <option value="보통">보통</option>
                <option value="나쁨">나쁨</option>
                <option value="매우 나쁨">매우 나쁨</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">앉는 자세</label>
              <select
                className="form-control"
                value={formData.chairSittingStyle}
                onChange={(e) => handleInputChange('chairSittingStyle', e.target.value)}
              >
                <option value="등을 완전히 붙이고 앉음">등을 완전히 붙이고 앉음</option>
                <option value="등받이에 기대지 않음">등받이에 기대지 않음</option>
                <option value="한쪽으로 기울어져 앉음">한쪽으로 기울어져 앉음</option>
                <option value="다리를 꼬고 앉음">다리를 꼬고 앉음</option>
              </select>
            </div>
          </div>

          <div className="form-section">
            <h3>🖥️ 모니터 및 입력장치</h3>
            
            <div className="form-group">
              <label className="form-label">모니터 높이</label>
              <select
                className="form-control"
                value={formData.monitorHeight}
                onChange={(e) => handleInputChange('monitorHeight', e.target.value)}
              >
                <option value="눈높이보다 높음">눈높이보다 높음</option>
                <option value="눈높이와 같음">눈높이와 같음</option>
                <option value="눈높이보다 낮음">눈높이보다 낮음</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">키보드 종류</label>
              <select
                className="form-control"
                value={formData.keyboardType}
                onChange={(e) => handleInputChange('keyboardType', e.target.value)}
              >
                <option value="일반 키보드">일반 키보드</option>
                <option value="기계식">기계식</option>
                <option value="인체공학적 키보드">인체공학적 키보드</option>
                <option value="무선 키보드">무선 키보드</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">마우스 종류</label>
              <select
                className="form-control"
                value={formData.mouseType}
                onChange={(e) => handleInputChange('mouseType', e.target.value)}
              >
                <option value="일반 마우스">일반 마우스</option>
                <option value="인체공학적">인체공학적</option>
                <option value="무선 마우스">무선 마우스</option>
                <option value="트랙볼">트랙볼</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">모니터와의 거리</label>
              <select
                className="form-control"
                value={formData.monitorDistanceLevel}
                onChange={(e) => handleInputChange('monitorDistanceLevel', e.target.value)}
              >
                <option value="너무 가깝다 (30cm 이하)">너무 가깝다 (30cm 이하)</option>
                <option value="적당하다 (50-70cm)">적당하다 (50-70cm)</option>
                <option value="너무 멀다 (100cm 이상)">너무 멀다 (100cm 이상)</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">손목 받침대</label>
              <select
                className="form-control"
                value={formData.wristRest}
                onChange={(e) => handleInputChange('wristRest', e.target.value)}
              >
                <option value="있음">있음</option>
                <option value="없음">없음</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">조명 상태</label>
              <select
                className="form-control"
                value={formData.lightingCondition}
                onChange={(e) => handleInputChange('lightingCondition', e.target.value)}
              >
                <option value="너무 밝음">너무 밝음</option>
                <option value="적절함">적절함</option>
                <option value="너무 어두움">너무 어두움</option>
                <option value="반사광 있음">반사광 있음</option>
              </select>
            </div>
          </div>
        </div>
      </section>

      <hr className="section-divider" />

      <section className="posture-guide">
        <h2>📋 올바른 자세 가이드</h2>
        <div className="guide-grid">
          <div className="guide-item">
            <h4>🖥️ 모니터 위치</h4>
            <ul>
              <li>눈높이와 같거나 약간 아래</li>
              <li>팔 길이만큼 거리 유지 (50-70cm)</li>
            </ul>
          </div>
          <div className="guide-item">
            <h4>⌨️ 키보드 & 마우스</h4>
            <ul>
              <li>팔꿈치 각도 90도</li>
              <li>손목은 일직선 유지</li>
            </ul>
          </div>
        </div>
      </section>

      <hr className="section-divider" />

      <section className="environment-score">
        <h2>📊 작업환경 점수</h2>
        <div className="score-display">
          <div className="score-circle">
            <div 
              className="score-value"
              style={{ color: getScoreColor(envScore) }}
            >
              {envScore}
            </div>
            <div className="score-max">/ 100</div>
          </div>
          <div className="score-info">
            <div 
              className="score-status"
              style={{ color: getScoreColor(envScore) }}
            >
              {getScoreStatus(envScore)}
            </div>
            <div className="score-description">
              {envScore >= 80 && "훌륭한 작업환경입니다! 현재 상태를 유지하세요."}
              {envScore >= 60 && envScore < 80 && "보통 수준의 작업환경입니다. 몇 가지 개선이 필요합니다."}
              {envScore < 60 && "작업환경 개선이 시급합니다. VDT 증후군 위험이 높습니다."}
            </div>
          </div>
        </div>

        <div className="score-breakdown">
          <h4>점수 구성</h4>
          <div className="breakdown-grid">
            <div className="breakdown-item">
              <span>책상 높이</span>
              <span>{formData.deskHeight === "적절함" ? "20점" : "0점"}</span>
            </div>
            <div className="breakdown-item">
              <span>의자 지지력</span>
              <span>
                {formData.chairSupport === "매우 좋음" ? "20점" : 
                 formData.chairSupport === "좋음" ? "15점" : 
                 formData.chairSupport === "보통" ? "8점" : "0점"}
              </span>
            </div>
            <div className="breakdown-item">
              <span>앉는 자세</span>
              <span>{formData.chairSittingStyle === "등을 완전히 붙이고 앉음" ? "10점" : "0점"}</span>
            </div>
            <div className="breakdown-item">
              <span>모니터 높이</span>
              <span>
                {formData.monitorHeight === "눈높이와 같음" ? "15점" : 
                 formData.monitorHeight === "눈높이보다 낮음" ? "8점" : "0점"}
              </span>
            </div>
            <div className="breakdown-item">
              <span>손목 받침대</span>
              <span>{formData.wristRest === "있음" ? "7점" : "0점"}</span>
            </div>
            <div className="breakdown-item">
              <span>조명 상태</span>
              <span>{formData.lightingCondition === "적절함" ? "7점" : "0점"}</span>
            </div>
          </div>
        </div>
      </section>

      <div className="form-actions">
        <button 
          className="btn btn-primary"
          onClick={handleNext}
        >
          ✅ 저장하고 다음 단계로
        </button>
      </div>
    </div>
  );
};

export default WorkEnvironment;