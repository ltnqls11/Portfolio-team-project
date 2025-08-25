import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Home.css';

const Home = ({ onNavigate }) => {
  const navigate = useNavigate();
  
  const handleStartClick = () => {
    navigate('/condition-selection');
    onNavigate("증상 선택");
  };

  return (
    <div className="home">
      <div className="page-header">
        <h1 className="page-title">직장인들의 건강한 몸상태를 응원합니다.</h1>
      </div>

      <hr className="section-divider" />

      <section className="vdt-info">
        <h2>🏥 VDT 증후군의 주요 근골격계 증상</h2>
        
        <div className="symptoms-grid">
          <div className="symptom-card">
            <h3>🐢 거북목 증후군</h3>
            <p>모니터를 내려다보느라 목이 앞으로 구부러지는 증상</p>
          </div>
          
          <div className="symptom-card">
            <h3>🔴 목디스크</h3>
            <p>고개를 숙이는 자세로 목 디스크에 가해지는 하중 증가</p>
          </div>
          
          <div className="symptom-card">
            <h3>💪 근막통증 증후군</h3>
            <p>근육의 통증 유발점에 의해 발생하는 통증</p>
          </div>
          
          <div className="symptom-card">
            <h3>⌨️ 손목터널 증후군</h3>
            <p>키보드 장시간 사용으로 인한 손가락 저림 및 통증</p>
          </div>
        </div>
      </section>

      <hr className="section-divider" />

      <section className="cta-section">
        <div className="cta-container">
          <button 
            className="btn btn-primary cta-button"
            onClick={handleStartClick}
          >
            🏃‍♂️ <strong>증상 선택하고 건강 관리 시작하기</strong>
          </button>
        </div>
      </section>

      <section className="additional-info">
        <div className="info-grid">
          <div className="info-card">
            <h3>📊 맞춤형 분석</h3>
            <p>개인의 작업환경과 증상을 분석하여 맞춤형 운동 프로그램을 제공합니다.</p>
          </div>
          
          <div className="info-card">
            <h3>🎯 전문 운동 추천</h3>
            <p>VDT 증후군 전문 운동 영상과 스트레칭 가이드를 제공합니다.</p>
          </div>
          
          <div className="info-card">
            <h3>⏰ 스마트 알림</h3>
            <p>작업 강도에 맞는 휴식 알림으로 건강한 업무 습관을 만들어갑니다.</p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;