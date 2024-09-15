import tkinter as tk
from time import strftime
from tkinter import font as tkfont
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import colorsys
from pynput import keyboard

class FancyClock(tk.Tk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.attributes('-alpha', 0.7)
        self.configure(bg='black')

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = screen_width - 280
        y = 50
        self.geometry(f'260x180+{x}+{y}')  # Increased height to accommodate the cat image

        self.create_widgets()
        self.bind_events()
        self.setup_volume_control()
        self.setup_global_hotkeys()        
        self.animation_frame = 0

    def create_widgets(self):
        self.canvas = tk.Canvas(self, bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Create colorful glowing border
        self.border_items = self.create_glow()

        self.frame = tk.Frame(self.canvas, bg='black')
        self.canvas.create_window(130, 90, window=self.frame)  # Adjusted y-position

        self.time_font = tkfont.Font(family='Helvetica', size=36, weight='bold')
        self.date_font = tkfont.Font(family='Helvetica', size=14)
        self.volume_font = tkfont.Font(family='Helvetica', size=12)

        self.time_label = tk.Label(self.frame, font=self.time_font, bg='black', fg='white')
        self.time_label.pack(pady=(10, 0))

        self.date_label = tk.Label(self.frame, font=self.date_font, bg='black', fg='white')
        self.date_label.pack()

        self.volume_label = tk.Label(self.frame, font=self.volume_font, bg='black', fg='white')
        self.volume_label.pack(pady=(5, 0))

        close_button = tk.Button(self, text='×', command=self.quit, bg='black', fg='white', 
                                 font=('Arial', 16), bd=0, highlightthickness=0)
        close_button.place(x=230, y=5)

    def create_glow(self):
        border_items = []
        width, height = 258, 178  # Adjusted height for the new window size
        for i in range(width * 2 + height * 2):
            if i < width:
                x1, y1 = i, 0
                x2, y2 = i + 1, 0
            elif i < width + height:
                x1, y1 = width, i - width
                x2, y2 = width, i - width + 1
            elif i < width * 2 + height:
                x1, y1 = width - (i - width - height), height
                x2, y2 = width - (i - width - height) - 1, height
            else:
                x1, y1 = 0, height - (i - width * 2 - height)
                x2, y2 = 0, height - (i - width * 2 - height) - 1
            
            item = self.canvas.create_line(x1 + 1, y1 + 1, x2 + 1, y2 + 1, fill='white', width=2)
            border_items.append(item)
        return border_items

    def animate_border(self):
        for i, item in enumerate(self.border_items):
            angle = (i + self.animation_frame) / len(self.border_items)
            r, g, b = [int(x * 255) for x in colorsys.hsv_to_rgb(angle, 1.0, 1.0)]
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.canvas.itemconfig(item, fill=color)
        self.animation_frame = (self.animation_frame + 1) % len(self.border_items)
        self.after(50, self.animate_border)

    def bind_events(self):
        self.bind('<ButtonPress-1>', self.start_move)
        self.bind('<ButtonRelease-1>', self.stop_move)
        self.bind('<B1-Motion>', self.do_move)
        self.bind('<F10>', self.toggle_mute)
        self.bind('<F12>', self.increase_volume)
        self.bind('<F11>', self.decrease_volume)

    def setup_volume_control(self):
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))
        self.update_volume_display()

    def setup_global_hotkeys(self):
        self.listener = keyboard.GlobalHotKeys({
            '<f10>': self.toggle_mute,
            '<f11>': self.decrease_volume,
            '<f12>': self.increase_volume
        })
        self.listener.start()

    def toggle_mute(self):
        mute_state = self.volume.GetMute()
        self.volume.SetMute(not mute_state, None)
        self.update_volume_display()

    def increase_volume(self):
        current_volume = self.volume.GetMasterVolumeLevelScalar()
        new_volume = min(1.0, current_volume + 0.05)
        self.volume.SetMasterVolumeLevelScalar(new_volume, None)
        self.update_volume_display()

    def decrease_volume(self):
        current_volume = self.volume.GetMasterVolumeLevelScalar()
        new_volume = max(0.0, current_volume - 0.05)
        self.volume.SetMasterVolumeLevelScalar(new_volume, None)
        self.update_volume_display()

    def update_volume_display(self):
        current_volume = self.volume.GetMasterVolumeLevelScalar()
        volume_percentage = int(current_volume * 100)
        mute_state = self.volume.GetMute()
        if mute_state:
            self.volume_label.config(text="Volume: Muted")
        else:
            self.volume_label.config(text=f"Volume: {volume_percentage}%")

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def update_time(self):
        time_string = strftime('%H:%M:%S')
        date_string = strftime('%B %d, %Y')
        self.time_label.config(text=time_string)
        self.date_label.config(text=date_string)
        self.after(1000, self.update_time)

    def run(self):
        self.update_time()
        self.animate_border()
        self.mainloop()

if __name__ == "__main__":
    clock = FancyClock()
    clock.run()