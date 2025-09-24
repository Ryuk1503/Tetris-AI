import tkinter as tk
from PIL import Image, ImageTk

import random

class tetrisUI:
    def reset_game(self):
        # Xóa toàn bộ canvas
        self.canvas.delete("all")
        self.next_canvas.delete("all")
        self.ai_canvas.delete("all")
        # Reset điểm
        self.score_var.set(0)
        self.ai_score_var.set(0)
        # Tạo lại game logic cho player
        self.game = tetrisGame(self.canvas, self.next_canvas)
        self.game.score_var = self.score_var
        self.game.ui_ref = self
        # Tạo lại game logic cho AI
        self.ai_game = tetrisGame(self.ai_canvas, None)
        self.ai_game.ai_score_var = self.ai_score_var
        self.ai_game.ui_ref = self
        # Gán đối thủ cho nhau
        self.game.opponent = self.ai_game
        self.ai_game.opponent = self.game
        # Khởi tạo lại AI controller
        self.ai_controller = AIController(self.ai_game)
        def ai_spawn_block_and_play():
            tetrisGame.spawn_block(self.ai_game)
            self.ai_game.canvas.after(500, self.ai_controller.start)
        self.ai_game.spawn_block = ai_spawn_block_and_play
        # Đặt lại trạng thái
        self.game_running = False
        self.game_paused = False
        # Đặt lại nút
        self.start_button.config(text="START")
    def __init__(self, root):
        root.title("tetris Game")
        root.geometry("1000x700")
        # Khung chính chia làm 3 phần
        # Người chơi
        self.left_frame = tk.Frame(root, width=400, height=700, bg="#433C3C")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        # Điểm, next block,...
        self.middle_frame = tk.Frame(root, width=200, height=700, bg="#EBEBEB")
        self.middle_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        # AI
        self.right_frame = tk.Frame(root, width=400, height=700, bg="#433C3C")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)

        # Khởi tạo canvas màn hình chơi
        self.canvas = tk.Canvas(self.left_frame, width=400, height=700, bg="#433C3C", highlightthickness=0)
        self.canvas.pack()
        # Label "Next block" phía trên canvas khối tiếp theo
        self.next_label = tk.Label(self.middle_frame, text="Your next block", font=("Arial", 14, "bold"), bg="#EBEBEB")
        self.next_label.pack(pady=(30, 5))
        # Khởi tạo canvas khối tiếp theo
        self.next_canvas = tk.Canvas(self.middle_frame, width=130, height=130, bg="#EBEBEB", highlightthickness=2, highlightbackground="#333")
        self.next_canvas.pack(pady=(0, 20), padx=40)
        # Biến lưu điểm của cả 2
        self.score_var = tk.IntVar(value=0)
        self.ai_score_var = tk.IntVar(value=0)
        # Label "AI SCORE"
        self.ai_score_title = tk.Label(self.middle_frame, text="AI SCORE", font=("Arial", 14, "bold"), bg="#EBEBEB")
        self.ai_score_title.pack(pady=(0, 2))
        # Label hiển thị điểm của AI
        self.ai_score_label = tk.Label(self.middle_frame, textvariable=self.ai_score_var, font=("Arial", 18), bg="#EBEBEB")
        self.ai_score_label.pack(pady=(0, 20))
        # Label "YOUR SCORE" phía trên điểm
        self.score_title = tk.Label(self.middle_frame, text="YOUR SCORE", font=("Arial", 14, "bold"), bg="#EBEBEB")
        self.score_title.pack(pady=(0, 2))
        # Label hiển thị điểm của bạn
        self.score_label = tk.Label(self.middle_frame, textvariable=self.score_var, font=("Arial", 18), bg="#EBEBEB")
        self.score_label.pack(pady=(0, 10))

        # Thêm frame chứa nút START
        self.button_frame = tk.Frame(self.middle_frame, bg="#EBEBEB")
        self.button_frame.pack(pady=(0, 20))
        self.start_button = tk.Button(self.button_frame, text="START", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", command=self.start_game, width=15)
        self.start_button.pack(pady=5)
        
        # Khởi tạo game logic
        self.game = tetrisGame(self.canvas, self.next_canvas)
        self.game.score_var = self.score_var
        self.game.ui_ref = self  # Tham chiếu tới UI
        self.game_running = False
        self.game_paused = False

        # Khởi tạo khu vực chơi của AI
        self.ai_canvas = tk.Canvas(self.right_frame, width=400, height=700, bg="#433C3C", highlightthickness=0)
        self.ai_canvas.pack()
        self.ai_game = tetrisGame(self.ai_canvas, None)
        self.ai_game.ai_score_var = self.ai_score_var
        self.ai_game.ui_ref = self  # Tham chiếu tới UI
        # Gán đối thủ cho nhau
        self.game.opponent = self.ai_game
        self.ai_game.opponent = self.game

        # Khởi tạo AI controller cho tetrisGame AI
        self.ai_controller = AIController(self.ai_game)
        # Override spawn_block để AI tự động điều khiển mỗi lần spawn block
        def ai_spawn_block_and_play():
            tetrisGame.spawn_block(self.ai_game)
            self.ai_game.canvas.after(500, self.ai_controller.start)
        self.ai_game.spawn_block = ai_spawn_block_and_play

        # Bind phím điều khiển
        root.bind('<a>', lambda e: self.game.move_left())
        root.bind('<A>', lambda e: self.game.move_left())
        root.bind('<d>', lambda e: self.game.move_right())
        root.bind('<D>', lambda e: self.game.move_right())
        root.bind('<KeyPress-s>', lambda e: self.game.set_fast(True))
        root.bind('<KeyPress-S>', lambda e: self.game.set_fast(True))
        root.bind('<KeyRelease-s>', lambda e: self.game.set_fast(False))
        root.bind('<KeyRelease-S>', lambda e: self.game.set_fast(False))
        root.bind('<space>', lambda e: self.game.rotate_block())

        # Game sẽ chỉ bắt đầu khi nhấn START

    def update_start_button_restart(self):
        self.start_button.config(state="normal", text="RESTART")

    def start_game(self):
        # Nếu đang ở trạng thái game over (nút là RESTART), reset lại toàn bộ game
        if self.start_button.cget("text") == "RESTART":
            self.reset_game()
        if not self.game_running:
            self.game_running = True
            self.game_paused = False
            self.game.spawn_block()
            self.game.fall()
            self.ai_game.spawn_block()
            self.ai_game.fall()
            self.start_button.config(state="disabled")
class tetrisGame:
    def add_garbage_row(self):
    # Tạo một hàng cản với 1 ô random trống
        empty_idx = random.randint(0, tetrisGame.BOARD_WIDTH - 1)
        garbage_row = ["gray" if x != empty_idx else None for x in range(tetrisGame.BOARD_WIDTH)]
        # Đẩy các khối hiện tại lên trên 1 hàng
        self.board.pop(0)
        self.board.append(garbage_row)
        self.draw_block()

    def check_and_clear_lines(self, opponent=None):
        full_rows = [y for y in range(tetrisGame.BOARD_HEIGHT) if all(self.board[y][x] for x in range(tetrisGame.BOARD_WIDTH))]
        if not full_rows:
            return
        def blink(times=0):
            for y in full_rows:
                for x in range(tetrisGame.BOARD_WIDTH):
                    px = x * tetrisGame.BLOCK_SIZE
                    py = y * tetrisGame.BLOCK_SIZE
                    color = "white" if times % 2 == 0 else self.board[y][x]
                    self.canvas.create_rectangle(px, py, px + tetrisGame.BLOCK_SIZE, py + tetrisGame.BLOCK_SIZE, fill=color, outline="black", width=4, tags="blink")
            if times < 3:
                self.canvas.after(120, lambda: blink(times + 1))
            else:
                # Xóa hàng
                for y in full_rows:
                    del self.board[y]
                    self.board.insert(0, [None for _ in range(tetrisGame.BOARD_WIDTH)])
                self.canvas.delete("blink")
                self.draw_block()
                # Cộng điểm
                if self.score_var:
                    self.score_var.set(self.score_var.get() + len(full_rows))
                    # Nếu có đối thủ, thêm hàng cản cho đối thủ
                    if opponent:
                        for _ in range(len(full_rows)):
                            opponent.add_garbage_row()
                if self.ai_score_var:
                    self.ai_score_var.set(self.ai_score_var.get() + len(full_rows))
                    if opponent:
                        for _ in range(len(full_rows)):
                            opponent.add_garbage_row()
        blink()

    # Xoay khối theo chiều kim đồng hồ nếu không va chạm
    def rotate_block(self):
        # Chỉ xoay các khối không phải hình vuông
        if self.current_block == tetrisGame.BLOCKS[0][0]:
            return
        rotated = [(dy, -dx) for dx, dy in self.current_block]
        px, py = self.current_pos
        # Tìm offset để đẩy khối vào trong nếu va chạm thành hoặc khối khác
        min_x = min(px + dx for dx, dy in rotated)
        max_x = max(px + dx for dx, dy in rotated)
        offset = 0
        if min_x < 0:
            offset = -min_x
        elif max_x >= tetrisGame.BOARD_WIDTH:
            offset = tetrisGame.BOARD_WIDTH - 1 - max_x
        # Kiểm tra va chạm với các khối khác
        can_fit = True
        for dx, dy in rotated:
            nx = px + dx + offset
            ny = py + dy
            if ny < 0 or ny >= tetrisGame.BOARD_HEIGHT or nx < 0 or nx >= tetrisGame.BOARD_WIDTH:
                can_fit = False
                break
            if self.board[ny][nx]:
                can_fit = False
                break
        # Nếu không fit được, thử dịch sang trái/phải tối đa 2 ô để fit
        if not can_fit:
            for try_offset in [-2, -1, 1, 2]:
                fit = True
                for dx, dy in rotated:
                    nx = px + dx + offset + try_offset
                    ny = py + dy
                    if ny < 0 or ny >= tetrisGame.BOARD_HEIGHT or nx < 0 or nx >= tetrisGame.BOARD_WIDTH:
                        fit = False
                        break
                    if self.board[ny][nx]:
                        fit = False
                        break
                if fit:
                    offset += try_offset
                    can_fit = True
                    break
        if can_fit:
            self.current_block = rotated
            self.current_pos[0] += offset
            self.draw_block()

    # Thiết lập trạng thái rơi nhanh (giữ S)
    def set_fast(self, fast):
        self.fast = fast

    # Di chuyển khối sang trái nếu không va chạm
    def move_left(self):
        px, py = self.current_pos
        for dx, dy in self.current_block:
            nx = px + dx - 1
            ny = py + dy
            if nx < 0 or (self.board[ny][nx] if 0 <= ny < tetrisGame.BOARD_HEIGHT else False):
                return
        self.current_pos[0] -= 1
        self.draw_block()
    # Di chuyển khối sang phải nếu không va chạm
    def move_right(self):
        px, py = self.current_pos
        for dx, dy in self.current_block:
            nx = px + dx + 1
            ny = py + dy
            if nx >= tetrisGame.BOARD_WIDTH or (self.board[ny][nx] if 0 <= ny < tetrisGame.BOARD_HEIGHT and 0 <= nx < tetrisGame.BOARD_WIDTH else False):
                return
        self.current_pos[0] += 1
        self.draw_block()

    BLOCK_SIZE = 30
    BOARD_WIDTH = 400 // 30
    BOARD_HEIGHT = 700 // 30

    # Định nghĩa các khối
    BLOCKS = [
        # Square
        [[(0,0),(1,0),(0,1),(1,1)]],
        # I
        [[(0,0),(0,1),(0,2),(0,3)]],
        # Z
        [[(0,0),(1,0),(1,1),(2,1)]],
        # S
        [[(1,0),(2,0),(0,1),(1,1)]],
        # L
        [[(0,0),(0,1),(0,2),(1,2)]],
        # J
        [[(1,0),(1,1),(1,2),(0,2)]],
        # T
        [[(1,0),(0,1),(1,1),(2,1)]]
    ]

    COLORS = ["yellow", "cyan", "red", "green", "orange", "blue", "purple"]

    # Khởi tạo game, tạo board lưu trạng thái các ô
    def __init__(self, canvas, next_canvas):
        self.fast = False
        self.canvas = canvas
        self.next_canvas = next_canvas
        self.current_block = None
        self.current_pos = None
        self.current_color = None
        self.next_block = None
        self.next_color = None
        self.score_var = None  # Chỉ dùng cho người chơi
        self.ai_score_var = None  # Chỉ dùng cho AI
        self.is_game_over_flag = False  # Cờ game over chung
        # Khởi tạo board rỗng
        self.board = [[None for _ in range(tetrisGame.BOARD_WIDTH)] for _ in range(tetrisGame.BOARD_HEIGHT)]

    # Kiểm tra có khối nào chạm đỉnh không
    def is_game_over(self):
        if self.is_game_over_flag:
            return True
        for x in range(tetrisGame.BOARD_WIDTH):
            if self.board[0][x]:
                # Hiện cửa sổ thông báo
                msg = "GAME OVER" if self.score_var else "YOU WIN"
                win = tk.Toplevel(self.canvas)
                win.title("Thông báo")
                win.geometry("300x120")
                label = tk.Label(win, text=msg, font=("Arial", 24, "bold"))
                label.pack(pady=20)
                if self.score_var:
                    self.score_var.set(0)
                elif self.ai_score_var:
                    self.ai_score_var.set(0)
                self.is_game_over_flag = True
                # Đồng bộ cờ với đối thủ nếu có
                if hasattr(self, 'opponent') and self.opponent:
                    self.opponent.is_game_over_flag = True
                # Enable nút Start và đổi thành Restart nếu có ui_ref
                if hasattr(self, 'ui_ref') and self.ui_ref:
                    self.ui_ref.update_start_button_restart()
                return True
        return False

    # Sinh khối mới, chọn ngẫu nhiên và đặt ở giữa đỉnh
    def spawn_block(self):
        if self.is_game_over_flag:
            return
        if self.is_game_over():
            return
        self.fast = False  # Reset tốc độ về bình thường khi spawn block mới
        # Nếu đã có khối tiếp theo thì dùng, chưa có thì random
        if self.next_block is None:
            idx = random.randint(0, len(tetrisGame.BLOCKS)-1)
            self.next_block = tetrisGame.BLOCKS[idx][0]
            self.next_color = tetrisGame.COLORS[idx]
        self.current_block = self.next_block
        self.current_color = self.next_color
        start_x = tetrisGame.BOARD_WIDTH // 2 - 2
        start_y = 0
        self.current_pos = [start_x, start_y]
        # Random khối tiếp theo
        idx = random.randint(0, len(tetrisGame.BLOCKS)-1)
        self.next_block = tetrisGame.BLOCKS[idx][0]
        self.next_color = tetrisGame.COLORS[idx]
        self.draw_block()
        if self.next_canvas:
            self.draw_next_block()

    def draw_next_block(self):
        if not self.next_canvas:
            return
        self.next_canvas.delete("all")
        block = self.next_block
        color = self.next_color
        # Căn giữa khối trong canvas nhỏ
        min_x = min(dx for dx, dy in block)
        min_y = min(dy for dx, dy in block)
        max_x = max(dx for dx, dy in block)
        max_y = max(dy for dx, dy in block)
        block_size = tetrisGame.BLOCK_SIZE
        offset_x = (130 - (max_x - min_x + 1) * block_size) // 2
        offset_y = (130 - (max_y - min_y + 1) * block_size) // 2
        for dx, dy in block:
            x = offset_x + (dx - min_x) * block_size
            y = offset_y + (dy - min_y) * block_size
            self.next_canvas.create_rectangle(
                x, y, x + block_size, y + block_size,
                fill=color, outline="black", width=3
            )

    # Vẽ lại toàn bộ board và khối hiện tại lên canvas
    def draw_block(self):
        self.canvas.delete("block")
        # Vẽ các khối đã nằm dưới
        for y in range(tetrisGame.BOARD_HEIGHT):
            for x in range(tetrisGame.BOARD_WIDTH):
                color = self.board[y][x]
                if color:
                    px = x * tetrisGame.BLOCK_SIZE
                    py = y * tetrisGame.BLOCK_SIZE
                    self.canvas.create_rectangle(
                        px, py, px + tetrisGame.BLOCK_SIZE, py + tetrisGame.BLOCK_SIZE,
                        fill=color, outline="black", width=4, tags="block"
                    )
        # Vẽ khối hiện tại
        px, py = self.current_pos
        for dx, dy in self.current_block:
            x = (px + dx) * tetrisGame.BLOCK_SIZE
            y = (py + dy) * tetrisGame.BLOCK_SIZE
            self.canvas.create_rectangle(
                x, y, x + tetrisGame.BLOCK_SIZE, y + tetrisGame.BLOCK_SIZE,
                fill=self.current_color, outline="black", width=4, tags="block"
            )

    # Kiểm tra khối hiện tại có thể rơi xuống tiếp không (va chạm đáy hoặc khối khác)
    def can_move_down(self):
        px, py = self.current_pos
        for dx, dy in self.current_block:
            nx = px + dx
            ny = py + dy + 1
            # Va chạm đáy
            if ny >= tetrisGame.BOARD_HEIGHT:
                return False
            # Va chạm khối đã nằm dưới
            if self.board[ny][nx]:
                return False
        return True

    # Khóa khối hiện tại vào board (khi không thể rơi tiếp)
    def lock_block(self):
        px, py = self.current_pos
        for dx, dy in self.current_block:
            nx = px + dx
            ny = py + dy
            if 0 <= nx < tetrisGame.BOARD_WIDTH and 0 <= ny < tetrisGame.BOARD_HEIGHT:
                self.board[ny][nx] = self.current_color

    # Di chuyển khối xuống, xử lý va chạm và sinh khối mới khi cần
    def fall(self):
        if self.is_game_over_flag:
            return
        if self.is_game_over():
            return
        delay = 400 // 5 if getattr(self, 'fast', False) else 400
        if self.can_move_down():
            self.current_pos[1] += 1
            self.draw_block()
            self.canvas.after(delay, self.fall)
        else:
            # Khóa khối vào board
            self.lock_block()
            self.draw_block()
            # Truyền đối thủ vào hàm check_and_clear_lines
            if hasattr(self, 'opponent') and self.opponent:
                self.check_and_clear_lines(opponent=self.opponent)
            else:
                self.check_and_clear_lines()
            # Nếu game over thì không spawn block và không gọi fall nữa
            if self.is_game_over_flag:
                return
            if self.is_game_over():
                return
            self.spawn_block()
            self.fall()

class AIController:
    """
    AI heuristic cho Tetris: thử mọi vị trí và hướng xoay, chọn nước đi tốt nhất.
    Score = w1 x LinesCleared + w2 x Height + w3 x Holes + w4 x Bumpiness

    Nâng cấp: dùng Expectimax + Lookahead 1 khối tiếp theo.
    """
    def __init__(self, game):
        self.game = game
        self.running = False
        self.target_x = None
        self.target_rot = None

    def start(self):
        if self.game.is_game_over():
            return
        self.running = True
        self.plan_move()
        self.do_move()

    def plan_move(self):
        if self.game.is_game_over():
            return
        # Expectimax: thử mọi nước đi cho khối hiện tại, giả lập mọi khối tiếp theo
        best_score = None
        best_x = None
        best_rot = None
        block = self.game.current_block
        color = self.game.current_color
        board = [row[:] for row in self.game.board]
        px, py = self.game.current_pos
        # Tạo tất cả các hướng xoay
        rotations = [block]
        for _ in range(3):
            block = [(dy, -dx) for dx, dy in block]
            if block not in rotations:
                rotations.append(block)
        # Lấy danh sách khối tiếp theo
        next_blocks = self.game.BLOCKS
        next_colors = self.game.COLORS
        for rot_idx, rot in enumerate(rotations):
            min_x = min(dx for dx, dy in rot)
            max_x = max(dx for dx, dy in rot)
            for x in range(-min_x, self.game.BOARD_WIDTH - max_x):
                # Tìm vị trí y thấp nhất có thể đặt khối
                y = 0
                while True:
                    if not self.can_place(rot, x, y, board):
                        break
                    y += 1
                y -= 1
                if y < 0:
                    continue
                temp_board = [row[:] for row in board]
                for dx, dy in rot:
                    nx = x + dx
                    ny = y + dy
                    temp_board[ny][nx] = color
                # Lookahead: thử mọi khối tiếp theo, lấy điểm kỳ vọng
                expect_score = 0
                for nb_idx, nb in enumerate(next_blocks):
                    nb_rot = nb[0]
                    nc = next_colors[nb_idx]
                    # Thử mọi vị trí cho khối tiếp theo
                    nb_rotations = [nb_rot]
                    for _ in range(3):
                        nb_rot = [(dy, -dx) for dx, dy in nb_rot]
                        if nb_rot not in nb_rotations:
                            nb_rotations.append(nb_rot)
                    nb_best = None
                    for nb_rot2 in nb_rotations:
                        nb_min_x = min(dx for dx, dy in nb_rot2)
                        nb_max_x = max(dx for dx, dy in nb_rot2)
                        for nb_x in range(-nb_min_x, self.game.BOARD_WIDTH - nb_max_x):
                            nb_y = 0
                            while True:
                                if not self.can_place(nb_rot2, nb_x, nb_y, temp_board):
                                    break
                                nb_y += 1
                            nb_y -= 1
                            if nb_y < 0:
                                continue
                            temp_board2 = [row[:] for row in temp_board]
                            for dx2, dy2 in nb_rot2:
                                nx2 = nb_x + dx2
                                ny2 = nb_y + dy2
                                temp_board2[ny2][nx2] = nc
                            score2 = self.heuristic(temp_board2)
                            if nb_best is None or score2 > nb_best:
                                nb_best = score2
                    if nb_best is not None:
                        expect_score += nb_best
                # Trung bình kỳ vọng
                expect_score = expect_score / len(next_blocks)
                if best_score is None or expect_score > best_score:
                    best_score = expect_score
                    best_x = x
                    best_rot = rot_idx
        self.target_x = best_x
        self.target_rot = best_rot

    def can_place(self, block, px, py, board):
        for dx, dy in block:
            nx = px + dx
            ny = py + dy
            if nx < 0 or nx >= self.game.BOARD_WIDTH or ny < 0 or ny >= self.game.BOARD_HEIGHT:
                return False
            if board[ny][nx]:
                return False
        return True

    def heuristic(self, board):
        # Pierre Dellacherie weights
        w_lines = 0.76
        w_height = -0.51
        w_holes = -0.36
        w_bump = -0.18
        lines_cleared = self.count_lines(board)
        agg_height, bumpiness = self.get_heights_bump(board)
        holes = self.count_holes(board)
        score = (w_lines * lines_cleared + w_height * agg_height + w_holes * holes + w_bump * bumpiness)
        return score

    def count_lines(self, board):
        return sum(1 for row in board if all(row))

    def get_heights_bump(self, board):
        heights = []
        for x in range(self.game.BOARD_WIDTH):
            h = 0
            for y in range(self.game.BOARD_HEIGHT):
                if board[y][x]:
                    h = self.game.BOARD_HEIGHT - y
                    break
            heights.append(h)
        agg_height = sum(heights)
        bumpiness = sum(abs(heights[i] - heights[i+1]) for i in range(len(heights)-1))
        return agg_height, bumpiness

    def count_holes(self, board):
        holes = 0
        for x in range(self.game.BOARD_WIDTH):
            block_found = False
            for y in range(self.game.BOARD_HEIGHT):
                if board[y][x]:
                    block_found = True
                elif block_found:
                    holes += 1
        return holes

    def do_move(self):
        if self.game.is_game_over():
            return
        # Xoay khối về đúng hướng
        rot_count = 0
        block = self.game.current_block
        while rot_count < self.target_rot:
            self.game.rotate_block()
            rot_count += 1
        # Di chuyển sang trái/phải
        px, _ = self.game.current_pos
        while px < self.target_x:
            self.game.move_right()
            px += 1
        while px > self.target_x:
            self.game.move_left()
            px -= 1
        
        self.game.set_fast(True)

if __name__ == "__main__":
    root = tk.Tk()
    start = tetrisUI(root)
    root.mainloop()