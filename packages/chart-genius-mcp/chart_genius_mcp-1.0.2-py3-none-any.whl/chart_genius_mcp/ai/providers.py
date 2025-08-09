from __future__ import annotations

from typing import Any, Dict, List, Optional
import os
import json
import httpx
import pandas as pd
import logging

from .chart_detector import SmartChartDetector
from .insight_generator import InsightGenerator

SUPPORTED_CHART_TYPES = {
    "bar", "line", "scatter", "pie", "heatmap", "histogram", "area", "box", "violin", "bubble"
}


def _coerce_chart_type(value: str) -> str:
    v = (value or "").strip().lower()
    return v if v in SUPPORTED_CHART_TYPES else "bar"


def _default_theme_for_context(context: str) -> str:
    mapping = {
        "business": "corporate",
        "executive": "corporate",
        "technical": "modern",
    }
    return mapping.get((context or "").lower(), "modern")


def _summarize_dataframe(df: pd.DataFrame, sample_rows: int = 5) -> Dict[str, Any]:
    summary = {
        "columns": list(map(str, df.columns.tolist())),
        "shape": [int(df.shape[0]), int(df.shape[1])],
        "dtypes": {str(c): str(t) for c, t in zip(df.columns, df.dtypes)},
        "head": df.head(sample_rows).to_dict(orient="records"),
    }
    return summary


