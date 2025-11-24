from abc import ABC, abstractmethod
from typing import List, Dict, Tuple
from models import Process
import copy

class CPUSchedulingStrategy(ABC):
    @abstractmethod
    def schedule(self, processes: List[Process], quantum: int = None) -> Tuple[List[Dict], float, float]:
        """
        Retorna:
        1. Timeline (Gantt): Lista de dicts {'pid': int, 'start': int, 'end': int}
        2. Average Wait Time
        3. Average Turnaround Time
        """
        pass

class FCFSStrategy(CPUSchedulingStrategy):
    def schedule(self, processes: List[Process], quantum: int = None):
        # Ordenar por llegada
        sorted_procs = sorted(processes, key=lambda p: p.arrival_time)
        current_time = 0
        timeline = []
        wait_times = {}
        turnaround_times = {}
        
        for p in sorted_procs:
            if current_time < p.arrival_time:
                current_time = p.arrival_time
            
            start_time = current_time
            end_time = start_time + p.burst_time
            
            timeline.append({'pid': p.pid, 'start': start_time, 'end': end_time})
            
            turnaround_times[p.pid] = end_time - p.arrival_time
            wait_times[p.pid] = turnaround_times[p.pid] - p.burst_time
            
            current_time = end_time
            
        avg_wait = sum(wait_times.values()) / len(processes)
        avg_turnaround = sum(turnaround_times.values()) / len(processes)
        
        return timeline, avg_wait, avg_turnaround

class SJFStrategy(CPUSchedulingStrategy):
    def schedule(self, processes: List[Process], quantum: int = None):
        # SJF No Expropiativo
        # Necesitamos simular el paso del tiempo y ver quién está disponible
        pending = sorted(processes, key=lambda p: p.arrival_time)
        ready_queue = []
        completed = []
        current_time = 0
        timeline = []
        
        # Si el primer proceso no llega en 0, avanzamos el tiempo
        if pending and pending[0].arrival_time > current_time:
            current_time = pending[0].arrival_time

        while pending or ready_queue:
            # Mover procesos que han llegado a la cola de listos
            while pending and pending[0].arrival_time <= current_time:
                ready_queue.append(pending.pop(0))
            
            if not ready_queue:
                # Si no hay nadie listo, avanzamos al siguiente que llega
                if pending:
                    current_time = pending[0].arrival_time
                continue
            
            # Seleccionar el de menor ráfaga (Burst Time)
            ready_queue.sort(key=lambda p: p.burst_time)
            process = ready_queue.pop(0)
            
            start_time = current_time
            end_time = start_time + process.burst_time
            timeline.append({'pid': process.pid, 'start': start_time, 'end': end_time})
            
            # Calcular métricas
            turnaround = end_time - process.arrival_time
            wait = turnaround - process.burst_time
            completed.append({'pid': process.pid, 'wait': wait, 'turnaround': turnaround})
            
            current_time = end_time
            
        avg_wait = sum(c['wait'] for c in completed) / len(processes)
        avg_turnaround = sum(c['turnaround'] for c in completed) / len(processes)
        
        return timeline, avg_wait, avg_turnaround

class RoundRobinStrategy(CPUSchedulingStrategy):
    def schedule(self, processes: List[Process], quantum: int = 2):
        # Round Robin con Quantum
        # Necesitamos manejar el estado de ráfaga restante
        
        # Estructura auxiliar para manejar burst restante
        proc_state = {p.pid: {'remaining': p.burst_time, 'arrival': p.arrival_time, 'burst': p.burst_time} for p in processes}
        
        pending = sorted(processes, key=lambda p: p.arrival_time)
        ready_queue = []
        current_time = 0
        timeline = []
        completed_info = {} # pid -> end_time
        
        # Inicialización
        if pending and pending[0].arrival_time > current_time:
            current_time = pending[0].arrival_time

        # Cargar iniciales
        while pending and pending[0].arrival_time <= current_time:
            ready_queue.append(pending.pop(0))

        while ready_queue or pending:
            if not ready_queue:
                if pending:
                    current_time = pending[0].arrival_time
                    while pending and pending[0].arrival_time <= current_time:
                        ready_queue.append(pending.pop(0))
                continue

            process = ready_queue.pop(0)
            pid = process.pid
            
            burst_to_do = min(proc_state[pid]['remaining'], quantum)
            
            start_time = current_time
            end_time = start_time + burst_to_do
            timeline.append({'pid': pid, 'start': start_time, 'end': end_time})
            
            proc_state[pid]['remaining'] -= burst_to_do
            current_time = end_time
            
            # Verificar si llegaron nuevos procesos MIENTRAS se ejecutaba este
            while pending and pending[0].arrival_time <= current_time:
                ready_queue.append(pending.pop(0))
            
            if proc_state[pid]['remaining'] > 0:
                ready_queue.append(process) # Vuelve a la cola
            else:
                completed_info[pid] = current_time # Terminó

        # Calcular métricas finales
        total_wait = 0
        total_turnaround = 0
        
        for p in processes:
            end_t = completed_info[p.pid]
            turnaround = end_t - p.arrival_time
            wait = turnaround - p.burst_time
            total_wait += wait
            total_turnaround += turnaround
            
        avg_wait = total_wait / len(processes)
        avg_turnaround = total_turnaround / len(processes)
        
        return timeline, avg_wait, avg_turnaround

class CPUScheduler:
    def __init__(self, strategy: CPUSchedulingStrategy):
        self.strategy = strategy
    
    def set_strategy(self, strategy: CPUSchedulingStrategy):
        self.strategy = strategy
        
    def run(self, processes: List[Process], quantum: int = None):
        return self.strategy.schedule(processes, quantum)
