class Table:
    def __init__(self):
        self.data =[]

    def insert(self, student):
        self.data.append(student)
        return len(self.data) - 1  # Trả về Pointer (Index của dòng)

    def get(self, index):
        if index is None or index >= len(self.data):
            return None
        return self.data[index]

    def delete(self, index):
        # Gán None thay vì pop() để giữ nguyên pointer của các record khác
        if 0 <= index < len(self.data):
            self.data[index] = None