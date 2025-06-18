.PHONY: shorts daily compile clean setup

# Default Python and Node commands
PYTHON := python3
NODE := node
NPM := npm

# Directories
AGENTS_DIR := agents
VISUALIZER_DIR := visualizer
AUDIO_DIR := audio
OUT_DIR := out

setup:
	@echo "Setting up environment..."
	$(PYTHON) -m pip install -r requirements.txt
	cd $(VISUALIZER_DIR) && $(NPM) install

short: setup
	@echo "Generating a single short video..."
	@mkdir -p $(AUDIO_DIR) $(OUT_DIR)
	$(PYTHON) $(AGENTS_DIR)/trend_scout.py
	$(PYTHON) $(AGENTS_DIR)/story_writer.py 1
	$(PYTHON) $(AGENTS_DIR)/compliance_editor.py
	$(PYTHON) $(AGENTS_DIR)/narrator.py
	@echo "Rendering video..."
	@STORY_TEXT=$$(cat clean.json | jq -r '.[0].story // "Default story"' 2>/dev/null || echo "Default story"); \
	AUDIO_FILE=$$(cat clean.json | jq -r '.[0].audio_file // "default.wav"' 2>/dev/null || echo "default.wav"); \
	npx remotion render visualizer/src/index.ts StoryVideo $(OUT_DIR)/short_$$(date +%s).mp4 --codec=h264 --props="{\"storyText\":\"$$STORY_TEXT\", \"audioFile\":\"$$AUDIO_FILE\"}"
	@echo "Short video generation complete!"

shorts: short

daily: setup
	@echo "Generating 10 short videos for daily upload..."
	@mkdir -p $(AUDIO_DIR) $(OUT_DIR)
	@for i in $$(seq 1 10); do \
		echo "Generating video $$i/10..."; \
		make short; \
		sleep 2; \
	done
	@echo "Daily video generation complete! Generated 10 videos."

test: setup
	@echo "Generating single test video (30 seconds)..."
	@mkdir -p $(AUDIO_DIR) $(OUT_DIR)
	$(PYTHON) $(AGENTS_DIR)/trend_scout.py
	$(PYTHON) $(AGENTS_DIR)/story_writer.py 1
	$(PYTHON) $(AGENTS_DIR)/compliance_editor.py
	$(PYTHON) $(AGENTS_DIR)/narrator.py
	@echo "Rendering test video..."
	@STORY_TEXT=$$(cat clean.json | jq -r '.[0].story // "Test story"' 2>/dev/null || echo "Test story"); \
	AUDIO_FILE=$$(cat clean.json | jq -r '.[0].audio_file // "default.wav"' 2>/dev/null || echo "default.wav"); \
	npx remotion render visualizer/src/index.ts StoryVideo $(OUT_DIR)/test_video.mp4 --codec=h264 --frames=450 --props="{\"storyText\":\"$$STORY_TEXT\", \"audioFile\":\"$$AUDIO_FILE\"}"
	@echo "Test video generation complete!"

compile:
	@echo "Creating compilation from latest 30 videos..."
	@mkdir -p $(OUT_DIR)
	@ls -t $(OUT_DIR)/*.mp4 | head -30 > /tmp/video_list.txt
	@if [ -s /tmp/video_list.txt ]; then \
		echo "Concatenating videos..."; \
		sed 's/^/file /' /tmp/video_list.txt > /tmp/ffmpeg_list.txt; \
		ffmpeg -f concat -safe 0 -i /tmp/ffmpeg_list.txt -c copy $(OUT_DIR)/compilation_$$(date +%s).mp4; \
		echo "Compilation complete!"; \
	else \
		echo "No videos found for compilation."; \
	fi

clean:
	@echo "Cleaning up generated files..."
	rm -f hooks.csv scripts.json clean.json
	rm -rf $(AUDIO_DIR)/* $(OUT_DIR)/*
	@echo "Cleanup complete!"

help:
	@echo "Available targets:"
	@echo "  short    - Generate a single short video"
	@echo "  shorts   - Alias for short"
	@echo "  daily    - Generate 10 videos for daily upload"
	@echo "  test     - Generate single test video (30 seconds)"
	@echo "  compile  - Create compilation from latest 30 videos"
	@echo "  clean    - Clean up generated files"
	@echo "  setup    - Install dependencies"
