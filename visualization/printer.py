def print_table(table):
    print("TABLE:")
    has_data = False
    for i, s in enumerate(table.data):
        if s is not None:
            print(f"[{i}] {s.sid} | {s.name}")
            has_data = True
    if not has_data:
        print("(Empty)")

def print_btree(node, prefix="", is_last=True):
    if not node:
        return

    print(prefix + ("└── " if is_last else "├── ") + str(node.keys))

    new_prefix = prefix + ("    " if is_last else "│   ")

    for i, child in enumerate(node.children):
        last = (i == len(node.children) - 1)
        print_btree(child, new_prefix, last)

def print_mappings(node):
    """In ra map (Key -> [Pointers]) để dễ hình dung"""
    if not node:
        return
    for i, key in enumerate(node.keys):
        if node.pointers[i]:  # Chỉ in những key còn pointer
            print(f"({key} → {node.pointers[i]})")
    for child in node.children:
        print_mappings(child)

def print_system_state(table, index_mssv, index_name):
    print_table(table)
    print("\nB-TREE MSSV:")
    print_btree(index_mssv.root)
    print_mappings(index_mssv.root)
    
    print("\nB-TREE NAME:")
    print_btree(index_name.root)
    print_mappings(index_name.root)
    print("-" * 40)