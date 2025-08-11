from capm.config import load_config, save_config_to_file
from capm.entities.Config import Config
from capm.entities.PackageConfig import PackageConfig


def test_load_config_one_package():
    config = ''
    config += 'packages:\n'
    config += '  - id: codelimit\n'

    result = load_config(config)

    assert len(result.packages) == 1
    assert result.packages[0].id == 'codelimit'


def test_load_config_two_packages():
    config = ''
    config += 'packages:\n'
    config += '  - id: codelimit\n'
    config += '  - id: ruff\n'

    result = load_config(config)

    assert len(result.packages) == 2
    assert result.packages[0].id == 'codelimit'
    assert result.packages[1].id == 'ruff'


def test_load_config_no_packages():
    config = ''

    result = load_config(config)

    assert len(result.packages) == 0


def test_save_config_to_file(tmp_path):
    config = Config(packages=[PackageConfig(id='codelimit'), PackageConfig(id='ruff')])
    config_path = tmp_path / 'test_config.yml'

    save_config_to_file(config, config_path)

    expected = ''
    expected += 'packages:\n'
    expected += '- id: codelimit\n'
    expected += '- id: ruff\n'

    with open(config_path, 'r') as file:
        content = file.read()

    assert content == expected