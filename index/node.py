class BTreeNode:
    def __init__(self, leaf=True):
        self.leaf = leaf
        self.keys =[]      # Danh sách các key (MSSV hoặc Name)
        self.pointers = []  # Danh sách list các pointers: VD [[0],[1, 2]]
        self.children =[]  # Danh sách các node con