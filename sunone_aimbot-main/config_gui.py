import configparser
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.ini"

OPTION_DESCRIPTIONS_RU = {
    # Detection window
    "detection_window_width": "Ширина области (в пикселях), из которой ИИ анализирует кадр. Больше значение = больше зона обзора, но ниже производительность.",
    "detection_window_height": "Высота области (в пикселях), из которой ИИ анализирует кадр. Увеличение повышает нагрузку на систему.",
    "circle_capture": "Если включено, область захвата становится круглой. Уменьшает лишние объекты по краям, но может отрезать полезные цели.",

    # Capture Methods
    "capture_fps": "Частота захвата кадров. Чем выше, тем быстрее реакция, но сильнее нагрузка на CPU/GPU.",
    "bettercam_capture": "Использовать Bettercam для захвата экрана. Рекомендуется только если драйвер и система поддерживают этот метод стабильно.",
    "bettercam_monitor_id": "Номер монитора для Bettercam. Меняйте, если игра открыта на другом экране.",
    "bettercam_gpu_id": "ID видеокарты для Bettercam. Актуально для систем с несколькими GPU.",
    "obs_capture": "Захват через виртуальную камеру OBS. Удобно, если поток уже обрабатывается в OBS.",
    "obs_camera_id": "Идентификатор камеры OBS (обычно auto/0/1...). Неправильный ID = чёрный кадр или отсутствие захвата.",
    "mss_capture": "Захват через MSS (обычно самый универсальный метод). Подходит как базовый вариант без дополнительных зависимостей.",

    # Aim
    "body_y_offset": "Вертикальное смещение точки прицеливания по телу. Положительные/отрицательные значения двигают прицел выше/ниже.",
    "hideout_targets": "Игнорировать/учитывать цели в специфичных ситуациях (например, тренировочные/скрытые сценарии).",
    "disable_headshot": "Отключает прицеливание в голову. Полезно для более стабильного прицеливания в корпус.",
    "disable_prediction": "Отключить предсказание движения цели. Если выключить предикт, при резких движениях может быть больше промахов.",
    "prediction_interval": "Интервал/сила предсказания движения. Больше значение = агрессивнее упреждение.",
    "third_person": "Режим под игры с видом от 3-го лица. Меняет логику выбора точки и поведения прицеливания.",

    # Hotkeys
    "hotkey_targeting": "Кнопки удержания/активации наведения. Можно задать несколько через запятую.",
    "hotkey_exit": "Клавиша быстрого выхода из программы.",
    "hotkey_pause": "Клавиша паузы/возобновления работы.",
    "hotkey_reload_config": "Клавиша перезагрузки конфига без перезапуска.",

    # Mouse
    "mouse_dpi": "DPI мыши. Используется для расчёта корректной скорости перемещения прицела.",
    "mouse_sensitivity": "Игровая чувствительность. Влияет на масштаб движения и точность перевода.",
    "mouse_fov_width": "Ширина зоны захвата цели для мыши (FOV). Чем больше, тем дальше от центра будут подхватываться цели.",
    "mouse_fov_height": "Высота зоны FOV для мыши. Настраивается совместно с шириной.",
    "mouse_min_speed_multiplier": "Минимальный множитель скорости движения мыши. Слишком маленький = «вялое» наведение.",
    "mouse_max_speed_multiplier": "Максимальный множитель скорости движения. Слишком большой может дать рывки/перелёт.",
    "mouse_lock_target": "Фиксация на выбранной цели. Уменьшает перескакивания между противниками.",
    "mouse_auto_aim": "Автоматическое наведение без постоянного удержания клавиши (в зависимости от логики остальной конфигурации).",
    "mouse_ghub": "Использовать управление мышью через Logitech G Hub драйверный путь.",
    "mouse_rzr": "Использовать Razer-метод управления мышью (если поддерживается окружением).",

    # Shooting
    "auto_shoot": "Автоматический выстрел при уверенном захвате цели.",
    "triggerbot": "Стреляет, когда цель в зоне перекрестия/условии триггера.",
    "force_click": "Принудительный клик-режим выстрела. Может конфликтовать с отдельными играми/античитом.",
    "bscope_multiplier": "Множитель для зоны/логики bScope. Влияет на чувствительность условия стрельбы.",

    # Arduino
    "arduino_move": "Перемещение мыши через Arduino HID. Часто используется как альтернативный метод ввода.",
    "arduino_shoot": "Клик/выстрел через Arduino HID.",
    "arduino_port": "COM-порт Arduino (например, COM3) или auto.",
    "arduino_baudrate": "Скорость последовательного порта Arduino. Должна совпадать с прошивкой.",
    "arduino_16_bit_mouse": "Режим 16-битного позиционирования мыши для более точного движения (если поддерживается прошивкой).",

    # AI
    "ai_model_name": "Имя файла модели в папке models. Неверное имя = модель не загрузится.",
    "ai_model_image_size": "Размер входного изображения в модель. Больше размер = выше точность на дальних целях, но ниже FPS.",
    "ai_conf": "Порог уверенности детектора (confidence). Низкий порог = больше ложных срабатываний.",
    "ai_device": "Устройство инференса: CPU/GPU. При отсутствии CUDA автоматически может использоваться CPU.",
    "ai_enable_amd": "Флаг включения AMD-режима (если доступна соответствующая поддержка окружения).",
    "disable_tracker": "Отключить трекинг целей между кадрами. Может повысить FPS, но ухудшить стабильность сопровождения.",

    # Overlay
    "show_overlay": "Включить оверлей поверх игры/экрана.",
    "overlay_show_borders": "Показывать границы области захвата в оверлее.",
    "overlay_show_boxes": "Показывать боксы обнаруженных целей.",
    "overlay_show_target_line": "Линия к текущей цели.",
    "overlay_show_target_prediction_line": "Линия предсказания движения цели.",
    "overlay_show_labels": "Подписи классов/меток в оверлее.",
    "overlay_show_conf": "Показывать confidence у найденных объектов.",

    # Debug window
    "show_window": "Показать debug-окно с видеопотоком и диагностикой.",
    "show_detection_speed": "Показывать скорость детекции.",
    "show_window_fps": "Показывать FPS debug-окна.",
    "show_boxes": "Рисовать боксы целей в debug-окне.",
    "show_labels": "Показывать подписи целей в debug-окне.",
    "show_conf": "Показывать confidence в debug-окне.",
    "show_target_line": "Показывать линию к цели в debug-окне.",
    "show_target_prediction_line": "Показывать линию предикта в debug-окне.",
    "show_bscope_box": "Показывать bScope-зону в debug-окне.",
    "show_history_points": "Показывать историю точек цели (трек движения).",
    "debug_window_always_on_top": "Окно диагностики всегда поверх остальных окон.",
    "spawn_window_pos_x": "Позиция debug-окна по X при старте.",
    "spawn_window_pos_y": "Позиция debug-окна по Y при старте.",
    "debug_window_scale_percent": "Масштаб debug-окна в процентах.",
    "debug_window_screenshot_key": "Горячая клавиша для скриншота debug-окна.",
}


