# YouTube IP V5 Architecture

## Sidebar Navigation

1. `Channel Analysis`
2. `Channel Insights`
3. `Thumbnails`
4. `Outlier Finder`
5. `Ytuber`
6. `Tools`
7. `Deployment`

V5 removes the sidebar `Assistant` and removes Google OAuth from `Channel Insights`.

## Full Runtime And Data Pipeline

```mermaid
flowchart TD
    A["GitHub committed CSVs<br/>data/youtube api data/*.csv"] --> B["streamlit_app.py"]
    U["User actions"] --> B
    B --> C["dashboard/app.py"]
    C --> D["dashboard/components/sidebar.py"]
    D --> E["Page views"]

    S["Streamlit secrets / env"] --> F["src/utils/api_keys.py"]
    F --> G["YouTube Data API v3"]
    F --> H["Gemini / OpenAI"]

    A --> J["Channel Analysis / Thumbnails"]
    G --> K["Ytuber / Channel Insights / Outlier Finder / Tools"]
    H --> L["Thumbnails / Ytuber / Outlier Finder"]

    J --> M["pandas transforms + service payloads"]
    K --> M
    L --> M

    K --> N["Channel Insights service path"]
    N --> N1["load_public_channel_workspace(...)"]
    N1 --> N2["ensure_public_channel_frame(...)"]
    N2 --> N3["add_channel_video_features(...)"]
    N3 --> N4["_apply_requested_topic_mode(...)"]
    N4 --> N5["assign_topic_labels(...)"]
    N4 --> N6["apply_optional_topic_model(...)"]
    N6 -->|failure| N5
    N5 --> N7["primary_topic + topic_labels + topic_source"]
    N6 --> N7
    N7 --> N8["_score_videos(...)"]
    N8 --> N9["topic / duration / title / timing metrics"]
    N9 --> N10["summary + outliers + recommendations + snapshots"]

    M --> P["dashboard/components/visualizations.py"]
    N10 --> P
    P --> Q["Charts, cards, tables, downloads, AI outputs"]
```

## Page Problem Map

| Page | Problem Solved | Main Services / Inputs | Main UI Outputs | Interlinks |
| --- | --- | --- | --- | --- |
| `Channel Analysis` | benchmark bundled datasets | CSVs, pandas, visualization helpers | KPI cards, trend charts, ranked tables | shares benchmark context with `Thumbnails` |
| `Channel Insights` | analyze one tracked public channel over time | `public_channel_service`, `channel_snapshot_store`, `channel_insights_service`, optional BERTopic | topic trends, format analysis, outliers, next-topic ideas | can inform `Outlier Finder` themes |
| `Thumbnails` | generate or export thumbnails without mixing broader strategy UI | `thumbnail_generator.py`, `thumbnail_hub_service.py`, public thumbnail URLs | generated thumbnails, preview cards, downloadable images | lighter replacement for the old recommendations surface |
| `Outlier Finder` | find niche winners | `outliers_finder.py`, `outlier_ai.py`, YouTube API | scored outlier tables, breakout snapshot, AI research | receives handoff from `Ytuber` and `Channel Insights` |
| `Ytuber` | run a live creator AI workspace | YouTube API, pooled API keys, thumbnail generator | AI Studio, audit views, keyword and planner outputs | can hand off into `Outlier Finder` |
| `Tools` | export public YouTube assets | `youtube_tools.py`, `transcript_service.py`, `yt-dlp`, `ffmpeg` | metadata previews, transcript/audio/video/thumbnail downloads | standalone utility surface |
| `Deployment` | explain setup and deployment | static instructions in app shell | repo, branch, secrets, deploy notes | operational reference only |

## Live API Extraction Flow

```mermaid
flowchart LR
    A["User enters channel, keyword, or URL"] --> B["Page view"]
    B --> C["src/utils/api_keys.py"]
    C --> D["Selected provider key"]
    D --> E["YouTube Data API request"]
    E --> F["Service-layer normalization"]
    F --> G["pandas dataframes / scored payloads"]
    G --> H["dashboard/components/visualizations.py"]
    H --> I["Rendered Streamlit UI"]
```

In V5, `Channel Insights` is public-only. It does not use Google OAuth and it does not merge owner-only YouTube Analytics metrics.

## Channel Insights Topic Integration

The base `Channel Insights` dataframe is built the same way regardless of topic mode:

