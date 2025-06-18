import os
import json
import openai
from rapidfuzz import fuzz
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

class ComplianceEditor:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_KEY'))
        
    def read_scripts(self) -> List[Dict]:
        """Read scripts from JSON file."""
        try:
            with open('scripts.json', 'r', encoding='utf-8') as jsonfile:
                return json.load(jsonfile)
        except FileNotFoundError:
            print("scripts.json not found. Run story_writer.py first.")
            return []
    
    def check_originality(self, scripts: List[Dict]) -> List[Dict]:
        """Check originality using Levenshtein distance."""
        filtered_scripts = []
        
        for i, script in enumerate(scripts):
            is_original = True
            current_story = script['story']
            
            for j, other_script in enumerate(scripts):
                if i != j:
                    other_story = other_script['story']
                    similarity = fuzz.ratio(current_story, other_story) / 100.0
                    
                    if similarity > 0.65:  # 1 - 0.35 = 0.65
                        is_original = False
                        break
            
            if is_original:
                filtered_scripts.append(script)
            else:
                print(f"Script {i+1} filtered out due to low originality")
        
        return filtered_scripts
    
    def check_quality(self, script: Dict) -> int:
        """Check story quality using GPT and return score 0-100."""
        prompt = f"""
        Rate this story on a scale of 0-100 based on:
        1. Engagement potential (hooks the audience)
        2. Narrative structure (clear beginning, middle, end)
        3. Emotional impact
        4. Clarity and readability
        5. Appropriateness for short-form video content
        
        Story: "{script['story']}"
        
        Respond with only a number between 0-100.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a content quality evaluator for viral short-form videos."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,
                temperature=0.3
            )
            
            score_text = response.choices[0].message.content.strip()
            score = int(''.join(filter(str.isdigit, score_text)))
            return min(max(score, 0), 100)  # Clamp between 0-100
            
        except Exception as e:
            print(f"Error evaluating quality: {e}")
            return 50  # Default score if evaluation fails
    
    def moderate_content(self, script: Dict) -> bool:
        """Check if content passes moderation guidelines."""
        try:
            response = self.openai_client.moderations.create(
                input=script['story']
            )
            
            return not response.results[0].flagged
            
        except Exception as e:
            print(f"Error in moderation check: {e}")
            return True  # Default to safe if check fails
    
    def save_clean_scripts(self, scripts: List[Dict]):
        """Save clean scripts to JSON file."""
        with open('clean.json', 'w', encoding='utf-8') as jsonfile:
            json.dump(scripts, jsonfile, indent=2, ensure_ascii=False)
    
    def run(self):
        """Main execution method."""
        print("Reading scripts from JSON...")
        scripts = self.read_scripts()
        
        if not scripts:
            print("No scripts found. Exiting.")
            return
        
        print(f"Processing {len(scripts)} scripts...")
        
        print("Running moderation checks...")
        moderated_scripts = []
        for script in scripts:
            if self.moderate_content(script):
                moderated_scripts.append(script)
            else:
                print(f"Script filtered out due to moderation: {script['title'][:50]}...")
        
        print(f"{len(moderated_scripts)} scripts passed moderation")
        
        print("Checking originality...")
        original_scripts = self.check_originality(moderated_scripts)
        print(f"{len(original_scripts)} scripts passed originality check")
        
        print("Evaluating quality...")
        quality_scripts = []
        for script in original_scripts:
            quality_score = self.check_quality(script)
            script['quality_score'] = quality_score
            
            if quality_score >= 70:
                quality_scripts.append(script)
            else:
                print(f"Script filtered out due to low quality ({quality_score}): {script['title'][:50]}...")
        
        print(f"{len(quality_scripts)} scripts passed quality check")
        
        print("Saving clean scripts...")
        self.save_clean_scripts(quality_scripts)
        print(f"Compliance editing complete! {len(quality_scripts)} clean scripts saved.")

if __name__ == "__main__":
    editor = ComplianceEditor()
    editor.run()
