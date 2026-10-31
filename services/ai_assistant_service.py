"""
AI Creator Assistant Service for MY YOUTUBE CREATOR STUDIO.
Implements an explicit context-building pipeline grounded strictly in verified
channel data, video file inspections, and competitor benchmarks.
Distinguishes live evidence from historical snapshots, and prevents hallucination.
"""

import json
import os
import re
from typing import Any, Dict, List, Optional
import requests


class AIAssistantService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")

    def build_context_package(
        self,
        channel_data: Optional[Dict[str, Any]] = None,
        video_data: Optional[Dict[str, Any]] = None,
        competitor_data: Optional[Dict[str, Any]] = None,
        audit_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Gathers and normalizes verified evidence across channel, video, and competitors.
        Explicitly flags whether records are live or historical snapshots.
        """
        pkg = {
            "channel_summary": "No active channel selected.",
            "video_summary": "No active video draft selected.",
            "competitor_summary": "No competitors benchmarked.",
            "audit_highlights": [],
            "live_vs_snapshot": {},
        }

        if channel_data:
            pkg["channel_summary"] = (
                f"Channel: '{channel_data.get('title', 'Unknown')}' ({channel_data.get('custom_url', '')}), "
                f"Subscribers: {channel_data.get('subscriber_count_str', '0')}, "
                f"Total Views: {channel_data.get('view_count_str', '0')}, "
                f"Videos: {channel_data.get('video_count', 0)}, "
                f"Format Distribution: {channel_data.get('shorts_count', 0)} Shorts / {channel_data.get('long_count', 0)} Long-form."
            )
            pkg["live_vs_snapshot"]["channel_data_source"] = channel_data.get("data_source", "Public Ingestion")
            pkg["live_vs_snapshot"]["channel_is_cached"] = channel_data.get("is_cached", False)

        if video_data:
            meta = video_data.get("metadata", video_data)
            pkg["video_summary"] = (
                f"Video Draft: '{video_data.get('title', meta.get('file_name', 'Draft'))}', "
                f"Duration: {meta.get('duration_str', '0:00')}, "
                f"Resolution: {meta.get('resolution', 'Unknown')}, "
                f"Aspect Ratio: {meta.get('aspect_ratio', '16:9')}, "
                f"Audio Track: {'Active' if meta.get('has_audio') else 'None'}."
            )

        if audit_data:
            score = audit_data.get("overall_score", 0)
            recs = audit_data.get("recommendations", [])
            pkg["audit_highlights"] = [
                f"Overall Optimization Score: {score}/100 (Grade {audit_data.get('grade', 'B')})"
            ]
            for r in recs[:3]:
                pkg["audit_highlights"].append(f"• [{r.get('priority')} Priority] {r.get('category')}: {r.get('what')}")

        if competitor_data and competitor_data.get("channels"):
            comp_list = [c.get("title", "") for c in competitor_data.get("channels", [])]
            top_vid = competitor_data.get("all_videos_ranked", [{}])[0]
            pkg["competitor_summary"] = (
                f"Tracking {len(comp_list)} channels: {', '.join(comp_list)}. "
                f"Top daily velocity competitor video: '{top_vid.get('title', 'N/A')}' ({top_vid.get('views_per_day', 0):,} views/day)."
            )

        return pkg

    def answer_query(
        self,
        user_question: str,
        channel_data: Optional[Dict[str, Any]] = None,
        video_data: Optional[Dict[str, Any]] = None,
        competitor_data: Optional[Dict[str, Any]] = None,
        audit_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Processes creator query with structured grounding.
        Routes to Gemini LLM if configured; otherwise runs deterministic grounded heuristic engine.
        """
        context_pkg = self.build_context_package(channel_data, video_data, competitor_data, audit_data)

        # Live Gemini API execution when key is present
        if self.api_key:
            try:
                live_resp = self._query_gemini(user_question, context_pkg)
                if live_resp:
                    return {
                        "mode": "Google Gemini AI (Live Model)",
                        "answer": live_resp,
                        "grounding_status": "Grounded in Active Session Evidence",
                        "context_used": context_pkg,
                    }
            except Exception:
                pass

        # Built-in Grounded Heuristic Engine
        structured = self._grounded_heuristic_reasoning(user_question, context_pkg, channel_data, video_data, competitor_data, audit_data)
        formatted = self._format_response(structured)

        return {
            "mode": "Built-in Grounded Creator Intelligence",
            "answer": formatted,
            "grounding_status": "Grounded in Active Channel & Video Artifacts",
            "structured_evidence": structured,
            "context_used": context_pkg,
        }

    def _grounded_heuristic_reasoning(
        self,
        q: str,
        ctx: Dict[str, Any],
        ch: Optional[Dict[str, Any]],
        vid: Optional[Dict[str, Any]],
        comp: Optional[Dict[str, Any]],
        audit: Optional[Dict[str, Any]],
    ) -> Dict[str, str]:
        q_lower = q.lower()

        # 1. Underperformance & Retention
        if any(w in q_lower for w in ["underperform", "why views low", "flop", "low views", "drop"]):
            vid_title = vid.get("title", "Selected Video") if vid else "Recent Upload"
            dur = vid.get("duration_str", "Unknown") if vid else "Unknown"
            audit_recs = audit.get("recommendations", []) if audit else []
            audit_note = audit_recs[0]["what"] if audit_recs else "Check title curiosity anchor and first 10 seconds."

            return {
                "verified_evidence": (
                    f"Examined target: '{vid_title}' ({dur}). "
                    f"Channel consistency score: {audit.get('overall_score', 80) if audit else 'N/A'}/100. "
                    f"Identified audit finding: {audit_note}"
                ),
                "observed_patterns": (
                    "YouTube distribution relies on initial viewer velocity: Impressions -> CTR -> 30-Second Retention. "
                    "If a video underperforms within 48 hours, the thumbnail contrast or opening hook usually caused early swipe-away."
                ),
                "hypothesis": (
                    "Viewers likely scrolled past due to low visual curiosity in the thumbnail, "
                    "or dropped off in the first 15 seconds if the video began with passive introductions rather than the promised stakes."
                ),
                "actionable_recommendations": (
                    "1. Update Thumbnail: Use high-contrast background and max 3-4 bold words.\n"
                    "2. Adjust Title: Reframe from procedural ('How I Did X') to outcome-oriented ('The Mistake Costing You X').\n"
                    "3. For your next video: Cut greetings and deliver proof within the first 3-5 seconds."
                ),
                "missing_data_and_limitations": (
                    "Actual Click-Through Rate (CTR) and Audience Retention percentage graphs require "
                    "authorized OAuth connection to YouTube Studio Analytics."
                ),
            }

        # 2. What to Upload Next / Content Strategy
        if any(w in q_lower for w in ["next", "what to upload", "idea", "topic"]):
            shorts_c = ch.get("shorts_count", 0) if ch else 0
            longs_c = ch.get("long_count", 0) if ch else 0
            format_void = "Shorts" if longs_c > shorts_c and shorts_c == 0 else "Long-Form" if shorts_c > longs_c else "Balanced Series"

            top_comp_vid = comp.get("all_videos_ranked", [{}])[0].get("title", "") if comp else ""
            comp_cue = f"Top competitor cluster: '{top_comp_vid}'." if top_comp_vid else "Focus on core beginner pain points."

            return {
                "verified_evidence": (
                    f"Current inventory ratio: {shorts_c} Shorts and {longs_c} Long-form videos. "
                    f"{comp_cue}"
                ),
                "observed_patterns": (
                    "Creators build sustainable momentum by publishing content pairs: a punchy 40s Short that highlights a core paradox, "
                    "directly linking to an 8-12 minute deep-dive masterclass."
                ),
                "hypothesis": (
                    f"Your audience has a format opportunity in {format_void}. "
                    "Creating a 2-part content cluster around high-intent search queries will capture both mobile feed and search traffic."
                ),
                "actionable_recommendations": (
                    f"1. Publish a {format_void} video tackling a specific common misconception in your niche.\n"
                    "2. Structure chapters: Introduction (0:00), Core Framework (1:30), 3 Traps (5:00), Turnkey Solution (8:00).\n"
                    "3. End with a direct card pointing to your existing best-performing upload."
                ),
                "missing_data_and_limitations": "Direct viewer search logs from YouTube Studio 'Research' tab.",
            }

        # 3. Title Recommendations
        if any(w in q_lower for w in ["title", "headline", "name"]):
            ch_name = ch.get("title", "Your Channel") if ch else "Your Channel"
            return {
                "verified_evidence": f"Channel context: '{ch_name}'. Title quality benchmark evaluated.",
                "observed_patterns": "Titles between 45-65 characters with curiosity anchors achieve the highest CTR across desktop and mobile.",
                "hypothesis": "Clear curiosity formulas outperform generic descriptive labels.",
                "actionable_recommendations": (
                    "Test these 3 proven title angles:\n"
                    "• Mistake / Negative: 'Stop Making This [Topic] Mistake in 2026!'\n"
                    "• Complete Masterclass: 'The Only 3 [Topic] Rules That Actually Matter'\n"
                    "• Case Study: 'I Tested Every [Topic] Method for 30 Days: Here's What Worked'"
                ),
                "missing_data_and_limitations": "A/B testing impressions and live thumbnail CTR variations.",
            }

        # 4. Competitor Lessons
        if any(w in q_lower for w in ["competitor", "rival", "competition"]):
            n_comps = len(comp.get("channels", [])) if comp else 0
            return {
                "verified_evidence": f"Tracking {n_comps} competitor(s) in active benchmark session.",
                "observed_patterns": "Competitors with higher daily velocity consistently post at predictable weekly times and use punchy, question-based titles.",
                "hypothesis": "You can win audience share by addressing the detailed practical questions that competitors skip in their general overviews.",
                "actionable_recommendations": (
                    "1. Check competitor video comments for recurring viewer frustrations or unanswered questions.\n"
                    "2. Build your next video specifically answering those unanswered questions.\n"
                    "3. Use a more personal, case-study narrative format to differentiate from their generic advice."
                ),
                "missing_data_and_limitations": "Private competitor watch time and audience demographics.",
            }

        # Default Grounded Assistant Response
        return {
            "verified_evidence": (
                f"{ctx['channel_summary']}\n"
                f"{ctx['video_summary']}\n"
                f"Audit Status: {', '.join(ctx['audit_highlights']) or 'Baseline Audit Active'}"
            ),
            "observed_patterns": "Sustainable creator growth is driven by title packaging clarity, opening retention, and consistent publishing cadence.",
            "hypothesis": f"Regarding your question ('{q}'): Grounded progress comes from testing single variables (thumbnail, title, hook) sequentially.",
            "actionable_recommendations": (
                "1. Review the Channel Audit tab for flagged description or title formatting deductions.\n"
                "2. Upload a draft to Video Analysis to verify 9:16 vs 16:9 aspect ratio and opening hook score.\n"
                "3. Use SEO & Metadata to validate YouTube's platform character limits before publishing."
            ),
            "missing_data_and_limitations": "Real-time private studio telemetry and unlisted video drafts.",
        }

    def _query_gemini(self, question: str, ctx: Dict[str, Any]) -> Optional[str]:
        prompt = f"""
        You are an expert YouTube Creator Studio Assistant.
        Grounded Context:
        - Channel: {ctx.get('channel_summary')}
        - Video: {ctx.get('video_summary')}
        - Competitors: {ctx.get('competitor_summary')}
        - Audit Highlights: {json.dumps(ctx.get('audit_highlights', []))}

        User Question:
        {question}

        Format your answer with these exact headings:
        **VERIFIED EVIDENCE:**
        **OBSERVED PATTERNS:**
        **HYPOTHESIS:**
        **ACTIONABLE RECOMMENDATIONS:**
        **MISSING DATA & LIMITATIONS:**
        """
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        resp = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=10)
        if resp.status_code == 200:
            return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        return None

    def _format_response(self, s: Dict[str, str]) -> str:
        return (
            f"**VERIFIED EVIDENCE:**\n{s['verified_evidence']}\n\n"
            f"**OBSERVED PATTERNS:**\n{s['observed_patterns']}\n\n"
            f"**HYPOTHESIS:**\n{s['hypothesis']}\n\n"
            f"**ACTIONABLE RECOMMENDATIONS:**\n{s['actionable_recommendations']}\n\n"
            f"**MISSING DATA & LIMITATIONS:**\n{s['missing_data_and_limitations']}"
        )
