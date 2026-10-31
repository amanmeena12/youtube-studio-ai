"""
Competitor Analysis Service for MY YOUTUBE CREATOR STUDIO.
Provides deep-dive intelligence for any specific competitor channel:
- Channel performance baseline (median views, mean views, range)
- Outlier breakout videos (> 1.5x baseline) vs underperformers (< 0.5x baseline)
- Content format success comparison (Shorts vs Long-form velocity)
- Upload schedule cadence (days between uploads, posting day distribution)
- Title patterns and keyword intelligence in breakout videos
- Actionable transfer strategies with explicit [Measured Fact] vs [Creator Hypothesis] separation.
"""

import datetime
import math
import statistics
from typing import Any, Dict, List, Optional
from .youtube_service import YouTubeService


class CompetitorService:
    def __init__(self, youtube_service: Optional[YouTubeService] = None):
        self.yt = youtube_service or YouTubeService()

    def analyze_single_competitor(
        self, channel_input: str, user_channel: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Performs an exhaustive, evidence-grounded audit of a single competitor channel.
        Distinguishes measured historical facts from strategic creator hypotheses.
        """
        ch = self.yt.fetch_channel_data(channel_input)
        videos = ch.get("videos", [])
        now = datetime.datetime.now()

        if not videos:
            return {
                "channel": ch,
                "error": "No public video uploads found or accessible for this channel.",
                "has_data": False,
            }

        # 1. Performance Baseline (Median, Mean, Min, Max)
        view_counts = [v.get("views", 0) for v in videos]
        median_views = int(statistics.median(view_counts)) if view_counts else 0
        mean_views = int(statistics.mean(view_counts)) if view_counts else 0
        max_views = max(view_counts) if view_counts else 0
        min_views = min(view_counts) if view_counts else 0

        # 2. Daily Velocity & Outlier Calculation
        enriched_videos = []
        breakout_videos = []
        underperforming_videos = []

        for v in videos:
            pub_date_str = v.get("published_at", "")
            days_old = 1.0
            day_name = "Unknown"
            if pub_date_str:
                try:
                    pub_dt = datetime.datetime.fromisoformat(pub_date_str.replace("Z", "+00:00"))
                    delta = (now.astimezone() - pub_dt).total_seconds() / 86400.0
                    days_old = max(0.5, delta)
                    day_name = pub_dt.strftime("%A")
                except Exception:
                    days_old = 1.0

            views = v.get("views", 0)
            views_per_day = round(views / days_old, 1)
            baseline_multiplier = round(views / max(1, median_views), 1)

            enriched = {
                "video_id": v.get("video_id", ""),
                "title": v.get("title", "Untitled Video"),
                "published_at": pub_date_str[:10],
                "publishing_day": day_name,
                "duration_str": v.get("duration_str", "0:00"),
                "duration_sec": v.get("duration_sec", 0),
                "is_short": v.get("is_short", False),
                "views": views,
                "likes": v.get("likes", 0),
                "comments": v.get("comments", 0),
                "days_published": round(days_old, 1),
                "views_per_day": views_per_day,
                "baseline_multiplier": baseline_multiplier,
                "thumbnail": v.get("thumbnail", ""),
            }
            enriched_videos.append(enriched)

            # Classify Breakout (> 1.5x baseline) vs Underperformer (< 0.5x baseline)
            if baseline_multiplier >= 1.5:
                breakout_videos.append(enriched)
            elif baseline_multiplier <= 0.6 and views > 0:
                underperforming_videos.append(enriched)

        # Sort breakout videos by views descending
        breakout_videos.sort(key=lambda x: x["views"], reverse=True)
        underperforming_videos.sort(key=lambda x: x["views"])

        # 3. Format Success Comparison (Shorts vs Long-form)
        shorts_list = [v for v in enriched_videos if v["is_short"]]
        long_list = [v for v in enriched_videos if not v["is_short"]]

        shorts_median = int(statistics.median([v["views"] for v in shorts_list])) if shorts_list else 0
        long_median = int(statistics.median([v["views"] for v in long_list])) if long_list else 0

        if shorts_median > 0 and long_median > 0:
            if shorts_median >= long_median:
                format_insight = f"Shorts outperform long-form on this channel by {round(shorts_median / max(1, long_median), 1)}x median views."
                leading_format = "Shorts"
            else:
                format_insight = f"Long-form outperforms Shorts on this channel by {round(long_median / max(1, shorts_median), 1)}x median views."
                leading_format = "Long-form"
        elif shorts_list and not long_list:
            format_insight = "Exclusively Shorts-focused channel."
            leading_format = "Shorts"
        else:
            format_insight = "Exclusively Long-form focused channel."
            leading_format = "Long-form"

        # 4. Upload Cadence & Scheduling Frequency
        parsed_dates = []
        day_counter: Dict[str, int] = {}
        for v in enriched_videos:
            if v["published_at"]:
                try:
                    dt = datetime.date.fromisoformat(v["published_at"])
                    parsed_dates.append(dt)
                    day_name = v.get("publishing_day", "Unknown")
                    day_counter[day_name] = day_counter.get(day_name, 0) + 1
                except Exception:
                    pass

        avg_days_between = 0.0
        videos_per_week = 0.0
        if len(parsed_dates) >= 2:
            parsed_dates.sort()
            total_span_days = (parsed_dates[-1] - parsed_dates[0]).days
            avg_days_between = round(total_span_days / max(1, len(parsed_dates) - 1), 1)
            videos_per_week = round(7.0 / max(0.5, avg_days_between), 1)

        most_active_day = max(day_counter.items(), key=lambda x: x[1])[0] if day_counter else "Varied"

        # 5. Title Patterns and Keywords in Top Performers
        stop_words = {
            "the", "a", "an", "in", "to", "for", "and", "of", "on", "is", "with",
            "this", "how", "what", "shorts", "your", "my", "from", "at", "by", "it"
        }
        word_freq: Dict[str, int] = {}
        top_subset = breakout_videos if breakout_videos else enriched_videos[:3]
        for v in top_subset:
            words = v["title"].lower().split()
            for w in words:
                clean_w = "".join(c for c in w if c.isalnum())
                if len(clean_w) > 3 and clean_w not in stop_words:
                    word_freq[clean_w] = word_freq.get(clean_w, 0) + 1

        top_keywords = [k for k, _ in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:6]]

        # Analyze structural title patterns in breakout videos
        question_titles = sum(1 for v in top_subset if "?" in v["title"])
        numbered_titles = sum(1 for v in top_subset if any(c.isdigit() for c in v["title"]))
        bracket_titles = sum(1 for v in top_subset if "[" in v["title"] or "(" in v["title"])

        title_patterns = []
        if question_titles > 0:
            title_patterns.append(f"Curiosity Questions ({question_titles} top video(s) use '?' to provoke intrigue)")
        if numbered_titles > 0:
            title_patterns.append(f"Numbered Lists / Metrics ({numbered_titles} top video(s) incorporate specific digits)")
        if bracket_titles > 0:
            title_patterns.append(f"Bracketed Context Tags ({bracket_titles} top video(s) frame value using [ ] or ( ))")

        # 6. Actionable Transfer Strategies for User's Channel
        transfer_strategies = []
        if breakout_videos:
            top_vid = breakout_videos[0]
            transfer_strategies.append({
                "strategy_title": f"Adapt Breakout Hook: '{top_vid['title'][:45]}...'",
                "evidence_measured_fact": (
                    f"Measured Fact: Competitor's video '{top_vid['title']}' generated {top_vid['views']:,} views "
                    f"({top_vid['baseline_multiplier']}x channel baseline of {median_views:,} views) at {top_vid['views_per_day']:,} views/day."
                ),
                "creator_hypothesis": (
                    "Creator Hypothesis: High baseline multiple indicates this specific topic angle pierced YouTube's "
                    "broader recommendation browse feed rather than relying solely on subscribers."
                ),
                "actionable_test": (
                    f"Actionable Test: Produce a video addressing the same underlying problem from your unique experience. "
                    f"Model the tension created in the first 25 characters of the title."
                ),
            })

        if top_keywords:
            kw_str = ", ".join([f"'{k}'" for k in top_keywords[:3]])
            transfer_strategies.append({
                "strategy_title": f"Target Keyword Cluster: {kw_str}",
                "evidence_measured_fact": (
                    f"Measured Fact: The keyword cluster [{kw_str}] appears across multiple top-performing uploads on this channel."
                ),
                "creator_hypothesis": (
                    "Creator Hypothesis: The audience actively clicks and watches content addressing these exact subject areas."
                ),
                "actionable_test": (
                    f"Actionable Test: Create a comprehensive beginner or advanced tutorial featuring {kw_str} in both your title and opening 15 seconds of dialogue."
                ),
            })

        transfer_strategies.append({
            "strategy_title": f"Format Optimization: {leading_format} Leverage",
            "evidence_measured_fact": (
                f"Measured Fact: {format_insight} (Shorts median: {shorts_median:,} vs Long-form median: {long_median:,})."
            ),
            "creator_hypothesis": (
                f"Creator Hypothesis: This niche's current viewer behavior heavily favors {leading_format.lower()} packaging."
            ),
            "actionable_test": (
                f"Actionable Test: Align your publishing schedule to include at least 1 high-effort {leading_format.lower()} piece weekly."
            ),
        })

        return {
            "channel": ch,
            "has_data": True,
            "baseline": {
                "median_views": median_views,
                "mean_views": mean_views,
                "max_views": max_views,
                "min_views": min_views,
                "total_observed_videos": len(videos),
                "total_observed_views": sum(view_counts),
            },
            "breakout_videos": breakout_videos,
            "underperforming_videos": underperforming_videos,
            "all_videos_ranked": enriched_videos,
            "format_analysis": {
                "shorts_count": len(shorts_list),
                "long_count": len(long_list),
                "shorts_median": shorts_median,
                "long_median": long_median,
                "leading_format": leading_format,
                "insight": format_insight,
            },
            "upload_cadence": {
                "avg_days_between": avg_days_between,
                "videos_per_week": videos_per_week,
                "most_active_day": most_active_day,
                "day_distribution": day_counter,
                "summary": (
                    f"Uploads approximately every {avg_days_between} days (~{videos_per_week} videos/week), "
                    f"most active on {most_active_day}s."
                    if avg_days_between > 0 else "Insufficient publication dates to establish upload cadence."
                ),
            },
            "keyword_intelligence": {
                "top_keywords": top_keywords,
                "recurring_patterns": title_patterns or ["Direct problem statement in title"],
            },
            "transfer_strategies": transfer_strategies,
        }

    def analyze_competitors(self, channel_inputs: List[str]) -> Dict[str, Any]:
        """
        Analyzes a batch of competitor channels for head-to-head comparison
        while retaining deep-dive statistics per competitor.
        """
        channels: List[Dict[str, Any]] = []
        deep_dives: Dict[str, Any] = []
        errors: List[str] = []

        for inp in channel_inputs:
            clean = inp.strip()
            if not clean:
                continue
            try:
                single_res = self.analyze_single_competitor(clean)
                if single_res.get("has_data"):
                    channels.append(single_res["channel"])
                    deep_dives.append(single_res)
                else:
                    errors.append(f"Channel '{clean}': {single_res.get('error', 'No data')}")
            except Exception as e:
                errors.append(f"Failed to scan '{clean}': {str(e)}")

        if not channels:
            return {
                "channels": [],
                "deep_dives": [],
                "errors": errors,
                "summary": "No competitor channels could be analyzed.",
                "all_videos_ranked": [],
                "differentiation_opportunities": [],
            }

        # Aggregate comparison table
        comparison_table = []
        all_videos = []

        for dive in deep_dives:
            ch = dive["channel"]
            baseline = dive["baseline"]
            fmt = dive["format_analysis"]
            cad = dive["upload_cadence"]

            comparison_table.append({
                "title": ch.get("title", ""),
                "handle": ch.get("custom_url", ""),
                "subscribers": ch.get("subscriber_count", 0),
                "subscribers_str": ch.get("subscriber_count_str", "0"),
                "total_videos": ch.get("video_count", 0),
                "observed_recent_videos": baseline["total_observed_videos"],
                "median_views": baseline["median_views"],
                "shorts_median": fmt["shorts_median"],
                "long_median": fmt["long_median"],
                "upload_frequency": cad["summary"],
                "profile_image": ch.get("profile_image", ""),
            })

            for v in dive["all_videos_ranked"]:
                v_copy = dict(v)
                v_copy["channel_title"] = ch.get("title", "")
                v_copy["channel_id"] = ch.get("channel_id", "")
                all_videos.append(v_copy)

        # Rank all videos by Views Per Day
        all_videos_ranked = sorted(all_videos, key=lambda x: x["views_per_day"], reverse=True)

        # Cross-channel opportunities
        opportunities = self._extract_cross_channel_opportunities(deep_dives)

        return {
            "channels": channels,
            "deep_dives": deep_dives,
            "comparison_table": comparison_table,
            "all_videos_ranked": all_videos_ranked,
            "differentiation_opportunities": opportunities,
            "errors": errors,
        }

    def _extract_cross_channel_opportunities(
        self, deep_dives: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        opportunities = []

        # Aggregate top keywords across all competitors
        all_keywords: Dict[str, int] = {}
        for dive in deep_dives:
            for kw in dive["keyword_intelligence"]["top_keywords"]:
                all_keywords[kw] = all_keywords.get(kw, 0) + 1

        frequent_kw = [k for k, cnt in all_keywords.items() if cnt >= 2]
        if frequent_kw:
            opportunities.append({
                "theme": f"Industry-Wide Demand Theme: {', '.join(frequent_kw[:3])}",
                "observation": f"Multiple competitors are seeing top velocity when addressing {', '.join(frequent_kw[:3])}.",
                "actionable_takeaway": "Build your own authoritative response piece that synthesizes the strengths and avoids the flaws of these competing uploads.",
                "opportunity_level": "High",
            })

        # Format voids
        total_shorts = sum(d["format_analysis"]["shorts_count"] for d in deep_dives)
        total_long = sum(d["format_analysis"]["long_count"] for d in deep_dives)
        total_all = total_shorts + total_long

        if total_all > 0:
            if (total_shorts / total_all) > 0.65:
                opportunities.append({
                    "theme": "Market Void: In-Depth Long-Form Authoritative Content",
                    "observation": f"Competitors are oversaturating the niche with quick Shorts ({int((total_shorts/total_all)*100)}% of uploads).",
                    "actionable_takeaway": "Differentiate with an exhaustive 12-18 minute masterclass with chapters, solving what their 45-second clips only skim.",
                    "opportunity_level": "High",
                })
            elif (total_long / total_all) > 0.8:
                opportunities.append({
                    "theme": "Discovery Void: Vertical Shorts Mobile Feed",
                    "observation": f"Competitors upload almost exclusively long-form ({int((total_long/total_all)*100)}%), neglecting mobile top-of-funnel reach.",
                    "actionable_takeaway": "Repurpose sharp 30-45s insights into high-energy Shorts to siphon mobile subscribers from this niche.",
                    "opportunity_level": "High",
                })

        return opportunities
