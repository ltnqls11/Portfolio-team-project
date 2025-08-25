import React, { useState } from 'react';
import ProgressHeader from './common/ProgressHeader';
import './ExerciseSurvey.css';

const ExerciseSurvey = ({ sessionState, updateSessionState, onNavigate, progress }) => {
  const [exerciseSchedule, setExerciseSchedule] = useState({
    availableDays: sessionState.exerciseSchedule?.availableDays || [],
    dailyMinutes: sessionState.exerciseSchedule?.dailyMinutes || 30,
    preferredTime: sessionState.exerciseSchedule?.preferredTime || '언제든지',
    difficultyLevel: sessionState.exerciseSchedule?.difficultyLevel || '초급자',
    exerciseGoals: sessionState.exerciseSchedule?.exerciseGoals || [],
    currentFitness: sessionState.exerciseSchedule?.currentFitness || '낮음',
    previousInjuries: sessionState.exerciseSchedule?.previousInjuries || '없음'
  });

  const weekDays = [
    '월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일'
  ];

  const exerciseGoalOptions = [
    '통증 완화', '자세 교정', '근력 강화', '유연성 향상', '스트레스 해소', '체중 관리'
  ];

  const handleDayToggle = (day) => {
    const newDays = exerciseSchedule.availableDays.includes(day)
      ? exerciseSchedule.availableDays.filter(d => d !== day)
      : [...exerciseSchedule.availableDays, day];
    
    setExerciseSchedule(prev => ({
      ...prev,
      availableDays: newDays,
      totalWeeklyMinutes: newDays.length * prev.dailyMinutes
    }));
  };

  const handleGoalToggle = (goal) => {
    const newGoals = exerciseSchedule.exerciseGoals.includes(goal)
      ? exerciseSchedule.exerciseGoals.filter(g => g !== goal)
      : [...exerciseSchedule.exerciseGoals, goal];
    
    setExerciseSchedule(prev => ({
      ...prev,
      exerciseGoals: newGoals
    }));
  };

  const handleInputChange = (field, value) => {
    setExerciseSchedule(prev => {
      const updated = {
        ...prev,
        [field]: value
      };
      
      // 일일 운동 시간이 변경되면 주간 총 시간도 업데이트
      if (field === 'dailyMinutes') {
        updated.totalWeeklyMinutes = prev.availableDays.length * value;
      }
      
      return updated;
    });
  };

  const handleNext = () => {
    const updatedUserData = {
      ...sessionState.userData,
      exerciseSchedule: exerciseSchedule
    };

    const updatedStepsCompleted = [...sessionState.stepsCompleted];
    updatedStepsCompleted[3] = true;

    updateSessionState({
      userData: updatedUserData,
      exerciseSchedule: exerciseSchedule,
      stepsCompleted: updatedStepsCompleted,
      currentStep: 4
    });

    onNavigate("운동 추천");
    // React Router로 직접 이동
    window.location.href = '/exercise-recommendation';
  };

  const isFormValid = exerciseSchedule.availableDays.length > 0 && exerciseSchedule.exerciseGoals.length > 0;
  const totalWeeklyMinutes = exerciseSchedule.availableDays.length * exerciseSchedule.dailyMinutes;

  if (!sessionState.selectedConditions || sessionState.selectedConditions.length === 0) {
    return (
      <div className="exercise-survey">
        <div className="alert alert-warning">
          먼저 증상을 선택해주세요.
        </div>
      </div>
    );
  }

  return (
    <div className="exercise-survey">
      <div className="page-header">
        <h1 className="page-title">개인 운동 설문조사</h1>
      </div>

      <ProgressHeader progress={progress} />

      <hr className="section-divider" />

      <section className="schedule-section">
        <h2>📅 운동 가능 시간</h2>
        <p className="section-description">
          일주일 중 운동이 가능한 요일과 시간을 선택해주세요.
        </p>

        <div className="form-group">
          <label className="form-label">운동 가능한 요일 (복수 선택 가능)</label>
          <div className="days-grid">
            {weekDays.map(day => (
              <label key={day} className="day-checkbox">
                <input
                  type="checkbox"
                  checked={exerciseSchedule.availableDays.includes(day)}
                  onChange={() => handleDayToggle(day)}
                />
                <span className="day-label">{day}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="time-settings">
          <div className="form-group">
            <label className="form-label">
              하루 운동 시간: {exerciseSchedule.dailyMinutes}분
            </label>
            <input
              type="range"
              className="slider"
              min="15"
              max="120"
              step="15"
              value={exerciseSchedule.dailyMinutes}
              onChange={(e) => handleInputChange('dailyMinutes', parseInt(e.target.value))}
            />
            <div className="slider-labels">
              <span>15분</span>
              <span>60분</span>
              <span>120분</span>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">선호하는 운동 시간대</label>
            <select
              className="form-control"
              value={exerciseSchedule.preferredTime}
              onChange={(e) => handleInputChange('preferredTime', e.target.value)}
            >
              <option value="언제든지">언제든지</option>
              <option value="아침 (06:00-09:00)">아침 (06:00-09:00)</option>
              <option value="오전 (09:00-12:00)">오전 (09:00-12:00)</option>
              <option value="점심시간 (12:00-14:00)">점심시간 (12:00-14:00)</option>
              <option value="오후 (14:00-18:00)">오후 (14:00-18:00)</option>
              <option value="저녁 (18:00-21:00)">저녁 (18:00-21:00)</option>
              <option value="밤 (21:00-24:00)">밤 (21:00-24:00)</option>
            </select>
          </div>
        </div>

        {exerciseSchedule.availableDays.length > 0 && (
          <div className="schedule-summary">
            <h4>📊 운동 계획 요약</h4>
            <div className="summary-grid">
              <div className="summary-item">
                <span className="summary-label">선택된 요일</span>
                <span className="summary-value">{exerciseSchedule.availableDays.join(', ')}</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">주간 운동 일수</span>
                <span className="summary-value">{exerciseSchedule.availableDays.length}일</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">일일 운동 시간</span>
                <span className="summary-value">{exerciseSchedule.dailyMinutes}분</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">주간 총 시간</span>
                <span className="summary-value">{totalWeeklyMinutes}분</span>
              </div>
            </div>
          </div>
        )}
      </section>

      <hr className="section-divider" />

      <section className="goals-section">
        <h2>🎯 운동 목표</h2>
        <p className="section-description">
          운동을 통해 달성하고 싶은 목표를 선택해주세요. (복수 선택 가능)
        </p>

        <div className="goals-grid">
          {exerciseGoalOptions.map(goal => (
            <label key={goal} className="goal-checkbox">
              <input
                type="checkbox"
                checked={exerciseSchedule.exerciseGoals.includes(goal)}
                onChange={() => handleGoalToggle(goal)}
              />
              <span className="goal-label">{goal}</span>
            </label>
          ))}
        </div>
      </section>

      <hr className="section-divider" />

      <section className="fitness-section">
        <h2>💪 현재 체력 수준 및 경험</h2>
        
        <div className="form-grid">
          <div className="form-group">
            <label className="form-label">운동 난이도 수준</label>
            <select
              className="form-control"
              value={exerciseSchedule.difficultyLevel}
              onChange={(e) => handleInputChange('difficultyLevel', e.target.value)}
            >
              <option value="초급자">초급자 (운동 경험 거의 없음)</option>
              <option value="초중급">초중급 (가끔 운동함)</option>
              <option value="중급자">중급자 (규칙적으로 운동함)</option>
              <option value="중상급">중상급 (운동을 즐겨함)</option>
              <option value="상급자">상급자 (전문적으로 운동함)</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">현재 체력 수준</label>
            <select
              className="form-control"
              value={exerciseSchedule.currentFitness}
              onChange={(e) => handleInputChange('currentFitness', e.target.value)}
            >
              <option value="매우 낮음">매우 낮음</option>
              <option value="낮음">낮음</option>
              <option value="보통">보통</option>
              <option value="높음">높음</option>
              <option value="매우 높음">매우 높음</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">과거 운동 부상 경험</label>
            <select
              className="form-control"
              value={exerciseSchedule.previousInjuries}
              onChange={(e) => handleInputChange('previousInjuries', e.target.value)}
            >
              <option value="없음">없음</option>
              <option value="목/어깨 부상">목/어깨 부상</option>
              <option value="허리 부상">허리 부상</option>
              <option value="손목/팔 부상">손목/팔 부상</option>
              <option value="기타 부상">기타 부상</option>
            </select>
          </div>
        </div>
      </section>

      <div className="form-actions">
        {isFormValid ? (
          <button 
            className="btn btn-primary"
            onClick={handleNext}
          >
            ✅ 설문 완료 - 다음 단계로
          </button>
        ) : (
          <div className="alert alert-warning">
            ⚠️ 운동 가능한 요일과 운동 목표를 선택해주세요.
          </div>
        )}
      </div>
    </div>
  );
};

export default ExerciseSurvey;