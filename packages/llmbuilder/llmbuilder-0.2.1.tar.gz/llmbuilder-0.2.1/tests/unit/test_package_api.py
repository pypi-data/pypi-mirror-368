import importlib


def test_package_import_and_metadata():
    llmbuilder = importlib.import_module('llmbuilder')
    assert hasattr(llmbuilder, '__version__')
    assert hasattr(llmbuilder, '__author__')


def test_public_api_functions_exist():
    llmbuilder = importlib.import_module('llmbuilder')
    for name in [
        'load_config',
        'build_model',
        'train_model',
        'generate_text',
        'interactive_cli',
        'finetune_model',
    ]:
        assert hasattr(llmbuilder, name), f"Missing public function: {name}"
        assert callable(getattr(llmbuilder, name))


def test_submodules_accessible():
    llmbuilder = importlib.import_module('llmbuilder')
    for module in [
        'config', 'data', 'tokenizer', 'model', 'training', 'finetune', 'inference', 'export', 'utils'
    ]:
        assert hasattr(llmbuilder, module), f"Missing submodule: {module}"
        getattr(llmbuilder, module)  # should not raise
