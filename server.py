"""
Custom Web Application Server for MY YOUTUBE CREATOR STUDIO.
Zero-Streamlit, high-performance asynchronous web architecture powered by Tornado.
Provides comprehensive REST API endpoints and serves the modern YouTube Studio dark dashboard.
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict

import tornado.ioloop
import tornado.web
import tornado.escape

from database.db_manager import DatabaseManager
from services.youtube_service import YouTubeService
from services.competitor_service import CompetitorService
from services.video_analyzer import VideoAnalyzer
from services.metadata_generator import MetadataGenerator
from services.ai_assistant_service import AIAssistantService
from services.oauth_service import OAuthAnalyticsService
from services.algorithm_optimizer import AlgorithmOptimizer

# Initialize core services
db = DatabaseManager()
yt_service = YouTubeService()
comp_service = CompetitorService(yt_service)
video_analyzer = VideoAnalyzer()
meta_gen = MetadataGenerator()
ai_assistant = AIAssistantService()
oauth_service = OAuthAnalyticsService()
algo_optimizer = AlgorithmOptimizer()


class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, DELETE")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()

    def get_json_body(self) -> Dict[str, Any]:
        try:
            return json.loads(self.request.body.decode("utf-8")) if self.request.body else {}
        except Exception:
            return {}

    def write_json(self, data: Dict[str, Any], status_code: int = 200):
        self.set_status(status_code)
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(data))


class ActiveChannelHandler(BaseHandler):
    def get(self):
        """Returns the currently active channel or default sample channel."""
        active_id = db.get_setting("active_channel_id")
        channel = None
        audit = None
        if active_id:
            channel = db.get_channel(active_id)
            audit = db.get_latest_channel_audit(active_id)

        if not channel:
            # Fallback to demo channel
            channel = yt_service.fetch_channel_data("@mkbhd")
            audit = yt_service.audit_channel(channel)
            db.save_channel(channel)
            db.save_channel_audit(channel["channel_id"], audit["overall_score"], audit, audit.get("score_breakdown"))
            db.set_setting("active_channel_id", channel["channel_id"])

        self.write_json({"success": True, "channel": channel, "audit": audit})


class ChannelScanHandler(BaseHandler):
    def post(self):
        """Scans any YouTube URL, handle, or ID."""
        body = self.get_json_body()
        input_url = body.get("url_or_handle", "").strip()
        force_refresh = body.get("force_refresh", False)

        if not input_url:
            self.write_json({"success": False, "error": "Please provide a valid YouTube channel URL or handle."}, 400)
            return

        try:
            scanned = yt_service.fetch_channel_data(input_url, force_refresh=force_refresh, db_manager=db)
            audit = yt_service.audit_channel(scanned)
            db.save_channel(scanned)
            db.save_channel_audit(scanned["channel_id"], audit["overall_score"], audit, audit.get("score_breakdown"))
            db.set_setting("active_channel_id", scanned["channel_id"])
            self.write_json({"success": True, "channel": scanned, "audit": audit})
        except Exception as e:
            self.write_json({"success": False, "error": str(e)}, 500)


class CompetitorSingleHandler(BaseHandler):
    def post(self):
        """Deep-dive baseline intelligence for a single competitor."""
        body = self.get_json_body()
        input_url = body.get("url_or_handle", "").strip()

        if not input_url:
            self.write_json({"success": False, "error": "Please provide a competitor URL or handle."}, 400)
            return

        try:
            res = comp_service.analyze_single_competitor(input_url)
            self.write_json({"success": True, "data": res})
        except Exception as e:
            self.write_json({"success": False, "error": str(e)}, 500)


class CompetitorBatchHandler(BaseHandler):
    def post(self):
        """Batch competitor comparison table & velocity rankings."""
        body = self.get_json_body()
        channels = body.get("channels", [])

        if not channels:
            self.write_json({"success": False, "error": "Please provide competitor channels."}, 400)
            return

        try:
            res = comp_service.analyze_competitors(channels)
            self.write_json({"success": True, "data": res})
        except Exception as e:
            self.write_json({"success": False, "error": str(e)}, 500)


class VideoAnalysisHandler(BaseHandler):
    def post(self):
        """Upload video container bytes and subtitles for deep inspection."""
        transcript_text = self.get_argument("transcript", "")
        topic_hint = self.get_argument("topic", "Uploaded Video")

        # Check for uploaded video file
        video_files = self.request.files.get("video")
        raw_meta = {}
        if video_files:
            v_file = video_files[0]
            raw_meta = video_analyzer.inspect_video_file(v_file.body, filename=v_file.filename)
            if not topic_hint or topic_hint == "Uploaded Video":
                topic_hint = v_file.filename
        else:
            raw_meta = {
                "file_name": "Script_Draft.txt",
                "duration_sec": 300.0,
                "duration_str": "5:00",
                "resolution": "1920x1080",
                "aspect_ratio": "16:9",
                "format_type": "Standard Widescreen",
                "is_short": False,
                "file_size_mb": 0,
                "has_audio": True,
                "bitrate_kbps": 4500,
                "audio_channels": 2,
                "audio_sample_rate": 44100,
            }

        # Check for uploaded subtitles file
        sub_files = self.request.files.get("subtitles")
        if sub_files:
            s_file = sub_files[0]
            parsed_sub = video_analyzer.parse_subtitle_file(s_file.body.decode("utf-8", errors="ignore"))
            transcript_text = parsed_sub["full_text"]
            if parsed_sub.get("cues"):
                raw_meta["cues"] = parsed_sub["cues"]

        try:
            analysis = video_analyzer.analyze_content(raw_meta, transcript_text=transcript_text, topic_hint=topic_hint)
            active_cid = db.get_setting("active_channel_id")
            db.save_video_analysis({
                "channel_id": active_cid,
                "title": topic_hint,
                "source_type": "upload",
                "file_name": raw_meta.get("file_name", "Video"),
                "file_size": raw_meta.get("file_size_bytes", 0),
                "duration": raw_meta.get("duration_sec", 0),
                "aspect_ratio": raw_meta.get("aspect_ratio", "16:9"),
                "resolution": raw_meta.get("resolution", "1920x1080"),
                "bitrate": raw_meta.get("bitrate_kbps", 0),
                "hook_score": analysis.get("hook_score", 70),
                "pacing_score": analysis.get("pacing_score", 70),
                "readiness_score": analysis.get("overall_score", 75),
                "scores_json": json.dumps(analysis.get("component_scores", {})),
                "details": {"metadata": raw_meta, "content_eval": analysis},
            })
            self.write_json({"success": True, "metadata": raw_meta, "analysis": analysis})
        except Exception as e:
            self.write_json({"success": False, "error": str(e)}, 500)


class MetadataGeneratorHandler(BaseHandler):
    def post(self):
        """Generates SEO titles, descriptions, and tags."""
        body = self.get_json_body()
        topic = body.get("topic", "Mastering Modern Content")
        niche = body.get("niche", "Creator Economy")
        fmt = body.get("format_type", "Long-form")
        audience = body.get("target_audience", "General Audience")
        country = body.get("target_country", "United States")

        try:
            meta = meta_gen.generate_all(topic=topic, niche=niche, format_type=fmt, target_audience=audience, target_country=country)
            self.write_json({"success": True, "data": meta})
        except Exception as e:
            self.write_json({"success": False, "error": str(e)}, 500)


class AiChatHandler(BaseHandler):
    def post(self):
        """Grounded AI Assistant chat."""
        body = self.get_json_body()
        query = body.get("query", "").strip()
        active_cid = db.get_setting("active_channel_id")
        channel = db.get_channel(active_cid) if active_cid else None

        if not query:
            self.write_json({"success": False, "error": "Query cannot be empty."}, 400)
            return

        try:
            ans = ai_assistant.answer_query(query, channel_data=channel)
            self.write_json({"success": True, "response": ans})
        except Exception as e:
            self.write_json({"success": False, "error": str(e)}, 500)


class TasksHandler(BaseHandler):
    def get(self):
        tasks = db.get_publishing_tasks()
        self.write_json({"success": True, "tasks": tasks})

    def post(self):
        body = self.get_json_body()
        title = body.get("title", "").strip()
        fmt = body.get("format_type", "Long-form")
        date_str = body.get("target_date", "")

        if not title:
            self.write_json({"success": False, "error": "Title required."}, 400)
            return

        active_cid = db.get_setting("active_channel_id")
        task_id = db.save_publishing_task({
            "channel_id": active_cid,
            "title": title,
            "format_type": fmt,
            "target_date": date_str,
            "status": "Scheduled",
        })
        self.write_json({"success": True, "task_id": task_id})


class SettingsHandler(BaseHandler):
    def get(self):
        active_id = db.get_setting("active_channel_id") or ""
        api_key = db.get_setting("youtube_api_key") or ""
        self.write_json({"success": True, "active_channel_id": active_id, "has_api_key": bool(api_key)})

    def post(self):
        body = self.get_json_body()
        if "youtube_api_key" in body:
            db.set_setting("youtube_api_key", body["youtube_api_key"])
        self.write_json({"success": True, "message": "Settings updated."})


class AlgorithmicAuditHandler(BaseHandler):
    def get(self):
        """Returns deep algorithmic audit for active channel."""
        active_id = db.get_setting("active_channel_id")
        channel = db.get_channel(active_id) if active_id else None
        if not channel:
            channel = yt_service.fetch_channel_data("@mkbhd")
            db.save_channel(channel)
            db.set_setting("active_channel_id", channel["channel_id"])

        try:
            audit = algo_optimizer.generate_algorithmic_audit(channel)
            self.write_json({"success": True, "audit": audit})
        except Exception as e:
            self.write_json({"success": False, "error": str(e)}, 500)

    def post(self):
        """Runs deep algorithmic audit for any provided channel URL or handle."""
        body = self.get_json_body()
        input_url = body.get("url_or_handle", "").strip()
        if not input_url:
            active_id = db.get_setting("active_channel_id")
            channel = db.get_channel(active_id) if active_id else None
        else:
            channel = yt_service.fetch_channel_data(input_url, db_manager=db)

        if not channel:
            channel = yt_service.fetch_channel_data("@mkbhd")

        try:
            audit = algo_optimizer.generate_algorithmic_audit(channel)
            self.write_json({"success": True, "audit": audit})
        except Exception as e:
            self.write_json({"success": False, "error": str(e)}, 500)


class RetentionSimHandler(BaseHandler):
    def post(self):
        """Simulates audience retention curve R(t) based on mathematical double-exponential decay."""
        body = self.get_json_body()
        duration_sec = float(body.get("duration_sec", 300.0))
        hook_score = float(body.get("hook_score", 75.0))
        pacing_wpm = float(body.get("pacing_wpm", 145.0))
        cuts_per_min = float(body.get("cuts_per_min", 8.0))
        has_fluff = bool(body.get("has_intro_fluff", False))
        is_short = bool(body.get("is_short", False))

        try:
            sim = algo_optimizer.simulate_retention_curve(
                duration_sec=duration_sec,
                hook_score=hook_score,
                pacing_wpm=pacing_wpm,
                cuts_per_min=cuts_per_min,
                has_intro_fluff=has_fluff,
                is_short=is_short,
            )
            self.write_json({"success": True, "simulation": sim})
        except Exception as e:
            self.write_json({"success": False, "error": str(e)}, 500)


class BayesianCtrPredictHandler(BaseHandler):
    def post(self):
        """Predicts expected Click-Through Rate and virality index via Bayesian Beta-Binomial updating."""
        body = self.get_json_body()
        title = body.get("title", "").strip()
        niche = body.get("niche", "General")
        is_short = bool(body.get("is_short", False))

        try:
            pred = algo_optimizer.predict_bayesian_ctr(title, niche=niche, is_short=is_short)
            self.write_json({"success": True, "prediction": pred})
        except Exception as e:
            self.write_json({"success": False, "error": str(e)}, 500)


class OutlierDistributionHandler(BaseHandler):
    def post(self):
        """Computes log-normal Z-scores and breakout tiers for a list of videos."""
        body = self.get_json_body()
        videos = body.get("videos")
        if not videos:
            active_id = db.get_setting("active_channel_id")
            channel = db.get_channel(active_id) if active_id else None
            videos = channel.get("videos", []) if channel else []

        try:
            dist = algo_optimizer.analyze_outlier_distribution(videos)
            self.write_json({"success": True, "distribution": dist})
        except Exception as e:
            self.write_json({"success": False, "error": str(e)}, 500)


class WinningNgramsHandler(BaseHandler):
    def post(self):
        """Extracts high-multiplier n-grams via TF-IDF vectorization."""
        body = self.get_json_body()
        videos = body.get("videos")
        top_k = int(body.get("top_k", 12))
        if not videos:
            active_id = db.get_setting("active_channel_id")
            channel = db.get_channel(active_id) if active_id else None
            videos = channel.get("videos", []) if channel else []

        try:
            ngrams = algo_optimizer.extract_winning_ngrams(videos, top_k=top_k)
            self.write_json({"success": True, "ngrams": ngrams})
        except Exception as e:
            self.write_json({"success": False, "error": str(e)}, 500)


class TimingHeatmapHandler(BaseHandler):
    def post(self):
        """Builds 7x24 upload timing and view velocity heatmap."""
        body = self.get_json_body()
        videos = body.get("videos")
        if not videos:
            active_id = db.get_setting("active_channel_id")
            channel = db.get_channel(active_id) if active_id else None
            videos = channel.get("videos", []) if channel else []

        try:
            timing = algo_optimizer.compute_upload_timing_heatmap(videos)
            self.write_json({"success": True, "timing": timing})
        except Exception as e:
            self.write_json({"success": False, "error": str(e)}, 500)


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
        index_file = os.path.join(static_dir, "index.html")
        if os.path.exists(index_file):
            with open(index_file, "r", encoding="utf-8") as f:
                self.write(f.read())
        else:
            self.write("<h1>MY YOUTUBE CREATOR STUDIO</h1><p>Static index.html loading...</p>")


def make_app():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    static_path = os.path.join(base_dir, "static")

    return tornado.web.Application(
        [
            (r"/", IndexHandler),
            (r"/api/channel/active", ActiveChannelHandler),
            (r"/api/channel/scan", ChannelScanHandler),
            (r"/api/competitor/single", CompetitorSingleHandler),
            (r"/api/competitor/batch", CompetitorBatchHandler),
            (r"/api/video/analyze", VideoAnalysisHandler),
            (r"/api/metadata/generate", MetadataGeneratorHandler),
            (r"/api/ai/chat", AiChatHandler),
            (r"/api/tasks", TasksHandler),
            (r"/api/settings", SettingsHandler),
            (r"/api/algorithm/audit", AlgorithmicAuditHandler),
            (r"/api/algorithm/retention-sim", RetentionSimHandler),
            (r"/api/algorithm/ctr-predict", BayesianCtrPredictHandler),
            (r"/api/algorithm/outliers", OutlierDistributionHandler),
            (r"/api/algorithm/ngrams", WinningNgramsHandler),
            (r"/api/algorithm/timing", TimingHeatmapHandler),
            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": static_path}),
        ],
        autoreload=False,
        debug=False,
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8501))
    app = make_app()
    app.listen(port, address="0.0.0.0")
    print(f"==================================================")
    print(f"MY YOUTUBE CREATOR STUDIO — Web Server Running!")
    print(f"Server Port: {port}")
    print(f"Local URL:   http://localhost:{port}")
    print(f"Framework:   Tornado (Zero-Streamlit Architecture)")
    print(f"==================================================")
    tornado.ioloop.IOLoop.current().start()
