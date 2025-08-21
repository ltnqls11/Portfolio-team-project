#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
n8n 워크플로우와 연동을 위한 Flask API 서버
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import subprocess
import sys
import os
from google_sheets_client import GoogleSheetsClient
from config import API_SERVER_HOST, API_SERVER_PORT, SECRET_KEY, DEFAULT_SHEET_ID, DEFAULT_SHEET_NAME

app = Flask(__name__)
app.secret_key = SECRET_KEY
CORS(app)  # React 앱에서 호출할 수 있도록 CORS 설정

# 전역 변수로 설정 저장 (.env에서 기본값 로드)
current_config = {
    'sheet_id': DEFAULT_SHEET_ID,
    'sheet_name': DEFAULT_SHEET_NAME,
    'last_keyword': ''
}


@app.route('/api/health', methods=['GET'])
def health_check():
    """API 서버 상태 확인"""
    return jsonify({
        'status': 'healthy',
        'message': 'RPA API Server is running'
    })


@app.route('/api/config', methods=['POST'])
def set_config():
    """설정 저장"""
    try:
        data = request.get_json()
        current_config['sheet_id'] = data.get('sheet_id', '')
        current_config['sheet_name'] = data.get('sheet_name', '')
        
        return jsonify({
            'success': True,
            'message': '설정이 저장되었습니다.',
            'config': current_config
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/scrape', methods=['POST'])
def start_scraping():
    """네이버 블로그 스크래핑 시작"""
    try:
        data = request.get_json()
        keyword = data.get('keyword', '')
        sheet_id = data.get('sheet_id', current_config['sheet_id'])
        sheet_name = data.get('sheet_name', current_config['sheet_name'])
        
        if not all([keyword, sheet_id, sheet_name]):
            return jsonify({
                'success': False,
                'error': '필수 매개변수가 누락되었습니다. (keyword, sheet_id, sheet_name)'
            }), 400
        
        # 현재 설정 업데이트
        current_config['sheet_id'] = sheet_id
        current_config['sheet_name'] = sheet_name
        current_config['last_keyword'] = keyword
        
        # 메인 스크립트 실행
        cmd = [
            sys.executable,
            'main.py',
            '--keyword', keyword,
            '--sheet-id', sheet_id,
            '--sheet-name', sheet_name
        ]
        
        # 백그라운드에서 실행
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 프로세스 완료 대기 (타임아웃 설정)
        try:
            stdout, stderr = process.communicate(timeout=300)  # 5분 타임아웃
            
            if process.returncode == 0:
                return jsonify({
                    'success': True,
                    'message': f'키워드 "{keyword}"로 스크래핑이 완료되었습니다.',
                    'keyword': keyword,
                    'output': stdout
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'스크래핑 실행 중 오류 발생: {stderr}',
                    'output': stdout
                }), 500
                
        except subprocess.TimeoutExpired:
            process.kill()
            return jsonify({
                'success': False,
                'error': '스크래핑 작업이 시간 초과되었습니다.'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/bloggers', methods=['GET'])
def get_bloggers():
    """Google Sheets에서 블로거 데이터 읽기 (n8n 워크플로우용)"""
    try:
        sheet_id = request.args.get('sheet_id', current_config['sheet_id'])
        sheet_name = request.args.get('sheet_name', current_config['sheet_name'])
        
        if not sheet_id or not sheet_name:
            return jsonify({
                'success': False,
                'error': 'sheet_id와 sheet_name이 필요합니다.'
            }), 400
        
        # Google Sheets에서 데이터 읽기
        sheets_client = GoogleSheetsClient()
        blogger_data = sheets_client.get_blogger_data(sheet_id, sheet_name)
        
        return jsonify({
            'success': True,
            'count': len(blogger_data),
            'bloggers': blogger_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/bloggers/emails', methods=['GET'])
def get_blogger_emails():
    """이메일이 있는 블로거 목록만 반환 (이메일 발송용)"""
    try:
        sheet_id = request.args.get('sheet_id', current_config['sheet_id'])
        sheet_name = request.args.get('sheet_name', current_config['sheet_name'])
        
        if not sheet_id or not sheet_name:
            return jsonify({
                'success': False,
                'error': 'sheet_id와 sheet_name이 필요합니다.'
            }), 400
        
        sheets_client = GoogleSheetsClient()
        blogger_data = sheets_client.get_blogger_data(sheet_id, sheet_name)
        
        # 이메일 형식으로 변환
        email_list = []
        for blogger in blogger_data:
            email_list.append({
                '블로그명': blogger['blog_name'],
                '포스트URL': blogger['post_url'],
                '블로그URL': blogger['blog_url'],
                '이메일': blogger['email']
            })
        
        return jsonify({
            'success': True,
            'count': len(email_list),
            'data': email_list
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/webhook/email', methods=['POST'])
def webhook_email():
    """n8n 이메일 워크플로우용 웹훅"""
    try:
        data = request.get_json()
        
        # 제품 정보 등 추가 데이터 처리
        product_name = data.get('productName', '신제품')
        
        # 블로거 데이터 가져오기
        sheet_id = data.get('sheet_id', current_config['sheet_id'])
        sheet_name = data.get('sheet_name', current_config['sheet_name'])
        
        if not sheet_id or not sheet_name:
            return jsonify({
                'success': False,
                'error': 'sheet_id와 sheet_name이 필요합니다.'
            }), 400
        
        sheets_client = GoogleSheetsClient()
        blogger_data = sheets_client.get_blogger_data(sheet_id, sheet_name)
        
        # n8n에서 사용할 수 있는 형태로 반환
        response_data = []
        for blogger in blogger_data:
            response_data.append({
                '블로그명': blogger['blog_name'],
                '포스트URL': blogger['post_url'],
                '블로그URL': blogger['blog_url'],
                '이메일': blogger['email'],
                'productName': product_name
            })
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/webhook/cafe', methods=['POST'])
def webhook_cafe():
    """n8n 카페 포스팅 워크플로우용 웹훅"""
    try:
        data = request.get_json()
        
        # 카페 포스팅에 필요한 데이터 반환
        return jsonify({
            'success': True,
            'productName': data.get('productName', '신제품'),
            'eventInfo': data.get('eventInfo', '특별 할인 이벤트'),
            'timestamp': data.get('timestamp', ''),
            'message': '카페 포스팅 데이터가 준비되었습니다.'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/complete-automation', methods=['POST'])
def run_complete_automation():
    """완전한 자동화 프로세스 실행 (n8n 없이 독립 실행)"""
    try:
        data = request.get_json()
        keyword = data.get('keyword', '')
        sheet_id = data.get('sheet_id', current_config['sheet_id'])
        sheet_name = data.get('sheet_name', current_config['sheet_name'])
        product_name = data.get('product_name', '')
        event_info = data.get('event_info', '특별 할인 이벤트')
        sender_name = data.get('sender_name', '마케팅팀')
        
        if not all([keyword, sheet_id, sheet_name, product_name]):
            return jsonify({
                'success': False,
                'error': '필수 매개변수가 누락되었습니다. (keyword, sheet_id, sheet_name, product_name)'
            }), 400
        
        # 완전한 자동화 스크립트 실행
        cmd = [
            sys.executable,
            'complete_automation.py',
            '--keyword', keyword,
            '--sheet-id', sheet_id,
            '--sheet-name', sheet_name,
            '--product-name', product_name,
            '--event-info', event_info,
            '--sender-name', sender_name
        ]
        
        # 백그라운드에서 실행
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 프로세스 완료 대기 (긴 타임아웃 설정)
        try:
            stdout, stderr = process.communicate(timeout=600)  # 10분 타임아웃
            
            if process.returncode == 0:
                return jsonify({
                    'success': True,
                    'message': f'완전한 자동화 프로세스가 성공적으로 완료되었습니다!',
                    'keyword': keyword,
                    'product_name': product_name,
                    'output': stdout
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'자동화 프로세스 실행 중 오류 발생: {stderr}',
                    'output': stdout
                }), 500
                
        except subprocess.TimeoutExpired:
            process.kill()
            return jsonify({
                'success': False,
                'error': '자동화 프로세스가 시간 초과되었습니다.'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("RPA API 서버 시작...")
    print("=" * 50)
    print(f"서버 주소: http://{API_SERVER_HOST}:{API_SERVER_PORT}")
    print("사용 가능한 엔드포인트:")
    print("- GET  /api/health - 서버 상태 확인")
    print("- POST /api/config - 설정 저장")
    print("- POST /api/scrape - 스크래핑 시작")
    print("- GET  /api/bloggers - 블로거 데이터 조회")
    print("- GET  /api/bloggers/emails - 이메일 목록 조회")
    print("- POST /api/webhook/email - n8n 이메일 웹훅")
    print("- POST /api/webhook/cafe - n8n 카페 웹훅")
    print("=" * 50)
    print(f"기본 Google Sheets ID: {DEFAULT_SHEET_ID or '설정되지 않음'}")
    print(f"기본 시트 이름: {DEFAULT_SHEET_NAME}")
    print("=" * 50)
    
    app.run(host=API_SERVER_HOST, port=API_SERVER_PORT, debug=True)