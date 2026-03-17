import os
import time
from langchain_groq import ChatGroq
from langchain_core.callbacks import BaseCallbackHandler
from dotenv import load_dotenv

load_dotenv()

class PipelineLogger(BaseCallbackHandler):
    """Logs every llm Call - token, time errors"""
    def on_llm_start(self, serialized, prompts, **kwargs):
        self._start = time.time()
        prompt_len = sum(len(p) for p in prompts)
        print(f"\n[LLM] call Started | Prompt: {prompt_len} chars")

    def on_llm_end(self, response, **kwargs):
        duration = round(time.time() - self._start, 2)
        usage = response.llm_output.get("token_usage", {}) if response.llm_output else {}
        print(
            f"[LLM] Done in {duration}s | "
            f"Tokens: {usage.get('total_tokens', '?')} "
            f"(prompt: {usage.get('prompt_tokens', '?')} "
            f"completion: {usage.get('completion_tokens', '?')})"
        )

    def on_llm_error(self, error, **kwargs):
        print(f"[LLM] Error: {error}")

# for combined analyser - analyses only 
llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
    temperature=0.3,
    max_tokens=800,
    api_key=os.getenv("GROQ_API_KEY"),
    callbacks=[PipelineLogger()]
)

# for variants generator - 2 emails + reasoning needs more tokens
llm_large = ChatGroq(
    model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
    temperature=0.7,
    max_tokens=1500,
    api_key=os.getenv("GROQ_API_KEY"),
    callbacks=[PipelineLogger()]
)