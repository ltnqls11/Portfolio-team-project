"""
통합 고객 데이터 관리 시스템
Supabase를 사용한 고객 정보 및 운동/통증 기록 통합 관리
"""

from supabase import create_client, Client
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, date
import json
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomerDatabase:
    def __init__(self):
        """Supabase 클라이언트 초기화"""
        try:
            self.supabase: Client = create_client(
                config.SUPABASE_URL, 
                config.SUPABASE_ANON_KEY
            )
            logger.info("Customer Database 연결 성공")
            self._ensure_tables_exist()
        except Exception as e:
            logger.error(f"Supabase 연결 실패: {e}")
            self.supabase = None

    def _ensure_tables_exist(self):
        """필요한 테이블 존재 여부 확인"""
        if not self.supabase:
            return False
        
        try:
            # customers 테이블 확인 (생성은 Supabase 콘솔에서)
            self.supabase.table('customers').select('id').limit(1).execute()
            logger.info("customers 테이블 확인 완료")
            
            # exercise_records 테이블 확인
            self.supabase.table('exercise_records').select('id').limit(1).execute()
            logger.info("exercise_records 테이블 확인 완료")
            
            return True
        except Exception as e:
            logger.warning(f"테이블 확인 실패: {e}")
            return False

    def save_customer_data(self, email: str, user_data: Dict, conditions: List[str], pain_scores: Dict) -> bool:
        """고객 기본 정보 저장/업데이트"""
        if not self.supabase:
            logger.warning("Supabase 연결이 없습니다")
            return False
        
        try:
            # 기존 고객 확인
            existing = self.supabase.table('customers').select('*').eq('email', email).execute()
            
            if existing.data:
                # 기존 고객 - personal_info에서 visit_count와 last_visit 보존
                existing_personal_info = json.loads(existing.data[0]['personal_info']) if existing.data[0]['personal_info'] else {}
                
                # visit_count와 last_visit 정보 보존
                if 'visit_count' in existing_personal_info:
                    user_data['visit_count'] = existing_personal_info['visit_count']
                if 'last_visit' in existing_personal_info:
                    user_data['last_visit'] = existing_personal_info['last_visit']
            
            customer_data = {
                'email': email,
                'personal_info': json.dumps(user_data, ensure_ascii=False, default=str),
                'conditions': json.dumps(conditions, ensure_ascii=False),
                'pain_scores': json.dumps(pain_scores, ensure_ascii=False),
                'updated_at': datetime.now().isoformat()
            }
            
            if existing.data:
                # 업데이트
                result = self.supabase.table('customers').update(customer_data).eq('email', email).execute()
                logger.info(f"고객 데이터 업데이트: {email}")
            else:
                # 새로 생성 - 첫 방문이므로 visit_count = 1로 설정
                user_data['visit_count'] = 1
                user_data['last_visit'] = datetime.now().isoformat()
                customer_data['personal_info'] = json.dumps(user_data, ensure_ascii=False, default=str)
                customer_data['created_at'] = datetime.now().isoformat()
                result = self.supabase.table('customers').insert(customer_data).execute()
                logger.info(f"새 고객 데이터 생성: {email}")
            
            return True
            
        except Exception as e:
            logger.error(f"고객 데이터 저장 실패: {e}")
            return False

    def get_customer_data(self, email: str) -> Optional[Dict]:
        """고객 기본 정보 조회"""
        if not self.supabase:
            return None
        
        try:
            result = self.supabase.table('customers').select('*').eq('email', email).execute()
            
            if result.data:
                customer = result.data[0]
                return {
                    'email': customer['email'],
                    'personal_info': json.loads(customer['personal_info']) if customer['personal_info'] else {},
                    'conditions': json.loads(customer['conditions']) if customer['conditions'] else [],
                    'pain_scores': json.loads(customer['pain_scores']) if customer['pain_scores'] else {},
                    'created_at': customer.get('created_at'),
                    'updated_at': customer.get('updated_at')
                }
            return None
            
        except Exception as e:
            logger.error(f"고객 데이터 조회 실패: {e}")
            return None

    def save_exercise_record(self, email: str, record_type: str, value: Any, record_date: str = None) -> bool:
        """운동/통증 기록 저장"""
        if not self.supabase:
            logger.warning("Supabase 연결이 없습니다")
            return False
        
        try:
            if not record_date:
                record_date = str(date.today())
            
            # 같은 날짜의 기존 기록 확인
            existing = self.supabase.table('exercise_records').select('*').eq('email', email).eq('record_type', record_type).eq('record_date', record_date).execute()
            
            record_data = {
                'email': email,
                'record_type': record_type,  # 'exercise_log' 또는 'pain_data'
                'record_date': record_date,
                'value': str(value),
                'updated_at': datetime.now().isoformat()
            }
            
            if existing.data:
                # 업데이트 (같은 날 중복 기록 시)
                result = self.supabase.table('exercise_records').update(record_data).eq('email', email).eq('record_type', record_type).eq('record_date', record_date).execute()
                logger.info(f"운동 기록 업데이트: {email} - {record_type} - {record_date}")
            else:
                # 새로 생성
                record_data['created_at'] = datetime.now().isoformat()
                result = self.supabase.table('exercise_records').insert(record_data).execute()
                logger.info(f"새 운동 기록 생성: {email} - {record_type} - {record_date}")
            
            return True
            
        except Exception as e:
            logger.error(f"운동 기록 저장 실패: {e}")
            return False

    def get_exercise_records(self, email: str, record_type: str = None, days: int = 30) -> List[Dict]:
        """운동/통증 기록 조회"""
        if not self.supabase:
            return []
        
        try:
            query = self.supabase.table('exercise_records').select('*').eq('email', email)
            
            if record_type:
                query = query.eq('record_type', record_type)
            
            # 최근 N일간 데이터
            from datetime import datetime, timedelta
            since_date = (datetime.now() - timedelta(days=days)).date().isoformat()
            query = query.gte('record_date', since_date)
            
            result = query.order('record_date', desc=False).execute()
            
            records = []
            for record in result.data:
                records.append({
                    'record_date': record['record_date'],
                    'record_type': record['record_type'],
                    'value': record['value'],
                    'created_at': record.get('created_at'),
                    'updated_at': record.get('updated_at')
                })
            
            return records
            
        except Exception as e:
            logger.error(f"운동 기록 조회 실패: {e}")
            return []

    def get_visit_count(self, email: str) -> int:
        """고객의 방문 횟수 조회"""
        if not self.supabase:
            return 1
        
        try:
            # personal_info 필드에서 visit_count 조회
            result = self.supabase.table('customers').select('personal_info').eq('email', email).execute()
            
            if result.data:
                personal_info = json.loads(result.data[0]['personal_info']) if result.data[0]['personal_info'] else {}
                return personal_info.get('visit_count', 1)
            return 1
        except Exception as e:
            logger.error(f"방문 횟수 조회 실패: {e}")
            return 1

    def increment_visit_count(self, email: str) -> int:
        """고객의 방문 횟수 증가"""
        if not self.supabase:
            return 1
        
        try:
            # 현재 방문 횟수 조회
            current_count = self.get_visit_count(email)
            new_count = current_count + 1
            
            # personal_info 업데이트
            result = self.supabase.table('customers').select('personal_info').eq('email', email).execute()
            
            if result.data:
                personal_info = json.loads(result.data[0]['personal_info']) if result.data[0]['personal_info'] else {}
                personal_info['visit_count'] = new_count
                personal_info['last_visit'] = datetime.now().isoformat()
                
                # 업데이트
                update_data = {
                    'personal_info': json.dumps(personal_info, ensure_ascii=False, default=str),
                    'updated_at': datetime.now().isoformat()
                }
                self.supabase.table('customers').update(update_data).eq('email', email).execute()
                logger.info(f"방문 횟수 업데이트: {email} - {new_count}회")
                
            return new_count
        except Exception as e:
            logger.error(f"방문 횟수 증가 실패: {e}")
            return current_count if 'current_count' in locals() else 1

    def get_all_customers(self) -> List[Dict]:
        """모든 고객 목록 조회 (관리용)"""
        if not self.supabase:
            return []
        
        try:
            result = self.supabase.table('customers').select('email, created_at, updated_at').order('created_at', desc=True).execute()
            return result.data
        except Exception as e:
            logger.error(f"고객 목록 조회 실패: {e}")
            return []

    def delete_old_exercise_management_data(self):
        """기존 exercise_management 테이블 데이터 정리"""
        if not self.supabase:
            return False
        
        try:
            # exercise_management 테이블의 모든 데이터 삭제
            result = self.supabase.table('exercise_management').delete().neq('id', 0).execute()
            logger.info("exercise_management 테이블 데이터 정리 완료")
            return True
        except Exception as e:
            logger.warning(f"exercise_management 테이블 정리 실패: {e}")
            return False

# 전역 인스턴스
customer_db = CustomerDatabase()

def save_customer_data(email: str, user_data: Dict, conditions: List[str], pain_scores: Dict) -> bool:
    """고객 데이터 저장 함수 (기존 호환성 유지)"""
    return customer_db.save_customer_data(email, user_data, conditions, pain_scores)

def get_customer_data(email: str) -> Optional[Dict]:
    """고객 데이터 조회 함수"""
    return customer_db.get_customer_data(email)

def save_exercise_record(email: str, record_type: str, value: Any, record_date: str = None) -> bool:
    """운동/통증 기록 저장 함수"""
    return customer_db.save_exercise_record(email, record_type, value, record_date)

def get_exercise_records(email: str, record_type: str = None, days: int = 30) -> List[Dict]:
    """운동/통증 기록 조회 함수"""
    return customer_db.get_exercise_records(email, record_type, days)

def get_visit_count(email: str) -> int:
    """방문 횟수 조회 함수"""
    return customer_db.get_visit_count(email)

def increment_visit_count(email: str) -> int:
    """방문 횟수 증가 함수"""
    return customer_db.increment_visit_count(email)