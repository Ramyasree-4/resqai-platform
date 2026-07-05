"""
ResQAI – LangSmith Tracer Unit Tests

Tests:
  - Module init with tracing disabled (no API key)
  - Module init with tracing enabled (mocked client)
  - AITrace context manager: inputs, outputs, tags, metadata
  - Token tracking
  - Fallback event recording
  - Error recording
  - trace_ai_call convenience wrapper
  - langsmith_status() helper
  - Decorator langsmith_trace
  - Graceful no-op when LangSmith is unavailable
  - LangSmith client interaction (create_run + update_run)
"""
import os
import time
import pytest
from unittest.mock import MagicMock, patch, call

# ── env vars before imports ───────────────────────────────────────────────────
os.environ.setdefault("FIREBASE_PROJECT_ID", "test")
os.environ.setdefault("FIREBASE_STORAGE_BUCKET", "test.appspot.com")
os.environ.setdefault("FIREBASE_WEB_API_KEY", "test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-minimum-32-characters!!")


# ═══════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════

def _reset_module_state(available: bool = False, client=None):
    """Reset langsmith_tracer module globals between tests."""
    import app.ai.langsmith_tracer as mod
    mod._LANGSMITH_AVAILABLE = available
    mod._client = client


# ═══════════════════════════════════════════════════════
# INIT TESTS
# ═══════════════════════════════════════════════════════

class TestLangSmithInit:

    def test_disabled_when_tracing_false(self):
        with patch.dict(os.environ, {"LANGCHAIN_TRACING_V2": "false"}, clear=False):
            _reset_module_state()
            from app.ai.langsmith_tracer import init_langsmith
            result = init_langsmith()
            assert result is False

    def test_disabled_when_no_api_key(self):
        env = {
            "LANGCHAIN_TRACING_V2": "true",
            "LANGSMITH_API_KEY": "",
            "LANGCHAIN_API_KEY": "",
        }
        with patch.dict(os.environ, env, clear=False):
            _reset_module_state()
            from app.ai.langsmith_tracer import init_langsmith
            result = init_langsmith()
            assert result is False

    def test_enabled_with_valid_key_and_flag(self):
        mock_client = MagicMock()
        mock_client.list_projects.return_value = [MagicMock(name="ResQAI")]

        env = {
            "LANGCHAIN_TRACING_V2": "true",
            "LANGSMITH_API_KEY": "ls-test-api-key-valid",
            "LANGCHAIN_PROJECT": "ResQAI",
        }
        with patch.dict(os.environ, env, clear=False):
            with patch("langsmith.Client", return_value=mock_client):
                _reset_module_state()
                from app.ai.langsmith_tracer import init_langsmith
                result = init_langsmith()
                assert result is True

    def test_creates_project_if_not_exists(self):
        mock_client = MagicMock()
        mock_client.list_projects.return_value = []  # No projects

        env = {
            "LANGCHAIN_TRACING_V2": "true",
            "LANGSMITH_API_KEY": "ls-test-key",
            "LANGCHAIN_PROJECT": "ResQAI",
        }
        with patch.dict(os.environ, env, clear=False):
            with patch("langsmith.Client", return_value=mock_client):
                _reset_module_state()
                from app.ai.langsmith_tracer import init_langsmith
                init_langsmith()
                mock_client.create_project.assert_called_once_with(
                    "ResQAI", description="ResQAI Disaster Response AI"
                )

    def test_handles_import_error_gracefully(self):
        env = {
            "LANGCHAIN_TRACING_V2": "true",
            "LANGSMITH_API_KEY": "ls-key",
        }
        with patch.dict(os.environ, env, clear=False):
            with patch.dict("sys.modules", {"langsmith": None}):
                _reset_module_state()
                from app.ai.langsmith_tracer import init_langsmith
                result = init_langsmith()
                # Should return False without raising
                assert result is False

    def test_handles_network_error_gracefully(self):
        mock_client = MagicMock()
        mock_client.list_projects.side_effect = ConnectionError("No network")

        env = {
            "LANGCHAIN_TRACING_V2": "true",
            "LANGSMITH_API_KEY": "ls-key",
        }
        with patch.dict(os.environ, env, clear=False):
            with patch("langsmith.Client", return_value=mock_client):
                _reset_module_state()
                from app.ai.langsmith_tracer import init_langsmith
                # Should not raise — graceful degradation
                try:
                    init_langsmith()
                except Exception as e:
                    pytest.fail(f"init_langsmith raised unexpectedly: {e}")


