import json
import logging
import requests
from typing import Dict, Any, List, Optional
from app.config import settings
from app.services.ai.base_provider import BaseAIProvider
from app.services.ai.smart_engine import SmartHeuristicEngine

logger = logging.getLogger(__name__)

class OpenAICompatibleProvider(BaseAIProvider):
    """
    OpenAI-compatible API Integration (OpenAI, Groq, Ollama, OpenRouter, etc.).
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.openai.com/v1",
        model_name: str = "gpt-4o-mini"
    ):
        self.api_key = api_key or settings.OPENAI_API_KEY or settings.AI_API_KEY
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self.fallback = SmartHeuristicEngine()

    def generate_form_insights(
        self,
        form_title: str,
        form_description: str,
        stats: Dict[str, Any],
        text_analysis: Dict[str, Any],
        comparisons: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        if not self.api_key and "localhost" not in self.base_url:
            return self.fallback.generate_form_insights(form_title, form_description, stats, text_analysis, comparisons)

        try:
            url = f"{self.base_url}/chat/completions"
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            system_prompt = (
                "You are FormMind AI, a specialized survey analytics intelligence agent. "
                "Analyze verified statistics strictly and return JSON with keys: "
                "'executive_summary', 'facts', 'interpretations', 'recommendations', 'key_insights'. "
                "NEVER fabricate numbers."
            )
            user_prompt = f"""
Survey Title: {form_title}
Total Responses: {stats.get('basic', {}).get('total_responses')}
Statistics: {json.dumps(stats)}
Comparisons: {json.dumps(comparisons)}
Text Analysis: {json.dumps(text_analysis)}
"""
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.2
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                return json.loads(content)
        except Exception as e:
            logger.warning(f"OpenAI compatible request failed: {e}. Falling back to SmartEngine.")

        return self.fallback.generate_form_insights(form_title, form_description, stats, text_analysis, comparisons)

    def answer_chat_query(
        self,
        user_message: str,
        form_context: Dict[str, Any],
        grounded_facts: Dict[str, Any],
        chat_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        if not self.api_key and "localhost" not in self.base_url:
            return self.fallback.answer_chat_query(user_message, form_context, grounded_facts, chat_history)

        try:
            url = f"{self.base_url}/chat/completions"
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            system_prompt = (
                f"You are FormMind AI, an intelligent conversational AI survey analyst and assistant for '{form_context.get('title')}'.\n"
                f"Total Verified Responses: {form_context.get('total_responses')} | Completion Rate: {form_context.get('completion_rate')}\n\n"
                "You have full conversational memory of past conversation turns. Answer both specific questions grounded in the verified dataset "
                "and general questions (such as survey methodology, data analysis advice, statistics concepts, and helpful follow-ups).\n\n"
                f"VERIFIED GROUND-TRUTH FORM FACTS:\n{json.dumps(grounded_facts, indent=2)}"
            )

            messages = [{"role": "system", "content": system_prompt}]
            # Add past turns excluding the last if it's already the current user message
            prev_turns = chat_history[:-1] if (chat_history and chat_history[-1].get("content") == user_message) else chat_history
            for msg in prev_turns[-8:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": user_message})

            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": 0.3
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                return {
                    "role": "assistant",
                    "content": content,
                    "chart_data": grounded_facts.get("chart_data"),
                    "grounded_facts": grounded_facts,
                    "intent_detected": grounded_facts.get("intent", "general_query")
                }
        except Exception as e:
            logger.warning(f"OpenAI compatible chat failed: {e}")

        return self.fallback.answer_chat_query(user_message, form_context, grounded_facts, chat_history)

    def generate_report_markdown(
        self,
        form_title: str,
        stats: Dict[str, Any],
        text_analysis: Dict[str, Any],
        comparisons: List[Dict[str, Any]],
        report_type: str = "full",
        custom_instructions: Optional[str] = None
    ) -> str:
        return self.fallback.generate_report_markdown(form_title, stats, text_analysis, comparisons, report_type, custom_instructions)
