# YouTube Creator Insights — Week 7 & 8 Progress
**Project:** Purdue Industry Practicum (PYI)
**Date:** February 25, 2026
**Sprint Focus:** Data Pipeline Completion → BERTopic Model Training → Dashboard Shell

---

## Overview

This document covers all work completed in the current sprint session, spanning the tail end of Week 6 through Week 7 and the start of Week 8. The session took the project from raw category CSVs through a fully merged, cleaned, and preprocessed dataset, and completed BERTopic model training with validated output.

---

## Week 6 Completion — Data Cleaning & EDA (PYI-3)

**Status: Complete — mark Done in Jira.**

### Merge (`scripts/merge_datasets.py`)

Consolidated the six category CSVs into `data/processed/combined_videos_raw.csv`.

**Duplicate handling:**

- **Within-file duplicates** — Gaming, entertainment, food, and tech each contained videos scraped on multiple snapshot dates. Resolved by keeping the latest snapshot per `video_id`.
- **Cross-category duplicates** — 250 video_ids appeared in both `research_science` and `tech` (Ben Eater, Computerphile, Practical Engineering, Real Engineering, Two Minute Papers). Resolved by reassigning all five channels to `research_science` (more specific label) before deduplication.

**Final merged dataset:** 29,702 rows → 28,037 unique videos across 461 channels.

| Category | Videos | Channels |
|---|---|---|
| research_science | 6,779 | 40 |
| entertainment | 4,690 | 99 |
| tech | 4,294 | 92 |
| food | 4,126 | 87 |
| gaming | 4,093 | 59 |
| fitness | 4,055 | 84 |

---

### EDA (`notebooks/exploratory/02_eda_youtube_metadata.ipynb`)

9 cells, all executed. Figures saved to `outputs/figures/`.

| Cell | Content |
|---|---|
| 1 | Imports, load, type casting, duration parsing |
| 2 | Dataset overview — null rates, videos/channels per category, Shorts counts |
| 3 | View count distribution (log scale) + median views by category |
| 4 | Engagement metrics — like rate and comment rate by category |
| 5 | Duration distribution — long-form histogram + median duration by category |
| 6 | Channel-level stats — subscribers vs median views scatter, top 10 channels |
| 7 | Publishing volume per quarter by category (2020–2026) |
| 8 | Text field coverage — BERTopic readiness by category |
| 9 | Data quality flag summary |

**Key findings:**
- Shorts are 22.8% of all videos; fitness (35.6%) and food (31.9%) most short-form heavy
- 29% of videos have no tags; fitness worst at 40.1%
- 2,426 videos have neither description nor tags — title only for BERTopic
- Top channels by median views: MrBeast Gaming (47.6M), Mark Rober (24.4M), NileRed (11.6M)

---

### Preprocessing (`notebooks/modeling/03_bertopic_experiments.ipynb`, Cells 1–8)

| Cell | Content |
|---|---|
| 1 | Imports, load `combined_videos_raw.csv`, type casting |
| 2 | Drop unusable rows — 37 dropped (1 null views, 36 unparseable durations) |
| 3 | Derive engagement features: `like_rate`, `comment_rate`, `views_per_day`, `publish_year`, `publish_month` |
| 4 | Text cleaning — strip URLs, hashtags, @mentions, emoji, punctuation from title/description/tags |
| 5 | Build `bertopic_text` — title doubled + description + tags; flag sparse docs (< 5 tokens) |
| 6 | Drop 26 low-value columns (thumbnail URLs/dimensions, redundant IDs, low-signal booleans) |
| 7 | Save three output files |
| 8 | Preprocessing summary |

**bertopic_text strategy:**
```
bertopic_text = title_clean + " " + title_clean + " " + desc_clean + " " + tags_clean
```
Title doubled to upweight it relative to the longer description.

**Text coverage in final corpus (28,000 docs):**

| Coverage | Count | % |
|---|---|---|
| Title + description + tags | 19,740 | 70.5% |
| Title + description only | 5,512 | 19.7% |
| Title + tags only | 166 | 0.6% |
| Title only | 2,426 | 8.7% |
| Sparse (< 5 tokens) | 182 | 0.7% |

