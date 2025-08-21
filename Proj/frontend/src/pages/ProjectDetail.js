import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import './ProjectDetail.css';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000/api';

const ProjectDetail = () => {
  const { id } = useParams();
  const [project, setProject] = useState(null);
  const [bloggers, setBloggers] = useState([]);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [automationLoading, setAutomationLoading] = useState(false);

  useEffect(() => {
    loadProjectData();
  }, [id]);

  const loadProjectData = async () => {
    try {
      setLoading(true);
      
      // 프로젝트 정보 로드
      const projectResponse = await axios.get(`${API_BASE_URL}/projects/${id}`);
      if (projectResponse.data.success) {
        setProject(projectResponse.data.project);
      }

      // 블로거 목록 로드
      const bloggersResponse = await axios.get(`${API_BASE_URL}/projects/${id}/bloggers`);
      if (bloggersResponse.data.success) {
        setBloggers(bloggersResponse.data.bloggers);
      }

      // 로그 로드
      const logsResponse = await axios.get(`${API_BASE_URL}/projects/${id}/logs`);
      if (logsResponse.data.success) {
        setLogs(logsResponse.data.logs);
      }

    } catch (error) {
      console.error('프로젝트 데이터 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStartScraping = async () => {
    try {
      setAutomationLoading(true);
      const response = await axios.post(`${API_BASE_URL}/projects/${id}/scrape`);
      
      if (response.data.success) {
        alert('블로거 정보 수집이 완료되었습니다!');
        loadProjectData(); // 데이터 새로고침
      } else {
        alert(`수집 실패: ${response.data.error}`);
      }
    } catch (error) {
      alert(`오류 발생: ${error.message}`);
    } finally {
      setAutomationLoading(false);
    }
  };

  const handleCompleteAutomation = async () => {
    try {
      setAutomationLoading(true);
      const response = await axios.post(`${API_BASE_URL}/projects/${id}/complete-automation`);
      
      if (response.data.success) {
        alert('완전한 자동화가 완료되었습니다!');
        loadProjectData(); // 데이터 새로고침
      } else {
        alert(`자동화 실패: ${response.data.error}`);
      }
    } catch (error) {
      alert(`오류 발생: ${error.message}`);
    } finally {
      setAutomationLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusMap = {
      'created': { class: 'badge-secondary', text: '생성됨' },
      'scraping': { class: 'badge-warning', text: '수집중' },
      'scraping_completed': { class: 'badge-success', text: '수집완료' },
      'scraping_failed': { class: 'badge-danger', text: '수집실패' },
      'automation_running': { class: 'badge-info', text: '자동화중' },
      'automation_completed': { class: 'badge-success', text: '완료' },
      'automation_failed': { class: 'badge-danger', text: '실패' }
    };
    
    const statusInfo = statusMap[status] || { class: 'badge-secondary', text: status };
    return <span className={`badge ${statusInfo.class}`}>{statusInfo.text}</span>;
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="project-detail-loading">
        <div className="spinner"></div>
        <p>프로젝트 정보를 불러오는 중...</p>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="project-not-found">
        <h2>프로젝트를 찾을 수 없습니다</h2>
        <Link to="/projects" className="btn btn-primary">프로젝트 목록으로</Link>
      </div>
    );
  }

  return (
    <div className="project-detail">
      {/* 페이지 헤더 */}
      <div className="page-header">
        <div>
          <div className="breadcrumb">
            <Link to="/projects">프로젝트</Link> / {project.name}
          </div>
          <h1 className="page-title">{project.name}</h1>
          <p className="page-subtitle">키워드: {project.keyword}</p>
        </div>
        <div className="header-actions">
          <button 
            className="btn btn-primary"
            onClick={handleStartScraping}
            disabled={automationLoading}
          >
            {automationLoading ? '실행 중...' : '블로거 수집'}
          </button>
          <button 
            className="btn btn-success"
            onClick={handleCompleteAutomation}
            disabled={automationLoading || !project.product_name}
          >
            {automationLoading ? '실행 중...' : '완전 자동화'}
          </button>
        </div>
      </div>

      {/* 프로젝트 정보 카드 */}
      <div className="row">
        <div className="col-8">
          <div className="card">
            <div className="card-header">
              <h3>프로젝트 정보</h3>
            </div>
            <div className="card-body">
              <div className="project-info-grid">
                <div className="info-item">
                  <label>상태</label>
                  <div>{getStatusBadge(project.status)}</div>
                </div>
                <div className="info-item">
                  <label>검색 키워드</label>
                  <div>{project.keyword}</div>
                </div>
                <div className="info-item">
                  <label>제품명</label>
                  <div>{project.product_name || '-'}</div>
                </div>
                <div className="info-item">
                  <label>Google Sheets</label>
                  <div>{project.sheet_name}</div>
                </div>
                <div className="info-item">
                  <label>생성일시</label>
                  <div>{formatDate(project.created_at)}</div>
                </div>
                <div className="info-item">
                  <label>수정일시</label>
                  <div>{formatDate(project.updated_at)}</div>
                </div>
              </div>
              {project.event_info && (
                <div className="event-info">
                  <label>이벤트 정보</label>
                  <p>{project.event_info}</p>
                </div>
              )}
            </div>
          </div>
        </div>
        
        <div className="col-4">
          <div className="card">
            <div className="card-header">
              <h3>통계</h3>
            </div>
            <div className="card-body">
              <div className="stats">
                <div className="stat-item">
                  <div className="stat-value">{bloggers.length}</div>
                  <div className="stat-label">수집된 블로거</div>
                </div>
                <div className="stat-item">
                  <div className="stat-value">{bloggers.filter(b => b.email).length}</div>
                  <div className="stat-label">이메일 보유</div>
                </div>
                <div className="stat-item">
                  <div className="stat-value">{bloggers.filter(b => b.email_sent).length}</div>
                  <div className="stat-label">이메일 발송</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 블로거 목록 */}
      <div className="card">
        <div className="card-header">
          <h3>수집된 블로거 목록 ({bloggers.length}명)</h3>
        </div>
        <div className="card-body">
          {bloggers.length > 0 ? (
            <div className="table-container">
              <table className="table">
                <thead>
                  <tr>
                    <th>No.</th>
                    <th>블로그명</th>
                    <th>이메일</th>
                    <th>이메일 발송</th>
                    <th>수집일시</th>
                    <th>작업</th>
                  </tr>
                </thead>
                <tbody>
                  {bloggers.map((blogger, index) => (
                    <tr key={blogger.id}>
                      <td>{index + 1}</td>
                      <td>
                        <a href={blogger.blog_url} target="_blank" rel="noopener noreferrer">
                          {blogger.blog_name}
                        </a>
                      </td>
                      <td>{blogger.email || '-'}</td>
                      <td>
                        {blogger.email_sent ? (
                          <span className="badge badge-success">발송완료</span>
                        ) : (
                          <span className="badge badge-secondary">미발송</span>
                        )}
                      </td>
                      <td>{formatDate(blogger.created_at)}</td>
                      <td>
                        <a 
                          href={blogger.post_url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="btn btn-sm btn-outline-primary"
                        >
                          포스트 보기
                        </a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-icon">👥</div>
              <h3>수집된 블로거가 없습니다</h3>
              <p>블로거 수집을 시작하여 데이터를 수집하세요.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProjectDetail;