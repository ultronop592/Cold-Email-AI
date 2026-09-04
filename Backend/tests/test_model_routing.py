import unittest
import sys
import os
from unittest.mock import patch

# Ensure Backend is on the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from llms.groq_client import (
    resolve_model_routing,
    get_analyzer_llm,
    get_writer_llm,
    create_chat_model,
    MODEL_70B,
    MODEL_8B,
    llm,
    llm_large
)
from langchain_core.runnables.fallbacks import RunnableWithFallbacks
from langchain_groq import ChatGroq


class TestModelRouting(unittest.TestCase):

    def test_default_quality_routing(self):
        with patch.dict(os.environ, {}, clear=True):
            routing = resolve_model_routing()
            self.assertEqual(routing["mode"], "quality")
            self.assertEqual(routing["analyzer_model"], MODEL_70B)
            self.assertEqual(routing["writer_model"], MODEL_70B)
            self.assertEqual(routing["fallback_model"], MODEL_8B)

    def test_balanced_mode_routing(self):
        with patch.dict(os.environ, {"GROQ_ROUTING_MODE": "balanced"}, clear=True):
            routing = resolve_model_routing()
            self.assertEqual(routing["mode"], "balanced")
            self.assertEqual(routing["analyzer_model"], MODEL_8B)
            self.assertEqual(routing["writer_model"], MODEL_70B)
            self.assertEqual(routing["fallback_model"], MODEL_8B)

    def test_fast_mode_routing(self):
        with patch.dict(os.environ, {"GROQ_ROUTING_MODE": "fast"}, clear=True):
            routing = resolve_model_routing()
            self.assertEqual(routing["mode"], "fast")
            self.assertEqual(routing["analyzer_model"], MODEL_8B)
            self.assertEqual(routing["writer_model"], MODEL_8B)
            self.assertEqual(routing["fallback_model"], MODEL_70B)

    def test_explicit_env_overrides(self):
        env = {
            "GROQ_ROUTING_MODE": "quality",
            "GROQ_ANALYZER_MODEL": "custom-analyzer-model",
            "GROQ_WRITER_MODEL": "custom-writer-model",
            "GROQ_FALLBACK_MODEL": "custom-fallback-model"
        }
        with patch.dict(os.environ, env, clear=True):
            routing = resolve_model_routing()
            self.assertEqual(routing["analyzer_model"], "custom-analyzer-model")
            self.assertEqual(routing["writer_model"], "custom-writer-model")
            self.assertEqual(routing["fallback_model"], "custom-fallback-model")

    def test_analyzer_model_hyperparameters(self):
        analyzer = get_analyzer_llm(enable_fallback=False)
        self.assertIsInstance(analyzer, ChatGroq)
        self.assertEqual(analyzer.temperature, 0.2)
        self.assertEqual(analyzer.max_tokens, 1500)

    def test_writer_model_hyperparameters(self):
        writer = get_writer_llm(enable_fallback=False)
        self.assertIsInstance(writer, ChatGroq)
        self.assertEqual(writer.temperature, 0.7)
        self.assertEqual(writer.max_tokens, 2000)

    def test_fallback_chain_construction(self):
        analyzer_chain = get_analyzer_llm(enable_fallback=True)
        self.assertIsInstance(analyzer_chain, RunnableWithFallbacks)
        self.assertGreater(len(analyzer_chain.fallbacks), 0)

        writer_chain = get_writer_llm(enable_fallback=True)
        self.assertIsInstance(writer_chain, RunnableWithFallbacks)
        self.assertGreater(len(writer_chain.fallbacks), 0)

    def test_backward_compatibility_exports(self):
        self.assertIsNotNone(llm)
        self.assertIsNotNone(llm_large)
        self.assertTrue(hasattr(llm, "invoke") or hasattr(llm, "ainvoke"))
        self.assertTrue(hasattr(llm_large, "invoke") or hasattr(llm_large, "ainvoke"))


if __name__ == "__main__":
    unittest.main()
