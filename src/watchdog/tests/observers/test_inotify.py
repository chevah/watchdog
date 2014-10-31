"""
Test for inotify emitter and observer.
"""
from Queue import Queue

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


class InMemoryInotifyBuffer(object):
    """
    A fake InotifyBuffer to help testing EmitterTestCase.
    """
    def __init__(self, queue=None):
        if queue is None:
            queue = []
        self.queue = queue
        self._inotify = None

    def start(self):
        self._inotify = object()

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

        with self.assertRaises(AssertionError) as context:
            self.sut.start()

        self.assertIs(error, context.exception)

    def test_queue_events_stop(self):
        """
        When inotify buffers return the stop, event it does not queue any
        event.
        """
        self.patchBuffer()
        self.buffer.queue = [None]

        self.sut.queue_events()

        self.assertTrue(self.emitter_queue.empty())
