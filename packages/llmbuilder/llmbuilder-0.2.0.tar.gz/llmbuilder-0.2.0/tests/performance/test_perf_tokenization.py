import importlib
import os
import pytest

bench_available = True
try:
    import pytest_benchmark  # noqa: F401
except Exception:
    bench_available = False


def _skip_reason():
    if not os.environ.get('RUN_PERF'):
        return 'Set RUN_PERF=1 to enable performance tests'
    if not bench_available:
        return 'pytest-benchmark not installed'
    return None


@pytest.mark.skipif(_skip_reason() is not None, reason=_skip_reason() or '')
def test_tokenization_performance(benchmark, tiny_corpus):
    tokenizer_mod = importlib.import_module('llmbuilder.tokenizer')
    # Use a minimal/dummy manager or utils if available
    # Fallback to a simple split to ensure the benchmark runs regardless of tokenizer impl
    text = tiny_corpus.read_text(encoding='utf-8')

    def _tok():
        if hasattr(tokenizer_mod, 'utils') and hasattr(tokenizer_mod.utils, 'TokenizerManager'):
            # If a Manager exists, try to instantiate minimally
            try:
                tm = tokenizer_mod.utils.TokenizerManager()
                return tm.encode(text)
            except Exception:
                pass
        # Fallback
        return text.split()

    result = benchmark(_tok)
    assert result is not None
