# Structured Logging Utilities for ECL microservices

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-Proprietary-lightgrey)

Internal package for consistent structured logging across ECL microservices. Features JSON formatting, automatic metadata capture, and environment-based configuration. Utility will also handle pushing logs to OpenSearch if the OpenSearch related environment variables are set.

## Features

- 📝 **Structured JSON logs** with consistent schema
- 🕒 **Automatic timestamping** in ISO 8601 format
- 📍 **Complete source location** (file path, line number, module, function)
- 🔍 **Query-ready fields** (transaction_id, request_ip, service_name)
- ⚙️ **Environment-controlled** log levels
- 🔗 **Request context propagation** across services
- ☁️ **Push logs to OpenSearch enterprise-grade search and observability suite that brings order to unstructured data at scale.**
- 👖 **Push error and critical logs to Slack**
- 🛡 **Private package** for internal use of ECL

## Environment Variables
- **ECL_LOGGING_UTILITY_LOG_LEVEL**: Set the log level, default: *INFO*
- **ECL_LOGGING_UTILITY_APP_VERSION**: Denotes the app version which will be displayed in the log, default: *AMBIVALENT_APP_VERSION*
- **ECL_LOGGING_UTILITY_SERVICE_NAME**: Denotes the service name which will be displayed in the log, default: *AMBIVALENT_SERVICE_NAME*
- **ECL_LOGGING_UTILITY_OPENSEARCH_ENABLED**: Flag to enable/disable pushing logs to OpenSearch endpoint, default: *False*
- **ECL_LOGGING_UTILITY_OPENSEARCH_HOST**: OpenSearch endpoint's host, default: *localhost*
- **ECL_LOGGING_UTILITY_OPENSEARCH_PORT**: OpenSearch endpoint's port, default: *9200*
- **ECL_LOGGING_UTILITY_OPENSEARCH_USERNAME**: Basic Auth username, default: *None*
- **ECL_LOGGING_UTILITY_OPENSEARCH_PASSWORD**: Basic Auth password, default: *None*
- **ECL_LOGGING_UTILITY_SLACK_WEBHOOK_URL**: Webhook URL of Slack channel to push notification in case of `error` & `critical` logs

## Installation

```bash
pip install ecl-logging-utility
```

## Usage
```python
from ecl_logging_utility import logger
logger.info("You have hit heartbeat", custom_1="1234", custom_2=500.0)
```

## Version History  
See [CHANGELOG.md](CHANGELOG.md) for release notes.  