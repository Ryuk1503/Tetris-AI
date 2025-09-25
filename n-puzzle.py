import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import random
from collections import deque


TILE_SIZE = 100

class NPuzzleGame:

    def __init__(self, root):
        self.root = root
        self.root.title("N-Puzzle Game")
        self.steps = 0
        self.tiles = []
        self.goal_tiles = []
        self.blank_pos = None
        self.image = None
        self.goal_image = None
        self.tile_map = {}
        self.rev_map = {}

        self.shuffle_history = []  # Lưu lịch sử xáo trộn
        self.current_id = 1        # ID cho mỗi đề xáo
        self.last_algo = ""        # Thuật toán đã dùng cho đề hiện tại

        self.rows = 3
        self.cols = 3

        # UI setup
        self.frame = tk.Frame(root)
        self.frame.pack()

        tk.Label(self.frame, text="Rows:").grid(row=0, column=0)
        self.row_entry = tk.Entry(self.frame, width=3)
        self.row_entry.insert(0, "3")
        self.row_entry.grid(row=0, column=1)
        tk.Label(self.frame, text="Cols:").grid(row=0, column=2)
        self.col_entry = tk.Entry(self.frame, width=3)
        self.col_entry.insert(0, "3")
        self.col_entry.grid(row=0, column=3)

        self.canvas = tk.Canvas(self.frame, width=self.cols*TILE_SIZE, height=self.rows*TILE_SIZE)
        self.canvas.grid(row=1, column=0, columnspan=4, rowspan=5)
        self.goal_canvas = tk.Canvas(self.frame, width=self.cols*40, height=self.rows*40)
        self.goal_canvas.grid(row=1, column=4, padx=20)


        self.btn_load = tk.Button(self.frame, text="Tải ảnh lên", command=self.load_image)
        self.btn_load.grid(row=2, column=4, sticky="ew")

        # Dropdown menu chọn thuật toán ngay bên trên nút tự động giải
        self.solver_var = tk.StringVar()
        self.solver_var.set("(Hãy lựa chọn thuật toán)")
        self.solver_menu = tk.OptionMenu(self.frame, self.solver_var, "BFS", "DFS", "Greedy", "A*", "UCS")
        self.solver_menu.grid(row=3, column=4, sticky="ew")

        self.btn_solve = tk.Button(self.frame, text="Tự động giải", command=self.auto_solve)
        self.btn_solve.grid(row=4, column=4, sticky="ew")
        self.btn_create = tk.Button(self.frame, text="Create", command=self.create)
        self.btn_create.grid(row=5, column=4, sticky="ew")

        self.btn_reset = tk.Button(self.frame, text="Reset", command=self.back_last_history)
        self.btn_reset.grid(row=6, column=4, sticky="ew")

        self.step_label = tk.Label(self.frame, text="Steps: 0")
        self.step_label.grid(row=7, column=4)

        self.btn_history = tk.Button(self.frame, text="Lịch sử", command=self.show_history, width=12)
        self.btn_history.grid(row=8, column=1, columnspan=2, sticky="ew", pady=10)

        self.canvas.bind("<Button-1>", self.on_click)

    def back_last_history(self):
        # Quay lại lịch sử gần nhất (trước đó), không tạo id mới
        if len(self.shuffle_history) < 1:
            messagebox.showinfo("Thông báo", "Không có lịch sử trước đó để quay lại!")
            return
        # Xóa lịch sử hiện tại và khôi phục lại trạng thái trước đó
        last = self.shuffle_history[-1]
        self.rows = int(self.row_entry.get())
        self.cols = int(self.col_entry.get())
        if self.image:
            self.image = self.image.resize((self.cols*TILE_SIZE, self.rows*TILE_SIZE), Image.LANCZOS)
            self.goal_image = self.image.copy().resize((self.cols*40, self.rows*40), Image.LANCZOS)
            self.goal_tiles = self.split_image(self.goal_image, 40)
            self.tiles = self.split_image(self.image, TILE_SIZE)
            idx = 0
            for i in range(self.rows):
                for j in range(self.cols):
                    val = last["state"][idx]
                    if val == 0:
                        self.tiles[i][j] = None
                        self.blank_pos = (i, j)
                    else:
                        self.tiles[i][j] = self.tile_map[val]
                    idx += 1
            self.steps = 0
            self.update_ui()

    def load_image(self):
        try:
            self.rows = int(self.row_entry.get())
            self.cols = int(self.col_entry.get())
            if self.rows < 2 or self.cols < 2 or self.rows > 5 or self.cols > 5:
                raise ValueError
        except Exception:
            messagebox.showerror("Lỗi", "Số hàng/cột phải >= 2 và <= 5")
            return
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg")])
        if not file_path:
            return
        # Resize ảnh đúng kích thước puzzle
        img = Image.open(file_path)
        img = img.resize((self.cols*TILE_SIZE, self.rows*TILE_SIZE), Image.LANCZOS)
        self.image = img
        self.goal_image = img.copy().resize((self.cols*40, self.rows*40), Image.LANCZOS)
        self.goal_tiles = self.split_image(self.goal_image, 40)
        self.tiles = self.split_image(self.image, TILE_SIZE)
        self.blank_pos = (self.rows-1, self.cols-1)
        self.steps = 0
        self.update_ui()

    def split_image(self, img, size):
        tiles = []
        tile_id = 1
        for i in range(self.rows):
            row = []
            for j in range(self.cols):
                left = j*size
                top = i*size
                tile = img.crop((left, top, left+size, top+size))
                if i == self.rows-1 and j == self.cols-1:
                    row.append(None)  # blank
                else:
                    photo = ImageTk.PhotoImage(tile)
                    row.append(photo)
                    self.tile_map[tile_id] = photo
                    self.rev_map[photo] = tile_id
                    tile_id += 1
            tiles.append(row)
        return tiles

    def shuffle_tiles(self):
        # Tạo danh sách các mảnh (bao gồm None cho ô trống)
        flat_tiles = []
        for i in range(self.rows):
            for j in range(self.cols):
                flat_tiles.append(self.tiles[i][j])
        while True:
            random.shuffle(flat_tiles)
            # Chuyển về dạng ma trận
            idx = 0
            for i in range(self.rows):
                for j in range(self.cols):
                    self.tiles[i][j] = flat_tiles[idx]
                    if flat_tiles[idx] is None:
                        self.blank_pos = (i, j)
                    idx += 1
            # Đảm bảo trạng thái sinh ra là khả giải
            if self.is_solvable():
                break

    def is_solvable(self):
        # Chuyển trạng thái hiện tại thành mảng 1D
        arr = []
        blank_row = None
        for i in range(self.rows):
            for j in range(self.cols):
                if self.tiles[i][j] is None:
                    blank_row = i  # hàng của ô trống (từ trên xuống)
                    arr.append(0)
                else:
                    arr.append(self.rev_map[self.tiles[i][j]])
        # Đếm số nghịch thế
        inv = 0
        arr_no_blank = [x for x in arr if x != 0]
        for i in range(len(arr_no_blank)):
            for j in range(i+1, len(arr_no_blank)):
                if arr_no_blank[i] > arr_no_blank[j]:
                    inv += 1
        # Quy tắc khả giải:
        if self.cols % 2 == 1:
            return inv % 2 == 0
        else:
            # Nếu số cột chẵn, kiểm tra vị trí hàng ô trống (từ dưới lên)
            blank_from_bottom = self.rows - blank_row
            return (inv + blank_from_bottom) % 2 == 0

    def update_ui(self):
        self.canvas.config(width=self.cols*TILE_SIZE, height=self.rows*TILE_SIZE)
        self.goal_canvas.config(width=self.cols*40, height=self.rows*40)
        self.canvas.delete("all")
        for i in range(self.rows):
            for j in range(self.cols):
                x, y = j*TILE_SIZE, i*TILE_SIZE
                if self.tiles[i][j]:
                    self.canvas.create_image(x, y, anchor="nw", image=self.tiles[i][j])
                else:
                    self.canvas.create_rectangle(x, y, x+TILE_SIZE, y+TILE_SIZE, fill="white")
        self.goal_canvas.delete("all")
        for i in range(self.rows):
            for j in range(self.cols):
                x, y = j*40, i*40
                if self.goal_tiles[i][j]:
                    self.goal_canvas.create_image(x, y, anchor="nw", image=self.goal_tiles[i][j])
        self.step_label.config(text=f"Steps: {self.steps}")

    def on_click(self, event):
        i, j = event.y // TILE_SIZE, event.x // TILE_SIZE
        if 0 <= i < self.rows and 0 <= j < self.cols and self.can_move(i, j):
            self.move_tile(i, j)
            self.steps += 1
            self.update_ui()
            if self.check_win():
                messagebox.showinfo("Chúc mừng!", "Bạn đã giải xong puzzle!")

    def can_move(self, i, j):
        bi, bj = self.blank_pos
        return (abs(bi-i) == 1 and bj == j) or (abs(bj-j) == 1 and bi == i)

    def move_tile(self, i, j):
        bi, bj = self.blank_pos
        self.tiles[bi][bj], self.tiles[i][j] = self.tiles[i][j], self.tiles[bi][bj]
        self.blank_pos = (i, j)

    def check_win(self):
        goal = self.get_goal_state()
        return self.get_state() == goal

    def create(self):
        try:
            self.rows = int(self.row_entry.get())
            self.cols = int(self.col_entry.get())
            if self.rows < 2 or self.cols < 2 or self.rows > 5 or self.cols > 5:
                raise ValueError
        except Exception:
            messagebox.showerror("Lỗi", "Số hàng/cột phải >= 2 và <= 5")
            return
        if self.image:
            # Resize lại ảnh nếu thay đổi kích thước
            self.image = self.image.resize((self.cols*TILE_SIZE, self.rows*TILE_SIZE), Image.LANCZOS)
            self.goal_image = self.image.copy().resize((self.cols*40, self.rows*40), Image.LANCZOS)
            self.goal_tiles = self.split_image(self.goal_image, 40)
            self.tiles = self.split_image(self.image, TILE_SIZE)
            algo = self.solver_var.get()
            while True:
                flat_tiles = []
                for i in range(self.rows):
                    for j in range(self.cols):
                        flat_tiles.append(self.tiles[i][j])
                random.shuffle(flat_tiles)
                idx = 0
                for i in range(self.rows):
                    for j in range(self.cols):
                        self.tiles[i][j] = flat_tiles[idx]
                        if flat_tiles[idx] is None:
                            self.blank_pos = (i, j)
                        idx += 1
                if self.is_solvable():
                    break
            self.steps = 0
            self.update_ui()

            # Lưu lịch sử xáo trộn: luôn tạo lịch sử mới với id mới
            state = self.get_state()
            history_item = {
                "id": self.current_id,
                "state": state,
                "algo": "",  # Thuật toán chưa dùng
                "steps": None,
                "generated": None,
                "visited": None,
                "time": None
            }
            self.shuffle_history.append(history_item)
            self.current_id += 1
            self.last_algo = ""

