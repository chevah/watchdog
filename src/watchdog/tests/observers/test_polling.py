"""
Test for directory polling emitter.
"""
from Queue import Queue
import time

from watchdog.observers.polling import PollingEmitter
from watchdog.tests import WatchdogTestCase
from watchdog.tests.observers.emitter_mixin import EmitterSystemMixin


class TestPollingEmitter(WatchdogTestCase, EmitterSystemMixin):
    """
    Unit tests for PollingEmitter.
    """

    def setUp(self):
        super(TestPollingEmitter, self).setUp()
        self.emitter_queue = Queue()
        # Configure default emitter in temp folder.
        self.sut = self.makeEmitter()

    def makeEmitter(self, path=None):
        """
        Return an emitter.
        """
        return PollingEmitter(
            event_queue=self.emitter_queue,
            watch=self.ObservedWatch(path=path),
            timeout=0.1,
            )

    def fixClockResolution(self):
        """
        See: EmitterSystemMixin.
        """
        # On Windows filesystem timestamp has 0 decimals second. Same
        # for 2.6 Linux versions. On newer Linux it has 2 decimals.
        time.sleep(1)
