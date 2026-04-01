from index.node import BTreeNode

class BTree:
    def __init__(self, order=3):
        self.root = BTreeNode(True)
        self.order = order
        self.min_keys = (order - 1) // 2  # Số khóa tối thiểu trong một node (trừ root)

    def search(self, key, node=None):
        if node is None:
            node = self.root
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        
        if i < len(node.keys) and key == node.keys[i]:
            return node.pointers[i]
        elif node.leaf:
            return []
        else:
            return self.search(key, node.children[i])

    def insert(self, key, pointer):
        # Nếu trùng key, chỉ append pointer
        if self._append_if_exists(self.root, key, pointer):
            return

        # Gọi hàm đệ quy chèn từ dưới lên
        promoted_key, promoted_ptr, new_right_child = self._insert_bottom_up(self.root, key, pointer)

        # Nếu Node Gốc bị nổ và đẩy 1 khóa lên -> Tạo Gốc mới
        if promoted_key is not None:
            new_root = BTreeNode(False)
            new_root.keys = [promoted_key]
            new_root.pointers = [promoted_ptr] # Chú ý: promoted_ptr đã là 1 list
            new_root.children = [self.root, new_right_child]
            self.root = new_root

    def _insert_bottom_up(self, node, key, pointer):
        """Hàm đệ quy: Chèn trước, nếu đầy (đạt 3 khóa) thì nổ và đẩy lên trên"""
        i = len(node.keys) - 1
        
        # --- BƯỚC 1: ĐI XUỐNG TÌM CHỖ CHÈN ---
        if node.leaf:
            # Nếu là lá: Chèn luôn vào mảng (dù có làm mảng phình ra thành 3 khóa)
            node.keys.append(None)
            node.pointers.append(None)
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                node.pointers[i + 1] = node.pointers[i]
                i -= 1
            node.keys[i + 1] = key
            node.pointers[i + 1] = [pointer]
        else:
            # Nếu là Node trong: Tìm đường đi xuống
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            
            # Đệ quy xuống Node con
            p_key, p_ptr, right_child = self._insert_bottom_up(node.children[i], key, pointer)
            
            # Nếu Node con ở dưới BỊ NỔ và đẩy dữ liệu lên
            if p_key is not None:
                node.keys.insert(i, p_key)
                node.pointers.insert(i, p_ptr)
                node.children.insert(i + 1, right_child)

        # --- BƯỚC 2: KIỂM TRA OVERFLOW (Quá tải) TRƯỚC KHI QUAY LUI ---
        # Bậc 3 -> Max keys là 2. Nếu sau khi chèn có >= 3 khóa -> BỊ NỔ (Split)
        if len(node.keys) > self.order - 1:
            mid = len(node.keys) // 2  # Với 3 khóa, mid = 1 (khóa ở giữa)
            
            # Lấy khóa ở giữa để đẩy lên cha
            promoted_key = node.keys[mid]
            promoted_ptr = list(node.pointers[mid])
            
            # Tạo Node mới chứa nửa bên phải
            new_sibling = BTreeNode(node.leaf)
            new_sibling.keys = node.keys[mid + 1:]
            new_sibling.pointers = node.pointers[mid + 1:]
            
            # Giữ lại nửa bên trái cho Node hiện tại
            node.keys = node.keys[:mid]
            node.pointers = node.pointers[:mid]
            
            # Chia lại Node con (nếu không phải lá)
            if not node.leaf:
                new_sibling.children = node.children[mid + 1:]
                node.children = node.children[:mid + 1]
                
            # Trả về khóa bị đẩy lên để Node cha tiếp nhận
            return promoted_key, promoted_ptr, new_sibling
            
        # Nếu an toàn (<= 2 khóa), không cần đẩy gì lên
        return None, None, None
    
    def _append_if_exists(self, node, key, pointer):
        """Hàm tìm xem key đã tồn tại chưa, nếu có thì chỉ thêm pointer vào list"""
        i = 0
        # Kiểm tra các khóa ở node hiện tại
        while i < len(node.keys):
            if key == node.keys[i]:
                if pointer not in node.pointers[i]:
                    node.pointers[i].append(pointer)
                return True
            if key < node.keys[i]:
                break
            i += 1

        # Nếu là lá mà tìm đến đây không thấy thì nghĩa là key chưa tồn tại
        if node.leaf:
            return False

        # Nếu không phải lá, đệ quy xuống node con tương ứng
        # i lúc này đang dừng ở vị trí con trỏ dẫn đến node con chứa key tiềm năng
        return self._append_if_exists(node.children[i], key, pointer)

    def delete_pointer(self, key, pointer):
        """Bước 1: Tìm key và xóa pointer. Nếu key hết pointer thì xóa key khỏi cấu trúc B-Tree"""
        if not self.root:
            return
            
        node = self._find_node(self.root, key)
        if not node:
            return  # Key không tồn tại
            
        idx = node.keys.index(key)
        if pointer in node.pointers[idx]:
            node.pointers[idx].remove(pointer)
            
        # Bước 2: Nếu không còn pointer nào, thực hiện xóa key khỏi cấu trúc cây
        if len(node.pointers[idx]) == 0:
            self._delete_structural(key)

    def _find_node(self, node, key):
        """Hàm phụ trợ tìm Node chứa Key"""
        if not node: return None
        i = 0
        while i < len(node.keys) and key > node.keys[i]: i += 1
        if i < len(node.keys) and key == node.keys[i]: return node
        if node.leaf: return None
        return self._find_node(node.children[i], key)

    def _delete_structural(self, key):
        """Hàm khởi chạy xoá cấu trúc và xử lý Trường hợp III (Giảm chiều cao cây)"""
        self._delete_key_recursive(self.root, key)
        
        # TRƯỜNG HỢP III: Chiều cao cây thu hẹp lại
        # Nếu sau khi hợp nhất (merge) lan lên tới gốc, root không còn key nào
        if len(self.root.keys) == 0:
            if not self.root.leaf:
                # Root trở thành node con đầu tiên
                self.root = self.root.children[0] 
            else:
                # Cây rỗng hoàn toàn
                self.root = BTreeNode(True)

    def _delete_key_recursive(self, node, key):
        idx = 0
        while idx < len(node.keys) and key > node.keys[idx]:
            idx += 1
            
        # --- NẾU TÌM THẤY KHÓA TRONG NODE NÀY ---
        if idx < len(node.keys) and node.keys[idx] == key:
            if node.leaf:
                # TRƯỜNG HỢP I: Khóa được xóa nằm ở node lá
                node.keys.pop(idx)
                node.pointers.pop(idx)
            else:
                # TRƯỜNG HỢP II: Khóa cần xóa nằm ở node bên trong
                left_child = node.children[idx]
                right_child = node.children[idx + 1]
                min_keys = (self.order - 1) // 2 # Bậc 3 -> min_keys = 1
                
                # TH II.1: Node con trái có nhiều hơn số khóa tối thiểu
                if len(left_child.keys) > min_keys:
                    pred_key, pred_ptrs = self._get_max(left_child) # Tìm node trước (predecessor)
                    node.keys[idx] = pred_key
                    node.pointers[idx] = list(pred_ptrs)
                    self._delete_key_recursive(left_child, pred_key)
                    
                # TH II.2: Node con phải có nhiều hơn số khóa tối thiểu
                elif len(right_child.keys) > min_keys:
                    succ_key, succ_ptrs = self._get_min(right_child) # Tìm node kế nhiệm (successor)
                    node.keys[idx] = succ_key
                    node.pointers[idx] = list(succ_ptrs)
                    self._delete_key_recursive(right_child, succ_key)
                    
                # TH II.3: Cả hai con đều có chính xác số lượng khóa tối thiểu
                else:
                    self._merge(node, idx) # Hợp nhất 2 node con
                    # Sau khi hợp nhất, khóa đã bị đẩy xuống node con bên trái, đệ quy xóa tiếp
                    self._delete_key_recursive(node.children[idx], key)
                    
        # --- NẾU KHÔNG TÌM THẤY KHÓA TRONG NODE NÀY (Đệ quy xuống con) ---
        else:
            if node.leaf:
                return # Khóa không tồn tại trong cây
                
            child_idx = idx
            self._delete_key_recursive(node.children[child_idx], key)
            
            # KIỂM TRA TRƯỜNG HỢP I & III (Sau khi đệ quy xóa):
            # Nếu việc xóa làm node con mất khóa, bị vi phạm số lượng tối thiểu
            if len(node.children[child_idx].keys) < ((self.order - 1) // 2) or len(node.children[child_idx].keys) == 0:
                self._fix_child(node, child_idx)

    def _fix_child(self, node, idx):
        """Xử lý node con vi phạm số lượng khóa tối thiểu"""
        min_keys = (self.order - 1) // 2
        
        # Mượn từ node anh em bên trái
        if idx > 0 and len(node.children[idx - 1].keys) > min_keys:
            self._borrow_from_left(node, idx)
            
        # Mượn từ node anh em bên phải
        elif idx < len(node.children) - 1 and len(node.children[idx + 1].keys) > min_keys:
            self._borrow_from_right(node, idx)
            
        # Cả hai node anh em đã có số lượng khóa tối thiểu -> Hợp nhất
        else:
            if idx > 0:
                self._merge(node, idx - 1)
            else:
                self._merge(node, idx)

    def _borrow_from_left(self, node, idx):
        child = node.children[idx]
        sibling = node.children[idx - 1]
        
        # 1. Kéo khóa từ node cha xuống child
        child.keys.insert(0, node.keys[idx - 1])
        child.pointers.insert(0, node.pointers[idx - 1])
        
        # 2. Đẩy khóa lớn nhất của anh em trái lên làm cha
        node.keys[idx - 1] = sibling.keys.pop(-1)
        node.pointers[idx - 1] = sibling.pointers.pop(-1)
        
        # 3. Kéo node con của anh em trái sang child
        if not child.leaf:
            child.children.insert(0, sibling.children.pop(-1))

    def _borrow_from_right(self, node, idx):
        child = node.children[idx]
        sibling = node.children[idx + 1]
        
        # 1. Kéo khóa từ node cha xuống child
        child.keys.append(node.keys[idx])
        child.pointers.append(node.pointers[idx])
        
        # 2. Đẩy khóa nhỏ nhất của anh em phải lên làm cha
        node.keys[idx] = sibling.keys.pop(0)
        node.pointers[idx] = sibling.pointers.pop(0)
        
        # 3. Kéo node con của anh em phải sang child
        if not child.leaf:
            child.children.append(sibling.children.pop(0))

    def _merge(self, node, idx):
        """Hợp nhất node con thứ idx và idx+1"""
        left = node.children[idx]
        right = node.children[idx + 1]
        
        # 1. Kéo khóa từ cha xuống
        left.keys.append(node.keys.pop(idx))
        left.pointers.append(node.pointers.pop(idx))
        
        # 2. Gộp toàn bộ dữ liệu từ node phải sang node trái
        left.keys.extend(right.keys)
        left.pointers.extend(right.pointers)
        if not left.leaf:
            left.children.extend(right.children)
            
        # 3. Loại bỏ node phải khỏi danh sách con của cha
        node.children.pop(idx + 1)

        # 🔥 ĐIỀU CHỈNH QUAN TRỌNG CHO BẬC 3:
        # Nếu sau khi gộp, node trái có 3 khóa, ta phải split nó ngay
        if len(left.keys) > self.order - 1:
            self._split_child_during_delete(node, idx)

    def _delete_key_recursive(self, node, key):
        idx = 0
        while idx < len(node.keys) and key > node.keys[idx]:
            idx += 1
            
        # --- NẾU TÌM THẤY KHÓA TRONG NODE NÀY ---
        if idx < len(node.keys) and node.keys[idx] == key:
            if node.leaf:
                # TÌNH HUỐNG 1: Ở node lá -> Xóa trực tiếp
                node.keys.pop(idx)
                node.pointers.pop(idx)
            else:
                # TÌNH HUỐNG 2: Ở node trung gian -> Tráo đổi với Predecessor
                left_child = node.children[idx]
                
                # Tìm khóa lớn nhất nhánh trái để "Thế thân"
                pred_key, pred_ptrs = self._get_max(left_child) 
                node.keys[idx] = pred_key
                node.pointers[idx] = list(pred_ptrs)
                
                # Đệ quy xuống nhánh trái để xóa khóa thế thân
                self._delete_key_recursive(left_child, pred_key)
                
                # CHỐT CHẶN BẢO VỆ (Bottom-up): Khi đệ quy đi lên, nếu phát hiện con bị thiếu khóa
                if len(left_child.keys) < self.min_keys:
                    self._fix_child(node, idx)
                    
        # --- NẾU KHÔNG TÌM THẤY Ở ĐÂY (Đi xuống con tìm tiếp) ---
        else:
            if node.leaf:
                return # Key không tồn tại
                
            self._delete_key_recursive(node.children[idx], key)
            
            # CHỐT CHẶN BẢO VỆ: Nếu việc xóa ở dưới làm node con này bị thiếu khóa
            if len(node.children[idx].keys) < self.min_keys:
                self._fix_child(node, idx)

    def _merge(self, node, idx):
        """Hợp nhất node con thứ idx và idx+1 (Đã tinh gọn, không cần hàm split phụ nữa)"""
        left = node.children[idx]
        right = node.children[idx + 1]
        
        # 1. Kéo 1 khóa từ cha xuống
        left.keys.append(node.keys.pop(idx))
        left.pointers.append(node.pointers.pop(idx))
        
        # 2. Gom node phải vào node trái
        left.keys.extend(right.keys)
        left.pointers.extend(right.pointers)
        if not left.leaf:
            left.children.extend(right.children)
            
        # 3. Hủy node phải
        node.children.pop(idx + 1)
        
        # GIẢI MÃ TOÁN HỌC TẠI SAO KHÔNG BAO GIỜ VƯỢT QUÁ 2 KHÓA NỮA:
        # Hàm merge này CHỈ ĐƯỢC GỌI khi left (hoặc right) có 0 khóa. Sibling có 1 khóa.
        # Tổng sau khi gom: 0 (Node đói) + 1 (Từ cha) + 1 (Từ anh em) = 2 Khóa.
        # Số lượng 2 khóa là hoàn hảo cho Bậc 3, không bao giờ bị nổ!

    def _get_max(self, node):
        """Tìm Predecessor (node trước lớn nhất)"""
        while not node.leaf:
            node = node.children[-1]
        return node.keys[-1], node.pointers[-1]

    def _get_min(self, node):
        """Tìm Successor (node kế nhiệm nhỏ nhất)"""
        while not node.leaf:
            node = node.children[0]
        return node.keys[0], node.pointers[0]