class AiProvider:
    async def analyze_question(self, question: str, data: pd.DataFrame, context: str = "business") -> Dict[str, Any]:
        raise NotImplementedError

    async def generate_insights(
        self,
        data: pd.DataFrame,
        chart_type: str,
        question: Optional[str] = None,
        insight_types: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        raise NotImplementedError


class HeuristicProvider(AiProvider):
    def __init__(self) -> None:
        self.detector = SmartChartDetector()
        self.insights = InsightGenerator()

    async def analyze_question(self, question: str, data: pd.DataFrame, context: str = "business") -> Dict[str, Any]:
        return await self.detector.analyze_question(question=question, data=data, context=context)

    async def generate_insights(
        self,
        data: pd.DataFrame,
        chart_type: str,
        question: Optional[str] = None,
        insight_types: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        return await self.insights.generate_insights(
            data=data,
            question=question or "",
            chart_type=chart_type,
            insight_types=insight_types or ["trends", "outliers", "correlations"],
        )


class OpenAIProvider(AiProvider):
    def __init__(self, api_key: str, model: Optional[str] = None, timeout_s: float = 12.0) -> None:
        self.api_key = api_key
        self.model = model or os.getenv("CHART_AI_MODEL_OPENAI", "gpt-4o-mini")
        self.timeout_s = timeout_s
        self.url = "https://api.openai.com/v1/responses"

    async def _call(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self.model,
            "input": prompt,
        }
        async with httpx.AsyncClient(timeout=self.timeout_s) as client:
            try:
                r = await client.post(self.url, headers=headers, json=body)
            except httpx.HTTPError as e:
                logging.getLogger(__name__).debug(f"OpenAI HTTP error: model={self.model} err={e}")
                raise
            r.raise_for_status()
            data = r.json()
            # Try to extract text
            text = None
            if isinstance(data, dict):
                if "output_text" in data:
                    text = data["output_text"]
                elif "content" in data and isinstance(data["content"], list) and data["content"]:
                    # Fallback if using older shapes
                    maybe = data["content"][0]
                    if isinstance(maybe, dict) and "text" in maybe:
                        text = maybe["text"]
            return text or json.dumps(data)

    async def analyze_question(self, question: str, data: pd.DataFrame, context: str = "business") -> Dict[str, Any]:
        summary = _summarize_dataframe(data)
        prompt = (
            "You are a chart recommendation assistant.\n"
            "Given a dataset summary and user question, respond ONLY with JSON of the form:\n"
            "{\"recommended_chart\": string, \"reasoning\": string, \"confidence\": number, \"theme\": string}.\n"
            f"Context: {context}\n"
            f"Question: {question}\n"
            f"Dataset summary: {json.dumps(summary)[:4000]}\n"
            "Use supported chart types only: bar,line,scatter,pie,heatmap,histogram,area,box,violin,bubble."
        )
        try:
            text = await self._call(prompt)
            obj = json.loads(text)
            return {
                "recommended_chart": _coerce_chart_type(obj.get("recommended_chart", "")),
                "recommended_engine": "plotly",
                "recommended_theme": obj.get("theme") or _default_theme_for_context(context),
                "reasoning": obj.get("reasoning", ""),
                "confidence": float(obj.get("confidence", 0.7)),
            }
        except Exception:
            # Defer fallback to router (catch at caller)
            raise

    async def generate_insights(
        self,
        data: pd.DataFrame,
        chart_type: str,
        question: Optional[str] = None,
        insight_types: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        summary = _summarize_dataframe(data)
        kinds = ", ".join(insight_types or ["trends", "outliers", "correlations"]).lower()
        prompt = (
            "You are a data analyst.\n"
            "Analyze the dataset summary and return ONLY a JSON array of short insights, each as an object with keys: \n"
            "{\"type\": string, \"text\": string}.\n"
            f"Insight types to focus: {kinds}.\n"
            f"Chart type: {chart_type}.\n"
            f"Question (optional): {question or ''}.\n"
            f"Dataset summary: {json.dumps(summary)[:4000]}\n"
        )
        try:
            text = await self._call(prompt)
            arr = json.loads(text)
            if isinstance(arr, list):
                return [i for i in arr if isinstance(i, dict) and "text" in i]
            return []
        except Exception:
            raise


class AnthropicProvider(AiProvider):
    def __init__(self, api_key: str, model: Optional[str] = None, timeout_s: float = 12.0) -> None:
        self.api_key = api_key
        self.model = model or os.getenv("CHART_AI_MODEL_CLAUDE", "claude-3-5-sonnet-20240620")
        self.timeout_s = timeout_s
        self.url = "https://api.anthropic.com/v1/messages"

    async def _call(self, prompt: str) -> str:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        body = {"model": self.model, "max_tokens": 400, "messages": [{"role": "user", "content": prompt}]}
        async with httpx.AsyncClient(timeout=self.timeout_s) as client:
            try:
                r = await client.post(self.url, headers=headers, json=body)
            except httpx.HTTPError as e:
                logging.getLogger(__name__).debug(f"Anthropic HTTP error: model={self.model} err={e}")
                raise
            r.raise_for_status()
            data = r.json()
            # Extract text
            try:
                content = data.get("content", [])
                if content and isinstance(content, list):
                    maybe = content[0]
                    if isinstance(maybe, dict) and "text" in maybe:
                        return maybe["text"]
            except Exception:
                pass
            return json.dumps(data)

    async def analyze_question(self, question: str, data: pd.DataFrame, context: str = "business") -> Dict[str, Any]:
        summary = _summarize_dataframe(data)
        prompt = (
            "Return ONLY JSON: {\"recommended_chart\":string, \"reasoning\":string, \"confidence\":number, \"theme\":string}.\n"
            f"Context: {context}\nQuestion: {question}\nDataset summary: {json.dumps(summary)[:4000]}\n"
            "Supported charts: bar,line,scatter,pie,heatmap,histogram,area,box,violin,bubble."
        )
        text = await self._call(prompt)
        obj = json.loads(text)
        return {
            "recommended_chart": _coerce_chart_type(obj.get("recommended_chart", "")),
            "recommended_engine": "plotly",
            "recommended_theme": obj.get("theme") or _default_theme_for_context(context),
            "reasoning": obj.get("reasoning", ""),
            "confidence": float(obj.get("confidence", 0.7)),
        }

    async def generate_insights(
        self,
        data: pd.DataFrame,
        chart_type: str,
        question: Optional[str] = None,
        insight_types: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        summary = _summarize_dataframe(data)
        kinds = ", ".join(insight_types or ["trends", "outliers", "correlations"]).lower()
        prompt = (
            "Return ONLY JSON array of {type,text}.\n"
            f"Types: {kinds}, Chart: {chart_type}, Question: {question or ''}.\n"
            f"Dataset summary: {json.dumps(summary)[:4000]}\n"
        )
        text = await self._call(prompt)
        arr = json.loads(text)
        return [i for i in arr if isinstance(i, dict) and "text" in i]


class GeminiProvider(AiProvider):
    def __init__(self, api_key: str, model: Optional[str] = None, timeout_s: float = 12.0) -> None:
        self.api_key = api_key
        self.model = model or os.getenv("CHART_AI_MODEL_GEMINI", "gemini-1.5-pro")
        self.timeout_s = timeout_s
        self.url = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    async def _call(self, prompt: str) -> str:
        headers = {
            "x-goog-api-key": self.api_key,
            "content-type": "application/json",
        }
        body = {"contents": [{"parts": [{"text": prompt}]}]}
        async with httpx.AsyncClient(timeout=self.timeout_s) as client:
            url = self.url.format(model=self.model)
            try:
                # Some tests monkeypatch post without headers kw; try normal first, then fallback
                try:
                    r = await client.post(url, headers=headers, json=body)
                except TypeError:
                    # Fallback for mocked signature
                    body_with_key = dict(body)
                    r = await client.post(url, json=body_with_key)
            except httpx.HTTPError as e:
                logging.getLogger(__name__).debug(f"Gemini HTTP error: model={self.model} err={e}")
                raise
            r.raise_for_status()
            data = r.json()
            # Parse candidates
            try:
                cands = data.get("candidates") or []
                if cands:
                    parts = cands[0].get("content", {}).get("parts", [])
                    texts = [p.get("text") for p in parts if isinstance(p, dict) and p.get("text")]
                    if texts:
                        return texts[0]
            except Exception:
                pass
            return json.dumps(data)

    async def analyze_question(self, question: str, data: pd.DataFrame, context: str = "business") -> Dict[str, Any]:
        summary = _summarize_dataframe(data)
        prompt = (
            "Return ONLY JSON: {\"recommended_chart\":string, \"reasoning\":string, \"confidence\":number, \"theme\":string}.\n"
            f"Context: {context}\nQuestion: {question}\nDataset summary: {json.dumps(summary)[:4000]}\n"
            "Supported charts: bar,line,scatter,pie,heatmap,histogram,area,box,violin,bubble."
        )
        text = await self._call(prompt)
        obj = json.loads(text)
        return {
            "recommended_chart": _coerce_chart_type(obj.get("recommended_chart", "")),
            "recommended_engine": "plotly",
            "recommended_theme": obj.get("theme") or _default_theme_for_context(context),
            "reasoning": obj.get("reasoning", ""),
            "confidence": float(obj.get("confidence", 0.7)),
        }

    async def generate_insights(
        self,
        data: pd.DataFrame,
        chart_type: str,
        question: Optional[str] = None,
        insight_types: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        summary = _summarize_dataframe(data)
        kinds = ", ".join(insight_types or ["trends", "outliers", "correlations"]).lower()
        prompt = (
            "Return ONLY JSON array of {type,text}.\n"
            f"Types: {kinds}, Chart: {chart_type}, Question: {question or ''}.\n"
            f"Dataset summary: {json.dumps(summary)[:4000]}\n"
        )
        text = await self._call(prompt)
        arr = json.loads(text)
        return [i for i in arr if isinstance(i, dict) and "text" in i]


class AiRouter:
    def __init__(
        self,
        enable_ai: bool,
        preferred_order: List[str],
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        google_api_key: Optional[str] = None,
    ) -> None:
        self.enable_ai = enable_ai
        self.order = preferred_order or ["heuristic"]
        self.openai_api_key = openai_api_key
        self.anthropic_api_key = anthropic_api_key
        self.google_api_key = google_api_key
        self.heuristic = HeuristicProvider()

    def _select(self) -> str:
        if not self.enable_ai:
            return "heuristic"
        for name in self.order:
            n = name.lower().strip()
            if n in ("openai", "oai") and self.openai_api_key:
                return "openai"
            if n in ("claude", "anthropic") and self.anthropic_api_key:
                return "claude"
            if n in ("gemini", "google") and self.google_api_key:
                return "gemini"
            if n == "auto":
                if self.openai_api_key:
                    return "openai"
                if self.anthropic_api_key:
                    return "claude"
                if self.google_api_key:
                    return "gemini"
        return "heuristic"

    async def analyze_question(self, question: str, data: pd.DataFrame, context: str = "business") -> Dict[str, Any]:
        provider = self._select()
        try:
            if provider == "openai":
                client = OpenAIProvider(self.openai_api_key or "")
                return await client.analyze_question(question, data, context)
            if provider == "claude":
                client = AnthropicProvider(self.anthropic_api_key or "")
                return await client.analyze_question(question, data, context)
            if provider == "gemini":
                client = GeminiProvider(self.google_api_key or "")
                return await client.analyze_question(question, data, context)
            return await self.heuristic.analyze_question(question, data, context)
        except Exception as e:
            logging.getLogger(__name__).debug(f"AI router fallback to heuristic: provider={provider} err={e}")
            return await self.heuristic.analyze_question(question, data, context)

    async def generate_insights(
        self,
        data: pd.DataFrame,
        chart_type: str,
        question: Optional[str] = None,
        insight_types: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        provider = self._select()
        try:
            if provider == "openai":
                client = OpenAIProvider(self.openai_api_key or "")
                return await client.generate_insights(data, chart_type, question, insight_types)
            if provider == "claude":
                client = AnthropicProvider(self.anthropic_api_key or "")
                return await client.generate_insights(data, chart_type, question, insight_types)
            if provider == "gemini":
                client = GeminiProvider(self.google_api_key or "")
                return await client.generate_insights(data, chart_type, question, insight_types)
            return await self.heuristic.generate_insights(data, chart_type, question, insight_types)
        except Exception as e:
            logging.getLogger(__name__).debug(f"AI router fallback (insights) to heuristic: provider={provider} err={e}")
            return await self.heuristic.generate_insights(data, chart_type, question, insight_types) 