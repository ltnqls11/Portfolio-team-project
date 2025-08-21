import React, { useState } from 'react';
import { UserInfo, Symptom, PainLocation, WorkEnvironment, DailyHabits, Mode } from '../types';
import './UserInfoForm.css';

interface UserInfoFormProps {
  onSubmit: (userInfo: UserInfo) => void;
  initialData?: Partial<UserInfo>;
}

const UserInfoForm: React.FC<UserInfoFormProps> = ({ onSubmit, initialData }) => {
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
    mode: 'prevention',
    ...initialData
  });

  const [currentStep, setCurrentStep] = useState(1);
  const totalSteps = 4;

  const symptoms: { value: Symptom; label: string; description: string }[] = [
    { value: 'turtle_neck', label: '거북목', description: '목이 앞으로 나온 상태' },
    { value: 'rounded_shoulders', label: '둥근 어깨', description: '어깨가 앞으로 굽은 상태' },
    { value: 'disc_herniation', label: '디스크 탈출증', description: '허리 디스크 문제' },
    { value: 'carpal_tunnel_syndrome', label: '손목 터널 증후군', description: '손목 통증 및 저림' }
  ];

  const painLocations: { value: PainLocation; label: string }[] = [
    { value: 'neck', label: '목' },
    { value: 'shoulders', label: '어깨' },
    { value: 'back', label: '허리' },
    { value: 'wrist', label: '손목' },
    { value: 'arms', label: '팔' },
    { value: 'legs', label: '다리' }
  ];

  const workEnvironments: { value: WorkEnvironment; label: string; description: string }[] = [
    { value: 'office_desk', label: '사무실 책상', description: '주로 앉아서 컴퓨터 작업' },
    { value: 'standing_work', label: '서서 하는 작업', description: '서서 하는 업무' },
    { value: 'manual_labor', label: '육체 노동', description: '힘든 육체 작업' },
    { value: 'driving', label: '운전', description: '장시간 운전' },
    { value: 'home_office', label: '재택 근무', description: '집에서 원격 근무' }
  ];

  const dailyHabits: { value: DailyHabits; label: string; description: string }[] = [
    { value: 'sedentary', label: '거의 움직이지 않음', description: '하루 대부분 앉아있음' },
    { value: 'moderate_activity', label: '가벼운 활동', description: '가끔 걷기나 간단한 운동' },
    { value: 'active', label: '활동적', description: '정기적으로 운동함' },
    { value: 'very_active', label: '매우 활동적', description: '매일 운동하거나 스포츠 활동' }
  ];

  const modes: { value: Mode; label: string; description: string }[] = [
    { value: 'prevention', label: '예방', description: '증상이 없지만 예방하고 싶음' },
    { value: 'exercise', label: '운동', description: '일반적인 건강 관리 운동' },
    { value: 'rehabilitation', label: '재활', description: '기존 증상 개선을 위한 운동' }
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

  const nextStep = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.symptoms && formData.symptoms.length > 0) {
      onSubmit(formData as UserInfo);
    } else {
      alert('최소 하나의 증상을 선택해주세요.');
    }
  };

  const renderStepIndicator = () => (
    <div className="step-indicator">
      {Array.from({ length: totalSteps }, (_, i) => (
        <div
          key={i}
          className={`step ${i + 1 === currentStep ? 'active' : i + 1 < currentStep ? 'completed' : ''}`}
        >
          <span className="step-number">{i + 1}</span>
          <span className="step-label">
            {i === 0 && '증상'}
            {i === 1 && '환경'}
            {i === 2 && '정보'}
            {i === 3 && '완료'}
          </span>
        </div>
      ))}
    </div>
  );

  const renderStep1 = () => (
    <div className="form-step">
      <h2>증상과 통증 위치를 알려주세요</h2>
      <p className="step-description">현재 겪고 계신 증상을 선택해주세요. 복수 선택이 가능합니다.</p>
      
      <div className="form-section">
        <h3>증상 선택</h3>
        <div className="symptoms-grid">
          {symptoms.map(symptom => (
            <label key={symptom.value} className={`symptom-card ${formData.symptoms?.includes(symptom.value) ? 'selected' : ''}`}>
              <input
                type="checkbox"
                checked={formData.symptoms?.includes(symptom.value) || false}
                onChange={() => handleSymptomChange(symptom.value)}
              />
              <div className="symptom-content">
                <h4>{symptom.label}</h4>
                <p>{symptom.description}</p>
              </div>
            </label>
          ))}
        </div>
      </div>

      <div className="form-section">
        <h3>통증 위치</h3>
        <div className="pain-locations">
          {painLocations.map(location => (
            <label key={location.value} className={`pain-location ${formData.painLocation?.includes(location.value) ? 'selected' : ''}`}>
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

      <div className="form-section">
        <h3>통증 심각도</h3>
        <div className="pain-severity">
          <div className="severity-labels">
            <span>약함</span>
            <span>강함</span>
          </div>
          <div className="severity-buttons">
            {[1, 2, 3, 4, 5].map(level => (
              <button
                key={level}
                type="button"
                className={`severity-btn ${formData.painSeverity === level ? 'selected' : ''}`}
                onClick={() => handleInputChange('painSeverity', level)}
              >
                {level}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="form-step">
      <h2>작업 환경과 생활 습관을 알려주세요</h2>
      <p className="step-description">일상적인 활동과 작업 환경을 선택해주세요.</p>
      
      <div className="form-section">
        <h3>작업 환경</h3>
        <div className="environment-grid">
          {workEnvironments.map(env => (
            <label key={env.value} className={`environment-card ${formData.workEnvironment === env.value ? 'selected' : ''}`}>
              <input
                type="radio"
                name="workEnvironment"
                value={env.value}
                checked={formData.workEnvironment === env.value}
                onChange={(e) => handleInputChange('workEnvironment', e.target.value)}
              />
              <div className="environment-content">
                <h4>{env.label}</h4>
                <p>{env.description}</p>
              </div>
            </label>
          ))}
        </div>
      </div>

      <div className="form-section">
        <h3>일상 활동량</h3>
        <div className="habits-grid">
          {dailyHabits.map(habit => (
            <label key={habit.value} className={`habit-card ${formData.dailyHabits === habit.value ? 'selected' : ''}`}>
              <input
                type="radio"
                name="dailyHabits"
                value={habit.value}
                checked={formData.dailyHabits === habit.value}
                onChange={(e) => handleInputChange('dailyHabits', e.target.value)}
              />
              <div className="habit-content">
                <h4>{habit.label}</h4>
                <p>{habit.description}</p>
              </div>
            </label>
          ))}
        </div>
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div className="form-step">
      <h2>개인 정보와 운동 목표를 설정해주세요</h2>
      <p className="step-description">더 정확한 운동 추천을 위한 정보입니다.</p>
      
      <div className="form-section">
        <h3>기본 정보</h3>
        <div className="basic-info-grid">
          <div className="input-group">
            <label>나이</label>
            <input
              type="number"
              min="10"
              max="100"
              value={formData.age}
              onChange={(e) => handleInputChange('age', parseInt(e.target.value))}
              placeholder="나이를 입력하세요"
            />
          </div>
          <div className="input-group">
            <label>직장 위치</label>
            <input
              type="text"
              value={formData.workplace}
              onChange={(e) => handleInputChange('workplace', e.target.value)}
              placeholder="직장 위치를 입력하세요"
            />
          </div>
          <div className="input-group">
            <label>집 위치</label>
            <input
              type="text"
              value={formData.homeLocation}
              onChange={(e) => handleInputChange('homeLocation', e.target.value)}
              placeholder="집 위치를 입력하세요"
            />
          </div>
        </div>
      </div>

      <div className="form-section">
        <h3>근무 시간</h3>
        <div className="working-hours">
          <div className="time-input">
            <label>시작 시간</label>
            <input
              type="time"
              value={formData.workingHours?.start}
              onChange={(e) => handleInputChange('workingHours', {
                ...formData.workingHours,
                start: e.target.value
              })}
            />
          </div>
          <div className="time-input">
            <label>종료 시간</label>
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

      <div className="form-section">
        <h3>운동 목표</h3>
        <div className="mode-grid">
          {modes.map(mode => (
            <label key={mode.value} className={`mode-card ${formData.mode === mode.value ? 'selected' : ''}`}>
              <input
                type="radio"
                name="mode"
                value={mode.value}
                checked={formData.mode === mode.value}
                onChange={(e) => handleInputChange('mode', e.target.value)}
              />
              <div className="mode-content">
                <h4>{mode.label}</h4>
                <p>{mode.description}</p>
              </div>
            </label>
          ))}
        </div>
      </div>
    </div>
  );

  const renderStep4 = () => (
    <div className="form-step">
      <h2>입력 정보 확인</h2>
      <p className="step-description">입력하신 정보를 확인해주세요.</p>
      
      <div className="summary-section">
        <div className="summary-card">
          <h3>선택한 증상</h3>
          <div className="summary-tags">
            {formData.symptoms?.map(symptom => (
              <span key={symptom} className="summary-tag">
                {symptoms.find(s => s.value === symptom)?.label}
              </span>
            ))}
          </div>
        </div>

        <div className="summary-card">
          <h3>작업 환경</h3>
          <p>{workEnvironments.find(w => w.value === formData.workEnvironment)?.label}</p>
        </div>

        <div className="summary-card">
          <h3>운동 목표</h3>
          <p>{modes.find(m => m.value === formData.mode)?.label}</p>
        </div>
      </div>

      <div className="submit-section">
        <button type="submit" className="submit-btn">
          운동 추천 받기
        </button>
      </div>
    </div>
  );

  return (
    <div className="user-info-form">
      {renderStepIndicator()}
      
      <form onSubmit={handleSubmit}>
        {currentStep === 1 && renderStep1()}
        {currentStep === 2 && renderStep2()}
        {currentStep === 3 && renderStep3()}
        {currentStep === 4 && renderStep4()}

        <div className="form-navigation">
          {currentStep > 1 && (
            <button type="button" onClick={prevStep} className="nav-btn prev">
              이전
            </button>
          )}
          {currentStep < totalSteps && (
            <button type="button" onClick={nextStep} className="nav-btn next">
              다음
            </button>
          )}
        </div>
      </form>
    </div>
  );
};

export default UserInfoForm;
