import pydot
import os

def process_dot_file(file_path, output_file):
    # 读取 DOT 文件（可能包含多个图，这里取第一个）
    graphs = pydot.graph_from_dot_file(file_path)
    if len(graphs) == 0:
        print(f"未找到图: {file_path}")
        return set()
    elif len(graphs) > 1:
        raise ValueError("不支持多个图")
    graph = graphs[0]
    
    # 用显式节点和边上出现的节点构造节点集合
    node_set = set()
    label_set = set()  # 存储 label 的集合
    for node in graph.get_nodes():
        node_name = node.get_name()
        if node_name not in ('node', 'graph', 'edge'):  # 排除 pydot 内部符号，一些metadata
            node_set.add(node_name)
            label = node.get('label')  # 获取 label 属性
            if label:
                label = label.strip('"')  # 去掉引号
                filename = os.path.basename(label)  # 提取文件名
                label_set.add(filename)
            else:
                print(f"Warning: Node {node_name} has no label.")
            
    new_node_set = set()
    for edge in graph.get_edges():
        src_node_name = edge.get_source()
        dst_node_name = edge.get_destination()
        new_node_set.add(src_node_name)
        new_node_set.add(dst_node_name)

    if node_set != new_node_set:
        with open(output_file, 'a') as f:  
            f.write(f"Warning: node set mismatch in {file_path}")
            f.write(f"graph.get_nodes() 独有的节点: {node_set - new_node_set}")
            f.write(f"graph.get_edges()的edge的src和dst node中 独有的节点: {new_node_set - node_set}")
        node_set = node_set.union(new_node_set)

    node_count = len(node_set)
    edges = graph.get_edges()
    edge_count = len(edges)
    
    # 初始化入度和出度
    in_degree = {node_name: 0 for node_name in node_set}
    out_degree = {node_name: 0 for node_name in node_set}
    for edge in edges:
        src_node_name = edge.get_source()
        dst_node_name = edge.get_destination()
        out_degree[src_node_name] += 1
        in_degree[dst_node_name] += 1

    # 叶子节点：出度为 0
    leaves = [node_name for node_name, deg in in_degree.items() if deg == 0]
    # 根节点：入度为 0
    roots = [node_name for node_name, deg in out_degree.items() if deg == 0]

    # 将输出写入文件
    with open(output_file, 'a') as f:  # 'a' 表示追加模式
        f.write(f"\n处理文件: {os.path.basename(file_path)}\n")
        f.write(f"节点个数: {node_count}\n")
        f.write(f"边的个数: {edge_count}\n")
        f.write(f"根节点个数: {len(roots)}\n")
        f.write(f"叶子节点个数: {len(leaves)}\n")
        f.write(f"根节点的哈希: {roots}\n")
        f.write(f"叶子节点的哈希: {leaves}\n")
    
    return label_set

if __name__ == '__main__':
    project_path = input("请输入工程路径：").strip()
    output_file = f"{project_path}/build/graph_analysis.txt"
    
    # 清空输出文件内容（覆盖写入）
    open(output_file, 'w', encoding='utf-8').close()
    
    # 处理两个 DOT 文件（假定 process_dot_file 已经定义）
    ninja_nodes = process_dot_file(f"{project_path}/build/build_ninja/graph.dot", output_file)
    make_nodes = process_dot_file(f"{project_path}/build/build_make/graph.dot", output_file)
    
    # 计算交集
    intersection = ninja_nodes.intersection(make_nodes)
    
    # 将结果追加写入输出文件
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write("\n两个图中节点（文件名）的交集:\n")
        f.write(f"交集个数: {len(intersection)}\n")
        f.write(f"交集内容: {sorted(intersection)}\n")