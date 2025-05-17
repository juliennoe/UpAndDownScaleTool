#!/usr/bin/env python3
import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image

class UpscaleApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Real-ESRGAN Batch Upscaler/Downscaler")
        self.resizable(False, False)
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.script_path = os.path.join(self.script_dir, "inference_realesrgan.py")

        # State variables
        self.input_files = []
        self.output_folder = ""
        self.source_mode = tk.StringVar(value="File")  # File or Folder
        self.operation = tk.StringVar(value="Upscale")  # Upscale or Downscale
        self.scale = tk.StringVar(value="2")           # Default x2

        # Build UI
        self.create_widgets()
        # Adjust window size after widgets are laid out
        self.after(0, self.adjust_window)

    def create_widgets(self):
        # Input Type
        mode_frame = ttk.Frame(self)
        mode_frame.grid(row=0, column=0, padx=10, pady=(10,5), sticky="ew")
        ttk.Label(mode_frame, text="1️⃣ Input Type:").pack(side='left', padx=(0,5))
        mode_combo = ttk.Combobox(mode_frame, textvariable=self.source_mode,
                                  values=("File", "Folder"), state="readonly", width=10)
        mode_combo.pack(side='left')

        # Select input
        btn_select = ttk.Button(self, text="2️⃣ Select...", command=self.select_input)
        btn_select.grid(row=1, column=0, padx=10, pady=(0,5), sticky="ew")
        self.input_label = ttk.Label(self, text="No input selected", wraplength=400)
        self.input_label.grid(row=2, column=0, padx=10, pady=(0,10))

        # Select output folder
        btn_output = ttk.Button(self, text="3️⃣ Choose Output Folder", command=self.select_output)
        btn_output.grid(row=3, column=0, padx=10, pady=(0,5), sticky="ew")
        self.output_label = ttk.Label(self, text="No output folder selected", wraplength=400)
        self.output_label.grid(row=4, column=0, padx=10, pady=(0,10))

        # Operation
        op_frame = ttk.Frame(self)
        op_frame.grid(row=5, column=0, padx=10, pady=(0,5), sticky="ew")
        ttk.Label(op_frame, text="4️⃣ Operation:").pack(side='left', padx=(0,5))
        ttk.Radiobutton(op_frame, text="Upscale", variable=self.operation,
                        value="Upscale").pack(side='left', padx=5)
        ttk.Radiobutton(op_frame, text="Downscale", variable=self.operation,
                        value="Downscale").pack(side='left', padx=5)

        # Scale factor
        scale_frame = ttk.Frame(self)
        scale_frame.grid(row=6, column=0, padx=10, pady=(0,10), sticky="ew")
        ttk.Label(scale_frame, text="5️⃣ Scale:").pack(side='left', padx=(0,5))
        scale_combo = ttk.Combobox(scale_frame, textvariable=self.scale,
                                   values=("2", "4"), state="readonly", width=5)
        scale_combo.pack(side='left')

        # Progress bar
        self.progress = ttk.Progressbar(self, orient='horizontal', length=400, mode='determinate')
        self.progress.grid(row=7, column=0, padx=10, pady=(0,5))

        # Run button
        btn_run = ttk.Button(self, text="6️⃣ Run", command=self.run_process)
        btn_run.grid(row=8, column=0, padx=10, pady=(0,10), sticky="ew")

    def adjust_window(self):
        # Resize window to fit content
        self.update_idletasks()
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        self.geometry(f"{width}x{height}")

    def select_input(self):
        mode = self.source_mode.get()
        if mode == "File":
            path = filedialog.askopenfilename(title="Select PNG Image",
                                              filetypes=[("PNG files", "*.png")])
            if path:
                self.input_files = [path]
                self.input_label.config(text=os.path.basename(path))
        else:
            folder = filedialog.askdirectory(title="Select Folder with PNGs")
            if folder:
                files = [os.path.join(folder, f) for f in os.listdir(folder)
                         if f.lower().endswith('.png')]
                if files:
                    self.input_files = files
                    self.input_label.config(text=f"{len(files)} file(s) in {os.path.basename(folder)}")
                else:
                    messagebox.showwarning("No PNG", "No PNG files found in the folder.")

    def select_output(self):
        folder = filedialog.askdirectory(title="Choose Output Folder")
        if folder:
            self.output_folder = folder
            self.output_label.config(text=os.path.basename(folder))

    def run_process(self):
        if not self.input_files:
            messagebox.showerror("Error", "No input selected.")
            return
        if not self.output_folder:
            messagebox.showerror("Error", "No output folder selected.")
            return

        op = self.operation.get()
        factor = int(self.scale.get())
        count = len(self.input_files)
        self.progress.config(maximum=count, value=0)

        for i, input_path in enumerate(self.input_files, 1):
            filename = os.path.basename(input_path)
            self.input_label.config(text=f"[{i}/{count}] {op} {filename} x{factor}")
            self.update_idletasks()

            if op == "Upscale":
                model_name = f"RealESRGAN_x{factor}plus"
                model_path = os.path.join(self.script_dir, "weights", f"{model_name}.pth")
                if not os.path.exists(model_path):
                    messagebox.showerror("Model Not Found", f"{model_name} missing:\n{model_path}")
                    return
                cmd = [sys.executable, self.script_path,
                       "-i", input_path,
                       "-n", model_name,
                       "--outscale", str(factor),
                       "--fp32",
                       "-o", self.output_folder]
                subprocess.run(cmd, cwd=self.script_dir)
            else:
                img = Image.open(input_path)
                new_size = (img.width // factor, img.height // factor)
                down = img.resize(new_size, Image.LANCZOS)
                base, ext = os.path.splitext(os.path.basename(input_path))
                out_path = os.path.join(self.output_folder, f"{base}_downx{factor}{ext}")
                down.save(out_path)

            self.progress.step()

        messagebox.showinfo("Done", f"✅ {op} completed!\nResults in: {self.output_folder}")
        # Reset interface
        self.input_label.config(text="No input selected")
        self.source_mode.set("File")
        self.input_files = []
        self.output_folder = ""
        self.output_label.config(text="No output folder selected")
        self.operation.set("Upscale")
        self.scale.set("2")
        self.progress.config(value=0)

if __name__ == "__main__":
    app = UpscaleApp()
    app.mainloop()
