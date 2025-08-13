from os import path, listdir
from pathlib import Path

import docker
import yaml
from docker.errors import ContainerError

from capm.config import run_commands
from capm.entities.PackageConfig import PackageConfig
from capm.entities.PackageDefinition import PackageDefinition
from capm.utils.Spinner import Spinner


def load_packages() -> dict[str, PackageDefinition]:
    result: dict[str, PackageDefinition] = {}
    packages_dir = Path(__file__).parent.joinpath('packages')
    yml_files = [packages_dir.joinpath(f) for f in listdir(packages_dir) if
                 packages_dir.joinpath(f).is_file() and f.endswith('.yml')]
    for yml_file in yml_files:
        with open(yml_file, 'r') as file:
            d = yaml.safe_load(file)
            package_id = path.splitext(path.basename(yml_file))[0]
            result[package_id] = PackageDefinition(**d)
    return result


def run_package(package_definition: PackageDefinition, package_config: PackageConfig, show_output: bool,
                path: Path = Path('.')) -> int:
    client = docker.from_env()
    spinner = Spinner('Loading')
    spinner.start()
    if package_config.image:
        image = package_config.image
    else:
        image = package_definition.image
    spinner.text = f'[{package_config.id}] Pulling image: {image}'
    client.images.pull(image)
    spinner.text = f'[{package_config.id}] Running image: ({image})'
    args = package_config.args if package_config.args else package_definition.args
    report_dir = str(run_commands.reports_dir.joinpath(package_config.id))
    command = ''
    if package_definition.entrypoint:
        command = package_definition.entrypoint + ' '
    args = args.format(workspace=str(run_commands.workspace_dir), report_dir=report_dir)
    if package_config.extra_args:
        args = package_config.extra_args + ' ' + args
    command += args
    if package_definition.install_command:
        command = f'/bin/sh -c \'{package_definition.install_command} >/dev/null 2>&1 && {command}\''
    mode = package_config.workspace_mode if package_config.workspace_mode else package_definition.workspace_mode
    volumes = {str(path.resolve()): {'bind': str(run_commands.workspace_dir), 'mode': mode}}
    try:
        output = client.containers.run(image, command, volumes=volumes)
        spinner.succeed(f'[{package_config.id}] Package executed successfully')
        if output and show_output:
            print(output.decode('utf-8'))
        return 0
    except ContainerError as e:
        spinner.fail(f"[{package_config.id}] Error running package, exit code: {e.exit_status}")
        print(e.container.logs().decode('utf-8'))
        return e.exit_status
