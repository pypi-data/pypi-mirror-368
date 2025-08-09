from .taskmanager import TaskManager
from .broker import MessageBroker
from .bemcp.bemcp import MCPManager

"""
全局共享实例
"""

task_manager = TaskManager()
broker = MessageBroker()
mcp_manager = MCPManager()