"""
MY YOUTUBE CREATOR STUDIO
A professional, local-first creator analytics dashboard and video optimization suite.
Designed with YouTube Studio aesthetics, robust SQLite persistence, and multi-workspace workflows.
"""

import datetime
import os
import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

from database.db_manager import DatabaseManager
from services.scoring_engine import ScoringEngine
from services.youtube_service import YouTubeService
from services.video_analyzer import VideoAnalyzer
from services.metadata_generator import MetadataGenerator
from services.competitor_service import CompetitorService
from services.us_optimization_service import USOptimizationService
from services.ai_assistant_service import AIAssistantService
from services.oauth_service import OAuthAnalyticsService

# --- Page Configuration ---
st.set_page_config(
    page_title="YouTube Creator Studio",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Service Dependency Injection ---
@st.cache_resource
def get_services():
    db = DatabaseManager()
    scoring = ScoringEngine()
    yt = YouTubeService()
    analyzer = VideoAnalyzer()
    meta = MetadataGenerator()
    comp = CompetitorService(yt)
    us_opt = USOptimizationService()
    ai = AIAssistantService()
    oauth = OAuthAnalyticsService()
    return db, scoring, yt, analyzer, meta, comp, us_opt, ai, oauth

db, scoring_engine, yt_service, video_analyzer, meta_gen, comp_service, us_service, ai_service, oauth_service = get_services()

# --- Session State Setup ---
if "active_channel" not in st.session_state:
    recent_channels = db.get_recent_channels(limit=1)
    st.session_state.active_channel = recent_channels[0] if recent_channels else None
if "active_audit" not in st.session_state and st.session_state.active_channel:
    st.session_state.active_audit = db.get_latest_channel_audit(st.session_state.active_channel["channel_id"])
elif "active_audit" not in st.session_state:
    st.session_state.active_audit = None

if "active_video_analysis" not in st.session_state:
    recent_vids = db.get_recent_video_analyses(limit=1)
    st.session_state.active_video_analysis = recent_vids[0] if recent_vids else None
if "competitor_data" not in st.session_state:
    st.session_state.competitor_data = None
if "chat_session_id" not in st.session_state:
    st.session_state.chat_session_id = "default_session"
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = db.get_setting("theme_mode", "Dark")

# --- Dynamic Styling: Studio Dark & Light Themes ---
is_dark = st.session_state.theme_mode == "Dark"
bg_color = "#0F0F0F" if is_dark else "#F9F9F9"
card_bg = "#1F1F1F" if is_dark else "#FFFFFF"
text_color = "#F1F1F1" if is_dark else "#0F0F0F"
text_sub = "#AAAAAA" if is_dark else "#606060"
border_color = "#303030" if is_dark else "#E5E5E5"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    .studio-topbar {{
        background-color: {card_bg};
        border-bottom: 1px solid {border_color};
        padding: 10px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-radius: 8px;
        margin-bottom: 20px;
    }}
    .metric-card {{
        background-color: {card_bg};
        border: 1px solid {border_color};
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        margin-bottom: 15px;
    }}
    .metric-title {{
        font-size: 0.85rem;
        color: {text_sub};
        text-transform: uppercase;
        font-weight: 600;
        margin-bottom: 5px;
    }}
    .metric-val {{
        font-size: 1.6rem;
        font-weight: 700;
        color: {text_color};
    }}
    .metric-sub {{
        font-size: 0.8rem;
        color: #3EA6FF;
        margin-top: 4px;
    }}
    .badge-high {{
        background-color: #CC0000;
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: bold;
    }}
    .badge-med {{
        background-color: #FF8800;
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: bold;
    }}
    .badge-low {{
        background-color: #2BA640;
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: bold;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- SIDEBAR: YouTube Studio Brand & Navigation ---
st.sidebar.markdown(
    """
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
        <span style="font-size: 26px;">🔴</span>
        <div>
            <div style="font-size: 1.15rem; font-weight: 700; letter-spacing: -0.5px;">Studio</div>
            <div style="font-size: 0.7rem; color: #888888; text-transform: uppercase;">Creator Analytics</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Active Channel Header in Sidebar
ch = st.session_state.active_channel
if ch:
    st.sidebar.markdown(
        f"""
        <div style="background-color: {card_bg}; padding: 12px; border-radius: 8px; border: 1px solid {border_color}; margin-bottom: 15px;">
            <div style="font-size: 0.75rem; color: {text_sub};">CURRENT CHANNEL</div>
            <div style="font-size: 0.95rem; font-weight: bold; color: {text_color};">{ch.get('title')}</div>
            <div style="font-size: 0.8rem; color: #3EA6FF;">{ch.get('custom_url')}</div>
            <div style="font-size: 0.75rem; color: {text_sub}; margin-top: 4px;">{ch.get('subscriber_count_str', '0')} subscribers</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.sidebar.info("No active channel. Scan a channel below to begin.")

# 14 Primary Studio Workspaces (Phase 2 Requirement)
nav_choice = st.sidebar.radio(
    "Navigation",
    [
        "1. Dashboard",
        "2. My Channel",
        "3. Channel Audit",
        "4. Content",
        "5. Shorts Studio",
        "6. Long-Form Studio",
        "7. Video Analysis",
        "8. SEO and Metadata",
        "9. Thumbnail Lab",
        "10. Competitor Research",
        "11. Analytics",
        "12. Publishing Planner",
        "13. AI Creator Assistant",
        "14. Settings",
    ],
)

st.sidebar.markdown("---")
# Quick Theme Switcher
theme_toggle = st.sidebar.selectbox("Theme", ["Dark", "Light"], index=0 if is_dark else 1)
if theme_toggle != st.session_state.theme_mode:
    st.session_state.theme_mode = theme_toggle
    db.set_setting("theme_mode", theme_toggle)
    st.rerun()

# ==============================================================================
# STUDIO TOPBAR: CHANNEL SELECTOR & DATA REFRESH
# ==============================================================================
top_col1, top_col2, top_col3 = st.columns([5, 2, 2])
with top_col1:
    if ch:
        cache_status = "⚠️ Cached Snapshot" if ch.get("is_cached") else "🟢 Live Data"
        st.markdown(
            f"**Channel:** {ch.get('title')} &nbsp;|&nbsp; **Source:** `{ch.get('data_source', 'Public')}` &nbsp;|&nbsp; **Status:** {cache_status}"
        )
    else:
        st.markdown("**Studio Status:** Ready • Connect a channel to unlock creator analytics.")
with top_col2:
    # Channel Switcher Dropdown
    recent_all = db.get_recent_channels(limit=10)
    if recent_all:
        ch_names = {c["title"]: c for c in recent_all}
        current_name = ch.get("title") if ch else list(ch_names.keys())[0]
        selected_name = st.selectbox("Switch Channel", list(ch_names.keys()), index=list(ch_names.keys()).index(current_name) if current_name in ch_names else 0, label_visibility="collapsed")
        if ch and selected_name != ch.get("title"):
            st.session_state.active_channel = ch_names[selected_name]
            st.session_state.active_audit = db.get_latest_channel_audit(ch_names[selected_name]["channel_id"])
            st.rerun()
with top_col3:
    if st.button("🔄 Refresh Data", use_container_width=True, help="Force fresh public scan and bypass cache"):
        if ch:
            with st.spinner("Fetching fresh data from YouTube..."):
                fresh_ch = yt_service.fetch_channel_data(ch["custom_url"] or ch["channel_id"], force_refresh=True)
                fresh_audit = yt_service.audit_channel(fresh_ch)
                db.save_channel(fresh_ch, is_cached=False)
                db.save_channel_audit(fresh_ch["channel_id"], fresh_audit["overall_score"], fresh_audit, fresh_audit.get("score_breakdown"))
                st.session_state.active_channel = fresh_ch
                st.session_state.active_audit = fresh_audit
                st.success("Channel data refreshed!")
                st.rerun()

st.markdown("---")

# ==============================================================================
# WORKSPACE 1: DASHBOARD
# ==============================================================================
if nav_choice == "1. Dashboard":
    st.markdown("## 📊 Channel Dashboard")
    st.caption("Real-time channel overview, recent performance, and key creator action items.")

    if not ch:
        st.info("Welcome to Studio! Enter a public YouTube channel link, handle, or ID below to generate your dashboard.")
        d_input = st.text_input("YouTube Channel Link / Handle", placeholder="e.g. @veritasium or https://youtube.com/@mkbhd")
        if st.button("Initialize Dashboard", type="primary") and d_input:
            with st.spinner("Scanning channel and compiling audit..."):
                new_ch = yt_service.fetch_channel_data(d_input, force_refresh=True)
                new_audit = yt_service.audit_channel(new_ch)
                db.save_channel(new_ch)
                db.save_channel_audit(new_ch["channel_id"], new_audit["overall_score"], new_audit, new_audit.get("score_breakdown"))
                st.session_state.active_channel = new_ch
                st.session_state.active_audit = new_audit
                st.rerun()
    else:
        audit = st.session_state.active_audit or yt_service.audit_channel(ch)

        # 4 Core Studio KPI Cards
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">Subscribers</div>
                    <div class="metric-val">{ch.get('subscriber_count_str', '0')}</div>
                    <div class="metric-sub">Public Count</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with k2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">Lifetime Views</div>
                    <div class="metric-val">{ch.get('view_count_str', '0')}</div>
                    <div class="metric-sub">{ch.get('video_count', 0)} Videos Published</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with k3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">Readiness Score</div>
                    <div class="metric-val">{audit.get('overall_score', 0)}/100</div>
                    <div class="metric-sub">Grade: {audit.get('grade', 'B')} (Documented)</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with k4:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">Format Balance</div>
                    <div class="metric-val">{ch.get('shorts_count', 0)}S / {ch.get('long_count', 0)}L</div>
                    <div class="metric-sub">Shorts vs Long-form</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        d_col1, d_col2 = st.columns([3, 2])
        with d_col1:
            st.markdown("### 🎬 Recent Uploads Performance")
            vids = ch.get("videos", [])
            if vids:
                df_vids = pd.DataFrame(vids)
                st.dataframe(
                    df_vids[["title", "duration_str", "is_short", "views", "likes", "published_at"]].rename(
                        columns={"title": "Title", "duration_str": "Duration", "is_short": "Is Short", "views": "Views", "likes": "Likes", "published_at": "Published"}
                    ),
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.write("No public videos available in this scan.")

        with d_col2:
            st.markdown("### ⚠️ Top Optimization Deductions")
            recs = audit.get("recommendations", [])
            if recs:
                for r in recs[:3]:
                    badge = "badge-high" if r["priority"] == "High" else "badge-med"
                    st.markdown(
                        f"""
                        <div style="background-color: {card_bg}; border: 1px solid {border_color}; padding: 12px; border-radius: 6px; margin-bottom: 10px;">
                            <span class="{badge}">{r['priority']}</span> <strong>{r['category']}</strong><br>
                            <span style="font-size: 0.85rem;">{r['what']}</span><br>
                            <small style="color: {text_sub};">Fix: {r['fix']}</small>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.success("No critical health issues detected.")

# ==============================================================================
# WORKSPACE 2: MY CHANNEL
# ==============================================================================
elif nav_choice == "2. My Channel":
    st.markdown("## 📺 Channel Overview & Identity")
    st.caption("Manage your connected channel profile, branding, and active metadata.")

    c_in1, c_in2 = st.columns([3, 1])
    with c_in1:
        new_channel_url = st.text_input("Scan / Switch Channel URL", value=ch.get("custom_url", "") if ch else "")
    with c_in2:
        st.write("")
        st.write("")
        if st.button("Scan Channel", type="primary", use_container_width=True) and new_channel_url:
            with st.spinner("Fetching channel..."):
                scanned = yt_service.fetch_channel_data(new_channel_url, force_refresh=True)
                audit_res = yt_service.audit_channel(scanned)
                db.save_channel(scanned)
                db.save_channel_audit(scanned["channel_id"], audit_res["overall_score"], audit_res, audit_res.get("score_breakdown"))
                st.session_state.active_channel = scanned
                st.session_state.active_audit = audit_res
                st.success("Channel connected!")
                st.rerun()

    if ch:
        st.markdown("---")
        h1, h2 = st.columns([1, 4])
        with h1:
            if ch.get("profile_image"):
                st.image(ch["profile_image"], width=130)
        with h2:
            st.markdown(f"### {ch.get('title')}")
            st.markdown(f"**Handle:** `{ch.get('custom_url')}` &nbsp;|&nbsp; **Channel ID:** `{ch.get('channel_id')}`")
            st.caption(f"Country: {ch.get('country', 'Unknown')} • Joined: {ch.get('published_at', '')[:10]}")

        st.markdown("#### Public Description")
        st.text_area("About Section", ch.get("description", ""), height=140, disabled=True)

# ==============================================================================
# WORKSPACE 3: CHANNEL AUDIT
# ==============================================================================
elif nav_choice == "3. Channel Audit":
    st.markdown("## 📋 Comprehensive Channel Health Audit")
    st.caption("10-pillar documented optimization audit. Every score deduction is justified with evidence.")

    if not ch:
        st.warning("Please scan a channel in Dashboard or My Channel to view its health audit.")
    else:
        audit = st.session_state.active_audit or yt_service.audit_channel(ch)
        score_bd = audit.get("score_breakdown", {})

        s1, s2, s3 = st.columns(3)
        s1.metric("Overall Optimization Score", f"{audit.get('overall_score', 0)}/100", f"Grade: {audit.get('grade', 'B')}")
        s2.metric("Metadata Completeness", f"{score_bd.get('metadata_completeness', {}).get('score', 0)}/100")
        s3.metric("Channel Consistency", f"{score_bd.get('channel_consistency', {}).get('score', 0)}/100")

        st.markdown("### 🔍 Documented Deductions & Recommendations")
        recs = audit.get("recommendations", [])
        if recs:
            for r in recs:
                badge = "badge-high" if r["priority"] == "High" else "badge-med" if r["priority"] == "Medium" else "badge-low"
                st.markdown(
                    f"""
                    <div style="background-color: {card_bg}; border-left: 4px solid #CC0000; border: 1px solid {border_color}; padding: 15px; border-radius: 6px; margin-bottom: 12px;">
                        <span class="{badge}">{r['priority']} Priority</span> &nbsp;<strong>{r['category']}</strong><br><br>
                        <strong>Issue:</strong> {r['what']}<br>
                        <em>Why it matters:</em> {r['why']}<br>
                        <em>Evidence:</em> {r['evidence']}<br>
                        <strong>How to Fix:</strong> {r['fix']}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.success("No health deductions found. Excellent metadata!")

# ==============================================================================
# WORKSPACE 4: CONTENT
# ==============================================================================
elif nav_choice == "4. Content":
    st.markdown("## 🎥 Channel Content Library")
    st.caption("Searchable, sortable video inventory with duration flags and engagement figures.")

    if not ch or not ch.get("videos"):
        st.info("No video uploads available for the active channel.")
    else:
        vids = ch["videos"]
        search_kw = st.text_input("🔍 Search Videos by Title or Tag", "")
        filtered = [v for v in vids if search_kw.lower() in v["title"].lower() or any(search_kw.lower() in t.lower() for t in v.get("tags", []))]

        st.markdown(f"**Showing {len(filtered)} of {len(vids)} observed uploads:**")
        cols = st.columns(3)
        for idx, v in enumerate(filtered):
            with cols[idx % 3]:
                if v.get("thumbnail"):
                    st.image(v["thumbnail"], use_container_width=True)
                tag = "📱 Short" if v.get("is_short") else "📺 Long"
                st.markdown(f"**{v['title'][:48]}...**")
                st.caption(f"{tag} • {v.get('duration_str')} • {v.get('views', 0):,} views • {v.get('likes', 0):,} likes")

# ==============================================================================
# WORKSPACE 5: SHORTS STUDIO
# ==============================================================================
elif nav_choice == "5. Shorts Studio":
    st.markdown("## 📱 YouTube Shorts Studio")
    st.caption("Tailored workspace for vertical mobile video (<60s, 9:16 aspect ratio, high-energy pacing).")

    sh_c1, sh_c2 = st.columns(2)
    with sh_c1:
        sh_topic = st.text_input("Short Topic", value="1 Simple Habit That Changed Everything")
        sh_niche = st.selectbox("Shorts Category", ["Productivity", "Tech & AI", "Finance", "Fitness", "Storytelling"])
    with sh_c2:
        sh_hook = st.text_area("Opening Spoken Hook (First 3-5 seconds)", value="Never upload your video before checking this 1 critical setting!")

    if st.button("Generate Shorts Blueprint", type="primary"):
        meta = meta_gen.generate_all(topic=sh_topic, niche=sh_niche, format_type="Shorts", transcript_snippet=sh_hook)
        st.markdown("---")
        st.markdown("### 5 High-Impact Shorts Titles")
        for idx, t in enumerate(meta["titles"]):
            t_col1, t_col2 = st.columns([4, 1])
            t_col1.write(f"**{idx+1}. {t['title']}** — *{t['formula']}*")
            t_col2.code(t["title"], language=None)

        st.markdown("### Copy-Ready Shorts Description")
        st.text_area("Shorts Description", meta["description"], height=110)

        st.markdown("### Suggested Hashtags")
        for h in meta["hashtags"]:
            st.write(f"• **{h['tag']}**: {h['relationship']}")

# ==============================================================================
# WORKSPACE 6: LONG-FORM STUDIO
# ==============================================================================
elif nav_choice == "6. Long-Form Studio":
    st.markdown("## 📺 Long-Form Video Studio")
    st.caption("Deep-dive optimization, structured chapters, pattern interrupts, and 8+ minute monetization checklists.")

    lf_c1, lf_c2 = st.columns(2)
    with lf_c1:
        lf_topic = st.text_input("Video Topic", value="Mastering System Architecture in 2026")
        lf_niche = st.text_input("Channel Niche", value="Software Engineering")
    with lf_c2:
        lf_dur = st.slider("Target Video Duration (minutes)", 5, 45, 12)
        lf_cta = st.selectbox("End-Screen Action", ["Subscribe for Masterclasses", "Watch Related Case Study Video", "Download Free Code Template"])

    if st.button("Generate Long-Form Masterclass Blueprint", type="primary"):
        meta = meta_gen.generate_all(topic=lf_topic, niche=lf_niche, format_type="Long-form")
        st.markdown("---")
        st.markdown("### 5 Search & Suggested Titles")
        for idx, t in enumerate(meta["titles"]):
            t_col1, t_col2 = st.columns([4, 1])
            t_col1.write(f"**{idx+1}. {t['title']}** &nbsp;*({t['char_count']} chars)*")
            t_col2.code(t["title"], language=None)

        st.markdown("### Chapterized Description")
        st.text_area("Full Description Template", meta["description"], height=180)

        st.markdown("### Comma-Separated Search Tags")
        st.code(meta["tags_comma_separated"], language=None)

# ==============================================================================
# WORKSPACE 7: VIDEO ANALYSIS
# ==============================================================================
elif nav_choice == "7. Video Analysis":
    st.markdown("## 🔬 Video File & Transcript Analysis")
    st.caption("Inspect local MP4/MOV container bytes, parse SRT/VTT subtitles, calculate speech rate WPM, and check opening hooks.")

    up_col1, up_col2 = st.columns(2)
    with up_col1:
        uploaded_video = st.file_uploader("Upload Video File (MP4, MOV)", type=["mp4", "mov"])
    with up_col2:
        uploaded_sub = st.file_uploader("Upload Subtitle File (.srt, .vtt) or text", type=["srt", "vtt", "txt"])

    raw_transcript_text = st.text_area("Or Paste Raw Audio Script / Transcript", height=100)

    if st.button("Analyze Video Content", type="primary"):
        if not uploaded_video and not raw_transcript_text and not uploaded_sub:
            st.warning("Please upload a video file or provide a transcript.")
        else:
            with st.spinner("Processing container atoms and calculating pacing metrics..."):
                sub_text = raw_transcript_text
                if uploaded_sub:
                    sub_parsed = video_analyzer.parse_subtitle_file(uploaded_sub.getvalue().decode("utf-8", errors="ignore"))
                    sub_text = sub_parsed["full_text"]

                raw_meta = {}
                if uploaded_video:
                    raw_meta = video_analyzer.inspect_video_file(uploaded_video.getvalue(), filename=uploaded_video.name)
                else:
                    raw_meta = {
                        "file_name": "Transcript_Only.txt",
                        "duration_sec": 300.0,
                        "duration_str": "5:00",
                        "resolution": "1920x1080",
                        "aspect_ratio": "16:9",
                        "format_type": "Widescreen",
                        "is_short": False,
                        "file_size_mb": 0,
                        "has_audio": True,
                        "bitrate_kbps": 0,
                        "audio_channels": 2,
                        "audio_sample_rate": 44100,
                        "observed_facts": {"estimated_frame_rate": 30.0},
                    }

                analysis_res = video_analyzer.analyze_content(
                    raw_meta,
                    transcript_text=sub_text,
                    topic_hint=uploaded_video.name if uploaded_video else "Video Subject",
                )

                # Save record to database
                db.save_video_analysis(
                    {
                        "channel_id": ch.get("channel_id") if ch else None,
                        "title": uploaded_video.name if uploaded_video else "Script Draft",
                        "source_type": "upload",
                        "file_name": uploaded_video.name if uploaded_video else "Script",
                        "file_size": raw_meta.get("file_size_bytes", 0),
                        "duration": raw_meta.get("duration_sec", 0),
                        "aspect_ratio": raw_meta.get("aspect_ratio", "16:9"),
                        "resolution": raw_meta.get("resolution", "1920x1080"),
                        "bitrate": raw_meta.get("bitrate_kbps", 0),
                        "audio_channels": raw_meta.get("audio_channels", 2),
                        "sample_rate": raw_meta.get("audio_sample_rate", 44100),
                        "hook_score": analysis_res["hook_score"],
                        "pacing_score": analysis_res["structure_score_info"]["score"],
                        "details": {"metadata": raw_meta, "content_eval": analysis_res},
                    },
                    channel_id=ch.get("channel_id") if ch else None,
                )
                st.session_state.active_video_analysis = {
                    "details": {"metadata": raw_meta, "content_eval": analysis_res},
                    "title": uploaded_video.name if uploaded_video else "Script Draft",
                }
                st.success("Video analysis completed!")

    if st.session_state.active_video_analysis:
        va = st.session_state.active_video_analysis["details"]
        meta = va["metadata"]
        content = va["content_eval"]

        st.markdown("---")
        # 1. Prominent Readiness Recommendation Banner
        rec_badge = content.get("readiness_recommendation", "NEEDS IMPROVEMENT")
        rec_color = content.get("readiness_color", "#FFA000")
        st.markdown(
            f"""
            <div style="background-color: {card_bg}; border: 2px solid {rec_color}; border-radius: 8px; padding: 18px; margin: 15px 0; text-align: center;">
                <span style="font-size: 0.85rem; font-weight: bold; color: {text_sub}; text-transform: uppercase; letter-spacing: 1px;">Pre-Upload Decision</span>
                <div style="font-size: 1.8rem; font-weight: 800; color: {rec_color}; margin: 5px 0;">{rec_badge}</div>
                <div style="font-size: 1.1rem; font-weight: 600;">Overall Video Readiness Score: {content.get('overall_score', 75)} / 100</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 2. Component Scores Breakdown
        st.markdown("### 📈 Supporting Component Scores")
        comp_scores = content.get("component_scores", {})
        cs1, cs2, cs3, cs4, cs5 = st.columns(5)
        cs1.metric("Technical Quality", f"{comp_scores.get('technical_quality', 80)}/100")
        cs2.metric("Opening Hook", f"{comp_scores.get('opening_hook', 75)}/100")
        cs3.metric("Pacing & Cadence", f"{comp_scores.get('pacing_cadence', 75)}/100")
        cs4.metric("Story Progression", f"{comp_scores.get('story_progression', 70)}/100")
        cs5.metric("Ending Payoff / CTA", f"{comp_scores.get('ending_payoff', 65)}/100")

        # 3. Verified Container Facts
        st.markdown("### 📊 Verified Video & Speech Facts")
        f1, f2, f3, f4 = st.columns(4)
        f1.metric("Duration", f"{meta.get('duration_str')} ({meta.get('duration_sec')}s)")
        f2.metric("Resolution", meta.get("resolution"))
        f3.metric("Aspect Ratio", meta.get("aspect_ratio"))
        f4.metric("Speech Rate", f"{content.get('words_per_minute')} WPM")

        # 4. Detected Problems with Exact Timestamps
        st.markdown("### ⚠️ Detected Editing Problems & Retention Lulls")
        detected_probs = content.get("detected_problems", [])
        if detected_probs:
            for prob in detected_probs:
                st.markdown(
                    f"""
                    <div style="background-color: {card_bg}; border-left: 4px solid #FF4E45; border: 1px solid {border_color}; padding: 12px; border-radius: 6px; margin-bottom: 8px;">
                        <span style="background-color: #3f1515; color: #ff8585; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 0.8rem;">⏱️ {prob.get('timestamp', 'Global')}</span>
                        &nbsp;<strong>{prob.get('component', 'Issue')}:</strong> {prob.get('issue')}<br>
                        <div style="margin-top: 4px; color: {text_sub};"><em>Practical Fix:</em> {prob.get('fix')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.success("✅ No critical retention drops, passive greetings, or pacing lulls detected.")

        # 5. Practical Editing Suggestions
        st.markdown("### 🛠️ Practical Editing Suggestions")
        for idx, sug in enumerate(content.get("editing_suggestions", [])):
            st.write(f"**{idx+1}.** {sug}")

        # 6. Pre-Upload Technical Checklist
        st.markdown("### ✅ Pre-Upload Technical Checklist")
        for chk in content.get("checklist", []):
            st.write(f"{'✅' if chk['passed'] else '⚠️'} **{chk['item']}**: {chk['detail']}")

# ==============================================================================
# WORKSPACE 8: SEO AND METADATA
# ==============================================================================
elif nav_choice == "8. SEO and Metadata":
    st.markdown("## 🏷️ SEO & Metadata Engine")
    st.caption("Generate compliant titles, descriptions, tags, and validate against YouTube's platform character limits.")

    sm_c1, sm_c2 = st.columns(2)
    with sm_c1:
        s_topic = st.text_input("Video Topic", value="YouTube Automation in 2026")
        s_niche = st.text_input("Channel Niche", value="Creator Economy")
        s_fmt = st.selectbox("Format", ["Long-form", "Shorts"])
    with sm_c2:
        s_aud = st.selectbox("Target Audience", ["General Audience", "Beginners", "Advanced Creators"])
        s_cntry = st.selectbox("Target Region", ["United States", "India", "United Kingdom", "Canada", "Australia"])

    if st.button("Generate & Validate Metadata", type="primary"):
        meta = meta_gen.generate_all(topic=s_topic, niche=s_niche, format_type=s_fmt, target_audience=s_aud, target_country=s_cntry)
        st.markdown("---")
        val = meta["validation"]
        if val["status"] == "PASSED":
            st.success("✅ All YouTube platform compliance checks passed!")
        else:
            st.warning(f"Status: {val['status']}")

        for w in val["warnings"]:
            st.warning(f"⚠️ {w}")

        st.markdown("### 5 Generated Title Options")
        for t in meta["titles"]:
            tc1, tc2 = st.columns([4, 1])
            tc1.write(f"**{t['title']}** — *{t['angle']}*")
            tc2.code(t["title"], language=None)

        st.markdown("### Full Description")
        st.text_area("Description", meta["description"], height=160)

        st.markdown("### Comma-Separated Tags")
        st.code(meta["tags_comma_separated"], language=None)

# ==============================================================================
# WORKSPACE 9: THUMBNAIL LAB
# ==============================================================================
elif nav_choice == "9. Thumbnail Lab":
    st.markdown("## 🖼️ Thumbnail Lab & Preview Studio")
    st.caption("Inspect thumbnail dimensions, file size, aspect ratios, and test high-contrast readability across YouTube feed mockups.")

    thumb_file = st.file_uploader("Upload Thumbnail Image (PNG, JPG, WEBP)", type=["png", "jpg", "jpeg", "webp"])
    mock_title = st.text_input("Overlay Title for Preview", value="Why Everyone Is Wrong About AI in 2026")

    if thumb_file:
        img = Image.open(thumb_file)
        w, h = img.size
        size_kb = int(len(thumb_file.getvalue()) / 1024)

        t_score = scoring_engine.score_thumbnail(
            has_thumbnail=True,
            dimensions=(w, h),
            file_size_kb=size_kb,
        )

        st.markdown("---")
        c1, c2 = st.columns([1, 1])
        with c1:
            st.image(img, use_container_width=True, caption=f"Uploaded Thumbnail: {w}x{h} ({size_kb} KB)")
        with c2:
            st.markdown("### 📏 Quality Inspection")
            st.metric("Thumbnail Score", f"{t_score['score']}/100", f"Confidence: {t_score['confidence']}")
            for d in t_score.get("deductions", []):
                st.write(f"⚠️ **{d['component']}**: {d['reason']}")
            if not t_score.get("deductions"):
                st.success("✅ Meets all 1280x720 16:9 YouTube requirements!")

        st.markdown("### 📱 YouTube Feed Mobile Card Preview")
        import base64
        b64_img = base64.b64encode(thumb_file.getvalue()).decode("utf-8")
        st.markdown(
            f"""
            <div style="max-width: 400px; background-color: {card_bg}; border: 1px solid {border_color}; border-radius: 8px; overflow: hidden; margin-top: 10px;">
                <img src="data:image/png;base64,{b64_img}" style="width: 100%; display: block;" onerror="this.src='https://via.placeholder.com/640x360';"/>
                <div style="padding: 10px;">
                    <div style="font-weight: bold; font-size: 0.95rem; margin-bottom: 4px;">{mock_title}</div>
                    <div style="font-size: 0.8rem; color: {text_sub};">Creator Channel • 140K views • 2 days ago</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("Upload a thumbnail image above to evaluate its technical dimensions and feed preview.")

# ==============================================================================
# WORKSPACE 10: COMPETITOR RESEARCH
# ==============================================================================
elif nav_choice == "10. Competitor Research":
    st.markdown("## 🔍 Competitor Research & Baseline Intelligence")
    st.caption("Deep-dive into specific competitor baselines, breakout outlier videos (>1.5x baseline), upload cadence, and testable strategies.")

    tab_single, tab_multi = st.tabs(["🎯 Specific Competitor Deep-Dive", "📊 Multi-Channel Benchmark"])

    with tab_single:
        st.markdown("### Analyze Any Specific Competitor Channel")
        st.caption("Paste a competitor URL or handle to calculate their median view baseline, breakout videos, upload schedule, and winning title keywords.")
        c_input1, c_input2 = st.columns([3, 1])
        with c_input1:
            single_comp_url = st.text_input("Competitor Channel URL / Handle", value="https://www.youtube.com/@veritasium", key="single_comp_in")
        with c_input2:
            st.write("")
            st.write("")
            btn_audit_comp = st.button("Audit Competitor", type="primary", use_container_width=True)

        if btn_audit_comp and single_comp_url:
            with st.spinner("Retrieving competitor video history and computing baseline..."):
                try:
                    single_audit = comp_service.analyze_single_competitor(single_comp_url)
                    st.session_state.single_competitor_audit = single_audit
                    st.success("Competitor analysis compiled!")
                except Exception as e:
                    st.error(f"Failed to analyze competitor: {str(e)}")

        if st.session_state.get("single_competitor_audit"):
            sa = st.session_state.single_competitor_audit
            if sa.get("has_data"):
                ch_c = sa["channel"]
                base = sa["baseline"]
                fmt = sa["format_analysis"]
                cad = sa["upload_cadence"]

                st.markdown("---")
                ch_col1, ch_col2 = st.columns([1, 4])
                with ch_col1:
                    if ch_c.get("profile_image"):
                        st.image(ch_c["profile_image"], width=100)
                with ch_col2:
                    st.markdown(f"### {ch_c.get('title')}")
                    st.markdown(f"**Handle:** `{ch_c.get('custom_url')}` &nbsp;|&nbsp; **Subscribers:** `{ch_c.get('subscriber_count_str')}` &nbsp;|&nbsp; **Source:** `{ch_c.get('data_source')}`")

                # Baseline KPI cards
                st.markdown("#### 📐 Historical Baseline Performance")
                k1, k2, k3, k4 = st.columns(4)
                k1.metric("Median Baseline Views", f"{base['median_views']:,}", help="Normal expected viewership per video")
                k2.metric("Mean Average Views", f"{base['mean_views']:,}")
                k3.metric("Upload Cadence", f"~{cad['videos_per_week']} vids/wk", cad['summary'])
                k4.metric("Format Winner", fmt['leading_format'], fmt['insight'])

                # Outlier Breakout Videos
                st.markdown("#### 🚀 Breakout Outlier Videos (> 1.5x Channel Baseline)")
                st.caption("Videos that dramatically exceeded the channel's normal viewership baseline:")
                if sa.get("breakout_videos"):
                    for bv in sa["breakout_videos"]:
                        st.markdown(
                            f"""
                            <div style="background-color: {card_bg}; border: 1px solid {border_color}; border-left: 4px solid #2BA640; border-radius: 6px; padding: 12px; margin-bottom: 8px;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="font-weight: bold; font-size: 1rem;">{bv['title']}</span>
                                    <span style="background-color: #1e3a1e; color: #4ade80; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 0.85rem;">{bv['baseline_multiplier']}x Baseline</span>
                                </div>
                                <div style="font-size: 0.85rem; color: {text_sub}; margin-top: 4px;">
                                    Views: <strong>{bv['views']:,}</strong> &nbsp;|&nbsp; Daily Velocity: <strong>{bv['views_per_day']:,} views/day</strong> &nbsp;|&nbsp; Format: <strong>{'Shorts' if bv['is_short'] else 'Long-form'}</strong> &nbsp;|&nbsp; Published: {bv['published_at']} ({bv['publishing_day']})
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                else:
                    st.info("No videos exceeding 1.5x median baseline in observed recent uploads.")

                # Underperforming Videos
                if sa.get("underperforming_videos"):
                    with st.expander("🔻 Underperforming Videos (< 0.6x Channel Baseline)"):
                        st.caption("Content topics that fell flat compared to the channel's standard view volume:")
                        for uv in sa["underperforming_videos"][:4]:
                            st.write(f"• **{uv['title']}** — {uv['views']:,} views *({uv['baseline_multiplier']}x baseline)*")

                # Keyword & Title Pattern Intelligence
                st.markdown("#### 🧠 Winning Title & Keyword Patterns")
                kw_intel = sa.get("keyword_intelligence", {})
                kw1, kw2 = st.columns(2)
                with kw1:
                    st.write("**Top Frequency Keywords in Breakouts:**")
                    if kw_intel.get("top_keywords"):
                        st.write(", ".join([f"`{k}`" for k in kw_intel["top_keywords"]]))
                    else:
                        st.write("Varied individual vocabulary")
                with kw2:
                    st.write("**Identified Title Structures:**")
                    for pat in kw_intel.get("recurring_patterns", []):
                        st.write(f"• {pat}")

                # Strategic Transfer Strategies
                st.markdown("#### 💡 Actionable Strategies to Test on Your Channel")
                st.caption("Distinguishing measured platform facts from creator hypotheses:")
                for strat in sa.get("transfer_strategies", []):
                    st.markdown(
                        f"""
                        <div style="background-color: {card_bg}; border: 1px solid {border_color}; border-left: 4px solid #8b5cf6; border-radius: 6px; padding: 14px; margin-bottom: 10px;">
                            <strong style="font-size: 1.05rem; color: #c4b5fd;">{strat['strategy_title']}</strong><br>
                            <div style="margin-top: 6px; font-size: 0.9rem;"><strong>[Measured Fact]</strong> {strat['evidence_measured_fact']}</div>
                            <div style="margin-top: 4px; font-size: 0.9rem; color: #d8b4fe;"><strong>[Creator Hypothesis]</strong> {strat['creator_hypothesis']}</div>
                            <div style="margin-top: 6px; padding: 8px; background-color: rgba(139, 92, 246, 0.1); border-radius: 4px; font-size: 0.9rem;">
                                🎯 <strong>[Actionable Test]</strong> {strat['actionable_test']}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.warning(sa.get("error", "No data accessible for this channel."))

    with tab_multi:
        st.markdown("### Multi-Competitor Velocity Benchmark")
        default_links = "https://www.youtube.com/@veritasium\nhttps://www.youtube.com/@mkbhd"
        comp_inputs = st.text_area("Competitor URLs / Handles (One per line)", value=default_links, height=85)

        if st.button("Run Multi-Channel Benchmark", type="primary"):
            lines = [line.strip() for line in comp_inputs.split("\n") if line.strip()]
            with st.spinner("Analyzing competitor channels..."):
                results = comp_service.analyze_competitors(lines)
                st.session_state.competitor_data = results
                for ch_comp in results.get("channels", []):
                    db.save_competitor({
                        "channel_id": ch_comp["channel_id"],
                        "channel_title": ch_comp["title"],
                        "handle": ch_comp["custom_url"],
                        "subscriber_count": ch_comp["subscriber_count"],
                        "video_count": ch_comp["video_count"],
                        "view_count": ch_comp["view_count"],
                        "raw_data": ch_comp,
                    })
                st.success("Competitor benchmark generated!")

        if st.session_state.competitor_data:
            cdata = st.session_state.competitor_data
            st.markdown("### 📊 Head-to-Head Comparison")
            if cdata.get("comparison_table"):
                st.dataframe(pd.DataFrame(cdata["comparison_table"])[["title", "handle", "subscribers", "observed_recent_videos", "median_views", "shorts_median", "long_median", "upload_frequency"]], use_container_width=True)

            st.markdown("### 🎯 Strategic Differentiation Opportunities")
            for opp in cdata.get("differentiation_opportunities", []):
                st.markdown(
                    f"""
                    <div style="background-color: {card_bg}; border-left: 4px solid #3EA6FF; border: 1px solid {border_color}; padding: 12px; border-radius: 6px; margin-bottom: 10px;">
                        <strong>{opp['theme']}</strong> ({opp['opportunity_level']} Opportunity)<br>
                        <em>Observation:</em> {opp['observation']}<br>
                        <strong>Actionable Strategy:</strong> {opp['actionable_takeaway']}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

# ==============================================================================
# WORKSPACE 11: ANALYTICS
# ==============================================================================
elif nav_choice == "11. Analytics":
    st.markdown("## 📈 Studio Analytics & Audience Retention")
    st.caption("Explore verified Studio metrics: CTR, viewer retention curves, and traffic source distribution.")

    tab_sample, tab_live = st.tabs(["📊 Studio Analytics Preview", "🔑 OAuth Connection Workflow"])
    with tab_sample:
        analytics = oauth_service.fetch_authorized_analytics("demo_token", days=28)
        m = analytics["metrics"]

        ak1, ak2, ak3, ak4 = st.columns(4)
        ak1.metric("28-Day Views", f"{m['total_views']:,}")
        ak2.metric("Watch Time", f"{m['total_watch_time_hours']:,} hrs")
        ak3.metric("Click-Through Rate", m["click_through_rate"])
        ak4.metric("Average Duration", m["average_view_duration_str"])

        df_t = pd.DataFrame(analytics["daily_trends"])
        fig_trend = px.line(df_t, x="date", y="views", title="Daily Views (Last 28 Days)", markers=True)
        st.plotly_chart(fig_trend, use_container_width=True)

        ts_col, ret_col = st.columns(2)
        with ts_col:
            df_ts = pd.DataFrame(analytics["traffic_sources"])
            fig_ts = px.pie(df_ts, values="percentage", names="source", hole=0.35, title="Traffic Sources Breakdown")
            st.plotly_chart(fig_ts, use_container_width=True)
        with ret_col:
            df_ret = pd.DataFrame(analytics["retention_curve"])
            fig_ret = px.area(df_ret, x="timestamp", y="retention", title="Audience Retention % Curve")
            st.plotly_chart(fig_ret, use_container_width=True)

    with tab_live:
        st.markdown("### Google Cloud OAuth2 Credentials")
        st.caption("Connect your personal Google Cloud Project to query official YouTube Analytics API endpoints.")
        c_id = st.text_input("OAuth Client ID", value=db.get_setting("google_client_id", ""))
        c_sec = st.text_input("OAuth Client Secret", type="password", value=db.get_setting("google_client_secret", ""))
        if st.button("Save OAuth Credentials"):
            db.set_setting("google_client_id", c_id)
            db.set_setting("google_client_secret", c_sec)
            st.success("Credentials saved to local settings.")

# ==============================================================================
# WORKSPACE 12: PUBLISHING PLANNER
# ==============================================================================
elif nav_choice == "12. Publishing Planner":
    st.markdown("## 📅 Publishing Planner & Release Calendar")
    st.caption("Plan upcoming content drops, assign format types, and coordinate optimal publishing windows.")

    pl_col1, pl_col2 = st.columns([1, 2])
    with pl_col1:
        st.markdown("### Schedule New Video")
        plan_title = st.text_input("Video Working Title", placeholder="e.g. 5 Mistakes in Video Editing")
        plan_fmt = st.selectbox("Format", ["Long-form", "Shorts", "Live Stream"])
        plan_date = st.date_input("Target Date", datetime.date.today())
        plan_time = st.time_input("Target Time", datetime.time(14, 0))
        plan_notes = st.text_input("Production Notes", placeholder="e.g. Include sponsor link in description")

        if st.button("Add to Publishing Queue", type="primary") and plan_title:
            db.save_publishing_task({
                "channel_id": ch.get("channel_id") if ch else None,
                "title": plan_title,
                "format_type": plan_fmt,
                "target_date": str(plan_date),
                "target_time": str(plan_time),
                "status": "Scheduled",
                "notes": plan_notes,
            })
            st.success("Added to publishing schedule!")
            st.rerun()

    with pl_col2:
        st.markdown("### Upcoming Release Schedule")
        tasks = db.get_publishing_tasks(channel_id=ch.get("channel_id") if ch else None)
        if tasks:
            for t in tasks:
                tc1, tc2 = st.columns([4, 1])
                tc1.markdown(f"**{t['title']}** ({t['format_type']}) • 🗓️ `{t['target_date']} at {t['target_time']}`")
                if t.get("notes"):
                    tc1.caption(f"Note: {t['notes']}")
                if tc2.button("Delete", key=f"del_task_{t['id']}"):
                    db.delete_publishing_task(t["id"])
                    st.rerun()
        else:
            st.info("No publishing tasks scheduled. Add your next video drop on the left.")

# ==============================================================================
# WORKSPACE 13: AI CREATOR ASSISTANT
# ==============================================================================
elif nav_choice == "13. AI Creator Assistant":
    st.markdown("## 🤖 Grounded AI Creator Assistant")
    st.caption("Conversational creator strategy grounded directly in your active channel, video drafts, and competitor data.")

    # Show Active Grounding Evidence
    st.markdown(
        f"""
        <div style="background-color: {card_bg}; border: 1px solid {border_color}; padding: 12px; border-radius: 6px; margin-bottom: 15px;">
            <strong>Active Grounding Context:</strong><br>
            • Channel: <code>{ch.get('title') if ch else 'None loaded'}</code><br>
            • Video Draft: <code>{st.session_state.active_video_analysis.get('title') if st.session_state.active_video_analysis else 'None loaded'}</code><br>
            • Competitors: <code>{len(st.session_state.competitor_data.get('channels', [])) if st.session_state.competitor_data else 0} tracked</code>
        </div>
        """,
        unsafe_allow_html=True,
    )

    q_cols = st.columns(4)
    q1 = q_cols[0].button("Why might views be low?")
    q2 = q_cols[1].button("What should I upload next?")
    q3 = q_cols[2].button("Recommend 3 title formulas")
    q4 = q_cols[3].button("What can I learn from competitors?")

    user_query = st.chat_input("Ask a question about your channel or video strategy...")
    if q1:
        user_query = "Why might this video be underperforming?"
    elif q2:
        user_query = "What should I upload next based on my niche and format balance?"
    elif q3:
        user_query = "What title best represents my video topic?"
    elif q4:
        user_query = "What can I learn from my competitors?"

    # Display History
    history = db.get_chat_history(st.session_state.chat_session_id)
    for msg in history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["message"])

    if user_query:
        with st.chat_message("user"):
            st.markdown(user_query)
        db.save_chat_message(st.session_state.chat_session_id, "user", user_query, channel_id=ch.get("channel_id") if ch else None)

        with st.spinner("Analyzing strategy..."):
            ans_payload = ai_service.answer_query(
                user_query,
                channel_data=ch,
                video_data=st.session_state.active_video_analysis,
                competitor_data=st.session_state.competitor_data,
                audit_data=st.session_state.active_audit,
            )
            reply = ans_payload["answer"]

        with st.chat_message("assistant"):
            st.caption(f"Powered by {ans_payload['mode']}")
            st.markdown(reply)

        db.save_chat_message(st.session_state.chat_session_id, "assistant", reply, channel_id=ch.get("channel_id") if ch else None)

    if st.sidebar.button("Clear Assistant Chat"):
        db.clear_chat_history(st.session_state.chat_session_id)
        st.rerun()

# ==============================================================================
# WORKSPACE 14: SETTINGS
# ==============================================================================
elif nav_choice == "14. Settings":
    st.markdown("## ⚙️ Studio Settings & API Configurations")
    st.caption("Configure optional API keys, region defaults, and manage local database storage.")

    set_c1, set_c2 = st.columns(2)
    with set_c1:
        st.markdown("### API Keys Configuration")
        yt_key = st.text_input("YouTube Data API v3 Key", value=db.get_setting("youtube_api_key", os.getenv("YOUTUBE_API_KEY", "")))
        gem_key = st.text_input("Google Gemini API Key", type="password", value=db.get_setting("gemini_api_key", os.getenv("GEMINI_API_KEY", "")))

        if st.button("Save API Keys"):
            db.set_setting("youtube_api_key", yt_key)
            db.set_setting("gemini_api_key", gem_key)
            st.success("API keys saved to local settings!")

    with set_c2:
        st.markdown("### Regional Defaults")
        def_cntry = st.selectbox("Default Target Region", ["United States", "India", "United Kingdom", "Canada", "Australia"])
        def_tz = st.selectbox("Default Timezone", ["Eastern Time (EST/EDT)", "Central Time (CST/CDT)", "Mountain Time (MST/MDT)", "Pacific Time (PST/PDT)"])

        if st.button("Save Regional Defaults"):
            db.set_setting("default_country", def_cntry)
            db.set_setting("default_timezone", def_tz)
            st.success("Regional defaults saved!")

    st.markdown("---")
    st.markdown("### 🗄️ Database Management")
    st.write(f"Database File: `{db.db_path}`")
    if st.button("Reset Session State"):
        st.session_state.active_channel = None
        st.session_state.active_audit = None
        st.session_state.active_video_analysis = None
        st.session_state.competitor_data = None
        st.success("Session state cleared.")
        st.rerun()

st.sidebar.caption("MY YOUTUBE CREATOR STUDIO • Local Offline First")
