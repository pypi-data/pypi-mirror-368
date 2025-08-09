import importlib
import json


def test_load_config_callable():
    llmbuilder = importlib.import_module('llmbuilder')
    assert callable(llmbuilder.load_config)


def test_load_config_from_preset_or_file(tiny_config_path):
    llmbuilder = importlib.import_module('llmbuilder')
    # Prefer file-based to avoid relying on preset names
    cfg = llmbuilder.load_config(path=str(tiny_config_path))
    # Minimal sanity: expect dict-like or object with common attrs
    if isinstance(cfg, dict):
        assert cfg.get('n_layer') in (1, 2, 3)
    else:
        # dataclass-like
        assert hasattr(cfg, 'n_layer')
