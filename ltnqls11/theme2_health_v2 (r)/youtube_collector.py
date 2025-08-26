from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import re
import config

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YouTubeCollector:
    def __init__(self):
        """YouTube Data API 클라이언트 초기화"""
        try:
            if not config.YOUTUBE_API_KEY:
                logger.warning("YouTube API 키가 설정되지 않았습니다.")
                self.youtube = None
                return
            
            self.youtube = build('youtube', 'v3', developerKey=config.YOUTUBE_API_KEY)
            logger.info("YouTube API 연결 성공")
        except Exception as e:
            logger.error(f"YouTube API 연결 실패: {e}")
            self.youtube = None

    def search_videos(self, query: str, max_results: int = 20, 
                     order: str = 'relevance') -> List[Dict[str, Any]]:
        """키워드로 YouTube 비디오 검색 - 개선된 버전"""
        try:
            if not self.youtube:
                logger.warning("YouTube API가 설정되지 않아 빈 목록을 반환합니다.")
                return []
            
            # 검색 쿼리 최적화
            optimized_query = self._optimize_search_query(query)
            
            # 검색 요청
            search_response = self.youtube.search().list(
                q=optimized_query,
                part='snippet',
                type='video',
                maxResults=min(max_results, 50),  # API 제한
                order=order,
                regionCode='KR',  # 한국 지역
                relevanceLanguage='ko',  # 한국어 우선
                videoDuration='medium',  # 4분-20분 영상 (적당한 운동 시간)
                videoDefinition='any'  # HD 우선하지만 전체 포함
            ).execute()

            video_ids = []
            basic_info = {}

            # 비디오 ID 추출 및 기본 정보 저장
            for item in search_response['items']:
                video_id = item['id']['videoId']
                video_ids.append(video_id)
                
                basic_info[video_id] = {
                    'video_id': video_id,
                    'title': item['snippet']['title'],
                    'channel_name': item['snippet']['channelTitle'],
                    'description': item['snippet']['description'],
                    'thumbnail_url': item['snippet']['thumbnails'].get('medium', {}).get('url', ''),
                    'published_at': item['snippet']['publishedAt']
                }

            # 상세 정보 가져오기
            detailed_videos = self._get_video_details(video_ids, basic_info)
            
            # VDT 관련성 및 품질 필터링
            filtered_videos = []
            for video in detailed_videos:
                if self._is_high_quality_vdt_video(video):
                    filtered_videos.append(video)
            
            logger.info(f"'{query}' 검색 완료: {len(detailed_videos)}개 중 {len(filtered_videos)}개 VDT 관련 비디오")
            return filtered_videos

        except HttpError as e:
            logger.error(f"YouTube API 오류: {e}")
            return []
        except Exception as e:
            logger.error(f"비디오 검색 중 오류: {e}")
            return []

    def _optimize_search_query(self, query: str) -> str:
        """검색 쿼리 최적화"""
        # 기본 쿼리에 품질 관련 키워드 추가
        quality_keywords = ["운동", "스트레칭", "교정"]
        
        # 이미 품질 키워드가 포함되어 있는지 확인
        if not any(keyword in query for keyword in quality_keywords):
            query += " 운동"
        
        # 불필요한 키워드 제거 필터
        exclude_keywords = ["-리뷰", "-후기", "-광고"]
        
        for exclude in exclude_keywords:
            query += f" {exclude}"
        
        return query

    def _get_video_details(self, video_ids: List[str], 
                          basic_info: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """비디오 상세 정보 조회"""
        detailed_videos = []
        
        try:
            # 한 번에 최대 50개까지 조회 가능
            for i in range(0, len(video_ids), 50):
                batch_ids = video_ids[i:i+50]
                
                videos_response = self.youtube.videos().list(
                    part='contentDetails,statistics,snippet',
                    id=','.join(batch_ids)
                ).execute()

                for item in videos_response['items']:
                    video_id = item['id']
                    
                    # 기본 정보와 상세 정보 병합
                    video_data = basic_info.get(video_id, {})
                    
                    # 지속 시간 파싱
                    duration = self._parse_duration(
                        item['contentDetails'].get('duration', 'PT0S')
                    )
                    
                    # 통계 정보
                    stats = item.get('statistics', {})
                    view_count = int(stats.get('viewCount', 0))
                    like_count = int(stats.get('likeCount', 0))
                    comment_count = int(stats.get('commentCount', 0))

                    # 업로드 날짜 파싱
                    upload_date = self._parse_upload_date(
                        item['snippet'].get('publishedAt', '')
                    )

                    # 최종 비디오 데이터
                    video_data.update({
                        'duration_seconds': duration,
                        'view_count': view_count,
                        'like_count': like_count,
                        'comment_count': comment_count,
                        'upload_date': upload_date,
                        'tags': item['snippet'].get('tags', []),
                        'category_id': item['snippet'].get('categoryId', ''),
                        'default_language': item['snippet'].get('defaultLanguage', 'ko'),
                        'url': f"https://www.youtube.com/watch?v={video_id}"
                    })
                    
                    detailed_videos.append(video_data)

            return detailed_videos

        except Exception as e:
            logger.error(f"비디오 상세 정보 조회 중 오류: {e}")
            return []

    def _parse_duration(self, duration_str: str) -> int:
        """ISO 8601 duration을 초로 변환"""
        try:
            # PT15M33S -> 933초
            pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
            match = re.match(pattern, duration_str)
            
            if not match:
                return 0
            
            hours = int(match.group(1) or 0)
            minutes = int(match.group(2) or 0)
            seconds = int(match.group(3) or 0)
            
            return hours * 3600 + minutes * 60 + seconds
            
        except Exception:
            return 0

    def _parse_upload_date(self, published_at: str) -> Optional[str]:
        """업로드 날짜 파싱"""
        try:
            if published_at:
                dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                return dt.date().isoformat()
            return None
        except Exception:
            return None

    def _is_high_quality_vdt_video(self, video_data: Dict[str, Any]) -> bool:
        """고품질 VDT 관련 비디오인지 확인 - 강화된 필터"""
        try:
            # 기본 VDT 관련성 확인
            if not self._is_vdt_related(video_data):
                return False
            
            # 영상 길이 필터 (너무 짧거나 너무 긴 영상 제외)
            duration = video_data.get('duration_seconds', 0)
            if duration < 60:  # 1분 미만
                return False
            if duration > 3600:  # 1시간 초과
                return False
            
            # 조회수 기반 품질 필터 (너무 적은 조회수 제외)
            view_count = video_data.get('view_count', 0)
            if view_count < 100:
                return False
            
            # 제목 품질 확인
            title = video_data.get('title', '').lower()
            
            # 제외할 키워드 (광고, 후기 등)
            exclude_keywords = [
                '광고', '협찬', '리뷰', 'asmr', '먹방', '게임', '쇼핑',
                '화장품', '패션', 'vlog', '일상', '브이로그'
            ]
            
            if any(keyword in title for keyword in exclude_keywords):
                return False
            
            # 포함되어야 할 품질 키워드
            quality_keywords = [
                '운동', '스트레칭', '교정', '치료', '완화', '예방',
                '마사지', '풀기', '이완', '근력', '자세'
            ]
            
            if not any(keyword in title for keyword in quality_keywords):
                return False
            
            return True

        except Exception as e:
            logger.error(f"품질 확인 중 오류: {e}")
            return True  # 오류 시 보수적으로 포함

    def _is_vdt_related(self, video_data: Dict[str, Any]) -> bool:
        """VDT 증후군 관련 비디오인지 확인"""
        try:
            # 제목, 설명, 태그에서 VDT 관련 키워드 확인
            text_to_check = (
                video_data.get('title', '') + ' ' +
                video_data.get('description', '') + ' ' +
                ' '.join(video_data.get('tags', []))
            ).lower()

            # VDT 관련 키워드 - 확장된 목록
            vdt_keywords = [
                # 증상 키워드
                '거북목', '라운드숄더', '허리디스크', '손목터널', '목통증', '어깨통증',
                '허리통증', '손목통증', '목어깨', '승모근', '경추', '요추', '일자목',
                '스트레이트넥', '굽은어깨', '어깨결림', '목결림',
                
                # 운동 키워드
                '목스트레칭', '어깨스트레칭', '허리스트레칭', '손목스트레칭',
                '자세교정', '교정운동', '재활운동', '치료운동',
                
                # 원인 키워드
                '사무직', '컴퓨터', '모니터', '키보드', '마우스', 'vdt',
                '장시간앉기', '책상앞', '의자', '작업환경',
                
                # 대상 키워드
                '직장인', '사무원', '개발자', '프로그래머', '학생', '공부'
            ]

            # 키워드 매칭
            matched_keywords = []
            for keyword in vdt_keywords:
                if keyword in text_to_check:
                    matched_keywords.append(keyword)
            
            # 최소 2개 이상의 키워드 매칭 필요
            if len(matched_keywords) >= 2:
                return True

            # 채널명 기반 필터링 (신뢰할 수 있는 건강/운동 채널)
            channel_name = video_data.get('channel_name', '').lower()
            
            trusted_channels = [
                '김계란', '핏블리', '땅크', '닥터', '물리치료', '재활',
                '헬스', '요가', '필라테스', '스트레칭', '운동', '피트니스',
                '치료사', '트레이너', '코치', '센터', '클리닉'
            ]
            
            for channel_keyword in trusted_channels:
                if channel_keyword in channel_name:
                    # 신뢰할 수 있는 채널이면서 기본 VDT 키워드가 있으면 통과
                    if any(basic_keyword in text_to_check for basic_keyword in 
                          ['목', '어깨', '허리', '손목', '자세', '스트레칭', '운동']):
                        return True

            return len(matched_keywords) >= 1  # 최소 1개 키워드라도 있으면 포함

        except Exception as e:
            logger.error(f"VDT 관련성 확인 중 오류: {e}")
            return True  # 오류 시 보수적으로 포함

    def search_videos_by_condition(self, condition: str, purpose: str = "예방", 
                                 max_results: int = 10) -> List[Dict[str, Any]]:
        """조건과 목적에 맞는 특화 검색"""
        try:
            # 조건별 최적화된 검색 키워드 생성
            search_queries = self._generate_condition_queries(condition, purpose)
            
            all_videos = []
            collected_ids = set()
            
            for query in search_queries:
                videos = self.search_videos(query, max_results=15)
                
                # 중복 제거하면서 추가
                for video in videos:
                    video_id = video.get('video_id')
                    if video_id and video_id not in collected_ids:
                        collected_ids.add(video_id)
                        all_videos.append(video)
                
                # 목표 개수에 도달하면 중단
                if len(all_videos) >= max_results:
                    break
            
            # 관련성 점수 기반 정렬
            scored_videos = []
            for video in all_videos:
                relevance_score = self._calculate_relevance_score(video, condition, purpose)
                video['relevance_score'] = relevance_score
                scored_videos.append(video)
            
            # 점수 기준 정렬 및 상위 결과 반환
            scored_videos.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            
            return scored_videos[:max_results]
            
        except Exception as e:
            logger.error(f"조건별 검색 중 오류: {e}")
            return []

    def _generate_condition_queries(self, condition: str, purpose: str) -> List[str]:
        """조건과 목적에 맞는 검색 쿼리 생성"""
        base_queries = {
            '거북목': [
                '거북목 교정 운동',
                '목 스트레칭 거북목',
                '거북목 치료 운동',
                '목 자세 교정'
            ],
            '라운드숄더': [
                '라운드숄더 교정',
                '어깨 교정 운동',
                '굽은어깨 펴기',
                '어깨 스트레칭'
            ],
            '허리디스크': [
                '허리 디스크 운동',
                '허리 강화 운동',
                '허리 스트레칭',
                '요통 완화 운동'
            ],
            '손목터널증후군': [
                '손목 터널 증후군 운동',
                '손목 스트레칭',
                '손목 통증 완화',
                '손목 강화 운동'
            ]
        }
        
        # 목적별 키워드 추가
        purpose_modifiers = {
            '예방': ['예방', '방지', '자세교정'],
            '운동': ['강화', '근력', '운동'],
            '재활': ['재활', '치료', '완화', '회복']
        }
        
        queries = base_queries.get(condition, ['목어깨 운동'])
        modifiers = purpose_modifiers.get(purpose, ['운동'])
        
        # 기본 쿼리와 목적 키워드 조합
        combined_queries = []
        for query in queries[:2]:  # 상위 2개 쿼리만 사용
            combined_queries.append(query)
            for modifier in modifiers[:2]:  # 상위 2개 수정자만 사용
                combined_queries.append(f"{query} {modifier}")
        
        return combined_queries[:3]  # 최대 3개 쿼리

    def _calculate_relevance_score(self, video: Dict[str, Any], condition: str, purpose: str) -> float:
        """비디오의 관련성 점수 계산"""
        try:
            score = 0.0
            
            title = video.get('title', '').lower()
            description = video.get('description', '').lower()
            channel = video.get('channel_name', '').lower()
            
            # 조건 관련성 (40점)
            condition_keywords = config.VDT_CONDITIONS.get(condition, [])
            for keyword in condition_keywords:
                if keyword in title:
                    score += 8  # 제목에서 발견시 높은 점수
                elif keyword in description:
                    score += 3  # 설명에서 발견시 낮은 점수
            
            # 목적 관련성 (30점)
            purpose_keywords = config.EXERCISE_PURPOSES.get(purpose, [])
            for keyword in purpose_keywords:
                if keyword in title:
                    score += 6
                elif keyword in description:
                    score += 2
            
            # 품질 지표 (30점)
            view_count = video.get('view_count', 0)
            like_count = video.get('like_count', 0)
            duration = video.get('duration_seconds', 0)
            
            # 조회수 점수 (10점)
            if view_count > 100000:
                score += 10
            elif view_count > 10000:
                score += 7
            elif view_count > 1000:
                score += 4
            
            # 좋아요 비율 점수 (10점)
            if view_count > 0:
                like_ratio = like_count / view_count
                if like_ratio > 0.01:  # 1% 이상
                    score += 10
                elif like_ratio > 0.005:  # 0.5% 이상
                    score += 6
                elif like_ratio > 0.001:  # 0.1% 이상
                    score += 3
            
            # 적절한 길이 점수 (10점)
            if 300 <= duration <= 1200:  # 5분-20분
                score += 10
            elif 120 <= duration < 300 or 1200 < duration <= 1800:  # 2-5분 또는 20-30분
                score += 6
            elif 60 <= duration < 120:  # 1-2분
                score += 3
            
            # 채널 신뢰도 보너스
            trusted_keywords = ['물리치료', '재활', '닥터', '트레이너', '코치']
            if any(keyword in channel for keyword in trusted_keywords):
                score += 15  # 보너스 점수
            
            return round(score, 2)
            
        except Exception as e:
            logger.error(f"관련성 점수 계산 중 오류: {e}")
            return 0.0

    def collect_vdt_videos(self, max_per_keyword: int = 15) -> List[Dict[str, Any]]:
        """VDT 증후군 관련 비디오 대량 수집 - 개선된 버전"""
        all_videos = []
        collected_video_ids = set()

        logger.info("VDT 증후군 관련 비디오 수집 시작")

        # 우선순위가 높은 키워드부터 처리
        priority_keywords = config.SEARCH_KEYWORDS[:8]  # 상위 8개만 사용
        
        for keyword in priority_keywords:
            try:
                logger.info(f"키워드 '{keyword}' 검색 중...")
                videos = self.search_videos(keyword, max_per_keyword)
                
                # 중복 제거 및 품질 필터링
                unique_videos = []
                for video in videos:
                    video_id = video.get('video_id')
                    if video_id and video_id not in collected_video_ids:
                        # 추가 품질 검사
                        if self._passes_quality_check(video):
                            collected_video_ids.add(video_id)
                            unique_videos.append(video)
                
                all_videos.extend(unique_videos)
                logger.info(f"키워드 '{keyword}': {len(unique_videos)}개 새 비디오 수집")

            except Exception as e:
                logger.error(f"키워드 '{keyword}' 검색 중 오류: {e}")
                continue

        # 최종 정렬: 조회수와 관련성 기준
        all_videos.sort(key=lambda x: (x.get('relevance_score', 0), x.get('view_count', 0)), reverse=True)

        logger.info(f"총 {len(all_videos)}개 VDT 관련 비디오 수집 완료")
        return all_videos

    def _passes_quality_check(self, video: Dict[str, Any]) -> bool:
        """추가 품질 검사"""
        try:
            # 최소 조회수 기준
            if video.get('view_count', 0) < 500:
                return False
            
            # 적절한 영상 길이
            duration = video.get('duration_seconds', 0)
            if duration < 120 or duration > 2400:  # 2분-40분
                return False
            
            # 제목 길이 체크 (너무 짧거나 긴 제목 제외)
            title_length = len(video.get('title', ''))
            if title_length < 10 or title_length > 100:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"품질 검사 중 오류: {e}")
            return True

    def get_video_details_by_id(self, video_id: str) -> Optional[Dict[str, Any]]:
        """비디오 ID로 상세 정보 조회"""
        try:
            if not self.youtube:
                return None
            
            basic_info = {
                video_id: {
                    'video_id': video_id, 
                    'title': '', 
                    'channel_name': '', 
                    'description': ''
                }
            }
            detailed_videos = self._get_video_details([video_id], basic_info)
            return detailed_videos[0] if detailed_videos else None
        except Exception as e:
            logger.error(f"비디오 상세 조회 중 오류: {e}")
            return None