# ============================================ #
    def get_state(self):
        """Trả về trạng thái hiện tại dạng tuple 1D"""
        state = []
        for i in range(self.rows):
            for j in range(self.cols):
                if self.tiles[i][j] is None:
                    state.append(0)
                else:
                    state.append(self.rev_map[self.tiles[i][j]])
        return tuple(state)

    def get_goal_state(self):
        """Trạng thái đích"""
        state = []
        for i in range(self.rows):
            for j in range(self.cols):
                if i == self.rows-1 and j == self.cols-1:
                    state.append(0)
                else:
                    state.append(i*self.cols + j + 1)
        return tuple(state)

    def bfs_solve(self, start, goal, max_steps=1000000):
        import time
        from collections import deque
        moves = [(-1,0,'U'), (1,0,'D'), (0,-1,'L'), (0,1,'R')]
        blank = start.index(0)
        queue = deque()
        queue.append((start, [], blank))
        visited = set()
        visited.add(start)
        steps = 0
        generated = 1
        visited_count = 0
        t0 = time.perf_counter()
        while queue:
            state, path, blank = queue.popleft()
            visited_count += 1
            if state == goal:
                t1 = time.perf_counter()
                self.last_time = round(t1-t0, 4)
                self.last_generated = generated
                self.last_visited = visited_count
                return path
            if steps > max_steps:
                break
            steps += 1
            bi, bj = divmod(blank, self.cols)
            for di, dj, move in moves:
                ni, nj = bi+di, bj+dj
                if 0 <= ni < self.rows and 0 <= nj < self.cols:
                    new_blank = ni*self.cols + nj
                    new_state = list(state)
                    new_state[blank], new_state[new_blank] = new_state[new_blank], new_state[blank]
                    new_state_tuple = tuple(new_state)
                    if new_state_tuple not in visited:
                        visited.add(new_state_tuple)
                        queue.append((new_state_tuple, path+[move], new_blank))
                        generated += 1
        t1 = time.perf_counter()
        self.last_time = round(t1-t0, 4)
        self.last_generated = generated
        self.last_visited = visited_count
        return None
    
    def dfs_solve(self, start, goal, max_depth=100000):
        import time
        moves = [(-1,0,'U'), (1,0,'D'), (0,-1,'L'), (0,1,'R')]
        stack = [(start, [], start.index(0), 0)]
        visited = set()
        visited.add(start)
        steps = 0
        max_steps = 200000  # Giới hạn số bước duyệt
        generated = 1
        visited_count = 0
        t0 = time.perf_counter()
        while stack:
            state, path, blank, depth = stack.pop()
            visited_count += 1
            steps += 1
            if steps > max_steps:
                break
            if state == goal:
                t1 = time.perf_counter()
                self.last_time = round(t1-t0, 4)
                self.last_generated = generated
                self.last_visited = visited_count
                return path
            if depth > max_depth:
                continue
            bi, bj = divmod(blank, self.cols)
            for di, dj, move in moves:
                ni, nj = bi+di, bj+dj
                if 0 <= ni < self.rows and 0 <= nj < self.cols:
                    new_blank = ni*self.cols + nj
                    new_state = list(state)
                    new_state[blank], new_state[new_blank] = new_state[new_blank], new_state[blank]
                    new_state_tuple = tuple(new_state)
                    if new_state_tuple not in visited:
                        visited.add(new_state_tuple)
                        stack.append((new_state_tuple, path+[move], new_blank, depth+1))
                        generated += 1
        t1 = time.perf_counter()
        self.last_time = round(t1-t0, 4)
        self.last_generated = generated
        self.last_visited = visited_count
        return None
    
    def greedy_solve(self, start, goal):
        import time
        import heapq
        moves = [(-1,0,'U'), (1,0,'D'), (0,-1,'L'), (0,1,'R')]
        def manhattan(state):
            dist = 0
            for idx, val in enumerate(state):
                if val == 0:
                    continue
                goal_idx = goal.index(val)
                x1, y1 = divmod(idx, self.cols)
                x2, y2 = divmod(goal_idx, self.cols)
                dist += abs(x1-x2) + abs(y1-y2)
            return dist

        heap = []
        blank = start.index(0)
        heapq.heappush(heap, (manhattan(start), start, [], blank))
        visited = set()
        visited.add(start)
        generated = 1
        visited_count = 0
        t0 = time.perf_counter()
        while heap:
            _, state, path, blank = heapq.heappop(heap)
            visited_count += 1
            if state == goal:
                t1 = time.perf_counter()
                self.last_time = round(t1-t0, 4)
                self.last_generated = generated
                self.last_visited = visited_count
                return path
            bi, bj = divmod(blank, self.cols)
            for di, dj, move in moves:
                ni, nj = bi+di, bj+dj
                if 0 <= ni < self.rows and 0 <= nj < self.cols:
                    new_blank = ni*self.cols + nj
                    new_state = list(state)
                    new_state[blank], new_state[new_blank] = new_state[new_blank], new_state[blank]
                    new_state_tuple = tuple(new_state)
                    if new_state_tuple not in visited:
                        visited.add(new_state_tuple)
                        heapq.heappush(heap, (manhattan(new_state_tuple), new_state_tuple, path+[move], new_blank))
                        generated += 1
        t1 = time.perf_counter()
        self.last_time = round(t1-t0, 4)
        self.last_generated = generated
        self.last_visited = visited_count
        return None
    
    def Astar_solve(self, start, goal):
        import time
        import heapq
        moves = [(-1,0,'U'), (1,0,'D'), (0,-1,'L'), (0,1,'R')]
        def manhattan(state):
            dist = 0
            for idx, val in enumerate(state):
                if val == 0:
                    continue
                goal_idx = goal.index(val)
                x1, y1 = divmod(idx, self.cols)
                x2, y2 = divmod(goal_idx, self.cols)
                dist += abs(x1-x2) + abs(y1-y2)
            return dist
        heap = []
        blank = start.index(0)
        heapq.heappush(heap, (manhattan(start), 0, start, [], blank))  # (f, g, state, path, blank)
        visited = {}
        visited[start] = 0
        generated = 1
        visited_count = 0
        t0 = time.perf_counter()
        while heap:
            f, g, state, path, blank = heapq.heappop(heap)
            visited_count += 1
            if state == goal:
                t1 = time.perf_counter()
                self.last_time = round(t1-t0, 4)
                self.last_generated = generated
                self.last_visited = visited_count
                return path
            bi, bj = divmod(blank, self.cols)
            for di, dj, move in moves:
                ni, nj = bi+di, bj+dj
                if 0 <= ni < self.rows and 0 <= nj < self.cols:
                    new_blank = ni*self.cols + nj
                    new_state = list(state)
                    new_state[blank], new_state[new_blank] = new_state[new_blank], new_state[blank]
                    new_state_tuple = tuple(new_state)
                    new_g = g + 1
                    if new_state_tuple not in visited or new_g < visited[new_state_tuple]:
                        visited[new_state_tuple] = new_g
                        f_new = new_g + manhattan(new_state_tuple)
                        heapq.heappush(heap, (f_new, new_g, new_state_tuple, path+[move], new_blank))
                        generated += 1
        t1 = time.perf_counter()
        self.last_time = round(t1-t0, 4)
        self.last_generated = generated
        self.last_visited = visited_count
        return None
    
    def UCS_solve(self, start, goal):
        import time
        import heapq
        moves = [(-1,0,'U'), (1,0,'D'), (0,-1,'L'), (0,1,'R')]
        heap = []
        blank = start.index(0)
        heapq.heappush(heap, (0, start, [], blank))  # (cost, state, path, blank)
        visited = {}
        visited[start] = 0
        generated = 1
        visited_count = 0
        t0 = time.perf_counter()
        while heap:
            cost, state, path, blank = heapq.heappop(heap)
            visited_count += 1
            if state == goal:
                t1 = time.perf_counter()
                self.last_time = round(t1-t0, 4)
                self.last_generated = generated
                self.last_visited = visited_count
                return path
            bi, bj = divmod(blank, self.cols)
            for di, dj, move in moves:
                ni, nj = bi+di, bj+dj
                if 0 <= ni < self.rows and 0 <= nj < self.cols:
                    new_blank = ni*self.cols + nj
                    new_state = list(state)
                    new_state[blank], new_state[new_blank] = new_state[new_blank], new_state[blank]
                    new_state_tuple = tuple(new_state)
                    new_cost = cost + 1
                    if new_state_tuple not in visited or new_cost < visited[new_state_tuple]:
                        visited[new_state_tuple] = new_cost
                        heapq.heappush(heap, (new_cost, new_state_tuple, path+[move], new_blank))
                        generated += 1
        t1 = time.perf_counter()
        self.last_time = round(t1-t0, 4)
        self.last_generated = generated
        self.last_visited = visited_count
        return None

    def auto_solve(self):
        if not self.image:
            return

        start = self.get_state()
        goal = self.get_goal_state()
        algo = self.solver_var.get()
        path = None
        if algo == "BFS":
            path = self.bfs_solve(start, goal, max_steps=1000000)
        if algo == "DFS":
            path = self.dfs_solve(start, goal, max_depth=100000)
        if algo == "Greedy":
            path = self.greedy_solve(start, goal)
        if algo == "A*":
            path = self.Astar_solve(start, goal)
        if algo == "UCS":
            path = self.UCS_solve(start, goal)
        # Có thể thêm các thuật toán khác ở đây
        if not path:
            messagebox.showerror("Lỗi", "Không tìm thấy lời giải với thuật toán đã chọn!")
            return

        # Tính tốc độ giải dựa vào số bước
        delay = 200
        if path:
            if len(path) > 100:
                delay = int(delay / 3)
            elif len(path) > 50:
                delay = int(delay / 2)
            elif len(path) > 25:
                delay = int(delay / 1.5)

        def do_step(idx=0):
            if idx >= len(path):
                return
            move = path[idx]
            bi, bj = self.blank_pos
            if move == 'U' and bi > 0:
                self.move_tile(bi-1, bj)
            elif move == 'D' and bi < self.rows-1:
                self.move_tile(bi+1, bj)
            elif move == 'L' and bj > 0:
                self.move_tile(bi, bj-1)
            elif move == 'R' and bj < self.cols-1:
                self.move_tile(bi, bj+1)
            self.steps += 1
            self.update_ui()
            self.root.after(delay, lambda: do_step(idx+1))

        do_step()

        # Lưu lịch sử giải đề theo logic mới
        found = False
        for item in reversed(self.shuffle_history):
            if item["state"] == start:
                if item["algo"] == "":
                    # Nếu chưa có thuật toán, cập nhật trực tiếp
                    item["algo"] = algo
                    item["steps"] = len(path) if path else None
                    item["generated"] = getattr(self, "last_generated", None)
                    item["visited"] = getattr(self, "last_visited", None)
                    item["time"] = getattr(self, "last_time", None)
                    found = True
                    break
                elif item["algo"] != algo:
                    # Nếu đã có thuật toán khác, tạo bản ghi mới với cùng id
                    history_item = {
                        "id": item["id"],
                        "state": start,
                        "algo": algo,
                        "steps": len(path) if path else None,
                        "generated": getattr(self, "last_generated", None),
                        "visited": getattr(self, "last_visited", None),
                        "time": getattr(self, "last_time", None)
                    }
                    self.shuffle_history.append(history_item)
                    found = True
                    break
        if not found:
            # Nếu chưa có đề này trong lịch sử, tạo mới với id mới
            history_item = {
                "id": self.current_id,
                "state": start,
                "algo": algo,
                "steps": len(path) if path else None,
                "generated": getattr(self, "last_generated", None),
                "visited": getattr(self, "last_visited", None),
                "time": getattr(self, "last_time", None)
            }
            self.shuffle_history.append(history_item)
            self.current_id += 1
        self.last_algo = algo
    def show_history(self):
        # Hiển thị lịch sử xáo trộn với thanh trượt và chiều ngang cố định
        win = tk.Toplevel(self.root)
        win.title("Lịch sử xáo trộn")
        win.geometry("505x350")

        frame = tk.Frame(win)
        frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(frame, width=505, height=350)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        table_frame = tk.Frame(canvas, width=600)
        canvas.create_window((0,0), window=table_frame, anchor="nw")

        # Header
        tk.Label(table_frame, text="ID", width=5, borderwidth=1, relief="solid").grid(row=0, column=0)
        tk.Label(table_frame, text="Thuật toán", width=12, borderwidth=1, relief="solid").grid(row=0, column=1)
        tk.Label(table_frame, text="Generated", width=10, borderwidth=1, relief="solid").grid(row=0, column=2)
        tk.Label(table_frame, text="Visited", width=10, borderwidth=1, relief="solid").grid(row=0, column=3)
        tk.Label(table_frame, text="Số bước", width=8, borderwidth=1, relief="solid").grid(row=0, column=4)
        tk.Label(table_frame, text="Time (s)", width=10, borderwidth=1, relief="solid").grid(row=0, column=5)
        tk.Label(table_frame, text="Khởi tạo", width=10, borderwidth=1, relief="solid").grid(row=0, column=6)

        for idx, item in enumerate(self.shuffle_history):
            tk.Label(table_frame, text=str(item["id"]), width=5, borderwidth=1, relief="solid").grid(row=idx+1, column=0)
            tk.Label(table_frame, text=str(item["algo"]), width=12, borderwidth=1, relief="solid").grid(row=idx+1, column=1)
            tk.Label(table_frame, text=str(item["generated"] if item.get("generated") is not None else ""), width=10, borderwidth=1, relief="solid").grid(row=idx+1, column=2)
            tk.Label(table_frame, text=str(item["visited"] if item.get("visited") is not None else ""), width=10, borderwidth=1, relief="solid").grid(row=idx+1, column=3)
            tk.Label(table_frame, text=str(item["steps"] if item["steps"] is not None else ""), width=8, borderwidth=1, relief="solid").grid(row=idx+1, column=4)
            tk.Label(table_frame, text=str(item["time"] if item.get("time") is not None else ""), width=10, borderwidth=1, relief="solid").grid(row=idx+1, column=5)
            btn = tk.Button(table_frame, text="Khởi tạo", command=lambda s=item["state"]: self.recreate_state(s, win))
            btn.grid(row=idx+1, column=6)

        # Update scrollregion after widgets are added
        table_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def recreate_state(self, state, win=None):
        # Tạo lại đề với trạng thái đã chọn
        self.rows = int(self.row_entry.get())
        self.cols = int(self.col_entry.get())
        if self.image:
            self.image = self.image.resize((self.cols*TILE_SIZE, self.rows*TILE_SIZE), Image.LANCZOS)
            self.goal_image = self.image.copy().resize((self.cols*40, self.rows*40), Image.LANCZOS)
            self.goal_tiles = self.split_image(self.goal_image, 40)
            self.tiles = self.split_image(self.image, TILE_SIZE)
            idx = 0
            for i in range(self.rows):
                for j in range(self.cols):
                    val = state[idx]
                    if val == 0:
                        self.tiles[i][j] = None
                        self.blank_pos = (i, j)
                    else:
                        self.tiles[i][j] = self.tile_map[val]
                    idx += 1
            self.steps = 0
            self.update_ui()
        if win:
            win.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    game = NPuzzleGame(root)
    root.mainloop()