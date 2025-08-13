# -*- coding: utf-8 -*-
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

from datetime import datetime
from queue import Empty, Queue
from socket import gaierror as socket_gaierror
from threading import Event, Thread

from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import ConnectTimeout, HTTPError, ProxyError, RetryError, Timeout

from sag_py_logging_logstash.constants import constants
from sag_py_logging_logstash.memory_cache import MemoryCache
from sag_py_logging_logstash.safe_logger import SafeLogger

NETWORK_EXCEPTIONS = (
    # Python
    ConnectionError,
    TimeoutError,
    socket_gaierror,
    # Requests
    ConnectTimeout,
    RequestsConnectionError,
    HTTPError,
    ProxyError,
    RetryError,
    Timeout,
)


class ProcessingError(Exception):
    """"""


class LogProcessingWorker(Thread):  # pylint: disable=too-many-instance-attributes
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        self._safe_logger: SafeLogger = kwargs.pop("safe_logger")
        self._host = kwargs.pop("host")
        self._port = kwargs.pop("port")
        self._transport = kwargs.pop("transport")
        self._ssl_enable = kwargs.pop("ssl_enable")
        self._memory_cache = kwargs.pop("cache")
        self._event_ttl = kwargs.pop("event_ttl")

        super().__init__(*args, **kwargs)
        self.daemon = True
        self.name = self.__class__.__name__

        self._shutdown_event = Event()
        self._flush_event = Event()
        self._queue = Queue()

        self._event = None
        self._last_event_flush_date = None
        self._non_flushed_event_count = None
        self._logger = None
        self._rate_limit_storage = None
        self._rate_limit_strategy = None
        self._rate_limit_item = None

    # ----------------------------------------------------------------------
    def enqueue_event(self, event):
        # called from other threads
        self._queue.put(event)

    # ----------------------------------------------------------------------
    def shutdown(self):
        # called from other threads
        self._shutdown_event.set()

    # ----------------------------------------------------------------------
    def run(self):
        self._reset_flush_counters()
        self._setup_memory_cache()
        try:
            self._fetch_events()
        except Exception as exc:
            # we really should not get anything here, and if, the worker thread is dying
            # too early resulting in undefined application behaviour
            self._log_general_error(exc)
        # check for empty queue and report if not
        self._warn_about_non_empty_queue_on_shutdown()

    # ----------------------------------------------------------------------
    def force_flush_queued_events(self):
        self._flush_event.set()

    # ----------------------------------------------------------------------
    def _reset_flush_counters(self):
        self._last_event_flush_date = datetime.now()
        self._non_flushed_event_count = 0

    # ----------------------------------------------------------------------
    def _clear_flush_event(self):
        self._flush_event.clear()

    # ----------------------------------------------------------------------
    def _setup_memory_cache(self):
        self._memory_cache = MemoryCache(
            safe_logger=self._safe_logger, cache=self._memory_cache, event_ttl=self._event_ttl
        )

    # ----------------------------------------------------------------------
    def _fetch_events(self):
        while True:
            try:
                self._fetch_event()
                self._process_event()
            except Empty:
                # Flush queued (in database) events after internally queued events has been
                # processed, i.e. the queue is empty.
                if self._shutdown_requested():
                    self._flush_queued_events(force=True)
                    return

                force_flush = self._flush_requested()
                self._flush_queued_events(force=force_flush)
                self._delay_processing()
                self._expire_events()
            except ProcessingError:
                if self._shutdown_requested():
                    return

                self._requeue_event()
                self._delay_processing()

    # ----------------------------------------------------------------------
    def _fetch_event(self):
        self._event = self._queue.get(block=False)

    # ----------------------------------------------------------------------
    def _process_event(self):
        try:
            self._write_event_to_database()

        except Exception as exc:
            self._log_processing_error(exc)
            raise ProcessingError from exc
        else:
            self._event = None

    # ----------------------------------------------------------------------
    def _expire_events(self):
        self._memory_cache.expire_events()

    # ----------------------------------------------------------------------
    def _log_processing_error(self, exception):
        self._safe_logger.log(
            "exception", "Log processing error (queue size: %3s): %s", self._queue.qsize(), exception, exc=exception
        )

    # ----------------------------------------------------------------------
    def _delay_processing(self):
        self._shutdown_event.wait(constants.QUEUE_CHECK_INTERVAL)

    # ----------------------------------------------------------------------
    def _shutdown_requested(self):
        return self._shutdown_event.is_set()

    # ----------------------------------------------------------------------
    def _flush_requested(self):
        return self._flush_event.is_set()

    # ----------------------------------------------------------------------
    def _requeue_event(self):
        self._queue.put(self._event)

    # ----------------------------------------------------------------------
    def _write_event_to_database(self):
        self._memory_cache.add_event(self._event)
        self._non_flushed_event_count += 1

    # ----------------------------------------------------------------------
    def _flush_queued_events(self, force=False):
        # check if necessary and abort if not
        if not force and not self._queued_event_interval_reached() and not self._queued_event_count_reached():
            return

        self._clear_flush_event()

        while True:
            queued_events = self._fetch_queued_events_for_flush()
            if not queued_events:
                break

            try:
                events = [event["event_text"] for event in queued_events]
                self._send_events(events)
            # exception types for which we do not want a stack trace
            except NETWORK_EXCEPTIONS as exc:
                self._safe_logger.log("error", "An error occurred while sending events: %s", exc)
                self._memory_cache.requeue_queued_events(queued_events)
                break
            except Exception as exc:
                self._safe_logger.log("exception", "An error occurred while sending events: %s", exc, exc=exc)
                self._memory_cache.requeue_queued_events(queued_events)
                break
            else:
                self._delete_queued_events_from_database()
                self._reset_flush_counters()

    # ----------------------------------------------------------------------
    def _fetch_queued_events_for_flush(self):
        try:
            return self._memory_cache.get_queued_events()

        except Exception as exc:
            # just log the exception and hope we can recover from the error
            self._safe_logger.log("exception", "Error retrieving queued events: %s", exc, exc=exc)
            return None

    # ----------------------------------------------------------------------
    def _delete_queued_events_from_database(self):
        self._memory_cache.delete_queued_events()

    # ----------------------------------------------------------------------
    def _queued_event_interval_reached(self):
        delta = datetime.now() - self._last_event_flush_date
        return delta.total_seconds() > constants.QUEUED_EVENTS_FLUSH_INTERVAL

    # ----------------------------------------------------------------------
    def _queued_event_count_reached(self):
        return self._non_flushed_event_count > constants.QUEUED_EVENTS_FLUSH_COUNT

    # ----------------------------------------------------------------------
    def _send_events(self, events):
        use_logging = not self._shutdown_requested()
        self._transport.send(events, use_logging=use_logging)

    # ----------------------------------------------------------------------
    def _log_general_error(self, exc):
        self._safe_logger.log("exception", "An unexpected error occurred: %s", exc, exc=exc)

    # ----------------------------------------------------------------------
    def _warn_about_non_empty_queue_on_shutdown(self):
        queue_size = self._queue.qsize()
        if queue_size:
            self._safe_logger.log(
                "warning",
                "Non-empty queue while shutting down ({} events pending). "
                "This indicates a previous error.".format(queue_size),
                extra=dict(queue_size=queue_size),
            )