**Outputs:** `combined_videos_clean.csv` (28,000 × 42), `bertopic_corpus.txt` (28,000 lines), `bertopic_metadata.csv` (28,000 × 12)

---

## Week 7 — BERTopic Model Training (PYI-84)

**Status: Complete — mark Done in Jira.**

### Environment Setup

BERTopic is not available on conda defaults. Required a fresh environment:

```bash
conda create -n youtube-ip python=3.11
conda activate youtube-ip
pip install bertopic sentence-transformers umap-learn hdbscan jupyter pandas numpy matplotlib seaborn
pip install ipykernel
python -m ipykernel install --user --name youtube-ip --display-name "youtube-ip"
```

**Why Python 3.11:** The base environment (Python 3.12) triggers a `ForwardRef._evaluate()` TypeError via a `langsmith` → `pydantic.v1` chain imported by BERTopic's LangChain backend. Python 3.11 avoids this entirely.

**Issue encountered:** Cell 10 (component model assembly) was accidentally saved as a Markdown cell instead of Code. This caused `NameError: name 'embedding_model' is not defined` in Cell 12, and cells 12–15 all failed. Fixed by changing the cell type back to Code and rerunning from Cell 10.

---

### PYI-87 — Implement Training Notebook (Cells 9–11)

**Cell 9 — Imports & Config**

| Constant | Value | Notes |
|---|---|---|
| `RANDOM_STATE` | 42 | Reproducibility |
| `MIN_TOPIC_SIZE` | 30 | Min videos per topic |
| `N_GRAM_RANGE` | (1, 2) | Unigrams + bigrams |
| `TOP_N_WORDS` | 10 | Keywords per topic |

**Cell 10 — Component Models**

