from storage.table import Table
from index.btree import BTree
from visualization.printer import print_system_state

class StudentService:
    def __init__(self):
        self.table = Table()
        self.index_mssv = BTree(order=3)
        self.index_name = BTree(order=3)

    def show_state(self):
        print_system_state(self.table, self.index_mssv, self.index_name)

    def add(self, student):
        print(f"\n{'='*10} INSERT ({student.sid}, {student.name}) {'='*10}")
        print("BEFORE:")
        self.show_state()

        # 1. Thêm vào Table lấy Pointer
        ptr = self.table.insert(student)

        # 2. Thêm vào 2 Index
        self.index_mssv.insert(student.sid, ptr)
        self.index_name.insert(student.name, ptr)

        print("AFTER:")
        self.show_state()

    def delete(self, sid):
        print(f"\n{'='*10} DELETE ({sid}) {'='*10}")
        print("BEFORE:")
        self.show_state()

        # 1. Tìm pointer qua MSSV Index
        ptrs = self.index_mssv.search(sid)
        if not ptrs:
            print("Không tìm thấy sinh viên!")
            return
        
        ptr = ptrs[0]
        student = self.table.get(ptr)

        if student:
            # 2. Xóa Pointer khỏi các Index
            self.index_mssv.delete_pointer(student.sid, ptr)
            self.index_name.delete_pointer(student.name, ptr)
            
            # 3. Mark delete trong Table
            self.table.delete(ptr)

        print("AFTER:")
        self.show_state()

    def search_by_name(self, name):
        print(f"\n--- SEARCH NAME: '{name}' ---")
        ptrs = self.index_name.search(name)
        if not ptrs:
            print("Không tìm thấy!")
            return
        
        print(f"-> B-Tree Name found pointers: {ptrs}")
        print("-> TABLE records:")
        for ptr in ptrs:
            student = self.table.get(ptr)
            if student:
                print(f"[{ptr}] {student}")