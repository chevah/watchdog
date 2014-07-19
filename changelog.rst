.. :changelog:

API changes
-----------

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