# 전역 수집기 인스턴스
try:
    collector = YouTubeCollector()
except Exception as e:
    logger.error(f"YouTube 수집기 초기화 실패: {e}")
    collector = None

# app.py에서 사용할 수 있는 헬퍼 함수들
def search_youtube_videos(query: str, max_results: int = 20) -> List[Dict[str, Any]]:
    """YouTube 비디오 검색 (app.py 연동용)"""
    if collector and collector.youtube:
        return collector.search_videos(query, max_results)
    else:
        logger.warning("YouTube API가 설정되지 않아 빈 목록을 반환합니다.")
        return []

def search_videos_by_condition(condition: str, purpose: str = "예방", max_results: int = 10) -> List[Dict[str, Any]]:
    """조건별 특화 검색 (app.py 연동용)"""
    if collector and collector.youtube:
        return collector.search_videos_by_condition(condition, purpose, max_results)
    else:
        logger.warning("YouTube API가 설정되지 않아 빈 목록을 반환합니다.")
        return []

def collect_all_vdt_videos(max_per_keyword: int = 15) -> List[Dict[str, Any]]:
    """VDT 관련 비디오 일괄 수집 (app.py 연동용)"""
    if collector and collector.youtube:
        return collector.collect_vdt_videos(max_per_keyword)
    else:
        logger.warning("YouTube API가 설정되지 않아 빈 목록을 반환합니다.")
        return []

def get_video_details_by_id(video_id: str) -> Optional[Dict[str, Any]]:
    """비디오 ID로 상세 정보 조회 (app.py 연동용)"""
    if collector and collector.youtube:
        return collector.get_video_details_by_id(video_id)
    else:
        logger.warning("YouTube API가 설정되지 않았습니다.")
        return None
