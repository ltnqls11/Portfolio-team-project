import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Dashboard.css';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000/api';

const Dashboard = () => {
  const [stats, setStats] = useState({
    total_projects: 0,
    total_bloggers: 0,
    emails_sent: 0,
    success_rate: 0
  });
  const [recentProjects, setRecentProjects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/dashboard/stats`);
      
      if (response.data.success) {
        setStats(response.data.stats);
        setRecentProjects(response.data.recent_projects);
      }
    } catch (error) {
      console.error('대시보드 데이터 로드 실패:', error);
    } finally {
      setLoading(false);
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
      <div className="dashboard-loading">
        <div className="spinner"></div>
        <p>대시보드 데이터를 불러오는 중...</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      {/* 페이지 헤더 */}
      <div className="page-header">
        <div>
          <h1 className="page-title">대시보드</h1>
          <p className="page-subtitle">블로거 마케팅 RPA 시스템 현황</p>
        </div>
        <button className="btn btn-primary" onClick={loadDashboardData}>
          <span>🔄</span>
          새로고침
        </button>
      </div>

      {/* 통계 카드들 */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon projects">📁</div>
          <div className="stat-content">
            <div className="stat-value">{stats.total_projects.toLocaleString()}</div>
            <div className="stat-label">총 프로젝트</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon bloggers">👥</div>
          <div className="stat-content">
            <div className="stat-value">{stats.total_bloggers.toLocaleString()}</div>
            <div className="stat-label">수집된 블로거</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon emails">📧</div>
          <div className="stat-content">
            <div className="stat-value">{stats.emails_sent.toLocaleString()}</div>
            <div className="stat-label">발송된 이메일</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon success">📈</div>
          <div className="stat-content">
            <div className="stat-value">{stats.success_rate}%</div>
            <div className="stat-label">성공률</div>
          </div>
        </div>
      </div>

      {/* 최근 프로젝트 테이블 (첨부 이미지 스타일) */}
      <div className="card">
        <div className="card-header">
          <h3>최근 프로젝트</h3>
        </div>
        <div className="card-body">
          {recentProjects.length > 0 ? (
            <div className="table-container">
              <table className="table">
                <thead>
                  <tr>
                    <th>No.</th>
                    <th>프로젝트명</th>
                    <th>검색 키워드</th>
                    <th>상태</th>
                    <th>제품명</th>
                    <th>생성일시</th>
                    <th>수정일시</th>
                  </tr>
                </thead>
                <tbody>
                  {recentProjects.map((project, index) => (
                    <tr key={project.id}>
                      <td>{index + 1}</td>
                      <td>
                        <div className="project-name">
                          <strong>{project.name}</strong>
                        </div>
                      </td>
                      <td>
                        <span className="keyword-tag">{project.keyword}</span>
                      </td>
                      <td>{getStatusBadge(project.status)}</td>
                      <td>{project.product_name || '-'}</td>
                      <td>{formatDate(project.created_at)}</td>
                      <td>{formatDate(project.updated_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-icon">📁</div>
              <h3>프로젝트가 없습니다</h3>
              <p>새 프로젝트를 생성하여 블로거 마케팅을 시작하세요.</p>
              <button className="btn btn-primary">
                <span>➕</span>
                새 프로젝트 생성
              </button>
            </div>
          )}
        </div>
      </div>

      {/* 빠른 액션 */}
      <div className="quick-actions">
        <h3>빠른 실행</h3>
        <div className="action-grid">
          <div className="action-card">
            <div className="action-icon">🕷️</div>
            <h4>블로거 수집</h4>
            <p>네이버 블로그에서 인플루언서 정보를 수집합니다.</p>
            <button className="btn btn-outline-primary">시작하기</button>
          </div>

          <div className="action-card">
            <div className="action-icon">📧</div>
            <h4>이메일 발송</h4>
            <p>수집된 블로거들에게 마케팅 이메일을 발송합니다.</p>
            <button className="btn btn-outline-primary">시작하기</button>
          </div>

          <div className="action-card">
            <div className="action-icon">📝</div>
            <h4>카페 포스팅</h4>
            <p>네이버 카페에 제품 홍보 글을 자동으로 게시합니다.</p>
            <button className="btn btn-outline-primary">시작하기</button>
          </div>

          <div className="action-card featured">
            <div className="action-icon">🚀</div>
            <h4>완전 자동화</h4>
            <p>모든 과정을 한 번에 자동으로 실행합니다.</p>
            <button className="btn btn-primary">시작하기</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;