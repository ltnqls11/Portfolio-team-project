import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000/api';

function App() {
  const [config, setConfig] = useState({
    keyword: '',
    sheetId: '',
    sheetName: '',
    productName: '',
    eventInfo: ''
  });
  
  const [status, setStatus] = useState({
    scraping: false,
    emailSending: false,
    cafePosting: false,
    completeAutomation: false
  });
  
  const [logs, setLogs] = useState([]);
  const [bloggers, setBloggers] = useState([]);

  // 로그 추가 함수
  const addLog = (message, type = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, { timestamp, message, type }]);
  };

  // API 서버 상태 확인
  useEffect(() => {
    checkServerHealth();
  }, []);

  const checkServerHealth = async () => {
    try {
      await axios.get(`${API_BASE_URL}/health`);
      addLog('API 서버 연결 성공', 'success');
    } catch (error) {
      addLog('API 서버 연결 실패. 서버를 시작해주세요.', 'error');
    }
  };

  // 설정 저장
  const saveConfig = async () => {
    try {
      await axios.post(`${API_BASE_URL}/config`, {
        sheet_id: config.sheetId,
        sheet_name: config.sheetName
      });
      addLog('설정이 저장되었습니다.', 'success');
    } catch (error) {
      addLog(`설정 저장 실패: ${error.message}`, 'error');
    }
  };

  // 1단계: 네이버 블로그 스크래핑
  const startScraping = async () => {
    if (!config.keyword || !config.sheetId || !config.sheetName) {
      addLog('키워드, 시트 ID, 시트 이름을 모두 입력해주세요.', 'error');
      return;
    }

    setStatus(prev => ({ ...prev, scraping: true }));
    addLog(`스크래핑 시작: "${config.keyword}"`, 'info');

    try {
      const response = await axios.post(`${API_BASE_URL}/scrape`, {
        keyword: config.keyword,
        sheet_id: config.sheetId,
        sheet_name: config.sheetName
      });

      if (response.data.success) {
        addLog('스크래핑 완료!', 'success');
        loadBloggers(); // 블로거 목록 새로고침
      } else {
        addLog(`스크래핑 실패: ${response.data.error}`, 'error');
      }
    } catch (error) {
      addLog(`스크래핑 오류: ${error.message}`, 'error');
    } finally {
      setStatus(prev => ({ ...prev, scraping: false }));
    }
  };

  // 블로거 목록 로드
  const loadBloggers = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/bloggers`, {
        params: {
          sheet_id: config.sheetId,
          sheet_name: config.sheetName
        }
      });

      if (response.data.success) {
        setBloggers(response.data.bloggers);
        addLog(`블로거 ${response.data.count}명 로드됨`, 'success');
      }
    } catch (error) {
      addLog(`블로거 목록 로드 실패: ${error.message}`, 'error');
    }
  };

  // 2단계: n8n 이메일 워크플로우 실행
  const triggerEmailWorkflow = async () => {
    if (!config.productName) {
      addLog('제품명을 입력해주세요.', 'error');
      return;
    }

    if (!config.sheetId || !config.sheetName) {
      addLog('Google Sheets ID와 시트 이름을 입력해주세요.', 'error');
      return;
    }

    setStatus(prev => ({ ...prev, emailSending: true }));
    addLog('이메일 발송 워크플로우 실행 중...', 'info');

    try {
      // n8n 웹훅 URL - .env 파일에서 설정 로드
      const n8nBaseUrl = process.env.REACT_APP_N8N_BASE_URL || 'http://localhost:5678';
      const emailWebhookId = process.env.REACT_APP_N8N_EMAIL_WEBHOOK_ID || 'webhook-email-start';
      const webhookUrl = `${n8nBaseUrl}/webhook/${emailWebhookId}`;
      
      const requestData = {
        productName: config.productName,
        sheet_id: config.sheetId,
        sheet_name: config.sheetName,
        timestamp: new Date().toISOString()
      };

      addLog(`n8n 웹훅 호출: ${webhookUrl}`, 'info');
      const response = await axios.post(webhookUrl, requestData);

      addLog('✅ 이메일 발송 워크플로우가 성공적으로 실행되었습니다!', 'success');
      addLog(`응답: ${JSON.stringify(response.data)}`, 'info');
    } catch (error) {
      addLog(`❌ 이메일 워크플로우 실행 실패: ${error.message}`, 'error');
      if (error.response) {
        addLog(`서버 응답: ${JSON.stringify(error.response.data)}`, 'error');
      }
    } finally {
      setStatus(prev => ({ ...prev, emailSending: false }));
    }
  };

  // 3단계: n8n 카페 포스팅 워크플로우 실행
  const triggerCafeWorkflow = async () => {
    if (!config.productName || !config.eventInfo) {
      addLog('제품명과 이벤트 정보를 모두 입력해주세요.', 'error');
      return;
    }

    setStatus(prev => ({ ...prev, cafePosting: true }));
    addLog('카페 포스팅 워크플로우 실행 중...', 'info');

    try {
      // n8n 웹훅 URL - .env 파일에서 설정 로드
      const n8nBaseUrl = process.env.REACT_APP_N8N_BASE_URL || 'http://localhost:5678';
      const cafeWebhookId = process.env.REACT_APP_N8N_CAFE_WEBHOOK_ID || 'webhook-cafe-post';
      const webhookUrl = `${n8nBaseUrl}/webhook/${cafeWebhookId}`;
      
      const requestData = {
        productName: config.productName,
        eventInfo: config.eventInfo,
        timestamp: new Date().toISOString()
      };

      addLog(`n8n 웹훅 호출: ${webhookUrl}`, 'info');
      const response = await axios.post(webhookUrl, requestData);

      addLog('✅ 카페 포스팅 워크플로우가 성공적으로 실행되었습니다!', 'success');
      addLog(`응답: ${JSON.stringify(response.data)}`, 'info');
    } catch (error) {
      addLog(`❌ 카페 워크플로우 실행 실패: ${error.message}`, 'error');
      if (error.response) {
        addLog(`서버 응답: ${JSON.stringify(error.response.data)}`, 'error');
      }
    } finally {
      setStatus(prev => ({ ...prev, cafePosting: false }));
    }
  };

  // 🚀 완전한 자동화: 모든 단계를 한 번에 실행 (n8n 없이 독립 실행)
  const runCompleteAutomation = async () => {
    if (!config.keyword || !config.sheetId || !config.sheetName || !config.productName) {
      addLog('모든 필수 정보를 입력해주세요. (키워드, 시트 ID, 시트 이름, 제품명)', 'error');
      return;
    }

    setStatus(prev => ({ ...prev, completeAutomation: true }));
    addLog('🚀 완전한 자동화 프로세스 시작!', 'info');
    addLog('①블로거 정보 수집 → ②이메일 발송 → ③카페 포스팅을 순차적으로 실행합니다.', 'info');

    try {
      const requestData = {
        keyword: config.keyword,
        sheet_id: config.sheetId,
        sheet_name: config.sheetName,
        product_name: config.productName,
        event_info: config.eventInfo || '특별 할인 이벤트',
        sender_name: '마케팅팀'
      };

      addLog('완전한 자동화 API 호출 중...', 'info');
      const response = await axios.post(`${API_BASE_URL}/complete-automation`, requestData);

      if (response.data.success) {
        addLog('🎉 완전한 자동화 프로세스가 성공적으로 완료되었습니다!', 'success');
        addLog('✅ ①블로거 정보 수집 완료', 'success');
        addLog('✅ ②이메일 자동 발송 완료', 'success');
        addLog('✅ ③네이버 카페 자동 포스팅 완료', 'success');
        loadBloggers(); // 블로거 목록 새로고침
      } else {
        addLog(`❌ 완전한 자동화 실패: ${response.data.error}`, 'error');
      }
    } catch (error) {
      addLog(`❌ 완전한 자동화 오류: ${error.message}`, 'error');
      if (error.response) {
        addLog(`서버 응답: ${JSON.stringify(error.response.data)}`, 'error');
      }
    } finally {
      setStatus(prev => ({ ...prev, completeAutomation: false }));
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🤖 블로거 마케팅 RPA 제어판</h1>
        <p>네이버 블로그 인플루언서 자동화 시스템</p>
      </header>

      <main className="App-main">
        {/* 설정 섹션 */}
        <section className="config-section">
          <h2>⚙️ 기본 설정</h2>
          <div className="form-group">
            <label>검색 키워드:</label>
            <input
              type="text"
              value={config.keyword}
              onChange={(e) => setConfig(prev => ({ ...prev, keyword: e.target.value }))}
              placeholder="예: 내돈내산 영양"
            />
          </div>
          
          <div className="form-group">
            <label>Google Sheets ID:</label>
            <input
              type="text"
              value={config.sheetId}
              onChange={(e) => setConfig(prev => ({ ...prev, sheetId: e.target.value }))}
              placeholder="Google Sheets 문서 ID"
            />
          </div>
          
          <div className="form-group">
            <label>시트 이름:</label>
            <input
              type="text"
              value={config.sheetName}
              onChange={(e) => setConfig(prev => ({ ...prev, sheetName: e.target.value }))}
              placeholder="Sheet1"
            />
          </div>
          
          <div className="form-group">
            <label>제품명:</label>
            <input
              type="text"
              value={config.productName}
              onChange={(e) => setConfig(prev => ({ ...prev, productName: e.target.value }))}
              placeholder="마케팅할 제품명"
            />
          </div>
          
          <div className="form-group">
            <label>이벤트 정보:</label>
            <input
              type="text"
              value={config.eventInfo}
              onChange={(e) => setConfig(prev => ({ ...prev, eventInfo: e.target.value }))}
              placeholder="특별 할인 이벤트"
            />
          </div>
          
          <button onClick={saveConfig} className="btn btn-secondary">
            설정 저장
          </button>
        </section>

        {/* 완전한 자동화 섹션 */}
        <section className="complete-automation-section">
          <h2>🚀 완전한 자동화 (원클릭 실행)</h2>
          <div className="complete-automation-card">
            <h3>🤖 모든 단계 자동 실행</h3>
            <p>①블로거 정보 수집 → ②이메일 발송 → ③카페 포스팅을 한 번에 실행합니다.</p>
            <p><strong>n8n 없이 독립적으로 동작합니다!</strong></p>
            <button 
              onClick={runCompleteAutomation} 
              disabled={status.completeAutomation || !config.keyword || !config.sheetId || !config.sheetName || !config.productName}
              className="btn btn-complete"
            >
              {status.completeAutomation ? '🔄 자동화 실행 중...' : '🚀 완전한 자동화 시작'}
            </button>
          </div>
        </section>

        {/* 개별 실행 버튼들 */}
        <section className="actions-section">
          <h2>🔧 개별 단계 실행</h2>
          
          <div className="action-card">
            <h3>1단계: 블로거 정보 수집</h3>
            <p>네이버 블로그에서 인플루언서 정보를 수집합니다.</p>
            <button 
              onClick={startScraping} 
              disabled={status.scraping}
              className="btn btn-primary"
            >
              {status.scraping ? '수집 중...' : '블로거 정보 수집 시작'}
            </button>
          </div>

          <div className="action-card">
            <h3>2단계: 이메일 발송 (n8n)</h3>
            <p>수집된 블로거들에게 마케팅 이메일을 발송합니다.</p>
            <button 
              onClick={triggerEmailWorkflow} 
              disabled={status.emailSending}
              className="btn btn-success"
            >
              {status.emailSending ? '발송 중...' : '이메일 발송 시작'}
            </button>
          </div>

          <div className="action-card">
            <h3>3단계: 카페 포스팅 (n8n)</h3>
            <p>네이버 카페에 제품 홍보 글을 자동으로 게시합니다.</p>
            <button 
              onClick={triggerCafeWorkflow} 
              disabled={status.cafePosting}
              className="btn btn-warning"
            >
              {status.cafePosting ? '포스팅 중...' : '카페 포스팅 시작'}
            </button>
          </div>
        </section>

        {/* 블로거 목록 */}
        <section className="bloggers-section">
          <h2>👥 수집된 블로거 목록 ({bloggers.length}명)</h2>
          <button onClick={loadBloggers} className="btn btn-secondary">
            목록 새로고침
          </button>
          
          <div className="bloggers-list">
            {bloggers.map((blogger, index) => (
              <div key={index} className="blogger-card">
                <h4>{blogger.blog_name}</h4>
                <p>📧 {blogger.email}</p>
                <p>🔗 <a href={blogger.blog_url} target="_blank" rel="noopener noreferrer">블로그 방문</a></p>
              </div>
            ))}
          </div>
        </section>

        {/* 로그 섹션 */}
        <section className="logs-section">
          <h2>📋 실행 로그</h2>
          <div className="logs-container">
            {logs.map((log, index) => (
              <div key={index} className={`log-entry log-${log.type}`}>
                <span className="log-time">{log.timestamp}</span>
                <span className="log-message">{log.message}</span>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;