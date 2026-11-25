import logging

from google import genai

from config.settings import (
    ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
)

logger = logging.getLogger("LINKBUILD_AI_OS.AI_ROUTER")


class AIRouter:

    def __init__(self):
        self.clients = {}

        if GEMINI_API_KEY:
            self.clients["gemini"] = genai.Client(api_key=GEMINI_API_KEY)

        if OPENAI_API_KEY:
            try:
                from openai import OpenAI
                self.clients["openai"] = OpenAI(api_key=OPENAI_API_KEY)
            except ImportError:
                pass

        if ANTHROPIC_API_KEY:
            try:
                from anthropic import Anthropic
                self.clients["anthropic"] = Anthropic(api_key=ANTHROPIC_API_KEY)
            except ImportError:
                pass

        self.models = {
            "gemini": GEMINI_MODEL,
            "openai": OPENAI_MODEL,
            "anthropic": ANTHROPIC_MODEL,
        }

    def available_providers(self):
        return list(self.clients.keys())

    def _generate_gemini(self, prompt):
        candidate_models = []
        for m in (
            self.models["gemini"],
            "gemini-3-flash-preview",
            "gemini-3.1-flash-lite-preview",
            "gemini-flash-latest",
        ):
            if m and m not in candidate_models:
                candidate_models.append(m)

        last_err = None
        for model_name in candidate_models:
            try:
                response = self.clients["gemini"].models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                text = (response.text or "").strip()
                if text:
                    return model_name, text
            except Exception as err:
                last_err = err
                logger.warning("Gemini model %s failed: %s", model_name, err)
        raise last_err or RuntimeError("Gemini failed to return content.")

    def _generate_openai(self, prompt):
        model_name = self.models["openai"]
        response = self.clients["openai"].chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
        )
        text = (response.choices[0].message.content or "").strip()
        return model_name, text

    def _generate_anthropic(self, prompt):
        model_name = self.models["anthropic"]
        response = self.clients["anthropic"].messages.create(
            model=model_name,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(
            block.text for block in response.content if hasattr(block, "text")
        ).strip()
        return model_name, text

    def _call_provider(self, provider_name, prompt):
        if provider_name == "gemini":
            return self._generate_gemini(prompt)
        if provider_name == "openai":
            return self._generate_openai(prompt)
        if provider_name == "anthropic":
            return self._generate_anthropic(prompt)
        raise ValueError(f"Unsupported provider: {provider_name}")

    def generate(self, prompt: str, provider="auto"):
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        if not self.clients:
            raise RuntimeError(
                "No AI provider API keys configured. Set GEMINI_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY."
            )

        requested = (provider or "auto").lower().strip()
        if requested != "auto":
            if requested not in self.clients:
                raise RuntimeError(f"Requested AI provider '{requested}' is not configured.")
            order = [requested]
        else:
            order = [p for p in ("gemini", "openai", "anthropic") if p in self.clients]

        last_error = None
        for current_provider in order:
            try:
                used_model, result = self._call_provider(current_provider, prompt)
                if not result:
                    raise RuntimeError(f"{current_provider} returned an empty response.")
                logger.info("AI response generated using %s (%s)", current_provider, used_model)
                return {
                    "success": True,
                    "provider": current_provider,
                    "model": used_model,
                    "response": result,
                }
            except Exception as err:
                last_error = err
                logger.warning("Provider %s failed: %s", current_provider, err)

        raise last_error or RuntimeError("All AI providers failed.")


ai_router = AIRouter()
