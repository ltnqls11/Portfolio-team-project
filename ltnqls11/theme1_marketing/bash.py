# Crawl4AI Docker 이미지 받기
docker pull unlecode/crawl4ai:basic-amd64

# 컨테이너 실행하기 (보안을 위한 API 토큰 설정)
docker run -p 11235:11235 -e CRAWL4AI_API_TOKEN=나만의_비밀토큰 unlecode/crawl4ai:latest