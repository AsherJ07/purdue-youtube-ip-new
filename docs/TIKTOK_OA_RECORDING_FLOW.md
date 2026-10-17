# YCreator TikTok OA — Recording Flow Before Final Script

Use this as a screen-direction guide, not a narration script. Record the walkthrough first. After the video is attached to the chat, the final script will be written against the actual click timing, loading time, scroll position, and visible results.

## Keep this opening

> Hi, I’m Asher, and this is YCreator. I built it around a problem creators face every week: they must publish before audience interest moves on, but analytics explain the past and generative AI often returns generic ideas without evidence. YCreator connects those worlds to help creators decide what to test next. It is a large product, and with only five minutes I’ll cover the supporting analytics quickly and focus on the AI workflows. That prioritization is intentional; good product management means deciding what matters most.

After this opening, speak naturally or record only the screen flow. Do not try to follow the earlier draft script.

## Before recording

Open these five tabs in order:

1. [Channel Analysis](https://youtube-ip-v7.streamlit.app/)
2. [YCreator architecture](../.archify/architecture-ycreate-ai-decision-system-20261016-034758/ycreate-ai-decision-system.html)
3. [Channel Insights](https://youtube-ip-v7.streamlit.app/_page_channel_insights)
4. [Creator Studio](https://youtube-ip-v7.streamlit.app/_page_creator_studio)
5. [Outlier Finder](https://youtube-ip-v7.streamlit.app/_page_outlier_finder)

Preload `@Ninja` in Channel Insights and Creator Studio. Select BERTopic once so its result is cached. Run the Creator Studio actions you intend to show once before recording. Leave Outlier Finder reset because `science shorts` should be entered visibly during the recording.

## Five-minute screen flow

### 0:00–0:35 — Opening and product scope

**Starting screen:** Channel Analysis near the top of the page.

- Deliver the approved opening above.
- Keep the cursor still until mentioning that the product is broad.
- Briefly move the cursor across the four destinations in the left navigation.
- Do not click through them yet.
- At approximately 0:33, switch to the architecture tab.

**What the viewer should understand:** the urgent creator problem, what YCreator does, and why the demo will prioritize AI.

### 0:35–1:35 — Architecture

**Starting screen:** architecture in Presentation mode with the entire diagram visible.

Trace this route slowly with the cursor:

1. **Creator**
2. **YCreator product UI**
3. **YouTube Data API** into **Public data access**
4. **Evidence engine**
5. **Topic intelligence**
6. **Decision engine** back to the product UI
7. **Gemini / OpenAI** into the **Generative AI layer**
8. Editable output back to the product UI

Pause the cursor briefly on:

- **Evidence engine:** deterministic metrics and age/channel baselines
- **Topic intelligence:** heuristics versus BERTopic, abstention, and fallback
- **Generative AI layer:** user-triggered text and image generation

Do not open node detail panels. Return to Channel Analysis at approximately 1:32.

**What the viewer should understand:** AI generation comes after evidence, weak semantic results can fall back, and creators retain control.

### 1:35–1:45 — Channel Analysis

- Point to the headline metrics.
- Point to one comparison chart only.
- Do not scroll through the page.
- Switch to Channel Insights.

**What the viewer should understand:** this page provides a consistent benchmark and is intentionally not the focus of the AI demo.

### 1:45–2:15 — Channel Insights and BERTopic

**Starting state:** Ninja loaded with BERTopic selected.

1. Point to **Heuristics** and **BERTopic** so the two modes are visible.
2. Expand **How BERTopic works**.
3. Let the viewer see the actual pipeline explanation:
   - cleaned titles, descriptions, and tags
   - semantic grouping rather than exact keyword matching
   - comparison by daily reach, momentum, and supporting-video count
   - fallback when text or model output is unreliable
4. Collapse the explanation.
5. Point to the current theme result and its confidence/fallback state.
6. Open **Topic Trends** only if the useful chart is immediately visible; otherwise remain on Overview.
7. Switch to Creator Studio.

**What the viewer should understand:** what BERTopic receives, what it produces, how topic quality is evaluated, and what happens when confidence is weak.

### 2:15–3:45 — Creator Studio

**Starting state:** `@Ninja` already loaded.

Move through the workflow selector in this order:

1. **Channel overview** — show the channel baseline for two or three seconds.
2. **Topic opportunities** — point to the highest-ranked useful themes.
3. **Content ideas and drafts** — show the prefilled Fortnite brief, provider/model selection, audience, format, and constraints. Show a cached generated draft if available.
4. **Title and metadata review** — show the prefilled title and description. Run or reveal the score and point to one actionable improvement.
5. **Competitor comparison** — show the prefilled `@SypherPK`, `@NickEh30`, and `@TypicalGamer` set. Show the cached comparison and one topic gap; do not wait for a fresh API pull.
6. **Publishing planner** — point to the timing matrix and the four-week test calendar.
7. **Thumbnail lab** — show the prefilled creative direction, provider/model controls, and an existing output if available. Do not wait for a new image generation.

Move quickly but allow each selected workflow to finish rendering before clicking the next one.

**What the viewer should understand:** YCreator carries one evidence-backed signal through ideation, packaging, competitive context, scheduling, and visual creation. The creator controls the models and can edit every output.

### 3:45–4:40 — Outlier Finder and evidence synthesis

1. Click **Niche or keyword**.
2. Type `science shorts` manually.
3. Click **Find outliers**.
4. Point to two outlier cards from differently sized channels.
5. Point briefly to the breakout map.
6. Scroll to **AI evidence synthesis**.
7. Click **Generate synthesis**.
8. When the result appears, show:
   - breakout subthemes inside science shorts
   - the supporting video evidence
   - the winning title structure or repeatable content angle
   - the final concept, opening hook, and success check

Do not expand supporting evidence unless enough time remains.

**What the viewer should understand:** the query defines a category, while the AI identifies what to make inside that category. Recommendations must be supported by repeated measured evidence.

### 4:40–5:00 — Hold the outcome and close

- Keep the recommended next-video brief visible.
- Do not navigate again.
- Leave the final frame on the concept, hook, and measurable success check.

**What the viewer should understand:** the product ends with a testable creator decision, not an ungrounded AI paragraph.

## If something loads slowly

- Do not refresh the application.
- Wait no more than about six seconds for a model response.
- If a prepared result does not appear, move to the next step and leave the loading state in the recording.
- Do not restart the five-minute walkthrough for a small delay. The final narration can use that time to explain the underlying product decision.

## What to send back

Attach the recorded video file directly to the chat. A rough or silent recording is acceptable. The final script will then be matched to:

- the exact duration of each screen
- the actual clicks and scrolls
- visible metrics and generated outputs
- pauses caused by loading
- where deeper BERTopic and generative-AI explanations naturally fit

