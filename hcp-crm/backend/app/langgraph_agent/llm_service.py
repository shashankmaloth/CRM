"""
Groq LLM service for HCP CRM.
Handles model initialization and fallback logic.
"""
import json
import re
import logging
from groq import Groq
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class GroqLLMService:
    """
    Service class for interacting with Groq API.
    Supports primary (gemma2-9b-it) and fallback (llama-3.3-70b-versatile) models.
    Client is lazily initialized so the API key is read after .env is loaded.
    """

    def __init__(self):
        self._client = None
        self.primary_model = settings.PRIMARY_MODEL
        self.fallback_model = settings.FALLBACK_MODEL

    @property
    def client(self):
        """Lazy-init Groq client so it picks up the API key after startup."""
        if self._client is None:
            api_key = get_settings().GROQ_API_KEY
            if not api_key:
                raise ValueError(
                    "GROQ_API_KEY is not set. "
                    "Add it to backend/.env: GROQ_API_KEY=gsk_..."
                )
            self._client = Groq(api_key=api_key)
        return self._client

    def chat(self, messages: list, model: str = None, temperature: float = 0.1) -> str:
        """
        Send messages to Groq and return the response text.
        Falls back to secondary model on failure.
        """
        model = model or self.primary_model
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=2048,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.warning(f"Primary model {model} failed: {e}. Trying fallback.")
            if model != self.fallback_model:
                return self.chat(messages, model=self.fallback_model, temperature=temperature)
            raise

    def extract_interaction(self, raw_text: str) -> dict:
        """
        Use LLM to extract structured interaction data from natural language text.
        Returns a dict matching the interactions table schema.
        """
        system_prompt = """You are an AI assistant for a pharmaceutical CRM system.
Extract structured interaction data from the user's natural language description.

Return ONLY a valid JSON object with these exact fields (use null for missing values):
{
  "hcp_name": "string or null",
  "specialty": "string or null",
  "hospital": "string or null",
  "interaction_type": "Visit|Call|Meeting or null",
  "datetime": "ISO 8601 datetime string or null",
  "products": "comma-separated product names or null",
  "notes": "cleaned notes string or null",
  "sentiment": "positive|neutral|negative",
  "follow_up_date": "ISO 8601 datetime string or null",
  "summary": "2-3 sentence professional summary of the interaction"
}

Rules:
- sentiment must be one of: positive, neutral, negative
- interaction_type must be one of: Visit, Call, Meeting
- For relative dates like "next Monday" or "next week", use null (cannot resolve without current date)
- Extract product names accurately from pharma context
- summary should be professional and concise"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Extract interaction data from this text:\n\n{raw_text}"}
        ]

        response_text = self.chat(messages)

        # Parse JSON from response
        try:
            # Try to find JSON block in response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {e}\nResponse: {response_text}")
            # Return minimal structure on parse failure
            return {
                "hcp_name": None,
                "specialty": None,
                "hospital": None,
                "interaction_type": None,
                "datetime": None,
                "products": None,
                "notes": raw_text,
                "sentiment": "neutral",
                "follow_up_date": None,
                "summary": raw_text[:200]
            }

    def suggest_next_actions(self, interaction_data: dict) -> list:
        """
        Use LLM to suggest follow-up actions based on interaction data.
        """
        system_prompt = """You are a pharmaceutical sales strategy AI.
Based on the HCP interaction data provided, suggest 3-5 specific, actionable next steps.
Return ONLY a JSON array of strings. Each string is one action item.
Example: ["Schedule follow-up call within 7 days", "Send product samples for Januvia"]"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Suggest next actions for this interaction:\n{json.dumps(interaction_data, indent=2)}"}
        ]

        response_text = self.chat(messages)
        try:
            arr_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if arr_match:
                return json.loads(arr_match.group())
            return json.loads(response_text)
        except Exception:
            return ["Schedule a follow-up meeting", "Send product literature", "Update CRM records"]

    def summarize_interactions(self, interactions: list) -> str:
        """
        Generate a comprehensive summary of multiple interactions with an HCP.
        """
        system_prompt = """You are a pharmaceutical sales analytics AI.
Analyze the provided list of HCP interactions and generate a comprehensive summary.
Include:
1. Overall relationship trend (improving/stable/declining)
2. Key products discussed and HCP interest level
3. Sentiment trend over time
4. Opportunities identified
5. Risk alerts (if any)
Keep the summary professional and under 300 words."""

        interactions_text = json.dumps(interactions, indent=2, default=str)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Summarize these interactions:\n{interactions_text}"}
        ]

        return self.chat(messages, temperature=0.3)

    def understand_intent(self, user_message: str) -> dict:
        """
        Determine the user's intent from their message.
        Returns intent type and relevant parameters.
        """
        system_prompt = """You are an intent classifier for a pharmaceutical CRM chatbot.
Classify the user's message into one of these intents:
- log_interaction: User wants to log a new HCP interaction
- edit_interaction: User wants to edit an existing interaction
- get_history: User wants to see interaction history for an HCP
- suggest_actions: User wants suggestions for next steps
- summarize: User wants a summary of interactions
- general: General question or unclear intent

Return ONLY a JSON object:
{
  "intent": "one of the above intents",
  "hcp_name": "extracted HCP name or null",
  "interaction_id": "extracted interaction ID as integer or null",
  "confidence": 0.0 to 1.0
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        response_text = self.chat(messages)
        try:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return json.loads(response_text)
        except Exception:
            return {"intent": "log_interaction", "hcp_name": None, "interaction_id": None, "confidence": 0.5}


# Singleton instance
llm_service = GroqLLMService()
