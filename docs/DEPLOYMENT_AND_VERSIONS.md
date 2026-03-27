# Deployment, Model Flow, And Version Notes

## Branch Tag

- Original repo branch tag: `youtube-ip-v4`
- Original repo: `matt-foor/purdue-youtube-ip`
- Deploy repo: `royayushkr/Youtube-IP-V4`
- Deploy branch: `main`

## How The App And Scripts Work Together

```mermaid
flowchart TD
    A["User opens Streamlit app"] --> B["streamlit_app.py"]
    B --> C["dashboard/app.py"]
    C --> D["dashboard/components/sidebar.py"]
    D --> E["Sidebar pages"]
    D --> F["Sidebar Assistant"]

    subgraph Pages
        E1["Channel Analysis"]
        E2["Recommendations"]
        E3["Ytuber"]
        E4["Channel Insights"]
        E5["Outlier Finder"]
        E6["Tools"]
        E7["Deployment"]
    end

    E --> E1
    E --> E2
    E --> E3
    E --> E4
    E --> E5
    E --> E6
    E --> E7

    E1 --> G1["Bundled CSV analytics"]
    E2 --> G2["Strategy guidance + thumbnail generation"]
    E3 --> G3["Live YouTube API + AI suite"]
    E4 --> G4["Channel snapshot and topic services"]
    E5 --> G5["Outlier search + AI report"]
    E6 --> G6["Metadata, transcript, audio, video, thumbnail tools"]
    F --> G7["Assistant retrieval and LLM services"]
```

## How Model-Backed Topics Are Actually Deployed

The BERTopic-backed topic mode is activated through Streamlit secrets, not through a model file committed into the main runtime tree.

```mermaid
flowchart LR
    A["Streamlit secrets"] --> B["MODEL_ARTIFACTS_ENABLED"]
    A --> C["MODEL_ARTIFACTS_MANIFEST_URL"]
    C --> D["src/services/model_artifact_service.py"]
    D --> E["Manifest JSON"]
    E --> F["artifact_url + sha256 + bundle_version"]
    F --> G["Download artifact on explicit beta request"]
    G --> H["outputs/models/runtime/<bundle_version>/"]
    H --> I["src/services/topic_model_runtime.py"]
    I --> J["src/services/channel_insights_service.py"]
    J --> K["dashboard/views/channel_insights.py"]
    J --> L["SQLite snapshot payload"]
```

### Streamlit Secrets Block

```toml
YOUTUBE_API_KEYS = ["your_youtube_key_1", "your_youtube_key_2"]
GEMINI_API_KEYS = ["your_gemini_key_1", "your_gemini_key_2"]
OPENAI_API_KEYS = ["your_openai_key_1", "your_openai_key_2"]

GOOGLE_OAUTH_CLIENT_ID = "your-google-oauth-client-id"
GOOGLE_OAUTH_CLIENT_SECRET = "your-google-oauth-client-secret"
GOOGLE_OAUTH_REDIRECT_URI = "https://your-app-name.streamlit.app/"

MODEL_ARTIFACTS_ENABLED = true
MODEL_ARTIFACTS_MANIFEST_URL = "https://raw.githubusercontent.com/royayushkr/Youtube-IP-V4/main/data/model_manifests/bertopic_manifest_2026.03.27.json"
MODEL_ARTIFACTS_CACHE_DIR = "outputs/models/runtime"
MODEL_ARTIFACTS_DOWNLOAD_TIMEOUT_SECONDS = 300
MODEL_ARTIFACTS_MAX_SIZE_MB = 512
```

### What The Manifest Does

The secret points to a manifest JSON file in the deploy repo. That manifest then defines:

- the external `artifact_url`
- the expected `sha256`
- the `bundle_version`
- the loading subpath for the runtime service

In this branch, the checked-in manifest currently points to the external BERTopic artifact hosted from the `asher` artifact source. The app reads the manifest first, then downloads and validates the artifact lazily only when beta topic mode is requested.

## V4 Vs V5

| Area | V4 (`youtube-ip-v4`) | V5 (`youtube-ip-v5`) |
| --- | --- | --- |
| Sidebar Assistant | Present | Removed |
| Google OAuth | Present | Removed |
| Channel Insights | Public + owner overlays when authorized | Public-only |
| Recommendations page | Present as `Recommendations` | Renamed in-app to `Thumbnails` |
| Ytuber | Present | Present |
| Tools | Present | Present |
| Deployment page | Present | Present |
| BERTopic beta | Optional | Optional |
| Deploy repo | `royayushkr/Youtube-IP-V4` | `royayushkr/Youtube-IP-V5` |

## What To Use When

- Use `youtube-ip-v4` if you want the fullest legacy product surface, including the Assistant and Google OAuth owner analytics.
- Use `youtube-ip-v5` if you want the lighter shell and public-only Channel Insights while still keeping the AI suite pages.
