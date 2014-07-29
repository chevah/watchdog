"""
Test suite for watchdog.
"""
from chevah.empirical import EmpiricalTestCase, mk

from watchdog.observers.api import ObservedWatch


class WatchdogTestCase(EmpiricalTestCase):
    """
    Testcase for watchdog project.
    """

    def ObservedWatch(self, path=None, recursive=False):
        """
        Return an ObservedWatch instance.
        """
        if path is None:
            path = mk.fs.temp_path

        return ObservedWatch(path=path, recursive=recursive)