1. `load_public_channel_workspace(...)`
2. `ensure_public_channel_frame(...)`
3. `add_channel_video_features(...)`
4. `_apply_requested_topic_mode(...)`

After that, both topic modes feed the same downstream metrics, scoring, outlier detection, idea generation, and snapshot persistence.

```mermaid
flowchart TD
    A["dashboard/views/channel_insights.py"] --> B["refresh_channel_insights(...)"]
    B --> C["load_public_channel_workspace(...)"]
    C --> D["ensure_public_channel_frame(...)"]
    D --> E["add_channel_video_features(...)"]
    E --> F["_apply_requested_topic_mode(...)"]
    F --> G["assign_topic_labels(...)"]
    F --> H["apply_optional_topic_model(...)"]
    H -->|failure| G
    G --> I["primary_topic + topic_labels + topic_source='heuristic'"]
    H --> J["model_topic_id + model_topic_label_raw + model_topic_label"]
    J --> K["primary_topic + topic_labels + topic_source='bertopic_global'"]
    I --> L["_score_videos(...)"]
    K --> L
    L --> M["build_topic_metrics(...)"]
    L --> N["build_duration_metrics(...)"]
    L --> O["build_title_pattern_metrics(...)"]
    L --> P["build_publish_day_metrics(...) + build_publish_hour_metrics(...)"]
    M --> Q["_outlier_and_underperformer_tables(...)"]
    N --> R["_build_summary(...)"]
    O --> R
    P --> R
    Q --> S["build_grounded_idea_bundle(...) + maybe_generate_ai_overlay(...)"]
    R --> T["store_channel_snapshot(...)"]
    S --> T
    T --> U["Overview / Topic Trends / Formats / Outliers / Next Topics / History"]
```

### Topic Outputs That Persist

- `primary_topic` is the row-level theme key used in topic metrics and UI explanations.
- `topic_labels` stores the per-video label list used for grouping and later inspection.
- `topic_source` records whether the row came from heuristics or BERTopic beta.
- summary JSON and insight payloads persist:
  - `topic_mode_requested`
  - `topic_mode_used`
  - `topic_model_status`
  - `topic_model_bundle_version`
  - `topic_model_failure_reason`

## Model-Backed Topic Flow

```mermaid
flowchart LR
    A["Streamlit secrets"] --> B["MODEL_ARTIFACTS_ENABLED"]
    A --> C["MODEL_ARTIFACTS_MANIFEST_URL"]
    C --> D["src/services/model_artifact_service.py"]
    D --> E["Manifest JSON"]
    E --> F["artifact_url + sha256 + bundle_version"]
    F --> G["Download on explicit beta refresh only"]
    G --> H["outputs/models/runtime/<bundle_version>/"]
    H --> I["src/services/topic_model_runtime.py"]
    I --> J["src/services/channel_insights_service.py"]
    J --> K["dashboard/views/channel_insights.py"]
    D --> L["Fallback to heuristic topics"]
    L --> J
```

Topic modes:

- `Heuristic Topics` uses built-in keyword and rule grouping
- `Model-Backed Topics` uses optional BERTopic semantic grouping

### Heuristic Topic Derivation

```mermaid
flowchart LR
    A["video_title + video_tags + short video_description excerpt"] --> B["tokenize_topic_text(...)"]
    B --> C["normalize_topic_token(...)"]
    C --> D["drop stopwords + short tokens"]
    D --> E["weight tokens using log1p(views_per_day + 1)"]
    E --> F["build top token pool"]
    F --> G["assign topic_labels"]
    G --> H["set primary_topic from first label"]
```

### BERTopic Beta Preprocessing

```mermaid
flowchart LR
    A["video_title"] --> B["duplicate title"]
    C["video_description"] --> D["strip boilerplate + truncate"]
    E["video_tags"] --> F["normalize tags"]
    B --> G["build_bertopic_inference_text(...)"]
    D --> G
    F --> G
    G --> H["remove standalone digits"]
    H --> I["compute bertopic_token_count"]
    I --> J["flag is_sparse_text"]
    J --> K["BERTopic transform(...)"]
    K --> L["model_topic_id + raw label + human label + topic_source"]
```

## Branch Notes

- V5 removes the global `Assistant`
- V5 removes Google OAuth and owner-only analytics overlays
- V5 renames page 3 to `Thumbnails`
- BERTopic is optional and never required at app boot
