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

shorts: setup
	@echo "Generating a single short video..."
	@mkdir -p $(AUDIO_DIR) $(OUT_DIR)
	$(PYTHON) $(AGENTS_DIR)/trend_scout.py
	$(PYTHON) $(AGENTS_DIR)/story_writer.py
	$(PYTHON) $(AGENTS_DIR)/compliance_editor.py
	$(PYTHON) $(AGENTS_DIR)/narrator.py
	@echo "Rendering video..."
	cd $(VISUALIZER_DIR) && npx remotion render src/index.ts StoryVideo ../$(OUT_DIR)/short_$$(date +%s).mp4 --props='{"storyText":"Generated story will be here","audioFile":"generated_audio.wav"}'
	@echo "Short video generation complete!"

daily: setup
	@echo "Generating 10 short videos for daily upload..."
	@mkdir -p $(AUDIO_DIR) $(OUT_DIR)
	@for i in $$(seq 1 10); do \
		echo "Generating video $$i/10..."; \
		$(PYTHON) $(AGENTS_DIR)/trend_scout.py; \
		$(PYTHON) $(AGENTS_DIR)/story_writer.py; \
		$(PYTHON) $(AGENTS_DIR)/compliance_editor.py; \
		$(PYTHON) $(AGENTS_DIR)/narrator.py; \
		cd $(VISUALIZER_DIR) && npx remotion render src/index.ts StoryVideo ../$(OUT_DIR)/daily_$$(date +%s)_$$i.mp4 --props='{"storyText":"Generated story $$i","audioFile":"generated_audio.wav"}' && cd ..; \
		sleep 2; \
	done
	@echo "Daily video generation complete! Generated 10 videos."

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
	@echo "  shorts   - Generate a single short video"
	@echo "  daily    - Generate 10 videos for daily upload"
	@echo "  compile  - Create compilation from latest 30 videos"
	@echo "  clean    - Clean up generated files"
	@echo "  setup    - Install dependencies"
