.. :changelog:


API changes
-----------


0.8.2.c1
~~~~~~~~

 - Update chevah code with upstream 0.8.2.


0.8.2
~~~~~

 - Event emitters are no longer started on schedule if ``Observer`` is not
   already running.


0.8.1.c6
~~~~~~~~

- Fail if observer took to much to start in blocking mode.


0.8.1.c5
~~~~~~~~

- Prevent starting the same emitter twice by removing it after start failure.


0.8.1.c4
~~~~~~~~

- Fix the emitter failing to become ready when there were errors at start.
- Use threading.Event instead of time.sleep() loop.


0.8.1.c3
~~~~~~~~

- Fix an error from 0.8.1.c4 where errors at emitter start were not raised.


0.8.1.c2
~~~~~~~~

- Catch in main thread start error from read_directory_changes.


0.8.1.c1
~~~~~~~~

- Update with latest master.
- Prevent starting the same emitter twice.


0.8.0.c7
~~~~~~~~

- Catch in main thread start error from inotify and directory polling.


0.8.0.c6
~~~~~~~~

- Ignore permission changes in Inotify.


0.8.0.c5
~~~~~~~~

- On Windows Native (ReadDirectoryChangesW) don't monitor changes on
  file attributes / security / last access time.
- Revert to daemon threads as on Windows we don't yet know what is going on.


0.8.0.c4
~~~~~~~~

- Wait for polling emitter to start and take a first snapshot at start.


0.8.0.c3
~~~~~~~~

 - Don't start emitter thread before observer is started.
 - Remove logging from inotify_buffer.
 - Wait for emitter to start before returning from schedule.


0.8.0.c2
~~~~~~~~

 - Remove automatic observer selection from observers.__init__.py.


0.8.0.c1
~~~~~~~~

 - Fix InotifyEmitter thread stop.
 - Fix Observer unschedule and unschedule_all to wait for emitter to stop.


0.8.0
~~~~~

 - ``DirectorySnapshot``: methods returning internal stat info replaced by
   ``mtime``, ``inode`` and ``path`` methods.
 - ``DirectorySnapshot``: ``walker_callback`` parameter deprecated.
