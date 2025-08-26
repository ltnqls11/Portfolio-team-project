import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ProgressHeader from './common/ProgressHeader';
import PainScale from './common/PainScale';
import './ConditionSelection.css';

const ConditionSelection = ({ sessionState, updateSessionState, onNavigate, progress }) => {
  const navigate = useNavigate();
  const [selectedConditions, setSelectedConditions] = useState(sessionState.selectedConditions || []);
  const [painScores, setPainScores] = useState(sessionState.userData.painScores || {});
  const [subjectiveStatus, setSubjectiveStatus] = useState(sessionState.subjectiveStatus || '');

  // 디버깅을 위한 상태 변화 추적
  useEffect(() => {
    console.log('ConditionSelection 상태 변화:', {
      selectedConditions,
      painScores,
      subjectiveStatus,
      sessionState
    });
  }, [selectedConditions, painScores, subjectiveStatus, sessionState]);

  const conditions = {
    "거북목": "목이 앞으로 나오고 목, 어깨 통증이 있음",
    "라운드숄더": "어깨가 앞으로 말리고 상체가 구부정함",
    "허리디스크": "허리 통증, 다리 저림 등의 증상",
    "손목터널증후군": "손목, 손가락 저림 및 통증"
  };

  const handleConditionChange = (condition, checked) => {
    let newSelected;
    if (checked) {
      newSelected = [...selectedConditions, condition];
      // 새로 선택된 증상에 대한 기본 통증 점수 설정
      setPainScores(prev => ({
        ...prev,
        [condition]: prev[condition] || 5
      }));
    } else {
      newSelected = selectedConditions.filter(c => c !== condition);
      // 선택 해제된 증상의 통증 점수 제거
      const newPainScores = { ...painScores };
      delete newPainScores[condition];
      setPainScores(newPainScores);
    }
    setSelectedConditions(newSelected);
  };

  const handlePainScoreChange = (condition, score) => {
    setPainScores(prev => ({
      ...prev,
      [condition]: score
    }));
  };

  const handleNext = async () => {
    console.log('ConditionSelection handleNext 시작');
    console.log('선택된 증상:', selectedConditions);
    console.log('통증 점수:', painScores);
    
    // 유효성 검사
    if (selectedConditions.length === 0) {
      alert('최소 하나의 증상을 선택해주세요.');
      return;
    }

    // 선택된 증상에 대한 통증 점수 확인
    const missingPainScores = selectedConditions.filter(condition => 
      painScores[condition] === undefined || painScores[condition] === null
    );
    
    if (missingPainScores.length > 0) {
      alert(`다음 증상의 통증 점수를 설정해주세요: ${missingPainScores.join(', ')}`);
      return;
    }
    
    try {
      // 세션 상태 업데이트
      const updatedUserData = {
        ...sessionState.userData,
        painScores: painScores,
        subjectiveStatus: subjectiveStatus
      };

      const updatedStepsCompleted = [...sessionState.stepsCompleted];
      updatedStepsCompleted[0] = true;

      const newSessionState = {
        ...sessionState,
        selectedConditions: selectedConditions,
        userData: updatedUserData,
        subjectiveStatus: subjectiveStatus,
        stepsCompleted: updatedStepsCompleted,
        currentStep: 1
      };

      console.log('업데이트할 세션 상태:', newSessionState);
      
      // 상태 업데이트
      updateSessionState(newSessionState);
      
      // 성공 메시지
      console.log('증상 선택 완료:', {
        conditions: selectedConditions,
        painScores: painScores,
        subjectiveStatus: subjectiveStatus
      });
      
      // 메뉴 상태 업데이트를 먼저 실행
      onNavigate("개인정보 입력");
      
      // 상태 업데이트가 완료될 때까지 잠시 대기
      await new Promise(resolve => setTimeout(resolve, 300));
      
      // 네비게이션 실행
      console.log('네비게이션 시작: /personal-info');
      navigate('/personal-info');
      
      // 네비게이션이 실패할 경우를 대비한 백업 방법
      setTimeout(() => {
        if (window.location.pathname !== '/personal-info') {
          console.log('네비게이션 실패, 백업 방법 사용');
          window.location.href = '/personal-info';
        }
      }, 500);
      
    } catch (error) {
      console.error('handleNext 오류:', error);
      alert('저장 중 오류가 발생했습니다. 다시 시도해주세요.');
    }
  };

  const isFormValid = () => {
    // 최소 하나의 증상이 선택되어야 함
    if (selectedConditions.length === 0) {
      return false;
    }
    
    // 선택된 모든 증상에 대해 통증 점수가 설정되어야 함
    const hasAllPainScores = selectedConditions.every(condition => 
      painScores[condition] !== undefined && painScores[condition] !== null
    );
    
    return hasAllPainScores;
  };

  return (
    <div className="condition-selection">
      <div className="page-header">
        <h1 className="page-title">증상 선택 및 통증 평가</h1>
      </div>

      <ProgressHeader progress={progress} />

      <hr className="section-divider" />

      <section className="condition-selection-section">
        <h2>증상 선택</h2>
        <p className="section-description">현재 겪고 있는 증상을 모두 선택해주세요.</p>
        
        <div className="conditions-grid">
          {Object.entries(conditions).map(([condition, description]) => (
            <div key={condition} className="condition-item">
              <label className="condition-label">
                <input
                  type="checkbox"
                  checked={selectedConditions.includes(condition)}
                  onChange={(e) => handleConditionChange(condition, e.target.checked)}
                  className="condition-checkbox"
                />
                <div className="condition-content">
                  <h3 className="condition-name">{condition}</h3>
                  <p className="condition-description">{description}</p>
                </div>
              </label>
            </div>
          ))}
        </div>

        {selectedConditions.length > 0 && (
          <div className="alert alert-success">
            ✅ <strong>선택된 증상</strong>: {selectedConditions.join(', ')}
          </div>
        )}
      </section>

      {selectedConditions.length > 0 && (
        <>
          <hr className="section-divider" />
          
          <section className="pain-assessment-section">
            <h2>🔴 통증 정도 평가</h2>
            <div className="alert alert-info">
              각 증상별로 현재 통증 정도를 아래 이모티콘과 색상을 참고하여 평가해주세요
            </div>

            <PainScale />

            <div className="pain-scores">
              {selectedConditions.map(condition => (
                <div key={condition} className="pain-score-item">
                  <h3>{condition} 통증 정도</h3>
                  
                  <div className="pain-input-container">
                    <input
                      type="range"
                      min="0"
                      max="10"
                      value={painScores[condition] || 5}
                      onChange={(e) => handlePainScoreChange(condition, parseInt(e.target.value))}
                      className="pain-slider"
                    />
                    
                    <div className="current-pain">
                      <div 
                        className="current-pain-indicator"
                        style={{ backgroundColor: getPainColor(painScores[condition] || 5) }}
                      >
                        <div className="current-pain-emoji">
                          {getPainEmoji(painScores[condition] || 5)}
                        </div>
                        <div className="current-pain-number">
                          {painScores[condition] || 5}
                        </div>
                      </div>
                      
                      <div className="current-pain-info">
                        <h4>현재 선택: {painScores[condition] || 5}점</h4>
                        <p><strong>상태</strong>: {getPainDescription(painScores[condition] || 5)}</p>
                        <p><strong>설명</strong>: {condition} 증상으로 인한 현재 통증이 이 정도입니다.</p>
                      </div>
                    </div>
                  </div>
                  
                  <hr className="pain-divider" />
                </div>
              ))}
            </div>
          </section>

          <hr className="section-divider" />

          <section className="subjective-section">
            <h2>📋 주관적 상태 설명</h2>
            <div className="alert alert-info">
              현재 건강 상태나 증상에 대해 자유롭게 작성해주세요 (100자 이내)
            </div>
            
            <div className="form-group">
              <label className="form-label">현재 상태</label>
              <textarea
                className="form-control"
                value={subjectiveStatus}
                onChange={(e) => setSubjectiveStatus(e.target.value)}
                maxLength={100}
                placeholder="예: 오른쪽 어깨가 특히 많이 아프고, 업무 후 두통이 자주 생깁니다."
                rows={3}
              />
              <small className="form-text">
                의료진에게 전달하고 싶은 증상을 구체적으로 작성해주세요. ({subjectiveStatus.length}/100자)
              </small>
            </div>
          </section>

          <div className="form-actions">
            {isFormValid() ? (
              <button 
                className="btn btn-primary"
                onClick={handleNext}
              >
                ✅ 저장하고 다음 단계로
              </button>
            ) : (
              <div className="alert alert-warning">
                {selectedConditions.length === 0 
                  ? "⚠️ 최소 하나의 증상을 선택해주세요."
                  : "⚠️ 선택한 모든 증상의 통증 점수를 설정해주세요."
                }
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

// 통증 수준에 따른 이모티콘 반환
const getPainEmoji = (level) => {
  const painScale = {
    0: "😊", 1: "🙂", 2: "😐", 3: "🤕", 4: "😟",
    5: "😣", 6: "😖", 7: "😫", 8: "😵", 9: "😱", 10: "🥵"
  };
  return painScale[level] || "❓";
};

// 통증 수준에 따른 색상 반환
const getPainColor = (level) => {
  const colors = {
    0: "#00FF00", 1: "#66FF66", 2: "#99FF99", 3: "#CCFF99", 4: "#FFFF99",
    5: "#FFCC99", 6: "#FF9966", 7: "#FF6633", 8: "#FF3300", 9: "#CC0000", 10: "#990000"
  };
  return colors[level] || "#808080";
};

// 통증 수준에 따른 설명 반환
const getPainDescription = (level) => {
  const descriptions = {
    0: "통증 없음", 1: "매우 경미한 통증", 2: "경미한 통증", 3: "불편함", 4: "약간 아픔",
    5: "보통 아픔", 6: "상당히 아픔", 7: "많이 아픔", 8: "심한 통증", 9: "매우 심한 통증", 10: "견딜 수 없는 통증"
  };
  return descriptions[level] || "알 수 없음";
};

export default ConditionSelection;