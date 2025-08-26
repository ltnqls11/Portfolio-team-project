"""
VDT 자동 메일 스케줄러 독립 실행 스크립트
이 스크립트를 실행하면 Streamlit과 독립적으로 자동 메일 발송이 시작됩니다.
"""

import os
import sys
import time
import json
from email_scheduler import EmailScheduler

def main():
    print("🚀 VDT 자동 메일 스케줄러 독립 실행")
    print("=" * 50)
    
    # 스케줄러 인스턴스 생성
    scheduler = EmailScheduler()
    
    # 현재 설정 표시
    status = scheduler.get_status()
    print(f"📧 스케줄러 활성화: {status['enabled']}")
    print(f"🏃 실행 상태: {'실행 중' if status['running'] else '중지됨'}")
    print(f"📬 발송 횟수: {status['email_count']}회")
    if status['last_email_time']:
        print(f"⏰ 마지막 발송: {status['last_email_time']}")
    
    if not status['enabled']:
        print("\n❌ 스케줄러가 비활성화되어 있습니다.")
        print("💡 Streamlit 앱에서 '자동 메일 스케줄러 사용'을 체크하고 설정을 완료해주세요.")
        return
    
    print(f"\n📧 수신자: {status['config']['email_settings']['recipient_email']}")
    print(f"⏰ 발송 간격: {status['config']['schedule_settings']['interval_minutes']}분마다")
    print(f"🕒 근무 시간: {status['config']['schedule_settings']['work_start_time']} ~ {status['config']['schedule_settings']['work_end_time']}")
    print(f"📅 평일만 발송: {status['config']['schedule_settings']['work_days_only']}")
    
    print("\n🎯 스케줄러를 시작합니다...")
    success = scheduler.start()
    
    if success:
        print("✅ 자동 메일 스케줄러가 시작되었습니다!")
        print("💡 프로그램을 종료하려면 Ctrl+C를 누르세요.")
        print("🔄 상태 업데이트는 실시간으로 표시됩니다.")
        print("-" * 50)
        
        try:
            last_count = 0
            while True:
                time.sleep(10)  # 10초마다 상태 체크
                
                current_status = scheduler.get_status()
                if current_status['email_count'] > last_count:
                    print(f"📧 새 메일 발송됨! (총 {current_status['email_count']}회)")
                    if current_status['last_email_time']:
                        print(f"⏰ 발송 시간: {current_status['last_email_time']}")
                    last_count = current_status['email_count']
                
        except KeyboardInterrupt:
            print("\n⏸️ 사용자에 의해 중단되었습니다.")
            success = scheduler.stop()
            if success:
                print("✅ 스케줄러가 정상적으로 중지되었습니다.")
            else:
                print("⚠️ 스케줄러 중지 중 문제가 발생했습니다.")
    else:
        print("❌ 스케줄러 시작에 실패했습니다.")
        print("💡 설정을 확인하고 다시 시도해주세요.")

if __name__ == "__main__":
    main()