# ═══════════════════════════════════════════════════════
# AITRACE CONTEXT MANAGER TESTS
# ═══════════════════════════════════════════════════════

class TestAITrace:

    def _make_mock_client(self):
        mock_client = MagicMock()
        mock_run = MagicMock()
        mock_run.id = str(__import__("uuid").uuid4())
        mock_client.create_run.return_value = mock_run
        return mock_client, mock_run

    def test_no_op_when_langsmith_disabled(self):
        """When LangSmith is disabled, AITrace runs cleanly without any client calls."""
        _reset_module_state(available=False, client=None)
        from app.ai.langsmith_tracer import AITrace

        with AITrace("test_op", "mistral-large-latest") as trace:
            trace.set_response("some response")
            trace.set_tokens(100, 50)

        # No exception — clean no-op
        assert trace.response_text == "some response"
        assert trace.token_usage["total_tokens"] == 150

    def test_create_run_called_with_correct_inputs(self):
        mock_client, mock_run = self._make_mock_client()
        _reset_module_state(available=True, client=mock_client)

        from app.ai.langsmith_tracer import AITrace

        with AITrace(
            operation="analyze_incident",
            model="mistral-large-latest",
            incident_id="INC-2024-TEST001",
            prompt="Analyze this flood...",
            metadata={"district": "Khurda"},
        ) as trace:
            trace.set_response("FLOOD CRITICAL")

        # create_run was called
        mock_client.create_run.assert_called_once()
        call_kwargs = mock_client.create_run.call_args

        # Verify inputs
        inputs = call_kwargs.kwargs.get("inputs") or call_kwargs[1].get("inputs") or {}
        assert inputs.get("model") == "mistral-large-latest"
        assert "Analyze this flood" in inputs.get("prompt", "")
        assert inputs.get("incident_id") == "INC-2024-TEST001"

    def test_update_run_called_on_exit(self):
        mock_client, mock_run = self._make_mock_client()
        _reset_module_state(available=True, client=mock_client)

        from app.ai.langsmith_tracer import AITrace

        with AITrace("test_update", "gemini-1.5-pro") as trace:
            trace.set_response("response text")

        # update_run was called
        mock_client.update_run.assert_called_once()

    def test_update_run_includes_latency(self):
        mock_client, mock_run = self._make_mock_client()
        _reset_module_state(available=True, client=mock_client)

        from app.ai.langsmith_tracer import AITrace

        with AITrace("test_latency", "mistral-large-latest") as trace:
            time.sleep(0.01)  # ensure measurable latency
            trace.set_response("ok")

        update_kwargs = mock_client.update_run.call_args
        outputs = update_kwargs.kwargs.get("outputs") or update_kwargs[1].get("outputs", {})
        assert outputs.get("latency_ms", 0) > 0

    def test_token_usage_recorded(self):
        mock_client, _ = self._make_mock_client()
        _reset_module_state(available=True, client=mock_client)

        from app.ai.langsmith_tracer import AITrace

        with AITrace("token_test", "mistral-large-latest") as trace:
            trace.set_tokens(prompt_tokens=512, completion_tokens=256)

        assert trace.token_usage["prompt_tokens"] == 512
        assert trace.token_usage["completion_tokens"] == 256
        assert trace.token_usage["total_tokens"] == 768

        update_kwargs = mock_client.update_run.call_args
        outputs = update_kwargs.kwargs.get("outputs") or {}
        assert outputs.get("token_usage", {}).get("total_tokens") == 768

    def test_fallback_recorded_in_outputs(self):
        mock_client, _ = self._make_mock_client()
        _reset_module_state(available=True, client=mock_client)

        from app.ai.langsmith_tracer import AITrace

        with AITrace("fallback_test", "mistral-large-latest") as trace:
            trace.set_fallback("mistral_rate_limit")

        assert trace.fallback_triggered is True
        assert trace.fallback_reason == "mistral_rate_limit"

        update_kwargs = mock_client.update_run.call_args
        outputs = update_kwargs.kwargs.get("outputs") or {}
        assert outputs.get("fallback_triggered") is True
        assert outputs.get("fallback_reason") == "mistral_rate_limit"

    def test_error_recorded_on_run(self):
        mock_client, _ = self._make_mock_client()
        _reset_module_state(available=True, client=mock_client)

        from app.ai.langsmith_tracer import AITrace

        with AITrace("error_test", "gemini-1.5-pro") as trace:
            trace.set_error("HTTP 500 Internal Server Error")

        update_kwargs = mock_client.update_run.call_args
        assert update_kwargs.kwargs.get("error") == "HTTP 500 Internal Server Error"

    def test_retry_count_recorded(self):
        mock_client, _ = self._make_mock_client()
        _reset_module_state(available=True, client=mock_client)

        from app.ai.langsmith_tracer import AITrace

        with AITrace("retry_test", "mistral-large-latest") as trace:
            trace.set_retry(3)

        assert trace.retry_count == 3
        update_kwargs = mock_client.update_run.call_args
        outputs = update_kwargs.kwargs.get("outputs") or {}
        assert outputs.get("retry_count") == 3

    def test_uncaught_exception_does_not_suppress(self):
        mock_client, _ = self._make_mock_client()
        _reset_module_state(available=True, client=mock_client)

        from app.ai.langsmith_tracer import AITrace

        with pytest.raises(ValueError):
            with AITrace("exc_test", "mistral-large-latest") as trace:
                raise ValueError("deliberate test error")

    def test_uncaught_exception_captured_in_error(self):
        mock_client, _ = self._make_mock_client()
        _reset_module_state(available=True, client=mock_client)

        from app.ai.langsmith_tracer import AITrace

        try:
            with AITrace("exc_capture", "gemini-1.5-pro") as trace:
                raise RuntimeError("test runtime error")
        except RuntimeError:
            pass

        # error field should be set on the update call
        update_kwargs = mock_client.update_run.call_args
        assert update_kwargs.kwargs.get("error") is not None
        assert "test runtime error" in update_kwargs.kwargs.get("error", "")

    def test_langsmith_failure_does_not_crash_app(self):
        """If LangSmith itself fails, the application must continue."""
        mock_client = MagicMock()
        mock_client.create_run.side_effect = Exception("LangSmith connection dropped")
        _reset_module_state(available=True, client=mock_client)

        from app.ai.langsmith_tracer import AITrace

        # Must not raise
        result = "not set"
        with AITrace("crash_test", "mistral-large-latest") as trace:
            result = "inside context"

        assert result == "inside context"

    def test_response_truncated_to_2000_chars(self):
        _reset_module_state(available=False)
        from app.ai.langsmith_tracer import AITrace

        long_response = "A" * 5000
        with AITrace("truncate_test", "mistral") as trace:
            trace.set_response(long_response)

        assert len(trace.response_text) == 2000

    def test_prompt_truncated_in_inputs(self):
        mock_client, _ = self._make_mock_client()
        _reset_module_state(available=True, client=mock_client)

        from app.ai.langsmith_tracer import AITrace

        long_prompt = "P" * 10000
        with AITrace("prompt_trunc", "mistral", prompt=long_prompt) as trace:
            pass

        inputs = mock_client.create_run.call_args.kwargs.get("inputs") or {}
        assert len(inputs.get("prompt", "")) <= 4000


