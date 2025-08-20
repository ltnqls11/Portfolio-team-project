#블로거 점수화 & 추천 코드

import pandas as pd
import re
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from datetime import datetime

# ✅ CSV 불러오기
df = pd.read_csv("lipstick_blogs.csv")

# ✅ 최신성 점수 (최근일수 → 점수화)
today = datetime.today()
df["days_since"] = df["postdate"].apply(lambda x: (today - datetime.strptime(str(x), "%Y%m%d")).days)
scaler = MinMaxScaler()
df["recency_score"] = 1 - scaler.fit_transform(df[["days_since"]])  # 최신 글일수록 점수 ↑

# ✅ 참여율 점수 (likes+comments)
df["engagement"] = df["likes"] + df["comments"]
df["engagement_score"] = scaler.fit_transform(df[["engagement"]])

# ✅ 카테고리 적합도 (제목 키워드 포함 여부)
keywords = ["립스틱", "립", "화장품", "메이크업"]
def category_score(title):
    title = re.sub(r"<.*?>", "", str(title))  # HTML 태그 제거
    return 1 if any(k in title for k in keywords) else 0.5  # 키워드 없으면 낮게
df["category_score"] = df["title"].apply(category_score)

# ✅ 최종 점수 (가중치 합산)
df["final_score"] = (
    df["recency_score"] * 0.3 +
    df["engagement_score"] * 0.4 +
    df["category_score"] * 0.3
) * 100

# ✅ 상위 블로거 추천 (TOP 5)
top_blogs = df.sort_values("final_score", ascending=False).head(5)
print(top_blogs[["title", "blogger", "link", "likes", "comments", "postdate", "final_score"]])

# ✅ CSV 저장
top_blogs.to_csv("lipstick_top_blogs.csv", index=False, encoding="utf-8-sig")
print("✅ lipstick_top_blogs.csv 파일로 저장 완료!")
