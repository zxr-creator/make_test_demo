import pydot
import os


pseudo_targets = {'default_target', 'all', 'phony'}

# NOTE: 通过对于输入以及输出节点的公共节点和特有节点的分析，来判断workload的相似性
# TODO: 特有的叶子节点和根节点有哪些
# 把真正的路径弄出来，不要取最后一个文件名防止有些问题
# TODO: 大量的目标节点/根节点，没有找不到，那就无法完成我们想知道根节点是什么的目标
def find_true_roots(graph, initial_roots, node_dict):
    """
    递归追溯真正的根节点，跳过伪根节点（如 default_target 和 all）。
    """
    true_roots = set()
    to_process = set(initial_roots)
    processed = set()

    while to_process:
        root = to_process.pop()
        if root in processed:
            continue
        processed.add(root)

        if root not in node_dict:
            true_roots.add(root)
            continue

        node = node_dict[root]
        label = node.get('label').strip('"')
        
        if label in pseudo_targets:
            for edge in graph.get_edges():
                if edge.get_destination() == root:
                    to_process.add(edge.get_source())
        else:
            true_roots.add(root)

    return true_roots

def process_ninja_dot_file(file_path, output_file):
    """处理 Ninja 构建系统生成的 DOT 文件"""
    graphs = pydot.graph_from_dot_file(file_path)
    if not graphs:
        print(f"未找到图: {file_path}")
        return set(), set(), set(), set(), set()
    elif len(graphs) > 1:
        raise ValueError("不支持多个图")
    graph = graphs[0]

    node_set = set()
    label_set = set()
    root_files = set()
    leaf_files = set()
    
    # Ninja: 收集所有节点信息
    for node in graph.get_nodes():
        node_name = node.get_name()
        if node_name not in ('node', 'graph', 'edge'):
            node_set.add(node_name)
            label = node.get('label')
            if label:
                label = label.strip('"')
                filename = os.path.basename(label)
                label_set.add(filename)

    # Ninja: 从边扩展节点
    new_node_set = set()
    for edge in graph.get_edges():
        src = edge.get_source()
        dst = edge.get_destination()
        new_node_set.add(src)
        new_node_set.add(dst)

    if node_set != new_node_set:
        with open(output_file, 'a') as f:
            f.write(f"Warning: Ninja node set mismatch in {file_path}\n")
            f.write(f"Ninja graph.get_nodes() 独有: {node_set - new_node_set}\n")
            f.write(f"Ninja graph.get_edges() 独有: {new_node_set - node_set}\n")
        node_set.update(new_node_set)

    # Ninja: 计算入度和出度
    in_degree = {node: 0 for node in node_set}
    out_degree = {node: 0 for node in node_set}
    for edge in graph.get_edges():
        src = edge.get_source()
        dst = edge.get_destination()
        out_degree[src] += 1
        in_degree[dst] += 1

    # Ninja: 确定初始根节点和叶子节点
    leaves = [node for node, deg in in_degree.items() if deg == 0]
    roots = [node for node, deg in out_degree.items() if deg == 0]
    node_dict = {node.get_name(): node for node in graph.get_nodes()}
    roots = find_true_roots(graph, roots, node_dict)
    
    node_to_label = {node.get_name(): node.get('label').strip('"') 
                    for node in graph.get_nodes() if node.get('label')}

    # Ninja: 获取根节点和叶子节点文件名
    for node_name in roots:
        if node_name in node_to_label:
            filename = os.path.basename(node_to_label[node_name])
            if filename and filename not in pseudo_targets:
                root_files.add(filename)
    for node_name in leaves:
        if node_name in node_to_label:
            filename = os.path.basename(node_to_label[node_name])
            if filename:
                leaf_files.add(filename)

    # Ninja: 输出统计信息
    with open(output_file, 'a') as f:
        f.write(f"\n[Ninja] 处理文件: {os.path.basename(file_path)}\n")
        f.write(f"[Ninja] 节点个数: {len(node_set)}\n")
        f.write(f"[Ninja] 边的个数: {len(graph.get_edges())}\n")
        f.write(f"[Ninja] 根节点个数: {len(roots)}\n")
        f.write(f"[Ninja] 叶子节点个数: {len(leaves)}\n")
        f.write(f"[Ninja] 根节点对应的文件名: {sorted(root_files)}\n")
        f.write(f"[Ninja] 叶子节点对应的文件名: {sorted(leaf_files)}\n")

    return label_set, root_files, leaf_files, roots, leaves

