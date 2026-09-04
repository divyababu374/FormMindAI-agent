from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BaseAIProvider(ABC):
    """
    Abstract AI Provider Interface for FormMind AI.
    Ensures seamless switching between Gemini, OpenAI, Groq, Ollama, and Built-in engine.
    """

    @abstractmethod
    def generate_form_insights(
        self,
        form_title: str,
        form_description: str,
        stats: Dict[str, Any],
        text_analysis: Dict[str, Any],
        comparisons: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generates executive summary, structured facts, interpretations, and recommendations.
        """
        pass

    @abstractmethod
    def answer_chat_query(
        self,
        user_message: str,
        form_context: Dict[str, Any],
        grounded_facts: Dict[str, Any],
        chat_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Answers a user question grounded in calculated statistical facts and retrieved data.
        """
        pass

    @abstractmethod
    def generate_report_markdown(
        self,
        form_title: str,
        stats: Dict[str, Any],
        text_analysis: Dict[str, Any],
        comparisons: List[Dict[str, Any]],
        report_type: str,
        custom_instructions: Optional[str] = None
    ) -> str:
        """
        Generates full structured markdown report.
        """
        pass