class ToolTip:
    def __init__(self, widget, text: str):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, _event=None):
        if self.tip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 16
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6

        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = ttk.Label(
            tw,
            text=self.text,
            justify="left",
            background="#fffce0",
            relief="solid",
            borderwidth=1,
            padding=6,
            wraplength=520,
        )
        label.pack()

    def hide(self, _event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


class ConfigEditorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Sunone Aimbot - Полная GUI настройка")
        self.root.geometry("1120x760")

        self.config = configparser.ConfigParser()
        self.variables: dict[tuple[str, str], tk.Variable] = {}
        self.tooltips: list[ToolTip] = []

        self.aimbot_process: subprocess.Popen | None = None
        self.helper_process: subprocess.Popen | None = None

        self._build_layout()
        self.reload_config()

    def _build_layout(self):
        toolbar = ttk.Frame(self.root, padding=8)
        toolbar.pack(fill="x")

        ttk.Button(toolbar, text="Reload", command=self.reload_config).pack(side="left")
        ttk.Button(toolbar, text="Save", command=self.save_config).pack(side="left", padx=6)
        ttk.Button(toolbar, text="Запустить Aimbot", command=self.start_aimbot).pack(side="left", padx=6)
        ttk.Button(toolbar, text="Остановить Aimbot", command=self.stop_aimbot).pack(side="left", padx=6)
        ttk.Button(toolbar, text="Запустить Helper GUI", command=self.start_helper_gui).pack(side="left", padx=6)
        ttk.Button(toolbar, text="Exit", command=self.on_exit).pack(side="right")

        self.status_var = tk.StringVar(value="Готово")
        ttk.Label(toolbar, textvariable=self.status_var).pack(side="right", padx=8)

        content = ttk.Frame(self.root)
        content.pack(fill="both", expand=True)

        self.notebook = ttk.Notebook(content)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def _parse_value(self, raw_value: str):
        value = raw_value.strip()
        low = value.lower()

        if low in {"true", "false"}:
            return "bool", low == "true"

        try:
            if any(ch in low for ch in [".", "e"]):
                return "float", float(value)
            return "int", int(value)
        except ValueError:
            return "string", value

    def _description_for(self, option: str):
        return OPTION_DESCRIPTIONS_RU.get(
            option.lower(),
            "Параметр конфигурации. Наведите и изменяйте аккуратно: неверные значения могут ухудшить точность, скорость или запуск программы.",
        )

    def _build_section_tab(self, section: str):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=section)

        canvas = tk.Canvas(tab, highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        frame = ttk.Frame(canvas)

        frame.bind("<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for row, (option, raw_value) in enumerate(self.config.items(section)):
            value_type, parsed_value = self._parse_value(raw_value)

            label = ttk.Label(frame, text=option, width=36)
            label.grid(row=row, column=0, sticky="w", padx=8, pady=6)
            self.tooltips.append(ToolTip(label, self._description_for(option)))

            if value_type == "bool":
                var = tk.BooleanVar(value=parsed_value)
                widget = ttk.Checkbutton(frame, variable=var)
            elif value_type == "int":
                var = tk.IntVar(value=parsed_value)
                widget = ttk.Spinbox(frame, from_=-10_000_000, to=10_000_000, textvariable=var, width=24)
            elif value_type == "float":
                var = tk.DoubleVar(value=parsed_value)
                widget = ttk.Entry(frame, textvariable=var, width=30)
            else:
                var = tk.StringVar(value=parsed_value)
                widget = ttk.Entry(frame, textvariable=var, width=44)

            widget.grid(row=row, column=1, sticky="w", padx=8, pady=6)
            self.tooltips.append(ToolTip(widget, self._description_for(option)))
            self.variables[(section, option)] = var

        frame.grid_columnconfigure(1, weight=1)

    def reload_config(self):
        if not CONFIG_PATH.exists():
            messagebox.showerror("Ошибка", f"Не найден config.ini: {CONFIG_PATH}")
            return

        self.config.read(CONFIG_PATH, encoding="utf-8")
        self.variables.clear()
        self.tooltips.clear()

        for tab_id in self.notebook.tabs():
            self.notebook.forget(tab_id)

        for section in self.config.sections():
            self._build_section_tab(section)

        self.status_var.set(f"Загружен: {CONFIG_PATH.name}")

    def save_config(self):
        try:
            for (section, option), var in self.variables.items():
                value = var.get()
                if isinstance(var, tk.BooleanVar):
                    self.config.set(section, option, "True" if value else "False")
                else:
                    self.config.set(section, option, str(value))

            with open(CONFIG_PATH, "w", encoding="utf-8") as config_file:
                self.config.write(config_file)

            self.status_var.set("Сохранено")
            messagebox.showinfo("Успех", "Конфигурация сохранена успешно.")
        except Exception as exc:
            messagebox.showerror("Ошибка сохранения", str(exc))

    def start_aimbot(self):
        if self.aimbot_process and self.aimbot_process.poll() is None:
            self.status_var.set("Aimbot уже запущен")
            return
        self.save_config()
        self.aimbot_process = subprocess.Popen([sys.executable, "run.py"], cwd=BASE_DIR)
        self.status_var.set("Aimbot запущен")

    def stop_aimbot(self):
        if not self.aimbot_process or self.aimbot_process.poll() is not None:
            self.status_var.set("Aimbot не запущен")
            return
        self.aimbot_process.terminate()
        self.status_var.set("Aimbot остановлен")

    def start_helper_gui(self):
        if self.helper_process and self.helper_process.poll() is None:
            self.status_var.set("Helper GUI уже запущен")
            return
        self.helper_process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "helper.py"], cwd=BASE_DIR)
        self.status_var.set("Helper GUI запущен")

    def on_exit(self):
        if self.aimbot_process and self.aimbot_process.poll() is None:
            self.aimbot_process.terminate()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = ConfigEditorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
