import React, { useState } from 'react';
import { UserInfo, Symptom, PainLocation, WorkEnvironment, DailyHabits, Mode } from '../types';
import './UserInfoForm.css';

interface UserInfoFormProps {
  onSubmit: (userInfo: UserInfo) => void;
}

const UserInfoForm: React.FC<UserInfoFormProps> = ({ onSubmit }) => {
  const [formData, setFormData] = useState<Partial<UserInfo>>({
    symptoms: [],
    painLocation: [],
    painSeverity: 3,
    workEnvironment: 'office_desk',
    dailyHabits: 'sedentary',
    age: 30,
    workplace: '',
    homeLocation: '',
    workingHours: {
      start: '09:00',
      end: '18:00'
    },
    mode: 'prevention'
  });

  const symptoms: { value: Symptom; label: string }[] = [
    { value: 'turtle_neck', label: '거북목' },
    { value: 'rounded_shoulders', label: '둥근 어깨' },
    { value: 'disc_herniation', label: '디스크 탈출증' },
    { value: 'carpal_tunnel_syndrome', label: '손목 터널 증후군' }
  ];

  const painLocations: { value: PainLocation; label: string }[] = [
    { value: 'neck', label: '목' },
    { value: 'shoulders', label: '어깨' },
    { value: 'back', label: '허리' },
    { value: 'wrist', label: '손목' },
    { value: 'arms', label: '팔' },
    { value: 'legs', label: '다리' }
  ];

  const workEnvironments: { value: WorkEnvironment; label: string }[] = [
    { value: 'office_desk', label: '사무실 책상' },
    { value: 'standing_work', label: '서서 하는 작업' },
    { value: 'manual_labor', label: '육체 노동' },
    { value: 'driving', label: '운전' },
    { value: 'home_office', label: '재택 근무' }
  ];

  const dailyHabits: { value: DailyHabits; label: string }[] = [
    { value: 'sedentary', label: '거의 움직이지 않음' },
    { value: 'moderate_activity', label: '가벼운 활동' },
    { value: 'active', label: '활동적' },
    { value: 'very_active', label: '매우 활동적' }
  ];

  const modes: { value: Mode; label: string }[] = [
    { value: 'prevention', label: '예방' },
    { value: 'exercise', label: '운동' },
    { value: 'rehabilitation', label: '재활' }
  ];

  const handleSymptomChange = (symptom: Symptom) => {
    setFormData(prev => ({
      ...prev,
      symptoms: prev.symptoms?.includes(symptom)
        ? prev.symptoms.filter(s => s !== symptom)
        : [...(prev.symptoms || []), symptom]
    }));
  };

  const handlePainLocationChange = (location: PainLocation) => {
    setFormData(prev => ({
      ...prev,
      painLocation: prev.painLocation?.includes(location)
        ? prev.painLocation.filter(l => l !== location)
        : [...(prev.painLocation || []), location]
    }));
  };

  const handleInputChange = (field: keyof UserInfo, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.symptoms && formData.symptoms.length > 0) {
      onSubmit(formData as UserInfo);
    } else {
      alert('최소 하나의 증상을 선택해주세요.');
    }
  };

  return (
    <div className="user-info-form">
      <h2>건강 정보 입력</h2>
      <form onSubmit={handleSubmit}>
        {/* 증상 선택 */}
        <div className="form-section">
          <h3>증상 선택 (복수 선택 가능)</h3>
          <div className="checkbox-group">
            {symptoms.map(symptom => (
              <label key={symptom.value} className="checkbox-item">
                <input
                  type="checkbox"
                  checked={formData.symptoms?.includes(symptom.value) || false}
                  onChange={() => handleSymptomChange(symptom.value)}
                />
                {symptom.label}
              </label>
            ))}
          </div>
        </div>

        {/* 통증 위치 */}
        <div className="form-section">
          <h3>통증 위치 (복수 선택 가능)</h3>
          <div className="checkbox-group">
            {painLocations.map(location => (
              <label key={location.value} className="checkbox-item">
                <input
                  type="checkbox"
                  checked={formData.painLocation?.includes(location.value) || false}
                  onChange={() => handlePainLocationChange(location.value)}
                />
                {location.label}
              </label>
            ))}
          </div>
        </div>

        {/* 통증 심각도 */}
        <div className="form-section">
          <h3>통증 심각도 (1-5점)</h3>
          <div className="pain-severity">
            {[1, 2, 3, 4, 5].map(level => (
              <label key={level} className="radio-item">
                <input
                  type="radio"
                  name="painSeverity"
                  value={level}
                  checked={formData.painSeverity === level}
                  onChange={(e) => handleInputChange('painSeverity', parseInt(e.target.value))}
                />
                {level}점
              </label>
            ))}
          </div>
        </div>

        {/* 작업 환경 */}
        <div className="form-section">
          <h3>작업 환경</h3>
          <select
            value={formData.workEnvironment}
            onChange={(e) => handleInputChange('workEnvironment', e.target.value)}
          >
            {workEnvironments.map(env => (
              <option key={env.value} value={env.value}>
                {env.label}
              </option>
            ))}
          </select>
        </div>

        {/* 일상 습관 */}
        <div className="form-section">
          <h3>일상 활동량</h3>
          <select
            value={formData.dailyHabits}
            onChange={(e) => handleInputChange('dailyHabits', e.target.value)}
          >
            {dailyHabits.map(habit => (
              <option key={habit.value} value={habit.value}>
                {habit.label}
              </option>
            ))}
          </select>
        </div>

        {/* 나이 */}
        <div className="form-section">
          <h3>나이</h3>
          <input
            type="number"
            min="10"
            max="100"
            value={formData.age}
            onChange={(e) => handleInputChange('age', parseInt(e.target.value))}
            placeholder="나이를 입력하세요"
          />
        </div>

        {/* 직장 위치 */}
        <div className="form-section">
          <h3>직장 위치</h3>
          <input
            type="text"
            value={formData.workplace}
            onChange={(e) => handleInputChange('workplace', e.target.value)}
            placeholder="직장 위치를 입력하세요"
          />
        </div>

        {/* 집 위치 */}
        <div className="form-section">
          <h3>집 위치</h3>
          <input
            type="text"
            value={formData.homeLocation}
            onChange={(e) => handleInputChange('homeLocation', e.target.value)}
            placeholder="집 위치를 입력하세요"
          />
        </div>

        {/* 근무 시간 */}
        <div className="form-section">
          <h3>근무 시간</h3>
          <div className="time-inputs">
            <div>
              <label>시작 시간:</label>
              <input
                type="time"
                value={formData.workingHours?.start}
                onChange={(e) => handleInputChange('workingHours', {
                  ...formData.workingHours,
                  start: e.target.value
                })}
              />
            </div>
            <div>
              <label>종료 시간:</label>
              <input
                type="time"
                value={formData.workingHours?.end}
                onChange={(e) => handleInputChange('workingHours', {
                  ...formData.workingHours,
                  end: e.target.value
                })}
              />
            </div>
          </div>
        </div>

        {/* 모드 선택 */}
        <div className="form-section">
          <h3>운동 모드</h3>
          <select
            value={formData.mode}
            onChange={(e) => handleInputChange('mode', e.target.value)}
          >
            {modes.map(mode => (
              <option key={mode.value} value={mode.value}>
                {mode.label}
              </option>
            ))}
          </select>
        </div>

        <button type="submit" className="submit-btn">
          운동 추천 받기
        </button>
      </form>
    </div>
  );
};

export default UserInfoForm;
