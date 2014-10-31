"""
Common tests for all emitters.
"""
import unicodedata

from watchdog.events import EVENT_TYPE_CREATED, EVENT_TYPE_MODIFIED
from watchdog.tests import mk


class EmitterSystemMixin(object):
    """
    System tests for emitters.
    """
    def fixClockResolution(self):
        """
        Some observers use timestamp to observer changes and on some
        systems timestamp has a lower resolution.
        """
        pass

    def test_run_ok(self):
        """
        After emitter start, ready event is set and no error is set.
        """
        self.sut.start()

        self.assertIsNone(self.sut.start_error)
        self.assertIsTrue(self.sut.ready.is_set())
        self.assertTrue(self.emitter_queue.empty())

        self.endThread(self.sut)

    def test_run_bad_path(self):
        """
        It can be initialized with a bad path but error is only
        raised when emitter starts.
        """
        sut = self.makeEmitter(path='no-such-path')
        self.assertIsNone(sut.start_error)

        # Start will call the run method.
        sut.start()

        # Thread is stopped on failures.
        sut.join()
        self.assertIsInstance(OSError, sut.start_error)
        self.assertIsTrue(sut.ready.is_set())

    def test_queue_events_file_created(self):
        """
        After started it will put events in the queue.

        For file created it creates 2 events.
        """
        self.sut.start()
        self.addCleanup(self.endThread, self.sut)

        self.fixClockResolution()
        self.test_segments = mk.fs.createFileInTemp()

        self.waitQueueSize(2, self.emitter_queue)
        event, watch = self.emitter_queue.get()
        new_path = mk.fs.getEncodedPath(
            mk.fs.getRealPathFromSegments(self.test_segments))

        if self.os_name == 'osx':
            src_path = event.src_path.decode('utf-8')
            self.assertEqual(
                mk.fs.getRealPathFromSegments(self.test_segments),
                unicodedata.normalize('NFC', src_path),
                )
        else:
            self.assertEqual(new_path, event.src_path)

        self.assertFalse(event.is_directory)
        self.assertEqual(EVENT_TYPE_CREATED, event.event_type)
        event, watch = self.emitter_queue.get()

        if self.os_name == 'osx':
            src_path = event.src_path.decode('utf-8')
            self.assertEqual(
                mk.fs.temp_path, unicodedata.normalize('NFC', src_path))
        else:
            self.assertEqual(
                mk.fs.getEncodedPath(mk.fs.temp_path), event.src_path)

        self.assertTrue(event.is_directory)
        self.assertEqual(EVENT_TYPE_MODIFIED, event.event_type)
