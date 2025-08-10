"""Environment variable definitions for lighthouse OpenTelemetry integration.

This module defines environment variables used to configure the lighthouse OpenTelemetry integration.
Each environment variable includes documentation on its purpose, expected values, and defaults.
"""

lighthouse_TRACING_ENVIRONMENT = "lighthouse_TRACING_ENVIRONMENT"
"""
.. envvar:: lighthouse_TRACING_ENVIRONMENT

The tracing environment. Can be any lowercase alphanumeric string with hyphens and underscores that does not start with 'lighthouse'.

**Default value:** ``"default"``
"""

lighthouse_RELEASE = "lighthouse_RELEASE"
"""
.. envvar:: lighthouse_RELEASE

Release number/hash of the application to provide analytics grouped by release.
"""


lighthouse_PUBLIC_KEY = "lighthouse_PUBLIC_KEY"
"""
.. envvar:: lighthouse_PUBLIC_KEY

Public API key of lighthouse project
"""

lighthouse_SECRET_KEY = "lighthouse_SECRET_KEY"
"""
.. envvar:: lighthouse_SECRET_KEY

Secret API key of lighthouse project
"""

lighthouse_HOST = "https://lighthouse-observability.onrender.com"
"""
.. envvar:: lighthouse_HOST

Host of lighthouse API. Can be set via `lighthouse_HOST` environment variable.

**Default value:** ``"https://cloud.lighthouse.com"``
"""

lighthouse_DEBUG = "lighthouse_DEBUG"
"""
.. envvar:: lighthouse_DEBUG

Enables debug mode for more verbose logging.

**Default value:** ``"False"``
"""

lighthouse_TRACING_ENABLED = "lighthouse_TRACING_ENABLED"
"""
.. envvar:: lighthouse_TRACING_ENABLED

Enables or disables the lighthouse client. If disabled, all observability calls to the backend will be no-ops. Default is True. Set to `False` to disable tracing.

**Default value:** ``"True"``
"""

lighthouse_MEDIA_UPLOAD_THREAD_COUNT = "lighthouse_MEDIA_UPLOAD_THREAD_COUNT"
"""
.. envvar:: lighthouse_MEDIA_UPLOAD_THREAD_COUNT 

Number of background threads to handle media uploads from trace ingestion.

**Default value:** ``1``
"""

lighthouse_FLUSH_AT = "lighthouse_FLUSH_AT"
"""
.. envvar:: lighthouse_FLUSH_AT

Max batch size until a new ingestion batch is sent to the API.
**Default value:** ``15``
"""

lighthouse_FLUSH_INTERVAL = "lighthouse_FLUSH_INTERVAL"
"""
.. envvar:: lighthouse_FLUSH_INTERVAL

Max delay in seconds until a new ingestion batch is sent to the API.
**Default value:** ``1``
"""

lighthouse_SAMPLE_RATE = "lighthouse_SAMPLE_RATE"
"""
.. envvar: lighthouse_SAMPLE_RATE

Float between 0 and 1 indicating the sample rate of traces to bet sent to lighthouse servers.

**Default value**: ``1.0``

"""
lighthouse_OBSERVE_DECORATOR_IO_CAPTURE_ENABLED = (
    "lighthouse_OBSERVE_DECORATOR_IO_CAPTURE_ENABLED"
)
"""
.. envvar: lighthouse_OBSERVE_DECORATOR_IO_CAPTURE_ENABLED

Default capture of function args, kwargs and return value when using the @observe decorator.

Having default IO capture enabled for observe decorated function may have a performance impact on your application
if large or deeply nested objects are attempted to be serialized. Set this value to `False` and use manual
input/output setting on your observation to avoid this.

**Default value**: ``True``
"""

lighthouse_MEDIA_UPLOAD_ENABLED = "lighthouse_MEDIA_UPLOAD_ENABLED"
"""
.. envvar: lighthouse_MEDIA_UPLOAD_ENABLED

Controls whether media detection and upload is attempted by the SDK.

**Default value**: ``True``
"""

lighthouse_TIMEOUT = "lighthouse_TIMEOUT"
"""
.. envvar: lighthouse_TIMEOUT

Controls the timeout for all API requests in seconds

**Default value**: ``5``
"""
