
import logging

from google import genai

from config.settings import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
)

logger = logging.getLogger("LINKBUILD_AI_OS.AI_ROUTER")


class AIRouter:

    def __init__(self):
        self.clients = {}

        if GEMINI_API_KEY:
            self.clients["gemini"] = genai.Client(
                api_key=GEMINI_API_KEY
            )

        self.models = {
            "gemini": GEMINI_MODEL,
        }

    def available_providers(self):
        return list(self.clients.keys())

    def _generate(self, prompt):

        if "gemini" not in self.clients:
            raise RuntimeError(
                "Gemini API key is not configured."
            )

        response = self.clients["gemini"].models.generate_content(
            model=self.models["gemini"],
            contents=prompt,
        )

        return response.text or ""

    def generate(self, prompt: str, provider=None):

        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        if provider and provider.lower() not in ("gemini", "auto"):
            raise ValueError(
                "Only Gemini provider is enabled."
            )

        if "gemini" not in self.clients:
            raise RuntimeError(
                "Gemini API key is missing. Check your .env file."
            )

        try:
            result = self._generate(prompt)

            if not result.strip():
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            logger.info("AI response generated using Gemini")

            return {
                "success": True,
                "provider": "gemini",
                "model": self.models["gemini"],
                "response": result,
            }

        except Exception:
            logger.exception("Gemini provider failed")
            raise


ai_router = AIRouter()
