import logging
import json
import os
import structlog
import sys
import traceback
import atexit
import time
#
from datetime import datetime
from queue import Queue, Empty
from opensearchpy import OpenSearch
from structlog.contextvars import bind_contextvars, clear_contextvars
from structlog.processors import CallsiteParameter
from threading import Thread, Event
#
from .slack_session_manager import SlackSessionManager

# Map string log levels to logging constants
LOG_LEVEL_MAP = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

# Default log level if not specified
DEFAULT_LOG_LEVEL = logging.INFO


def get_log_level():
    """Get log level from environment variable"""
    level_str = os.environ.get('ECL_LOGGING_UTILITY_LOG_LEVEL', 'INFO').upper()
    return LOG_LEVEL_MAP.get(level_str, DEFAULT_LOG_LEVEL)


# Custom processor to rename fields
def rename_fields(_, __, event_dict):
    field_mappings = {
        'pathname': 'file_path',
        'lineno': 'line_number',
        'func_name': 'function_name'
    }
    for old_key, new_key in field_mappings.items():
        if old_key in event_dict:
            event_dict[new_key] = event_dict.pop(old_key)
    return event_dict


# Custom processor for error-specific actions
def error_handler_processor(_, method_name, event_dict):
    if method_name in ('error', 'critical'):
        slack_webhook_url = os.environ.get('ECL_LOGGING_UTILITY_SLACK_WEBHOOK_URL')
        if slack_webhook_url:
            try:
                payload = {
                    "text": f"🚨 Error in {os.environ.get('ECL_LOGGING_UTILITY_SERVICE_NAME', 'AMBIVALENT_SERVICE_NAME')}",
                    "attachments": [{
                        "color": "danger",
                        "fields": [
                            {"title": key.replace('_', ' ').title(), "value": str(value), "short": len(str(value)) < 50}
                            for key, value in event_dict.items()
                        ]
                    }]
                }
                # Using singleton pattern to reuse requests session and save time creating new sessions
                # Making async call to avoid blocking the logging flow
                Thread(
                    target=lambda: SlackSessionManager().get_session().post(slack_webhook_url, json=payload, timeout=5),
                    daemon=True).start()
            except Exception as e:
                print(f"Failed to send error log to Slack: {e}\n Trace: {traceback.format_exc()}")
    return event_dict


