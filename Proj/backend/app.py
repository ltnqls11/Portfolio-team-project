#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
블로거 마케팅 RPA 백엔드 API 서버
Flask + SQLAlchemy를 사용한 전문적인 백엔드 시스템
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import subprocess
import sys
import os
import uuid
from werkzeug.exceptions import BadRequest

# 상위 디렉토리의 모듈 import를 위한 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google_sheets_client import GoogleSheetsClient
from config import API_SERVER_HOST, API_SERVER_PORT, SECRET_KEY, DEFAULT_SHEET_ID, DEFAULT_SHEET_NAME

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blogger_rpa.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

# 데이터베이스 모델 정의
class Project(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    keyword = db.Column(db.String(200), nullable=False)
    sheet_id = db.Column(db.String(200), nullable=False)
    sheet_name = db.Column(db.String(100), nullable=False)
    product_name = db.Column(db.String(200))
    event_info = db.Column(db.Text)
    status = db.Column(db.String(50), default='created')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'keyword': self.keyword,
            'sheet_id': self.sheet_id,
            'sheet_name': self.sheet_name,
            'product_name': self.product_name,
            'event_info': self.event_info,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Blogger(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey('project.id'), nullable=False)
    blog_name = db.Column(db.String(200), nullable=False)
    post_url = db.Column(db.Text, nullable=False)
    blog_url = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(200))
    status = db.Column(db.String(50), default='collected')
    email_sent = db.Column(db.Boolean, default=False)
    email_sent_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'blog_name': self.blog_name,
            'post_url': self.post_url,
            'blog_url': self.blog_url,
            'email': self.email,
            'status': self.status,
            'email_sent': self.email_sent,
            'email_sent_at': self.email_sent_at.isoformat() if self.email_sent_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class AutomationLog(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey('project.id'), nullable=False)
    step = db.Column(db.String(50), nullable=False)  # scraping, email, cafe
    status = db.Column(db.String(50), nullable=False)  # running, completed, failed
    message = db.Column(db.Text)
    details = db.Column(db.Text)  # JSON 형태의 상세 정보
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'step': self.step,
            'status': self.status,
            'message': self.message,
            'details': json.loads(self.details) if self.details else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# 데이터베이스 초기화
with app.app_context():
    db.create_all()

# API 엔드포인트들

@app.route('/api/health', methods=['GET'])
def health_check():
    """API 서버 상태 확인"""
    return jsonify({
        'status': 'healthy',
        'message': 'Blogger Marketing RPA Backend is running',
        'version': '2.0.0'
    })

