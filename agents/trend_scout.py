import os
import csv
import praw
import openai
import numpy as np
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

class TrendScout:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT')
        )
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_KEY'))
        self.subreddits = ["tifu", "confession", "aita"]
        
    def get_embedding(self, text: str) -> List[float]:
        """Get text embedding using OpenAI."""
        response = self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    
    def cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        a_np = np.array(a)
        b_np = np.array(b)
        return np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np))
    
    def fetch_posts(self) -> List[Dict]:
        """Fetch top 150 posts from specified subreddits."""
        posts = []
        posts_per_sub = 50  # 150 total / 3 subs
        
        for sub_name in self.subreddits:
            subreddit = self.reddit.subreddit(sub_name)
            for post in subreddit.hot(limit=posts_per_sub):
                if not post.stickied and len(post.title) > 10:
                    posts.append({
                        'title': post.title,
                        'subreddit': sub_name,
                        'score': post.score,
                        'url': post.url,
                        'id': post.id
                    })
        
        return posts
    
    def rank_by_engagement_potential(self, posts: List[Dict]) -> List[Dict]:
        """Rank posts by their potential for viral engagement."""
        seed_text = "shocking twist unexpected ending dramatic reveal personal story emotional journey life changing moment"
        seed_vector = self.get_embedding(seed_text)
        
        for post in posts:
            title_vector = self.get_embedding(post['title'])
            similarity = self.cosine_similarity(title_vector, seed_vector)
            post['engagement_score'] = similarity
        
        posts.sort(key=lambda x: x['engagement_score'], reverse=True)
        return posts[:50]  # Top 50
    
    def save_hooks(self, posts: List[Dict]):
        """Save top hooks to CSV file."""
        with open('hooks.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['title', 'subreddit', 'score', 'url', 'id', 'engagement_score']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(posts)
    
    def run(self):
        """Main execution method."""
        print("Fetching posts from Reddit...")
        posts = self.fetch_posts()
        print(f"Fetched {len(posts)} posts")
        
        print("Ranking posts by engagement potential...")
        top_posts = self.rank_by_engagement_potential(posts)
        print(f"Selected top {len(top_posts)} posts")
        
        print("Saving hooks to CSV...")
        self.save_hooks(top_posts)
        print("Trend scouting complete!")

if __name__ == "__main__":
    scout = TrendScout()
    scout.run()
