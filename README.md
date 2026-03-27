# YouTube IP V4

YouTube IP V4 is a lighter Streamlit app for YouTube benchmarking, public channel intelligence, thumbnail work, and outlier research.

Live app:

- [youtube-ip-v4.streamlit.app](https://youtube-ip-v4.streamlit.app/)

## App Surface

The app now keeps a lighter core structure while preserving the AI suite pages that are still important to the product.

Primary sidebar order:

1. `Channel Analysis`
2. `Channel Insights`
3. `Thumbnails`
4. `Outlier Finder`

Additional AI suite pages:

5. `Ytuber`
6. `Tools`
7. `Deployment`

### 1. Channel Analysis

Dataset-backed benchmarking across the committed CSV files in `data/youtube api data/`.

It supports:

- category-level portfolio analysis
- channel filters
- date filters
- KPI summaries
- top channels and top videos
- publishing-day analysis
- views versus engagement analysis

Main file:

- `dashboard/views/channel_analysis.py`

### 2. Channel Insights

Public-channel snapshot workflow for recurring channel analysis.

It supports:

- add a public channel by URL, handle, or channel ID
- refresh and persist public snapshots locally
- topic trend analysis
- format and title-pattern analysis
- outlier and underperformer detection
- next-topic and video-direction recommendations
- optional BERTopic beta mode when external model artifact settings are configured

Main files:

- `dashboard/views/channel_insights.py`
- `src/services/channel_insights_service.py`
- `src/services/channel_snapshot_store.py`
- `src/services/public_channel_service.py`
- `src/services/topic_analysis_service.py`
- `src/services/channel_idea_service.py`

Storage:

- `outputs/channel_insights/channel_insights.db`

### 3. Thumbnails

Thumbnail-only workspace.

It supports:

- AI thumbnail generation with Gemini or OpenAI
- richer thumbnail model, size, quality, and output controls
- public YouTube thumbnail preview and export by URL or video ID
- direct image downloads from Streamlit

Main files:

- `dashboard/views/recommendations.py`
- `src/llm_integration/thumbnail_generator.py`
- `src/services/thumbnail_hub_service.py`

Generated outputs:

- `outputs/thumbnails/`

### 4. Outlier Finder

Standalone niche-research and outlier-video discovery workflow.

It supports:

- niche / keyword search
- timeframe, region, and language filters
- subscriber and duration filters
- outlier scoring and scan summaries
- breakout tables and charts
- structured AI report cards

Main files:

- `dashboard/views/outlier_finder.py`
- `src/services/outliers_finder.py`
- `src/services/outlier_ai.py`

### 5. Ytuber

AI workspace for creator planning and generation workflows.

It remains available for:

- AI Studio generation flows
- channel audit views
- keyword and SEO exploration
- competitor and planner workflows
- outlier handoff from the workspace

Main file:

- `dashboard/views/ytuber.py`

### 6. Tools

Standalone creator utility workspace.

It remains available for:

- metadata preview
- thumbnail download
- transcript export
- audio download
- video download
- batch and playlist operations

Main files:

- `dashboard/views/tools.py`
- `src/services/youtube_tools.py`
- `src/services/transcript_service.py`

### 7. Deployment

In-app deployment checklist and setup guidance for Streamlit.

## What Was Removed

This cleaned V4 build intentionally removes:

- the sidebar Assistant
- Google OAuth
- owner-only YouTube Analytics metrics

The app is still public-data-first, lighter to deploy, and easier to reason about, but it keeps the separate AI suite pages that are still part of the workflow.

## Runtime Layout

Active runtime surface:

- `streamlit_app.py`
- `dashboard/`
- `src/services/`
- `src/utils/`
- `src/llm_integration/thumbnail_generator.py`
- `data/model_manifests/`
- `data/youtube api data/`
- `outputs/channel_insights/`
- `outputs/models/`
- `outputs/thumbnails/`

Historical research material remains archived under:

- `research_archive/`

## Local Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Alternative entrypoint:

```bash
streamlit run dashboard/app.py
```

## Streamlit Deployment

Deploy from:

- repo: `royayushkr/Youtube-IP-V5`
- branch: `main`
- main file: `streamlit_app.py`

The root Streamlit entrypoint remains:

- `streamlit_app.py`

## Secrets

Add these in Streamlit Community Cloud or `.streamlit/secrets.toml`:

```toml
YOUTUBE_API_KEYS = ["your_youtube_key_1", "your_youtube_key_2"]
GEMINI_API_KEYS = ["your_gemini_key_1", "your_gemini_key_2"]
OPENAI_API_KEYS = ["your_openai_key_1", "your_openai_key_2"]
```

Optional single-key fallbacks also work:

```toml
YOUTUBE_API_KEY = "your_youtube_key"
GEMINI_API_KEY = "your_gemini_key"
OPENAI_API_KEY = "your_openai_key"
```

### Optional BERTopic Beta For Channel Insights

If you want the experimental model-backed topic flow:

```toml
MODEL_ARTIFACTS_ENABLED = true
MODEL_ARTIFACTS_MANIFEST_URL = "https://raw.githubusercontent.com/royayushkr/Youtube-IP-V4/main/data/model_manifests/bertopic_manifest_2026.03.27.json"
MODEL_ARTIFACTS_CACHE_DIR = "outputs/models/runtime"
MODEL_ARTIFACTS_DOWNLOAD_TIMEOUT_SECONDS = 300
MODEL_ARTIFACTS_MAX_SIZE_MB = 512
```

Without those settings, `Channel Insights` stays on heuristic topics.

## Data And Storage Notes

- `Channel Analysis` reads committed CSVs under `data/youtube api data/`
- `Channel Insights` stores local snapshot history in SQLite under `outputs/channel_insights/`
- `Thumbnails` stores generated image files under `outputs/thumbnails/`
- BERTopic artifacts, if enabled, download lazily into `outputs/models/runtime/`

## Current Limitations

- `Channel Insights` is public-only in this cleaned V4 build
- no Google OAuth or owner-only metrics are available
- BERTopic is optional and off by default
- Channel Insights manual refreshes are persisted, but background daily jobs are not part of this Streamlit app
- thumbnail export is intentionally scoped to public thumbnail URLs only
- `Ytuber` and `Tools` remain richer AI-suite surfaces, so this build is lighter than before but not reduced to a strict 4-page app

## Validation

Recommended validation before deploy:

```bash
python3 -m py_compile dashboard/app.py
pytest -q
streamlit run streamlit_app.py --server.headless true
```
