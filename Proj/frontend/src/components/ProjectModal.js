import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './ProjectModal.css';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000/api';

const ProjectModal = ({ project, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    name: '',
    keyword: '',
    sheet_id: '',
    sheet_name: 'Sheet1',
    product_name: '',
    event_info: ''
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (project) {
      setFormData({
        name: project.name || '',
        keyword: project.keyword || '',
        sheet_id: project.sheet_id || '',
        sheet_name: project.sheet_name || 'Sheet1',
        product_name: project.product_name || '',
        event_info: project.event_info || ''
      });
    }
  }, [project]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // 에러 제거
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.name.trim()) {
      newErrors.name = '프로젝트명은 필수입니다.';
    }
    
    if (!formData.keyword.trim()) {
      newErrors.keyword = '검색 키워드는 필수입니다.';
    }
    
    if (!formData.sheet_id.trim()) {
      newErrors.sheet_id = 'Google Sheets ID는 필수입니다.';
    }
    
    if (!formData.sheet_name.trim()) {
      newErrors.sheet_name = '시트 이름은 필수입니다.';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    try {
      setLoading(true);
      
      let response;
      if (project) {
        // 수정
        response = await axios.put(`${API_BASE_URL}/projects/${project.id}`, formData);
      } else {
        // 생성
        response = await axios.post(`${API_BASE_URL}/projects`, formData);
      }
      
      if (response.data.success) {
        onSave();
      }
    } catch (error) {
      console.error('프로젝트 저장 실패:', error);
      if (error.response?.data?.error) {
        setErrors({ general: error.response.data.error });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{project ? '프로젝트 수정' : '새 프로젝트 생성'}</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        
        <form onSubmit={handleSubmit} className="modal-body">
          {errors.general && (
            <div className="error-message">{errors.general}</div>
          )}
          
          <div className="form-group">
            <label className="form-label">프로젝트명 *</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              className={`form-control ${errors.name ? 'error' : ''}`}
              placeholder="예: 영양제 마케팅 프로젝트"
            />
            {errors.name && <div className="field-error">{errors.name}</div>}
          </div>
          
          <div className="form-group">
            <label className="form-label">검색 키워드 *</label>
            <input
              type="text"
              name="keyword"
              value={formData.keyword}
              onChange={handleInputChange}
              className={`form-control ${errors.keyword ? 'error' : ''}`}
              placeholder="예: 내돈내산 영양제"
            />
            {errors.keyword && <div className="field-error">{errors.keyword}</div>}
          </div>
          
          <div className="row">
            <div className="col-8">
              <div className="form-group">
                <label className="form-label">Google Sheets ID *</label>
                <input
                  type="text"
                  name="sheet_id"
                  value={formData.sheet_id}
                  onChange={handleInputChange}
                  className={`form-control ${errors.sheet_id ? 'error' : ''}`}
                  placeholder="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
                />
                {errors.sheet_id && <div className="field-error">{errors.sheet_id}</div>}
              </div>
            </div>
            <div className="col-4">
              <div className="form-group">
                <label className="form-label">시트 이름 *</label>
                <input
                  type="text"
                  name="sheet_name"
                  value={formData.sheet_name}
                  onChange={handleInputChange}
                  className={`form-control ${errors.sheet_name ? 'error' : ''}`}
                  placeholder="Sheet1"
                />
                {errors.sheet_name && <div className="field-error">{errors.sheet_name}</div>}
              </div>
            </div>
          </div>
          
          <div className="form-group">
            <label className="form-label">제품명</label>
            <input
              type="text"
              name="product_name"
              value={formData.product_name}
              onChange={handleInputChange}
              className="form-control"
              placeholder="예: 프리미엄 멀티비타민"
            />
          </div>
          
          <div className="form-group">
            <label className="form-label">이벤트 정보</label>
            <textarea
              name="event_info"
              value={formData.event_info}
              onChange={handleInputChange}
              className="form-control"
              rows="3"
              placeholder="예: 런칭 기념 50% 할인 이벤트"
            />
          </div>
        </form>
        
        <div className="modal-footer">
          <button type="button" className="btn btn-outline-primary" onClick={onClose}>
            취소
          </button>
          <button 
            type="submit" 
            className="btn btn-primary"
            onClick={handleSubmit}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                저장 중...
              </>
            ) : (
              project ? '수정' : '생성'
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProjectModal;