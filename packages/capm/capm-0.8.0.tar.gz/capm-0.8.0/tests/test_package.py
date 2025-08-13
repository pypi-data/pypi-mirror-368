from capm.package import load_packages


def test_load_packages():
    packages = load_packages()

    assert len(packages) > 0
    assert 'xenon' in packages
    assert packages['xenon'].install_command == 'pip install xenon'
    assert packages['xenon'].entrypoint == 'xenon'