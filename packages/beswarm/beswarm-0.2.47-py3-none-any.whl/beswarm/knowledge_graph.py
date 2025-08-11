import uuid
import networkx as nx
from pathlib import Path

class KnowledgeGraphManager:
    """
    一个使用 NetworkX 管理知识图谱的管理器。
    - 图数据存储在 networkx.DiGraph 对象中。
    - 数据持久化为 GraphML 文件。
    - 提供添加、删除、重命名、移动节点和渲染树状图的功能。
    """
    def __init__(self, storage_path="knowledge_graph.graphml", broker=None, publish_topic=None):
        """
        初始化知识图谱管理器。

        Args:
            storage_path (str, optional): GraphML文件的存储路径。
                                          默认为 'knowledge_graph.graphml'。
        """
        self.storage_path = Path(storage_path)
        self.graph = nx.DiGraph()
        self.root_path = None
        self.broker = broker
        self.publish_topic = publish_topic
        # self._load_graph()

    def set_root_path(self, root_path):
        """设置工作根目录并加载持久化的任务状态。"""
        if self.root_path is not None:
            return
        self.root_path = Path(root_path)
        self.cache_dir = self.root_path / ".beswarm"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.storage_path = self.cache_dir / "knowledge_graph.graphml"

        self._load_graph()

    def _load_graph(self):
        """从文件加载图，如果文件不存在或加载失败，则创建一个新的。"""
        if self.storage_path.exists():
            try:
                self.graph = nx.read_graphml(self.storage_path, node_type=str)
            except Exception:
                self._create_new_graph()
        else:
            self._create_new_graph()

    def _create_new_graph(self):
        """创建一个带有根节点的新图谱并保存。"""
        self.graph = nx.DiGraph()
        self.graph.add_node("root", name=".", description="知识图谱根节点")
        self._save_graph()

    def set_publish_topic(self, publish_topic):
        if not publish_topic:
            return
        self.publish_topic = publish_topic

    def _save_graph(self):
        """将当前图的状态保存到文件。"""
        nx.write_graphml(self.graph, self.storage_path)

        if self.publish_topic and self.broker:
            self.broker.publish({"message": "graph_updated", "graph": self.render_tree()}, self.publish_topic)

    def _get_node_id_by_path(self, path: str):
        """通过'/'分隔的路径查找节点的唯一ID，支持前缀匹配。"""
        if path is None or not path.strip() or path.strip() in ['.', '/']:
            return "root"

        segments = [s for s in path.strip('/').split('/') if s and s != '.']
        current_node_id = "root"

        for segment in segments:
            # 首先尝试完全匹配
            found_child = False
            for child_id in self.graph.successors(current_node_id):
                if self.graph.nodes[child_id].get('name') == segment:
                    current_node_id = child_id
                    found_child = True
                    break

            if found_child:
                continue

            # 如果完全匹配失败，尝试前缀匹配
            prefix_matches = []
            for child_id in self.graph.successors(current_node_id):
                child_name = self.graph.nodes[child_id].get('name', '')
                if child_name.startswith(segment):
                    prefix_matches.append(child_id)

            if len(prefix_matches) == 1:
                # 只有一个前缀匹配，使用这个节点
                current_node_id = prefix_matches[0]
            elif len(prefix_matches) > 1:
                # 多个前缀匹配，存在歧义，返回None
                return None
            else:
                # 没有前缀匹配，节点不存在
                return None

        return current_node_id

    def add_node(self, parent_path: str, node_name: str, description: str = "") -> str:
        """在指定父节点下添加一个新节点。"""
        if not node_name.strip():
            return "❌ 错误：节点名称不能为空。"
        if '/' in node_name:
            return f"❌ 错误：节点名称 '{node_name}' 不能包含'/'。"

        parent_id = self._get_node_id_by_path(parent_path)
        if parent_id is None:
            return f"❌ 错误：父路径 '{parent_path}' 不存在。"

        for child_id in self.graph.successors(parent_id):
            if self.graph.nodes[child_id].get('name') == node_name:
                return f"❌ 错误：在 '{parent_path}' 下已存在名为 '{node_name}' 的节点。"

        new_node_id = str(uuid.uuid4())
        self.graph.add_node(new_node_id, name=node_name, description=description)
        self.graph.add_edge(parent_id, new_node_id)
        self._save_graph()
        return f"✅ 成功在 '{parent_path}' 下添加节点 '{node_name}'。"

    def delete_node(self, node_path: str) -> str:
        """删除一个节点及其所有子孙节点。"""
        if node_path is None or node_path.strip() in ['.', '/']:
            return "❌ 错误：不能删除根节点。"

        node_id = self._get_node_id_by_path(node_path)
        if node_id is None:
            return f"❌ 错误：路径 '{node_path}' 不存在。"
        if node_id == "root":
            return "❌ 错误：不能删除根节点。"

        descendants = nx.descendants(self.graph, node_id)
        self.graph.remove_nodes_from(descendants.union({node_id}))
        self._save_graph()
        return f"✅ 成功删除节点 '{node_path}' 及其所有子节点。"

    def rename_node(self, node_path: str, new_name: str) -> str:
        """重命名一个节点。"""
        if not new_name.strip():
            return "❌ 错误：新名称不能为空。"
        if '/' in new_name:
            return f"❌ 错误：新名称 '{new_name}' 不能包含'/'。"

        node_id = self._get_node_id_by_path(node_path)
        if node_id is None:
            return f"❌ 错误：路径 '{node_path}' 不存在。"
        if node_id == "root":
            return "❌ 错误：不能重命名根节点。"

        parent_id = list(self.graph.predecessors(node_id))[0]
        for sibling_id in self.graph.successors(parent_id):
            if sibling_id != node_id and self.graph.nodes[sibling_id].get('name') == new_name:
                return f"❌ 错误：同级目录下已存在名为 '{new_name}' 的节点。"

        self.graph.nodes[node_id]['name'] = new_name
        self._save_graph()
        return f"✅ 成功将节点 '{node_path}' 重命名为 '{new_name}'。"

    def move_node(self, source_path: str, target_parent_path: str) -> str:
        """将一个节点移动到另一个父节点下。"""
        source_id = self._get_node_id_by_path(source_path)
        if source_id is None:
            return f"❌ 错误：源路径 '{source_path}' 不存在。"
        if source_id == "root":
            return "❌ 错误：不能移动根节点。"

        target_parent_id = self._get_node_id_by_path(target_parent_path)
        if target_parent_id is None:
            return f"❌ 错误：目标父路径 '{target_parent_path}' 不存在。"

        if source_id == target_parent_id or target_parent_id in nx.descendants(self.graph, source_id):
            return "❌ 错误：不能将节点移动到其自身或其子孙节点下。"

        source_name = self.graph.nodes[source_id]['name']
        for child_id in self.graph.successors(target_parent_id):
            if self.graph.nodes[child_id].get('name') == source_name:
                return f"❌ 错误：目标目录 '{target_parent_path}' 下已存在同名节点 '{source_name}'。"

        old_parent_id = list(self.graph.predecessors(source_id))[0]
        self.graph.remove_edge(old_parent_id, source_id)
        self.graph.add_edge(target_parent_id, source_id)
        self._save_graph()
        return f"✅ 成功将节点 '{source_path}' 移动到 '{target_parent_path}' 下。"

    def render_tree(self) -> str:
        """渲染整个知识图谱为树状结构的文本。"""
        if not self.graph or "root" not in self.graph:
            return "图谱为空或未正确初始化。"

        root_name = self.graph.nodes["root"].get("name", ".")
        tree_lines = [root_name]
        self._build_tree_string_recursive("root", "", tree_lines)
        return "\n".join(tree_lines)

    def _build_tree_string_recursive(self, parent_id, prefix, tree_lines):
        """递归辅助函数，用于构建树状图字符串。"""
        children = sorted(list(self.graph.successors(parent_id)), key=lambda n: self.graph.nodes[n].get('name', ''))
        for i, child_id in enumerate(children):
            is_last = (i == len(children) - 1)
            connector = "└── " if is_last else "├── "
            node_name = self.graph.nodes[child_id].get('name', '[Unnamed Node]')
            tree_lines.append(f"{prefix}{connector}{node_name}")
            new_prefix = prefix + "    " if is_last else prefix + "│   "
            self._build_tree_string_recursive(child_id, new_prefix, tree_lines)