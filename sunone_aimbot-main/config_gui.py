import configparser
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox

CONFIG_PATH = Path(__file__).resolve().parent / "config.ini"


class ConfigEditorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Sunone Aimbot - Config GUI")
        self.root.geometry("980x720")

        self.config = configparser.ConfigParser()
        self.variables: dict[tuple[str, str], tk.Variable] = {}

        self._build_layout()
        self.reload_config()

    def _build_layout(self):
        toolbar = ttk.Frame(self.root, padding=8)
        toolbar.pack(fill="x")

        ttk.Button(toolbar, text="Reload", command=self.reload_config).pack(side="left")
        ttk.Button(toolbar, text="Save", command=self.save_config).pack(side="left", padx=8)
        ttk.Button(toolbar, text="Exit", command=self.root.destroy).pack(side="right")

        self.status_var = tk.StringVar(value="Ready")
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

    def _build_section_tab(self, section: str):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=section)

        canvas = tk.Canvas(tab, highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        frame = ttk.Frame(canvas)

        frame.bind(
            "<Configure>",
            lambda _: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for row, (option, raw_value) in enumerate(self.config.items(section)):
            value_type, parsed_value = self._parse_value(raw_value)

            ttk.Label(frame, text=option, width=35).grid(row=row, column=0, sticky="w", padx=8, pady=6)

            if value_type == "bool":
                var = tk.BooleanVar(value=parsed_value)
                widget = ttk.Checkbutton(frame, variable=var)
                widget.grid(row=row, column=1, sticky="w", padx=8, pady=6)
            elif value_type == "int":
                var = tk.IntVar(value=parsed_value)
                widget = ttk.Spinbox(frame, from_=-10_000_000, to=10_000_000, textvariable=var, width=24)
                widget.grid(row=row, column=1, sticky="w", padx=8, pady=6)
            elif value_type == "float":
                var = tk.DoubleVar(value=parsed_value)
                widget = ttk.Entry(frame, textvariable=var, width=28)
                widget.grid(row=row, column=1, sticky="w", padx=8, pady=6)
            else:
                var = tk.StringVar(value=parsed_value)
                widget = ttk.Entry(frame, textvariable=var, width=42)
                widget.grid(row=row, column=1, sticky="w", padx=8, pady=6)

            self.variables[(section, option)] = var

        frame.grid_columnconfigure(1, weight=1)

    def reload_config(self):
        if not CONFIG_PATH.exists():
            messagebox.showerror("Error", f"Config file not found: {CONFIG_PATH}")
            return

        self.config.read(CONFIG_PATH, encoding="utf-8")
        self.variables.clear()

        for tab_id in self.notebook.tabs():
            self.notebook.forget(tab_id)

        for section in self.config.sections():
            self._build_section_tab(section)

        self.status_var.set(f"Loaded: {CONFIG_PATH.name}")

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

            self.status_var.set("Saved")
            messagebox.showinfo("Success", "Config saved successfully.")
        except Exception as exc:
            messagebox.showerror("Save error", str(exc))


def main():
    root = tk.Tk()
    app = ConfigEditorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
