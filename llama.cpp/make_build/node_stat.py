import pydot

def process_dot_file(file_path):
    # 读取 DOT 文件（可能包含多个图，这里取第一个）
    graphs = pydot.graph_from_dot_file(file_path)
    graph = graphs[0]
    
    # 用显式节点和边上出现的节点构造节点集合
    node_set = set()
    for node in graph.get_nodes():
        name = node.get_name().strip('"')
        if name not in ('node', 'graph', 'edge'):  # 排除一些 pydot 内部符号
            node_set.add(name)
    for edge in graph.get_edges():
        src = edge.get_source().strip('"')
        dst = edge.get_destination().strip('"')
        node_set.add(src)
        node_set.add(dst)
    
    node_count = len(node_set)
    edges = graph.get_edges()
    edge_count = len(edges)
    
    # 初始化入度和出度
    in_degree = {node: 0 for node in node_set}
    out_degree = {node: 0 for node in node_set}
    for edge in edges:
        src = edge.get_source().strip('"')
        dst = edge.get_destination().strip('"')
        out_degree[src] += 1
        in_degree[dst] += 1

    # 根节点：入度为 0
    roots = [node for node, deg in in_degree.items() if deg == 0]
    # 叶子节点：出度为 0
    leaves = [node for node, deg in out_degree.items() if deg == 0]

    print("节点个数:", node_count)
    print("边的个数:", edge_count)
    print("根节点个数:", len(roots))
    print("叶子节点个数:", len(leaves))
    print("根节点:", roots)
    print("叶子节点:", leaves)

if __name__ == '__main__':
    process_dot_file('llama_make_graph.dot')