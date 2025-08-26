"""
기존 Supabase 테이블에서 새로운 통합 테이블로 데이터 마이그레이션
"""

from supabase import create_client, Client
import os
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()

def migrate_supabase_data():
    """기존 데이터를 새로운 테이블 구조로 마이그레이션"""
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_ANON_KEY')
    
    if not url or not key:
        print("Supabase 환경변수가 설정되지 않았습니다.")
        return False
    
    client = create_client(url, key)
    
    print("=== 데이터 마이그레이션 시작 ===")
    
    try:
        # 1. customer_history 데이터를 customers 테이블로 마이그레이션
        print("1. 고객 데이터 마이그레이션 중...")
        
        old_customers = client.table('customer_history').select('*').execute()
        
        migrated_customers = 0
        for customer in old_customers.data:
            try:
                # 중복 확인
                existing = client.table('customers').select('id').eq('email', customer['email']).execute()
                
                if not existing.data:
                    new_customer = {
                        'email': customer['email'],
                        'personal_info': customer.get('user_data', '{}'),
                        'conditions': customer.get('conditions', '[]'),
                        'pain_scores': customer.get('pain_scores', '{}'),
                        'created_at': customer.get('created_at', datetime.now().isoformat()),
                        'updated_at': customer.get('updated_at', datetime.now().isoformat())
                    }
                    
                    client.table('customers').insert(new_customer).execute()
                    migrated_customers += 1
                    print(f"  ✓ {customer['email']} 마이그레이션 완료")
                else:
                    print(f"  - {customer['email']} 이미 존재")
                    
            except Exception as e:
                print(f"  ✗ {customer['email']} 마이그레이션 실패: {e}")
        
        print(f"고객 데이터 마이그레이션 완료: {migrated_customers}개")
        
        # 2. exercise_management 데이터를 exercise_records 테이블로 마이그레이션
        print("\n2. 운동/통증 데이터 마이그레이션 중...")
        
        old_records = client.table('exercise_management').select('*').execute()
        
        migrated_records = 0
        for record in old_records.data:
            try:
                # 중복 확인
                existing = client.table('exercise_records').select('id').eq('email', record['user_email']).eq('record_type', record['data_type']).eq('record_date', record['date']).execute()
                
                if not existing.data:
                    new_record = {
                        'email': record['user_email'],
                        'record_type': record['data_type'],
                        'record_date': record['date'],
                        'value': str(record['value']),
                        'created_at': record.get('created_at', datetime.now().isoformat()),
                        'updated_at': datetime.now().isoformat()
                    }
                    
                    client.table('exercise_records').insert(new_record).execute()
                    migrated_records += 1
                    print(f"  ✓ {record['user_email']} - {record['data_type']} - {record['date']} 마이그레이션 완료")
                else:
                    print(f"  - {record['user_email']} - {record['data_type']} - {record['date']} 이미 존재")
                    
            except Exception as e:
                print(f"  ✗ 레코드 마이그레이션 실패: {e}")
        
        print(f"운동/통증 데이터 마이그레이션 완료: {migrated_records}개")
        
        print("\n=== 마이그레이션 완료 ===")
        print(f"총 {migrated_customers}개 고객, {migrated_records}개 기록 마이그레이션")
        
        return True
        
    except Exception as e:
        print(f"마이그레이션 실패: {e}")
        return False

def cleanup_old_tables():
    """기존 테이블 정리 (주의: 데이터 삭제됨)"""
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_ANON_KEY')
    
    if not url or not key:
        print("Supabase 환경변수가 설정되지 않았습니다.")
        return False
    
    client = create_client(url, key)
    
    tables_to_cleanup = [
        'exercise_management',
        'backup_users', 
        'consultation_history',
        'customer_history',
        'exercise_effectiveness'
    ]
    
    print("\n=== 기존 테이블 데이터 정리 ===")
    print("주의: 이 작업은 기존 데이터를 삭제합니다.")
    
    for table in tables_to_cleanup:
        try:
            result = client.table(table).delete().neq('id', 0).execute()
            print(f"✓ {table} 테이블 데이터 정리 완료")
        except Exception as e:
            print(f"✗ {table} 테이블 정리 실패: {e}")
    
    print("기존 테이블 데이터 정리 완료")
    return True

if __name__ == "__main__":
    print("VDT 데이터베이스 마이그레이션 도구")
    print("=" * 50)
    
    # 마이그레이션 실행
    if migrate_supabase_data():
        print("\n마이그레이션이 성공적으로 완료되었습니다.")
        
        # 기존 테이블 정리 여부 확인
        cleanup = input("\n기존 테이블의 데이터를 정리하시겠습니까? (y/N): ")
        if cleanup.lower() == 'y':
            cleanup_old_tables()
        else:
            print("기존 테이블은 그대로 유지됩니다.")
    else:
        print("\n마이그레이션 실패")