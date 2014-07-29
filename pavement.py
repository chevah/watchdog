# Copyright (c) 2010-2013 Adi Roiban.
# See LICENSE for details.
"""
Build script for watchdog using brink build system.
"""
from pkg_resources import load_entry_point
import os
import sys

if os.name == 'nt':
    # Use shorter temp folder on Windows.
    import tempfile
    tempfile.tempdir = "c:\\temp"

PACKAGES = [

    'pathtools==0.1.2',

    # Buildbot is used for try scheduler
    'twisted==12.1.0-chevah3',
    'buildbot',

    'pytest==2.6.0',

    'chevah-compat==0.22.0',
    'chevah-empirical==0.28.2',
    'wmi==1.4.9',

    # Never version of nose, hangs on closing some tests
    # due to some thread handling.
    'nose==1.3.0-c5',
    'mock',

    # Linters.
    'pocketlint==1.4.4.c4',
    'pyflakes==0.7.3',

    # For PQM
    'chevah-github-hooks-server==0.1.6',
    'smmap==0.8.2',
    'async==0.6.1',
    'gitdb==0.5.4',
    'gitpython==0.3.2.RC1',
    'pygithub==1.10.0',


    # Required for some unicode handling.
    'unidecode',

    'bunch',
    ]


from brink.pavement_commons import (
    buildbot_list,
    buildbot_try,
    default,
    github,
    harness,
    help,
    lint,
    merge_init,
    merge_commit,
    pave,
    pqm,
    SETUP,
    test_python,
    test_remote,
    test_review,
    test_normal,
    test_super,
    )
from paver.easy import call_task, consume_args, needs, task

# Make pylint shut up.
buildbot_list
buildbot_try
default
github
harness
help
lint
merge_init
merge_commit
pqm
test_python
test_remote
test_review
test_normal
test_super

SETUP['product']['name'] = 'watchdog'
SETUP['folders']['source'] = u'src/watchdog'
SETUP['repository']['name'] = u'watchdog'
SETUP['github']['repo'] = 'chevah/watchdog'
SETUP['pocket-lint']['include_files'] = ['pavement.py', 'README-chevah.rst']
SETUP['pocket-lint']['include_folders'] = ['src/watchdog/tests']
SETUP['pocket-lint']['exclude_files'] = []
SETUP['test']['package'] = 'watchdog.tests'
SETUP['test']['elevated'] = None
SETUP['github']['url'] = 'https://github.com/chevah/watchdog'
SETUP['buildbot']['server'] = 'build.chevah.com'
SETUP['buildbot']['web_url'] = 'http://build.chevah.com:10088'
SETUP['pypi']['index_url'] = 'http://pypi.chevah.com:10042/simple'


@task
def deps():
    """
    Install all dependencies.
    """
    print('Installing build dependencies to %s...' % (pave.path.build))
    pave.pip(
        command='install',
        arguments=PACKAGES,
        silent=True,
        )


@task
def build():
    """
    Copy new source code to build folder.
    """
    # Clean previous files.

    build_target = pave.fs.join([pave.path.build, 'setup-build'])
    sys.argv = ['setup.py', '-q', 'build', '--build-base', build_target]
    print "Building in " + build_target
    # Importing setup will trigger executing commands from sys.argv.
    import setup
    setup.distribution.run_command('install')


@task
@consume_args
@needs('build', 'test_python')
def test(args):
    """
    Run all Python tests using nose.
    """


def _run(observer_class, args):
    """
    Run observer.
    """
    import logging
    import time
    from watchdog.events import LoggingEventHandler

    path = args[0] if len(args) > 1 else pave.path.build

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(message)s',
        datefmt='%H:%M:%S',
        )

    event_handler = LoggingEventHandler()
    observer = observer_class()
    observer.schedule(event_handler, path, recursive=True)
    print "Observer %s start monitoring %s\n" % (observer_class, path)

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print "\nStopping the observer.... wait"
        observer.stop()
    observer.join()


@task
@consume_args
@needs('build')
def run(args):
    """
    Run manual test using polling observer.
    """
    from watchdog.observers.polling import PollingObserver
    return _run(PollingObserver, args)


@task
@consume_args
@needs('build')
def run_native(args):
    """
    Run manual test using polling observer.
    """
    def _get_native_observer():
        """
        Return native observer... or fail.
        """
        from watchdog.utils import platform

        if platform.is_linux():
            from watchdog.observers.inotify import InotifyObserver
            return InotifyObserver

        if platform.is_windows():
            # TODO: find a reliable way of checking Windows version and import
            # polling explicitly for Windows XP
            try:
                from watchdog.observers.read_directory_changes import (
                    WindowsApiObserver)
                return WindowsApiObserver
            except:
                raise AssertionError('Native observer not supported.')

        raise AssertionError('Native observer not supported.')

    return _run(_get_native_observer(), args)


@task
@consume_args
@needs('build')
def test_pytest(args):
    """
    Run all Python tests using pytest... broken.
    """
    sys.argv = ['py.test']
    if args:
        sys.argv.extend(args)
    else:
        sys.argv.append('tests')

    sys.exit(
        load_entry_point('pytest==2.6.0', 'console_scripts', 'py.test')()
        )


@task
def test_os_independent():
    """
    Run os independent tests in buildbot.
    """
    call_task('lint', options={'all': True})


@task
# It needs consume_args to initialize the paver environment.
@consume_args
def test_ci(args):
    """
    Run tests in continuous integration environment.
    """
    env = os.environ.copy()
    args = env.get('TEST_ARGUMENTS', '')
    if not args:
        args = []
    else:
        args = [args]

    test_type = env.get('TEST_TYPE', 'normal')

    if test_type == 'os-independent':
        return call_task('test_os_independent')

    return call_task('test', args=args)
