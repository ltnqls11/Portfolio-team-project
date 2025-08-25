import React, { useState, useEffect } from 'react';
import ProgressHeader from './common/ProgressHeader';
import './ExerciseRecommendation.css';

const ExerciseRecommendation = ({ sessionState, updateSessionState, onNavigate, progress }) => {
  const [activeTab, setActiveTab] = useState('consultation');
  const [aiRecommendation, setAiRecommendation] = useState('');
  const [recommendedPurpose, setRecommendedPurpose] = useState(null);
  const [finalPurpose, setFinalPurpose] = useState('');
  const [weeklyRoutine, setWeeklyRoutine] = useState(null);
  const [loading, setLoading] = useState(false);

  // AI 추천 운동 목적 자동 계산
  useEffect(() => {
    if (sessionState.userData && sessionState.selectedConditions && sessionState.userData.painScores) {
      const recommendation = recommendExercisePurpose(
        sessionState.userData,
        sessionState.selectedConditions,
        sessionState.userData.painScores
      );
      setRecommendedPurpose(recommendation);
    }
  }, [sessionState]);

  const recommendExercisePurpose = (userData, conditions, painScores) => {
    const avgPain = Object.values(painScores).reduce((a, b) => a + b, 0) / Object.values(painScores).length;
    const envScore = userData.envScore || 50;
    const exerciseHabit = userData.exerciseHabit || '전혀 안함';
    const age = userData.age || 30;

    // 추천 로직
    if (avgPain >= 7) {
      return {
        purpose: '재활 (통증감소)',
        reason: `평균 통증 수준이 ${avgPain.toFixed(1)}점으로 높아 통증 감소가 우선적으로 필요합니다.`,
        confidence: 'high'
      };
    } else if (avgPain >= 4 && envScore < 50) {
      return {
        purpose: '재활 (통증감소)',
        reason: `통증 수준 ${avgPain.toFixed(1)}점과 작업환경 ${envScore}점으로 재활이 필요합니다.`,
        confidence: 'medium'
      };
    } else if (['주 3-4회', '주 5회 이상'].includes(exerciseHabit) && avgPain < 4) {
      return {
        purpose: '운동 (근력 및 체력 증진)',
        reason: `규칙적인 운동 습관(${exerciseHabit})과 낮은 통증 수준으로 체력 증진이 적합합니다.`,
        confidence: 'high'
      };
    } else if (age <= 35 && ['주 1-2회', '주 3-4회', '주 5회 이상'].includes(exerciseHabit)) {
      return {
        purpose: '운동 (근력 및 체력 증진)',
        reason: `젊은 연령(${age}세)과 운동 경험으로 근력 증진이 효과적입니다.`,
        confidence: 'medium'
      };
    } else {
      return {
        purpose: '예방 (자세교정)',
        reason: '현재 상태를 고려할 때 자세 교정을 통한 예방이 가장 적합합니다.',
        confidence: 'medium'
      };
    }
  };

  const generateAIRecommendation = async () => {
    setLoading(true);
    
    // AI 추천 시뮬레이션 (실제로는 API 호출)
    setTimeout(() => {
      const mockRecommendation = `
## 🎯 VDT 증후군 맞춤 운동 프로그램

### 1. 증상별 맞춤 운동법
**${sessionState.selectedConditions.join(', ')} 집중 관리**

${sessionState.selectedConditions.map(condition => {
  const painLevel = sessionState.userData.painScores[condition] || 0;
  if (condition === '거북목') {
    return `- **거북목 교정**: 목 스트레칭과 심부 목 굴곡근 강화 운동 (통증 수준: ${painLevel}/10점)`;
  } else if (condition === '라운드숄더') {
    return `- **라운드숄더 개선**: 가슴 스트레칭과 상부 등 근육 강화 (통증 수준: ${painLevel}/10점)`;
  } else if (condition === '허리디스크') {
    return `- **허리 안정화**: 코어 강화와 허리 유연성 운동 (통증 수준: ${painLevel}/10점)`;
  } else if (condition === '손목터널증후군') {
    return `- **손목 관리**: 손목 스트레칭과 신경 활주 운동 (통증 수준: ${painLevel}/10점)`;
  }
  return `- **${condition}**: 맞춤형 운동 프로그램 (통증 수준: ${painLevel}/10점)`;
}).join('\n')}

### 2. 운동 순서와 시간 배분
- **워밍업 (5분)**: 가벼운 관절 운동과 스트레칭
- **메인 운동 (${sessionState.exerciseSchedule?.dailyMinutes - 10 || 20}분)**: 증상별 맞춤 운동
- **쿨다운 (5분)**: 이완 스트레칭과 호흡 운동

### 3. 주의사항 및 금기사항
- 통증이 심해지면 즉시 중단하고 전문의 상담
- 급격한 움직임 금지, 천천히 부드럽게 진행
- 운동 전후 충분한 수분 섭취

### 4. 일주일 운동 계획표
**선택된 요일**: ${sessionState.exerciseSchedule?.availableDays?.join(', ') || '미설정'}
**일일 운동 시간**: ${sessionState.exerciseSchedule?.dailyMinutes || 30}분
**주간 총 시간**: ${(sessionState.exerciseSchedule?.availableDays?.length || 0) * (sessionState.exerciseSchedule?.dailyMinutes || 30)}분

### 5. 개선 예상 기간
- **1-2주**: 근육 긴장 완화 및 통증 감소
- **4-6주**: 자세 개선 및 근력 향상
- **8-12주**: 전반적인 VDT 증후군 증상 개선
      `;
      
      setAiRecommendation(mockRecommendation);
      setLoading(false);
    }, 2000);
  };

  const handlePurposeSelection = (purpose) => {
    setFinalPurpose(purpose);
    
    // 세션 상태 업데이트
    updateSessionState({
      finalExercisePurpose: purpose,
      aiRecommendedPurpose: recommendedPurpose
    });
  };

  const generateWeeklyRoutine = () => {
    if (!sessionState.exerciseSchedule || !sessionState.exerciseSchedule.availableDays) {
      return;
    }

    const routine = createPersonalizedRoutine(
      sessionState.userData,
      sessionState.selectedConditions,
      sessionState.userData.painScores,
      sessionState.exerciseSchedule,
      finalPurpose || recommendedPurpose?.purpose
    );
    
    setWeeklyRoutine(routine);
  };

  const createPersonalizedRoutine = (userData, conditions, painScores, schedule, purpose) => {
    const availableDays = schedule.availableDays;
    const dailyMinutes = schedule.dailyMinutes;
    const difficultyLevel = schedule.difficultyLevel;

    const weeklyRoutine = {};
    
    availableDays.forEach((day, index) => {
      const videoTime = Math.floor(dailyMinutes * 0.75);
      const stretchingTime = Math.floor(dailyMinutes * 0.15);
      const warmupTime = dailyMinutes - videoTime - stretchingTime;

      // 모의 운동 영상 데이터
      const mockVideos = conditions.map((condition, idx) => ({
        title: `${condition} 맞춤 운동 ${idx + 1}`,
        url: `https://example.com/video${idx + 1}`,
        duration: `${Math.floor(Math.random() * 10) + 5}:${Math.floor(Math.random() * 60).toString().padStart(2, '0')}`,
        channel: '전문 물리치료사',
        difficulty: difficultyLevel
      }));

      const conditionStretches = conditions.map(condition => ({
        부위: condition,
        동작: `${condition} 전용 스트레칭`,
        시간: '15초씩',
        횟수: '3세트',
        주의: '천천히 부드럽게'
      }));

      weeklyRoutine[day] = {
        총_시간: dailyMinutes,
        워밍업_시간: warmupTime,
        영상_시간: videoTime,
        스트레칭_시간: stretchingTime,
        선택된_영상: mockVideos,
        맞춤_스트레칭: conditionStretches,
        난이도: difficultyLevel
      };
    });

    return {
      주간_루틴: weeklyRoutine,
      총_주간시간: availableDays.length * dailyMinutes,
      운동_일수: availableDays.length,
      스트레칭_가이드: getStretchingGuide()
    };
  };

  const getStretchingGuide = () => ({
    "목 스트레칭": {
      자세: "의자에 똑바로 앉아 어깨를 자연스럽게 내린 상태",
      방법: [
        "1. 고개를 천천히 오른쪽으로 기울여 15초간 유지",
        "2. 같은 방법으로 왼쪽으로 기울여 15초간 유지",
        "3. 고개를 천천히 앞으로 숙여 15초간 유지",
        "4. 고개를 뒤로 젖혀 15초간 유지 (과도하지 않게)"
      ],
      주의사항: "급격한 움직임 금지, 통증이 있으면 즉시 중단",
      효과: "목 근육 이완, 긴장성 두통 완화"
    },
    "어깨 스트레칭": {
      자세: "서거나 앉은 상태에서 등을 곧게 편 자세",
      방법: [
        "1. 오른팔을 왼쪽으로 당겨 가슴 앞에서 15초간 유지",
        "2. 왼팔로 오른팔을 감싸며 당겨주기",
        "3. 반대쪽도 같은 방법으로 실시",
        "4. 양팔을 위로 들어 좌우로 기울이며 옆구리 늘리기"
      ],
      주의사항: "어깨에 무리가 가지 않도록 서서히 진행",
      효과: "어깨 근육 이완, 라운드 숄더 예방"
    }
  });

  const handleNext = () => {
    const updatedStepsCompleted = [...sessionState.stepsCompleted];
    updatedStepsCompleted[4] = true;

    updateSessionState({
      stepsCompleted: updatedStepsCompleted,
      currentStep: 5,
      weeklyRoutine: weeklyRoutine
    });

    onNavigate("휴식 알리미 설정");
    // React Router로 직접 이동
    window.location.href = '/notification-setup';
  };

  if (!sessionState.selectedConditions || sessionState.selectedConditions.length === 0) {
    return (
      <div className="exercise-recommendation">
        <div className="alert alert-warning">
          먼저 증상을 선택해주세요.
        </div>
      </div>
    );
  }

  return (
    <div className="exercise-recommendation">
      <div className="page-header">
        <h1 className="page-title">운동 추천</h1>
      </div>

      <ProgressHeader progress={progress} />

      <hr className="section-divider" />

      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'consultation' ? 'active' : ''}`}
          onClick={() => setActiveTab('consultation')}
        >
          👨‍⚕️ 재활의학과 전문의 챗봇과 실시간 상담
        </button>
        <button 
          className={`tab ${activeTab === 'routine' ? 'active' : ''}`}
          onClick={() => setActiveTab('routine')}
        >
          🏃‍♀️ 맞춤형 운동 루틴
        </button>
        <button 
          className={`tab ${activeTab === 'products' ? 'active' : ''}`}
          onClick={() => setActiveTab('products')}
        >
          🛒 맞춤 제품 추천
        </button>
      </div>

      {activeTab === 'consultation' && (
        <div className="consultation-tab">
          <section className="doctor-consultation">
            <h2>👨‍⚕️ 재활의학과 전문의 챗봇과 실시간 상담</h2>
            
            <div className="doctor-intro">
              <div className="doctor-card">
                <div className="doctor-avatar">👨‍⚕️</div>
                <div className="doctor-info">
                  <h3>VDT 증후군 전문의 챗봇</h3>
                  <p>재활의학과 전문의 지식을 바탕으로 한 AI 상담 시스템</p>
                  <div className="doctor-credentials">
                    <span>• 재활의학과 전문의</span>
                    <span>• VDT 증후군 전문</span>
                    <span>• 근골격계 질환 전문</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="patient-summary">
              <h3>📋 환자 정보 요약</h3>
              <div className="summary-grid">
                <div className="summary-item">
                  <span className="label">주요 증상:</span>
                  <span className="value">{sessionState.selectedConditions?.join(', ') || '없음'}</span>
                </div>
                <div className="summary-item">
                  <span className="label">평균 통증:</span>
                  <span className="value">
                    {sessionState.userData?.painScores ? 
                      (Object.values(sessionState.userData.painScores).reduce((a, b) => a + b, 0) / 
                       Object.values(sessionState.userData.painScores).length).toFixed(1) + '점' : '정보없음'}
                  </span>
                </div>
                <div className="summary-item">
                  <span className="label">작업환경:</span>
                  <span className="value">{sessionState.userData?.envScore || 0}점/100점</span>
                </div>
                <div className="summary-item">
                  <span className="label">일일 작업시간:</span>
                  <span className="value">{sessionState.userData?.dailyWorkHours || 0}시간</span>
                </div>
              </div>
            </div>

            {recommendedPurpose && (
              <div className="doctor-recommendation">
                <h3>🩺 전문의 소견</h3>
                <div className="medical-opinion">
                  <div className="diagnosis">
                    <strong>진단:</strong> {recommendedPurpose.purpose}
                  </div>
                  <div className="reasoning">
                    <strong>소견:</strong> {recommendedPurpose.reason}
                  </div>
                  <div className={`confidence-level ${recommendedPurpose.confidence}`}>
                    <strong>확신도:</strong> {recommendedPurpose.confidence === 'high' ? '높음' : 
                             recommendedPurpose.confidence === 'medium' ? '보통' : '낮음'}
                  </div>
                </div>
              </div>
            )}

            <div className="treatment-selection">
              <h3>💊 치료 방향 선택</h3>
              <p>전문의 소견을 참고하여 치료 방향을 선택해주세요.</p>
              
              <div className="treatment-options">
                {['예방 (자세교정)', '운동 (근력 및 체력 증진)', '재활 (통증감소)'].map(purpose => (
                  <button
                    key={purpose}
                    className={`treatment-btn ${finalPurpose === purpose ? 'selected' : ''} ${recommendedPurpose?.purpose === purpose ? 'recommended' : ''}`}
                    onClick={() => handlePurposeSelection(purpose)}
                  >
                    <div className="treatment-title">{purpose}</div>
                    <div className="treatment-desc">
                      {purpose === '예방 (자세교정)' && '올바른 자세 습관 형성 및 예방 중심'}
                      {purpose === '운동 (근력 및 체력 증진)' && '근력 강화 및 전반적인 체력 향상'}
                      {purpose === '재활 (통증감소)' && '통증 완화 및 기능 회복 중심'}
                    </div>
                    {recommendedPurpose?.purpose === purpose && <span className="recommended-badge">전문의 추천</span>}
                  </button>
                ))}
              </div>
            </div>

            {finalPurpose && (
              <div className="consultation-actions">
                <button 
                  className="btn btn-primary"
                  onClick={generateAIRecommendation}
                  disabled={loading}
                >
                  {loading ? '처방전 작성 중...' : '🩺 맞춤 처방전 받기'}
                </button>
              </div>
            )}

            {loading && (
              <div className="loading">
                <div className="spinner"></div>
                <p>전문의가 맞춤형 운동 처방전을 작성하고 있습니다...</p>
              </div>
            )}

            {aiRecommendation && (
              <div className="prescription-result">
                <h3>📋 운동 처방전</h3>
                <div className="prescription-header">
                  <div className="prescription-title">VDT 증후군 맞춤 운동 처방전</div>
                  <div className="prescription-date">처방일: {new Date().toLocaleDateString('ko-KR')}</div>
                </div>
                <div className="prescription-content">
                  {aiRecommendation.split('\n').map((line, index) => (
                    <div key={index} className="prescription-line">
                      {line.startsWith('##') ? (
                        <h2>{line.replace('##', '').trim()}</h2>
                      ) : line.startsWith('###') ? (
                        <h3>{line.replace('###', '').trim()}</h3>
                      ) : line.startsWith('**') && line.endsWith('**') ? (
                        <strong>{line.replace(/\*\*/g, '')}</strong>
                      ) : line.startsWith('-') ? (
                        <li>{line.replace('-', '').trim()}</li>
                      ) : (
                        <p>{line}</p>
                      )}
                    </div>
                  ))}
                </div>
                <div className="prescription-footer">
                  <p><strong>처방의:</strong> VDT 증후군 전문의 챗봇</p>
                  <p><strong>주의사항:</strong> 통증이 악화되거나 새로운 증상이 나타나면 즉시 전문의와 상담하세요.</p>
                </div>
              </div>
            )}
          </section>
        </div>
      )}

      {activeTab === 'routine' && (
        <div className="routine-tab">
          <section className="routine-generation">
            <h2>🏃‍♀️ 맞춤형 운동 루틴</h2>
            
            {!finalPurpose && !recommendedPurpose && (
              <div className="alert alert-warning">
                ❗ 먼저 '재활의학과 전문의 챗봇과 실시간 상담' 탭에서 상담을 진행해주세요.
              </div>
            )}

            {(finalPurpose || recommendedPurpose) && !sessionState.exerciseSchedule?.availableDays && (
              <div className="alert alert-warning">
                ❗ 먼저 '개인 운동 설문조사'를 완료해주세요.
                <br />
                📋 운동 가능한 요일과 시간을 설정한 후 맞춤 루틴을 생성할 수 있습니다.
              </div>
            )}

            {(finalPurpose || recommendedPurpose) && sessionState.exerciseSchedule?.availableDays && (
              <>
                <div className="routine-info">
                  <div className="consultation-summary">
                    <h3>🩺 상담 결과 요약</h3>
                    <div className="summary-content">
                      <div className="diagnosis-result">
                        <strong>진단 결과:</strong> {finalPurpose || recommendedPurpose.purpose}
                      </div>
                      <div className="treatment-plan">
                        <strong>치료 계획:</strong> 개인 맞춤형 운동 프로그램을 통한 단계적 개선
                      </div>
                    </div>
                  </div>
                  
                  <div className="alert alert-success">
                    🎯 <strong>처방된 운동 목적</strong>: {finalPurpose || recommendedPurpose.purpose}
                  </div>
                </div>

                {!weeklyRoutine && (
                  <div className="routine-actions">
                    <button 
                      className="btn btn-primary"
                      onClick={generateWeeklyRoutine}
                    >
                      📅 맞춤 운동 루틴 생성하기
                    </button>
                  </div>
                )}

                {weeklyRoutine && (
                  <div className="weekly-routine">
                    <h3>📊 주간 운동 루틴 요약</h3>
                    <div className="routine-summary">
                      <div className="summary-item">
                        <span>🗓️ 운동 일수</span>
                        <span>{weeklyRoutine.운동_일수}일</span>
                      </div>
                      <div className="summary-item">
                        <span>⏰ 주간 총 시간</span>
                        <span>{weeklyRoutine.총_주간시간}분</span>
                      </div>
                      <div className="summary-item">
                        <span>⭐ 난이도</span>
                        <span>{sessionState.exerciseSchedule.difficultyLevel}</span>
                      </div>
                      <div className="summary-item">
                        <span>📅 일일 평균</span>
                        <span>{Math.floor(weeklyRoutine.총_주간시간 / weeklyRoutine.운동_일수)}분</span>
                      </div>
                    </div>

                    <div className="exercise-videos-section">
                      <h3>🎬 추천 운동 영상</h3>
                      <div className="video-recommendations">
                        {sessionState.selectedConditions?.map((condition, index) => (
                          <div key={condition} className="condition-videos">
                            <h4>{condition} 맞춤 운동</h4>
                            <div className="video-grid">
                              <div className="video-card">
                                <div className="video-thumbnail">🎥</div>
                                <div className="video-info">
                                  <h5>{condition} 교정 운동 기초</h5>
                                  <p>📺 전문 물리치료사 | ⏱️ 8:30 | 👀 1.2M</p>
                                  <div className="video-tags">
                                    <span className="tag">초급자</span>
                                    <span className="tag">기초</span>
                                  </div>
                                </div>
                              </div>
                              <div className="video-card">
                                <div className="video-thumbnail">🎥</div>
                                <div className="video-info">
                                  <h5>{condition} 스트레칭 루틴</h5>
                                  <p>📺 재활의학과 | ⏱️ 12:15 | 👀 850K</p>
                                  <div className="video-tags">
                                    <span className="tag">스트레칭</span>
                                    <span className="tag">통증완화</span>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <h3>📅 요일별 상세 운동 계획</h3>
                    <div className="daily-routines">
                      {Object.entries(weeklyRoutine.주간_루틴).map(([day, routine]) => (
                        <div key={day} className="daily-routine">
                          <div className="routine-header">
                            <h4>📅 {day} - {routine.총_시간}분 루틴</h4>
                            <div className="routine-status">계획됨</div>
                          </div>
                          
                          <div className="routine-timeline">
                            <div className="timeline-item">
                              <div className="timeline-icon">🔥</div>
                              <div className="timeline-content">
                                <h5>워밍업 ({routine.워밍업_시간}분)</h5>
                                <ul>
                                  <li>관절 가동성 운동</li>
                                  <li>가벼운 스트레칭</li>
                                  <li>혈액순환 촉진</li>
                                </ul>
                              </div>
                            </div>
                            
                            <div className="timeline-item">
                              <div className="timeline-icon">💪</div>
                              <div className="timeline-content">
                                <h5>메인 운동 ({routine.영상_시간}분)</h5>
                                <div className="exercise-list">
                                  {routine.선택된_영상.map((video, index) => (
                                    <div key={index} className="exercise-item">
                                      <span className="exercise-name">{video.title}</span>
                                      <span className="exercise-duration">{video.duration}</span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            </div>
                            
                            <div className="timeline-item">
                              <div className="timeline-icon">🧘‍♀️</div>
                              <div className="timeline-content">
                                <h5>마무리 스트레칭 ({routine.스트레칭_시간}분)</h5>
                                <div className="stretch-list">
                                  {routine.맞춤_스트레칭.map((stretch, index) => (
                                    <div key={index} className="stretch-item">
                                      <span className="stretch-name">{stretch.부위} 스트레칭</span>
                                      <span className="stretch-duration">{stretch.시간}</span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>

                    <div className="routine-guidelines">
                      <h3>📋 운동 수행 가이드라인</h3>
                      <div className="guidelines-grid">
                        <div className="guideline-card">
                          <h4>⚠️ 주의사항</h4>
                          <ul>
                            <li>통증이 심해지면 즉시 중단</li>
                            <li>급격한 움직임 금지</li>
                            <li>개인 페이스에 맞춰 진행</li>
                            <li>충분한 수분 섭취</li>
                          </ul>
                        </div>
                        <div className="guideline-card">
                          <h4>📈 진행 방법</h4>
                          <ul>
                            <li>1주차: 기본 동작 익히기</li>
                            <li>2-3주차: 강도 점진적 증가</li>
                            <li>4주차 이후: 유지 및 발전</li>
                            <li>정기적인 상태 점검</li>
                          </ul>
                        </div>
                        <div className="guideline-card">
                          <h4>🎯 목표 설정</h4>
                          <ul>
                            <li>단기: 통증 감소 (2-4주)</li>
                            <li>중기: 자세 개선 (1-2개월)</li>
                            <li>장기: 습관 형성 (3개월 이상)</li>
                            <li>지속적인 건강 관리</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </>
            )}
          </section>
        </div>
      )}

      {activeTab === 'products' && (
        <div className="products-tab">
          <section className="product-recommendations">
            <h2>🛒 맞춤 제품 추천</h2>
            
            {!finalPurpose && !recommendedPurpose && (
              <div className="alert alert-warning">
                ❗ 먼저 '재활의학과 전문의 챗봇과 실시간 상담' 탭에서 상담을 진행해주세요.
              </div>
            )}

            {(finalPurpose || recommendedPurpose) && (
              <div className="product-info">
                <div className="personalized-recommendations">
                  <h3>🎯 개인 맞춤 제품 추천</h3>
                  <div className="recommendation-basis">
                    <p><strong>추천 근거:</strong> {sessionState.selectedConditions?.join(', ')} 증상 및 {finalPurpose || recommendedPurpose?.purpose} 목적</p>
                  </div>
                </div>

                <div className="coupang-partners">
                  <h3>🛍️ 쿠팡 파트너스 추천 상품</h3>
                  <div className="partner-notice">
                    <p>이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.</p>
                  </div>
                  
                  <div className="product-grid">
                    {sessionState.selectedConditions?.includes('거북목') && (
                      <div className="product-card coupang">
                        <div className="product-image">🦢</div>
                        <div className="product-info">
                          <h4>거북목 교정기</h4>
                          <p>자세 교정 및 목 통증 완화를 위한 전문 교정기</p>
                          <div className="product-price">₩29,900</div>
                          <div className="product-rating">⭐⭐⭐⭐⭐ (4.5/5)</div>
                          <button className="coupang-btn">쿠팡에서 보기</button>
                        </div>
                      </div>
                    )}
                    
                    {sessionState.selectedConditions?.includes('라운드숄더') && (
                      <div className="product-card coupang">
                        <div className="product-image">💪</div>
                        <div className="product-info">
                          <h4>어깨 밴드 교정기</h4>
                          <p>라운드숄더 교정을 위한 탄성 밴드</p>
                          <div className="product-price">₩19,900</div>
                          <div className="product-rating">⭐⭐⭐⭐ (4.2/5)</div>
                          <button className="coupang-btn">쿠팡에서 보기</button>
                        </div>
                      </div>
                    )}
                    
                    <div className="product-card coupang">
                      <div className="product-image">🪑</div>
                      <div className="product-info">
                        <h4>인체공학적 의자</h4>
                        <p>허리 지지력이 뛰어난 사무용 의자</p>
                        <div className="product-price">₩189,000</div>
                        <div className="product-rating">⭐⭐⭐⭐⭐ (4.7/5)</div>
                        <button className="coupang-btn">쿠팡에서 보기</button>
                      </div>
                    </div>
                    
                    <div className="product-card coupang">
                      <div className="product-image">⌨️</div>
                      <div className="product-info">
                        <h4>인체공학적 키보드</h4>
                        <p>손목 부담을 줄이는 분할형 키보드</p>
                        <div className="product-price">₩89,000</div>
                        <div className="product-rating">⭐⭐⭐⭐ (4.3/5)</div>
                        <button className="coupang-btn">쿠팡에서 보기</button>
                      </div>
                    </div>
                    
                    {sessionState.selectedConditions?.includes('손목터널증후군') && (
                      <div className="product-card coupang">
                        <div className="product-image">🖱️</div>
                        <div className="product-info">
                          <h4>손목 보호대</h4>
                          <p>손목터널증후군 예방 및 완화용 보호대</p>
                          <div className="product-price">₩15,900</div>
                          <div className="product-rating">⭐⭐⭐⭐ (4.1/5)</div>
                          <button className="coupang-btn">쿠팡에서 보기</button>
                        </div>
                      </div>
                    )}
                    
                    <div className="product-card coupang">
                      <div className="product-image">🖥️</div>
                      <div className="product-info">
                        <h4>모니터 암</h4>
                        <p>모니터 높이 조절을 위한 듀얼 모니터 암</p>
                        <div className="product-price">₩79,000</div>
                        <div className="product-rating">⭐⭐⭐⭐⭐ (4.6/5)</div>
                        <button className="coupang-btn">쿠팡에서 보기</button>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="google-adsense">
                  <h3>📢 Google AdSense</h3>
                  <div className="ad-container">
                    <div className="ad-placeholder">
                      <div className="ad-label">광고</div>
                      <div className="ad-content">
                        <h4>VDT 증후군 전문 클리닉</h4>
                        <p>전문의 진료 및 맞춤 치료 프로그램</p>
                        <p>📞 상담 예약: 1588-0000</p>
                      </div>
                    </div>
                    
                    <div className="ad-placeholder">
                      <div className="ad-label">광고</div>
                      <div className="ad-content">
                        <h4>온라인 운동 클래스</h4>
                        <p>집에서 하는 VDT 증후군 맞춤 운동</p>
                        <p>🎯 첫 달 50% 할인</p>
                      </div>
                    </div>
                    
                    <div className="ad-placeholder">
                      <div className="ad-label">광고</div>
                      <div className="ad-content">
                        <h4>건강 보조식품</h4>
                        <p>관절 건강을 위한 프리미엄 영양제</p>
                        <p>💊 무료 배송 + 30일 체험</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="health-products">
                  <h3>💊 건강 관리 제품</h3>
                  <div className="health-grid">
                    <div className="health-card">
                      <div className="health-icon">🧘‍♀️</div>
                      <h4>요가 매트</h4>
                      <p>집에서 하는 스트레칭과 요가를 위한 전용 매트</p>
                      <div className="health-price">₩39,000</div>
                    </div>
                    
                    <div className="health-card">
                      <div className="health-icon">🏃‍♂️</div>
                      <h4>운동 밴드 세트</h4>
                      <p>근력 강화를 위한 다양한 강도의 저항 밴드</p>
                      <div className="health-price">₩25,000</div>
                    </div>
                    
                    <div className="health-card">
                      <div className="health-icon">🌡️</div>
                      <h4>온열 찜질팩</h4>
                      <p>목과 어깨 통증 완화를 위한 전기 온열팩</p>
                      <div className="health-price">₩45,000</div>
                    </div>
                    
                    <div className="health-card">
                      <div className="health-icon">💆‍♀️</div>
                      <h4>마사지 볼</h4>
                      <p>근육 이완과 혈액순환 개선을 위한 마사지 볼</p>
                      <div className="health-price">₩18,000</div>
                    </div>
                  </div>
                </div>

                <div className="disclaimer">
                  <h4>⚠️ 구매 전 주의사항</h4>
                  <ul>
                    <li>제품 구매 전 전문의와 상담하시기 바랍니다.</li>
                    <li>개인의 증상과 체질에 따라 효과가 다를 수 있습니다.</li>
                    <li>사용 중 불편함이나 통증이 악화되면 즉시 사용을 중단하세요.</li>
                    <li>정확한 사용법을 숙지한 후 사용하시기 바랍니다.</li>
                  </ul>
                </div>
              </div>
            )}
          </section>
        </div>
      )}

      {(aiRecommendation || weeklyRoutine) && (
        <div className="form-actions">
          <button 
            className="btn btn-primary"
            onClick={handleNext}
          >
            ✅ 운동 추천 완료 - 다음 단계로
          </button>
        </div>
      )}
    </div>
  );
};

export default ExerciseRecommendation;