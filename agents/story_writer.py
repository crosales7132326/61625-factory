#!/usr/bin/env python3
"""
Story-Writer
------------
Turn hooks.csv rows into short first-person scripts.

CLI flags
---------
--limit N      Generate at most N stories (default 10)
--fallback     If OpenAI call fails, write a single hard-coded story so the
               pipeline can continue.

Example
-------
python agents/story_writer.py --limit 1 --fallback
"""
from __future__ import annotations

import argparse, csv, json, os, sys
from typing import List, Dict

import openai
from dotenv import load_dotenv

load_dotenv()


# ─────────────────────────────── utils ────────────────────────────────
def call_openai(prompt: str) -> str:
    client = openai.OpenAI(api_key=os.getenv("OPENAI_KEY"))
    rsp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a master storyteller who creates viral short-form content."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=200,
        temperature=0.8,
    )
    return rsp.choices[0].message.content.strip()


# ─────────────────────────────── main class ───────────────────────────
class StoryWriter:
    def __init__(self, limit: int = 10, allow_fallback: bool = True):
        self.limit = limit
        self.allow_fallback = allow_fallback

    # ------------------------------------------------------------------
    @staticmethod
    def read_hooks(limit: int) -> List[Dict]:
        hooks: List[Dict] = []
        try:
            with open("hooks.csv", newline="", encoding="utf-8") as f:
                for i, row in enumerate(csv.DictReader(f)):
                    if i >= limit:
                        break
                    hooks.append(row)
        except FileNotFoundError:
            print("hooks.csv not found. Run trend_scout.py first.")
        return hooks

    # ------------------------------------------------------------------
    def generate_story(self, hook: Dict) -> str:
        prompt = f"""
Based on this Reddit post title: "{hook['title']}"

Write a compelling 160-word first-person story that:
1. Starts with a cold open (jump right into action/drama)
2. Builds tension throughout
3. Has an unexpected twist or revelation
4. Uses simple, conversational language
5. Is suitable for a 60-second video

Story (first person):
"""
        try:
            return call_openai(prompt)
        except Exception as e:
            if self.allow_fallback:
                print(f"⚠️  OpenAI failed ({e!s}); using fallback story.")
                return (
                    "I shouldn’t have opened my mouth at Thanksgiving. "
                    "The room went silent when I blurted the secret. "
                    "Little did I know Grandma already knew—and planned the twist."
                )
            raise

    # ------------------------------------------------------------------
    def save_scripts(self, scripts: List[Dict], fname: str = "scripts.json") -> None:
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(scripts, f, indent=2, ensure_ascii=False)

    # ------------------------------------------------------------------
    def run(self) -> None:
        hooks = self.read_hooks(self.limit)
        if not hooks:
            print("No hooks found. Exiting.")
            return

        scripts: List[Dict] = []
        print(f"Generating stories for {len(hooks)} hooks…")
        for idx, hook in enumerate(hooks, 1):
            print(f"  • story {idx}/{len(hooks)}")
            story = self.generate_story(hook)
            scripts.append(
                {
                    "id": hook["id"],
                    "title": hook["title"],
                    "subreddit": hook["subreddit"],
                    "story": story,
                    "word_count": len(story.split()),
                    "engagement_score": float(hook["engagement_score"]),
                }
            )

        self.save_scripts(scripts)
        print(f"✅ story_writer wrote scripts.json with {len(scripts)} script(s)")


# ──────────────────────────── CLI entry ───────────────────────────────
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=10, help="max number of hooks to process")
    ap.add_argument(
        "--fallback",
        action="store_true",
        help="write a dummy story if OpenAI is unreachable",
    )
    args = ap.parse_args()

    StoryWriter(limit=args.limit, allow_fallback=args.fallback).run()
