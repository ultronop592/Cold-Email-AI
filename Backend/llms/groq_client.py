import os
import time
from typing import Dict, Any, Optional
from langchain_groq import ChatGroq
from langchain_core.callbacks import BaseCallbackHandler
from dotenv import load_dotenv

load_dotenv()

# Standard Groq Model Profiles
MODEL_70B = "llama-3.3-70b-versatile"
MODEL_8B = "llama-3.1-8b-instant"


class PipelineLogger(BaseCallbackHandler):
    """Logs every LLM call — token usage, duration, and errors."""
    def on_llm_start(self, serialized, prompts, **kwargs):
        self._start = time.time()
        prompt_len = sum(len(p) for p in prompts)
        model_name = kwargs.get("invocation_params", {}).get("model_name", "unknown")
        print(f"\n[LLM] Call started ({model_name}) | Prompt: {prompt_len} chars")

    def on_llm_end(self, response, **kwargs):
        duration = round(time.time() - self._start, 2)
        usage = response.llm_output.get("token_usage", {}) if response.llm_output else {}
        print(
            f"[LLM] Completed in {duration}s | "
            f"Tokens: {usage.get('total_tokens', '?')} "
            f"(prompt: {usage.get('prompt_tokens', '?')} "
            f"completion: {usage.get('completion_tokens', '?')})"
        )

    def on_llm_error(self, error, **kwargs):
        print(f"[LLM] Error encountered: {error}")


def resolve_model_routing() -> Dict[str, str]:
    """
    Resolve model names based on routing mode and environment variables.
    
    Supported GROQ_ROUTING_MODE values:
    - 'quality' (default): 70B for both tasks, with 8B as fallback
    - 'balanced': 8B for extraction/analysis (fast, low-TPM), 70B for copywriting
    - 'fast': 8B for both tasks (sub-second throughput)
    """
    mode = os.getenv("GROQ_ROUTING_MODE", "quality").strip().lower()

    if mode in ("fast",):
        analyzer_model = MODEL_8B
        writer_model = MODEL_8B
        fallback_model = MODEL_70B
    elif mode in ("balanced", "cost_saver"):
        analyzer_model = MODEL_8B
        writer_model = MODEL_70B
        fallback_model = MODEL_8B
    else:  # 'quality' / default
        legacy_model = os.getenv("GROQ_MODEL", MODEL_70B)
        analyzer_model = legacy_model
        writer_model = legacy_model
        fallback_model = MODEL_8B

    # Allow fine-grained environment variable overrides
    analyzer_model = os.getenv("GROQ_ANALYZER_MODEL", analyzer_model)
    writer_model = os.getenv("GROQ_WRITER_MODEL", writer_model)
    fallback_model = os.getenv("GROQ_FALLBACK_MODEL", fallback_model)

    return {
        "mode": mode,
        "analyzer_model": analyzer_model,
        "writer_model": writer_model,
        "fallback_model": fallback_model
    }


def create_chat_model(
    model_name: str,
    temperature: float,
    max_tokens: int,
    api_key: Optional[str] = None
) -> ChatGroq:
    """Instantiate a ChatGroq client with standard settings and pipeline logging."""
    key = api_key or os.getenv("GROQ_API_KEY") or "gsk_dummy_placeholder_for_offline"
    return ChatGroq(
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        api_key=key,
        callbacks=[PipelineLogger()]
    )


def get_analyzer_llm(enable_fallback: bool = True):
    """
    Task 1: Job Fit Analysis & Information Extraction.
    Configured with low temperature (0.2) for strict structured JSON output
    and expanded token limit (1500) to prevent payload truncation.
    """
    routing = resolve_model_routing()
    primary = create_chat_model(
        model_name=routing["analyzer_model"],
        temperature=0.2,
        max_tokens=1500
    )

    if enable_fallback and routing["fallback_model"] != routing["analyzer_model"]:
        fallback = create_chat_model(
            model_name=routing["fallback_model"],
            temperature=0.2,
            max_tokens=1500
        )
        return primary.with_fallbacks([fallback])

    return primary


def get_writer_llm(enable_fallback: bool = True):
    """
    Task 2: Strategic Cold Email Generation & Copywriting.
    Configured with medium-high temperature (0.7) for persuasive, distinctive variants
    and 2000 tokens for 2 multi-paragraph emails with structured reasoning.
    """
    routing = resolve_model_routing()
    primary = create_chat_model(
        model_name=routing["writer_model"],
        temperature=0.7,
        max_tokens=2000
    )

    if enable_fallback and routing["fallback_model"] != routing["writer_model"]:
        fallback = create_chat_model(
            model_name=routing["fallback_model"],
            temperature=0.7,
            max_tokens=2000
        )
        return primary.with_fallbacks([fallback])

    return primary


# Exported instances for direct drop-in usage across chains
llm = get_analyzer_llm()
llm_large = get_writer_llm()