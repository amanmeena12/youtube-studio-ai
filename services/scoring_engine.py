"""
Scoring Engine for MY YOUTUBE CREATOR STUDIO.
Implements 10 distinct, documented, evidence-based optimization scores.
Distinguishes between poor performance and missing data ("Insufficient Data"),
returns explicit component formulas, weights, evidence deductions, and confidence ratings.
"""

import math
import re
from typing import Any, Dict, List, Optional, Tuple


class ScoringEngine:
    # Defined Component Weights for Overall Optimization Readiness Score (Sum = 1.0)
    WEIGHTS = {
        "metadata_completeness": 0.15,
        "title_quality": 0.20,
        "description_quality": 0.15,
        "tag_relevance": 0.10,
        "hashtag_relevance": 0.05,
        "thumbnail_quality": 0.10,
        "content_structure": 0.10,
        "channel_consistency": 0.10,
        "data_completeness": 0.05,
    }

    def __init__(self):
        pass

    # 1. Metadata Completeness Score (0 - 100)
    def score_metadata_completeness(
        self,
        title: str,
        description: str,
        tags: List[str],
        category_id: Optional[str] = None,
        has_thumbnail: bool = False,
    ) -> Dict[str, Any]:
        """
        Formula:
          Score = (w_title * S_title) + (w_desc * S_desc) + (w_tags * S_tags) + (w_cat * S_cat) + (w_thumb * S_thumb)
          Weights: Title (30%), Desc (30%), Tags (20%), Category (10%), Thumbnail (10%)
        """
        deductions = []
        components = {}

        # Title presence & length (0 - 30)
        t_len = len(title.strip()) if title else 0
        if t_len == 0:
            s_title = 0
            deductions.append({"component": "Title", "deduction": 30, "reason": "Title is completely missing."})
        elif t_len > 100:
            s_title = 10
            deductions.append({"component": "Title", "deduction": 20, "reason": f"Title exceeds platform 100-character limit ({t_len} chars)."})
        elif 35 <= t_len <= 75:
            s_title = 30
        else:
            s_title = 20
            deductions.append({"component": "Title", "deduction": 10, "reason": f"Title length ({t_len} chars) is outside optimal range (35-75)."})
        components["title_score"] = s_title

        # Description presence (0 - 30)
        d_len = len(description.strip()) if description else 0
        if d_len == 0:
            s_desc = 0
            deductions.append({"component": "Description", "deduction": 30, "reason": "Description is completely empty."})
        elif d_len < 100:
            s_desc = 10
            deductions.append({"component": "Description", "deduction": 20, "reason": f"Description is very brief ({d_len} chars); min 100 recommended."})
        elif d_len > 5000:
            s_desc = 5
            deductions.append({"component": "Description", "deduction": 25, "reason": f"Description exceeds platform 5,000-character limit ({d_len} chars)."})
        else:
            s_desc = 30
        components["description_score"] = s_desc

        # Tags presence (0 - 20)
        tag_count = len(tags) if tags else 0
        if tag_count == 0:
            s_tags = 0
            deductions.append({"component": "Tags", "deduction": 20, "reason": "No tags provided."})
        elif tag_count < 3:
            s_tags = 10
            deductions.append({"component": "Tags", "deduction": 10, "reason": f"Only {tag_count} tag(s) listed; 5-15 recommended."})
        else:
            s_tags = 20
        components["tags_score"] = s_tags

        # Category presence (0 - 10)
        if category_id and str(category_id) not in ("0", ""):
            s_cat = 10
        else:
            s_cat = 0
            deductions.append({"component": "Category", "deduction": 10, "reason": "Category ID is unassigned."})
        components["category_score"] = s_cat

        # Thumbnail presence (0 - 10)
        s_thumb = 10 if has_thumbnail else 0
        if not has_thumbnail:
            deductions.append({"component": "Thumbnail", "deduction": 10, "reason": "Custom thumbnail image not attached."})
        components["thumbnail_presence_score"] = s_thumb

        total = s_title + s_desc + s_tags + s_cat + s_thumb
        return {
            "score": total,
            "status": "Calculated",
            "components": components,
            "deductions": deductions,
            "formula": "Weighted sum of Title (30%), Description (30%), Tags (20%), Category (10%), Thumbnail (10%)",
            "confidence": "High (Direct Metadata Verification)",
        }

    # 2. Title Relevance & Clarity Score (0 - 100)
    def score_title_quality(self, title: str, topic_context: str = "") -> Dict[str, Any]:
        """
        Formula:
          Score = Base (40) + Length_Fit (20) + Curiosity/Hook (20) + Readability/Case (20) - Spam_Penalties
        """
        if not title or not title.strip():
            return {
                "score": 0,
                "status": "Insufficient Data",
                "components": {},
                "deductions": [{"component": "Title", "deduction": 100, "reason": "No title provided to evaluate."}],
                "formula": "Length fit (20) + Curiosity trigger (20) + Readability (20) + Baseline (40)",
                "confidence": "None",
            }

        t = title.strip()
        t_len = len(t)
        deductions = []
        score = 40  # Baseline

        # 1. Optimal Length (45 - 65 chars is highest desktop/mobile sweet spot)
        if 40 <= t_len <= 70:
            score += 20
        elif 25 <= t_len < 40 or 70 < t_len <= 85:
            score += 10
            deductions.append({"component": "Length", "deduction": 10, "reason": f"Title is {t_len} characters. Ideal length is 40-70 characters."})
        else:
            deductions.append({"component": "Length", "deduction": 20, "reason": f"Title is {t_len} characters. Too short or prone to mobile truncation."})

        # 2. Curiosity / Intrigue Anchor Words
        hooks = ["why", "how to", "never", "secret", "truth", "tested", "blueprint", "mistake", "stop", "before you", "rules"]
        found_hooks = [h for h in hooks if re.search(rf"\b{h}\b", t.lower())]
        if found_hooks:
            score += 20
        elif "?" in t:
            score += 15
        else:
            score += 5
            deductions.append({"component": "Curiosity Trigger", "deduction": 15, "reason": "Lacks an intrigue anchor, emotional hook, or question mark."})

        # 3. Readability & Casing
        if t.isupper() and t_len > 15:
            score -= 15
            deductions.append({"component": "Spam / Formatting", "deduction": 15, "reason": "Entire title is in ALL CAPS. Damages trust and readability."})
        else:
            score += 20

        # 4. Keyword consistency with topic
        if topic_context:
            topic_words = [w.lower() for w in topic_context.split() if len(w) > 3]
            matches = [w for w in topic_words if w in t.lower()]
            if not matches and topic_words:
                score -= 10
                deductions.append({"component": "Relevance", "deduction": 10, "reason": f"Title lacks stated topic keywords: {', '.join(topic_words[:3])}."})

        final_score = max(10, min(100, score))
        return {
            "score": final_score,
            "status": "Calculated",
            "components": {"length_chars": t_len, "hooks_found": found_hooks},
            "deductions": deductions,
            "formula": "Baseline (40) + Length sweet spot (20) + Curiosity anchor (20) + Casing/Readability (20) - Keyword mismatch",
            "confidence": "High",
        }

    # 3. Description Quality Score (0 - 100)
    def score_description_quality(self, description: str, has_timestamps: bool = False) -> Dict[str, Any]:
        """
        Formula:
          Score = Length_Bracket (40) + Links_CTA (20) + Timestamps_Chapters (20) + Formatting_Paragraphs (20)
        """
        if not description or not description.strip():
            return {
                "score": 0,
                "status": "Insufficient Data",
                "components": {},
                "deductions": [{"component": "Description", "deduction": 100, "reason": "Description is empty."}],
                "formula": "Length bracket (40) + Outbound links (20) + Chapters (20) + Paragraphs (20)",
                "confidence": "None",
            }

        desc = description.strip()
        d_len = len(desc)
        score = 0
        deductions = []

        # Length bracket (0 - 40)
        if d_len >= 500:
            score += 40
        elif d_len >= 250:
            score += 25
            deductions.append({"component": "Length", "deduction": 15, "reason": f"Description is moderate ({d_len} chars); 500+ recommended for search."})
        elif d_len >= 100:
            score += 15
            deductions.append({"component": "Length", "deduction": 25, "reason": f"Description is short ({d_len} chars); missing search indexing depth."})
        else:
            score += 5
            deductions.append({"component": "Length", "deduction": 35, "reason": f"Description is extremely brief ({d_len} chars)."})

        # Links & CTAs (0 - 20)
        if "http://" in desc or "https://" in desc:
            score += 20
        else:
            deductions.append({"component": "Links / CTAs", "deduction": 20, "reason": "No links found for social media, resources, or community."})

        # Timestamps / Chapters (0 - 20)
        timestamp_regex = r"\b\d{1,2}:\d{2}\b"
        found_timestamps = re.findall(timestamp_regex, desc)
        if len(found_timestamps) >= 3 or has_timestamps:
            score += 20
        elif len(found_timestamps) >= 1:
            score += 10
            deductions.append({"component": "Timestamps", "deduction": 10, "reason": "Only 1-2 timestamps found; at least 3 chapters recommended for YouTube chapterization."})
        else:
            deductions.append({"component": "Timestamps", "deduction": 20, "reason": "No timestamps / chapter markers detected in description."})

        # Paragraph structure (0 - 20)
        paragraphs = [p for p in desc.split("\n\n") if p.strip()]
        if len(paragraphs) >= 3:
            score += 20
        elif len(paragraphs) >= 2:
            score += 10
            deductions.append({"component": "Structure", "deduction": 10, "reason": "Description lacks visual section breaks or headers."})
        else:
            deductions.append({"component": "Structure", "deduction": 20, "reason": "Description is a single unformatted wall of text."})

        final_score = max(5, min(100, score))
        return {
            "score": final_score,
            "status": "Calculated",
            "components": {"char_count": d_len, "timestamp_count": len(found_timestamps), "paragraphs": len(paragraphs)},
            "deductions": deductions,
            "formula": "Depth/Length (40) + Outbound links (20) + Chapters (20) + Layout/Paragraphs (20)",
            "confidence": "High",
        }

    # 4. Tag Relevance Score (0 - 100)
    def score_tags(self, tags: List[str], topic: str = "") -> Dict[str, Any]:
        """
        Formula:
          Score = Count_Rating (40) + Length_Budget (30) + Niche_Relevance (30)
        """
        if not tags:
            return {
                "score": 0,
                "status": "Insufficient Data",
                "components": {},
                "deductions": [{"component": "Tags", "deduction": 100, "reason": "No tags provided."}],
                "formula": "Tag count (40) + Total character budget (30) + Specificity & Topic match (30)",
                "confidence": "None",
            }

        count = len(tags)
        total_chars = sum(len(t) for t in tags) + len(tags)
        score = 0
        deductions = []

        # Count rating (0 - 40)
        if 8 <= count <= 20:
            score += 40
        elif 4 <= count < 8:
            score += 25
            deductions.append({"component": "Tag Count", "deduction": 15, "reason": f"{count} tags provided; 8-20 recommended for full coverage."})
        elif count > 20:
            score += 30
            deductions.append({"component": "Tag Count", "deduction": 10, "reason": f"{count} tags is high; avoid diluted search relevance."})
        else:
            score += 10
            deductions.append({"component": "Tag Count", "deduction": 30, "reason": f"Only {count} tag(s); insufficient topic coverage."})

        # Total characters (0 - 30, YouTube limit is 500)
        if total_chars > 500:
            score += 0
            deductions.append({"component": "Character Limit", "deduction": 30, "reason": f"Total tag characters ({total_chars}) exceeds YouTube's 500-char limit."})
        elif 200 <= total_chars <= 480:
            score += 30
        else:
            score += 15
            deductions.append({"component": "Character Budget", "deduction": 15, "reason": f"Total tag characters ({total_chars}/500) leaves substantial unused indexing space."})

        # Topic match (0 - 30)
        if topic:
            t_words = [w.lower() for w in topic.split() if len(w) > 3]
            matched = any(any(tw in tag.lower() for tw in t_words) for tag in tags)
            if matched:
                score += 30
            else:
                score += 10
                deductions.append({"component": "Relevance", "deduction": 20, "reason": "Tags do not contain core keywords from the video topic."})
        else:
            score += 20

        final_score = max(10, min(100, score))
        return {
            "score": final_score,
            "status": "Calculated",
            "components": {"tag_count": count, "total_characters": total_chars},
            "deductions": deductions,
            "formula": "Count rating (40) + Total character usage (30) + Topic keyword match (30)",
            "confidence": "High",
        }

    # 5. Hashtag Relevance Score (0 - 100)
    def score_hashtags(self, hashtags: List[str]) -> Dict[str, Any]:
        """
        Formula:
          Score = Count_Rating (60) + Format_Validation (40)
        """
        if not hashtags:
            return {
                "score": 0,
                "status": "Insufficient Data",
                "components": {},
                "deductions": [{"component": "Hashtags", "deduction": 100, "reason": "No hashtags provided."}],
                "formula": "Optimal count 3-5 (60) + Formatting without special characters (40)",
                "confidence": "None",
            }

        count = len(hashtags)
        score = 0
        deductions = []

        # Count (3 - 5 is optimal above title)
        if 3 <= count <= 5:
            score += 60
        elif 1 <= count < 3:
            score += 40
            deductions.append({"component": "Hashtag Count", "deduction": 20, "reason": f"{count} hashtag(s); 3-5 is the recommended YouTube standard."})
        elif 5 < count <= 15:
            score += 35
            deductions.append({"component": "Hashtag Count", "deduction": 25, "reason": f"{count} hashtags; YouTube only displays the first 3 above title."})
        else:
            score += 10
            deductions.append({"component": "Hashtag Count", "deduction": 50, "reason": f"{count} hashtags is excessive (>15 risks platform spam penalty)."})

        # Formatting validation
        invalid = [h for h in hashtags if not h.startswith("#") or len(h) < 2 or " " in h]
        if not invalid:
            score += 40
        else:
            score += 15
            deductions.append({"component": "Formatting", "deduction": 25, "reason": f"Invalid hashtags detected (spaces or missing #): {', '.join(invalid[:2])}."})

        final_score = max(10, min(100, score))
        return {
            "score": final_score,
            "status": "Calculated",
            "components": {"hashtag_count": count},
            "deductions": deductions,
            "formula": "Count sweet spot 3-5 (60) + Valid hashtag syntax (40)",
            "confidence": "High",
        }

    # 6. Thumbnail Quality Score (0 - 100, ONLY calculated if thumbnail exists)
    def score_thumbnail(
        self,
        has_thumbnail: bool,
        dimensions: Optional[Tuple[int, int]] = None,
        file_size_kb: Optional[int] = None,
        aspect_ratio: str = "16:9",
    ) -> Dict[str, Any]:
        """
        Formula:
          Score = Dimension_Check (40) + Aspect_Ratio (30) + File_Size_Check (30)
          CRITICAL REQUIREMENT: Returns 'Insufficient Data' if thumbnail was not inspected!
        """
        if not has_thumbnail or not dimensions:
            return {
                "score": None,
                "status": "Insufficient Data",
                "components": {},
                "deductions": [{"component": "Thumbnail Image", "deduction": 0, "reason": "No thumbnail file or inspected image stream available to analyze."}],
                "formula": "Standard 1280x720 (40) + 16:9 ratio (30) + Under 2MB file size (30)",
                "confidence": "None (Thumbnail was not inspected)",
            }

        w, h = dimensions
        score = 0
        deductions = []

        # Resolution check (YouTube standard: 1280x720 min 640x360)
        if w >= 1280 and h >= 720:
            score += 40
        elif w >= 640 and h >= 360:
            score += 25
            deductions.append({"component": "Resolution", "deduction": 15, "reason": f"Resolution ({w}x{h}) is below YouTube recommended 1280x720 HD standard."})
        else:
            score += 10
            deductions.append({"component": "Resolution", "deduction": 30, "reason": f"Resolution ({w}x{h}) is too low; thumbnail will appear pixelated on TVs."})

        # Aspect ratio check (16:9 for long-form)
        ratio = w / h if h > 0 else 1.0
        if 1.70 <= ratio <= 1.85:
            score += 30
        else:
            score += 10
            deductions.append({"component": "Aspect Ratio", "deduction": 20, "reason": f"Aspect ratio ({ratio:.2f}) does not match 16:9 (1.78). Will have black pillarbox bars."})

        # File size check (YouTube limit: 2MB)
        if file_size_kb:
            if file_size_kb <= 2048:
                score += 30
            else:
                score += 5
                deductions.append({"component": "File Size", "deduction": 25, "reason": f"Thumbnail ({file_size_kb} KB) exceeds YouTube's 2 MB upload limit."})
        else:
            score += 20

        final_score = max(10, min(100, score))
        return {
            "score": final_score,
            "status": "Calculated",
            "components": {"resolution": f"{w}x{h}", "aspect_ratio": f"{ratio:.2f}"},
            "deductions": deductions,
            "formula": "HD Resolution 1280x720 (40) + 16:9 Aspect Ratio (30) + Under 2MB size (30)",
            "confidence": "High (Image Geometry Verified)",
        }

    # 7. Content Structure Score (0 - 100)
    def score_content_structure(
        self, hook_score: float, pacing_wpm: int, is_short: bool, has_cta: bool
    ) -> Dict[str, Any]:
        """
        Formula:
          Score = (0.45 * Hook) + (0.35 * Pacing_Score) + (0.20 * CTA_Score)
        """
        deductions = []

        # Hook component (0 - 45)
        h_norm = max(0, min(100, hook_score))
        s_hook = (h_norm / 100.0) * 45
        if h_norm < 70:
            deductions.append({"component": "Opening Hook", "deduction": int(45 - s_hook), "reason": f"Hook score ({h_norm:.0f}/100) indicates passive opening phrasing."})

        # Pacing component (0 - 35)
        if is_short:
            # Shorts target: 150 - 195 WPM
            if 150 <= pacing_wpm <= 195:
                s_pacing = 35
            elif 120 <= pacing_wpm < 150 or 195 < pacing_wpm <= 220:
                s_pacing = 25
                deductions.append({"component": "Pacing (WPM)", "deduction": 10, "reason": f"Speech rate ({pacing_wpm} WPM) is slightly off target (150-195 WPM) for Shorts."})
            else:
                s_pacing = 15
                deductions.append({"component": "Pacing (WPM)", "deduction": 20, "reason": f"Speech rate ({pacing_wpm} WPM) is sub-optimal for high-retention Shorts."})
        else:
            # Long-form target: 130 - 165 WPM
            if 130 <= pacing_wpm <= 165:
                s_pacing = 35
            elif 105 <= pacing_wpm < 130 or 165 < pacing_wpm <= 190:
                s_pacing = 25
                deductions.append({"component": "Pacing (WPM)", "deduction": 10, "reason": f"Speech rate ({pacing_wpm} WPM) is slightly outside natural broadcast range (130-165 WPM)."})
            else:
                s_pacing = 15
                deductions.append({"component": "Pacing (WPM)", "deduction": 20, "reason": f"Speech rate ({pacing_wpm} WPM) risks audience drop-off."})

        # CTA component (0 - 20)
        s_cta = 20 if has_cta else 10
        if not has_cta:
            deductions.append({"component": "Call to Action", "deduction": 10, "reason": "No verbal call to action or next video recommendation detected."})

        total = int(s_hook + s_pacing + s_cta)
        return {
            "score": total,
            "status": "Calculated",
            "components": {"hook_score": hook_score, "pacing_wpm": pacing_wpm, "has_cta": has_cta},
            "deductions": deductions,
            "formula": "Hook (45%) + Speech Pacing WPM (35%) + Call to Action (20%)",
            "confidence": "High (Transcript & Audio Cadence Evaluated)",
        }

    # 8. Channel Consistency Score (0 - 100)
    def score_channel_consistency(
        self, video_count: int, recent_videos: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Formula:
          Score = Catalog_Size (40) + Title_Consistency (30) + Format_Strategy (30)
        """
        if video_count == 0:
            return {
                "score": 20,
                "status": "Calculated",
                "components": {},
                "deductions": [{"component": "Uploads", "deduction": 80, "reason": "No public uploads found on channel."}],
                "formula": "Catalog inventory (40) + Title consistency (30) + Format balance (30)",
                "confidence": "Medium",
            }

        score = 0
        deductions = []

        # Catalog size
        if video_count >= 50:
            score += 40
        elif video_count >= 20:
            score += 30
        elif video_count >= 5:
            score += 20
            deductions.append({"component": "Catalog Depth", "deduction": 20, "reason": f"Channel has {video_count} videos. 20+ videos build stronger algorithmic consistency."})
        else:
            score += 10
            deductions.append({"component": "Catalog Depth", "deduction": 30, "reason": f"Channel only has {video_count} video(s); young channel in initial discovery phase."})

        # Title formatting consistency
        if recent_videos:
            all_caps = sum(1 for v in recent_videos if v.get("title", "").isupper())
            if all_caps == 0:
                score += 30
            elif all_caps <= 1:
                score += 20
                deductions.append({"component": "Title Formatting", "deduction": 10, "reason": "Occasional ALL-CAPS title found among recent uploads."})
            else:
                score += 10
                deductions.append({"component": "Title Formatting", "deduction": 20, "reason": f"{all_caps} titles in ALL-CAPS; damages cohesive channel branding."})
        else:
            score += 20

        # Format balance
        if recent_videos:
            shorts = sum(1 for v in recent_videos if v.get("is_short"))
            longs = len(recent_videos) - shorts
            if shorts > 0 and longs > 0:
                score += 30
            elif longs > 0 and shorts == 0:
                score += 20
                deductions.append({"component": "Format Strategy", "deduction": 10, "reason": "Channel does not publish Shorts; missing top-of-funnel mobile traffic."})
            else:
                score += 20
                deductions.append({"component": "Format Strategy", "deduction": 10, "reason": "Channel only publishes Shorts; lacks high-RPM long-form watch time."})
        else:
            score += 20

        final_score = max(20, min(100, score))
        return {
            "score": final_score,
            "status": "Calculated",
            "components": {"total_videos": video_count, "recent_sample": len(recent_videos)},
            "deductions": deductions,
            "formula": "Catalog depth (40) + Branding consistency (30) + Format strategy (30)",
            "confidence": "High",
        }

    # 9. Data Completeness Score (0 - 100)
    def score_data_completeness(self, available_fields: List[str], required_fields: List[str]) -> Dict[str, Any]:
        """
        Formula:
          Score = (Count_of_Available_Required / Total_Required) * 100
        """
        if not required_fields:
            return {"score": 100, "status": "Calculated", "components": {}, "deductions": [], "formula": "100%", "confidence": "High"}

        present = [f for f in required_fields if f in available_fields]
        missing = [f for f in required_fields if f not in available_fields]
        pct = int((len(present) / len(required_fields)) * 100)
        deductions = [{"component": "Missing Fields", "deduction": int(100 - pct), "reason": f"Missing expected fields: {', '.join(missing)}"}] if missing else []

        return {
            "score": pct,
            "status": "Calculated",
            "components": {"available_count": len(present), "total_required": len(required_fields), "missing": missing},
            "deductions": deductions,
            "formula": "(Available Fields / Total Required Fields) * 100",
            "confidence": "High (Direct Schema Check)",
        }

    # 10. Overall Optimization Readiness Score (0 - 100)
    def calculate_overall_readiness(
        self,
        component_scores: Dict[str, Optional[int]],
    ) -> Dict[str, Any]:
        """
        Calculates a mathematically sound, weighted overall optimization readiness score.
        Gracefully handles components marked 'Insufficient Data' by renormalizing weights across available metrics.
        CRITICAL: Never invents numbers for missing components!
        """
        available_weights = {}
        weighted_sum = 0.0

        for key, weight in self.WEIGHTS.items():
            val = component_scores.get(key)
            if val is not None and isinstance(val, (int, float)):
                available_weights[key] = weight
                weighted_sum += (val * weight)

        if not available_weights:
            return {
                "overall_score": 0,
                "grade": "N/A",
                "status": "Insufficient Data",
                "components": {},
                "explanation": "Insufficient data available to compute overall readiness score.",
            }

        # Renormalize weights across available metrics
        total_weight = sum(available_weights.values())
        final_score = int(weighted_sum / total_weight)
        final_score = max(0, min(100, final_score))

        grade = "A" if final_score >= 88 else "B" if final_score >= 74 else "C" if final_score >= 60 else "D" if final_score >= 45 else "F"

        return {
            "overall_score": final_score,
            "grade": grade,
            "status": "Calculated",
            "active_weights": {k: round(v / total_weight, 3) for k, v in available_weights.items()},
            "formula": "Renormalized weighted sum of available dimension scores",
            "disclaimer": (
                "Notice: Optimization Readiness measures technical compliance, metadata depth, and structural best practices. "
                "It does not guarantee view counts or predict YouTube algorithmic impressions."
            ),
        }