# ═══════════════════════════════════════════════════════
# trace_ai_call CONTEXT MANAGER TESTS
# ═══════════════════════════════════════════════════════

class TestTraceAiCall:

    def test_returns_aitrace_instance(self):
        _reset_module_state(available=False)
        from app.ai.langsmith_tracer import trace_ai_call, AITrace

        with trace_ai_call("test_op", "mistral") as trace:
            assert isinstance(trace, AITrace)

    def test_all_params_passed_correctly(self):
        _reset_module_state(available=False)
        from app.ai.langsmith_tracer import trace_ai_call

        with trace_ai_call(
            "analyze_incident",
            "gemini-1.5-pro",
            incident_id="INC-123",
            prompt="test prompt",
            metadata={"key": "val"},
        ) as trace:
            assert trace.operation == "analyze_incident"
            assert trace.model == "gemini-1.5-pro"
            assert trace.incident_id == "INC-123"
            assert trace.prompt == "test prompt"
            assert trace.metadata["key"] == "val"

    def test_noop_when_disabled(self):
        _reset_module_state(available=False)
        from app.ai.langsmith_tracer import trace_ai_call

        executed = False
        with trace_ai_call("noop_test", "mistral") as trace:
            executed = True
            trace.set_tokens(100, 50)

        assert executed is True

    def test_exception_propagates(self):
        _reset_module_state(available=False)
        from app.ai.langsmith_tracer import trace_ai_call

        with pytest.raises(RuntimeError):
            with trace_ai_call("exc_test", "mistral"):
                raise RuntimeError("propagate me")


