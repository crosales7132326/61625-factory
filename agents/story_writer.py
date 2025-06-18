import os
import csv
import json
import openai
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

class StoryWriter:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_KEY'))
        
    def read_hooks(self, limit: int = 10) -> List[Dict]:
        """Read hooks from CSV file."""
        hooks = []
        try:
            with open('hooks.csv', 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for i, row in enumerate(reader):
                    if i >= limit:
                        break
                    hooks.append(row)
        except FileNotFoundError:
            print("hooks.csv not found. Run trend_scout.py first.")
            return []
        return hooks
    
    def generate_story(self, hook: Dict) -> str:
        """Generate a 160-word first-person story with cold-open and twist."""
        prompt = f"""
        Based on this Reddit post title: "{hook['title']}"
        
        Write a compelling 160-word first-person story that:
        1. Starts with a cold open (jump right into action/drama)
        2. Builds tension throughout
        3. Has an unexpected twist or revelation
        4. Uses simple, conversational language
        5. Is suitable for a 60-second video
        
        The story should be engaging, relatable, and have emotional impact.
        Write in first person ("I", "me", "my").
        
        Story:
        """
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a master storyteller who creates viral short-form content."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.8
        )
        
        return response.choices[0].message.content.strip()
    
    def save_scripts(self, scripts: List[Dict]):
        """Save generated scripts to JSON file."""
        with open('scripts.json', 'w', encoding='utf-8') as jsonfile:
            json.dump(scripts, jsonfile, indent=2, ensure_ascii=False)
    
    def run(self):
        """Main execution method."""
        print("Reading hooks from CSV...")
        hooks = self.read_hooks(10)
        
        if not hooks:
            print("No hooks found. Exiting.")
            return
        
        scripts = []
        print(f"Generating stories for {len(hooks)} hooks...")
        
        for i, hook in enumerate(hooks):
            print(f"Generating story {i+1}/{len(hooks)}...")
            try:
                story = self.generate_story(hook)
                script = {
                    'id': hook['id'],
                    'title': hook['title'],
                    'subreddit': hook['subreddit'],
                    'story': story,
                    'word_count': len(story.split()),
                    'engagement_score': float(hook['engagement_score'])
                }
                scripts.append(script)
            except Exception as e:
                print(f"Error generating story for hook {i+1}: {e}")
                continue
        
        print("Saving scripts to JSON...")
        self.save_scripts(scripts)
        print(f"Story writing complete! Generated {len(scripts)} scripts.")

if __name__ == "__main__":
    writer = StoryWriter()
    writer.run()
