# 61625-factory • Makefile
.PHONY: setup short shorts daily test compile clean help

PYTHON := python3
NPM    := npm

VISUALIZER_DIR := visualizer
PUBLIC_AUDIO   := public/audio      # <-- fixed path
AUDIO_DIR      := audio
OUT_DIR        := out

# ------------------------------------------------------------------
setup: ## install deps
	@echo "🔧 Installing deps…"
	$(PYTHON) -m pip install -r requirements.txt
	cd $(VISUALIZER_DIR) && $(NPM) ci

# ------------------------------------------------------------------
define render
	@STORY_TEXT=$$(jq -r '.[0].story' clean.json | jq -Rs .); \
	AUDIO_SRC_RAW=$$(jq -r '.[0].audio_file' clean.json); \
	AUDIO_SRC=$$(case "$$AUDIO_SRC_RAW" in audio/*) echo "$$AUDIO_SRC_RAW";; *) echo "audio/$$AUDIO_SRC_RAW";; esac); \
	AUDIO_BASE=$$(basename $$AUDIO_SRC); \
	mkdir -p $(PUBLIC_AUDIO); \
	cp $$AUDIO_SRC $(PUBLIC_AUDIO)/$$AUDIO_BASE; \
	PROPS=$$(jq -n --arg st "$$STORY_TEXT" --arg af "audio/$$AUDIO_BASE" \
	      '{"storyText":$$st,"audioFile":$$af}'); \
	npx remotion render \
	    visualizer/src/index.ts \
	    StoryVideo \
	    $(1) --codec=h264 $(2) --props "$$PROPS"
endef

# ------------------------------------------------------------------
short: setup ## 1 full-length Short
	mkdir -p $(AUDIO_DIR) $(OUT_DIR)
	$(PYTHON) agents/trend_scout.py  --limit 1
	$(PYTHON) agents/story_writer.py --limit 1
	$(PYTHON) agents/compliance_editor.py
	$(PYTHON) agents/narrator.py     --limit 1
	$(call render,$(OUT_DIR)/short_$$(date +%s).mp4,)
	@echo "✅ short done"

shorts: short  ## alias

# ------------------------------------------------------------------
daily: setup   ## 10 Shorts
	@for i in $$(seq 1 10); do echo "── video $$i/10 ──"; $(MAKE) --no-print-directory short; done
	@echo "✅ daily done"

# ------------------------------------------------------------------
test: setup    ## 30-s quick test
	mkdir -p $(AUDIO_DIR) $(OUT_DIR)
	$(PYTHON) agents/trend_scout.py  --limit 1 --fallback
	$(PYTHON) agents/story_writer.py --limit 1 --fallback
	$(PYTHON) agents/compliance_editor.py
	$(PYTHON) agents/narrator.py     --limit 1 --fallback
	$(call render,$(OUT_DIR)/test_video.mp4,--frames=0-899)
	@echo "✅ test done"

# ------------------------------------------------------------------
compile: ## concat last 30 MP4s
	@ls -t $(OUT_DIR)/*.mp4 2>/dev/null | head -30 > /tmp/list.txt || true
	@if [ -s /tmp/list.txt ]; then sed 's/^/file /' /tmp/list.txt > /tmp/ff.txt && \
	   ffmpeg -y -f concat -safe 0 -i /tmp/ff.txt -c copy \
	   $(OUT_DIR)/compilation_$$(date +%s).mp4; \
	else echo "⚠️  No MP4s."; fi

clean: ## delete artefacts
	rm -f hooks.csv scripts.json clean.json
	rm -rf $(AUDIO_DIR) $(OUT_DIR) public
	@echo "🧹 cleaned"

help:  ## show targets
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | \
	  awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-10s\033[0m %s\n",$$1,$$2}'
