"""
Test for inotify emitter and observer.
"""

from watchdog.tests import WatchdogTestCase

# Inotify is only supported on Linux.
if WatchdogTestCase.os_name != 'linux':
    raise WatchdogTestCase.skipTest()

# RHEL-4 has an old version of libc.
if 'rhel-4' in WatchdogTestCase.getHostname():
    raise WatchdogTestCase.skipTest()

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

    def start(self):
        self._inotify = object()

    def close(self):
        self._inotify = None
        self.queue = []

    def read_event(self):
        return self.queue.pop()


class InotifyEmitterTestCase(WatchdogTestCase):
    """
    Unit tests for InotifyEmitter.
    """

    def setUp(self):
        super(InotifyEmitterTestCase, self).setUp()
        from watchdog.observers.inotify import InotifyEmitter

        self.emitter_queue = []
        self.sut = InotifyEmitter(
            event_queue=self.emitter_queue,
            watch=self.ObservedWatch(),
            timeout=0,
            )
        self.buffer = InMemoryInotifyBuffer()

    def patchBuffer(self):
        """
        Patch the emitter with a fake buffer.
        """
        self.sut._inotify = self.buffer

    def test_queue_events_stop(self):
        """
        When inotify buffers return the stop, event it does not queue any
        event.
        """
        self.patchBuffer()
        self.buffer.queue = [STOP_EVENT]

        self.sut.queue_events()

        self.assertIsEmpty(self.emitter_queue)
