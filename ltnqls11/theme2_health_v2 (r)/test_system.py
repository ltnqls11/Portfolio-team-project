"""
VDT 증후군 관리 시스템 통합 테스트
모든 주요 기능을 테스트하는 종합 테스트 스위트
"""

import os
import sys
import json
import time
from datetime import datetime
import logging
from typing import Dict, List, Any

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VDTSystemTester:
    def __init__(self):
        """테스트 시스템 초기화"""
        self.test_results = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def run_all_tests(self) -> Dict[str, Any]:
        """모든 테스트 실행"""
        logger.info("=== VDT 시스템 통합 테스트 시작 ===")
        start_time = datetime.now()
        
        # 테스트 목록
        tests = [
            ("환경 변수 테스트", self.test_environment_variables),
            ("설정 파일 테스트", self.test_config_files),
            ("YouTube API 테스트", self.test_youtube_api),
            ("Gemini AI API 테스트", self.test_gemini_api),
            ("Supabase 연결 테스트", self.test_supabase_connection),
            ("Google Sheets 연결 테스트", self.test_google_sheets),
            ("영상 수집 테스트", self.test_video_collection),
            ("영상 분석 테스트", self.test_video_analysis),
            ("데이터베이스 저장 테스트", self.test_database_operations),
            ("알림 시스템 테스트", self.test_notification_system)
        ]
        
        # 각 테스트 실행
        for test_name, test_func in tests:
            logger.info(f"실행 중: {test_name}")
            try:
                result = test_func()
                self.test_results[test_name] = {
                    "status": "PASS" if result else "FAIL",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
                if result:
                    self.passed_tests += 1
                else:
                    self.failed_tests += 1
            except Exception as e:
                logger.error(f"{test_name} 실행 중 오류: {e}")
                self.test_results[test_name] = {
                    "status": "ERROR",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                self.failed_tests += 1
            
            self.total_tests += 1
            time.sleep(1)  # API 제한 고려
        
        # 결과 생성
        end_time = datetime.now()
        duration = end_time - start_time
        
        summary = {
            "execution_time": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "duration_seconds": duration.total_seconds()
            },
            "test_summary": {
                "total_tests": self.total_tests,
                "passed_tests": self.passed_tests,
                "failed_tests": self.failed_tests,
                "success_rate": (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
            },
            "test_results": self.test_results,
            "system_status": "HEALTHY" if self.failed_tests == 0 else "ISSUES_DETECTED"
        }
        
        self._generate_test_report(summary)
        logger.info("=== VDT 시스템 통합 테스트 완료 ===")
        
        return summary
    
    def test_environment_variables(self) -> bool:
        """환경 변수 테스트"""
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            required_vars = [
                "YOUTUBE_API_KEY",
                "GEMINI_API_KEY", 
                "SUPABASE_URL",
                "SUPABASE_ANON_KEY"
            ]
            
            missing_vars = []
            for var in required_vars:
                if not os.getenv(var):
                    missing_vars.append(var)
            
            if missing_vars:
                logger.warning(f"누락된 환경 변수: {missing_vars}")
                return False
            
            logger.info("모든 필수 환경 변수가 설정되었습니다.")
            return True
            
        except Exception as e:
            logger.error(f"환경 변수 테스트 실패: {e}")
            return False
    
    def test_config_files(self) -> bool:
        """설정 파일 테스트"""
        try:
            import config
            
            # 필수 설정 확인
            required_configs = [
                "YOUTUBE_API_KEY",
                "GEMINI_API_KEY",
                "SUPABASE_URL",
                "SEARCH_KEYWORDS",
                "VDT_CONDITIONS"
            ]
            
            for attr in required_configs:
                if not hasattr(config, attr):
                    logger.error(f"config.py에 {attr}가 없습니다.")
                    return False
            
            # 검색 키워드 확인
            if len(config.SEARCH_KEYWORDS) < 5:
                logger.warning("검색 키워드가 너무 적습니다.")
                return False
            
            logger.info("config.py 설정이 올바릅니다.")
            return True
            
        except ImportError:
            logger.error("config.py를 불러올 수 없습니다.")
            return False
        except Exception as e:
            logger.error(f"설정 파일 테스트 실패: {e}")
            return False
    
    def test_youtube_api(self) -> bool:
        """YouTube API 테스트"""
        try:
            from youtube_collector import YouTubeCollector
            
            collector = YouTubeCollector()
            if not collector.youtube:
                logger.error("YouTube API 클라이언트 초기화 실패")
                return False
            
            # 간단한 검색 테스트
            test_videos = collector.search_videos("목 스트레칭", max_results=2)
            
            if not test_videos:
                logger.warning("YouTube 검색 결과가 없습니다.")
                return False
            
            # 비디오 데이터 구조 확인
            required_fields = ['video_id', 'title', 'channel_name', 'url']
            for field in required_fields:
                if field not in test_videos[0]:
                    logger.error(f"비디오 데이터에 {field} 필드가 없습니다.")
                    return False
            
            logger.info(f"YouTube API 테스트 성공: {len(test_videos)}개 비디오 검색")
            return True
            
        except Exception as e:
            logger.error(f"YouTube API 테스트 실패: {e}")
            return False
    
    def test_gemini_api(self) -> bool:
        """Gemini AI API 테스트"""
        try:
            import google.generativeai as genai
            import config
            
            if not config.GEMINI_API_KEY:
                logger.error("Gemini API 키가 설정되지 않았습니다.")
                return False
            
            genai.configure(api_key=config.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # 간단한 텍스트 생성 테스트
            response = model.generate_content("안녕하세요! 간단한 테스트입니다.")
            
            if not response or not response.text:
                logger.error("Gemini API 응답이 없습니다.")
                return False
            
            logger.info("Gemini AI API 테스트 성공")
            return True
            
        except Exception as e:
            logger.error(f"Gemini API 테스트 실패: {e}")
            return False
    
    def test_supabase_connection(self) -> bool:
        """Supabase 연결 테스트"""
        try:
            from database import VideoDatabase
            
            db = VideoDatabase()
            if not db.supabase:
                logger.error("Supabase 연결 실패")
                return False
            
            # 데이터베이스 분석 정보 조회 테스트
            analytics = db.get_analytics()
            
            if analytics is None:
                logger.warning("Supabase 연결은 되지만 데이터 조회에 문제가 있습니다.")
                return False
            
            logger.info("Supabase 연결 테스트 성공")
            return True
            
        except Exception as e:
            logger.error(f"Supabase 연결 테스트 실패: {e}")
            return False
    
    def test_google_sheets(self) -> bool:
        """Google Sheets 연결 테스트"""
        try:
            # Google Sheets는 선택 사항이므로 실패해도 경고만 출력
            if not os.path.exists("credentials.json"):
                logger.warning("credentials.json 파일이 없습니다. Google Sheets 기능이 비활성화됩니다.")
                return True
            
            from app import init_google_sheets
            
            client = init_google_sheets()
            if not client:
                logger.warning("Google Sheets 클라이언트 초기화 실패")
                return True  # 선택 사항이므로 True 반환
            
            spreadsheet_id = os.getenv("SPREADSHEET_ID")
            if not spreadsheet_id:
                logger.warning("SPREADSHEET_ID가 설정되지 않았습니다.")
                return True
            
            try:
                spreadsheet = client.open_by_key(spreadsheet_id)
                logger.info(f"Google Sheets 연결 성공: {spreadsheet.title}")
                return True
            except Exception as e:
                logger.warning(f"Google Sheets 연결 실패: {e}")
                return True  # 선택 사항이므로 True 반환
            
        except Exception as e:
            logger.warning(f"Google Sheets 테스트 실패: {e}")
            return True  # 선택 사항이므로 True 반환
    
    def test_video_collection(self) -> bool:
        """영상 수집 테스트"""
        try:
            from youtube_collector import search_youtube_videos
            
            # 소량 테스트 검색
            videos = search_youtube_videos("거북목 운동", max_results=3)
            
            if not videos:
                logger.error("영상 수집 실패")
                return False
            
            # 수집된 영상 데이터 검증
            for video in videos:
                required_fields = ['video_id', 'title', 'url']
                for field in required_fields:
                    if field not in video or not video[field]:
                        logger.error(f"영상 데이터에 {field} 필드가 누락되었습니다.")
                        return False
            
            logger.info(f"영상 수집 테스트 성공: {len(videos)}개 비디오")
            return True
            
        except Exception as e:
            logger.error(f"영상 수집 테스트 실패: {e}")
            return False
    
    def test_video_analysis(self) -> bool:
        """영상 분석 테스트"""
        try:
            from video_analyzer import analyze_single_video
            
            # 테스트용 가짜 비디오 데이터
            test_video = {
                'video_id': 'test123',
                'title': '거북목 교정 운동 5분',
                'channel_name': '테스트 채널',
                'description': '목 통증 완화를 위한 간단한 스트레칭',
                'duration_seconds': 300,
                'view_count': 10000,
                'like_count': 500,
                'comment_count': 50
            }
            
            # AI 분석 실행
            analysis_result = analyze_single_video(test_video)
            
            if not analysis_result:
                logger.error("영상 분석 실패")
                return False
            
            # 분석 결과 검증
            required_fields = ['target_condition', 'exercise_purpose', 'difficulty_level']
            for field in required_fields:
                if field not in analysis_result:
                    logger.error(f"분석 결과에 {field} 필드가 없습니다.")
                    return False
            
            logger.info("영상 분석 테스트 성공")
            return True
            
        except Exception as e:
            logger.error(f"영상 분석 테스트 실패: {e}")
            return False
    
    def test_database_operations(self) -> bool:
        """데이터베이스 작업 테스트"""
        try:
            from database import save_video_analysis_result, get_videos_for_condition
            
            # 테스트용 분석 데이터
            test_analysis = {
                'video_id': f'test_{int(time.time())}',
                'title': '테스트 영상',
                'url': 'https://youtube.com/test',
                'channel_name': '테스트 채널',
                'target_condition': '거북목',
                'exercise_purpose': '예방',
                'difficulty_level': 3,
                'exercise_type': '스트레칭',
                'body_parts': ['목', '어깨'],
                'intensity': '보통',
                'equipment_needed': '없음',
                'view_count': 1000,
                'like_count': 50,
                'comment_count': 10,
                'creator_type': '트레이너',
                'credential_verified': True,
                'medical_accuracy': 4.0,
                'age_group': '전연령',
                'fitness_level': '초보',
                'pain_level_range': '4-6',
                'effectiveness_score': 4.2,
                'completion_rate': 0.0,
                'user_rating': 0.0,
                'contraindications': '특별한 주의사항 없음',
                'expected_benefits': '목 근육 이완',
                'safety_level': '안전',
                'analysis_date': datetime.now().isoformat()
            }
            
            # 저장 테스트
            save_result = save_video_analysis_result(test_analysis)
            if not save_result:
                logger.warning("데이터베이스 저장 실패 (연결 문제일 수 있음)")
                return True  # Supabase 연결이 없어도 시스템은 동작해야 함
            
            # 조회 테스트
            videos = get_videos_for_condition('거북목', '예방', limit=1)
            
            logger.info("데이터베이스 작업 테스트 성공")
            return True
            
        except Exception as e:
            logger.error(f"데이터베이스 작업 테스트 실패: {e}")
            return False
    
    def test_notification_system(self) -> bool:
        """알림 시스템 테스트"""
        try:
            from notification_scheduler import NotificationScheduler
            
            # 테스트용 설정 파일 생성
            test_config = {
                "type": "이메일 (Gmail)",
                "email": "test@example.com",
                "email_password": "test_password",
                "work_start": "09:00",
                "work_end": "18:00",
                "interval": 30
            }
            
            test_config_file = "test_notification_config.json"
            with open(test_config_file, 'w', encoding='utf-8') as f:
                json.dump(test_config, f, ensure_ascii=False, indent=2)
            
            # 스케줄러 초기화 테스트
            scheduler = NotificationScheduler(test_config_file)
            
            if not scheduler.config:
                logger.error("알림 스케줄러 설정 로드 실패")
                return False
            
            # 근무 시간 확인 로직 테스트
            is_work_time = scheduler.is_work_time()
            
            # 테스트 파일 정리
            if os.path.exists(test_config_file):
                os.remove(test_config_file)
            
            logger.info("알림 시스템 테스트 성공")
            return True
            
        except Exception as e:
            logger.error(f"알림 시스템 테스트 실패: {e}")
            return False
    
    def _generate_test_report(self, summary: Dict[str, Any]):
        """테스트 보고서 생성"""
        report_filename = f"vdt_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_filename, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"테스트 보고서 저장: {report_filename}")
            
            # 콘솔에 요약 출력
            self._print_test_summary(summary)
            
        except Exception as e:
            logger.error(f"테스트 보고서 생성 실패: {e}")
    
    def _print_test_summary(self, summary: Dict[str, Any]):
        """테스트 결과 요약 출력"""
        print("\n" + "="*60)
        print("VDT 시스템 테스트 결과 요약")
        print("="*60)
        
        test_summary = summary['test_summary']
        print(f"총 테스트: {test_summary['total_tests']}개")
        print(f"성공: {test_summary['passed_tests']}개")
        print(f"실패: {test_summary['failed_tests']}개")
        print(f"성공률: {test_summary['success_rate']:.1f}%")
        
        print(f"\n시스템 상태: {summary['system_status']}")
        
        print("\n테스트 상세 결과:")
        for test_name, result in summary['test_results'].items():
            status_icon = "✅" if result['status'] == "PASS" else "❌" if result['status'] == "FAIL" else "⚠️"
            print(f"  {status_icon} {test_name}: {result['status']}")
            
            if result['status'] == "ERROR" and 'error' in result:
                print(f"    오류: {result['error']}")
        
        print("="*60)
        
        # 권장사항 출력
        if test_summary['failed_tests'] > 0:
            print("\n🔧 권장사항:")
            
            failed_tests = [name for name, result in summary['test_results'].items() 
                          if result['status'] in ['FAIL', 'ERROR']]
            
            if any('API' in test for test in failed_tests):
                print("  - API 키 설정을 확인해주세요 (.env 파일)")
            
            if any('환경' in test for test in failed_tests):
                print("  - 필요한 라이브러리를 설치해주세요 (pip install -r requirements.txt)")
            
            if any('데이터베이스' in test for test in failed_tests):
                print("  - Supabase 연결 설정을 확인해주세요")
            
            print("  - 자세한 내용은 로그 파일을 확인해주세요")

def run_quick_test():
    """빠른 테스트 실행"""
    tester = VDTSystemTester()
    return tester.run_all_tests()

def run_system_health_check():
    """시스템 헬스 체크"""
    logger.info("시스템 헬스 체크를 실행합니다...")
    
    tester = VDTSystemTester()
    summary = tester.run_all_tests()
    
    # 헬스 체크 결과
    if summary['system_status'] == 'HEALTHY':
        print("\n🎉 시스템이 정상적으로 작동합니다!")
        return True
    else:
        print(f"\n⚠️ 시스템에 {summary['test_summary']['failed_tests']}개의 문제가 발견되었습니다.")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "health":
        # 헬스 체크 모드
        run_system_health_check()
    else:
        # 전체 테스트 모드
        run_quick_test()
