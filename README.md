# MY YOUTUBE CREATOR STUDIO (Repaired & Scaled Architecture)

A professional, local-first YouTube Creator Studio desktop application and optimization suite built in Python with Streamlit and persistent SQLite storage.

---

## 🌟 Key Architecture & Workspaces

The application is structured into **14 dedicated Creator Workspaces** inspired by YouTube Studio's layout, hierarchy, and usability:

1. **Dashboard**: High-level channel snapshot, active channel card, 4 core KPIs, recent video performance table, top audit deductions, and data source indicators.
2. **My Channel**: Channel identity, handle, avatar, subscriber count, total views, video count, and public description inspector.
3. **Channel Audit**: 10-pillar documented health audit powered by the central `ScoringEngine`. Every deduction is backed by concrete evidence with prioritized recommendations.
4. **Content**: Searchable, sortable catalog of all observed uploads with duration labels (Shorts vs Long-form), view counts, likes, and thumbnail previews.
5. **Shorts Studio**: Dedicated workspace for vertical video (<60s, 9:16). Generates 5 high-impact title formulas, copy-ready descriptions, and platform hashtags.
6. **Long-Form Studio**: Structured chapters, introduction stakes, 5 search/suggested titles, and 8+ minute mid-roll monetization checklists.
7. **Video Analysis**: Pure-Python ISOBMFF box parser inspecting raw MP4/MOV bytes (duration, resolution, 16:9 vs 9:16 aspect ratio, audio presence, bitrate) plus **SRT/VTT subtitle parsing** for speech rate (WPM) and opening hook strength.
8. **SEO and Metadata**: Generates compliant titles, descriptions, and tags. Validates against official platform limits (Title: 100 max, 45-65 optimal; Description: 5,000 max; Tags: 500 max; Hashtags: 3-5 optimal).
9. **Thumbnail Lab**: Technical inspection (1280x720 resolution, 16:9 aspect ratio, <2MB file size) with a mobile YouTube feed card preview mockup.
10. **Competitor Research**: Head-to-head benchmarking of multiple competitor channels. Ranks top uploads by **Daily Velocity (Views / Day)** and identifies format voids.
11. **Analytics**: Official Google OAuth2 workflow + interactive studio demonstration preview for Click-Through Rate (CTR), 28-day retention curves, and traffic sources.
12. **Publishing Planner**: Production task calendar to schedule upcoming video drops, assign format types, and coordinate release windows.
13. **AI Creator Assistant**: Grounded strategy assistant that builds dynamic evidence packages from active channels and video drafts before answering. Distinguishes Verified Data, Observed Patterns, Hypotheses, Recommendations, and Missing Information.
14. **Settings**: Dark/Light theme toggle, API keys configuration (YouTube API v3, Gemini API, Google OAuth), default region/timezones, and database management.

---

## 📊 Documented Scoring Engine (`services/scoring_engine.py`)

Unlike arbitrary scoring systems, all scores are calculated through transparent formulas:

| Score | Scale | Primary Inputs | Failure vs Missing Data Handling |
| :--- | :--- | :--- | :--- |
| **Metadata Completeness** | 0 - 100 | Title (30%), Desc (30%), Tags (20%), Category (10%), Thumbnail (10%) | Evaluates presence & length compliance |
| **Title Clarity & Relevance** | 0 - 100 | Baseline (40) + Length fit (20) + Curiosity hook (20) + Readability (20) | Penalizes ALL-CAPS spam (-15) |
| **Description Quality** | 0 - 100 | Length depth (40) + Links/CTAs (20) + Chapters (20) + Layout (20) | Flags missing chapter timestamps |
| **Tag Relevance** | 0 - 100 | Tag count (40) + Total character budget (30) + Topic keyword match (30) | Flags exceeding 500-character budget |
| **Hashtag Relevance** | 0 - 100 | Optimal count 3-5 (60) + Valid syntax without spaces (40) | Penalizes >15 hashtags as spam risk |
| **Thumbnail Quality** | 0 - 100 | Resolution 1280x720 (40) + 16:9 ratio (30) + Under 2MB size (30) | **Returns 'Insufficient Data' if not inspected** |
| **Content Structure** | 0 - 100 | Opening Hook (45%) + Speech Rate WPM (35%) + Call to Action (20%) | Evaluates spoken transcript / subtitle cadence |
| **Channel Consistency** | 0 - 100 | Catalog depth (40) + Branding consistency (30) + Format strategy (30) | Distinguishes young vs established channels |
| **Data Completeness** | 0 - 100 | `(Available Fields / Total Required Fields) * 100` | Measures schema completeness |
| **Overall Optimization Readiness** | 0 - 100 | Weighted sum across available component scores | **Renormalizes weights; never fabricates missing data** |

---

## 🚀 Installation & Launch on Windows

### 1. Prerequisites
* Python 3.10+ (Verified on Python 3.12)
* PowerShell or Windows Command Prompt

### 2. Navigate to Directory
```powershell
cd C:\Users\am199\.gemini\antigravity\scratch\my_youtube_creator_studio
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Run the Application
```powershell
streamlit run app.py
```
Open your browser at: `http://localhost:8501`

---

## 🧪 Automated Testing (All 34 Tests Passing)

Execute the complete end-to-end test suite:
```powershell
python run_tests.py
```

### Verified Test Scenarios:
1. Valid public channel URL (handles query strings, `/videos` sub-paths)
2. Valid channel handle (`@handle`)
3. Invalid channel URL handling
4. Valid public video ID extraction
5. Invalid video URL handling
6. Fresh channel scan
7. Repeated scan utilizing SQLite cache
8. Explicit `force_refresh` bypassing cache
9. Uploaded video container parsing (MP4/MOV ISOBMFF)
10. Subtitle file parsing (.srt and .vtt timestamped dialogue)
11. Missing transcript handling (graceful fallback)
12. API quota recovery (automatic fallback without crashing)
13. Network failure / sandbox fallback with transparent provenance
14. AI provider unavailable / grounded heuristic engine fallback
15. Incomplete metadata scoring (penalties justified with evidence)
16. Missing thumbnail handling (returns "Insufficient Data", not a fake score)
17. Competitor channel with limited public information
18. Channel with few videos (flags young discovery phase)
19. Historical analytics preview
20. Application restart and persistence across SQLite tables

---

## 🔒 Security & Privacy Notice
* All data is stored locally in your SQLite database (`creator_studio.db`).
* No Google account passwords or OAuth tokens are ever logged or shared.
* The application operates offline-first and can be fully explored without external API keys.
