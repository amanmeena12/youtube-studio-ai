"""
USA Channel Optimization Service for MY YOUTUBE CREATOR STUDIO.
Provides audience targeting recommendations, American English vernacular guidance,
seasonal creator opportunities, and US timezone publishing schedules.
"""

from typing import Any, Dict, List


class USOptimizationService:
    US_TIMEZONES = {
        "Eastern Time (EST/EDT)": {"utc_offset": -5, "prime_start": "14:00", "prime_end": "17:00"},
        "Central Time (CST/CDT)": {"utc_offset": -6, "prime_start": "13:00", "prime_end": "16:00"},
        "Mountain Time (MST/MDT)": {"utc_offset": -7, "prime_start": "12:00", "prime_end": "15:00"},
        "Pacific Time (PST/PDT)": {"utc_offset": -8, "prime_start": "11:00", "prime_end": "14:00"},
    }

    SEASONAL_CALENDAR_US = {
        "Q1 (Jan - Mar)": {
            "themes": ["New Year Resolutions", "Tax Preparation & Finance", "Fitness & Habits", "Spring Reset"],
            "rpm_context": "Advertiser budgets reset in January (lower RPMs); focus on high-volume discovery content.",
        },
        "Q2 (Apr - Jun)": {
            "themes": ["Graduation & Summer Prep", "Travel & Outdoor Activities", "Mid-Year Reviews"],
            "rpm_context": "Ad rates recover steadily. High engagement for lifestyle and outdoor content.",
        },
        "Q3 (Jul - Sep)": {
            "themes": ["Back to School", "Fall Product Launches", "Tech Announcements"],
            "rpm_context": "Solid engagement. August has high back-to-school search velocity.",
        },
        "Q4 (Oct - Dec)": {
            "themes": ["Black Friday / Cyber Monday", "Holiday Gift Guides", "Year-End Reflections"],
            "rpm_context": "Peak advertiser spending and highest RPM of the year; prioritize monetizable reviews & guides.",
        },
    }

    AMERICAN_ENGLISH_PATTERNS = {
        "Spelling": [
            ("colour", "color"),
            ("flavour", "flavor"),
            ("optimise", "optimize"),
            ("analyse", "analyze"),
            ("centre", "center"),
            ("theatre", "theater"),
            ("programme", "program"),
        ],
        "Terminology": [
            ("holiday", "vacation"),
            ("postcode", "zip code"),
            ("CV / curriculum vitae", "resume"),
            ("mobile / mobile phone", "cell phone"),
            ("flat", "apartment"),
            ("biscuit", "cookie"),
        ],
    }

    def __init__(self):
        pass

    def get_optimization_report(
        self,
        target_country: str = "United States",
        selected_timezone: str = "Eastern Time (EST/EDT)",
        topic: str = "",
        niche: str = "",
    ) -> Dict[str, Any]:
        """Generates a complete country targeting and timezone scheduling report."""
        is_us = target_country == "United States"
        tz_info = self.US_TIMEZONES.get(selected_timezone, self.US_TIMEZONES["Eastern Time (EST/EDT)"])

        schedule_recommendations = self._calculate_publishing_windows(tz_info, is_us)
        language_guidance = self._get_language_guidance(is_us)
        seasonal_hooks = self._get_seasonal_recommendations()

        return {
            "target_country": target_country,
            "selected_timezone": selected_timezone,
            "is_us_focused": is_us,
            "schedule_recommendations": schedule_recommendations,
            "language_guidance": language_guidance,
            "seasonal_hooks": seasonal_hooks,
            "disclaimer": (
                "Important Note: Selecting the United States as your target region optimizes titles, phrasing, "
                "and publishing times for North American viewers, but does not guarantee algorithmic distribution. "
                "YouTube distributes videos based on individual viewer watch history and engagement signals."
            ),
        }

    def _calculate_publishing_windows(self, tz_info: Dict[str, Any], is_us: bool) -> List[Dict[str, str]]:
        if not is_us:
            return [
                {
                    "day": "Weekday (Mon - Fri)",
                    "recommended_time": "14:00 - 16:00 (Local Creator Time)",
                    "reasoning": "Publish 2 hours before local evening peak so YouTube has time to index and process HD resolutions.",
                },
                {
                    "day": "Weekend (Sat - Sun)",
                    "recommended_time": "09:00 - 11:00 (Local Creator Time)",
                    "reasoning": "Weekend viewing starts earlier in the day across desktop and mobile devices.",
                },
            ]

        # US audience schedule
        return [
            {
                "day": "Tuesday & Thursday (Peak Long-Form)",
                "recommended_time": f"{tz_info['prime_start']} - {tz_info['prime_end']} ({tz_info.get('name', 'Selected TZ')})",
                "reasoning": (
                    "Publishing early afternoon gives YouTube 2-3 hours to index metadata and generate resolutions "
                    "before peak 6:00 PM - 9:00 PM US leisure viewing."
                ),
            },
            {
                "day": "Saturday & Sunday (Weekend Viewership)",
                "recommended_time": "09:00 AM - 12:00 PM",
                "reasoning": "High morning consumption on tablets and smart TVs as audiences relax at home.",
            },
            {
                "day": "Shorts Cadence (Daily)",
                "recommended_time": "12:00 PM (Lunch Break) or 17:00 (Evening Commute)",
                "reasoning": "Mobile Shorts consumption spikes during mid-day breaks and evening commutes.",
            },
        ]

    def _get_language_guidance(self, is_us: bool) -> Dict[str, Any]:
        if not is_us:
            return {
                "tone": "International English or Native Language",
                "principles": [
                    "Speak clearly at a consistent pace.",
                    "Use universally understood examples and metric/imperial units where applicable.",
                    "Include English captions/subtitles to expand international discoverability.",
                ],
                "spelling_rules": [],
            }

        return {
            "tone": "Direct, Action-Oriented American English",
            "principles": [
                "Lead with outcomes: American viewers strongly prioritize 'What is in this for me?' within the first 10 seconds.",
                "Keep sentences concise and avoid overly formal academic phrasing.",
                "Use active voice ('I tested 5 tools' instead of '5 tools were tested by me').",
                "Use familiar American terminology for everyday concepts (e.g., 'resume' instead of 'CV').",
            ],
            "spelling_rules": self.AMERICAN_ENGLISH_PATTERNS["Spelling"][:5],
            "vocabulary_rules": self.AMERICAN_ENGLISH_PATTERNS["Terminology"][:5],
        }

    def _get_seasonal_recommendations(self) -> List[Dict[str, str]]:
        items = []
        for q, data in self.SEASONAL_CALENDAR_US.items():
            items.append({
                "quarter": q,
                "themes": ", ".join(data["themes"]),
                "rpm_context": data["rpm_context"],
            })
        return items
