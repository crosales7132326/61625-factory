import os
import json
import time
import requests
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

class Narrator:
    def __init__(self):
        self.api_key = os.getenv('E11_KEY')
        self.voice_id = os.getenv('E11_VOICE', 'EXAVITQu4vr4xnSDxMaL')
        if not self.voice_id:
            raise ValueError("E11_VOICE is not set")
        self.base_url = "https://api.elevenlabs.io/v1"
        
    def read_clean_scripts(self) -> List[Dict]:
        """Read clean scripts from JSON file."""
        try:
            with open('clean.json', 'r', encoding='utf-8') as jsonfile:
                return json.load(jsonfile)
        except FileNotFoundError:
            print("clean.json not found. Run compliance_editor.py first.")
            return []
    
    def generate_audio(self, text: str, filename: str, max_retries: int = 3) -> bool:
        """Generate audio using ElevenLabs TTS with retry logic."""
        url = f"{self.base_url}/text-to-speech/{self.voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.post(url, json=data, headers=headers)
                
                if response.status_code == 200:
                    audio_path = os.path.join('audio', filename)
                    with open(audio_path, 'wb') as f:
                        f.write(response.content)
                    print(f"Audio saved: {audio_path}")
                    return True
                    
                elif response.status_code == 429:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"Rate limit hit. Waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}")
                    time.sleep(wait_time)
                    continue
                    
                else:
                    print(f"Error generating audio: {response.status_code} - {response.text}")
                    return False
                    
            except Exception as e:
                print(f"Exception during audio generation (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                return False
        
        print(f"Failed to generate audio after {max_retries} attempts")
        return False
    
    def run(self):
        """Main execution method."""
        print("Reading clean scripts...")
        scripts = self.read_clean_scripts()
        
        if not scripts:
            print("No clean scripts found. Exiting.")
            return
        
        os.makedirs('audio', exist_ok=True)
        
        print(f"Generating audio for {len(scripts)} scripts...")
        successful_count = 0
        
        for i, script in enumerate(scripts):
            print(f"Generating audio {i+1}/{len(scripts)} for: {script['title'][:50]}...")
            
            filename = f"{script['id']}.wav"
            
            if self.generate_audio(script['story'], filename):
                successful_count += 1
                script['audio_file'] = filename
            else:
                print(f"Failed to generate audio for script: {script['title'][:50]}...")
        
        if successful_count > 0:
            with open('clean.json', 'w', encoding='utf-8') as jsonfile:
                json.dump(scripts, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"Narration complete! Generated {successful_count}/{len(scripts)} audio files.")

if __name__ == "__main__":
    narrator = Narrator()
    narrator.run()
