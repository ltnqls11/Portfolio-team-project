import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Bloggers.css';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000/api';

const Bloggers = () => {
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState('');
  const [bloggers, setBloggers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 10,
    total: 0,
    pages: 0
  });

  useEffect(() => {
    loadProjects();
  }, []);

  useEffect(() => {
    if (selectedProject) {
      loadBloggers();
    }
  }, [selectedProject, pagination.page]);

  const loadProjects = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/projects`);
      if (response.data.success) {
        setProjects(response.data.projects);
        if (response.data.projects.length > 0) {
          setSelectedProject(response.data.projects[0].id);
        }
      }
    } catch (error) {
      console.error('프로젝트 목록 로드 실패:', error);
    }
  };

  const loadBloggers = async () => {
    if (!selectedProject) return;

    try {
      setLoading(true);
      const response = await axios.get(
        `${API_BASE_URL}/projects/${selectedProject}/bloggers`,
        {
          params: {
            page: pagination.page,
            per_page: pagination.per_page
          }
        }
      );
      
      if (response.data.success) {
        setBloggers(response.data.bloggers);
        setPagination(prev => ({
          ...prev,
          ...response.data.pagination
        }));
      }
    } catch (error) {
      console.error('블로거 목록 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleProjectChange = (e) => {
    setSelectedProject(e.target.value);
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handlePageChange = (newPage) => {
    setPagination(prev => ({ ...prev, page: newPage }));
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

  const selectedProjectInfo = projects.find(p => p.id === selectedProject);

  return (
    <div className="bloggers">
      {/* 페이지 헤더 */}
      <div className="page-header">
        <div>
          <h1 className="page-title">블로거 관리</h1>
          <p className="page-subtitle">수집된 블로거 정보를 확인하고 관리합니다</p>
        </div>
        <div className="header-actions">
          <button className="btn btn-outline-primary" onClick={loadBloggers}>
            <span>🔄</span>
            새로고침
          </button>
        </div>
      </div>

      {/* 프로젝트 선택 */}
      <div className="card mb-3">
        <div className="card-body">
          <div className="row align-items-center">
            <div className="col-4">
              <div className="form-group">
                <label className="form-label">프로젝트 선택</label>
                <select 
                  className="form-control"
                  value={selectedProject}
                  onChange={handleProjectChange}
                >
                  <option value="">프로젝트를 선택하세요</option>
                  {projects.map(project => (
                    <option key={project.id} value={project.id}>
                      {project.name} ({project.keyword})
                    </option>
                  ))}
                </select>
              </div>
            </div>
            {selectedProjectInfo && (
              <div className="col-8">
                <div className="project-summary">
                  <div className="summary-item">
                    <span className="label">키워드:</span>
                    <span className="value">{selectedProjectInfo.keyword}</span>
                  </div>
                  <div className="summary-item">
                    <span className="label">제품명:</span>
                    <span className="value">{selectedProjectInfo.product_name || '-'}</span>
                  </div>
                  <div className="summary-item">
                    <span className="label">상태:</span>
                    <span className="value">
                      <span className={`badge badge-${selectedProjectInfo.status.includes('completed') ? 'success' : 'secondary'}`}>
                        {selectedProjectInfo.status}
                      </span>
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 블로거 목록 */}
      <div className="card">
        <div className="card-header">
          <h3>
            블로거 목록 
            {selectedProjectInfo && ` - ${selectedProjectInfo.name}`}
            {pagination.total > 0 && ` (${pagination.total}명)`}
          </h3>
        </div>
        <div className="card-body">
          {loading ? (
            <div className="loading-state">
              <div className="spinner"></div>
              <p>블로거 목록을 불러오는 중...</p>
            </div>
          ) : bloggers.length > 0 ? (
            <>
              <div className="table-container">
                <table className="table">
                  <thead>
                    <tr>
                      <th>No.</th>
                      <th>블로그명</th>
                      <th>이메일</th>
                      <th>블로그 URL</th>
                      <th>이메일 발송</th>
                      <th>발송일시</th>
                      <th>수집일시</th>
                    </tr>
                  </thead>
                  <tbody>
                    {bloggers.map((blogger, index) => (
                      <tr key={blogger.id}>
                        <td>{(pagination.page - 1) * pagination.per_page + index + 1}</td>
                        <td>
                          <a 
                            href={blogger.blog_url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="blogger-link"
                          >
                            {blogger.blog_name}
                          </a>
                        </td>
                        <td>
                          {blogger.email ? (
                            <a href={`mailto:${blogger.email}`} className="email-link">
                              {blogger.email}
                            </a>
                          ) : (
                            <span className="text-muted">-</span>
                          )}
                        </td>
                        <td>
                          <a 
                            href={blogger.blog_url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="url-link"
                          >
                            블로그 방문
                          </a>
                        </td>
                        <td>
                          {blogger.email_sent ? (
                            <span className="badge badge-success">발송완료</span>
                          ) : blogger.email ? (
                            <span className="badge badge-warning">미발송</span>
                          ) : (
                            <span className="badge badge-secondary">이메일없음</span>
                          )}
                        </td>
                        <td>{formatDate(blogger.email_sent_at)}</td>
                        <td>{formatDate(blogger.created_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* 페이지네이션 */}
              {pagination.pages > 1 && (
                <div className="pagination-container">
                  <div className="pagination">
                    <button 
                      className="btn btn-sm btn-outline-primary"
                      onClick={() => handlePageChange(pagination.page - 1)}
                      disabled={!pagination.has_prev}
                    >
                      이전
                    </button>
                    
                    <span className="page-info">
                      {pagination.page} / {pagination.pages} 페이지
                    </span>
                    
                    <button 
                      className="btn btn-sm btn-outline-primary"
                      onClick={() => handlePageChange(pagination.page + 1)}
                      disabled={!pagination.has_next}
                    >
                      다음
                    </button>
                  </div>
                </div>
              )}
            </>
          ) : selectedProject ? (
            <div className="empty-state">
              <div className="empty-icon">👥</div>
              <h3>수집된 블로거가 없습니다</h3>
              <p>선택한 프로젝트에서 블로거 수집을 먼저 실행하세요.</p>
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-icon">📁</div>
              <h3>프로젝트를 선택하세요</h3>
              <p>블로거 정보를 확인할 프로젝트를 선택해주세요.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Bloggers;