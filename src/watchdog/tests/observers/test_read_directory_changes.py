"""
Test for Windows read directory changes emitter.
"""
import platform

from Queue import Queue
from watchdog.tests import mk, WatchdogTestCase

# read_directory_changes is only supported on Windows.
if WatchdogTestCase.os_family != 'nt':
    raise WatchdogTestCase.skipTest('Windows specific.')

windows_signature = platform.win32_ver()
windows_major_version = int(windows_signature[1].split('.')[0])
if windows_major_version < 6:
    raise WatchdogTestCase.skipTest('2008 and above')

from watchdog.events import EVENT_TYPE_CREATED
from watchdog.observers.read_directory_changes import WindowsApiEmitter
from watchdog.tests.observers.emitter_mixin import EmitterSystemMixin


class TestWindowsApiEmitter(WatchdogTestCase, EmitterSystemMixin):
    """
    Unit tests for WindowsApiEmitter.
    """

    def setUp(self):
        super(TestWindowsApiEmitter, self).setUp()
        self.emitter_queue = Queue()
        # Configure emitter for temp folder.
        self.sut = self.makeEmitter()

    def makeEmitter(self, path=None):
        """
        Create a new emitter instance.
        """
        return WindowsApiEmitter(
            event_queue=self.emitter_queue,
            watch=self.ObservedWatch(path=path),
            timeout=0,
            )

    def test_queue_events_file_created(self):
        """
        After started it will put events in the queue.

        For file created it only creates one event, as
        opposed to the other observers.
        """
        self.sut.start()
        self.addCleanup(self.endThread, self.sut)
        self.test_segments = mk.fs.createFileInTemp()

        self.waitQueueSize(1, self.emitter_queue)
        event, watch = self.emitter_queue.get()
        new_path = mk.fs.getEncodedPath(
            mk.fs.getRealPathFromSegments(self.test_segments))
        self.assertEqual(new_path, event.src_path)
        self.assertFalse(event.is_directory)
        self.assertEqual(EVENT_TYPE_CREATED, event.event_type)
