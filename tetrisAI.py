import tkinter as tk
from PIL import Image, ImageTk
import time
import random

class tetrisUI:

    def __init__(self, root):
        root.title("Tetris Game")
        root.geometry("1111x700")
        # Người chơi
        self.left_frame = tk.Frame(root, width=400, height=700, bg="#433C3C")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        # Điểm, next block,... (thêm viền đỏ cho middle_frame)
        self.middle_frame = tk.Frame(root, width=200, height=700, bg="#EBEBEB", highlightbackground="#D33333", highlightthickness=6)
        self.middle_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        # AI
        self.right_frame = tk.Frame(root, width=400, height=700, bg="#433C3C")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)

        # Khởi tạo canvas màn hình chơi với kích thước đúng board
        self.canvas = tk.Canvas(
            self.left_frame,
            width=tetrisGame.BOARD_WIDTH * tetrisGame.BLOCK_SIZE,
            height=tetrisGame.BOARD_HEIGHT * tetrisGame.BLOCK_SIZE,
            bg="#433C3C", highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        # Label "Next block" phía trên canvas khối tiếp theo
        self.next_label = tk.Label(self.middle_frame, text="Your next block", font=("Kenney Future Narrow", 14, "bold"), bg="#EBEBEB")
        self.next_label.pack(pady=(30, 5))
        # Khởi tạo canvas khối tiếp theo
        self.next_canvas = tk.Canvas(self.middle_frame, width=130, height=130, bg="#EBEBEB", highlightthickness=2, highlightbackground="#D33333")
        self.next_canvas.pack(pady=(0, 20), padx=40)
        # Biến lưu điểm của cả 2
        self.score_var = tk.IntVar(value=0)
        self.ai_score_var = tk.IntVar(value=0)
        # Label "AI SCORE"
        self.ai_score_title = tk.Label(self.middle_frame, text="AI SCORE", font=("Kenney Future Narrow", 14, "bold"), bg="#EBEBEB")
        self.ai_score_title.pack(pady=(0, 2))
        # Label hiển thị điểm của AI
        self.ai_score_label = tk.Label(self.middle_frame, textvariable=self.ai_score_var, font=("Kenney Future Narrow", 18), bg="#EBEBEB")
        self.ai_score_label.pack(pady=(0, 20))
        # Label "YOUR SCORE" phía trên điểm
        self.score_title = tk.Label(self.middle_frame, text="YOUR SCORE", font=("Kenney Future Narrow", 14, "bold"), bg="#EBEBEB")
        self.score_title.pack(pady=(0, 2))
        # Label hiển thị điểm của bạn
        self.score_label = tk.Label(self.middle_frame, textvariable=self.score_var, font=("Kenney Future Narrow", 18), bg="#EBEBEB")
        self.score_label.pack(pady=(0, 10))
        # Credit
        self.credit_label = tk.Label(
            self.middle_frame,
            text="GROUP 11:\nNguyen Thanh Phuc - 23110140\nNguyen Le Huu Hoang - 23110099",
            font=("Kenney Future Narrow", 11),
            bg="#EBEBEB",
            fg="#333"
        )
        self.credit_label.pack(side=tk.BOTTOM, pady=(40, 8))

        # Đọc độ khó từ biến môi trường
        import os
        diff = os.environ.get("TETRIS_DIFFICULTY", "MEDIUM")
        self.difficulty_var = tk.StringVar(value=diff)

        # Âm thanh khi hover
        import pygame
        pygame.mixer.init()
        self.hover_sound = pygame.mixer.Sound(r"d:/STUDY/Trí tuệ nhân tạo/Audio/click4.ogg")


        # Khởi tạo biến thời gian chơi
        self.start_time = None

        # Khởi tạo game logic
        self.game = tetrisGame(self.canvas, self.next_canvas)
        self.game.score_var = self.score_var
        self.game.ui_ref = self  # Tham chiếu tới UI
        self.game_running = False  # Trạng thái đang chơi hay không
        self.game_paused = False

        # Khởi tạo khu vực chơi của AI với kích thước đúng board
        self.ai_canvas = tk.Canvas(
            self.right_frame,
            width=tetrisGame.BOARD_WIDTH * tetrisGame.BLOCK_SIZE,
            height=tetrisGame.BOARD_HEIGHT * tetrisGame.BLOCK_SIZE,
            bg="#433C3C", highlightthickness=0
        )
        self.ai_canvas.pack(fill=tk.BOTH, expand=True)
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
        # Tự động bắt đầu game khi khởi tạo UI
        self.start_game()

        # Bind phím điều khiển
        root = self.canvas.winfo_toplevel()
        root.bind('<a>', lambda e: self.game.move_left())
        root.bind('<A>', lambda e: self.game.move_left())
        root.bind('<d>', lambda e: self.game.move_right())
        root.bind('<D>', lambda e: self.game.move_right())
        root.bind('<KeyPress-s>', lambda e: self.game.set_fast(True))
        root.bind('<KeyRelease-s>', lambda e: self.game.set_fast(False))
        root.bind('<KeyPress-S>', lambda e: self.game.set_fast(True))
        root.bind('<KeyRelease-S>', lambda e: self.game.set_fast(False))
        # Nhấn SPACE để lập tức xuống
        def instant_drop_then_squash(event=None):
            self.game.instant_drop()
            self.squash_window()
        root.bind('<space>', instant_drop_then_squash)

    def squash_window(self):
        # Hiệu ứng cửa sổ chùng xuống
        root = self.canvas.winfo_toplevel()
        x = root.winfo_x()
        y = root.winfo_y()
        # Chùng xuống 10px
        root.geometry(f"1111x700+{x}+{y+10}")
        root.update()
        root.after(60)
        root.geometry(f"1111x700+{x}+{y}")
        root.bind('<w>', lambda e: self.game.rotate_block())

    def shake_window(self):
        # Hiệu ứng rung màn hình
        root = self.canvas.winfo_toplevel()
        x = root.winfo_x()
        y = root.winfo_y()
        import random
        for _ in range(10):
            dx = random.randint(-8, 8)
            dy = random.randint(-8, 8)
            root.geometry(f"1111x700+{x+dx}+{y+dy}")
            root.update()
            root.after(12)
        root.geometry(f"1111x700+{x}+{y}")

    def start_game(self):
        import time
        # Kiểm tra chọn độ khó
        if self.difficulty_var.get() == "(Chọn độ khó)":
            # Hiện popup ở giữa màn hình
            win = tk.Toplevel(self.button_frame)
            win.title("Thông báo")
            win.geometry("300x100")
            root = self.button_frame.winfo_toplevel()
            root.update_idletasks()
            root_x = root.winfo_x()
            root_y = root.winfo_y()
            root_w = root.winfo_width()
            root_h = root.winfo_height()
            popup_w, popup_h = 300, 100
            x = root_x + (root_w - popup_w) // 2
            y = root_y + (root_h - popup_h) // 2
            win.geometry(f"{popup_w}x{popup_h}+{x}+{y}")
            win.configure(bg="#f7f7f7")
            label = tk.Label(win, text="Bạn chưa chọn độ khó!", font=("Kenney Future Narrow", 18, "bold"), bg="#f7f7f7", fg="#C00")
            label.place(relx=0.5, rely=0.5, anchor="center")
            win.grab_set()
            return

        def countdown(n):
            if n > 0:
                lbl = tk.Label(self.middle_frame, text=str(n), font=("Kenney Future Narrow", 48, "bold"), fg="#D33333", bg="#EBEBEB")
                lbl.place(relx=0.51, rely=0.6, anchor="center")
                self.middle_frame.after(1000, lambda: [lbl.destroy(), countdown(n-1)])
            else:
                lbl = tk.Label(self.middle_frame, text="GO!", font=("Kenney Future Narrow", 48, "bold"), fg="#6EC6FF", bg="#EBEBEB")
                lbl.place(relx=0.55, rely=0.6, anchor="center")
                self.middle_frame.after(1000, lambda: [lbl.destroy(), self._start_game_real()])

        if not self.game_running:
            countdown(3)

    def _start_game_real(self):
        import time
        self.game_running = True
        self.game_paused = False
        self.start_time = time.time()
        self.game.spawn_block()
        self.game.fall()
        self.ai_game.spawn_block()
        self.ai_controller.start()
        self.ai_game.fall()
        
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

class tetrisGame:
    BLOCK_SIZE = 30
    BOARD_WIDTH = 400 // 30
    BOARD_HEIGHT = 700 // 30
    LOSE_LINE_Y = 2  # Hàng thứ 3 (y=2)

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
        self.next_next_block = None
        self.next_next_color = None
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
            if self.board[tetrisGame.LOSE_LINE_Y][x]:
                # Hiện cửa sổ thông báo
                # Đổi thông báo
                msg = "YOU LOSE" if self.score_var else "YOU WIN"
                win = tk.Toplevel(self.canvas)
                win.title("Thông báo")
                win.overrideredirect(True)  # Borderless window
                root = self.canvas.winfo_toplevel()
                root.update_idletasks()
                root_x = root.winfo_x()
                root_y = root.winfo_y()
                root_w = root.winfo_width()
                root_h = root.winfo_height()
                popup_w, popup_h = 370, 320
                x = root_x + (root_w - popup_w) // 2 + 10
                y = root_y + (root_h - popup_h) // 2
                win.geometry(f"{popup_w}x{popup_h}+{x}+{y}")
                # Frame viền đỏ
                border_frame = tk.Frame(win, bg="#D33333", width=popup_w, height=popup_h)
                border_frame.pack(fill=tk.BOTH, expand=True)
                inner = tk.Frame(border_frame, bg="#f7f7f7", width=popup_w-12, height=popup_h-12)
                inner.place(x=6, y=6, width=popup_w-12, height=popup_h-12)
                # Lấy điểm và thời gian
                player_score = 0
                ai_score = 0
                play_time = "--"
                if hasattr(self, 'ui_ref') and self.ui_ref:
                    player_score = self.ui_ref.score_var.get()
                    ai_score = self.ui_ref.ai_score_var.get()
                    import time
                    if getattr(self.ui_ref, 'start_time', None):
                        elapsed = int(time.time() - self.ui_ref.start_time)
                        m, s = divmod(elapsed, 60)
                        if m == 0:
                            play_time = f"{s} s"
                        else:
                            play_time = f"{m} m {s} s"
                # Hiển thị thông tin
                color = "#D33333" if msg == "YOU LOSE" else "#6EC6FF"
                label = tk.Label(inner, text=msg, font=("Kenney Future Narrow", 24, "bold"), fg=color, bg="#f7f7f7")
                label.pack(pady=(18, 8))
                label1 = tk.Label(inner, text=f"Your Score: {player_score}", font=("Kenney Future Narrow", 15), bg="#f7f7f7")
                label1.pack(pady=2)
                label2 = tk.Label(inner, text=f"AI Score: {ai_score}", font=("Kenney Future Narrow", 15), bg="#f7f7f7")
                label2.pack(pady=2)
                label3 = tk.Label(inner, text=f"Play Time: {play_time}", font=("Kenney Future Narrow", 15), bg="#f7f7f7")
                label3.pack(pady=2)
                # Buttons
                def restart():
                    win.destroy()
                    if hasattr(self, 'ui_ref'):
                        self.ui_ref.reset_game()
                        self.ui_ref.start_game()
                def main_menu():
                    win.destroy()
                    import subprocess, sys, os
                    subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "start_screen.py")])
                    root = self.canvas.winfo_toplevel()
                    root.destroy()
                btn_restart = tk.Button(inner, text="RESTART", font=("Kenney Future Narrow", 14, "bold"), bg="#6EC6FF", fg="white", command=restart, relief=tk.FLAT, width=16, height=1)
                btn_restart.pack(pady=(18, 8), ipadx=8, ipady=4, fill=tk.X)
                btn_menu = tk.Button(inner, text="MAIN MENU", font=("Kenney Future Narrow", 14, "bold"), bg="#D33333", fg="white", command=main_menu, relief=tk.FLAT, width=16, height=1)
                btn_menu.pack(pady=(0, 10), ipadx=8, ipady=4, fill=tk.X)
                # Lưu lịch sử vào file history.json
                def save_history_entry(player_score, ai_score, difficulty, result, play_time):
                    import json
                    import os
                    history_path = os.path.join(os.path.dirname(__file__), "history.json")
                    entry = {
                        "player": player_score,
                        "ai": ai_score,
                        "difficulty": difficulty,
                        "result": result,
                        "time": play_time
                    }
                    try:
                        if os.path.exists(history_path):
                            with open(history_path, "r", encoding="utf-8") as f:
                                history = json.load(f)
                        else:
                            history = []
                    except Exception:
                        history = []
                    history.append(entry)
                    try:
                        with open(history_path, "w", encoding="utf-8") as f:
                            json.dump(history, f, ensure_ascii=False, indent=2)
                    except Exception:
                        pass

                difficulty = ""
                if hasattr(self, 'ui_ref') and hasattr(self.ui_ref, 'difficulty_var'):
                    difficulty = self.ui_ref.difficulty_var.get()
                result = "Win" if (self.score_var and msg == "YOU WIN") or (self.ai_score_var and msg == "YOU LOSE") else "Lose"
                save_history_entry(player_score, ai_score, difficulty, result, play_time)
                if self.score_var:
                    self.score_var.set(0)
                elif self.ai_score_var:
                    self.ai_score_var.set(0)
                self.is_game_over_flag = True
                # Đồng bộ cờ với đối thủ nếu có
                if hasattr(self, 'opponent') and self.opponent:
                    self.opponent.is_game_over_flag = True
                return True
        return False

    # Sinh khối mới, chọn ngẫu nhiên và đặt ở giữa đỉnh
    def spawn_block(self):
        if self.is_game_over_flag:
            return
        if self.is_game_over():
            return
        self.fast = False
        # Nếu chưa có khối tiếp theo thì random
        if self.next_block is None:
            idx = random.randint(0, len(tetrisGame.BLOCKS)-1)
            self.next_block = tetrisGame.BLOCKS[idx][0]
            self.next_color = tetrisGame.COLORS[idx]
        # Nếu chưa có khối tiếp tiếp thì random
        if self.next_next_block is None:
            idx2 = random.randint(0, len(tetrisGame.BLOCKS)-1)
            self.next_next_block = tetrisGame.BLOCKS[idx2][0]
            self.next_next_color = tetrisGame.COLORS[idx2]
        self.current_block = self.next_block
        self.current_color = self.next_color
        start_x = tetrisGame.BOARD_WIDTH // 2 - 2
        start_y = 0
        self.current_pos = [start_x, start_y]
        # Đẩy khối tiếp tiếp lên làm khối tiếp theo, random khối tiếp tiếp mới
        self.next_block = self.next_next_block
        self.next_color = self.next_next_color
        idx3 = random.randint(0, len(tetrisGame.BLOCKS)-1)
        self.next_next_block = tetrisGame.BLOCKS[idx3][0]
        self.next_next_color = tetrisGame.COLORS[idx3]
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
        # Vẽ vạch thua màu đỏ, để các block nằm trên vạch thua
        line_y = tetrisGame.LOSE_LINE_Y * tetrisGame.BLOCK_SIZE
        self.canvas.create_rectangle(
            0, line_y, tetrisGame.BOARD_WIDTH * tetrisGame.BLOCK_SIZE, line_y + 4,
            fill="#D33333", outline="#D33333", tags="block"
        )
        # Vẽ nền trắng phía trên vạch thua (không viền)
        if tetrisGame.LOSE_LINE_Y > 0:
            self.canvas.create_rectangle(
                0, 0,
                tetrisGame.BOARD_WIDTH * tetrisGame.BLOCK_SIZE,
                tetrisGame.LOSE_LINE_Y * tetrisGame.BLOCK_SIZE,
                fill="#EBEBEB", outline="", tags="block"
            )
        # Vẽ các khối đã nằm dưới
        for y in range(tetrisGame.LOSE_LINE_Y, tetrisGame.BOARD_HEIGHT):
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
            if self.instant_dropping == False:
                try:
                    import pygame
                    if not hasattr(self, '_thud_sound'):
                        self._thud_sound = pygame.mixer.Sound(r"d:/STUDY/Trí tuệ nhân tạo/Audio/thud.wav")
                    self._thud_sound.play()
                except Exception:
                    pass
            # Khóa khối vào board
            self.lock_block()
            self.draw_block()
            # Chỉ gọi check_and_clear_lines nếu không phải vừa instant drop
            if not self.instant_dropping:
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
                    # Phát âm thanh score_sound khi player ăn điểm
                    try:
                        import pygame
                        if not hasattr(self, '_score_sound'):
                            self._score_sound = pygame.mixer.Sound(r"d:/STUDY/Trí tuệ nhân tạo/Audio/score_sound.wav")
                        self._score_sound.play()
                    except Exception:
                        pass
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

    def add_garbage_row(self):
    # Tạo một hàng cản với 1 ô random trống
        empty_idx = random.randint(0, tetrisGame.BOARD_WIDTH - 1)
        garbage_row = ["gray" if x != empty_idx else None for x in range(tetrisGame.BOARD_WIDTH)]
        # Đẩy các khối hiện tại lên trên 1 hàng
        self.board.pop(0)
        self.board.append(garbage_row)
        self.draw_block()

    # Thiết lập trạng thái rơi nhanh (giữ S)
    def set_fast(self, fast):
        self.fast = fast

    instant_dropping = False

    def instant_drop(self):
        # Di chuyển khối xuống đáy ngay lập tức
        self.instant_dropping = True
        while self.can_move_down():
            self.current_pos[1] += 1
        self.draw_block()
        self.lock_block()
        self.draw_block()
        # Phát âm thanh thud.wav khi instant drop
        try:
            import pygame
            if not hasattr(self, '_thud_sound'):
                self._thud_sound = pygame.mixer.Sound(r"d:/STUDY/Trí tuệ nhân tạo/Audio/thud.wav")
            self._thud_sound.play()
        except Exception:
            pass
        if hasattr(self, 'opponent') and self.opponent:
            self.check_and_clear_lines(opponent=self.opponent)
        else:
            self.check_and_clear_lines()
        if self.is_game_over_flag:
            return
        if self.is_game_over():
            return
        self.fast = False
        self.canvas.after(500, lambda: setattr(self, 'instant_dropping', False))

    def move_left(self):
        px, py = self.current_pos
        for dx, dy in self.current_block:
            nx = px + dx - 1
            ny = py + dy
            if nx < 0 or (self.board[ny][nx] if 0 <= ny < tetrisGame.BOARD_HEIGHT else False):
                return
        self.current_pos[0] -= 1
        self.draw_block()
    def move_right(self):
        px, py = self.current_pos
        for dx, dy in self.current_block:
            nx = px + dx + 1
            ny = py + dy
            if nx >= tetrisGame.BOARD_WIDTH or (self.board[ny][nx] if 0 <= ny < tetrisGame.BOARD_HEIGHT and 0 <= nx < tetrisGame.BOARD_WIDTH else False):
                return
        self.current_pos[0] += 1
        self.draw_block()

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

