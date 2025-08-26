"""
사용자의 방문 횟수 확인 스크립트
"""

from customer_database import CustomerDatabase
import json

def check_user_visits(email):
    """특정 사용자의 방문 정보 확인"""
    db = CustomerDatabase()
    
    # 고객 데이터 조회
    customer_data = db.get_customer_data(email)
    
    if customer_data:
        print(f"\n=== {email} 방문 정보 ===")
        
        # personal_info 파싱
        personal_info = customer_data.get('personal_info', {})
        
        # 방문 횟수
        visit_count = personal_info.get('visit_count', 1)
        print(f"총 방문 횟수: {visit_count}회")
        
        # 마지막 방문 시간
        last_visit = personal_info.get('last_visit', 'N/A')
        print(f"마지막 방문: {last_visit}")
        
        # 계정 생성일
        created_at = customer_data.get('created_at', 'N/A')
        print(f"첫 방문: {created_at}")
        
        # 마지막 업데이트
        updated_at = customer_data.get('updated_at', 'N/A')
        print(f"마지막 업데이트: {updated_at}")
        
        # 증상 정보
        conditions = customer_data.get('conditions', [])
        print(f"등록된 증상: {conditions}")
        
        # 통증 점수
        pain_scores = customer_data.get('pain_scores', {})
        print(f"통증 점수: {pain_scores}")
        
        return visit_count
    else:
        print(f"\n{email} - 등록된 고객 정보가 없습니다.")
        return 0

def list_all_users():
    """모든 사용자의 방문 횟수 확인"""
    db = CustomerDatabase()
    
    # 모든 고객 목록 조회
    customers = db.get_all_customers()
    
    print("\n=== 전체 사용자 방문 현황 ===")
    print(f"총 등록 사용자: {len(customers)}명\n")
    
    for customer in customers:
        email = customer['email']
        visit_count = db.get_visit_count(email)
        print(f"- {email}: {visit_count}회 방문")

if __name__ == "__main__":
    # 특정 사용자 확인
    target_email = "younjc7450@gmail.com"
    visit_count = check_user_visits(target_email)
    
    # 전체 사용자 목록
    print("\n" + "="*50)
    list_all_users()
    
    # 방문 횟수 테스트 증가
    if visit_count > 0:
        print("\n" + "="*50)
        print(f"\n방문 횟수 증가 테스트...")
        db = CustomerDatabase()
        new_count = db.increment_visit_count(target_email)
        print(f"{target_email}: {visit_count}회 → {new_count}회")