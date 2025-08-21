import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import ProjectModal from '../components/ProjectModal';
import './Projects.css';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000/api';

const Projects = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingProject, setEditingProject] = useState(null);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/projects`);
      
      if (response.data.success) {
        setProjects(response.data.projects);
      }
    } catch (error) {
      console.error('프로젝트 목록 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = () => {
    setEditingProject(null);
    setShowModal(true);
  };

  const handleEditProject = (project) => {
    setEditingProject(project);
    setShowModal(true);
  };

  const handleModalClose = () => {
    setShowModal(false);
    setEditingProject(null);
  };

  const handleProjectSaved = () => {
    loadProjects();
    handleModalClose();
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
      <div className="projects-loading">
        <div className="spinner"></div>
        <p>프로젝트 목록을 불러오는 중...</p>
      </div>
    );
  }

  return (
    <div className="projects">
      {/* 페이지 헤더 */}
      <div className="page-header">
        <div>
          <h1 className="page-title">프로젝트 관리</h1>
          <p className="page-subtitle">블로거 마케팅 프로젝트를 생성하고 관리합니다</p>
        </div>
        <div className="header-actions">
          <button className="btn btn-outline-primary" onClick={loadProjects}>
            <span>🔄</span>
            새로고침
          </button>
          <button className="btn btn-primary" onClick={handleCreateProject}>
            <span>➕</span>
            새 프로젝트
          </button>
        </div>
      </div>

      {/* 프로젝트 테이블 */}
      <div className="card">
        <div className="card-header">
          <h3>프로젝트 목록 ({projects.length}개)</h3>
        </div>
        <div className="card-body">
          {projects.length > 0 ? (
            <div className="table-container">
              <table className="table">
                <thead>
                  <tr>
                    <th>No.</th>
                    <th>프로젝트명</th>
                    <th>검색 키워드</th>
                    <th>제품명</th>
                    <th>상태</th>
                    <th>생성일시</th>
                    <th>수정일시</th>
                    <th>작업</th>
                  </tr>
                </thead>
                <tbody>
                  {projects.map((project, index) => (
                    <tr key={project.id}>
                      <td>{index + 1}</td>
                      <td>
                        <Link to={`/projects/${project.id}`} className="project-link">
                          <strong>{project.name}</strong>
                        </Link>
                      </td>
                      <td>
                        <span className="keyword-tag">{project.keyword}</span>
                      </td>
                      <td>{project.product_name || '-'}</td>
                      <td>{getStatusBadge(project.status)}</td>
                      <td>{formatDate(project.created_at)}</td>
                      <td>{formatDate(project.updated_at)}</td>
                      <td>
                        <div className="action-buttons">
                          <Link 
                            to={`/projects/${project.id}`} 
                            className="btn btn-sm btn-outline-primary"
                          >
                            상세보기
                          </Link>
                          <button 
                            className="btn btn-sm btn-outline-primary"
                            onClick={() => handleEditProject(project)}
                          >
                            수정
                          </button>
                        </div>
                      </td>
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
              <button className="btn btn-primary" onClick={handleCreateProject}>
                <span>➕</span>
                새 프로젝트 생성
              </button>
            </div>
          )}
        </div>
      </div>

      {/* 프로젝트 생성/수정 모달 */}
      {showModal && (
        <ProjectModal
          project={editingProject}
          onClose={handleModalClose}
          onSave={handleProjectSaved}
        />
      )}
    </div>
  );
};

export default Projects;