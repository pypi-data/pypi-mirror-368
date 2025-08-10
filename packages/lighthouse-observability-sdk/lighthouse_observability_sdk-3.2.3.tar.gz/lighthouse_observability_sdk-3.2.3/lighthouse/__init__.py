""".. include:: ../README.md"""

from ._client import client as _client_module
from ._client.attributes import lighthouseOtelSpanAttributes
from ._client.get_client import get_client
from ._client.observe import observe
from ._client.span import lighthouseEvent, lighthouseGeneration, lighthouseSpan

lighthouse = _client_module.lighthouse

__all__ = [
    "lighthouse",
    "get_client",
    "observe",
    "lighthouseSpan",
    "lighthouseGeneration",
    "lighthouseEvent",
    "lighthouseOtelSpanAttributes",
]
