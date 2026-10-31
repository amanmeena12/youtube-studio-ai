"""
Metadata Generation and Validation Engine for MY YOUTUBE CREATOR STUDIO.
Generates 5 distinct title formulas, copy-ready descriptions, relevant tags,
and explains hashtag relationships while validating YouTube's exact platform requirements.
"""

import re
from typing import Any, Dict, List, Optional


class MetadataGenerator:
    # Official YouTube platform limits
    MAX_TITLE_LENGTH = 100
    RECOMMENDED_TITLE_MIN = 35
    RECOMMENDED_TITLE_MAX = 70
    MAX_DESCRIPTION_LENGTH = 5000
    MAX_TAGS_TOTAL_CHARS = 500
    MAX_HASHTAGS_ALLOWED = 60
    RECOMMENDED_HASHTAGS = 5

    def __init__(self):
        pass

    def generate_all(
        self,
        topic: str,
        niche: str = "General",
        format_type: str = "Long-form",  # "Shorts" or "Long-form"
        target_audience: str = "General Audience",
        target_country: str = "United States",
        transcript_snippet: str = "",
    ) -> Dict[str, Any]:
        """Generates comprehensive metadata package with validation."""
        topic_clean = topic.strip() or "Content Strategy"
        is_short = "short" in format_type.lower()

        titles = self._generate_five_titles(topic_clean, niche, is_short, target_country)
        description = self._generate_description(topic_clean, niche, is_short, target_audience, transcript_snippet)
        tags = self._generate_tags(topic_clean, niche, is_short)
        hashtags = self._generate_hashtags(topic_clean, niche, is_short)

        # Validation
        validation = self.validate_metadata(
            title=titles[0]["title"],
            description=description,
            tags=tags,
            hashtags=[h["tag"] for h in hashtags],
        )

        return {
            "titles": titles,
            "description": description,
            "tags": tags,
            "tags_comma_separated": ", ".join(tags),
            "hashtags": hashtags,
            "validation": validation,
            "inputs": {
                "topic": topic_clean,
                "niche": niche,
                "format_type": format_type,
                "target_audience": target_audience,
                "target_country": target_country,
            },
        }

    def _generate_five_titles(
        self, topic: str, niche: str, is_short: bool, target_country: str
    ) -> List[Dict[str, Any]]:
        year = "2026"
        if is_short:
            return [
                {
                    "title": f"Stop Making This {topic} Mistake! #shorts",
                    "formula": "Pain Point & Mistake Avoidance",
                    "angle": "Stops the user mid-scroll by calling out an immediate behavior they might be doing wrong.",
                    "char_count": len(f"Stop Making This {topic} Mistake! #shorts"),
                },
                {
                    "title": f"The 10-Second {topic} Hack You Need",
                    "formula": "Speed & High-Value Shortcut",
                    "angle": "Promises maximum actionable outcome with minimal viewer time investment.",
                    "char_count": len(f"The 10-Second {topic} Hack You Need"),
                },
                {
                    "title": f"Why Nobody Tells You The Truth About {topic}",
                    "formula": "Insider Curiosity Gap",
                    "angle": "Creates cognitive dissonance by suggesting mainstream consensus is missing crucial facts.",
                    "char_count": len(f"Why Nobody Tells You The Truth About {topic}"),
                },
                {
                    "title": f"I Tested {topic} So You Don't Have To",
                    "formula": "Personal Case Study & Effort Relief",
                    "angle": "Saves the viewer effort and positions the creator as an authentic investigator.",
                    "char_count": len(f"I Tested {topic} So You Don't Have To"),
                },
                {
                    "title": f"Do THIS Before Starting {topic} in {year}",
                    "formula": "Urgency & Fresh Timeliness",
                    "angle": "Triggers fear of missing out (FOMO) before starting a project or habit.",
                    "char_count": len(f"Do THIS Before Starting {topic} in {year}"),
                },
            ]

        # Long-form title formulas
        return [
            {
                "title": f"How to Master {topic} in {year} (The Complete Blueprint)",
                "formula": "Definitive Guide / Search Intent",
                "angle": "Directly captures high-intent YouTube search traffic looking for a comprehensive masterclass.",
                "char_count": len(f"How to Master {topic} in {year} (The Complete Blueprint)"),
            },
            {
                "title": f"Why 90% of Creators Fail at {topic} (And What to Do Instead)",
                "formula": "Empathy + Contrarian Warning",
                "angle": "Normalizes viewer struggle while presenting your specific framework as the clear solution.",
                "char_count": len(f"Why 90% of Creators Fail at {topic} (And What to Do Instead)"),
            },
            {
                "title": f"The Only 3 {topic} Rules That Actually Matter",
                "formula": "Radical Simplification",
                "angle": "Relieves overwhelming information overload by distilling the complex topic into 3 tangible pillars.",
                "char_count": len(f"The Only 3 {topic} Rules That Actually Matter"),
            },
            {
                "title": f"I Tried Every {topic} Method: Here's What Worked",
                "formula": "Empirical Comparison & Transparency",
                "angle": "Builds intense viewer trust through genuine testing and data-backed takeaways.",
                "char_count": len(f"I Tried Every {topic} Method: Here's What Worked"),
            },
            {
                "title": f"The Step-by-Step {topic} System You Can Copy Today",
                "formula": "Turnkey Implementation",
                "angle": "Emphasizes immediate friction-free applicability for ambitious viewers.",
                "char_count": len(f"The Step-by-Step {topic} System You Can Copy Today"),
            },
        ]

    def _generate_description(
        self, topic: str, niche: str, is_short: bool, target_audience: str, snippet: str
    ) -> str:
        if is_short:
            return (
                f"Quick breakdown on {topic}! Make sure to subscribe for daily actionable {niche.lower()} tips.\n\n"
                f"Drop your questions below and let me know what we should cover next!\n\n"
                f"#{topic.replace(' ', '')} #Shorts #YouTubeShorts #{niche.replace(' ', '')}"
            )

        snippet_block = f"Key takeaway: {snippet[:120]}...\n\n" if snippet else ""

        return (
            f"In this video, we break down the definitive guide to {topic}. "
            f"Whether you are just getting started in {niche.lower()} or looking to refine your existing systems, "
            f"this step-by-step breakdown gives you the exact framework to succeed.\n\n"
            f"{snippet_block}"
            "TIMESTAMPS:\n"
            "0:00 - Introduction & The Big Problem\n"
            "1:30 - Core Foundation & Concepts\n"
            "4:15 - Step-by-Step Implementation Framework\n"
            "8:00 - 3 Costly Mistakes to Avoid\n"
            "11:45 - Summary & Action Steps\n\n"
            "FREE RESOURCES & TOOLS:\n"
            f"- Download our companion checklist: https://example.com/{topic.lower().replace(' ', '-')}-guide\n"
            "- Join our free community: https://example.com/community\n\n"
            "LET'S CONNECT:\n"
            "- Subscribe to the channel: https://youtube.com/@YourChannel\n"
            "- Business & Collaboration Inquiries: contact@yourdomain.com\n\n"
            "DISCLAIMER: The information shared in this video is based on independent testing and educational research. "
            "Always adapt strategies to your specific channel audience and goals.\n\n"
            f"#{topic.replace(' ', '')} #{niche.replace(' ', '')} #YouTubeGrowth #CreatorGuide"
        )

    def _generate_tags(self, topic: str, niche: str, is_short: bool) -> List[str]:
        words = topic.lower().split()
        tags = [topic.lower(), niche.lower()]
        for w in words:
            if len(w) > 3 and w not in tags:
                tags.append(w)

        standard = [
            f"{topic.lower()} tutorial",
            f"{topic.lower()} guide",
            f"{topic.lower()} for beginners",
            f"how to do {topic.lower()}",
            f"{topic.lower()} tips",
            f"best {topic.lower()} strategy",
            f"{niche.lower()} tips",
            "youtube growth",
            "2026 strategy",
        ]
        if is_short:
            standard.extend(["shorts", "youtube shorts", "quick tips"])

        for s in standard:
            if s not in tags:
                tags.append(s)

        # Ensure total character count fits under 500
        approved_tags = []
        cur_len = 0
        for t in tags:
            if cur_len + len(t) + 1 <= self.MAX_TAGS_TOTAL_CHARS:
                approved_tags.append(t)
                cur_len += len(t) + 1
            else:
                break
        return approved_tags

    def _generate_hashtags(self, topic: str, niche: str, is_short: bool) -> List[Dict[str, str]]:
        clean_topic = re.sub(r"[^a-zA-Z0-9]", "", topic.title())
        clean_niche = re.sub(r"[^a-zA-Z0-9]", "", niche.title())

        hashtags = [
            {
                "tag": f"#{clean_topic}" if clean_topic else "#Guide",
                "relationship": "Primary video topic anchor; connects your upload directly to viewers browsing this exact subject.",
            },
            {
                "tag": f"#{clean_niche}" if clean_niche else "#Tutorial",
                "relationship": "Broader industry niche category tag to place the video within relevant algorithmic clusters.",
            },
        ]
        if is_short:
            hashtags.append({
                "tag": "#Shorts",
                "relationship": "Universal YouTube platform hashtag required for indexing on the mobile Shorts player feed.",
            })
            hashtags.append({
                "tag": "#YouTubeShorts",
                "relationship": "Secondary feed discovery identifier used across mobile YouTube surfaces.",
            })
            hashtags.append({
                "tag": "#QuickTips",
                "relationship": "Signifies actionable bite-sized value to rapid mobile consumers.",
            })
        else:
            hashtags.append({
                "tag": "#YouTubeGrowth",
                "relationship": "Connects content with creators and active learners across creator economy topics.",
            })
            hashtags.append({
                "tag": "#Tutorial",
                "relationship": "Flags content as an educational instructional guide.",
            })
            hashtags.append({
                "tag": "#CreatorEconomy",
                "relationship": "Expands distribution to business and media professional feeds.",
            })
        return hashtags

    def validate_metadata(
        self,
        title: str,
        description: str,
        tags: List[str],
        hashtags: List[str],
    ) -> Dict[str, Any]:
        """Runs strict compliance and quality validation checks."""
        warnings = []
        errors = []
        passed = []

        # 1. Title Checks
        title_len = len(title.strip())
        if title_len == 0:
            errors.append("Title cannot be empty.")
        elif title_len > self.MAX_TITLE_LENGTH:
            errors.append(f"Title exceeds 100 character limit ({title_len}/100). YouTube will reject it.")
        elif title_len < self.RECOMMENDED_TITLE_MIN:
            warnings.append(f"Title is short ({title_len} chars). Target 45-65 characters for optimal CTR.")
        elif title_len > self.RECOMMENDED_TITLE_MAX:
            warnings.append(f"Title may be truncated on mobile devices ({title_len}/70 recommended mobile cutoff).")
        else:
            passed.append(f"Title length is optimal ({title_len} chars). Displays cleanly across desktop and mobile.")

        # Check ALL CAPS in title
        if title.isupper() and len(title) > 15:
            warnings.append("Title is in ALL CAPS. Use sentence case or capitalize only 1-2 emphasis words to avoid looking spammy.")

        # 2. Description Checks
        desc_len = len(description.strip())
        if desc_len == 0:
            warnings.append("Description is empty. YouTube algorithm and search rely heavily on description text.")
        elif desc_len > self.MAX_DESCRIPTION_LENGTH:
            errors.append(f"Description exceeds 5,000 character limit ({desc_len}/5000).")
        else:
            passed.append(f"Description length ({desc_len} chars) complies with the 5,000 character limit.")

        # Check links and timestamps in description
        if "http://" in description or "https://" in description:
            passed.append("Description contains relevant outbound links.")
        else:
            warnings.append("No links found in description (e.g., social links, website, resources).")

        # 3. Tags Checks
        total_tag_chars = sum(len(t) for t in tags) + len(tags)
        if total_tag_chars > self.MAX_TAGS_TOTAL_CHARS:
            errors.append(f"Tags exceed 500 character limit ({total_tag_chars}/500 chars).")
        else:
            passed.append(f"Tags total character footprint is within bounds ({total_tag_chars}/500 chars across {len(tags)} tags).")

        # 4. Hashtags Checks
        hashtag_count = len(hashtags)
        if hashtag_count > self.MAX_HASHTAGS_ALLOWED:
            errors.append(f"Exceeds 60 hashtags ({hashtag_count}). YouTube will ignore all hashtags on this video.")
        elif hashtag_count > self.RECOMMENDED_HASHTAGS:
            warnings.append(f"Using {hashtag_count} hashtags. YouTube typically displays only the first 3-5 above the title.")
        else:
            passed.append(f"Hashtag count is clean ({hashtag_count} hashtags).")

        status = "PASSED" if not errors else "FAILED"
        if warnings and status == "PASSED":
            status = "NEEDS_OPTIMIZATION"

        return {
            "status": status,
            "passed": passed,
            "warnings": warnings,
            "errors": errors,
            "metrics": {
                "title_length": title_len,
                "description_length": desc_len,
                "tag_count": len(tags),
                "tag_characters": total_tag_chars,
                "hashtag_count": hashtag_count,
            },
        }
