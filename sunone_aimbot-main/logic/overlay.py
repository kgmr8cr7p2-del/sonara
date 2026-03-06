from tkinter import Canvas
import tkinter as tk
import tkinter.font as tkFont
import threading
import queue

try:
    import win32con
    import win32gui
except Exception:
    win32con = None
    win32gui = None

from logic.config_watcher import cfg

class Overlay:
    def __init__(self):
        self.queue = queue.Queue()
        self.thread = None
        self.square_id = None
        self.overlay_offset_x = 0
        self.overlay_offset_y = 0
        
        # Skip frames so that the figures do not interfere with the detector ¯\_(ツ)_/¯
        self.frame_skip_counter = 0

    def run(self, width, height):
        if cfg.show_overlay:
            self.root = tk.Tk()
            self.root.overrideredirect(True)

            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()

            self.overlay_offset_x = (screen_width - width) // 2
            self.overlay_offset_y = (screen_height - height) // 2

            # Fullscreen transparent overlay so drawing is on top of the screen, not in a detached mini-window.
            self.root.geometry(f"{screen_width}x{screen_height}+0+0")
            self.root.attributes('-topmost', True)
            self.root.attributes('-transparentcolor', 'black')

            self.canvas = Canvas(self.root, bg='black', highlightthickness=0, cursor="none")
            self.canvas.pack(fill=tk.BOTH, expand=True)

            self.root.bind("<Button-1>", lambda e: "break")
            self.root.bind("<Button-2>", lambda e: "break")
            self.root.bind("<Button-3>", lambda e: "break")
            self.root.bind("<Motion>", lambda e: "break")
            self.root.bind("<Key>", lambda e: "break")
            self.root.bind("<Enter>", lambda e: "break")
            self.root.bind("<Leave>", lambda e: "break")
            self.root.bind("<FocusIn>", lambda e: "break")
            self.root.bind("<FocusOut>", lambda e: "break")
            
            self.canvas.bind("<Button-1>", lambda e: "break")
            self.canvas.bind("<Button-2>", lambda e: "break")
            self.canvas.bind("<Button-3>", lambda e: "break")
            self.canvas.bind("<Motion>", lambda e: "break")
            self.canvas.bind("<Key>", lambda e: "break")
            self.canvas.bind("<Enter>", lambda e: "break")
            self.canvas.bind("<Leave>", lambda e: "break")
            self.canvas.bind("<FocusIn>", lambda e: "break")
            self.canvas.bind("<FocusOut>", lambda e: "break")

            if cfg.overlay_show_borders:
                if cfg.circle_capture:
                    self.square_id = self.canvas.create_oval(self.overlay_offset_x, self.overlay_offset_y, self.overlay_offset_x + width, self.overlay_offset_y + height, outline='red', width=2)
                else:
                    self.square_id = self.canvas.create_rectangle(self.overlay_offset_x, self.overlay_offset_y, self.overlay_offset_x + width, self.overlay_offset_y + height, outline='red', width=2)

            # Try to make overlay click-through on Windows.
            if win32gui is not None and win32con is not None:
                try:
                    hwnd = self.root.winfo_id()
                    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                    ex_style |= win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_TOPMOST
                    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)
                except Exception:
                    pass

            self.process_queue()
            self.root.mainloop()

    def process_queue(self):
        self.frame_skip_counter += 1
        if self.frame_skip_counter % 3 == 0:
            if not self.queue.empty():
                for item in self.canvas.find_all():
                    if item != self.square_id:
                        self.canvas.delete(item)
                while not self.queue.empty():
                    command, args = self.queue.get()
                    command(*args)
            else:
                for item in self.canvas.find_all():
                    if item != self.square_id:
                        self.canvas.delete(item)
        self.root.after(2, self.process_queue)

    def draw_square(self, x1, y1, x2, y2, color='white', size=1):
        self.queue.put((self._draw_square, (x1, y1, x2, y2, color, size)))

    def _draw_square(self, x1, y1, x2, y2, color='white', size=1):
        self.canvas.create_rectangle(x1 + self.overlay_offset_x, y1 + self.overlay_offset_y, x2 + self.overlay_offset_x, y2 + self.overlay_offset_y, outline=color, width=size)

    def draw_oval(self, x1, y1, x2, y2, color='white', size=1):
        self.queue.put((self._draw_oval, (x1, y1, x2, y2, color, size)))

    def _draw_oval(self, x1, y1, x2, y2, color='white', size=1):
        self.canvas.create_oval(x1 + self.overlay_offset_x, y1 + self.overlay_offset_y, x2 + self.overlay_offset_x, y2 + self.overlay_offset_y, outline=color, width=size)

    def draw_line(self, x1, y1, x2, y2, color='white', size=1):
        self.queue.put((self._draw_line, (x1, y1, x2, y2, color, size)))

    def _draw_line(self, x1, y1, x2, y2, color='white', size=1):
        self.canvas.create_line(x1 + self.overlay_offset_x, y1 + self.overlay_offset_y, x2 + self.overlay_offset_x, y2 + self.overlay_offset_y, fill=color, width=size)

    def draw_point(self, x, y, color='white', size=1):
        self.queue.put((self._draw_point, (x, y, color, size)))

    def _draw_point(self, x, y, color='white', size=1):
        self.canvas.create_oval(x + self.overlay_offset_x - size, y + self.overlay_offset_y - size, x + self.overlay_offset_x + size, y + self.overlay_offset_y + size, fill=color, outline=color)

    def draw_text(self, x, y, text, size=12, color='white'):
        self.queue.put((self._draw_text, (x, y, text, size, color)))

    def _draw_text(self, x, y, text, size, color):
        self.canvas.create_text(x + self.overlay_offset_x, y + self.overlay_offset_y, text=text, font=('Arial', size), fill=color, state='')

    def show(self, width, height):
        if self.thread is None:
            self.thread = threading.Thread(target=self.run, args=(width, height), daemon=True, name="Overlay")
            self.thread.start()

overlay = Overlay()