class AIController:
    def __init__(self, game):
        self.game = game
        self.running = False
        self.target_x = None
        self.target_rot = None

    def start(self):
        if self.game.is_game_over():
            return
        self.running = True
        # Lấy độ khó từ UI
        if hasattr(self.game, 'ui_ref') and self.game.ui_ref:
            difficulty = self.game.ui_ref.difficulty_var.get()
        if difficulty == "EASY":
            self.plan_greedy_move()
        elif difficulty == "MEDIUM":
            self.plan_astar_move()
        elif difficulty == "HARD":
            self.plan_expectimax_move()
        else:
            self.plan_astar_move()
        self.do_move()

    def plan_greedy_move(self):
        # Xét khối hiện tại và khối kế tiếp, chọn điểm heuristic tốt nhất sau khi đặt cả hai khối
        best_score = None
        best_x = None
        best_rot = None
        block = self.game.current_block
        color = self.game.current_color
        board = [row[:] for row in self.game.board]
        rotations = [block]
        for _ in range(3):
            block = [(dy, -dx) for dx, dy in block]
            if block not in rotations:
                rotations.append(block)
        next_block = self.game.next_block
        next_color = self.game.next_color
        for rot_idx, rot in enumerate(rotations):
            min_x = min(dx for dx, dy in rot)
            max_x = max(dx for dx, dy in rot)
            for x in range(-min_x, self.game.BOARD_WIDTH - max_x):
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
                # Xét luôn khối kế tiếp
                nb_rot = next_block
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
                            temp_board2[ny2][nx2] = next_color
                        score2 = self.heuristic(temp_board2)
                        if nb_best is None or score2 > nb_best:
                            nb_best = score2
                # Điểm kỳ vọng là điểm tốt nhất sau khi đặt khối kế tiếp
                expect_score = nb_best
                if expect_score is not None:
                    if best_score is None or expect_score > best_score:
                        best_score = expect_score
                        best_x = x
                        best_rot = rot_idx
        self.target_x = best_x
        self.target_rot = best_rot

    def plan_astar_move(self):
        # Xét khối hiện tại, khối kế tiếp, và khối tiếp tiếp, chọn điểm kỳ vọng cao nhất
        best_score = None
        best_x = None
        best_rot = None
        block = self.game.current_block
        color = self.game.current_color
        board = [row[:] for row in self.game.board]
        rotations = [block]
        for _ in range(3):
            block = [(dy, -dx) for dx, dy in block]
            if block not in rotations:
                rotations.append(block)
        next_block = self.game.next_block
        next_color = self.game.next_color
        next_next_block = self.game.next_next_block
        next_next_color = self.game.next_next_color
        for rot_idx, rot in enumerate(rotations):
            min_x = min(dx for dx, dy in rot)
            max_x = max(dx for dx, dy in rot)
            for x in range(-min_x, self.game.BOARD_WIDTH - max_x):
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
                # Lookahead đúng khối kế tiếp (không xét các hướng xoay)
                nb_rot2 = next_block
                nb_min_x = min(dx for dx, dy in nb_rot2)
                nb_max_x = max(dx for dx, dy in nb_rot2)
                nb_best = None
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
                        temp_board2[ny2][nx2] = next_color
                    # Lookahead đúng khối tiếp tiếp (không xét các hướng xoay)
                    nnb_rot2 = next_next_block
                    nnb_min_x = min(dx for dx, dy in nnb_rot2)
                    nnb_max_x = max(dx for dx, dy in nnb_rot2)
                    nnb_best = None
                    for nnb_x in range(-nnb_min_x, self.game.BOARD_WIDTH - nnb_max_x):
                        nnb_y = 0
                        while True:
                            if not self.can_place(nnb_rot2, nnb_x, nnb_y, temp_board2):
                                break
                            nnb_y += 1
                        nnb_y -= 1
                        if nnb_y < 0:
                            continue
                        temp_board3 = [row[:] for row in temp_board2]
                        for dx3, dy3 in nnb_rot2:
                            nx3 = nnb_x + dx3
                            ny3 = nnb_y + dy3
                            temp_board3[ny3][nx3] = next_next_color
                        score3 = self.heuristic(temp_board3)
                        if nnb_best is None or score3 > nnb_best:
                            nnb_best = score3
                    if nnb_best is not None:
                        if nb_best is None or nnb_best > nb_best:
                            nb_best = nnb_best
                # Điểm kỳ vọng là điểm tốt nhất sau khi đặt cả 3 khối
                expect_score = nb_best
                if expect_score is not None:
                    if best_score is None or expect_score > best_score:
                        best_score = expect_score
                        best_x = x
                        best_rot = rot_idx
        self.target_x = best_x
        self.target_rot = best_rot

    def plan_expectimax_move(self):
        if self.game.is_game_over():
            return
        # Expectimax: thử mọi nước đi cho khối hiện tại, giả lập đúng khối tiếp theo và tiếp tiếp
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
        # Lấy đúng khối tiếp theo và tiếp tiếp
        next_block = self.game.next_block
        next_color = self.game.next_color
        next_next_block = self.game.next_next_block
        next_next_color = self.game.next_next_color
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
                # Lookahead: chỉ lấy 2 lựa chọn tốt nhất cho khối tiếp theo
                nb_rot = next_block
                nb_rotations = [nb_rot]
                for _ in range(3):
                    nb_rot = [(dy, -dx) for dx, dy in nb_rot]
                    if nb_rot not in nb_rotations:
                        nb_rotations.append(nb_rot)
                nb_moves = []
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
                            temp_board2[ny2][nx2] = next_color
                        score2 = self.heuristic(temp_board2)
                        nb_moves.append((score2, temp_board2))
                # Chỉ lấy 2 lựa chọn tốt nhất
                nb_moves.sort(reverse=True, key=lambda x: x[0])
                nb_moves = nb_moves[:2]
                expect_score = None
                for score2, temp_board2 in nb_moves:
                    # Lookahead tiếp tiếp
                    nnb_rot = next_next_block
                    nnb_rotations = [nnb_rot]
                    for _ in range(3):
                        nnb_rot = [(dy, -dx) for dx, dy in nnb_rot]
                        if nnb_rot not in nnb_rotations:
                            nnb_rotations.append(nnb_rot)
                    nnb_best = None
                    for nnb_rot2 in nnb_rotations:
                        nnb_min_x = min(dx for dx, dy in nnb_rot2)
                        nnb_max_x = max(dx for dx, dy in nnb_rot2)
                        for nnb_x in range(-nnb_min_x, self.game.BOARD_WIDTH - nnb_max_x):
                            nnb_y = 0
                            while True:
                                if not self.can_place(nnb_rot2, nnb_x, nnb_y, temp_board2):
                                    break
                                nnb_y += 1
                            nnb_y -= 1
                            if nnb_y < 0:
                                continue
                            temp_board3 = [row[:] for row in temp_board2]
                            for dx3, dy3 in nnb_rot2:
                                nx3 = nnb_x + dx3
                                ny3 = nnb_y + dy3
                                temp_board3[ny3][nx3] = next_next_color
                            score3 = self.heuristic(temp_board3)
                            if nnb_best is None or score3 > nnb_best:
                                nnb_best = score3
                    if nnb_best is not None:
                        if expect_score is None or nnb_best > expect_score:
                            expect_score = nnb_best
                if expect_score is not None:
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

        lines_cleared = self.count_lines(board)
        agg_height, bumpiness = self.get_heights_bump(board)
        holes = self.count_holes(board)
        covered_holes = self.count_covered_holes(board)
        # Trọng số cơ bản (khi chiều cao thấp)
        if agg_height <= self.game.BOARD_HEIGHT * self.game.BOARD_WIDTH * 0.6:
            w_lines = 1.0  
            w_height = -0.5
            w_holes = -0.7
            w_bump = -0.2
            w_covered_hole = -0.8 
        # Dynamically adjust weights if aggregate height is too high
        elif agg_height > self.game.BOARD_HEIGHT * self.game.BOARD_WIDTH * 0.6:
            # Board is getting dangerously high, prioritize lowering height and avoiding holes
            w_height = -1.2
            w_holes = -1.2
            w_covered_hole = -1.5
            w_lines = 1.2
            w_bump = -0.3

        score = (w_lines * lines_cleared + w_height * agg_height + w_holes * holes + w_bump * bumpiness + w_covered_hole * covered_holes)
        return score

    def count_covered_holes(self, board):
        covered = 0
        for x in range(self.game.BOARD_WIDTH):
            found_block = False
            for y in range(self.game.BOARD_HEIGHT):
                if board[y][x]:
                    found_block = True
                elif found_block:
                    # Nếu đã gặp block phía trên, đây là covered hole
                    covered += 1
        return covered

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
        # Chế độ Khó: dùng instant_drop
        if hasattr(self.game, 'ui_ref') and self.game.ui_ref:
            difficulty = self.game.ui_ref.difficulty_var.get()
        import random
        if difficulty == "HARD":
            self.game.instant_drop()
        elif difficulty == "MEDIUM":
            # 25% xác suất dùng instant_drop
            if random.random() < 0.25:
                self.game.instant_drop()
            else:
                self.game.set_fast(True)
        else:
            self.game.set_fast(True)

def main():
    root = tk.Tk()
    start = tetrisUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
