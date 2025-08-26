"""
간단한 알리미 스케줄러 테스트
이메일 발송 없이 스케줄링 로직만 테스트
"""

import json
import os
from datetime import datetime, timedelta

def test_config_and_timing():
    """설정 파일 읽기 및 시간 로직 테스트"""
    print("=== 스케줄러 로직 테스트 ===")
    
    # notification_config.json 파일이 있는지 확인
    config_file = "notification_config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print("O 기존 설정 파일 발견")
            print(f"- 알림 방식: {config.get('type', 'N/A')}")
            print(f"- 수신 이메일: {config.get('email', 'N/A')}")
            print(f"- 근무 시간: {config.get('work_start', 'N/A')} ~ {config.get('work_end', 'N/A')}")
            print(f"- 휴식 간격: {config.get('interval', 'N/A')}분")
            
            # 현재 시간이 근무 시간인지 확인
            now = datetime.now().time()
            work_start = datetime.strptime(config['work_start'], "%H:%M").time()
            work_end = datetime.strptime(config['work_end'], "%H:%M").time()
            
            print(f"\n현재 시간: {now.strftime('%H:%M')}")
            
            if work_start <= now <= work_end:
                print("O 현재 근무 시간입니다")
                
                # 다음 알림 시간 계산
                interval = config.get('interval', 30)
                next_time = datetime.now() + timedelta(minutes=interval)
                print(f"다음 알림 예정 시간: {next_time.strftime('%H:%M')}")
                
                return True
            else:
                print("X 현재 근무 시간이 아닙니다")
                print(f"근무 시간: {work_start.strftime('%H:%M')} ~ {work_end.strftime('%H:%M')}")
                return False
                
        except Exception as e:
            print(f"X 설정 파일 읽기 실패: {e}")
            return False
    else:
        print("X notification_config.json 파일이 없습니다")
        print("먼저 앱에서 알리미 설정을 완료해주세요")
        return False

def test_schedule_library():
    """schedule 라이브러리 설치 및 동작 테스트"""
    print("\n=== Schedule 라이브러리 테스트 ===")
    
    try:
        import schedule
        print("O schedule 라이브러리 로드 성공")
        
        # 간단한 스케줄 테스트
        def test_job():
            print(f"테스트 작업 실행: {datetime.now().strftime('%H:%M:%S')}")
        
        # 5초마다 실행하는 테스트 작업
        schedule.every(5).seconds.do(test_job)
        print("O 5초마다 실행되는 테스트 작업 등록")
        
        # 10초간 테스트
        print("10초간 스케줄 테스트...")
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=10)
        
        import time
        while datetime.now() < end_time:
            schedule.run_pending()
            time.sleep(1)
        
        print("O 스케줄 테스트 완료")
        schedule.clear()  # 스케줄 정리
        
        return True
        
    except ImportError:
        print("X schedule 라이브러리가 설치되지 않았습니다")
        print("pip install schedule 명령어로 설치해주세요")
        return False
    except Exception as e:
        print(f"X 스케줄 테스트 실패: {e}")
        return False

if __name__ == "__main__":
    print("VDT 휴식 알리미 스케줄러 테스트")
    print("=" * 50)
    
    # 1. 설정 및 시간 로직 테스트
    config_ok = test_config_and_timing()
    
    # 2. 스케줄 라이브러리 테스트
    schedule_ok = test_schedule_library()
    
    print("\n=== 테스트 결과 요약 ===")
    print(f"설정 파일 및 시간 로직: {'통과' if config_ok else '실패'}")
    print(f"스케줄 라이브러리: {'통과' if schedule_ok else '실패'}")
    
    if config_ok and schedule_ok:
        print("\nO 모든 테스트 통과!")
        print("실제 스케줄러를 실행하려면: python notification_scheduler.py")
    else:
        print("\nX 일부 테스트 실패. 설정을 확인해주세요.")