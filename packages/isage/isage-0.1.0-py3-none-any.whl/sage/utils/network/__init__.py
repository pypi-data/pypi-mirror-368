"""
Network utilities module

Re-exports network functionality from sage.common.utils.network
"""

try:
    from sage.common.utils.network.base_tcp_client import BaseTcpClient
    from sage.common.utils.network.local_tcp_server import BaseTcpServer, LocalTcpServer
except ImportError:
    # Fallback if sage-common is not available
    class BaseTcpClient:
        pass
    
    class BaseTcpServer:
        pass
    
    class LocalTcpServer:
        pass

__all__ = [
    "BaseTcpClient",
    "BaseTcpServer", 
    "LocalTcpServer"
]
