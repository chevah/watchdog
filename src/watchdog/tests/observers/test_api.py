#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2011 Yesudeep Mangalapilly <yesudeep@gmail.com>
# Copyright 2012 Google, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Tests for generic observer, generic emitter, generic event dispatcher...etc
"""
import tempfile
import threading

from watchdog.observers.api import BaseObserver, EventEmitter, ObservedWatch
from watchdog.tests import WatchdogTestCase


class DummyEventEmitter(EventEmitter):
    """
    Simple event emitter implementation to help with testing generic
    event emitters.
    """

    def start(self):
        self.ready.set()
        return super(DummyEventEmitter, self).start()


class DelayStartEventEmitter(EventEmitter):
    """
    An event emitter which delays the start until `delay` member is set.
    """
    exception = AssertionError('fail-to-start')

    def start(self):
        self.delay = threading.Event()
        self.delay.wait(timeout=10)
        self.ready.set()


class FailToStartEventEmitter(EventEmitter):
    """
    An event emitter which fails to start.
    """
    exception = AssertionError('fail-to-start')
    started = False

    def start(self):
        self.started = True
        self._start_error = self.exception
        self.ready.set()


class TestEventEmitter(WatchdogTestCase):
    """
    Unit test for EventEmitter.
    """

    def setUp(self):
        super(TestEventEmitter, self).setUp()
        self.queue = []
        watch = ObservedWatch(path=tempfile.tempdir, recursive=False)
        self.sut = DummyEventEmitter(self.queue, watch, timeout=0)

    def tearDown(self):
        if self.sut.is_alive():
            self.sut.stop()
            self.sut.join()
        super(TestEventEmitter, self).tearDown()

    def test_start_blocking(self):
        """
        It will start the emitter and wait for it to finish the start.
        """
        self.sut.start()

        self.assertTrue(self.sut.ready.is_set())


class DummyObserver(BaseObserver):
    """
    Dummy implementation to help with testing the BaseObserver.
    """


class TestBaseObserver(WatchdogTestCase):
    """
    Unit tests for BaseObserver.
    """

    def setUp(self):
        super(TestBaseObserver, self).setUp()
        self.sut = DummyObserver(DummyEventEmitter, timeout=0)

    def tearDown(self):
        if self.sut.is_alive():
            self.sut.stop()
            self.sut.join()
        super(TestBaseObserver, self).tearDown()

    def getEmitterForWatch(self, watch, observer=None):
        """
        Return the emitter associated with the `watch`, or None
        if no emitter is associated.
        """
        if observer is None:
            observer = self.sut
        try:
            return observer._get_emitter_for_watch(watch)
        except KeyError:
            return None

    def test_schedule_not_started(self):
        """
        It does not start the emitter when observer is not started yet.
        """
        handler = self.sut.schedule('handler', tempfile.tempdir)

        emitter = self.getEmitterForWatch(handler)
        self.assertFalse(emitter.is_alive())

    def test_schedule_started(self):
        """
        When observer is already started, it starts the emitter when
        it is scheduled.
        """
        self.sut.start()

        handler = self.sut.schedule('handler', tempfile.tempdir)

        emitter = self.getEmitterForWatch(handler)
        self.assertTrue(emitter.is_alive())
        self.assertTrue(emitter.ready)

    def test_schedule_started_fail(self):
        """
        When emitter fails to start, it will raise the start error
        and remove the emitter.
        """
        self.sut.start()
        self.sut._emitter_class = FailToStartEventEmitter

        with self.assertRaises(AssertionError) as context:
            self.sut.schedule('handler', tempfile.tempdir)
        self.assertIs(FailToStartEventEmitter.exception, context.exception)

        self.assertIsEmpty(self.sut._emitters)

    def test_run_fail_emitter(self):
        """
        When an emitter fails it will stop starting the other emitters
        and raise the error.
        """
        self.sut._emitter_class = FailToStartEventEmitter
        self.sut.schedule('handler-1', 'path-1')
        self.sut.schedule('handler-1', 'path-2')
        # Emitters is a set and we don't know its order.
        self.assertEqual(2, len(self.sut._emitters))

        with self.assertRaises(AssertionError) as context:
            self.sut.run()

        self.assertIs(FailToStartEventEmitter.exception, context.exception)
        self.assertEqual(1, len(self.sut._emitters))
        self.assertTrue(self.sut.ready.is_set())

    def test_start_blocking(self):
        """
        It starts the attached emitters.
        """
        handler = self.sut.schedule('handler', tempfile.tempdir)
        emitter = self.getEmitterForWatch(handler)
        self.assertFalse(emitter.is_alive())
        self.assertFalse(self.sut.is_alive())

        self.sut.start_blocking()

        self.assertTrue(emitter.is_alive())
        self.assertTrue(emitter.ready.is_set())
        self.assertTrue(self.sut.is_alive())
        self.assertTrue(self.sut.ready.is_set())

    def test_start_blocking_timeout(self):
        """
        It starts the attached emitters.
        """
        self.sut._emitter_class = DelayStartEventEmitter
        handler = self.sut.schedule('handler', tempfile.tempdir)
        emitter = self.getEmitterForWatch(handler)
        self.assertFalse(self.sut.is_alive())

        with self.assertRaises(AssertionError) as context:
            self.sut.start_blocking(timeout=0.01)

        emitter.delay.set()
        self.assertEqual('Took to much to start.', context.exception.message)
        self.assertFalse(self.sut.ready.is_set())

    def test_unschedule_not_started(self):
        """
        Removes the scheduled emitter.
        """
        handler = self.sut.schedule('handler', tempfile.tempdir)

        self.sut.unschedule(handler)

        self.assertIsNone(self.getEmitterForWatch(handler))

    def test_unschedule_all_not_started(self):
        """
        Removes all scheduled emitters.
        """
        handler = self.sut.schedule('handler', tempfile.tempdir)

        self.sut.unschedule_all()

        self.assertIsNone(self.getEmitterForWatch(handler))
