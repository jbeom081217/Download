import os
import tempfile
import requests
import subprocess
import time
import threading
from pynput import mouse, keyboard
from ctypes import *
from ctypes.wintypes import *
import ctypes
import sys
import winsound  # 🔊 비프음 모듈

# -------- 관리자 권한 확인 --------
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )
    sys.exit(0)

# -------- GitHub 파일 다운로드 --------
sys_url = "https://github.com/jbeom081217/Download/raw/refs/heads/main/Oykyo.sys"
injector_url = "https://github.com/jbeom081217/Download/raw/refs/heads/main/injector.exe"

temp_dir = tempfile.gettempdir()
injector_path = os.path.join(temp_dir, "injecter.exe")
target_file = os.path.join(temp_dir, "Oykyo.sys")

def download_file(url, path):
    r = requests.get(url)
    r.raise_for_status()
    with open(path, "wb") as f:
        f.write(r.content)

print(f"[+] Downloading injector.exe -> {injector_path}")
download_file(injector_url, injector_path)

print(f"[+] Downloading Oykyo.sys -> {target_file}")
download_file(sys_url, target_file)

# injector.exe 실행
print(f"[+] Running injector.exe with {target_file}")
subprocess.run([injector_path, target_file], shell=True)

# 5초 대기 후 파일 삭제
time.sleep(3)
for file_path in (injector_path, target_file):
    try:
        os.remove(file_path)
        print(f"[+] Deleted {file_path}")
    except OSError as e:
        print(f"[-] Failed to delete {file_path}: {e}")
        
time.sleep(3)
os.system('cls')
text = "made by くに"
for char in text:
    sys.stdout.write(char)
    sys.stdout.flush()
    time.sleep(0.1)
print()

# -------- 드라이버 마우스 제어 --------
GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
OPEN_EXISTING = 3
INVALID_HANDLE_VALUE = -1
USHORT = c_ushort

def CTL_CODE(DeviceType, Function, Method, Access):
    return (DeviceType << 16) | (Access << 14) | (Function << 2) | Method

class MouseController:
    def __init__(self):
        self.hDriver = windll.kernel32.CreateFileA(
            b"\\\\.\\Oykyo",
            GENERIC_READ | GENERIC_WRITE,
            FILE_SHARE_READ | FILE_SHARE_WRITE,
            None,
            OPEN_EXISTING,
            0,
            None,
        )
        if self.hDriver == INVALID_HANDLE_VALUE:
            raise RuntimeError("Failed to open driver.")

    def __del__(self):
        if self.hDriver != INVALID_HANDLE_VALUE:
            windll.kernel32.CloseHandle(self.hDriver)

    def move_mouse(self, x, y):
        return self.send_mouse_event(x, y, 0)

    def click(self, button):
        return self.send_mouse_event(0, 0, button)

    def send_mouse_event(self, x, y, button):
        if self.hDriver == INVALID_HANDLE_VALUE:
            return False

        class MOUSE_REQUEST(Structure):
            _fields_ = [("x", c_int), ("y", c_int), ("buttonFlags", USHORT)]

        request = MOUSE_REQUEST(int(x), int(y), USHORT(button))
        return windll.kernel32.DeviceIoControl(
            self.hDriver,
            CTL_CODE(34, 73142, 0, 0),
            byref(request),
            sizeof(request),
            None,
            0,
            byref(c_ulong()),
            None,
        )

# -------- 리코일 패턴 --------
AK_PATTERN = [
    (0.000000, -2.257792), (0.323242, -2.300758), (0.649593, -2.299759),
    (0.848786, -2.259034), (1.075408, -2.323947), (1.268491, -2.215956),
    (1.330963, -2.236556), (1.336833, -2.218203), (1.505516, -2.143454),
    (1.504423, -2.233091), (1.442116, -2.270194), (1.478543, -2.204318),
    (1.392874, -2.165817), (1.480824, -2.177887), (1.597069, -2.270915),
    (1.449996, -2.145893), (1.369179, -2.270450), (1.582363, -2.298334),
    (1.516872, -2.235066), (1.498249, -2.238401), (1.465769, -2.331642),
    (1.564812, -2.242621), (1.517519, -2.303052), (1.422433, -2.211946),
    (1.553195, -2.248043), (1.510463, -2.285327), (1.553878, -2.240047),
    (1.520380, -2.221839), (1.553878, -2.240047), (1.553195, -2.248043)
]

DELAY = 0.1333
left_pressed = False
right_pressed = False
ctrl_pressed = False  # 뒤로 버튼 대체
macro_enabled = True
stop_event = threading.Event()

# -------- 매크로 토글 --------
def toggle_macro():
    global macro_enabled
    macro_enabled = not macro_enabled
    if macro_enabled:
        winsound.Beep(1000, 200)
    else:
        winsound.Beep(600, 200)

# -------- 리코일 루프 --------
def recoil_loop():
    global left_pressed, right_pressed, ctrl_pressed
    mouse_driver = MouseController()
    steps = 20

    while left_pressed and right_pressed and macro_enabled:
        for i in range(len(AK_PATTERN) - 1):
            if not (left_pressed and right_pressed and macro_enabled):
                stop_event.set()
                break

            start = AK_PATTERN[i]
            end = AK_PATTERN[i + 1]
            dx = (end[0] - start[0]) / steps
            dy = (end[1] - start[1]) / steps

            for s in range(1, steps + 1):
                if not (left_pressed and right_pressed and macro_enabled):
                    stop_event.set()
                    break

                scale = 1.735 if ctrl_pressed else 3
                x = (start[0] + dx * s) * scale
                y = (start[1] + dy * s) * scale

                mouse_driver.move_mouse(-x, -y)
                time.sleep(DELAY / steps)

# -------- 마우스/키보드 이벤트 --------
def on_click(x, y, button, pressed):
    global left_pressed, right_pressed, ctrl_pressed
    if button == mouse.Button.left:
        left_pressed = pressed
    elif button == mouse.Button.right:
        right_pressed = pressed
    elif button == mouse.Button.x1:  # 뒤로 버튼
        ctrl_pressed = pressed

    if macro_enabled and left_pressed and right_pressed:
        if stop_event.is_set():
            stop_event.clear()
            threading.Thread(target=recoil_loop, daemon=True).start()
    else:
        if not stop_event.is_set():
            stop_event.set()

def on_key_press(key):
    if key == keyboard.Key.insert:  # Insert 키로 매크로 ON/OFF
        toggle_macro()

def on_key_release(key):
    pass

# -------- 메인 실행 --------
if __name__ == "__main__":
    stop_event.set()
    with mouse.Listener(on_click=on_click) as mouse_listener, \
         keyboard.Listener(on_press=on_key_press, on_release=on_key_release) as keyboard_listener:
        mouse_listener.join()
        keyboard_listener.join()
