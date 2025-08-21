import React, { useState } from 'react';
import './Settings.css';

const Settings = () => {
  const [settings, setSettings] = useState({
    googleSheetsId: '',
    defaultSheetName: 'Sheet1',
    naverClientId: '',
    naverClientSecret: '',
    naverCafeId: '',
    naverMenuId: '',
    emailSender: '마케팅팀',
    autoEmailSend: false,
    autoCafePost: false
  });

  const [saved, setSaved] = useState(false);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setSettings(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSave = () => {
    // 실제로는 API로 설정을 저장해야 함
    console.log('설정 저장:', settings);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="settings">
      {/* 페이지 헤더 */}
      <div className="page-header">
        <div>
          <h1 className="page-title">시스템 설정</h1>
          <p className="page-subtitle">RPA 시스템의 기본 설정을 관리합니다</p>
        </div>
        <div className="header-actions">
          <button 
            className={`btn ${saved ? 'btn-success' : 'btn-primary'}`}
            onClick={handleSave}
          >
            {saved ? '✅ 저장됨' : '💾 설정 저장'}
          </button>
        </div>
      </div>

      <div className="row">
        {/* Google Sheets 설정 */}
        <div className="col-6">
          <div className="card">
            <div className="card-header">
              <h3>📊 Google Sheets 설정</h3>
            </div>
            <div className="card-body">
              <div className="form-group">
                <label className="form-label">기본 Google Sheets ID</label>
                <input
                  type="text"
                  name="googleSheetsId"
                  value={settings.googleSheetsId}
                  onChange={handleInputChange}
                  className="form-control"
                  placeholder="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
                />
                <small className="form-text">새 프로젝트 생성 시 기본값으로 사용됩니다.</small>
              </div>
              
              <div className="form-group">
                <label className="form-label">기본 시트 이름</label>
                <input
                  type="text"
                  name="defaultSheetName"
                  value={settings.defaultSheetName}
                  onChange={handleInputChange}
                  className="form-control"
                  placeholder="Sheet1"
                />
              </div>
            </div>
          </div>
        </div>

        {/* 네이버 API 설정 */}
        <div className="col-6">
          <div className="card">
            <div className="card-header">
              <h3>🔑 네이버 API 설정</h3>
            </div>
            <div className="card-body">
              <div className="form-group">
                <label className="form-label">클라이언트 ID</label>
                <input
                  type="text"
                  name="naverClientId"
                  value={settings.naverClientId}
                  onChange={handleInputChange}
                  className="form-control"
                  placeholder="네이버 개발자 센터에서 발급받은 ID"
                />
              </div>
              
              <div className="form-group">
                <label className="form-label">클라이언트 시크릿</label>
                <input
                  type="password"
                  name="naverClientSecret"
                  value={settings.naverClientSecret}
                  onChange={handleInputChange}
                  className="form-control"
                  placeholder="네이버 개발자 센터에서 발급받은 시크릿"
                />
              </div>
              
              <div className="row">
                <div className="col-6">
                  <div className="form-group">
                    <label className="form-label">카페 ID</label>
                    <input
                      type="text"
                      name="naverCafeId"
                      value={settings.naverCafeId}
                      onChange={handleInputChange}
                      className="form-control"
                      placeholder="12345678"
                    />
                  </div>
                </div>
                <div className="col-6">
                  <div className="form-group">
                    <label className="form-label">메뉴 ID</label>
                    <input
                      type="text"
                      name="naverMenuId"
                      value={settings.naverMenuId}
                      onChange={handleInputChange}
                      className="form-control"
                      placeholder="87654321"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 이메일 설정 */}
      <div className="card">
        <div className="card-header">
          <h3>📧 이메일 설정</h3>
        </div>
        <div className="card-body">
          <div className="row">
            <div className="col-4">
              <div className="form-group">
                <label className="form-label">발신자명</label>
                <input
                  type="text"
                  name="emailSender"
                  value={settings.emailSender}
                  onChange={handleInputChange}
                  className="form-control"
                  placeholder="마케팅팀"
                />
              </div>
            </div>
            <div className="col-8">
              <div className="form-group">
                <label className="form-label">자동화 옵션</label>
                <div className="checkbox-group">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      name="autoEmailSend"
                      checked={settings.autoEmailSend}
                      onChange={handleInputChange}
                    />
                    <span>블로거 수집 완료 시 자동으로 이메일 발송</span>
                  </label>
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      name="autoCafePost"
                      checked={settings.autoCafePost}
                      onChange={handleInputChange}
                    />
                    <span>이메일 발송 완료 시 자동으로 카페 포스팅</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 시스템 정보 */}
      <div className="card">
        <div className="card-header">
          <h3>ℹ️ 시스템 정보</h3>
        </div>
        <div className="card-body">
          <div className="system-info-grid">
            <div className="info-item">
              <label>시스템 버전</label>
              <span>BloggerRPA v2.0.0</span>
            </div>
            <div className="info-item">
              <label>백엔드 상태</label>
              <span className="status-online">온라인</span>
            </div>
            <div className="info-item">
              <label>데이터베이스</label>
              <span>SQLite (blogger_rpa.db)</span>
            </div>
            <div className="info-item">
              <label>마지막 업데이트</label>
              <span>{new Date().toLocaleDateString('ko-KR')}</span>
            </div>
          </div>
        </div>
      </div>

      {/* 도움말 */}
      <div className="card">
        <div className="card-header">
          <h3>❓ 도움말</h3>
        </div>
        <div className="card-body">
          <div className="help-section">
            <h4>Google Sheets ID 찾는 방법</h4>
            <p>Google Sheets URL에서 ID를 확인할 수 있습니다:</p>
            <code>https://docs.google.com/spreadsheets/d/[SHEET_ID]/edit#gid=0</code>
            
            <h4>네이버 API 설정 방법</h4>
            <ol>
              <li><a href="https://developers.naver.com/" target="_blank" rel="noopener noreferrer">네이버 개발자 센터</a>에서 애플리케이션 등록</li>
              <li>카페 API 권한 신청</li>
              <li>발급받은 클라이언트 ID와 시크릿을 입력</li>
              <li>포스팅할 카페의 ID와 메뉴 ID 확인 후 입력</li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;