@app.route('/api/projects', methods=['GET'])
def get_projects():
    """프로젝트 목록 조회"""
    try:
        projects = Project.query.order_by(Project.created_at.desc()).all()
        return jsonify({
            'success': True,
            'projects': [project.to_dict() for project in projects]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/projects', methods=['POST'])
def create_project():
    """새 프로젝트 생성"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'keyword', 'sheet_id', 'sheet_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'{field}는 필수 항목입니다.'
                }), 400
        
        project = Project(
            name=data['name'],
            keyword=data['keyword'],
            sheet_id=data['sheet_id'],
            sheet_name=data['sheet_name'],
            product_name=data.get('product_name', ''),
            event_info=data.get('event_info', '')
        )
        
        db.session.add(project)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'project': project.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/projects/<project_id>', methods=['GET'])
def get_project(project_id):
    """특정 프로젝트 조회"""
    try:
        project = Project.query.get_or_404(project_id)
        return jsonify({
            'success': True,
            'project': project.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/projects/<project_id>', methods=['PUT'])
def update_project(project_id):
    """프로젝트 수정"""
    try:
        project = Project.query.get_or_404(project_id)
        data = request.get_json()
        
        project.name = data.get('name', project.name)
        project.keyword = data.get('keyword', project.keyword)
        project.sheet_id = data.get('sheet_id', project.sheet_id)
        project.sheet_name = data.get('sheet_name', project.sheet_name)
        project.product_name = data.get('product_name', project.product_name)
        project.event_info = data.get('event_info', project.event_info)
        project.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'project': project.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/projects/<project_id>/bloggers', methods=['GET'])
def get_project_bloggers(project_id):
    """프로젝트의 블로거 목록 조회"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        bloggers = Blogger.query.filter_by(project_id=project_id)\
                                .order_by(Blogger.created_at.desc())\
                                .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'bloggers': [blogger.to_dict() for blogger in bloggers.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': bloggers.total,
                'pages': bloggers.pages,
                'has_next': bloggers.has_next,
                'has_prev': bloggers.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/projects/<project_id>/scrape', methods=['POST'])
def start_scraping(project_id):
    """블로거 정보 수집 시작"""
    try:
        project = Project.query.get_or_404(project_id)
        
        # 로그 생성
        log = AutomationLog(
            project_id=project_id,
            step='scraping',
            status='running',
            message='블로거 정보 수집 시작'
        )
        db.session.add(log)
        
        # 프로젝트 상태 업데이트
        project.status = 'scraping'
        db.session.commit()
        
        # 스크래핑 스크립트 실행
        cmd = [
            sys.executable,
            '../main.py',
            '--keyword', project.keyword,
            '--sheet-id', project.sheet_id,
            '--sheet-name', project.sheet_name
        ]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        
        try:
            stdout, stderr = process.communicate(timeout=300)
            
            if process.returncode == 0:
                # 성공 시 Google Sheets에서 데이터 읽어와서 DB에 저장
                sheets_client = GoogleSheetsClient()
                blogger_data = sheets_client.get_blogger_data(project.sheet_id, project.sheet_name)
                
                # 기존 블로거 데이터 삭제
                Blogger.query.filter_by(project_id=project_id).delete()
                
                # 새 블로거 데이터 저장
                for blogger_info in blogger_data:
                    blogger = Blogger(
                        project_id=project_id,
                        blog_name=blogger_info['blog_name'],
                        post_url=blogger_info['post_url'],
                        blog_url=blogger_info['blog_url'],
                        email=blogger_info['email']
                    )
                    db.session.add(blogger)
                
                # 성공 로그 업데이트
                log.status = 'completed'
                log.message = f'블로거 정보 수집 완료: {len(blogger_data)}명'
                log.details = json.dumps({'count': len(blogger_data)})
                
                project.status = 'scraping_completed'
                
            else:
                # 실패 로그 업데이트
                log.status = 'failed'
                log.message = f'블로거 정보 수집 실패: {stderr}'
                log.details = json.dumps({'error': stderr, 'output': stdout})
                
                project.status = 'scraping_failed'
            
            db.session.commit()
            
            return jsonify({
                'success': process.returncode == 0,
                'message': log.message,
                'output': stdout if process.returncode == 0 else stderr
            })
            
        except subprocess.TimeoutExpired:
            process.kill()
            log.status = 'failed'
            log.message = '스크래핑 작업 시간 초과'
            project.status = 'scraping_failed'
            db.session.commit()
            
            return jsonify({
                'success': False,
                'error': '스크래핑 작업이 시간 초과되었습니다.'
            }), 500
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/projects/<project_id>/complete-automation', methods=['POST'])
def run_complete_automation(project_id):
    """완전한 자동화 프로세스 실행"""
    try:
        project = Project.query.get_or_404(project_id)
        
        if not project.product_name:
            return jsonify({
                'success': False,
                'error': '제품명이 설정되지 않았습니다.'
            }), 400
        
        # 로그 생성
        log = AutomationLog(
            project_id=project_id,
            step='complete_automation',
            status='running',
            message='완전한 자동화 프로세스 시작'
        )
        db.session.add(log)
        
        # 프로젝트 상태 업데이트
        project.status = 'automation_running'
        db.session.commit()
        
        # 완전한 자동화 스크립트 실행
        cmd = [
            sys.executable,
            '../complete_automation.py',
            '--keyword', project.keyword,
            '--sheet-id', project.sheet_id,
            '--sheet-name', project.sheet_name,
            '--product-name', project.product_name,
            '--event-info', project.event_info or '특별 할인 이벤트',
            '--sender-name', '마케팅팀'
        ]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        
        try:
            stdout, stderr = process.communicate(timeout=600)
            
            if process.returncode == 0:
                # 성공 시 블로거 데이터 업데이트
                sheets_client = GoogleSheetsClient()
                blogger_data = sheets_client.get_blogger_data(project.sheet_id, project.sheet_name)
                
                # 기존 블로거 데이터 삭제 후 새로 저장
                Blogger.query.filter_by(project_id=project_id).delete()
                
                for blogger_info in blogger_data:
                    blogger = Blogger(
                        project_id=project_id,
                        blog_name=blogger_info['blog_name'],
                        post_url=blogger_info['post_url'],
                        blog_url=blogger_info['blog_url'],
                        email=blogger_info['email'],
                        email_sent=True if blogger_info['email'] else False,
                        email_sent_at=datetime.utcnow() if blogger_info['email'] else None
                    )
                    db.session.add(blogger)
                
                # 성공 로그 업데이트
                log.status = 'completed'
                log.message = '완전한 자동화 프로세스 완료'
                log.details = json.dumps({
                    'bloggers_count': len(blogger_data),
                    'emails_sent': len([b for b in blogger_data if b['email']])
                })
                
                project.status = 'automation_completed'
                
            else:
                # 실패 로그 업데이트
                log.status = 'failed'
                log.message = f'자동화 프로세스 실패: {stderr}'
                log.details = json.dumps({'error': stderr, 'output': stdout})
                
                project.status = 'automation_failed'
            
            db.session.commit()
            
            return jsonify({
                'success': process.returncode == 0,
                'message': log.message,
                'output': stdout if process.returncode == 0 else stderr
            })
            
        except subprocess.TimeoutExpired:
            process.kill()
            log.status = 'failed'
            log.message = '자동화 프로세스 시간 초과'
            project.status = 'automation_failed'
            db.session.commit()
            
            return jsonify({
                'success': False,
                'error': '자동화 프로세스가 시간 초과되었습니다.'
            }), 500
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/projects/<project_id>/logs', methods=['GET'])
def get_project_logs(project_id):
    """프로젝트 로그 조회"""
    try:
        logs = AutomationLog.query.filter_by(project_id=project_id)\
                                  .order_by(AutomationLog.created_at.desc())\
                                  .limit(50).all()
        
        return jsonify({
            'success': True,
            'logs': [log.to_dict() for log in logs]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """대시보드 통계 정보"""
    try:
        total_projects = Project.query.count()
        total_bloggers = Blogger.query.count()
        emails_sent = Blogger.query.filter_by(email_sent=True).count()
        
        recent_projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_projects': total_projects,
                'total_bloggers': total_bloggers,
                'emails_sent': emails_sent,
                'success_rate': round((emails_sent / total_bloggers * 100) if total_bloggers > 0 else 0, 1)
            },
            'recent_projects': [project.to_dict() for project in recent_projects]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("블로거 마케팅 RPA 백엔드 서버 시작...")
    print("=" * 50)
    print(f"서버 주소: http://{API_SERVER_HOST}:{API_SERVER_PORT}")
    print("데이터베이스: SQLite (blogger_rpa.db)")
    print("=" * 50)
    
    app.run(host=API_SERVER_HOST, port=API_SERVER_PORT, debug=True)