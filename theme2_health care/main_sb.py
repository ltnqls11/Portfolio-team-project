# 1. 원하는 폴더로 이동 (예: Documents)
cd $env:USERPROFILE\Documents

# 2. Git으로 cursor-credits 저장소 클론
git clone https://github.com/CaptainCodeAU/cursor-credits.git

# 3. 내려받은 폴더로 이동
cd cursor-credits

# 4. 필요한 패키지 설치
python -m pip install requests

# 5. main.py 실행
python main.py
