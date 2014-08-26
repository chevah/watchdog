.. :changelog:

API changes
-----------


0.8.1.c1
~~~~~~~~

- Update.


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
