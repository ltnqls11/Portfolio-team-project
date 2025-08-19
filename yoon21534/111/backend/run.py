#!/usr/bin/env python3
"""
Flask 애플리케이션 실행 스크립트
"""

import os
from app import app, db
from config import config

def create_app(config_name=None):
    """애플리케이션 팩토리 패턴"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app.config.from_object(config[config_name])
    
    # 데이터베이스 초기화
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    flask_app = create_app()
    flask_app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=True
    )