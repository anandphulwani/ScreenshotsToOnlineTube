import ctypes
from PyQt5.QtCore import QAbstractNativeEventFilter, QTimer
from ctypes import wintypes
import win32con
import win32gui
import win32api
import pywintypes
import sys

user32 = ctypes.WinDLL('user32', use_last_error=True)

# Function prototypes
RegisterShellHookWindow = user32.RegisterShellHookWindow
RegisterShellHookWindow.restype = wintypes.BOOL
RegisterShellHookWindow.argtypes = [wintypes.HWND]
RegisterWindowMessage = user32.RegisterWindowMessageA
RegisterWindowMessage.restype = wintypes.UINT
RegisterWindowMessage.argtypes = [ctypes.c_char_p]

# Constants
HSHELL_WINDOWACTIVATED = 4
HSHELL_WINDOWCREATED = 1
HSHELL_WINDOWDESTROYED = 2
HSHELL_REDRAW = 6

class ShellHookEventFilter(QAbstractNativeEventFilter):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.register_shell_hook_window()
        self.previousLocationOfWindow = None
        self.app.show()
        self.app.hide()
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_window)
        self.timer.start(200)

    def nativeEventFilter(self, eventType, message):
        msg = ctypes.wintypes.MSG.from_address(message.__int__())
        if (msg.message == WM_SHELLHOOKMESSAGE and (msg.wParam == HSHELL_WINDOWCREATED or msg.wParam == HSHELL_WINDOWACTIVATED)):
            title = win32gui.GetWindowText(msg.lParam)
            if title == "Automatic Screenshotter":
                # print("Window is focused, ", end = "")
                if not hasattr(self, 'timer') or self.timer == None or not self.timer.isActive():
                    # print("Attaching and showing the window now, on create/activate.", end = "")
                    self.timer = QTimer()
                    self.timer.timeout.connect(self.check_window)
                    self.timer.start(200)
                # print("")
        elif msg.message == WM_SHELLHOOKMESSAGE and msg.wParam == HSHELL_WINDOWDESTROYED:
            title = win32gui.GetWindowText(msg.lParam)
            if title == "Automatic Screenshotter":
                # print("Detaching and hiding the window now, on destroy.")
                self.previousLocationOfWindow = None
                self.timer.stop() if hasattr(self, 'timer') and self.timer else None
                self.app.hide()
            return True, 0
        return False, 0

    def check_window(self):
        window_handle = win32gui.FindWindow("TMainForm", "Automatic Screenshotter")
        if window_handle:
            auto_scrnshtr_window_rect = win32gui.GetWindowRect(window_handle)
            if auto_scrnshtr_window_rect != self.previousLocationOfWindow:
                self.previousLocationOfWindow = auto_scrnshtr_window_rect
                new_x = auto_scrnshtr_window_rect[0] - self.app.width() + 5
                
                self.app.move(new_x, auto_scrnshtr_window_rect[1])
                if not self.app.isVisible():
                    self.app.show()
            
            hwnd = win32gui.GetForegroundWindow()
            if win32gui.GetWindowText(hwnd) == "Automatic Screenshotter":
                # print(f"Automatic Screenshotter is focused.")
                if not self.isUploaderWindowJustAfterAutomaticScreenshotter():
                    self.bring_to_front("Screenshots to YouTube Uploader")

    def register_shell_hook_window(self):
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = win32gui.DefWindowProc
        wc.lpszClassName = 'ShellHookClass'
        wc.hInstance = win32gui.GetModuleHandle(None)
        class_atom = win32gui.RegisterClass(wc)
        self.hook_window = win32gui.CreateWindowEx(
            0, class_atom, 'ShellHookWindow', 0, 0, 0, 0, 0, 0, 0, None, None)
        if not RegisterShellHookWindow(self.hook_window):
            raise ctypes.WinError(ctypes.get_last_error())

        # Register message
        global WM_SHELLHOOKMESSAGE
        WM_SHELLHOOKMESSAGE = RegisterWindowMessage(b"SHELLHOOK")
        if not WM_SHELLHOOKMESSAGE:
            raise ctypes.WinError(ctypes.get_last_error())

        win32gui.SetWindowLong(
            self.hook_window, win32con.GWL_WNDPROC, win32gui.DefWindowProc)

    def isUploaderWindowJustAfterAutomaticScreenshotter(self):
        automaticScreenshotterWindowIndex = None
        uploaderWindowIndex = None
        isAutomaticScreenshotterWindowFound = False
        hwnd = win32gui.GetForegroundWindow()
        i = 0
        while hwnd and (automaticScreenshotterWindowIndex is None or uploaderWindowIndex is None):
            window_text = win32gui.GetWindowText(hwnd)
            # current_hwnd = hwnd
            hwnd = win32gui.GetWindow(hwnd, win32con.GW_HWNDNEXT)
            if window_text == "MSCTFIME UI" or window_text == "Default IME" or window_text.strip() == "" or window_text == "Browse Saved Screenshot Files" \
                or (isAutomaticScreenshotterWindowFound and window_text == "Automatic Screenshotter") or window_text.startswith("Automatic Screenshotter "):
                continue
            if window_text == "Automatic Screenshotter":
                # print(f"Found automatic screenshotter window at index {i}.")
                automaticScreenshotterWindowIndex = i
                isAutomaticScreenshotterWindowFound = True
            if window_text == "Screenshots to YouTube Uploader":
                # print(f"Found uploader window at index {i}.")
                uploaderWindowIndex = i
            # print(f"Z-Order {i}: {window_text}")
            i += 1
        if uploaderWindowIndex - automaticScreenshotterWindowIndex == 1:
            return True
        return False

    def bring_to_front(self, window_title):
        try:
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            # print(f"Current window title: {title}")
    
            handle = win32gui.FindWindow(None, window_title)
            if handle:
                # Simulate an ALT key press and release
                win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)  # ALT Key Down
                win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)  # ALT Key Up

                # Try to bring the window to the foreground
                win32gui.ShowWindow(handle, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(handle)
                # print(f"Window '{window_title}' brought to front successfully.")
            else:
                print(f"No window found with title '{window_title}'.")
                sys.exit(1)
        except pywintypes.error as e:
            print(f"Failed to bring window to front: {e}")
            sys.exit(1)