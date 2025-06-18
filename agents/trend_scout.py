#!/usr/bin/env python3
"""
Trend-Scout
-----------
Fetch Reddit hooks and rank them for drama / engagement.

CLI flags
---------
--limit    N   Number of posts per subreddit (default 50)
--fallback     If Reddit auth fails, write one mock hook so the
               rest of the pipeline can run.

Examples
--------
# production (150 posts total)
python agents/trend_scout.py

# quick test (1 post total) – never crashes, even with bad creds
python agents/trend_scout.py --limit 1 --fallback
"""
import argparse, csv, os, sys
from typing import List, Dict

import numpy as np
import praw
import prawcore
import openai
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────── utils ────────────────────────────────
def cosine_similarity(a: List[float], b: List[float]) -> float:
    a_np = np.array(a)
    b_np = np.array(b)
    return float(np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np)))


def get_embedding(client: openai.OpenAI, text: str) -> List[float]:
    rsp = client.embeddings.create(model="text-embedding-3-small", input=text)
    return rsp.data[0].embedding


# ─────────────────────────────── main class ───────────────────────────
class TrendScout:
    SUBREDDITS = ["tifu", "confession", "aita"]

    def __init__(self, posts_per_sub: int = 50, allow_fallback: bool = False):
        self.posts_per_sub = posts_per_sub
        self.allow_fallback = allow_fallback

        missing = [
            k
            for k in (
                "REDDIT_CLIENT_ID",
                "REDDIT_SECRET",
                "REDDIT_USER_AGENT",
            )
            if not os.getenv(k)
        ]
        if missing:
            print(
                f"⚠️  Missing Reddit env vars: {', '.join(missing)}", file=sys.stderr
            )

        try:
            self.reddit = praw.Reddit(
                client_id=os.getenv("REDDIT_CLIENT_ID"),
                client_secret=os.getenv("REDDIT_SECRET"),
                user_agent=os.getenv("REDDIT_USER_AGENT"),
                username=os.getenv("REDDIT_USERNAME"),
                password=os.getenv("REDDIT_PASSWORD"),
                check_for_async=False,
            )
        except Exception:
            self.reddit = None

        openai_key = os.getenv("OPENAI_KEY")
        if openai_key:
            try:
                self.openai_client = openai.OpenAI(api_key=openai_key)
            except Exception:
                self.openai_client = None
        else:
            self.openai_client = None

    # ──────────────────────────────────────────────────────────────────
    def fetch_posts(self) -> List[Dict]:
        posts: List[Dict] = []
        try:
            if self.reddit is None:
                raise prawcore.exceptions.Forbidden()
            for sub in self.SUBREDDITS:
                for p in (
                    self.reddit.subreddit(sub)
                    .hot(limit=self.posts_per_sub)
                ):
                    if not p.stickied and len(p.title) > 10:
                        posts.append(
                            {
                                "title": p.title,
                                "subreddit": sub,
                                "score": p.score,
                                "url": p.url,
                                "id": p.id,
                            }
                        )
        except Exception:
            if self.allow_fallback:
                print(
                    "⚠️  Reddit auth failed – using built-in mock hook instead.",
                    file=sys.stderr,
                )
                posts = [
                    {
                        "title": "TIFU by oversharing at Thanksgiving dinner",
                        "subreddit": "tifu",
                        "score": 999,
                        "url": "https://reddit.com/mock",
                        "id": "mock123",
                    }
                ]
            else:
                raise RuntimeError(
                    "Reddit authentication failed.\n"
                    "Check REDDIT_* env vars or run with --fallback."
                )
        return posts

    # ──────────────────────────────────────────────────────────────────
    def rank(self, raw: List[Dict]) -> List[Dict]:
        seed = (
            "shocking twist unexpected ending dramatic reveal "
            "personal story emotional journey life changing moment"
        )
        if self.openai_client is None:
            return raw
        seed_vec = get_embedding(self.openai_client, seed)

        for post in raw:
            v = get_embedding(self.openai_client, post["title"])
            post["engagement_score"] = cosine_similarity(v, seed_vec)

        return sorted(raw, key=lambda x: x["engagement_score"], reverse=True)

    # ──────────────────────────────────────────────────────────────────
    @staticmethod
    def save_csv(rows: List[Dict], fname: str = "hooks.csv") -> None:
        with open(fname, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "title",
                    "subreddit",
                    "score",
                    "url",
                    "id",
                    "engagement_score",
                ],
            )
            writer.writeheader()
            writer.writerows(rows)

    # ──────────────────────────────────────────────────────────────────
    def run(self) -> None:
        print("Fetching Reddit posts…")
        raw = self.fetch_posts()
        print(f"Fetched {len(raw)} posts")

        print("Scoring for engagement…")
        top = self.rank(raw)[:50]
        print(f"Top {len(top)} selected")

        self.save_csv(top)
        print("✅ trend_scout wrote hooks.csv")


# ──────────────────────────── CLI entry ───────────────────────────────
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=50, help="posts per subreddit")
    ap.add_argument(
        "--fallback",
        action="store_true",
        help="use mock hook if Reddit auth fails",
    )
    args = ap.parse_args()

    TrendScout(posts_per_sub=args.limit, allow_fallback=args.fallback).run()
