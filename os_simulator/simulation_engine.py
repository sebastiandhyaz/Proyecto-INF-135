import json
from typing import List, Dict
from models import Process
from cpu_scheduler import CPUScheduler, FCFSStrategy, SJFStrategy, RoundRobinStrategy
from memory_manager import MemoryManager, FIFOStrategy, LRUStrategy, OptimalStrategy
from disk_controller import DiskController, FCFSDiskStrategy, SSTFStrategy, SCANStrategy

class SimulationEngine:
    def __init__(self):
        self.processes: List[Process] = []
        self.cpu_scheduler = CPUScheduler(FCFSStrategy())
        self.memory_manager = MemoryManager(FIFOStrategy())
        self.disk_controller = DiskController(FCFSDiskStrategy())
        
    def load_data(self, filepath: str):
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.processes = [Process.from_dict(p) for p in data]
            
    def run_cpu_simulation(self, algorithm: str, quantum: int = 2):
        if algorithm == "FCFS":
            self.cpu_scheduler.set_strategy(FCFSStrategy())
        elif algorithm == "SJF":
            self.cpu_scheduler.set_strategy(SJFStrategy())
        elif algorithm == "Round Robin":
            self.cpu_scheduler.set_strategy(RoundRobinStrategy())
            
        return self.cpu_scheduler.run(self.processes, quantum)

    def run_memory_simulation(self, algorithm: str, frames: int = 4):
        # Para la simulación "All-in-One", concatenamos todas las referencias
        # O podríamos simular por proceso. El prompt dice "Secuencia de referencias... generada por los 1000 procesos"
        # Asumiremos una gran cadena global de referencias para simplificar la visualización del algoritmo
        all_refs = []
        for p in self.processes:
            all_refs.extend(p.memory_refs)
            
        if algorithm == "FIFO":
            self.memory_manager.set_strategy(FIFOStrategy())
        elif algorithm == "LRU":
            self.memory_manager.set_strategy(LRUStrategy())
        elif algorithm == "Optimal":
            self.memory_manager.set_strategy(OptimalStrategy())
            
        return self.memory_manager.run(all_refs, frames)

    def run_disk_simulation(self, algorithm: str, start_pos: int = 50):
        # Concatenar todas las peticiones
        all_requests = []
        for p in self.processes:
            all_requests.extend(p.disk_requests)
            
        if algorithm == "FCFS":
            self.disk_controller.set_strategy(FCFSDiskStrategy())
        elif algorithm == "SSTF":
            self.disk_controller.set_strategy(SSTFStrategy())
        elif algorithm == "SCAN":
            self.disk_controller.set_strategy(SCANStrategy())
            
        return self.disk_controller.run(all_requests, start_pos)
