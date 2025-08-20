#두개 합친거

import requests
from bs4 import BeautifulSoup
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime
import re
import time

# ----------------------
# 1️⃣ 후보 블로그 리스트 (API, 유사도순)
# ----------------------
client_id = ""
client_secret = ""
query = "립스틱 후기"
url = "https://openapi.naver.com/v1/search/blog.json"
headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}

blogs = []
for start in range(1, 51, 10):
    params = {"query": query, "display": 10, "start": start, "sort": "sim"}
    res = requests.get(url, headers=headers, params=params)
    if res.status_code != 200:
        print("API 호출 실패:", res.status_code)
        continue
    data = res.json()
    for item in data.get('items', []):
        blogs.append({
            "title": re.sub(r"<.*?>", "", item.get('title', '')),
            "link": item.get('link', ''),
            "blogger": item.get('bloggername', ''),
            "postdate": item.get('postdate', ''),
            "description": re.sub(r"<.*?>", "", item.get('description', ''))
        })
    time.sleep(0.3)

# ----------------------
# 2️⃣ 공감·댓글·본문 키워드
# ----------------------
keywords = ["립스틱", "후기", "리뷰", "발색", "매트", "촉촉", "컬러", "지속력", "발림성"]

def _only_digits(s: str) -> int:
    s = (s or "").strip()
    digits = "".join(ch for ch in s if ch.isdigit())
    return int(digits) if digits else 0

def get_metrics_and_keyword_hits(link, fallback_text):
    try:
        res = requests.get(link, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        if res.status_code != 200:
            return 0, 0, 0
        soup = BeautifulSoup(res.text, "html.parser")
        likes_el = soup.select_one(".u_likeit_list_count._count")
        comments_el = soup.select_one(".u_likeit_list_count._count + span")
        likes = _only_digits(likes_el.text if likes_el else "0")
        comments = _only_digits(comments_el.text if comments_el else "0")
        content = soup.get_text(" ")
        content = content if content.strip() else fallback_text
        content = re.sub(r"\s+", " ", content)

        keyword_hits = sum(len(re.findall(re.escape(k), content)) for k in keywords)

        return likes, comments, keyword_hits
    except:
        return 0, 0, 0

for blog in blogs:
    likes, comments, keyword_hits = get_metrics_and_keyword_hits(blog["link"], blog["description"])
    blog["likes"] = likes
    blog["comments"] = comments
    blog["keyword_hits"] = keyword_hits
    time.sleep(0.3)

# ----------------------
# 3️⃣ 점수 계산
# ----------------------
df = pd.DataFrame(blogs).copy().reset_index(drop=True)

# 최신성 점수
today = datetime.today()
df["days_since"] = df["postdate"].apply(lambda x: (today - datetime.strptime(str(x), "%Y%m%d")).days if x else 365)
if len(df) > 1:
    df["recency_score"] = 1 - MinMaxScaler().fit_transform(df[["days_since"]])
else:
    df["recency_score"] = 1.0

# 참여율 점수
df["engagement"] = df["likes"] + df["comments"]
if len(df) > 1:
    df["engagement_score"] = MinMaxScaler().fit_transform(df[["engagement"]])
else:
    df["engagement_score"] = 1.0

# 키워드 점수
if len(df) > 1:
    df["keyword_score"] = MinMaxScaler().fit_transform(df[["keyword_hits"]])
else:
    df["keyword_score"] = 1.0

# 최종 점수
df["final_score"] = (df["recency_score"]*0.3 + df["engagement_score"]*0.4 + df["keyword_score"]*0.3)*100

# ----------------------
# 4️⃣ 추천 TOP 5
# ----------------------
top_blogs = df.sort_values("final_score", ascending=False).head(5)

print("\n[1단계] API 후보 수: ", len(blogs))
print("[2단계] 필터 후 수: ", len(df))
print("[3단계] 상위 5개(점수화 결과):")
print(top_blogs[["title", "blogger", "link", "likes", "comments", "keyword_hits", "final_score"]])

top_blogs.to_csv("top_lipstick_blogs_filtered.csv", index=False, encoding="utf-8-sig")
print("✅ top_lipstick_blogs_filtered.csv 저장 완료!")
