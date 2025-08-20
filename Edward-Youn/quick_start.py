"""
빠른 시작 스크립트
네이버 블로그 크롤러를 쉽게 실행할 수 있는 스크립트
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"

def check_requirements():
    """필수 패키지 확인"""
    print("📦 필수 패키지 확인 중...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'supabase',
        'beautifulsoup4',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 누락된 패키지: {', '.join(missing_packages)}")
        print("설치 중...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "-r", str(BACKEND_DIR / "requirements.txt")
        ])
        print("✅ 패키지 설치 완료")
    else:
        print("✅ 모든 필수 패키지가 설치되어 있습니다.")

def check_env_files():
    """환경 변수 파일 확인"""
    print("\n🔑 환경 변수 파일 확인 중...")
    
    env_supabase = PROJECT_ROOT / ".env.supabase"
    env_file = PROJECT_ROOT / ".env"
    
    if not env_supabase.exists():
        print("❌ .env.supabase 파일이 없습니다.")
        print("📝 .env.supabase 파일을 생성하고 Supabase 키를 설정하세요.")
        
        # 템플릿 생성
        template = """# Supabase Configuration
SUPABASE_URL=https://ohemvgnzikgdzjkzipvy.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_KEY=your_service_key_here
"""
        with open(env_supabase, 'w') as f:
            f.write(template)
        print(f"📁 템플릿 파일이 생성되었습니다: {env_supabase}")
        return False
    
    print("✅ 환경 변수 파일이 존재합니다.")
    return True

def start_api_server():
    """API 서버 시작"""
    print("\n🚀 API 서버 시작 중...")
    
    os.chdir(BACKEND_DIR)
    
    # Windows와 Unix 시스템 구분
    if os.name == 'nt':  # Windows
        subprocess.Popen([
            sys.executable, "main.py"
        ], creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:  # Unix/Linux/Mac
        subprocess.Popen([
            sys.executable, "main.py"
        ])
    
    print("⏳ 서버 시작 대기 중...")
    time.sleep(3)
    
    # 서버 상태 확인
    import requests
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ API 서버가 성공적으로 시작되었습니다.")
            print("📍 API 문서: http://localhost:8000/docs")
            return True
    except:
        pass
    
    print("⚠️ 서버 시작에 실패했거나 시간이 더 필요합니다.")
    return False

def run_sample_crawl():
    """샘플 크롤링 실행"""
    print("\n🔍 샘플 크롤링 실행")
    print("-" * 50)
    
    import requests
    
    # 테스트 키워드
    test_keywords = [
        {"keyword": "맛집 추천", "category": "맛집"},
        {"keyword": "스킨케어", "category": "뷰티"},
        {"keyword": "여행지 추천", "category": "여행"}
    ]
    
    for test in test_keywords:
        print(f"\n📌 '{test['keyword']}' 검색 중...")
        
        try:
            response = requests.post(
                "http://localhost:8000/api/naver-blogs/search",
                params={
                    "keyword": test['keyword'],
                    "category": test['category'],
                    "max_results": 5
                }
            )
            
            if response.status_code == 200:
                print(f"✅ 검색 시작: {test['keyword']}")
            else:
                print(f"❌ 검색 실패: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 오류: {e}")
    
    print("\n⏳ 크롤링 진행 중... (약 10초 대기)")
    time.sleep(10)
    
    # 결과 확인
    try:
        response = requests.get("http://localhost:8000/api/naver-blogs/statistics")
        if response.status_code == 200:
            stats = response.json()['statistics']
            print(f"\n📊 크롤링 결과:")
            print(f"  - 전체 블로그: {stats.get('total_blogs', 0)}개")
            print(f"  - 활성 블로그: {stats.get('active_blogs', 0)}개")
            
            categories = stats.get('categories', {})
            if categories:
                print("  - 카테고리별:")
                for cat, count in categories.items():
                    print(f"    • {cat}: {count}개")
    except Exception as e:
        print(f"통계 조회 실패: {e}")

def show_menu():
    """메뉴 표시"""
    print("\n" + "=" * 60)
    print("네이버 블로그 크롤러 - 빠른 시작")
    print("=" * 60)
    print("\n메뉴를 선택하세요:")
    print("1. 전체 자동 실행 (권장)")
    print("2. API 서버만 시작")
    print("3. 테스트 크롤링만 실행")
    print("4. 환경 설정 확인")
    print("5. 종료")
    print("-" * 60)

def main():
    """메인 함수"""
    print("=" * 60)
    print("🚀 네이버 블로그 크롤러 시작 스크립트")
    print("=" * 60)
    
    while True:
        show_menu()
        choice = input("\n선택 (1-5): ").strip()
        
        if choice == '1':
            # 전체 자동 실행
            print("\n[전체 자동 실행]")
            
            # 1. 요구사항 확인
            check_requirements()
            
            # 2. 환경 변수 확인
            if not check_env_files():
                print("⚠️ .env.supabase 파일을 설정한 후 다시 시도하세요.")
                continue
            
            # 3. API 서버 시작
            if start_api_server():
                # 4. 샘플 크롤링
                run_sample_crawl()
            
        elif choice == '2':
            # API 서버만 시작
            print("\n[API 서버 시작]")
            start_api_server()
            
        elif choice == '3':
            # 테스트 크롤링
            print("\n[테스트 크롤링]")
            run_sample_crawl()
            
        elif choice == '4':
            # 환경 설정 확인
            print("\n[환경 설정 확인]")
            check_requirements()
            check_env_files()
            
        elif choice == '5':
            print("\n👋 프로그램을 종료합니다.")
            break
            
        else:
            print("❌ 잘못된 선택입니다. 다시 선택해주세요.")
        
        input("\n계속하려면 Enter를 누르세요...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 프로그램이 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
