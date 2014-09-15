"""
Test for inotify emitter and observer.
"""
from Queue import Queue
import threading

from watchdog.tests import WatchdogTestCase
from watchdog.tests.observers.emitter_mixin import EmitterSystemMixin

# Inotify is only supported on Linux.
if WatchdogTestCase.os_name != 'linux':
    raise WatchdogTestCase.skipTest()

# RHEL-4 has an old version of libc.
if 'rhel-4' in WatchdogTestCase.getHostname():
    raise WatchdogTestCase.skipTest()

# Inotify is imported later.
from watchdog.observers.inotify import InotifyEmitter
from watchdog.observers.inotify_buffer import STOP_EVENT


class InMemoryInotifyBuffer(object):
    """
    A fake InotifyBuffer to help testing EmitterTestCase.
    """
    def __init__(self, queue=None):
        if queue is None:
            queue = []
        self.queue = queue
        self._inotify = None
        self.ready = threading.Event()

    def start(self):
        self._inotify = object()
        self.ready.set()

    def close(self):
        self._inotify = None
        self.queue = []

    def read_event(self):
        return self.queue.pop()


class TestInotifyEmitter(WatchdogTestCase, EmitterSystemMixin):
    """
    Unit tests for InotifyEmitter.
    """

    def setUp(self):
        super(TestInotifyEmitter, self).setUp()

        self.emitter_queue = Queue()
        # Configure emitter for temp folder.
        self.sut = self.makeEmitter()
        self.buffer = InMemoryInotifyBuffer()

    def makeEmitter(self, path=None):
        """
        Return a new emitter monitoring `path`.
        """
        return InotifyEmitter(
            event_queue=self.emitter_queue,
            watch=self.ObservedWatch(path=path),
            timeout=0,
            )

    def patchBuffer(self):
        """
        Patch the emitter with a fake buffer.
        """
        self.sut._inotify = self.buffer

    def test_start_failure(self):
        """
        Emitter will be ready with last error set when failing to start.

        This is an unit test,
        """
        error = AssertionError('fail-to-start')
        self.patchBuffer()
        self.buffer.start = self.Mock(side_effect=[error])

        self.sut.start()

        # Low level buffer is not ready but high level emitter is ready
        # due to start error.
        self.assertIsFalse(self.buffer.ready.is_set())
        self.assertIs(error, self.sut.start_error)
        self.assertIsTrue(self.sut.ready.is_set())

    def test_queue_events_stop(self):
        """
        When inotify buffers return the stop, event it does not queue any
        event.
        """
        self.patchBuffer()
        self.buffer.queue = [STOP_EVENT]

        self.sut.queue_events()

        self.assertTrue(self.emitter_queue.empty())