| Component | Choice | Rationale |
|---|---|---|
| Embedding model | `all-MiniLM-L6-v2` | Fast, lightweight, strong semantic quality for short-to-medium text |
| UMAP | `n_neighbors=15, n_components=5, metric=cosine` | 5 components before HDBSCAN (not 2 — that's visualization only) |
| HDBSCAN | `min_cluster_size=30, eom, prediction_data=True` | `prediction_data=True` required for `transform()` on new docs later |
| Vectorizer | `CountVectorizer(ngram_range=(1,2), stop_words=english, min_df=5, max_df=0.85)` | Bigrams improve keyword quality |
| Representation | `KeyBERTInspired()` | Refines c-TF-IDF labels using embedding similarity |

**Cell 11 — Training**

```
2026-02-25 13:52:43 — Embedding start
2026-02-25 13:56:08 — Embedding complete       (~3.5 min)
2026-02-25 13:56:08 — UMAP start
2026-02-25 13:56:30 — UMAP complete            (~22 sec)
2026-02-25 13:56:30 — HDBSCAN start
2026-02-25 13:56:32 — HDBSCAN complete         (~2 sec)
2026-02-25 13:56:32 — c-TF-IDF extraction
2026-02-25 13:56:34 — c-TF-IDF complete
2026-02-25 13:56:34 — Topic reduction start    (220 → auto-merge)
2026-02-25 13:56:51 — Representation fine-tuning complete
2026-02-25 13:56:51 — Reduced 220 → 119 topics

Total training time: ~7 minutes
```

**Training result:**
- **118 topics** found (excluding outlier topic -1)
- **10,459 outlier docs** (37.4%) assigned to topic -1

---

### PYI-88 — Topic Labels & Performance Stats (Cell 12)

**Top 20 topics by size:**

| Topic | Count | Label |
|---|---|---|
| 0 | 2,529 | yoga, routine, exercises, exercise |
| 1 | 1,740 | cook, cookbook, chef, cooking |
| 2 | 1,406 | black holes, space time, dark matter, general relativity |
| 3 | 974 | roblox, sonic, horror game, walkthrough gameplay |
| 4 | 579 | laptops, lenovo, laptop, dell |
| 5 | 550 | supernatural, thriller, ending explained, stranger things |
| 6 | 538 | verge, tech news, gadget tech, vergecast |
| 7 | 404 | fortnite, battle royale, nova, new update |
| 8 | 359 | science chemistry, chemical, chemistry, acid |
| 9 | 333 | gratitude, kindness, life, say thank |
| 10 | 321 | numberphile, numbers, number, mathematics comedy |
| 11 | 278 | nvidia ai, gpu, nvidia, simulations, unreal engine |
| 12 | 219 | spider man, avengers doomsday, avengers, marvel |
| 13 | 214 | computers computerphile, computerphile computer |
| 14 | 211 | statistics, data, statistical, data science |
| 15 | 193 | periodic videos, periodic, elements, element |
| 16 | 187 | tiktok, copyright, influencers, toxic |
| 17 | 177 | instagram smarter, smarter every day, patreon smarter |
| 18 | 176 | infrastructure, construction, practical engineering |
| 19 | 166 | arc raiders, ninja, fortnite |

**Top 15 topics by median views:**

| Topic | Label | Videos | Median Views | Top Category |
|---|---|---|---|---|
| 42 | minecraft challenges, future minecraft | 80 | 36,901,338 | gaming |
| 108 | arcade, order, vodka, 2nd channel | 39 | 7,586,647 | entertainment |
| 61 | instagram, livestreams, youtuber | 53 | 7,385,807 | entertainment |
| 107 | gym, olympic, competition, competing | 40 | 6,072,483 | fitness |
| 116 | kurzgesagt, voice, bird army | 32 | 4,997,199 | research_science |
| 8 | science chemistry, chemical, acid | 359 | 4,609,015 | research_science |
| 103 | stream, donations, channels, irl | 41 | 4,272,683 | gaming |
| 97 | pokemon, twitch discord, emerald | 43 | 3,345,146 | gaming |
| 17 | smarter every day, instagram smarter | 177 | 2,887,104 | research_science |
| 89 | uncle roger, grandpa, nigel | 46 | 2,002,146 | food |
| 18 | infrastructure, practical engineering | 176 | 1,866,527 | research_science |
| 31 | discord, nerdy maths, exclusive | 96 | 1,835,634 | research_science |
| 106 | hermit, episode 10, episode 23 | 40 | 1,716,370 | gaming |
| 28 | minecraft, empires, empire, adventure | 107 | 1,630,493 | gaming |
| 26 | animations, animating math, 3blue1brown | 112 | 1,622,943 | research_science |

---

### PYI-89 — Validate Model Output (Cell 13)

**Outlier rate: 37.4% ⚠ (target < 20%)**

This is high. Primary cause is likely `MIN_TOPIC_SIZE=30` being too large relative to the diversity of content — many short-form and niche videos don't cluster cleanly. Recommended tuning action: lower `MIN_TOPIC_SIZE` to 15–20 and retrain.

**Topic size distribution (118 topics, excl. outliers):**

| Stat | Value |
|---|---|
| Mean | 148.7 videos |
| Median | 54.5 videos |
| Min | 32 videos |
| Max | 2,529 videos |
| Topics < 50 videos | 41 |

**Category coherence:**
- Median dominant-category share: **0.97** — topics are almost entirely single-category
- 105 of 118 topics are >80% one category
- Only 2 topics are cross-category (≤50% dominant share)

This is a strong signal. The model is finding real semantic clusters within categories rather than blending unrelated niches.

**Spot-check (3 random topics):**

- **Topic 45** (fallout season, prime video, amazon prime) → TV/streaming content breakdown and review videos ✓
- **Topic 6** (verge, tech news, vergecast) → Contains some mismatches (self-hosted Nextcloud, Arduino) suggesting this topic is slightly broad
- **Topic 116** (kurzgesagt, bird army, voice) → Clean Kurzgesagt cluster ✓

---

### Save & Summary (Cell 14)

**Outputs saved:**
- `outputs/models/bertopic_model` — serialized model (pickle + c-TF-IDF)
- `data/processed/bertopic_metadata.csv` — 28,000 rows with `topic_id` and `topic_label`
- `data/processed/topic_stats.csv` — per-topic performance stats

```
Documents trained on   : 28,000
Topics found           : 118
Outlier docs (topic -1): 10,459 (37.4%)
Median topic size      : 54 videos
Largest topic          : 2,529 videos
```

---

## Week 8 — Dashboard Shell (PYI-90)

Not yet started. Tickets created today:

| Ticket | Task |
|---|---|
| PYI-91 | Theme & Config |
| PYI-92 | App Entry Point & Sidebar |
| PYI-93 | Build `home.py` |
| PYI-94 | `channel_analysis.py` — Benchmark stats & Data Explorer |
| PYI-95 | `channel_analysis.py` — Topic Landscape |
| PYI-96 | Recommendations Page |
| PYI-97 | Niche Benchmark Display |
| PYI-98 | Data-Driven Recommendations |
| PYI-99 | Wire Thumbnail Generator |
| PYI-100 | Extension Center & Deploy Notes |

Existing dashboard stubs: `dashboard/app.py`, `dashboard/components/sidebar.py`, `dashboard/components/visualizations.py`, `dashboard/pages/channel_analysis.py`, `dashboard/pages/recommendations.py`

---

## Jira Status Summary

| Ticket | Summary | Status |
|---|---|---|
| PYI-2 | Week 5: Full-Scale Data Collection | Done |
| PYI-3 | Week 6: Data Cleaning & EDA | **Mark Done** |
| PYI-66 | Week 6: BERTopic Research & Documentation | In Progress (Debadri) |
| PYI-67 | Week 6: LLM Strategy — Gemini vs GPT-4 | In Progress (Ayush) |
| PYI-68 | Week 5: Data Quality Assessment | Done |
| PYI-81 | Text preprocessing | **Mark Done** |
| PYI-82 | Handle missing data | **Mark Done** |
| PYI-83 | EDA & Quality Validation | **Mark Done** |
| PYI-84 | Week 7: BERTopic Model Training | **Mark Done** |
| PYI-87 | Implement Training Notebook | **Mark Done** |
| PYI-88 | Generate Topic Labels & Performance Stats | **Mark Done** |
| PYI-89 | Validate Model Output | **Mark Done** |
| PYI-90 | Week 7: App Shell & Navigation | To Do |

---

## Files Produced This Session

| File | Location | Description |
|---|---|---|
| `merge_datasets.py` | `scripts/` | Merges 6 category CSVs with dedup logic |
| `combined_videos_raw.csv` | `data/processed/` | 28,037 videos, 54 columns |
| `combined_videos_clean.csv` | `data/processed/` | 28,000 videos, 42 columns, clean text fields |
| `bertopic_corpus.txt` | `data/processed/` | 28,000 documents, one per line |
| `bertopic_metadata.csv` | `data/processed/` | 28,000 rows with topic_id and topic_label |
| `topic_stats.csv` | `data/processed/` | Per-topic performance stats (118 topics) |
| `bertopic_model` | `outputs/models/` | Serialized BERTopic model |
| `02_eda_youtube_metadata.ipynb` | `notebooks/exploratory/` | 9 cells, all executed |
| `03_bertopic_experiments.ipynb` | `notebooks/modeling/` | 14 cells, all executed |

---

## Immediate Next Steps

**Priority 1 — Tune the outlier rate (37.4% is too high):**

Rerun training with `MIN_TOPIC_SIZE = 15` in Cell 9 and re-execute cells 11–14. Target < 20% outliers. If still high at 15, try 10. This is the most important action before moving to the dashboard.

**Priority 2 — Begin PYI-90 (App Shell):**

Once outlier rate is acceptable, start the dashboard. The `bertopic_metadata.csv` and `topic_stats.csv` files are the primary data sources.

**Priority 3 — Mark tickets Done in Jira:**

PYI-3, PYI-81, PYI-82, PYI-83, PYI-84, PYI-87, PYI-88, PYI-89