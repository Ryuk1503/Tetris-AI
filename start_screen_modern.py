import pygame
import sys
import subprocess

# Đường dẫn file ảnh
BG_PATH = "D:/STUDY/Trí tuệ nhân tạo/UI/background.png"
BTN_PATH = "D:/STUDY/Trí tuệ nhân tạo/UI/PNG/Red/Double/button_rectangle_gloss.png"
LOGO_PATH = "D:/STUDY/Trí tuệ nhân tạo/UI/Tetris_logo.png"
MUSIC_PATH = "d:/STUDY/Trí tuệ nhân tạo/Audio/06 - Continue.mp3"

pygame.init()
screen = pygame.display.set_mode((1010, 700))
pygame.display.set_caption("Tetris Start Screen")
pygame.display.set_mode((1010, 700), pygame.NOFRAME)


# Nhạc nền
try:
    pygame.mixer.init()
    pygame.mixer.music.load(MUSIC_PATH)
    pygame.mixer.music.play(-1)
except Exception:
    pass

# Load images
bg = pygame.image.load(BG_PATH).convert()
# Phóng to logo
logo = pygame.image.load(LOGO_PATH).convert_alpha()
logo = pygame.transform.smoothscale(logo, (500, 374))
btn_img = pygame.image.load(BTN_PATH).convert_alpha()
btn_img = pygame.transform.smoothscale(btn_img, (300, 70))

# Button settings
btn_w, btn_h = 300, 70
total_height = btn_h * 3
x = (bg.get_width() - btn_w) // 2 - 140
y = (bg.get_height() - total_height) // 2 
# Tính lại vị trí logo cho căn giữa
logo_x = x + (btn_w - 500) // 2
logo_y = y - 250

# Button rects
start_rect = pygame.Rect(x, y + 150, btn_w, btn_h)
history_rect = pygame.Rect(x, y+btn_h+20 + 150, btn_w, btn_h)
quit_rect = pygame.Rect(x, y+btn_h*2+40 + 150, btn_w, btn_h)

font_btn = pygame.font.Font("D:/STUDY/Trí tuệ nhân tạo/Font/Kenney Future Narrow.ttf", 30)
font_logo = pygame.font.Font("D:/STUDY/Trí tuệ nhân tạo/Font/Kenney Future Narrow.ttf", 48)

