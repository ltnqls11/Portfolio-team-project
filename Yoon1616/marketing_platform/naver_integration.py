from typing import List, Dict
import pandas as pd
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler
import re

from .naver_crawling import collect_blogger_candidates


def _clean_html(text: str) -> str:
    return re.sub(r"<.*?>", "", str(text or ""))


def recommend_bloggers_with_naver(query: str, total: int = 50) -> pd.DataFrame:
    """
    네이버 API + 간단 점수화로 추천 상위 목록 반환
    columns: [title, blogger, link, postdate, likes, comments, engagement, recency_score, engagement_score, category_score, final_score]
    """
    rows: List[Dict] = collect_blogger_candidates(query=query, total=total)
    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    # 최신성 점수
    try:
        today = datetime.today()
        df["days_since"] = df["postdate"].apply(lambda x: (today - datetime.strptime(str(x), "%Y%m%d")).days)
    except Exception:
        df["days_since"] = df.get("postdate").astype(str).apply(lambda _: 180)

    scaler = MinMaxScaler()
    df["recency_score"] = 1 - scaler.fit_transform(df[["days_since"]])

    # 참여 스코어
    if "engagement" not in df:
        df["engagement"] = (df.get("likes", 0) or 0) + (df.get("comments", 0) or 0)
    df["engagement_score"] = scaler.fit_transform(df[["engagement"]])

    # 카테고리/키워드 적합도: 쿼리 키워드 포함 여부
    q_tokens = [t.strip() for t in re.split(r"[,\s]+", query) if t.strip()]
    def category_score(title: str) -> float:
        title = _clean_html(title)
        return 1.0 if any(t in title for t in q_tokens) else 0.6
    df["category_score"] = df["title"].apply(category_score)

    df["final_score"] = (
        df["recency_score"] * 0.3 +
        df["engagement_score"] * 0.5 +
        df["category_score"] * 0.2
    ) * 100

    df = df.sort_values("final_score", ascending=False).reset_index(drop=True)
    return df

