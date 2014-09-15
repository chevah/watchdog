"""
Test suite for watchdog.
"""
import time

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
        path = mk.fs.getEncodedPath(path)

        return ObservedWatch(path=path, recursive=recursive)

    def endThread(self, thread, timeout=5):
        """
        Stop a thread and wait for it to end.
        """
        thread.stop()
        thread.join(timeout)
        if thread.isAlive():
            raise AssertionError(
                'Thread %s is still alive after %s seconds' % (
                    thread, timeout))

    def waitQueueSize(self, size, queue, timeout=5):
        """
        Wait for queue to have `size`.
        """
        time_start = time.time()
        while time.time() - time_start < timeout:
            if queue.qsize() == size:
                return
            time.sleep(0.05)

        raise AssertionError(
            'Queue took more than %s second to grow to %s. Now at %s.\n%s' % (
                timeout, size, queue.qsize(), queue.queue))


def setup_package():
    """
    Called before running all tests.
    """
    # Prepare the main testing filesystem.
    mk.fs.setUpTemporaryFolder()


def teardown_package():
    """
    Called after all tests were run.
    """
    # Remove main testing folder.
    mk.fs.tearDownTemporaryFolder()
    mk.fs.checkCleanTemporaryFolders()
