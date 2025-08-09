import importlib
import pytest


@pytest.mark.parametrize('module_name', [
    'llmbuilder.config',
    'llmbuilder.data',
    'llmbuilder.tokenizer',
    'llmbuilder.model',
    'llmbuilder.training',
    'llmbuilder.finetune',
    'llmbuilder.inference',
    'llmbuilder.export',
    'llmbuilder.utils',
])
def test_import_module_smoke(module_name):
    mod = importlib.import_module(module_name)
    assert mod is not None


def test_training_exports():
    training = importlib.import_module('llmbuilder.training')
    for name in [
        'Trainer', 'TrainingMetrics', 'TrainingState',
        'train_model', 'resume_training', 'evaluate_model',
        'MetricsTracker', 'LearningRateScheduler', 'GradientClipper',
        'EarlyStopping', 'TrainingTimer', 'count_parameters', 'get_model_size_mb',
        'calculate_perplexity', 'warmup_lr_schedule', 'cosine_annealing_lr_schedule',
        'save_training_config', 'load_training_config'
    ]:
        assert hasattr(training, name)


def test_inference_api_presence():
    inference = importlib.import_module('llmbuilder.inference')
    for name in ['generate_text', 'interactive_cli', 'TextGenerator']:
        assert hasattr(inference, name)


def test_export_api_presence():
    export = importlib.import_module('llmbuilder.export')
    for name in ['GGUFExporter', 'ONNXExporter']:
        assert hasattr(export, name)
