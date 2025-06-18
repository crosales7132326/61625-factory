# Reddit Micro-Story → Shorts & Compilation Video Factory

Fully-automated system that creates YouTube Shorts from Reddit stories and compiles them into longer videos.

## Prerequisites

- Python 3.12
- Node.js 20
- ffmpeg
- GitHub repository secrets configured

## Quick Start

1. Clone the repository and set up environment:
```bash
git clone https://github.com/crosales7132326/61625-factory.git
cd 61625-factory
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
npm ci
make assets
```

2. Copy environment template and fill in your API keys:
```bash
cp .env.template .env
# Edit .env with your actual API keys
```

3. Run a single short video generation:
```bash
make shorts
```

4. Generate 10 videos for daily upload:
```bash
make daily
```

5. Create a compilation from recent videos:
```bash
make compile
```

## GitHub Secrets Setup

Add the following secrets in your repository Settings › Secrets and variables › Actions › New repository secret:

- `OPENAI_KEY` - Your OpenAI API key
- `REDDIT_CLIENT_ID` - Reddit app client ID
- `REDDIT_SECRET` - Reddit app secret
- `E11_KEY` - ElevenLabs API key
- `PEXELS_KEY` - Pexels API key

## Automation

The system runs automatically via GitHub Actions:
- Daily at 04:00 UTC: Generates 10 new short videos
- Sundays at 03:00 UTC: Creates compilation from latest 30 videos

## Quick Testing

To run a quick test that generates a single short video (about 60 seconds):

1. Go to Actions tab in GitHub
2. Select "Quick Test" workflow
3. Click "Run workflow"
4. Download the test video from artifacts after completion

Or run locally:
```bash
make test
```

The quick test generates one video in under 5 minutes and uploads it as a test artifact with 3-day retention.
