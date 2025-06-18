import os
import json
import csv
import pytest
from unittest.mock import patch, MagicMock

def test_hooks_csv_creation():
    """Test that hooks.csv is created and non-empty after trend_scout runs."""
    with patch('praw.Reddit') as mock_reddit, \
         patch('openai.OpenAI') as mock_openai:
        
        mock_post = MagicMock()
        mock_post.title = "Test story title"
        mock_post.subreddit.display_name = "tifu"
        mock_post.score = 100
        mock_post.url = "https://reddit.com/test"
        mock_post.id = "test123"
        mock_post.stickied = False
        
        mock_subreddit = MagicMock()
        mock_subreddit.hot.return_value = [mock_post] * 10
        mock_reddit.return_value.subreddit.return_value = mock_subreddit
        
        mock_embedding_response = MagicMock()
        mock_embedding_response.data = [MagicMock()]
        mock_embedding_response.data[0].embedding = [0.1] * 1536
        mock_openai.return_value.embeddings.create.return_value = mock_embedding_response
        
        from agents.trend_scout import TrendScout
        scout = TrendScout()
        scout.run()
        
        assert os.path.exists('hooks.csv'), "hooks.csv should be created"
        
        with open('hooks.csv', 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            assert len(rows) > 1, "hooks.csv should contain data beyond header"

def test_scripts_json_creation():
    """Test that scripts.json is created and non-empty after story_writer runs."""
    test_hooks = [
        {
            'title': 'Test story hook',
            'subreddit': 'tifu',
            'score': '100',
            'url': 'https://test.com',
            'id': 'test123',
            'engagement_score': '0.8'
        }
    ]
    
    with open('hooks.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=test_hooks[0].keys())
        writer.writeheader()
        writer.writerows(test_hooks)
    
    with patch('openai.OpenAI') as mock_openai:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "This is a test story with exactly the right length and content for testing purposes."
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        from agents.story_writer import StoryWriter
        writer = StoryWriter()
        writer.run()
        
        assert os.path.exists('scripts.json'), "scripts.json should be created"
        
        with open('scripts.json', 'r') as f:
            scripts = json.load(f)
            assert len(scripts) > 0, "scripts.json should contain generated scripts"
            assert 'story' in scripts[0], "Each script should have a story field"

def test_clean_json_creation():
    """Test that clean.json is created and non-empty after compliance_editor runs."""
    test_scripts = [
        {
            'id': 'test123',
            'title': 'Test story',
            'subreddit': 'tifu',
            'story': 'This is a unique test story that should pass all compliance checks.',
            'word_count': 12,
            'engagement_score': 0.8
        },
        {
            'id': 'test456',
            'title': 'Another test story',
            'subreddit': 'confession',
            'story': 'This is a completely different story with unique content and good quality.',
            'word_count': 13,
            'engagement_score': 0.7
        }
    ]
    
    with open('scripts.json', 'w') as f:
        json.dump(test_scripts, f)
    
    with patch('openai.OpenAI') as mock_openai:
        mock_moderation = MagicMock()
        mock_moderation.results = [MagicMock()]
        mock_moderation.results[0].flagged = False
        
        mock_quality = MagicMock()
        mock_quality.choices = [MagicMock()]
        mock_quality.choices[0].message.content = "85"
        
        mock_client = mock_openai.return_value
        mock_client.moderations.create.return_value = mock_moderation
        mock_client.chat.completions.create.return_value = mock_quality
        
        from agents.compliance_editor import ComplianceEditor
        editor = ComplianceEditor()
        editor.run()
        
        assert os.path.exists('clean.json'), "clean.json should be created"
        
        with open('clean.json', 'r') as f:
            clean_scripts = json.load(f)
            assert len(clean_scripts) > 0, "clean.json should contain clean scripts"
            assert 'quality_score' in clean_scripts[0], "Each clean script should have a quality score"

def test_file_cleanup():
    """Clean up test files after tests."""
    test_files = ['hooks.csv', 'scripts.json', 'clean.json']
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
