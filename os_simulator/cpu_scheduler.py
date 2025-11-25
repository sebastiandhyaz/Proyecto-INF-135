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
        # Implementación basada en el código proporcionado por el usuario
        # t_0 -> arrival_time
        # t -> burst_time
        
        # Ordenar por llegada (t_0)
        # Nota: El código original del usuario asume que ya vienen o se procesan en orden de llegada si hay empate
        # Aquí aseguramos el ordenamiento inicial
        sorted_procs = sorted(processes, key=lambda p: p.arrival_time)
        
        t_0 = [p.arrival_time for p in sorted_procs]
        t = [p.burst_time for p in sorted_procs]
        pids = [p.pid for p in sorted_procs]
        
        reloj = 0
        candidato = 0
        pocicion = 0
        r = [] # Lista de índices procesados
        
        timeline = []
        t_i = {} # Tiempo inicio real
        t_f = {} # Tiempo final
        
        # Lógica adaptada del usuario:
        # while len(r)< len(t_0):
        #     t_aux=reloj
        #     while pocicion <len(t_0):
        #         if pocicion not in r and t_0[pocicion]<=reloj:
        #             minimo= t_0[pocicion]
        #             candidato = pocicion
        #             for i in range(pocicion,len(t_0)):
        #                 if t_0[i]<= reloj and t_0[i]< minimo and i not in r:
        #                     minimo= t_0[i]
        #                     candidato = i
        #             ...
        
        # Simplificación: Como ya ordenamos por arrival_time, FCFS es simplemente iterar en orden
        # Pero mantendremos la lógica de "reloj" para ser fieles al comportamiento de simulación
        
        processed_count = 0
        n = len(sorted_procs)
        
        while processed_count < n:
            # Buscar candidato disponible (llegó antes o igual al reloj)
            # En FCFS puro ordenado, siempre es el siguiente en la lista que cumpla la condición
            
            # Filtrar candidatos que ya llegaron y no han sido procesados
            candidates_idx = [i for i in range(n) if i not in r and t_0[i] <= reloj]
            
            if not candidates_idx:
                # Si no hay nadie, avanzar reloj
                reloj += 1
                continue
            
            # De los candidatos, el que tenga menor tiempo de llegada (FCFS)
            # Como ya ordenamos sorted_procs por arrival_time, el primero de la lista candidates_idx es el correcto
            # Sin embargo, para ser robustos con el código original que busca el mínimo:
            best_idx = candidates_idx[0]
            min_arrival = t_0[best_idx]
            
            for idx in candidates_idx:
                if t_0[idx] < min_arrival:
                    min_arrival = t_0[idx]
                    best_idx = idx
            
            # Procesar
            start_time = reloj
            burst = t[best_idx]
            end_time = start_time + burst
            
            timeline.append({'pid': pids[best_idx], 'start': start_time, 'end': end_time})
            
            t_f[pids[best_idx]] = end_time
            reloj = end_time
            r.append(best_idx)
            processed_count += 1
            
        # Calcular métricas finales
        total_wait = 0
        total_turnaround = 0
        
        for p in sorted_procs:
            end_t = t_f[p.pid]
            turnaround = end_t - p.arrival_time
            wait = turnaround - p.burst_time
            total_wait += wait
            total_turnaround += turnaround
            
        avg_wait = total_wait / n
        avg_turnaround = total_turnaround / n
        
        return timeline, avg_wait, avg_turnaround

class SJFStrategy(CPUSchedulingStrategy):
    def schedule(self, processes: List[Process], quantum: int = None):
        # Implementación basada en el código SJN() del usuario
        # SJN (Shortest Job Next) es equivalente a SJF
        
        sorted_procs = sorted(processes, key=lambda p: p.arrival_time)
        t_0 = [p.arrival_time for p in sorted_procs]
        t = [p.burst_time for p in sorted_procs]
        pids = [p.pid for p in sorted_procs]
        
        reloj = 0
        r = [] # Índices procesados
        timeline = []
        t_f = {}
        
        n = len(sorted_procs)
        
        while len(r) < n:
            candidatos = []
            for i in range(n):
                if i not in r:
                    if t_0[i] <= reloj:
                        candidatos.append(i)
            
            if candidatos:
                # candidato = min(candidatos,key=lambda x:t[x])
                candidato_idx = min(candidatos, key=lambda x: t[x])
                
                start_time = reloj
                burst = t[candidato_idx]
                end_time = start_time + burst
                
                timeline.append({'pid': pids[candidato_idx], 'start': start_time, 'end': end_time})
                
                t_f[pids[candidato_idx]] = end_time
                reloj = end_time
                r.append(candidato_idx)
            else:
                reloj += 1
                
        # Métricas
        total_wait = 0
        total_turnaround = 0
        
        for p in sorted_procs:
            end_t = t_f[p.pid]
            turnaround = end_t - p.arrival_time
            wait = turnaround - p.burst_time
            total_wait += wait
            total_turnaround += turnaround
            
        avg_wait = total_wait / n
        avg_turnaround = total_turnaround / n
        
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

class PriorityStrategy(CPUSchedulingStrategy):
    def schedule(self, processes: List[Process], quantum: int = None):
        # Implementación basada en el código PR() del usuario
        
        sorted_procs = sorted(processes, key=lambda p: p.arrival_time)
        t_0 = [p.arrival_time for p in sorted_procs]
        t = [p.burst_time for p in sorted_procs]
        prioridad = [p.priority for p in sorted_procs]
        pids = [p.pid for p in sorted_procs]
        
        reloj = 0
        r = [] # Índices procesados
        timeline = []
        t_f = {}
        
        n = len(sorted_procs)
        
        while len(r) < n:
            candidatos = []
            for i in range(n):
                if i not in r:
                    if t_0[i] <= reloj:
                        candidatos.append(i)
            
            if candidatos:
                # candidato = min(candidatos, key=lambda x: prioridad[x])
                candidato_idx = min(candidatos, key=lambda x: prioridad[x])
                
                start_time = reloj
                burst = t[candidato_idx]
                end_time = start_time + burst
                
                timeline.append({'pid': pids[candidato_idx], 'start': start_time, 'end': end_time})
                
                t_f[pids[candidato_idx]] = end_time
                reloj = end_time
                r.append(candidato_idx)
            else:
                reloj += 1
                
        # Métricas
        total_wait = 0
        total_turnaround = 0
        
        for p in sorted_procs:
            end_t = t_f[p.pid]
            turnaround = end_t - p.arrival_time
            wait = turnaround - p.burst_time
            total_wait += wait
            total_turnaround += turnaround
            
        avg_wait = total_wait / n
        avg_turnaround = total_turnaround / n
        
        return timeline, avg_wait, avg_turnaround

class CPUScheduler:
    def __init__(self, strategy: CPUSchedulingStrategy):
        self.strategy = strategy
    
    def set_strategy(self, strategy: CPUSchedulingStrategy):
        self.strategy = strategy
        
    def run(self, processes: List[Process], quantum: int = None):
        return self.strategy.schedule(processes, quantum)
