import React, { useState, useEffect } from 'react';
import './ExerciseManagement.css';

const ExerciseManagement = ({ sessionState }) => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [exerciseLog, setExerciseLog] = useState([]);
  const [todayExercise, setTodayExercise] = useState(null);
  const [weeklyStats, setWeeklyStats] = useState({
    completedDays: 0,
    totalMinutes: 0,
    averagePain: 0,
    streak: 0
  });

  // 모의 데이터 생성
  useEffect(() => {
    generateMockData();
  }, []);

  const generateMockData = () => {
    const today = new Date();
    const mockLog = [];
    
    // 지난 7일간의 운동 기록 생성
    for (let i = 6; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      
      const isExerciseDay = Math.random() > 0.3; // 70% 확률로 운동
      
      if (isExerciseDay) {
        mockLog.push({
          date: date.toISOString().split('T')[0],
          completed: true,
          duration: Math.floor(Math.random() * 30) + 15, // 15-45분
          exercises: sessionState.selectedConditions?.map(condition => ({
            name: `${condition} 운동`,
            duration: Math.floor(Math.random() * 10) + 5,
            completed: true
          })) || [],
          painBefore: Math.floor(Math.random() * 10) + 1,
          painAfter: Math.floor(Math.random() * 6) + 1,
          notes: i === 0 ? '오늘 운동 완료!' : `${7-i}일 전 운동 기록`
        });
      }
    }
    
    setExerciseLog(mockLog);
    
    // 오늘의 운동 설정
    const todayLog = mockLog.find(log => log.date === today.toISOString().split('T')[0]);
    if (!todayLog && sessionState.exerciseSchedule?.availableDays) {
      const todayName = ['일요일', '월요일', '화요일', '수요일', '목요일', '금요일', '토요일'][today.getDay()];
      if (sessionState.exerciseSchedule.availableDays.includes(todayName)) {
        setTodayExercise({
          scheduled: true,
          completed: false,
          exercises: sessionState.selectedConditions?.map(condition => ({
            name: `${condition} 맞춤 운동`,
            duration: Math.floor((sessionState.exerciseSchedule.dailyMinutes || 30) / (sessionState.selectedConditions?.length || 1)),
            completed: false
          })) || []
        });
      }
    }
    
    // 주간 통계 계산
    const completedDays = mockLog.length;
    const totalMinutes = mockLog.reduce((sum, log) => sum + log.duration, 0);
    const averagePain = mockLog.length > 0 
      ? mockLog.reduce((sum, log) => sum + log.painAfter, 0) / mockLog.length 
      : 0;
    
    setWeeklyStats({
      completedDays,
      totalMinutes,
      averagePain: Math.round(averagePain * 10) / 10,
      streak: completedDays
    });
  };

  const handleCompleteExercise = (exerciseIndex) => {
    if (todayExercise) {
      const updatedExercises = [...todayExercise.exercises];
      updatedExercises[exerciseIndex].completed = true;
      
      const allCompleted = updatedExercises.every(ex => ex.completed);
      
      setTodayExercise({
        ...todayExercise,
        exercises: updatedExercises,
        completed: allCompleted
      });
      
      if (allCompleted) {
        // 오늘 운동 완료 시 로그에 추가
        const today = new Date().toISOString().split('T')[0];
        const newLog = {
          date: today,
          completed: true,
          duration: updatedExercises.reduce((sum, ex) => sum + ex.duration, 0),
          exercises: updatedExercises,
          painBefore: Math.floor(Math.random() * 8) + 3,
          painAfter: Math.floor(Math.random() * 5) + 1,
          notes: '오늘 운동 완료!'
        };
        
        setExerciseLog(prev => [...prev, newLog]);
        setWeeklyStats(prev => ({
          ...prev,
          completedDays: prev.completedDays + 1,
          totalMinutes: prev.totalMinutes + newLog.duration,
          streak: prev.streak + 1
        }));
      }
    }
  };

  const userEmail = sessionState.userData?.email || '사용자';

  return (
    <div className="exercise-management">
      <div className="page-header">
        <h1 className="page-title">운동 관리 대시보드</h1>
        <p className="page-subtitle">
          안녕하세요, {userEmail}님! 건강한 운동 습관을 함께 만들어가요. 💪
        </p>
      </div>

      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          📊 대시보드
        </button>
        <button 
          className={`tab ${activeTab === 'today' ? 'active' : ''}`}
          onClick={() => setActiveTab('today')}
        >
          🏃‍♂️ 오늘의 운동
        </button>
        <button 
          className={`tab ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          📈 운동 기록
        </button>
        <button 
          className={`tab ${activeTab === 'analysis' ? 'active' : ''}`}
          onClick={() => setActiveTab('analysis')}
        >
          📋 분석 리포트
        </button>
      </div>

      {activeTab === 'dashboard' && (
        <div className="dashboard-tab">
          <section className="stats-overview">
            <h2>📊 이번 주 운동 현황</h2>
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-icon">🗓️</div>
                <div className="stat-content">
                  <div className="stat-value">{weeklyStats.completedDays}</div>
                  <div className="stat-label">운동 완료 일수</div>
                </div>
              </div>
              
              <div className="stat-card">
                <div className="stat-icon">⏰</div>
                <div className="stat-content">
                  <div className="stat-value">{weeklyStats.totalMinutes}</div>
                  <div className="stat-label">총 운동 시간 (분)</div>
                </div>
              </div>
              
              <div className="stat-card">
                <div className="stat-icon">📉</div>
                <div className="stat-content">
                  <div className="stat-value">{weeklyStats.averagePain}</div>
                  <div className="stat-label">평균 통증 수준</div>
                </div>
              </div>
              
              <div className="stat-card">
                <div className="stat-icon">🔥</div>
                <div className="stat-content">
                  <div className="stat-value">{weeklyStats.streak}</div>
                  <div className="stat-label">연속 운동 일수</div>
                </div>
              </div>
            </div>
          </section>

          <section className="quick-actions">
            <h2>⚡ 빠른 실행</h2>
            <div className="action-grid">
              <button 
                className="action-card"
                onClick={() => setActiveTab('today')}
              >
                <div className="action-icon">🏃‍♂️</div>
                <div className="action-title">오늘의 운동 시작</div>
                <div className="action-desc">맞춤형 운동 루틴 실행</div>
              </button>
              
              <button 
                className="action-card"
                onClick={() => setActiveTab('history')}
              >
                <div className="action-icon">📈</div>
                <div className="action-title">운동 기록 보기</div>
                <div className="action-desc">지난 운동 기록 확인</div>
              </button>
              
              <div className="action-card disabled">
                <div className="action-icon">🎯</div>
                <div className="action-title">목표 설정</div>
                <div className="action-desc">운동 목표 수정 (준비중)</div>
              </div>
              
              <div className="action-card disabled">
                <div className="action-icon">📱</div>
                <div className="action-title">알림 설정</div>
                <div className="action-desc">휴식 알림 관리 (준비중)</div>
              </div>
            </div>
          </section>

          <section className="recent-activity">
            <h2>📝 최근 활동</h2>
            <div className="activity-list">
              {exerciseLog.slice(-3).reverse().map((log, index) => (
                <div key={index} className="activity-item">
                  <div className="activity-date">{log.date}</div>
                  <div className="activity-content">
                    <div className="activity-title">
                      ✅ 운동 완료 ({log.duration}분)
                    </div>
                    <div className="activity-desc">
                      통증 개선: {log.painBefore}점 → {log.painAfter}점
                    </div>
                  </div>
                </div>
              ))}
              
              {exerciseLog.length === 0 && (
                <div className="no-activity">
                  <p>아직 운동 기록이 없습니다.</p>
                  <p>오늘부터 건강한 운동 습관을 시작해보세요! 💪</p>
                </div>
              )}
            </div>
          </section>
        </div>
      )}

      {activeTab === 'today' && (
        <div className="today-tab">
          <section className="today-exercise">
            <h2>🏃‍♂️ 오늘의 운동</h2>
            
            {todayExercise ? (
              <div className="today-workout">
                <div className="workout-header">
                  <h3>📅 {new Date().toLocaleDateString('ko-KR', { 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric',
                    weekday: 'long'
                  })}</h3>
                  <div className={`workout-status ${todayExercise.completed ? 'completed' : 'pending'}`}>
                    {todayExercise.completed ? '✅ 완료' : '⏳ 진행중'}
                  </div>
                </div>

                <div className="exercise-list">
                  {todayExercise.exercises.map((exercise, index) => (
                    <div key={index} className={`exercise-item ${exercise.completed ? 'completed' : ''}`}>
                      <div className="exercise-info">
                        <h4>{exercise.name}</h4>
                        <p>예상 시간: {exercise.duration}분</p>
                      </div>
                      <div className="exercise-actions">
                        {exercise.completed ? (
                          <span className="completed-badge">✅ 완료</span>
                        ) : (
                          <button 
                            className="btn btn-primary"
                            onClick={() => handleCompleteExercise(index)}
                          >
                            완료 표시
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                {todayExercise.completed && (
                  <div className="completion-message">
                    <div className="alert alert-success">
                      🎉 오늘의 운동을 모두 완료했습니다! 수고하셨어요!
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="no-exercise-today">
                <div className="alert alert-info">
                  📅 오늘은 휴식일입니다.
                </div>
                <p>규칙적인 휴식도 건강한 운동 습관의 일부입니다.</p>
                <p>내일 운동을 위해 충분히 휴식하세요! 😊</p>
              </div>
            )}
          </section>

          <section className="exercise-tips">
            <h2>💡 운동 팁</h2>
            <div className="tips-grid">
              <div className="tip-card">
                <h4>🔥 워밍업의 중요성</h4>
                <p>운동 전 5분간 가벼운 스트레칭으로 부상을 예방하세요.</p>
              </div>
              <div className="tip-card">
                <h4>💧 수분 섭취</h4>
                <p>운동 중과 후에 충분한 물을 마셔 탈수를 방지하세요.</p>
              </div>
              <div className="tip-card">
                <h4>🎯 꾸준함이 핵심</h4>
                <p>강도보다는 꾸준함이 더 중요합니다. 매일 조금씩이라도 실천하세요.</p>
              </div>
            </div>
          </section>
        </div>
      )}

      {activeTab === 'history' && (
        <div className="history-tab">
          <section className="exercise-history">
            <h2>📈 운동 기록</h2>
            
            {exerciseLog.length > 0 ? (
              <div className="history-list">
                {exerciseLog.slice().reverse().map((log, index) => (
                  <div key={index} className="history-item">
                    <div className="history-date">
                      <div className="date-display">{log.date}</div>
                      <div className="duration-display">{log.duration}분</div>
                    </div>
                    
                    <div className="history-content">
                      <div className="exercises-completed">
                        <h4>완료한 운동</h4>
                        <ul>
                          {log.exercises.map((exercise, idx) => (
                            <li key={idx}>{exercise.name} ({exercise.duration}분)</li>
                          ))}
                        </ul>
                      </div>
                      
                      <div className="pain-improvement">
                        <h4>통증 개선</h4>
                        <div className="pain-comparison">
                          <span className="pain-before">운동 전: {log.painBefore}점</span>
                          <span className="pain-arrow">→</span>
                          <span className="pain-after">운동 후: {log.painAfter}점</span>
                          <span className={`pain-change ${log.painBefore > log.painAfter ? 'improved' : 'same'}`}>
                            ({log.painBefore > log.painAfter ? '-' : ''}{Math.abs(log.painBefore - log.painAfter)}점)
                          </span>
                        </div>
                      </div>
                      
                      {log.notes && (
                        <div className="exercise-notes">
                          <h4>메모</h4>
                          <p>{log.notes}</p>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-history">
                <p>아직 운동 기록이 없습니다.</p>
                <p>첫 운동을 시작해보세요! 🚀</p>
              </div>
            )}
          </section>
        </div>
      )}

      {activeTab === 'analysis' && (
        <div className="analysis-tab">
          <section className="analysis-report">
            <h2>📋 분석 리포트</h2>
            
            <div className="analysis-summary">
              <div className="alert alert-info">
                📊 <strong>운동 분석 리포트</strong> (최근 7일 기준)
              </div>
              
              <div className="analysis-grid">
                <div className="analysis-card">
                  <h3>🎯 운동 달성률</h3>
                  <div className="achievement-rate">
                    {sessionState.exerciseSchedule?.availableDays ? 
                      Math.round((weeklyStats.completedDays / sessionState.exerciseSchedule.availableDays.length) * 100) : 0}%
                  </div>
                  <p>
                    계획된 {sessionState.exerciseSchedule?.availableDays?.length || 0}일 중 {weeklyStats.completedDays}일 완료
                  </p>
                </div>
                
                <div className="analysis-card">
                  <h3>📉 통증 개선도</h3>
                  <div className="pain-improvement-rate">
                    {weeklyStats.averagePain > 0 ? 
                      `평균 ${weeklyStats.averagePain}점` : 
                      '데이터 없음'
                    }
                  </div>
                  <p>
                    {weeklyStats.averagePain <= 3 ? '좋음' : 
                     weeklyStats.averagePain <= 6 ? '보통' : '개선 필요'}
                  </p>
                </div>
                
                <div className="analysis-card">
                  <h3>⏰ 운동 시간</h3>
                  <div className="time-analysis">
                    주 {weeklyStats.totalMinutes}분
                  </div>
                  <p>
                    일평균 {Math.round(weeklyStats.totalMinutes / 7)}분
                  </p>
                </div>
              </div>
            </div>

            <div className="recommendations">
              <h3>💡 개선 제안</h3>
              <div className="recommendation-list">
                {weeklyStats.completedDays < 3 && (
                  <div className="recommendation-item">
                    <span className="rec-icon">📅</span>
                    <div className="rec-content">
                      <h4>운동 빈도 증가</h4>
                      <p>주 3회 이상 운동하시면 더 좋은 효과를 볼 수 있습니다.</p>
                    </div>
                  </div>
                )}
                
                {weeklyStats.averagePain > 6 && (
                  <div className="recommendation-item">
                    <span className="rec-icon">🏥</span>
                    <div className="rec-content">
                      <h4>전문의 상담</h4>
                      <p>통증이 지속되고 있습니다. 전문의 상담을 받아보세요.</p>
                    </div>
                  </div>
                )}
                
                {weeklyStats.totalMinutes < 90 && (
                  <div className="recommendation-item">
                    <span className="rec-icon">⏰</span>
                    <div className="rec-content">
                      <h4>운동 시간 증가</h4>
                      <p>주 150분 이상 운동하시면 건강에 더 도움이 됩니다.</p>
                    </div>
                  </div>
                )}
                
                {weeklyStats.completedDays >= 5 && weeklyStats.averagePain <= 4 && (
                  <div className="recommendation-item success">
                    <span className="rec-icon">🎉</span>
                    <div className="rec-content">
                      <h4>훌륭합니다!</h4>
                      <p>꾸준한 운동으로 좋은 결과를 얻고 계십니다. 계속 유지하세요!</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </section>
        </div>
      )}
    </div>
  );
};

export default ExerciseManagement;