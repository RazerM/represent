import re
from glob import glob
from pathlib import Path
from shutil import rmtree
from subprocess import call, CalledProcessError, check_call, check_output

from clint.textui import colored, indent, puts
from packaging.version import _Version, Version, VERSION_PATTERN

from doc import gen as doc_gen
from shovel import task

shovel_dir = Path(__file__).parent.resolve()
REPRESENT_DIR = shovel_dir.parent
INIT_PATH = Path(REPRESENT_DIR, 'represent', '__init__.py')


@task
def bump(dev=False, patch=False, minor=False, major=False, nocommit=False):
    """Bump version number and commit change."""
    if sum([int(x) for x in (patch, minor, major)]) > 1:
        raise ValueError('Only one of patch, minor, major can be incremented.')

    if check_staged():
        raise EnvironmentError('There are staged changes, abort.')

    with open(str(INIT_PATH)) as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        varmatch = re.match("__([a-z]+)__ = '([^']+)'", line)
        if varmatch:
            if varmatch.group(1) == 'version':
                version = Version(varmatch.group(2))
                vdict = version._version._asdict()
                print('Current version:', version)
                increment_release = True
                if dev:
                    if vdict['dev']:
                        vdict['dev'] = (vdict['dev'][0], vdict['dev'][1] + 1)
                        increment_release = False
                        if sum([int(x) for x in (patch, minor, major)]) > 0:
                            raise ValueError('Cannot increment patch, minor, or major between dev versions.')
                    else:
                        vdict['dev'] = ('dev', 0)
                else:
                    if vdict['dev']:
                        vdict['dev'] = None
                        increment_release = False

                if increment_release:
                    rel = vdict['release']
                    if major:
                        vdict['release'] = (rel[0] + 1, 0, 0)
                    elif patch:
                        vdict['release'] = (rel[0], rel[1], rel[2] + 1)
                    else:  # minor is default
                        vdict['release'] = (rel[0], rel[1] + 1, 0)

                version._version = _Version(**vdict)
                print('Version bumped to:', version)
                lines[i] = "__version__ = '{!s}'\n".format(version)
                break

    with open(str(INIT_PATH), 'w') as f:
        f.writelines(lines)

    if not nocommit:
        call(['git', 'add', 'represent/__init__.py'])
        call(['git', 'commit', '-m', 'Bumped version number to {!s}'.format(version)])
    return version


@task
def tag():
    """Tag current version."""
    if check_unstaged():
        raise EnvironmentError('There are staged changes, abort.')
    with open(str(INIT_PATH)) as f:
        metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", f.read()))
    version = metadata['version']
    check_output(['git', 'tag', version, '-m', 'Release v{}'.format(version)])


@task
def build():
    """Build source distribution."""
    rmtree(str(REPRESENT_DIR / 'dist'))
    o = check_output(['python', 'setup.py', 'sdist'])
    print(o.decode('utf-8'))


@task
def upload():
    """Upload source to PyPI using twine."""
    try:
        o = check_output(['twine', 'upload'] + glob('dist/*'))
    except CalledProcessError:
        call(['twine', 'upload'] + glob('dist/*'))
        raise
    print(o.decode('utf-8'))


@task
def release():
    """Bump version, tag, build, gen docs."""
    if check_staged():
        raise EnvironmentError('There are staged changes, abort.')
    if check_unstaged():
        raise EnvironmentError('There are unstaged changes, abort.')
    bump()
    tag()
    build()
    doc_gen()
    puts(colored.yellow("Remember to upload documentation and package:"))
    with indent(2):
        puts(colored.cyan("shovel doc.upload"))
        puts(colored.cyan("shovel version.upload"))


def check_staged():
    try:
        check_call(['git', 'diff-index', '--quiet', '--cached', 'HEAD'])
    except CalledProcessError:
        return True
    return False


def check_unstaged():
    try:
        check_call(['git', 'diff-files', '--quiet'])
    except CalledProcessError:
        return True
    return False