def show_history_popup(history_list):
    # Popup surface
    popup_w, popup_h = 900, 560
    popup = pygame.Surface((popup_w, popup_h), pygame.SRCALPHA)
    popup.fill((247, 247, 247, 240))
    pygame.draw.rect(popup, (211, 51, 51), (0, 0, popup_w, popup_h), 6)
    font_title = pygame.font.Font("D:/STUDY/Trí tuệ nhân tạo/Font/Kenney Future Narrow.ttf", 32)
    title = font_title.render("PLAY HISTORY", True, (211, 51, 51))
    popup.blit(title, ((popup_w-title.get_width())//2, 24))
    font_cell = pygame.font.Font("D:/STUDY/Trí tuệ nhân tạo/Font/Kenney Future Narrow.ttf", 20)
    max_rows = 10
    scroll_offset = 0
    total_rows = len(history_list)
    running_popup = True
    while running_popup:
        popup.fill((247, 247, 247, 240))
        pygame.draw.rect(popup, (211, 51, 51), (0, 0, popup_w, popup_h), 6)
        popup.blit(title, ((popup_w-title.get_width())//2, 24))
        headers = ["ID", "Difficulty", "Your Score", "AI Score", "Result", "Time"]
        # Tăng khoảng cách giữa các cột cho dễ nhìn
        # Khoảng cách cột: Difficulty gần ID, Your Score và AI Score cách đều nhau, các cột cách đều
        col_widths = [80, 170, 160, 160, 100, 100]
        x0 = 50
        y0 = 90
        font_btn = pygame.font.Font("D:/STUDY/Trí tuệ nhân tạo/Font/Kenney Future Narrow.ttf", 24)
        close_rect = pygame.Rect(popup_w-140, popup_h-70, 130, 50)
        clear_rect = pygame.Rect(popup_w-280, popup_h-70, 130, 50)
        pygame.draw.rect(popup, (211,51,51), close_rect, border_radius=12)
        pygame.draw.rect(popup, (80,80,80), clear_rect, border_radius=12)
        txt_close = font_btn.render("CLOSE", True, (255,255,255))
        popup.blit(txt_close, (close_rect.x + (close_rect.w-txt_close.get_width())//2, close_rect.y + (close_rect.h-txt_close.get_height())//2))
        txt_clear = font_btn.render("CLEAR", True, (255,255,255))
        popup.blit(txt_clear, (clear_rect.x + (clear_rect.w-txt_clear.get_width())//2, clear_rect.y + (clear_rect.h-txt_clear.get_height())//2))
        if not history_list:
            txt = font_cell.render("There is no play history.", True, (80,80,80))
            popup.blit(txt, ((popup_w-txt.get_width())//2, popup_h//2-20))
        else:
            # Header
            # Vẽ header, căn giữa text trong mỗi cột
            col_positions = [x0]
            for w in col_widths:
                col_positions.append(col_positions[-1] + w)
            for i, h in enumerate(headers):
                cell = font_cell.render(h, True, (211,51,51))
                col_center = col_positions[i] + col_widths[i]//2
                popup.blit(cell, (col_center - cell.get_width()//2, y0))
            # Vẽ đường kẻ ngang đỏ ngăn cách header và dữ liệu
            pygame.draw.line(popup, (211,51,51), (x0, y0+32), (col_positions[-1], y0+32), 3)
            show_rows = history_list[scroll_offset:scroll_offset+max_rows]
            for idx, entry in enumerate(show_rows, 1+scroll_offset):
                values = [str(idx), entry.get("difficulty",""), str(entry.get("player","")), str(entry.get("ai","")), entry.get("result",""), entry.get("time","")]
                for i, val in enumerate(values):
                    cell = font_cell.render(val, True, (40,40,40))
                    col_center = x0 + sum(col_widths[:i]) + col_widths[i]//2
                    popup.blit(cell, (col_center - cell.get_width()//2, y0+36+idx*32-scroll_offset*32))
            # Vẽ nút cuộn nếu cần
            if total_rows > max_rows:
                font_scroll = pygame.font.Font("D:/STUDY/Trí tuệ nhân tạo/Font/Kenney Future Narrow.ttf", 18)
                up_rect = pygame.Rect(popup_w-60, y0+36, 32, 32)
                down_rect = pygame.Rect(popup_w-60, y0+36+max_rows*32, 32, 32)
                pygame.draw.rect(popup, (211,51,51), up_rect, border_radius=8)
                pygame.draw.rect(popup, (211,51,51), down_rect, border_radius=8)
                up_txt = font_scroll.render("▲", True, (255,255,255))
                down_txt = font_scroll.render("▼", True, (255,255,255))
                popup.blit(up_txt, (up_rect.x+8, up_rect.y+2))
                popup.blit(down_txt, (down_rect.x+8, down_rect.y+2))
        px = (screen.get_width()-popup_w)//2
        py = (screen.get_height()-popup_h)//2
        screen.blit(popup, (px, py))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if pygame.Rect(px+close_rect.x, py+close_rect.y, close_rect.w, close_rect.h).collidepoint(mx, my):
                    running_popup = False
                elif pygame.Rect(px+clear_rect.x, py+clear_rect.y, clear_rect.w, clear_rect.h).collidepoint(mx, my):
                    import os
                    try:
                        with open("d:/STUDY/Trí tuệ nhân tạo/history.json", "w", encoding="utf-8") as f:
                            f.write("[]")
                    except Exception:
                        pass
                    history_list.clear()
                    scroll_offset = 0
                elif total_rows > max_rows:
                    up_rect = pygame.Rect(px+popup_w-60, py+y0+36, 32, 32)
                    down_rect = pygame.Rect(px+popup_w-60, py+y0+36+max_rows*32, 32, 32)
                    if up_rect.collidepoint(mx, my) and scroll_offset > 0:
                        scroll_offset -= 1
                    elif down_rect.collidepoint(mx, my) and scroll_offset+max_rows < total_rows:
                        scroll_offset += 1

def show_difficulty_popup():
    # Popup surface
    popup_w, popup_h = 440, 440  # Tăng chiều cao popup
    popup = pygame.Surface((popup_w, popup_h), pygame.SRCALPHA)
    popup.fill((220, 220, 238, 240))
    # Draw border
    pygame.draw.rect(popup, (211, 51, 51), (0, 0, popup_w, popup_h), 6)
    # Title
    font_title = pygame.font.Font("D:/STUDY/Trí tuệ nhân tạo/Font/Kenney Future Narrow.ttf", 32)
    title = font_title.render("CHOOSE DIFFICULTY", True, (211, 51, 51))
    popup.blit(title, ((popup_w-title.get_width())//2, 30))
    # Difficulty buttons
    btn_w, btn_h = 320, 60
    btn_x = (popup_w - btn_w)//2
    btn_ys = [110, 190, 270]
    btn_texts = ["EASY", "MEDIUM", "HARD"]
    font_diff = pygame.font.Font("D:/STUDY/Trí tuệ nhân tạo/Font/Kenney Future Narrow.ttf", 28)
    selected = None
    done = False
    confirmed = False
    # X và V button
    x_img = pygame.image.load("D:/STUDY/Trí tuệ nhân tạo/UI/PNG/Red/Double/check_square_grey_cross.png").convert_alpha()
    v_img = pygame.image.load("D:/STUDY/Trí tuệ nhân tạo/UI/PNG/Red/Double/check_square_grey_checkmark.png").convert_alpha()
    x_img = pygame.transform.smoothscale(x_img, (64,64))
    v_img = pygame.transform.smoothscale(v_img, (64,64))
    x_rect = pygame.Rect((popup_w//2)-82, 370, 64, 64)
    v_rect = pygame.Rect((popup_w//2)+18, 370, 64, 64)
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                px = (screen.get_width()-popup_w)//2
                py = (screen.get_height()-popup_h)//2
                # Check difficulty buttons
                for i, by in enumerate(btn_ys):
                    rect = pygame.Rect(px+btn_x, py+by, btn_w, btn_h)
                    if rect.collidepoint(mx, my):
                        selected = btn_texts[i]
                # Check X button
                if pygame.Rect(px+x_rect.x, py+x_rect.y, x_rect.w, x_rect.h).collidepoint(mx, my):
                    return None  # Thoát ra main menu
                # Check V button
                if pygame.Rect(px+v_rect.x, py+v_rect.y, v_rect.w, v_rect.h).collidepoint(mx, my):
                    if selected:
                        confirmed = True
                        done = True
        
        # Draw popup overlay only
        px = (screen.get_width()-popup_w)//2
        py = (screen.get_height()-popup_h)//2
        screen.blit(popup, (px, py))
        # Draw difficulty buttons
        for i, by in enumerate(btn_ys):
            rect = pygame.Rect(px+btn_x, py+by, btn_w, btn_h)
            if selected == btn_texts[i]:
                pygame.draw.rect(screen, (211, 51, 51), rect)
                txt = font_diff.render(btn_texts[i], True, (255, 255, 255))  # Chữ trắng khi chọn
            else:
                pygame.draw.rect(screen, (221, 221, 238), rect)
                txt = font_diff.render(btn_texts[i], True, (211, 51, 51))  # Chữ đỏ khi chưa chọn
            pygame.draw.rect(screen, (211, 51, 51), rect, 3)
            screen.blit(txt, (rect.x + (btn_w-txt.get_width())//2, rect.y + (btn_h-txt.get_height())//2))
        # Draw X and V buttons
        screen.blit(x_img, (px+x_rect.x, py+x_rect.y))
        screen.blit(v_img, (px+v_rect.x, py+v_rect.y))
        pygame.display.flip()
    return selected if confirmed else None

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if start_rect.collidepoint(event.pos):
                diff = show_difficulty_popup()
                print(f"START pressed, difficulty: {diff}")
                if diff:
                    import os
                    os.environ["TETRIS_DIFFICULTY"] = diff
                    subprocess.Popen([sys.executable, "d:/STUDY/Trí tuệ nhân tạo/tetrisAI.py"])
                    pygame.quit()
                    sys.exit()
            elif history_rect.collidepoint(event.pos):
                # Hiện popup lịch sử
                import json
                try:
                    with open("d:/STUDY/Trí tuệ nhân tạo/history.json", "r", encoding="utf-8") as f:
                        history_list = json.load(f)
                except Exception:
                    history_list = []
                show_history_popup(history_list)
            elif quit_rect.collidepoint(event.pos):
                running = False

    screen.blit(bg, (0, 0))
    screen.blit(logo, (logo_x, logo_y))
    # Draw buttons
    screen.blit(btn_img, start_rect)
    screen.blit(btn_img, history_rect)
    screen.blit(btn_img, quit_rect)
    # Draw button text
    start_text = font_btn.render("START", True, (255,255,255))
    history_text = font_btn.render("HISTORY", True, (255,255,255))
    quit_text = font_btn.render("QUIT", True, (255,255,255))
    screen.blit(start_text, (start_rect.x + (btn_w-start_text.get_width())//2, start_rect.y + (btn_h-start_text.get_height())//2))
    screen.blit(history_text, (history_rect.x + (btn_w-history_text.get_width())//2, history_rect.y + (btn_h-history_text.get_height())//2))
    screen.blit(quit_text, (quit_rect.x + (btn_w-quit_text.get_width())//2, quit_rect.y + (btn_h-quit_text.get_height())//2))

    pygame.display.flip()

pygame.quit()
sys.exit()
