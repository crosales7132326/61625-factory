# ───────────────────────────────────────────────────────────────
# 61625-factory  •  Video-factory automation
# ───────────────────────────────────────────────────────────────

.PHONY: setup short shorts daily test compile clean help

# Commands
PYTHON := python3
NPM    := npm

# Dirs
VISUALIZER_DIR := visualizer
AUDIO_DIR      := audio
OUT_DIR        := out

# --------------------------------------------------------------
setup: ## install Python + Node deps
	@echo "🔧 Setting up environment…"
	$(PYTHON) -m pip install -r requirements.txt
	cd $(VISUALIZER_DIR) && $(NPM) ci

# --------------------------------------------------------------
define render_video
	@STORY_TEXT=$$(jq -r '.[0].story' clean.json); \
	AUDIO_FILE=$$(jq -r '.[0].audio_file' clean.json); \
	PROPS=$$(jq -n --arg st "$$STORY_TEXT" --arg af "$$AUDIO_FILE" \
	    '{"storyText":$$st,"audioFile":$$af}'); \
	npx remotion render visualizer/src/index.ts StoryVideo \
	    $(1) --codec=h264 $(2) --props "$$PROPS"
endef

# --------------------------------------------------------------
short: setup ## 1 full-length narrated Short
	@echo "🎬 Generating a single short video…"
	@mkdir -p $(AUDIO_DIR) $(OUT_DIR)

	$(PYTHON) agents/trend_scout.py  --limit 1
	$(PYTHON) agents/story_writer.py --limit 1
	$(PYTHON) agents/compliance_editor.py
	$(PYTHON) agents/narrator.py     --limit 1

	@echo "🖥️  Rendering video…"
	$(call render_video,$(OUT_DIR)/short_$$(date +%s).mp4,)

	@echo "✅ short target complete!"

shorts: short  ## alias

# --------------------------------------------------------------
daily: setup  ## generate 10 Shorts
	@echo "📅 Generating 10 Shorts for daily upload…"
	@for i in $$(seq 1 10); do \
	    echo "─── Video $$i/10 ───"; \
	    $(MAKE) --no-print-directory short; \
	    sleep 1; \
	done
	@echo "🏁 daily target complete!"

# --------------------------------------------------------------
test: setup  ## quick CI test – 30-s video, fallback OK
	@echo "🧪 Generating 30-sec TEST video…"
	@mkdir -p $(AUDIO_DIR) $(OUT_DIR)

	$(PYTHON) agents/trend_scout.py  --limit 1 --fallback
	$(PYTHON) agents/story_writer.py --limit 1 --fallback
	$(PYTHON) agents/compliance_editor.py
	$(PYTHON) agents/narrator.py     --limit 1 --fallback

	@echo "🖥️  Rendering test video…"
	$(call render_video,$(OUT_DIR)/test_video.mp4,--frames=0-899)

	@echo "✅ test target complete!"

# --------------------------------------------------------------
compile: ## concat latest 30 MP4s
	@echo "📼 Compiling latest 30 videos…"
	@ls -t $(OUT_DIR)/*.mp4 2>/dev/null | head -30 > /tmp/video_list.txt || true
	@if [ -s /tmp/video_list.txt ]; then \
	    sed 's/^/file /' /tmp/video_list.txt > /tmp/ffmpeg_list.txt; \
	    ffmpeg -y -f concat -safe 0 -i /tmp/ffmpeg_list.txt -c copy \
	           $(OUT_DIR)/compilation_$$(date +%s).mp4; \
	    echo "✅ Compilation ready."; \
	else echo "⚠️  No MP4s found."; fi

# --------------------------------------------------------------
clean: ## delete generated artefacts
	@echo "🧹 Cleaning artefacts…"
	rm -f hooks.csv scripts.json clean.json 2>/dev/null || true
	rm -rf $(AUDIO_DIR) $(OUT_DIR)
	@echo "Done."

# --------------------------------------------------------------
help: ## show this list
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | \
	  awk 'BEGIN{FS=":.*?## "}$${printf "  \033[36m%-10s\033[0m %s\n",$$1,$$2}'
