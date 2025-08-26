"""
VDT 증후군 관리 시스템 메인 파이프라인
YouTube 영상 수집 -> AI 분석 -> 데이터베이스 저장 자동화
"""

import logging
import time
from datetime import datetime
from typing import List, Dict, Any
import config
from youtube_collector import collect_all_vdt_videos
from video_analyzer import analyze_multiple_videos
from database import save_video_analysis_result, get_database_analytics

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vdt_pipeline.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VDTPipeline:
    def __init__(self):
        """VDT 파이프라인 초기화"""
        self.total_collected = 0
        self.total_analyzed = 0
        self.total_saved = 0
        self.failed_analysis = 0
        self.failed_saves = 0
        
    def run_collection_pipeline(self, max_videos_per_keyword: int = 15) -> Dict[str, Any]:
        """전체 파이프라인 실행"""
        logger.info("=== VDT 영상 수집 및 분석 파이프라인 시작 ===")
        start_time = datetime.now()
        
        try:
            # 1단계: YouTube 영상 수집
            logger.info("1단계: YouTube 영상 수집 시작")
            videos = self._collect_videos(max_videos_per_keyword)
            
            if not videos:
                logger.warning("수집된 영상이 없습니다. 파이프라인을 종료합니다.")
                return self._generate_report(start_time, [])
            
            # 2단계: AI 분석
            logger.info("2단계: AI 영상 분석 시작")
            analyzed_videos = self._analyze_videos(videos)
            
            # 3단계: 데이터베이스 저장
            logger.info("3단계: 데이터베이스 저장 시작")
            saved_videos = self._save_videos(analyzed_videos)
            
            # 4단계: 결과 보고서 생성
            end_time = datetime.now()
            report = self._generate_report(start_time, saved_videos)
            
            logger.info("=== VDT 파이프라인 완료 ===")
            return report
            
        except Exception as e:
            logger.error(f"파이프라인 실행 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            return self._generate_error_report(start_time, str(e))
    
    def _collect_videos(self, max_per_keyword: int) -> List[Dict[str, Any]]:
        """YouTube 영상 수집"""
        try:
            videos = collect_all_vdt_videos(max_per_keyword)
            self.total_collected = len(videos)
            
            logger.info(f"영상 수집 완료: {self.total_collected}개")
            
            # 중복 제거
            unique_videos = []
            seen_ids = set()
            
            for video in videos:
                video_id = video.get('video_id')
                if video_id and video_id not in seen_ids:
                    seen_ids.add(video_id)
                    unique_videos.append(video)
            
            logger.info(f"중복 제거 후: {len(unique_videos)}개")
            return unique_videos
            
        except Exception as e:
            logger.error(f"영상 수집 중 오류: {e}")
            return []
    
    def _analyze_videos(self, videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """영상 AI 분석"""
        try:
            # 배치 크기 설정 (API 제한 고려)
            batch_size = 10
            analyzed_videos = []
            
            for i in range(0, len(videos), batch_size):
                batch = videos[i:i + batch_size]
                
                logger.info(f"배치 {i//batch_size + 1}/{(len(videos)-1)//batch_size + 1} 분석 중...")
                
                # 배치별 분석
                batch_results = analyze_multiple_videos(batch)
                analyzed_videos.extend(batch_results)
                
                self.total_analyzed += len(batch_results)
                self.failed_analysis += len(batch) - len(batch_results)
                
                # API 제한 방지를 위한 대기
                if i + batch_size < len(videos):
                    logger.info("API 제한 방지를 위해 10초 대기...")
                    time.sleep(10)
            
            logger.info(f"분석 완료: {self.total_analyzed}개 성공, {self.failed_analysis}개 실패")
            return analyzed_videos
            
        except Exception as e:
            logger.error(f"영상 분석 중 오류: {e}")
            return []
    
    def _save_videos(self, analyzed_videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """분석된 영상을 데이터베이스에 저장"""
        try:
            saved_videos = []
            
            for video in analyzed_videos:
                try:
                    success = save_video_analysis_result(video)
                    if success:
                        saved_videos.append(video)
                        self.total_saved += 1
                    else:
                        self.failed_saves += 1
                        logger.warning(f"저장 실패: {video.get('video_id', 'Unknown')}")
                        
                except Exception as e:
                    self.failed_saves += 1
                    logger.error(f"개별 영상 저장 오류: {e}")
            
            logger.info(f"저장 완료: {self.total_saved}개 성공, {self.failed_saves}개 실패")
            return saved_videos
            
        except Exception as e:
            logger.error(f"영상 저장 중 오류: {e}")
            return []
    
    def _generate_report(self, start_time: datetime, saved_videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """실행 결과 보고서 생성"""
        end_time = datetime.now()
        duration = end_time - start_time
        
        # 조건별 통계
        condition_stats = {}
        for video in saved_videos:
            condition = video.get('target_condition', '기타')
            if condition not in condition_stats:
                condition_stats[condition] = 0
            condition_stats[condition] += 1
        
        # 목적별 통계
        purpose_stats = {}
        for video in saved_videos:
            purpose = video.get('exercise_purpose', '기타')
            if purpose not in purpose_stats:
                purpose_stats[purpose] = 0
            purpose_stats[purpose] += 1
        
        # 데이터베이스 전체 통계
        try:
            db_analytics = get_database_analytics()
        except:
            db_analytics = {}
        
        report = {
            'execution_time': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat(),
                'duration_seconds': duration.total_seconds(),
                'duration_formatted': str(duration)
            },
            'collection_stats': {
                'total_collected': self.total_collected,
                'total_analyzed': self.total_analyzed,
                'total_saved': self.total_saved,
                'failed_analysis': self.failed_analysis,
                'failed_saves': self.failed_saves,
                'success_rate_analysis': (self.total_analyzed / max(self.total_collected, 1)) * 100,
                'success_rate_storage': (self.total_saved / max(self.total_analyzed, 1)) * 100
            },
            'content_stats': {
                'by_condition': condition_stats,
                'by_purpose': purpose_stats
            },
            'database_stats': db_analytics,
            'top_videos': [
                {
                    'title': video.get('title', 'N/A'),
                    'condition': video.get('target_condition', 'N/A'),
                    'purpose': video.get('exercise_purpose', 'N/A'),
                    'effectiveness': video.get('effectiveness_score', 0),
                    'medical_accuracy': video.get('medical_accuracy', 0),
                    'url': video.get('url', 'N/A')
                }
                for video in sorted(saved_videos, 
                                  key=lambda x: x.get('effectiveness_score', 0), 
                                  reverse=True)[:5]
            ]
        }
        
        # 로그에 요약 출력
        self._log_summary(report)
        
        return report
    
    def _generate_error_report(self, start_time: datetime, error_message: str) -> Dict[str, Any]:
        """오류 발생 시 보고서 생성"""
        end_time = datetime.now()
        duration = end_time - start_time
        
        return {
            'execution_time': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat(),
                'duration_seconds': duration.total_seconds(),
                'duration_formatted': str(duration)
            },
            'error': error_message,
            'collection_stats': {
                'total_collected': self.total_collected,
                'total_analyzed': self.total_analyzed,
                'total_saved': self.total_saved,
                'failed_analysis': self.failed_analysis,
                'failed_saves': self.failed_saves
            }
        }
    
    def _log_summary(self, report: Dict[str, Any]):
        """실행 결과 요약 로그"""
        stats = report['collection_stats']
        duration = report['execution_time']['duration_formatted']
        
        logger.info("=" * 50)
        logger.info("파이프라인 실행 결과 요약")
        logger.info("=" * 50)
        logger.info(f"실행 시간: {duration}")
        logger.info(f"수집된 영상: {stats['total_collected']}개")
        logger.info(f"분석 완료: {stats['total_analyzed']}개 ({stats['success_rate_analysis']:.1f}%)")
        logger.info(f"저장 완료: {stats['total_saved']}개 ({stats['success_rate_storage']:.1f}%)")
        
        if report['content_stats']['by_condition']:
            logger.info("조건별 수집 현황:")
            for condition, count in report['content_stats']['by_condition'].items():
                logger.info(f"  - {condition}: {count}개")
        
        if report['top_videos']:
            logger.info("최고 평점 영상 Top 3:")
            for i, video in enumerate(report['top_videos'][:3], 1):
                logger.info(f"  {i}. {video['title'][:50]}... (효과성: {video['effectiveness']:.1f}/5.0)")
        
        logger.info("=" * 50)

def run_daily_collection():
    """일일 영상 수집 실행"""
    pipeline = VDTPipeline()
    report = pipeline.run_collection_pipeline(max_videos_per_keyword=20)
    
    # 보고서를 파일로 저장
    report_filename = f"vdt_pipeline_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        import json
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        logger.info(f"보고서 저장: {report_filename}")
    except Exception as e:
        logger.error(f"보고서 저장 실패: {e}")
    
    return report

def run_quick_test():
    """빠른 테스트 실행 (소량 데이터)"""
    logger.info("빠른 테스트 모드 실행")
    pipeline = VDTPipeline()
    report = pipeline.run_collection_pipeline(max_videos_per_keyword=3)
    return report

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # 테스트 모드
        print("테스트 모드로 실행합니다...")
        run_quick_test()
    else:
        # 정규 실행
        print("정규 모드로 실행합니다...")
        run_daily_collection()
