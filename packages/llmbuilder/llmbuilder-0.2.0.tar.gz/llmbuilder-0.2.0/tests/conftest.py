import os
import sys
import json
from pathlib import Path
import pytest

# Ensure the package path is importable when running tests from repo root
REPO_ROOT = Path(__file__).resolve().parents[2]
PKG_ROOT = REPO_ROOT / 'llmbuilder_package'
if str(PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(PKG_ROOT))

@pytest.fixture(scope='session')
def tmp_workspace(tmp_path_factory):
    d = tmp_path_factory.mktemp('llmbuilder_tests')
    return d

@pytest.fixture(scope='session')
def tiny_corpus(tmp_workspace):
    text = "Hello world. This is a tiny corpus for tests. Hello again."
    p = tmp_workspace / 'tiny_corpus.txt'
    p.write_text(text, encoding='utf-8')
    return p

@pytest.fixture(scope='session')
def tiny_config_path(tmp_workspace):
    # Minimal, placeholder config used only for presence checks or very shallow operations
    cfg = {
        "vocab_size": 256,
        "n_layer": 1,
        "n_head": 1,
        "n_embd": 32,
        "block_size": 16,
        "dropout": 0.0,
        "bias": False,
        "device": "cpu"
    }
    p = tmp_workspace / 'tiny_config.json'
    p.write_text(json.dumps(cfg, indent=2), encoding='utf-8')
    return p


def env_flag(name: str) -> bool:
    val = os.environ.get(name, '')
    return val not in ('', '0', 'false', 'False')

@pytest.fixture(scope='session')
def run_slow():
    return env_flag('RUN_SLOW')

@pytest.fixture(scope='session')
def run_perf():
    return env_flag('RUN_PERF')
