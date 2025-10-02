import tkinter as tk
from PIL import Image, ImageTk

# Đường dẫn file ảnh
BG_PATH = "D:/STUDY/Trí tuệ nhân tạo/UI/background.png"
BTN_PATH = "D:/STUDY/Trí tuệ nhân tạo/UI/PNG/Red/Double/button_rectangle_gloss.png"

class StartScreen(tk.Frame):
    def __init__(self, master, on_start, on_history):
        super().__init__(master)
        self.pack(fill=tk.BOTH, expand=True)
        # Load background
        bg_img = Image.open(BG_PATH)
        self.bg_photo = ImageTk.PhotoImage(bg_img)
        self.bg_label = tk.Label(self, image=self.bg_photo, borderwidth=0, highlightthickness=0)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        # Load button image
        btn_img = Image.open(BTN_PATH)
        # Resize button image nhỏ lại
        btn_img = btn_img.resize((300, 70), Image.LANCZOS)
        self.btn_photo = ImageTk.PhotoImage(btn_img)
        btn_w, btn_h = btn_img.size
        # Đưa nút vào giữa màn hình (căn giữa cả cụm nút)
        total_height = btn_h * 2 + 20 # Giải thích: 2 nút cộng khoảng cách 20px
        x = (bg_img.width - btn_w) // 2 - 140 # Căn giữa theo chiều ngang
        y = (bg_img.height - total_height) // 2 # Căn giữa theo chiều dọc
        # START button
        self.start_btn = tk.Button(self, image=self.btn_photo, text="START", compound=tk.CENTER,
                                   font=("Kenney Future Narrow", 18, "bold"), fg="white", bg="#ff5a76",
                                   command=self.on_start_click, borderwidth=0, highlightthickness=0, activebackground="#ff5a76")
        self.start_btn.place(x=x, y=y, width=btn_w, height=btn_h)
        # HISTORY button
        self.history_btn = tk.Button(self, image=self.btn_photo, text="HISTORY", compound=tk.CENTER,
                                     font=("Kenney Future Narrow", 18, "bold"), fg="white", bg="#ff5a76",
                                     command=on_history, borderwidth=0, highlightthickness=0, activebackground="#ff5a76")
        self.history_btn.place(x=x, y=y+btn_h+20, width=btn_w, height=btn_h)

    def show_difficulty_popup(self, on_confirm):
        # Tạo cửa sổ popup không có header
        popup = tk.Toplevel(self)
        popup.overrideredirect(True)
        popup.geometry("440x440")
        # Đặt popup vào giữa màn hình
        root = self.winfo_toplevel()
        root.update_idletasks()
        x = root.winfo_x() + (root.winfo_width() - 440) // 2 + 10
        y = root.winfo_y() + (root.winfo_height() - 440) // 2 + 30
        popup.geometry(f"440x440+{x}+{y}")
        # Load hình nền popup (phóng to)
        popup_bg_img = Image.open("D:/STUDY/Trí tuệ nhân tạo/UI/PNG/Red/Double/button_square_border.png").resize((440, 440), Image.LANCZOS)
        popup_bg = ImageTk.PhotoImage(popup_bg_img)
        bg_label = tk.Label(popup, image=popup_bg, borderwidth=0)
        bg_label.image = popup_bg
        bg_label.place(x=0, y=0)
        # Dòng chữ chọn độ khó
        label = tk.Label(popup, text="Choose difficulty", font=("Kenney Future Narrow", 18, "bold"), fg="#d33", bg="#dde")
        label.place(x=58, y=60, width=327, height=60)
        # Custom select menu (phóng to nhẹ)
        select_img = Image.open("D:/STUDY/Trí tuệ nhân tạo/UI/PNG/Red/Double/button_rectangle_line.png").resize((320, 80), Image.LANCZOS)
        select_photo = ImageTk.PhotoImage(select_img)
        self.difficulty = tk.StringVar(value="EASY")
        def show_options():
            options_win = tk.Toplevel(popup)
            options_win.overrideredirect(True)
            options_win.geometry(f"320x240+{x+80}+{y+160}")
            options_win.configure(bg="#dde")
            for i, opt in enumerate(["EASY", "MEDIUM", "HARD"]):
                btn = tk.Button(options_win, text=opt, font=("Kenney Future Narrow", 22, "bold"), bg="#dde", fg="#d33", borderwidth=0,
                                command=lambda v=opt: (self.difficulty.set(v), options_win.destroy()))
                btn.place(x=0, y=i*80, width=320, height=80)
        select_btn = tk.Button(popup, image=select_photo, textvariable=self.difficulty, compound=tk.CENTER,
                              font=("Kenney Future Narrow", 22, "bold"), fg="#d33", bg="#dde", borderwidth=0,
                              command=show_options)
        select_btn.image = select_photo
        select_btn.place(x=80, y=160, width=320, height=80)
        # Dấu X và V (phóng to)
        def close_popup():
            popup.destroy()
        def confirm():
            if self.difficulty.get() != "(Chọn độ khó)":
                popup.destroy()
                on_confirm(self.difficulty.get())
        x_img = Image.open("D:/STUDY/Trí tuệ nhân tạo/UI/PNG/Red/Double/check_square_grey_cross.png").resize((64,64), Image.LANCZOS)
        v_img = Image.open("D:/STUDY/Trí tuệ nhân tạo/UI/PNG/Red/Double/check_square_grey_checkmark.png").resize((64,64), Image.LANCZOS)
        x_photo = ImageTk.PhotoImage(x_img)
        v_photo = ImageTk.PhotoImage(v_img)
        btn_y = 200
        btn_x = 120
        x_btn = tk.Button(popup, image=x_photo, borderwidth=0, command=close_popup, bg="#dde", activebackground="#dde")
        x_btn.image = x_photo
        x_btn.place(x=btn_x, y=btn_y, width=64, height=64)
        v_btn = tk.Button(popup, image=v_photo, borderwidth=0, command=confirm, bg="#dde", activebackground="#dde")
        v_btn.image = v_photo
        v_btn.place(x=btn_x+100, y=btn_y, width=64, height=64)

    def on_start_click(self):
        def start_game_with_difficulty(diff):
            self.master.destroy()
            import tetrisAI
            tetrisAI.selected_difficulty = diff
            tetrisAI.main()
        self.show_difficulty_popup(start_game_with_difficulty)

# Ví dụ sử dụng
if __name__ == "__main__":
    def show_game():
        root.destroy()
        # Ở đây bạn mở cửa sổ game hiện tại
        import tetrisAI
        tetrisAI.main()  # Giả sử game có hàm main
    def show_history():
        print("Lịch sử được nhấn!")
    root = tk.Tk()
    root.geometry("1010x700")
    root.overrideredirect(False)
    root.title("")
    StartScreen(root, show_game, show_history)
    root.mainloop()
