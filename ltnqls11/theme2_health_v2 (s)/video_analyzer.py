import google.generativeai as genai
import json
import re
import logging
from typing import Dict, Any, Optional, List
import config
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoAnalyzer:
    def __init__(self):
        """Gemini AI 클라이언트 초기화"""
        try:
            genai.configure(api_key=config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("Gemini AI 연결 성공")
        except Exception as e:
            logger.error(f"Gemini AI 연결 실패: {e}")
            raise

    def create_analysis_prompt(self, video_title: str, video_description: str = "", 
                             channel_name: str = "", duration: int = 0) -> str:
        """비디오 분석을 위한 전문가 프롬프트 생성"""
        
        duration_text = f"{duration//60}분 {duration%60}초" if duration > 0 else "정보 없음"
        
        prompt = f"""
당신은 공인된 재활의학과 전문의이자 면허를 받은 물리치료사입니다. 
저는 현재 장시간 컴퓨터와 화면 사용으로 인한 **VDT 증후군** 증상을 겪고 있습니다.

당신의 역할은 저의 디지털 재활 코치가 되어 통증 완화, 자세 교정, 장기적인 치유를 도와주는 것입니다.

다음 YouTube 영상을 의학적 관점에서 분석하고 분류해주세요:

**영상 정보:**
- 제목: {video_title}
- 채널: {channel_name}
- 길이: {duration_text}
- 설명: {video_description[:500] if video_description else "설명 없음"}

**분석 기준:**

다음 JSON 형식으로 정확하게 분석해주세요. 의학적 정확성을 최우선으로 하고, 공감적이면서도 전문적으로 평가해주세요.

```json
{{
  "기본정보": {{
    "target_condition": "거북목",
    "exercise_purpose": "예방",
    "difficulty_level": 3,
    "exercise_type": "스트레칭",
    "body_parts": ["목", "어깨"],
    "intensity": "낮음",
    "equipment_needed": "없음"
  }},
  "전문성평가": {{
    "creator_type": "물리치료사",
    "credential_verified": true,
    "medical_accuracy": 4
  }},
  "사용자맞춤": {{
    "age_group": "전연령",
    "fitness_level": "초보",
    "pain_level_range": "4-6"
  }},
  "의학적소견": {{
    "contraindications": "급성 목 부상이 있는 경우 피하세요",
    "expected_benefits": "목 근육 이완과 혈액순환 개선",
    "safety_level": "안전",
    "professional_recommendation": 4
  }}
}}
```

**필수 분류 값:**
- target_condition: "거북목", "라운드숄더", "허리디스크", "손목터널증후군", "기타" 중 하나
- exercise_purpose: "예방", "운동", "재활" 중 하나  
- difficulty_level: 1-5 (정수)
- exercise_type: "스트레칭", "근력강화", "마사지", "자세교정" 중 하나
- intensity: "낮음", "보통", "높음" 중 하나
- equipment_needed: "없음", "의자", "소도구", "기구" 중 하나
- creator_type: "의사", "물리치료사", "트레이너", "일반인" 중 하나
- age_group: "20대", "30대", "40대", "전연령" 중 하나
- fitness_level: "초보", "중급", "고급", "전체" 중 하나
- pain_level_range: "0-3", "4-6", "7-10" 중 하나
- safety_level: "안전", "주의", "위험" 중 하나

JSON 형식을 정확히 지켜주시고, 한국어로 응답해주세요.
"""
        return prompt

    def analyze_video(self, video_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Gemini AI를 사용하여 비디오 분석"""
        try:
            prompt = self.create_analysis_prompt(
                video_title=video_data.get('title', ''),
                video_description=video_data.get('description', ''),
                channel_name=video_data.get('channel_name', ''),
                duration=video_data.get('duration_seconds', 0)
            )
            
            logger.info(f"비디오 분석 시작: {video_data.get('video_id', 'Unknown')}")
            
            # Gemini AI 호출
            response = self.model.generate_content(prompt)
            
            if not response.text:
                logger.error("Gemini AI로부터 응답을 받지 못했습니다.")
                return None
            
            # JSON 추출 및 파싱
            analysis_result = self._parse_gemini_response(response.text)
            
            if analysis_result:
                # 기본 비디오 정보와 분석 결과 병합
                final_result = self._merge_video_data(video_data, analysis_result)
                logger.info(f"비디오 분석 완료: {video_data.get('video_id', 'Unknown')}")
                return final_result
            else:
                logger.error("Gemini AI 응답 파싱 실패")
                return None
                
        except Exception as e:
            logger.error(f"비디오 분석 중 오류: {e}")
            return None

    def _parse_gemini_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Gemini AI 응답에서 JSON 추출 및 파싱"""
        try:
            # 먼저 JSON 코드 블록 추출
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)
            else:
                # JSON 블록이 없다면 { } 사이의 내용 찾기
                json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text, re.DOTALL)
                if json_match:
                    json_text = json_match.group(0)
                else:
                    logger.error("JSON 형식을 찾을 수 없습니다.")
                    logger.error(f"응답 텍스트: {response_text[:200]}...")
                    return self._create_default_analysis()
            
            # JSON 파싱
            parsed_data = json.loads(json_text)
            
            # 데이터 검증 및 기본값 설정
            return self._validate_and_fix_data(parsed_data)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 오류: {e}")
            logger.error(f"파싱 시도한 텍스트: {json_text[:200] if 'json_text' in locals() else 'N/A'}...")
            return self._create_default_analysis()
        except Exception as e:
            logger.error(f"응답 파싱 중 오류: {e}")
            return self._create_default_analysis()

    def _create_default_analysis(self) -> Dict[str, Any]:
        """파싱 실패 시 기본 분석 결과 생성"""
        return {
            "기본정보": {
                "target_condition": "기타",
                "exercise_purpose": "예방",
                "difficulty_level": 3,
                "exercise_type": "스트레칭",
                "body_parts": ["목", "어깨"],
                "intensity": "보통",
                "equipment_needed": "없음"
            },
            "전문성평가": {
                "creator_type": "일반인",
                "credential_verified": False,
                "medical_accuracy": 3
            },
            "사용자맞춤": {
                "age_group": "전연령",
                "fitness_level": "초보",
                "pain_level_range": "4-6"
            },
            "의학적소견": {
                "contraindications": "특별한 주의사항 없음",
                "expected_benefits": "기본적인 운동 효과",
                "safety_level": "안전",
                "professional_recommendation": 3
            }
        }

    def _validate_and_fix_data(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """파싱된 데이터 검증 및 수정"""
        # 기본 구조 확인
        required_sections = ["기본정보", "전문성평가", "사용자맞춤", "의학적소견"]
        
        for section in required_sections:
            if section not in parsed_data:
                logger.warning(f"{section} 섹션이 없어서 기본값으로 설정합니다.")
                parsed_data[section] = self._create_default_analysis()[section]
        
        # 각 섹션의 필수 필드 확인 및 기본값 설정
        default_data = self._create_default_analysis()
        
        for section_name, section_data in default_data.items():
            if section_name in parsed_data:
                for key, default_value in section_data.items():
                    if key not in parsed_data[section_name] or parsed_data[section_name][key] is None:
                        parsed_data[section_name][key] = default_value
        
        return parsed_data

    def _merge_video_data(self, video_data: Dict[str, Any], analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """비디오 기본 정보와 AI 분석 결과 병합"""
        try:
            # 기본 정보 추출
            basic_info = analysis_result.get('기본정보', {})
            expert_eval = analysis_result.get('전문성평가', {})
            user_custom = analysis_result.get('사용자맞춤', {})
            medical_opinion = analysis_result.get('의학적소견', {})
            
            # 정제된 25개 컬럼 데이터 구조
            merged_data = {
                # 기본 정보 (6개)
                'video_id': video_data.get('video_id', ''),
                'title': video_data.get('title', ''),
                'url': f"https://www.youtube.com/watch?v={video_data.get('video_id', '')}",
                'channel_name': video_data.get('channel_name', ''),
                'upload_date': video_data.get('upload_date'),
                'duration_seconds': video_data.get('duration_seconds', 0),
                
                # 의료/운동 분류 (7개) - AI 응답 정규화 적용
                'target_condition': self._normalize_condition(basic_info.get('target_condition', '기타')),
                'exercise_purpose': self._normalize_exercise_purpose(basic_info.get('exercise_purpose', '예방')),
                'difficulty_level': basic_info.get('difficulty_level', 3),
                'exercise_type': self._normalize_exercise_type(basic_info.get('exercise_type', '스트레칭')),
                'body_parts': basic_info.get('body_parts', []),
                'intensity': basic_info.get('intensity', '보통'),
                'equipment_needed': basic_info.get('equipment_needed', '없음'),
                
                # 품질 지표 (3개) - like_ratio 제거
                'view_count': video_data.get('view_count', 0),
                'like_count': video_data.get('like_count', 0),
                'comment_count': video_data.get('comment_count', 0),
                
                # 전문성 검증 (3개) - 제작자 유형 정규화
                'creator_type': self._normalize_creator_type(expert_eval.get('creator_type', '일반인')),
                'credential_verified': expert_eval.get('credential_verified', False),
                'medical_accuracy': expert_eval.get('medical_accuracy', 3),
                
                # 사용자 맞춤화 (3개) - work_break_suitable, office_friendly 제거
                'age_group': user_custom.get('age_group', '전연령'),
                'fitness_level': user_custom.get('fitness_level', '전체'),
                'pain_level_range': user_custom.get('pain_level_range', '4-6'),
                
                # 효과성 추적 (3개) - 초기값 설정
                'effectiveness_score': float(medical_opinion.get('professional_recommendation', 3.0)),
                'completion_rate': 0.0,  # 사용자 피드백으로 업데이트
                'user_rating': 0.0,     # 사용자 피드백으로 업데이트
                
                # 추가 의학적 정보 (분석용)
                'contraindications': medical_opinion.get('contraindications', ''),
                'expected_benefits': medical_opinion.get('expected_benefits', ''),
                'safety_level': medical_opinion.get('safety_level', '안전'),
                'analysis_date': datetime.now().isoformat()
            }
            
            return merged_data
            
        except Exception as e:
            logger.error(f"데이터 병합 중 오류: {e}")
            return video_data
    
    def _normalize_condition(self, condition: str) -> str:
        """손목터널증후군 조건 통일화 및 AI 응답 정규화"""
        if not condition:
            return '기타'
            
        condition = condition.lower().strip()
        
        # 손목터널증후군 통일화
        if any(keyword in condition for keyword in ['손목터널', '손목증후군', 'carpal', '왼쪽', '오른쪽', '양쪽']):
            return '손목터널증후군'
        elif any(keyword in condition for keyword in ['거북목', 'turtle', '목']):
            return '거북목'
        elif any(keyword in condition for keyword in ['라운드숄더', 'round', '어깨']):
            return '라운드숄더'
        elif any(keyword in condition for keyword in ['허리디스크', '허리', 'disc', '요추']):
            return '허리디스크'
        else:
            return '기타'
    
    def _normalize_exercise_purpose(self, purpose: str) -> str:
        """운동 목적 정규화"""
        if not purpose:
            return '예방'
            
        purpose = purpose.lower().strip()
        
        if any(keyword in purpose for keyword in ['예방', 'prevention', '자세교정']):
            return '예방'
        elif any(keyword in purpose for keyword in ['재활', 'rehabilitation', '치료', '통증']):
            return '재활'
        elif any(keyword in purpose for keyword in ['운동', 'exercise', '근력', '체력']):
            return '운동'
        else:
            return '예방'
    
    def _normalize_exercise_type(self, exercise_type: str) -> str:
        """운동 유형 정규화"""
        if not exercise_type:
            return '스트레칭'
            
        exercise_type = exercise_type.lower().strip()
        
        if any(keyword in exercise_type for keyword in ['스트레칭', 'stretching', '스트레치']):
            return '스트레칭'
        elif any(keyword in exercise_type for keyword in ['근력', 'strength', '강화', '운동']):
            return '근력강화'
        elif any(keyword in exercise_type for keyword in ['마사지', 'massage', '지압']):
            return '마사지'
        elif any(keyword in exercise_type for keyword in ['자세교정', 'posture', '자세']):
            return '자세교정'
        else:
            return '스트레칭'
    
    def _normalize_creator_type(self, creator_type: str) -> str:
        """제작자 유형 정규화"""
        if not creator_type:
            return '일반인'
            
        creator_type = creator_type.lower().strip()
        
        if any(keyword in creator_type for keyword in ['의사', 'doctor', 'md', '의학']):
            return '의사'
        elif any(keyword in creator_type for keyword in ['물리치료', 'physical', 'pt', '치료사']):
            return '물리치료사'
        elif any(keyword in creator_type for keyword in ['트레이너', 'trainer', '헬스', '운동']):
            return '트레이너'
        else:
            return '일반인'

    def validate_analysis_result(self, analysis_data: Dict[str, Any]) -> bool:
        """분석 결과 유효성 검증"""
        required_fields = [
            'video_id', 'target_condition', 'exercise_purpose',
            'difficulty_level', 'creator_type', 'medical_accuracy'
        ]
        
        for field in required_fields:
            if field not in analysis_data or analysis_data[field] is None:
                logger.error(f"필수 필드 누락: {field}")
                return False
        
        # 값 범위 검증
        if not (1 <= analysis_data.get('difficulty_level', 0) <= 5):
            logger.error("difficulty_level은 1-5 범위여야 합니다.")
            return False
        
        if not (1 <= analysis_data.get('medical_accuracy', 0) <= 5):
            logger.error("medical_accuracy는 1-5 범위여야 합니다.")
            return False
        
        return True

    def get_analysis_summary(self, analysis_data: Dict[str, Any]) -> str:
        """분석 결과 요약 텍스트 생성"""
        try:
            summary = f"""
📊 **영상 분석 결과**

🎯 **대상 증상**: {analysis_data.get('target_condition', '정보없음')}
🏃 **운동 목적**: {analysis_data.get('exercise_purpose', '정보없음')}
⭐ **난이도**: {analysis_data.get('difficulty_level', 0)}/5
💪 **운동 유형**: {analysis_data.get('exercise_type', '정보없음')}
🏥 **전문성**: {analysis_data.get('creator_type', '정보없음')}
📈 **의학적 정확성**: {analysis_data.get('medical_accuracy', 0)}/5
🏢 **사무실 적합**: {'✅' if analysis_data.get('office_friendly', False) else '❌'}
⏰ **업무 중 실행**: {'✅' if analysis_data.get('work_break_suitable', False) else '❌'}

💡 **추천 대상**: {analysis_data.get('fitness_level', '전체')} 수준, {analysis_data.get('age_group', '전연령')}
🩺 **적합 통증 범위**: VAS {analysis_data.get('pain_level_range', '4-6')}점
"""
            return summary
        except Exception as e:
            logger.error(f"요약 생성 중 오류: {e}")
            return "분석 결과 요약을 생성할 수 없습니다."

    def batch_analyze_videos(self, video_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """여러 비디오를 일괄 분석"""
        analyzed_videos = []
        
        for i, video_data in enumerate(video_list):
            try:
                logger.info(f"비디오 분석 진행: {i+1}/{len(video_list)}")
                
                analysis_result = self.analyze_video(video_data)
                
                if analysis_result:
                    analyzed_videos.append(analysis_result)
                else:
                    logger.warning(f"비디오 분석 실패: {video_data.get('video_id', 'Unknown')}")
                
                # API 호출 제한을 위한 짧은 대기
                import time
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"비디오 분석 중 오류: {e}")
                continue
        
        logger.info(f"일괄 분석 완료: {len(analyzed_videos)}/{len(video_list)}개 성공")
        return analyzed_videos

# 전역 분석기 인스턴스
analyzer = VideoAnalyzer()

# app.py에서 사용할 수 있는 헬퍼 함수들
def analyze_single_video(video_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """단일 비디오 분석 (app.py 연동용)"""
    return analyzer.analyze_video(video_data)

def analyze_multiple_videos(video_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """다중 비디오 분석 (app.py 연동용)"""
    return analyzer.batch_analyze_videos(video_list)

def get_video_analysis_summary(analysis_data: Dict[str, Any]) -> str:
    """분석 결과 요약 (app.py 연동용)"""
    return analyzer.get_analysis_summary(analysis_data)