class OpenSearchLogger:
    _instance = None
    _initialized = False

    def __new__(cls, service_name: str = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, service_name: str = None):
        if self._initialized:
            return

        self.host = os.environ.get('ECL_LOGGING_UTILITY_OPENSEARCH_HOST', 'localhost')
        self.port = int(os.environ.get('ECL_LOGGING_UTILITY_OPENSEARCH_PORT', '9200'))
        self.username = os.environ.get('ECL_LOGGING_UTILITY_OPENSEARCH_USERNAME', None)
        self.password = os.environ.get('ECL_LOGGING_UTILITY_OPENSEARCH_PASSWORD', None)
        self.batch_size = int(os.environ.get('ECL_LOGGING_UTILITY_OPENSEARCH_BATCH_SIZE', '10'))
        self.flush_interval = int(os.environ.get('ECL_LOGGING_UTILITY_OPENSEARCH_FLUSH_INTERVAL', '5'))

        http_auth = None
        if self.username and self.password:
            http_auth = (self.username, self.password)

        scheme = "http"
        use_ssl = False
        verify_certs = False
        if self.port == 443:
            scheme = "https"
            use_ssl = True
            verify_certs = True

        self.index_prefix = service_name if service_name else "logs"
        self.log_queue = Queue()
        self.shutdown_event = Event()

        self.client = OpenSearch(
            hosts=[{'host': self.host, 'port': self.port}],
            scheme=scheme,
            http_auth=http_auth,
            use_ssl=use_ssl,
            verify_certs=verify_certs,
            timeout=10
        )

        # Start background worker thread
        self.worker_thread = Thread(target=self._worker, daemon=True)
        self.worker_thread.start()

        # Register cleanup on exit
        atexit.register(self._cleanup)
        self._initialized = True

    def _worker(self):
        """Background worker that processes the log queue"""
        batch = []
        last_flush = time.time()

        while not self.shutdown_event.is_set():
            try:
                # Get log with timeout
                log_entry = self.log_queue.get(timeout=1)
                batch.append(log_entry)

                # Flush if batch is full or time interval reached
                if len(batch) >= self.batch_size or (time.time() - last_flush) >= self.flush_interval:
                    self._flush_batch(batch)
                    batch = []
                    last_flush = time.time()

            except Empty:
                # Flush remaining logs on timeout
                if batch and (time.time() - last_flush) >= self.flush_interval:
                    self._flush_batch(batch)
                    batch = []
                    last_flush = time.time()
            except Exception as e:
                print(f"OpenSearch worker error: {e}")

        # Final flush on shutdown
        if batch:
            self._flush_batch(batch)

    def _flush_batch(self, batch):
        """Send batch of logs to OpenSearch with retry logic"""
        if not batch:
            return

        for attempt in range(3):  # Retry up to 3 times
            try:
                if len(batch) == 1:
                    # Single log
                    log_entry = batch[0]
                    self.client.index(
                        index=log_entry['index'],
                        body=log_entry['body']
                    )
                else:
                    # Bulk insert
                    actions = []
                    for log_entry in batch:
                        actions.extend([
                            {"index": {"_index": log_entry['index']}},
                            log_entry['body']
                        ])
                    self.client.bulk(body=actions)
                break
            except Exception as e:
                if attempt == 2:  # Last attempt
                    print(f"Failed to send logs to OpenSearch after 3 attempts: {e}")
                else:
                    time.sleep(0.5 * (attempt + 1))  # Exponential backoff

    def _cleanup(self):
        """Cleanup on shutdown"""
        self.shutdown_event.set()
        if hasattr(self, 'worker_thread') and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5)

    def __call__(self, logger, method_name, event_dict):
        # Queue the log entry for background processing
        index_name = f"{self.index_prefix}-{datetime.now().strftime('%Y.%m')}"

        # Handle both dict and string event_dict
        if isinstance(event_dict, dict):
            body = event_dict.copy()
        else:
            # If event_dict is already a string (from JSON renderer), parse it back
            try:
                body = json.loads(event_dict) if isinstance(event_dict, str) else event_dict
            except (json.JSONDecodeError, TypeError):
                body = {'message': str(event_dict)}

        log_entry = {
            'index': index_name,
            'body': body
        }

        try:
            self.log_queue.put_nowait(log_entry)
        except Exception as e:
            print(f"Failed to queue log for OpenSearch: {e}")

        return event_dict


# Custom JSON renderer that beautifies the entire log output
def beautified_json_renderer(_, __, event_dict):
    """Render the log entry as beautified JSON with newlines"""
    try:
        beautified = json.dumps(event_dict, indent=2, default=str, ensure_ascii=False)
        return f"\n{beautified}\n"
    except (TypeError, ValueError):
        # Fallback to regular JSON if beautification fails
        return json.dumps(event_dict, default=str)


def configure_logging():
    # Get environment variables
    app_version = os.getenv('ECL_LOGGING_UTILITY_APP_VERSION', 'AMBIVALENT_APP_VERSION')
    service_name = os.getenv('ECL_LOGGING_UTILITY_SERVICE_NAME', 'AMBIVALENT_SERVICE_NAME')
    log_level = get_log_level()

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.CallsiteParameterAdder(
            [
                CallsiteParameter.PATHNAME,
                CallsiteParameter.LINENO,
                CallsiteParameter.MODULE,
                CallsiteParameter.FUNC_NAME,
            ]
        ),
        rename_fields,
        error_handler_processor,
        structlog.processors.EventRenamer(to='message'),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        beautified_json_renderer
    ]

    if os.environ.get('ECL_LOGGING_UTILITY_OPENSEARCH_ENABLED', 'False').lower() == 'true':
        # Initialize OpenSearch logger
        processors.append(OpenSearchLogger(service_name=service_name))

    structlog.configure(
        processors=processors,
        context_class=structlog.threadlocal.wrap_dict(dict),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        cache_logger_on_first_use=False,
    )

    # Create logger with static context
    return structlog.get_logger(service_name).bind(
        app_version=app_version,
        service_name=service_name
    )


# Initialize logger with static context
logger = configure_logging()