# ═══════════════════════════════════════════════════════
# langsmith_status TESTS
# ═══════════════════════════════════════════════════════

class TestLangSmithStatus:

    def test_status_disabled(self):
        _reset_module_state(available=False, client=None)
        from app.ai.langsmith_tracer import langsmith_status

        with patch.dict(os.environ, {"LANGCHAIN_TRACING_V2": "false"}, clear=False):
            status = langsmith_status()

        assert status["enabled"] is False
        assert status["project"] is None

    def test_status_enabled(self):
        mock_client = MagicMock()
        _reset_module_state(available=True, client=mock_client)

        import app.ai.langsmith_tracer as mod
        mod._project = "ResQAI"

        from app.ai.langsmith_tracer import langsmith_status

        with patch.dict(os.environ, {
            "LANGCHAIN_TRACING_V2": "true",
            "LANGSMITH_API_KEY": "ls-key",
        }, clear=False):
            status = langsmith_status()

        assert status["enabled"] is True
        assert status["project"] == "ResQAI"
        assert status["tracing_v2"] is True
        assert status["has_api_key"] is True

    def test_status_has_all_required_keys(self):
        _reset_module_state(available=False)
        from app.ai.langsmith_tracer import langsmith_status
        status = langsmith_status()
        required_keys = {"enabled", "project", "endpoint", "tracing_v2", "has_api_key"}
        assert required_keys.issubset(status.keys())


# ═══════════════════════════════════════════════════════
# DECORATOR TEST
# ═══════════════════════════════════════════════════════

class TestLangSmithDecorator:

    def test_decorator_calls_function(self):
        _reset_module_state(available=False)
        from app.ai.langsmith_tracer import langsmith_trace

        @langsmith_trace(operation="test_classify", model="mistral-large-latest")
        def classify(data):
            return {"result": data}

        result = classify("flood_description")
        assert result == {"result": "flood_description"}

    def test_decorator_preserves_return_value(self):
        _reset_module_state(available=False)
        from app.ai.langsmith_tracer import langsmith_trace

        @langsmith_trace(operation="test_op", model="gemini-1.5-pro")
        def my_func(x, y):
            return x + y

        assert my_func(3, 4) == 7

    def test_decorator_propagates_exceptions(self):
        _reset_module_state(available=False)
        from app.ai.langsmith_tracer import langsmith_trace

        @langsmith_trace(operation="fail_op", model="mistral")
        def fail_func():
            raise ValueError("expected failure")

        with pytest.raises(ValueError, match="expected failure"):
            fail_func()

    def test_decorator_preserves_function_name(self):
        _reset_module_state(available=False)
        from app.ai.langsmith_tracer import langsmith_trace

        @langsmith_trace(operation="named", model="mistral")
        def my_named_function():
            pass

        assert my_named_function.__name__ == "my_named_function"
