"""CLI for pyxend"""
from shutil import copy, which
from pathlib import Path
from json import load, dump
from subprocess import run
from importlib.metadata import version

import click
from jinja2 import Environment, FileSystemLoader

from pyxend.parser import parse_decorators
from pyxend.license_gen import generate_MIT

TEMPLATE_DIR = Path(__file__).parent / "templates"
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


@click.group()
@click.version_option(version('pyxend'), "-v", "--version", message="pyxend version %(version)s")
def cli():
    pass

@cli.command()
@click.option('-t', '--target', default='.')
@click.argument('display_name')
@click.argument('extension_name', required=False)#help='Extension name, if not provided this argument will be your folder name.'
def init(target, display_name, extension_name):
    """init new project"""
    print('Initialize empty extension...')
    project_dir = Path(target).resolve()
    project_dir.mkdir(parents=True, exist_ok=True)
    ext_name = extension_name or project_dir.name

    copy(TEMPLATE_DIR / 'main.py', project_dir / 'main.py')
    copy(TEMPLATE_DIR / '.vscodeignore', project_dir / '.vscodeignore')

    with open(project_dir / 'extension.js', 'w') as fl:
        fl.write(env.get_template('extension.js.j2').render({'commands': [], 'extension_name': ext_name}))
    with open(project_dir / 'package.json', 'w') as fl:
        fl.write(env.get_template('package.json.j2').render({'commands': [], 'extension_name': ext_name, 'display_name': display_name}))

    print('Extension initalized.')
    print('You can change extension settings in package.json.')


@cli.command()
@click.option('-t', '--target', default='.')
def sync(target):
    """sync main.py commands and extension.js & package.json files"""
    print('Syncing...')
    project_dir = Path(target).resolve()
    decorators = parse_decorators(project_dir / 'main.py')
    print(f'Found {len(decorators)} decorators.')
    with open(project_dir / 'package.json', 'r') as fl:
        package = load(fl)

    with open(project_dir / 'extension.js', 'w') as fl:
        fl.write(env.get_template('extension.js.j2').render({
            'commands': [decorator['name'] for decorator in decorators],
            'extension_name': package['name'].replace('-', '').lower()
        }))
    package['activationEvents'] = [
        f'onCommand:{package["name"].replace("-", "").lower()}.{decorator["name"]}' for decorator in decorators
    ]
    package['contributes']['commands'] = [
        {'command': f'{package["name"].replace("-", "").lower()}.{decorator["name"]}', 'title': decorator['title']} for decorator in decorators
    ]
    with open(project_dir / 'package.json', 'w') as fl:
        dump(package, fl, indent=2)
    print('package.json and extension.js successfully updated.')


@cli.command()
@click.option('-t', '--target', default='.')
@click.option('-e', '--engine', help='VScode engine')
@click.option('-d', '--description', help='Description for extension')
@click.option('-g', '--git', help='Add git repository')
@click.option('-n', '--name', help='Display name for extension')
@click.option('-v', '--version', help='Extension version')
def metadata(target, engine, description, git, name, version):
    """update metadata (package.json) data, e.g. add description"""
    print('Updating package.json...')
    project_dir = Path(target).resolve()
    with open(project_dir / 'package.json', 'r') as fl:
        package = load(fl)

    if engine:
        package['engines']['vscode'] = f'^{engine}'
    if description:
        package['description'] = description
    if git:
        package['repository'] = {'type': 'git', 'url': git}
    if name:
        package['displayName'] = name
    if version:
        package['version'] = version

    with open(project_dir / 'package.json', 'w') as fl:
        dump(package, fl, indent=2)

    print('package.json updated.')


@cli.command()
@click.option('-t', '--target', default='.')
@click.argument('author')
def license(target, author):
    """Generate license file (requires for `vsce package`). Now only "MIT" license supports"""
    print('Generating license...')
    project_dir = Path(target).resolve()

    with open(project_dir / 'LICENSE', 'w') as fl:
        fl.write(generate_MIT(author))

    print('License generated.')


@cli.command()
@click.option('-t', '--target', default='.')
def build(target):
    """Build .vsix file"""
    print('Building extension...')
    project_dir = Path(target).resolve()
    result = run([which('vsce') or 'vsce', "package"], cwd=project_dir, capture_output=True, text=True)
    if result.returncode == 0:
        match = next((line for line in result.stdout.splitlines() if "Packaged:" in line), None)
        if match:
            filename = match.split("Packaged:")[-1].split('(')[0].strip()
            print(f'Build completed. Install package using "code --install-extension {filename}"')
        else:
            print("Build succeeded but could not find .vsix output.")

if __name__ == "__main__":
    cli()
