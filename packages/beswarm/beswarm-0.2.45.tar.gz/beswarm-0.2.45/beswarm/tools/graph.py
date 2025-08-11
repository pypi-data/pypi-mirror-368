from ..aient.src.aient.plugins import register_tool
from ..core import kgm

@register_tool()
def add_knowledge_node(parent_path: str, node_name: str, description: str = "") -> str:
    """
    在知识图谱的指定父路径下添加一个新节点。

    Args:
        parent_path (str): 父节点的路径。路径由'/'分隔，例如 'a/b'。根节点路径为 '.' 或 '/'。
        node_name (str): 新节点的名称。名称中不能包含'/'字符。
        description (str, optional): 节点的可选描述信息。默认为空字符串。

    Returns:
        str: 操作结果的描述信息，例如成功或失败的原因。
    """
    return kgm.add_node(parent_path, node_name, description)

@register_tool()
def delete_knowledge_node(node_path: str) -> str:
    """
    从知识图谱中删除一个节点及其所有后代节点。

    Args:
        node_path (str): 要删除的节点的完整路径，例如 'a/b/c'。不允许删除根节点。

    Returns:
        str: 操作结果的描述信息，例如成功或失败的原因。
    """
    return kgm.delete_node(node_path)

@register_tool()
def rename_knowledge_node(node_path: str, new_name: str) -> str:
    """
    重命名知识图谱中的一个现有节点。

    Args:
        node_path (str): 要重命名的节点的当前完整路径。
        new_name (str): 节点的新名称。名称中不能包含'/'字符。

    Returns:
        str: 操作结果的描述信息，例如成功或失败的原因。
    """
    return kgm.rename_node(node_path, new_name)

@register_tool()
def move_knowledge_node(source_path: str, target_parent_path: str) -> str:
    """
    将一个节点（及其整个子树）移动到知识图谱中的另一个父节点下。

    Args:
        source_path (str): 要移动的节点的当前完整路径。
        target_parent_path (str): 目标父节点的完整路径。节点将被移动到这个新父节点之下。

    Returns:
        str: 操作结果的描述信息，例如成功或失败的原因。
    """
    return kgm.move_node(source_path, target_parent_path)

@register_tool()
def get_knowledge_graph_tree() -> str:
    """
    渲染并返回整个知识图谱的文本树状图。

    此工具不需要任何参数，它会读取当前的图状态并生成一个易于阅读的、
    表示层级结构的字符串。

    注意：此函数返回的知识图谱状态是实时更新的，永远是最新的。只需要调用一次，不必重复调用。

    Returns:
        str: 表示整个知识图谱的、格式化的树状结构字符串。
    """
    return "<knowledge_graph_tree>" + kgm.render_tree() + "</knowledge_graph_tree>"
