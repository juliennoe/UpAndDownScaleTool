#!/usr/bin/env python3
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image

class UpscaleApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Real-ESRGAN Batch Upscaler/Downscaler")
        self.resizable(False, False)

        # Chemin du dossier courant (pour l'import d'inference_realesrgan)
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        if self.script_dir not in sys.path:
            sys.path.insert(0, self.script_dir)

        # État interne
        self.input_files = []
        self.output_folder = ""
        self.source_mode = tk.StringVar(value="File")   # "File" ou "Folder"
        self.operation   = tk.StringVar(value="Upscale")# "Upscale" ou "Downscale"
        self.scale       = tk.StringVar(value="2")      # "2" ou "4"

        # Construction de l'UI
        self._build_ui()
        self.after(0, self._adjust_window)

    def _build_ui(self):
        # Ligne 1: choix File/Folder
        frm1 = ttk.Frame(self)
        frm1.grid(row=0, column=0, padx=10, pady=(10,5), sticky="ew")
        ttk.Label(frm1, text="1️⃣ Input Type:").pack(side='left')
        ttk.Combobox(frm1, textvariable=self.source_mode,
                     values=("File","Folder"), state="readonly", width=10
        ).pack(side='left', padx=5)

        # Sélecteur d'input
        ttk.Button(self, text="2️⃣ Select...", command=self._select_input
        ).grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.input_label = ttk.Label(self, text="No input selected", wraplength=400)
        self.input_label.grid(row=2, column=0, padx=10, pady=(0,10))

        # Sélecteur d'output folder
        ttk.Button(self, text="3️⃣ Choose Output Folder", command=self._select_output
        ).grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        self.output_label = ttk.Label(self, text="No output folder selected", wraplength=400)
        self.output_label.grid(row=4, column=0, padx=10, pady=(0,10))

        # Radio Upscale / Downscale
        frm2 = ttk.Frame(self)
        frm2.grid(row=5, column=0, padx=10, pady=5, sticky="ew")
        ttk.Label(frm2, text="4️⃣ Operation:").pack(side='left')
        ttk.Radiobutton(frm2, text="Upscale",   variable=self.operation, value="Upscale"
        ).pack(side='left', padx=5)
        ttk.Radiobutton(frm2, text="Downscale", variable=self.operation, value="Downscale"
        ).pack(side='left')

        # Choix du scale
        frm3 = ttk.Frame(self)
        frm3.grid(row=6, column=0, padx=10, pady=(0,10), sticky="ew")
        ttk.Label(frm3, text="5️⃣ Scale:").pack(side='left')
        ttk.Combobox(frm3, textvariable=self.scale,
                     values=("2","4"), state="readonly", width=5
        ).pack(side='left', padx=5)

        # Barre de progression
        self.progress = ttk.Progressbar(self, orient='horizontal', length=400, mode='determinate')
        self.progress.grid(row=7, column=0, padx=10, pady=5)

        # Bouton Run
        ttk.Button(self, text="6️⃣ Run", command=self._run
        ).grid(row=8, column=0, padx=10, pady=(0,10), sticky="ew")

    def _adjust_window(self):
        self.update_idletasks()
        self.geometry(f"{self.winfo_reqwidth()}x{self.winfo_reqheight()}")

    def _select_input(self):
        if self.source_mode.get() == "File":
            path = filedialog.askopenfilename(title="Select PNG",
                                              filetypes=[("PNG files","*.png")])
            if path:
                self.input_files = [path]
                self.input_label.config(text=os.path.basename(path))
        else:
            folder = filedialog.askdirectory(title="Select Folder with PNGs")
            if folder:
                pics = [os.path.join(folder, f) for f in os.listdir(folder)
                        if f.lower().endswith('.png')]
                if pics:
                    self.input_files = pics
                    self.input_label.config(
                        text=f"{len(pics)} file(s) in {os.path.basename(folder)}"
                    )
                else:
                    messagebox.showwarning("No PNG", "No PNG files found in folder.")

    def _select_output(self):
        folder = filedialog.askdirectory(title="Choose Output Folder")
        if folder:
            self.output_folder = folder
            self.output_label.config(text=os.path.basename(folder))

    def _run(self):
        # Vérifications
        if not self.input_files:
            return messagebox.showerror("Error", "No input selected.")
        if not self.output_folder:
            return messagebox.showerror("Error", "No output folder selected.")

        # Lazy import
        try:
            from inference_realesrgan import main as inference_main
        except Exception as imp_err:
            return messagebox.showerror("Import Error", f"Cannot import inference:\n{imp_err}")

        op     = self.operation.get()
        factor = int(self.scale.get())
        total  = len(self.input_files)
        self.progress.config(maximum=total, value=0)

        # Sauvegarde argv
        argv_backup = sys.argv[:]

        for idx, inp in enumerate(self.input_files, start=1):
            self.input_label.config(text=f"[{idx}/{total}] {op} {os.path.basename(inp)} x{factor}")
            self.update_idletasks()

            if op == "Upscale":
                # Prépare les arguments comme en CLI
                sys.argv = [
                    sys.argv[0],
                    "-i", inp,
                    "-n", f"RealESRGAN_x{factor}plus",
                    "--outscale", str(factor),
                    "--fp32",
                    "-o", self.output_folder
                ]
                try:
                    inference_main()
                except Exception as inf_err:
                    messagebox.showerror("Inference Error", f"Error during inference:\n{inf_err}")
                finally:
                    sys.argv = argv_backup
            else:
                # Downscale intégral
                img = Image.open(inp)
                w, h = img.size
                new = img.resize((w//factor, h//factor), Image.LANCZOS)
                base, ext = os.path.splitext(os.path.basename(inp))
                outp = os.path.join(self.output_folder, f"{base}_downx{factor}{ext}")
                new.save(outp)

            self.progress.step()

        messagebox.showinfo("Done", f"✅ {op} completed!\nResults in: {self.output_folder}")

        # Reset UI
        self.input_files = []
        self.output_folder = ""
        self.source_mode.set("File")
        self.operation.set("Upscale")
        self.scale.set("2")
        self.input_label.config(text="No input selected")
        self.output_label.config(text="No output folder selected")
        self.progress.config(value=0)


if __name__ == "__main__":
    UpscaleApp().mainloop()
