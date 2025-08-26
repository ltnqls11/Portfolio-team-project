from supabase import create_client, Client
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import json
import config

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoDatabase:
    def __init__(self):
        """Supabase 클라이언트 초기화"""
        try:
            self.supabase: Client = create_client(
                config.SUPABASE_URL, 
                config.SUPABASE_ANON_KEY  # 서비스 키 대신 Anon 키 사용
            )
            logger.info("Supabase 연결 성공")
            self._ensure_table_exists()
        except Exception as e:
            logger.error(f"Supabase 연결 실패: {e}")
            # 연결 실패해도 시스템이 중단되지 않도록 처리
            self.supabase = None

    def _ensure_table_exists(self):
        """테이블 존재 여부 확인 및 생성"""
        try:
            if not self.supabase:
                return False
            
            # 테이블 조회 시도
            result = self.supabase.table('video_analysis').select('id').limit(1).execute()
            logger.info("video_analysis 테이블 확인 완료")
            return True
        except Exception as e:
            logger.warning(f"테이블 확인 실패 (정상적일 수 있음): {e}")
            return False

    def insert_video_analysis(self, video_data: Dict[str, Any]) -> Optional[Dict]:
        """비디오 분석 결과를 데이터베이스에 저장"""
        try:
            if not self.supabase:
                logger.warning("Supabase 연결이 없어 저장을 건너뜁니다.")
                return None
            
            # 중복 체크
            existing = self.supabase.table('video_analysis').select('id').eq('video_id', video_data['video_id']).execute()
            
            if existing.data:
                logger.info(f"비디오 {video_data['video_id']}는 이미 존재합니다.")
                return self.update_video_analysis(video_data['video_id'], video_data)
            
            # 데이터 정제
            clean_data = self._clean_video_data(video_data)
            
            # 새 데이터 삽입
            result = self.supabase.table('video_analysis').insert(clean_data).execute()
            
            if result.data:
                logger.info(f"비디오 분석 결과 저장 성공: {video_data['video_id']}")
                return result.data[0]
            else:
                logger.error(f"비디오 분석 결과 저장 실패: {result}")
                return None
                
        except Exception as e:
            logger.error(f"데이터베이스 저장 중 오류: {e}")
            return None

    def _clean_video_data(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """데이터베이스 저장을 위한 데이터 정제"""
        clean_data = {}
        
        # 필수 필드만 저장
        fields_mapping = {
            'video_id': str,
            'title': str,
            'url': str,
            'channel_name': str,
            'upload_date': str,
            'duration_seconds': int,
            'target_condition': str,
            'exercise_purpose': str,
            'difficulty_level': int,
            'exercise_type': str,
            'body_parts': list,
            'intensity': str,
            'equipment_needed': str,
            'view_count': int,
            'like_count': int,
            'comment_count': int,
            'creator_type': str,
            'credential_verified': bool,
            'medical_accuracy': float,
            'age_group': str,
            'fitness_level': str,
            'pain_level_range': str,
            'effectiveness_score': float,
            'completion_rate': float,
            'user_rating': float,
            'contraindications': str,
            'expected_benefits': str,
            'safety_level': str,
            'analysis_date': str
        }
        
        for field, field_type in fields_mapping.items():
            value = video_data.get(field)
            
            if value is not None:
                try:
                    if field_type == list:
                        clean_data[field] = json.dumps(value) if isinstance(value, list) else str(value)
                    elif field_type == str:
                        clean_data[field] = str(value)
                    elif field_type == int:
                        clean_data[field] = int(float(value)) if value else 0
                    elif field_type == float:
                        clean_data[field] = float(value) if value else 0.0
                    elif field_type == bool:
                        clean_data[field] = bool(value)
                except (ValueError, TypeError) as e:
                    logger.warning(f"필드 {field} 변환 실패: {e}")
                    # 기본값 설정
                    if field_type == str:
                        clean_data[field] = ""
                    elif field_type == int:
                        clean_data[field] = 0
                    elif field_type == float:
                        clean_data[field] = 0.0
                    elif field_type == bool:
                        clean_data[field] = False
                    elif field_type == list:
                        clean_data[field] = "[]"
        
        # 타임스탬프 추가
        clean_data['created_at'] = datetime.now().isoformat()
        clean_data['updated_at'] = datetime.now().isoformat()
        
        return clean_data

    def update_video_analysis(self, video_id: str, update_data: Dict[str, Any]) -> Optional[Dict]:
        """기존 비디오 분석 결과 업데이트"""
        try:
            if not self.supabase:
                return None
                
            clean_data = self._clean_video_data(update_data)
            clean_data['updated_at'] = datetime.now().isoformat()
            
            result = self.supabase.table('video_analysis').update(clean_data).eq('video_id', video_id).execute()
            
            if result.data:
                logger.info(f"비디오 분석 결과 업데이트 성공: {video_id}")
                return result.data[0]
            else:
                logger.error(f"비디오 분석 결과 업데이트 실패: {result}")
                return None
                
        except Exception as e:
            logger.error(f"데이터베이스 업데이트 중 오류: {e}")
            return None

    def get_video_by_id(self, video_id: str) -> Optional[Dict]:
        """비디오 ID로 분석 결과 조회"""
        try:
            if not self.supabase:
                return None
                
            result = self.supabase.table('video_analysis').select('*').eq('video_id', video_id).execute()
            
            if result.data:
                return self._process_video_data(result.data[0])
            return None
            
        except Exception as e:
            logger.error(f"비디오 조회 중 오류: {e}")
            return None

    def get_videos_by_condition(self, condition: str, purpose: Optional[str] = None, 
                               limit: int = 10) -> List[Dict]:
        """조건별 비디오 목록 조회 - 개선된 버전"""
        try:
            if not self.supabase:
                logger.warning("Supabase 연결이 없어 빈 목록을 반환합니다.")
                return []
            
            # 조건 정규화
            normalized_condition = self._normalize_condition(condition)
            
            query = self.supabase.table('video_analysis').select('*')
            
            # 조건 필터
            if normalized_condition and normalized_condition != '기타':
                query = query.eq('target_condition', normalized_condition)
            
            # 목적 필터
            if purpose:
                normalized_purpose = self._normalize_purpose(purpose)
                query = query.eq('exercise_purpose', normalized_purpose)
            
            # 정렬: 효과성 점수 -> 의학적 정확성 -> 조회수
            result = query.order('effectiveness_score', desc=True)\
                         .order('medical_accuracy', desc=True)\
                         .order('view_count', desc=True)\
                         .limit(limit)\
                         .execute()
            
            videos = []
            if result.data:
                for video in result.data:
                    processed_video = self._process_video_data(video)
                    if processed_video:
                        videos.append(processed_video)
            
            logger.info(f"조건 '{condition}' 목적 '{purpose}': {len(videos)}개 비디오 조회")
            return videos
            
        except Exception as e:
            logger.error(f"조건별 비디오 조회 중 오류: {e}")
            return []

    def get_recommended_videos_for_user(self, user_profile: Dict[str, Any], limit: int = 5) -> List[Dict]:
        """사용자 프로필 기반 맞춤 추천 비디오"""
        try:
            if not self.supabase:
                return []
            
            conditions = user_profile.get('conditions', [])
            pain_scores = user_profile.get('pain_scores', {})
            exercise_purpose = user_profile.get('exercise_purpose', '예방')
            fitness_level = user_profile.get('fitness_level', '초보')
            age = user_profile.get('age', 30)
            
            # 통증 수준에 따른 목적 자동 결정
            if pain_scores:
                max_pain = max(pain_scores.values()) if pain_scores.values() else 5
                if max_pain >= 7:
                    exercise_purpose = '재활'
                elif max_pain >= 4:
                    exercise_purpose = '운동'
                else:
                    exercise_purpose = '예방'
            
            # 나이대 결정
            if age < 30:
                age_group = '20대'
            elif age < 40:
                age_group = '30대'
            elif age < 50:
                age_group = '40대'
            else:
                age_group = '전연령'
            
            all_recommended = []
            
            # 각 조건별로 추천 비디오 수집
            for condition in conditions:
                videos = self.get_videos_by_condition(condition, exercise_purpose, limit=3)
                
                # 사용자 프로필에 맞는 필터링
                filtered_videos = []
                for video in videos:
                    if self._is_suitable_for_user(video, fitness_level, age_group):
                        filtered_videos.append(video)
                
                all_recommended.extend(filtered_videos[:2])  # 조건당 최대 2개
            
            # 중복 제거 및 점수 기반 정렬
            unique_videos = {}
            for video in all_recommended:
                video_id = video.get('video_id')
                if video_id and video_id not in unique_videos:
                    unique_videos[video_id] = video
            
            # 정렬: 효과성 점수 기준
            sorted_videos = sorted(
                unique_videos.values(),
                key=lambda x: (x.get('effectiveness_score', 0), x.get('medical_accuracy', 0)),
                reverse=True
            )
            
            return sorted_videos[:limit]
            
        except Exception as e:
            logger.error(f"사용자 맞춤 추천 중 오류: {e}")
            return []

    def _normalize_condition(self, condition: str) -> str:
        """조건명 정규화"""
        if not condition:
            return '기타'
        
        condition_lower = condition.lower().replace('_', ' ')
        
        # 손목터널증후군 통일화
        if any(keyword in condition_lower for keyword in ['손목터널', '손목증후군', '왼쪽', '오른쪽']):
            return '손목터널증후군'
        elif '거북목' in condition_lower:
            return '거북목'
        elif '라운드숄더' in condition_lower:
            return '라운드숄더'
        elif '허리' in condition_lower:
            return '허리디스크'
        else:
            return '기타'

    def _normalize_purpose(self, purpose: str) -> str:
        """목적 정규화"""
        if not purpose:
            return '예방'
        
        purpose_lower = purpose.lower()
        
        if '예방' in purpose_lower or '자세교정' in purpose_lower:
            return '예방'
        elif '재활' in purpose_lower or '통증' in purpose_lower:
            return '재활'
        elif '운동' in purpose_lower or '근력' in purpose_lower:
            return '운동'
        else:
            return '예방'

    def _process_video_data(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """데이터베이스에서 가져온 비디오 데이터 처리"""
        try:
            processed = video_data.copy()
            
            # body_parts JSON 파싱
            if 'body_parts' in processed and isinstance(processed['body_parts'], str):
                try:
                    processed['body_parts'] = json.loads(processed['body_parts'])
                except json.JSONDecodeError:
                    processed['body_parts'] = []
            
            # URL 생성 (없는 경우)
            if 'url' not in processed or not processed['url']:
                video_id = processed.get('video_id', '')
                processed['url'] = f"https://www.youtube.com/watch?v={video_id}"
            
            return processed
            
        except Exception as e:
            logger.error(f"비디오 데이터 처리 중 오류: {e}")
            return video_data

    def _is_suitable_for_user(self, video: Dict[str, Any], fitness_level: str, age_group: str) -> bool:
        """비디오가 사용자에게 적합한지 확인"""
        try:
            # 피트니스 레벨 확인
            video_fitness = video.get('fitness_level', '전체')
            if video_fitness != '전체' and video_fitness != fitness_level:
                # 초보자에게는 중급 이하만, 고급자에게는 모든 레벨
                if fitness_level == '초보' and video_fitness in ['중급', '고급']:
                    return False
            
            # 나이대 확인
            video_age = video.get('age_group', '전연령')
            if video_age != '전연령' and video_age != age_group:
                return False
            
            # 안전성 확인
            safety_level = video.get('safety_level', '안전')
            if safety_level == '위험':
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"적합성 확인 중 오류: {e}")
            return True  # 보수적으로 적합하다고 판단

    def get_analytics(self) -> Dict[str, Any]:
        """데이터베이스 분석 정보"""
        try:
            if not self.supabase:
                return {'total_videos': 0, 'conditions': {}, 'last_updated': None}
            
            # 전체 비디오 수
            total_result = self.supabase.table('video_analysis').select('id', count='exact').execute()
            total_count = total_result.count if total_result.count else 0
            
            # 조건별 비디오 수
            conditions_count = {}
            for condition in ['거북목', '라운드숄더', '허리디스크', '손목터널증후군']:
                condition_result = self.supabase.table('video_analysis')\
                    .select('id', count='exact')\
                    .eq('target_condition', condition)\
                    .execute()
                conditions_count[condition] = condition_result.count if condition_result.count else 0
            
            return {
                'total_videos': total_count,
                'conditions': conditions_count,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"분석 정보 조회 중 오류: {e}")
            return {'total_videos': 0, 'conditions': {}, 'last_updated': None}

    def update_user_feedback(self, video_id: str, user_rating: float, 
                           effectiveness_score: float, completion_rate: float) -> bool:
        """사용자 피드백 업데이트"""
        try:
            if not self.supabase:
                return False
            
            # 기존 데이터 조회
            current = self.get_video_by_id(video_id)
            if not current:
                logger.error(f"비디오 {video_id}를 찾을 수 없습니다.")
                return False
            
            # 평균 계산 (기존 값이 있다면 가중평균)
            current_rating = current.get('user_rating', 0) or 0
            current_effectiveness = current.get('effectiveness_score', 0) or 0
            current_completion = current.get('completion_rate', 0) or 0
            
            # 간단한 가중평균 (새 피드백 30%, 기존 70%)
            new_rating = (current_rating * 0.7) + (user_rating * 0.3)
            new_effectiveness = (current_effectiveness * 0.7) + (effectiveness_score * 0.3)
            new_completion = (current_completion * 0.7) + (completion_rate * 0.3)
            
            update_data = {
                'user_rating': round(new_rating, 2),
                'effectiveness_score': round(new_effectiveness, 2),
                'completion_rate': round(new_completion, 4),
                'updated_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('video_analysis').update(update_data).eq('video_id', video_id).execute()
            
            if result.data:
                logger.info(f"사용자 피드백 업데이트 성공: {video_id}")
                return True
            else:
                logger.error(f"사용자 피드백 업데이트 실패: {result}")
                return False
                
        except Exception as e:
            logger.error(f"사용자 피드백 업데이트 중 오류: {e}")
            return False

# 전역 데이터베이스 인스턴스
try:
    db = VideoDatabase()
except Exception as e:
    logger.error(f"데이터베이스 초기화 실패: {e}")
    db = None

# app.py에서 사용할 수 있는 헬퍼 함수들
def get_videos_for_condition(condition: str, purpose: str = None, limit: int = 10) -> List[Dict]:
    """조건별 비디오 목록 반환 (app.py 연동용)"""
    if db:
        return db.get_videos_by_condition(condition, purpose, limit)
    else:
        logger.warning("데이터베이스 연결이 없어 빈 목록을 반환합니다.")
        return []

def get_recommended_videos_for_user(user_profile: Dict[str, Any], limit: int = 5) -> List[Dict]:
    """사용자 맞춤 비디오 추천 (app.py 연동용)"""
    if db:
        return db.get_recommended_videos_for_user(user_profile, limit)
    else:
        logger.warning("데이터베이스 연결이 없어 빈 목록을 반환합니다.")
        return []

def save_video_analysis_result(video_data: Dict[str, Any]) -> bool:
    """비디오 분석 결과 저장 (app.py 연동용)"""
    if db:
        result = db.insert_video_analysis(video_data)
        return result is not None
    else:
        logger.warning("데이터베이스 연결이 없어 저장을 건너뜁니다.")
        return False

def update_video_user_feedback(video_id: str, rating: float, effectiveness: float, completion: float) -> bool:
    """사용자 피드백 업데이트 (app.py 연동용)"""
    if db:
        return db.update_user_feedback(video_id, rating, effectiveness, completion)
    else:
        logger.warning("데이터베이스 연결이 없어 피드백 업데이트를 건너뜁니다.")
        return False

def get_database_analytics() -> Dict[str, Any]:
    """데이터베이스 분석 정보 (app.py 연동용)"""
    if db:
        return db.get_analytics()
    else:
        return {'total_videos': 0, 'conditions': {}, 'last_updated': None}
