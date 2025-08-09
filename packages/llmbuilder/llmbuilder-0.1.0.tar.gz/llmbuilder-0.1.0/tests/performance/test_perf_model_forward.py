import importlib
import os
import pytest
try:
    import torch  # type: ignore
except Exception:  # torch not installed in this environment
    torch = None

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
    if torch is None:
        return 'torch not installed'
    return None


@pytest.mark.skipif(_skip_reason() is not None, reason=_skip_reason() or '')
def test_model_forward_performance(benchmark):
    model_mod = importlib.import_module('llmbuilder.model')
    # Build a tiny model config dict to pass through builder
    cfg = {
        'vocab_size': 256,
        'n_layer': 1,
        'n_head': 1,
        'n_embd': 32,
        'block_size': 16,
        'dropout': 0.0,
        'bias': False,
        'device': 'cpu',
    }
    model = model_mod.build_model(cfg)
    model.eval()

    x = torch.randint(0, cfg['vocab_size'], (1, 8))

    def _forward():
        with torch.no_grad():
            return model(x)

    out = benchmark(_forward)
    assert out is not None
