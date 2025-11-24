import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from simulation_engine import SimulationEngine
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("OS Simulator - Proyecto Final")
        self.geometry("1200x800")

        self.engine = SimulationEngine()
        self.data_loaded = False

        # Layout de Grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()
        self.create_main_view()

    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="OS Simulator", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Botones de Carga
        self.btn_generate = ctk.CTkButton(self.sidebar_frame, text="Generar Datos", command=self.generate_data_action)
        self.btn_generate.grid(row=1, column=0, padx=20, pady=10)
        
        self.btn_load = ctk.CTkButton(self.sidebar_frame, text="Cargar JSON", command=self.load_data_action)
        self.btn_load.grid(row=2, column=0, padx=20, pady=10)

        # Selectores de Algoritmos
        self.lbl_cpu = ctk.CTkLabel(self.sidebar_frame, text="CPU Algorithm:", anchor="w")
        self.lbl_cpu.grid(row=3, column=0, padx=20, pady=(10, 0))
        self.cpu_option = ctk.CTkOptionMenu(self.sidebar_frame, values=["FCFS", "Round Robin", "SJF"])
        self.cpu_option.grid(row=4, column=0, padx=20, pady=5)

        self.lbl_mem = ctk.CTkLabel(self.sidebar_frame, text="Memory Algorithm:", anchor="w")
        self.lbl_mem.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.mem_option = ctk.CTkOptionMenu(self.sidebar_frame, values=["FIFO", "LRU", "Optimal"])
        self.mem_option.grid(row=6, column=0, padx=20, pady=5)

        self.lbl_disk = ctk.CTkLabel(self.sidebar_frame, text="Disk Algorithm:", anchor="w")
        self.lbl_disk.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.disk_option = ctk.CTkOptionMenu(self.sidebar_frame, values=["FCFS", "SSTF", "SCAN"])
        self.disk_option.grid(row=8, column=0, padx=20, pady=5, sticky="n")

        # Botón Ejecutar
        self.btn_run = ctk.CTkButton(self.sidebar_frame, text="EJECUTAR SIMULACIÓN", fg_color="green", command=self.run_simulation)
        self.btn_run.grid(row=9, column=0, padx=20, pady=20)

    def create_main_view(self):
        self.tabview = ctk.CTkTabview(self, width=250)
        self.tabview.grid(row=0, column=1, padx=(20, 20), pady=(20, 20), sticky="nsew")
        
        self.tab_cpu = self.tabview.add("CPU Scheduling")
        self.tab_mem = self.tabview.add("Memory Management")
        self.tab_disk = self.tabview.add("Disk Controller")
        
        # Configurar grids de tabs
        self.tab_cpu.grid_columnconfigure(0, weight=1)
        self.tab_mem.grid_columnconfigure(0, weight=1)
        self.tab_disk.grid_columnconfigure(0, weight=1)

        # --- CPU Tab ---
        self.cpu_results_text = ctk.CTkTextbox(self.tab_cpu, width=800, height=200)
        self.cpu_results_text.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.cpu_plot_frame = ctk.CTkFrame(self.tab_cpu)
        self.cpu_plot_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # --- Memory Tab ---
        self.mem_results_label = ctk.CTkLabel(self.tab_mem, text="Resultados de Memoria", font=ctk.CTkFont(size=16))
        self.mem_results_label.grid(row=0, column=0, pady=10)
        self.mem_stats_frame = ctk.CTkFrame(self.tab_mem)
        self.mem_stats_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # --- Disk Tab ---
        self.disk_results_label = ctk.CTkLabel(self.tab_disk, text="Resultados de Disco", font=ctk.CTkFont(size=16))
        self.disk_results_label.grid(row=0, column=0, pady=10)
        self.disk_plot_frame = ctk.CTkFrame(self.tab_disk)
        self.disk_plot_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    def generate_data_action(self):
        from data_generator import generate_data
        generate_data()
        self.load_data_action("process_data.json")
        messagebox.showinfo("Info", "Datos generados y cargados correctamente.")

    def load_data_action(self, filepath=None):
        if not filepath:
            filepath = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        
        if filepath:
            try:
                self.engine.load_data(filepath)
                self.data_loaded = True
                print(f"Loaded {len(self.engine.processes)} processes.")
            except Exception as e:
                messagebox.showerror("Error", f"Error cargando archivo: {e}")

    def run_simulation(self):
        if not self.data_loaded:
            messagebox.showwarning("Warning", "Primero carga o genera los datos.")
            return

        # 1. CPU
        cpu_algo = self.cpu_option.get()
        timeline, avg_wait, avg_turn = self.engine.run_cpu_simulation(cpu_algo)
        
        self.cpu_results_text.delete("0.0", "end")
        self.cpu_results_text.insert("0.0", f"Resultados CPU ({cpu_algo}):\n")
        self.cpu_results_text.insert("end", f"Tiempo de Espera Promedio: {avg_wait:.2f}\n")
        self.cpu_results_text.insert("end", f"Tiempo de Retorno Promedio: {avg_turn:.2f}\n")
        self.cpu_results_text.insert("end", f"Total Procesos: {len(self.engine.processes)}\n")
        
        # 2. Memory
        mem_algo = self.mem_option.get()
        faults, hits = self.engine.run_memory_simulation(mem_algo)
        
        for widget in self.mem_stats_frame.winfo_children():
            widget.destroy()
            
        ctk.CTkLabel(self.mem_stats_frame, text=f"Algoritmo: {mem_algo}", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        ctk.CTkLabel(self.mem_stats_frame, text=f"Page Faults: {faults}", text_color="red").pack(pady=5)
        ctk.CTkLabel(self.mem_stats_frame, text=f"Page Hits: {hits}", text_color="green").pack(pady=5)
        total_refs = faults + hits
        hit_ratio = (hits / total_refs) * 100 if total_refs > 0 else 0
        ctk.CTkLabel(self.mem_stats_frame, text=f"Hit Ratio: {hit_ratio:.2f}%").pack(pady=5)

        # 3. Disk
        disk_algo = self.disk_option.get()
        seek_time, sequence = self.engine.run_disk_simulation(disk_algo)
        
        for widget in self.disk_plot_frame.winfo_children():
            widget.destroy()
            
        ctk.CTkLabel(self.disk_plot_frame, text=f"Algoritmo: {disk_algo}").pack()
        ctk.CTkLabel(self.disk_plot_frame, text=f"Total Seek Time: {seek_time} cilindros").pack()
        
        # Plot simple de disco
        fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
        # Graficar solo los primeros 50 movimientos para que sea legible
        subset_seq = sequence[:50]
        ax.plot(subset_seq, range(len(subset_seq)), marker='o')
        ax.set_title(f"Secuencia de Disco (Primeros 50 pasos)")
        ax.set_xlabel("Cilindro")
        ax.set_ylabel("Paso")
        ax.invert_yaxis() # Para que el paso 0 esté arriba
        
        canvas = FigureCanvasTkAgg(fig, master=self.disk_plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()
