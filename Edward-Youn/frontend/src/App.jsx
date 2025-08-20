import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [healthStatus, setHealthStatus] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // 백엔드 API 헬스 체크
    fetch('http://localhost:8000/health')
      .then(response => response.json())
      .then(data => {
        setHealthStatus(data)
        setLoading(false)
      })
      .catch(error => {
        console.error('API 연결 실패:', error)
        setLoading(false)
      })
  }, [])

  return (
    <div className="App">
      <header className="App-header">
        <h1>🌟 온라인 마케팅 연계 플랫폼</h1>
        <p>기업과 인플루언서를 연결하는 올인원 마케팅 자동화 플랫폼</p>
        
        <div className="status-card">
          <h3>🔍 시스템 상태</h3>
          {loading ? (
            <p>연결 확인 중...</p>
          ) : healthStatus ? (
            <div className="status-success">
              <p>✅ 백엔드 API: {healthStatus.status}</p>
              <p>📡 서비스: {healthStatus.service}</p>
            </div>
          ) : (
            <div className="status-error">
              <p>❌ 백엔드 API 연결 실패</p>
              <p>백엔드 서버가 실행 중인지 확인하세요</p>
            </div>
          )}
        </div>

        <div className="features-grid">
          <div className="feature-card">
            <h3>📊 캠페인 관리</h3>
            <p>마케팅 캠페인을 생성하고 관리합니다</p>
          </div>
          
          <div className="feature-card">
            <h3>👥 크리에이터 관리</h3>
            <p>인플루언서를 검색하고 연결합니다</p>
          </div>
          
          <div className="feature-card">
            <h3>✍️ 문구 생성</h3>
            <p>AI 기반 홍보 문구를 자동 생성합니다</p>
          </div>
          
          <div className="feature-card">
            <h3>🕷️ 크롤링</h3>
            <p>네이버, 인스타그램 데이터를 수집합니다</p>
          </div>
        </div>

        <div className="api-links">
          <h3>🔗 API 문서</h3>
          <a 
            href="http://localhost:8000/docs" 
            target="_blank" 
            rel="noopener noreferrer"
            className="api-link"
          >
            📖 Swagger UI
          </a>
          <a 
            href="http://localhost:8000/redoc" 
            target="_blank" 
            rel="noopener noreferrer"
            className="api-link"
          >
            📚 ReDoc
          </a>
        </div>
      </header>
    </div>
  )
}

export default App