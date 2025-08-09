import importlib
from click.testing import CliRunner


def test_cli_help_and_subcommands():
    cli = importlib.import_module('llmbuilder.cli')
    main = getattr(cli, 'main')
    runner = CliRunner()

    # main help
    res = runner.invoke(main, ['--help'])
    assert res.exit_code == 0
    assert 'LLMBuilder' in res.output

    # info
    res = runner.invoke(main, ['info'])
    assert res.exit_code == 0
    assert 'LLMBuilder version' in res.output

    # subcommand helps
    for cmd in ['data', 'train', 'finetune', 'generate', 'model', 'export', 'config']:
        res = runner.invoke(main, [cmd, '--help'])
        assert res.exit_code == 0, f"{cmd} help should work"

    # interactive option advertised under generate
    res = runner.invoke(main, ['generate', '--help'])
    assert res.exit_code == 0
    assert 'interactive' in res.output
