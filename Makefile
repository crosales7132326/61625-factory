.PHONY: short shorts daily test compile clean setup help

# Commands
PYTHON := python3
NPM    := npm
NODE   := node

# Directories
VISUALIZER_DIR := visualizer
AUDIO_DIR      := audio
OUT_DIR        := out

# ---------------------------------------------------------------------
setup:
	@echo "🔧 Setting up environment..."
	$(PYTHON) -m pip install -r requirements.txt
	cd $(VISUALIZER_DIR) && $(NPM) ci

# ---------------------------------------------------------------------
short: ## one narrated 60-sec Short (prod settings)
	@echo "🎬 Generating a single short video..."
	@mkdir -p $(AUDIO_DIR) $(OUT_DIR)

	# 1 hook  →  1 script → 1 WAV
	$(PYTHON) agents/trend_scout.py   --limit 1
	$(PYTHON) agents/story_writer.py  --limit 1
	$(PYTHON) agents/compliance_editor.py
	$(PYTHON) agents/narrator.py      --limit 1

	# Render full-length 60-sec video
	@echo "🖥️  Rendering video..."
	@STORY_TEXT=$$(jq -r '.[0].story'  clean.json); \
	AUDIO_FILE=$$(jq -r '.[0].audio_file' clean.json); \
	npx remotion render visualizer/src/index.ts StoryVideo \
	      $(OUT_DIR)/short_$$(date +%s).mp4 \
	      --codec=h264 \
	      --props="{\"storyText\":\"$$STORY_TEXT\",\"audioFile\":\"$$AUDIO_FILE\"}"

	@echo "✅ Short video generation complete!"

shorts: short             ## alias

# ---------------------------------------------------------------------
daily: setup              ## loop “short” 10× (prod)
	@echo "📅 Generating 10 short videos for daily upload..."
	@for i in $$(seq 1 10); do \
	    echo "------------ Video $$i/10 ------------"; \
	    $(MAKE) --no-print-directory short; \
	    sleep 1; \
	done
	@echo "🏁 Daily generation complete!"

# ---------------------------------------------------------------------
test: setup               ## one 30-sec quick-test with fallbacks
	@echo "🧪 Generating single test video (30 sec)…"
	@mkdir -p $(AUDIO_DIR) $(OUT_DIR)

	$(PYTHON) agents/trend_scout.py   --limit 1 --fallback
	$(PYTHON) agents/story_writer.py  --limit 1 --fallback
	$(PYTHON) agents/compliance_editor.py
	$(PYTHON) agents/narrator.py      --limit 1 --fallback

	@echo "🖥️  Rendering 30-sec test video..."
	@STORY_TEXT=$$(jq -r '.[0].story'  clean.json); \
	AUDIO_FILE=$$(jq -r '.[0].audio_file' clean.json); \
	npx remotion render visualizer/src/index.ts StoryVideo \
	      $(OUT_DIR)/test_video.mp4 \
	      --codec=h264 \
	      --frames=0-899 \
	      --props="{\"storyText\":\"$$STORY_TEXT\",\"audioFile\":\"$$AUDIO_FILE\"}"

	@echo "✅ Test video ready!"

# ---------------------------------------------------------------------
compile: ## concat latest 30 MP4s into one compilation
	@echo "📼 Creating compilation..."
	@ls -t $(OUT_DIR)/*.mp4 | head -30 > /tmp/video_list.txt || true
	@if [ -s /tmp/video_list.txt ]; then \
	    sed 's/^/file /' /tmp/video_list.txt > /tmp/ffmpeg_list.txt; \
	    ffmpeg -y -f concat -safe 0 -i /tmp/ffmpeg_list.txt -c copy \
	           $(OUT_DIR)/compilation_$$(date +%s).mp4; \
	    echo "✅ Compilation complete."; \
	else echo "⚠️  No videos found."; fi

# ---------------------------------------------------------------------
clean: ## delete generated files
	@echo "🧹 Cleaning build artefacts…"
	rm -f hooks.csv scripts.json clean.json || true
	rm -rf $(AUDIO_DIR) $(OUT_DIR)
	@echo "Done."

# ---------------------------------------------------------------------
help:  ## show this list
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'
