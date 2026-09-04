import json
import logging
import requests
from typing import Dict, Any, List, Optional
from app.config import settings
from app.services.ai.base_provider import BaseAIProvider
from app.services.ai.smart_engine import SmartHeuristicEngine

logger = logging.getLogger(__name__)

class GeminiProvider(BaseAIProvider):
    """
    Google Gemini API Integration for FormMind AI.
    Falls back gracefully to SmartHeuristicEngine if keys are absent or network errors occur.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY or settings.AI_API_KEY
        self.model_name = model_name or settings.MODEL_NAME or "gemini-1.5-flash"
        self.fallback = SmartHeuristicEngine()

    def generate_form_insights(
        self,
        form_title: str,
        form_description: str,
        stats: Dict[str, Any],
        text_analysis: Dict[str, Any],
        comparisons: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        if not self.api_key:
            return self.fallback.generate_form_insights(form_title, form_description, stats, text_analysis, comparisons)

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
            prompt = f"""
You are FormMind AI, a world-class survey data scientist.
Analyze the following verified survey statistics and generate structured insights.

CRITICAL RULES:
1. NEVER invent any statistics or percentages. Use ONLY the data provided below.
2. Distinguish clearly between FACT (exact numbers from data), INTERPRETATION (what the trends indicate), and RECOMMENDATION (action steps).
3. Return output strictly in valid JSON with keys: "executive_summary", "facts", "interpretations", "recommendations", "key_insights".

DATASET SCHEMA & STATS:
Form Title: {form_title}
Total Responses: {stats.get('basic', {}).get('total_responses')}
Completion Rate: {stats.get('basic', {}).get('completion_rate')}
Numerical Analysis: {json.dumps(stats.get('numerical', {}))}
Categorical Analysis: {json.dumps(stats.get('categorical', {}))}
Multiselect Analysis: {json.dumps(stats.get('multiselect', {}))}
Comparative Analysis: {json.dumps(comparisons)}
Open-Ended Text Analysis: {json.dumps(text_analysis)}
"""
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "temperature": 0.2
                }
            }
            resp = requests.post(url, json=payload, timeout=20)
            if resp.status_code == 200:
                result_json = resp.json()
                text_content = result_json["candidates"][0]["content"]["parts"][0]["text"]
                parsed = json.loads(text_content)
                return parsed
        except Exception as e:
            logger.warning(f"Gemini API request failed: {e}. Falling back to SmartEngine.")

        return self.fallback.generate_form_insights(form_title, form_description, stats, text_analysis, comparisons)

    def answer_chat_query(
        self,
        user_message: str,
        form_context: Dict[str, Any],
        grounded_facts: Dict[str, Any],
        chat_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        if not self.api_key:
            return self.fallback.answer_chat_query(user_message, form_context, grounded_facts, chat_history)

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
            
            history_lines = []
            if chat_history:
                for msg in chat_history[:-1]:
                    r = "User" if msg.get("role") == "user" else "Assistant"
                    history_lines.append(f"{r}: {msg.get('content', '')}")
            history_text = "\n".join(history_lines) if history_lines else "No previous messages in this session."

            prompt = f"""
You are FormMind AI, a world-class conversational AI survey analyst and assistant.
You are helping the user analyze verified responses for the form: "{form_context.get('title')}".
Total Responses: {form_context.get('total_responses')} | Completion Rate: {form_context.get('completion_rate')}

CONVERSATION MEMORY & PREVIOUS TURNS:
{history_text}

VERIFIED FORM RESPONDENTS & QUESTION DATA:
{json.dumps(grounded_facts.get('dataset_preview', grounded_facts), indent=2)}

DETERMINISTIC VERIFIED FACTS:
{json.dumps({k: v for k, v in grounded_facts.items() if k != 'dataset_preview'}, indent=2)}

CURRENT USER MESSAGE:
{user_message}

CRITICAL INSTRUCTIONS:
1. You have FULL conversational memory of the previous turns in CONVERSATION MEMORY above. When the user asks follow-up questions (e.g. "who are they?", "what about them?", "what was my first question?"), seamlessly use the conversation history to answer accurately.
2. You can answer BOTH specific questions about the form dataset AND general questions (e.g. "what is standard deviation?", "how to improve surveys?", data concepts, definitions, advice).
3. If the user asks about specific form data, respondent names, questions, or statistics, ground your answer 100% in the verified data provided above.
4. If 'direct_answer' is provided in the verified facts, incorporate it as the ground-truth answer.
5. Format your response cleanly with markdown (bolding, bullet points, numbered lists).
"""
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.2}
            }
            resp = requests.post(url, json=payload, timeout=15)
            if resp.status_code == 200:
                res_data = resp.json()
                reply = res_data["candidates"][0]["content"]["parts"][0]["text"]
                return {
                    "role": "assistant",
                    "content": reply,
                    "chart_data": grounded_facts.get("chart_data"),
                    "grounded_facts": grounded_facts,
                    "intent_detected": grounded_facts.get("intent", "general_query")
                }
        except Exception as e:
            logger.warning(f"Gemini Chat query failed: {e}")

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
        # Fallback generates clean, perfectly formatted markdown
        return self.fallback.generate_report_markdown(form_title, stats, text_analysis, comparisons, report_type, custom_instructions)
