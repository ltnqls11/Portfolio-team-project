#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
간단한 완전한 자동화 실행 스크립트
명령줄에서 쉽게 실행할 수 있는 래퍼 스크립트
"""

import sys
from complete_automation import CompleteAutomationSystem


def main():
    print("🤖 블로거 마케팅 완전한 자동화 시스템")
    print("="*50)
    
    # 사용자 입력 받기
    try:
        keyword = input("🔍 검색 키워드를 입력하세요: ").strip()
        if not keyword:
            print("❌ 키워드는 필수입니다.")
            return 1
        
        sheet_id = input("📊 Google Sheets ID를 입력하세요: ").strip()
        if not sheet_id:
            print("❌ Google Sheets ID는 필수입니다.")
            return 1
        
        sheet_name = input("📋 시트 이름을 입력하세요 (기본값: Sheet1): ").strip()
        if not sheet_name:
            sheet_name = "Sheet1"
        
        product_name = input("🎁 제품명을 입력하세요: ").strip()
        if not product_name:
            print("❌ 제품명은 필수입니다.")
            return 1
        
        event_info = input("🎉 이벤트 정보를 입력하세요 (기본값: 특별 할인 이벤트): ").strip()
        if not event_info:
            event_info = "특별 할인 이벤트"
        
        sender_name = input("👤 발신자명을 입력하세요 (기본값: 마케팅팀): ").strip()
        if not sender_name:
            sender_name = "마케팅팀"
        
        print("\n" + "="*50)
        print("입력된 정보:")
        print(f"🔍 키워드: {keyword}")
        print(f"📊 Google Sheets: {sheet_id} / {sheet_name}")
        print(f"🎁 제품명: {product_name}")
        print(f"🎉 이벤트: {event_info}")
        print(f"👤 발신자: {sender_name}")
        print("="*50)
        
        confirm = input("\n위 정보로 자동화를 시작하시겠습니까? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("❌ 사용자에 의해 취소되었습니다.")
            return 0
        
        # 자동화 시스템 실행
        automation = CompleteAutomationSystem()
        success = automation.run_complete_automation(
            keyword=keyword,
            sheet_id=sheet_id,
            sheet_name=sheet_name,
            product_name=product_name,
            event_info=event_info,
            sender_name=sender_name
        )
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n⏹️ 사용자에 의해 중단되었습니다.")
        return 0
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())