def process_make_dot_file(file_path, output_file):
    """处理 Make 构建系统生成的 DOT 文件"""
    graphs = pydot.graph_from_dot_file(file_path)
    if not graphs:
        print(f"未找到图: {file_path}")
        return set(), set(), set(), set(), set()
    elif len(graphs) > 1:
        raise ValueError("不支持多个图")
    graph = graphs[0]

    node_set = set()
    label_set = set()
    root_files = set()
    leaf_files = set()

    # Make: 收集所有节点信息
    for node in graph.get_nodes():
        node_name = node.get_name()
        if node_name not in ('node', 'graph', 'edge'):
            node_set.add(node_name)
            label = node.get('label')
            if label:
                label = label.strip('"')
                filename = os.path.basename(label)
                label_set.add(filename)

    # Make: 从边扩展节点
    new_node_set = set()
    for edge in graph.get_edges():
        src = edge.get_source()
        dst = edge.get_destination()
        new_node_set.add(src)
        new_node_set.add(dst)

    if node_set != new_node_set:
        with open(output_file, 'a') as f:
            f.write(f"Warning: Make node set mismatch in {file_path}\n")
            f.write(f"Make graph.get_nodes() 独有: {node_set - new_node_set}\n")
            f.write(f"Make graph.get_edges() 独有: {new_node_set - node_set}\n")
        node_set.update(new_node_set)

    # Make: 计算入度和出度
    in_degree = {node: 0 for node in node_set}
    out_degree = {node: 0 for node in node_set}
    for edge in graph.get_edges():
        src = edge.get_source()
        dst = edge.get_destination()
        out_degree[src] += 1
        in_degree[dst] += 1

    # Make: 确定初始根节点和叶子节点
    leaves = [node for node, deg in in_degree.items() if deg == 0]
    roots = [node for node, deg in out_degree.items() if deg == 0]
    node_dict = {node.get_name(): node for node in graph.get_nodes()}
    roots = find_true_roots(graph, roots, node_dict)

    node_to_label = {node.get_name(): node.get('label').strip('"') 
                    for node in graph.get_nodes() if node.get('label')}

    # Make: 获取根节点和叶子节点文件名
    for node_name in roots:
        if node_name in node_to_label:
            filename = os.path.basename(node_to_label[node_name])
            if filename and filename not in pseudo_targets:
                root_files.add(filename)
    for node_name in leaves:
        if node_name in node_to_label:
            filename = os.path.basename(node_to_label[node_name])
            if filename:
                leaf_files.add(filename)

    # Make: 输出统计信息
    with open(output_file, 'a') as f:
        f.write(f"\n[Make] 处理文件: {os.path.basename(file_path)}\n")
        f.write(f"[Make] 节点个数: {len(node_set)}\n")
        f.write(f"[Make] 边的个数: {len(graph.get_edges())}\n")
        f.write(f"[Make] 根节点个数: {len(roots)}\n")
        f.write(f"[Make] 叶子节点个数: {len(leaves)}\n")
        f.write(f"[Make] 根节点对应的文件名: {sorted(root_files)}\n")
        f.write(f"[Make] 叶子节点对应的文件名: {sorted(leaf_files)}\n")

    return label_set, root_files, leaf_files, roots, leaves

if __name__ == '__main__':
    project_path = "./libpng"
    output_file = f"{project_path}/build/graph_analysis.txt"
    
    open(output_file, 'w', encoding='utf-8').close()
    
    # 处理 Ninja 和 Make DOT 文件
    (ninja_nodes, ninja_root_files, ninja_leaf_files, 
     ninja_roots, ninja_leaves) = process_ninja_dot_file(
        f"{project_path}/build/build_ninja/graph.dot", output_file)
    (make_nodes, make_root_files, make_leaf_files, 
     make_roots, make_leaves) = process_make_dot_file(
        f"{project_path}/build/build_make/graph.dot", output_file)
    
    # 计算交集和特有节点
    intersection = ninja_nodes.intersection(make_nodes)
    root_intersection = ninja_root_files.intersection(make_root_files)
    leaf_intersection = ninja_leaf_files.intersection(make_leaf_files)
    
    ninja_unique_roots = ninja_root_files - make_root_files
    make_unique_roots = make_root_files - ninja_root_files
    ninja_unique_leaves = ninja_leaf_files - make_leaf_files
    make_unique_leaves = make_leaf_files - ninja_leaf_files
    
    # 输出分析结果
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write("\n=== 比较分析 ===\n")
        f.write("\n[Ninja vs Make] 节点（文件名）的交集:\n")
        f.write(f"交集个数: {len(intersection)}\n")
        f.write(f"交集内容: {sorted(intersection)}\n")
        
        f.write("\n[Ninja vs Make] 根节点的比较:\n")
        f.write(f"共同根文件个数: {len(root_intersection)}\n")
        f.write(f"共同根文件内容: {sorted(root_intersection)}\n")
        f.write(f"Ninja特有根文件个数: {len(ninja_unique_roots)}\n")
        f.write(f"Ninja特有根文件内容: {sorted(ninja_unique_roots)}\n")
        f.write(f"Make特有根文件个数: {len(make_unique_roots)}\n")
        f.write(f"Make特有根文件内容: {sorted(make_unique_roots)}\n")
        
        f.write("\n[Ninja vs Make] 叶子节点的比较:\n")
        f.write(f"共同叶子文件个数: {len(leaf_intersection)}\n")
        f.write(f"共同叶子文件内容: {sorted(leaf_intersection)}\n")
        f.write(f"Ninja特有叶子文件个数: {len(ninja_unique_leaves)}\n")
        f.write(f"Ninja特有叶子文件内容: {sorted(ninja_unique_leaves)}\n")
        f.write(f"Make特有叶子文件个数: {len(make_unique_leaves)}\n")
        f.write(f"Make特有叶子文件内容: {sorted(make_unique_leaves)}\n")