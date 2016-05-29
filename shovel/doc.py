from subprocess import call
from pathlib import Path
import os

from shovel import task


@task
def watch():
    """Renerate documentation when it changes."""
    index = Path(os.getcwd(), 'doc', 'html', 'index.html')

    gen()
    try:
        call(['watchmedo', 'shell-command', '--patterns=*.rst;*.py;*.css',
              '--ignore-pattern=_build/*', '--recursive',
              '--command=sphinx-build -b html doc doc/_build/html'])
    except FileNotFoundError:
        print('watchdog is required (pip install watchdog)')


@task
def gen():
    """Generate html and dirhtml output."""
    call(['sphinx-build', '-b', 'html', '-W', '-E', 'doc', 'doc/_build/html'])
    call(['sphinx-build', '-b', 'dirhtml', '-W', '-E', 'doc', 'doc/_build/dirhtml'])


@task
def clean():
    """Clean build directory."""
    call(['make', '-C', 'doc/', 'clean'])
