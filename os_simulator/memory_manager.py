from abc import ABC, abstractmethod
from typing import List, Tuple
import random

class MemoryStrategy(ABC):
    @abstractmethod
    def simulate(self, pages: List[int], frames_count: int, process_sizes: List[int] = None) -> Tuple[int, int, List[int]]:
        """
        Retorna: (Page Faults, Hits, History of Faults (cumulative))
        """
        pass

class FIFOStrategy(MemoryStrategy):
    def simulate(self, pages: List[int], frames_count: int, process_sizes: List[int] = None) -> Tuple[int, int, List[int]]:
        frames = []
        faults = 0
        hits = 0
        history = []
        
        for page in pages:
            if page not in frames:
                faults += 1
                if len(frames) < frames_count:
                    frames.append(page)
                else:
                    frames.pop(0) # Eliminar el primero (First In)
                    frames.append(page)
            else:
                hits += 1
            history.append(faults)
        
        return faults, hits, history

class LRUStrategy(MemoryStrategy):
    def simulate(self, pages: List[int], frames_count: int, process_sizes: List[int] = None) -> Tuple[int, int, List[int]]:
        frames = [] 
        faults = 0
        hits = 0
        history = []
        
        for page in pages:
            if page not in frames:
                faults += 1
                if len(frames) < frames_count:
                    frames.append(page)
                else:
                    frames.pop(0) 
                    frames.append(page)
            else:
                hits += 1
                frames.remove(page)
                frames.append(page)
            history.append(faults)
                
        return faults, hits, history

class OptimalStrategy(MemoryStrategy):
    def simulate(self, pages: List[int], frames_count: int, process_sizes: List[int] = None) -> Tuple[int, int, List[int]]:
        frames = []
        faults = 0
        hits = 0
        history = []
        
        for i, page in enumerate(pages):
            if page not in frames:
                faults += 1
                if len(frames) < frames_count:
                    frames.append(page)
                else:
                    farthest_idx = -1
                    victim_frame = -1
                    
                    for frame in frames:
                        try:
                            next_use = pages[i+1:].index(frame)
                        except ValueError:
                            next_use = float('inf')
                        
                        if next_use > farthest_idx:
                            farthest_idx = next_use
                            victim_frame = frame
                    
                    frames.remove(victim_frame)
                    frames.append(page)
            else:
                hits += 1
            history.append(faults)
                
        return faults, hits, history

class BestFitStrategy(MemoryStrategy):
    def simulate(self, pages: List[int], frames_count: int, process_sizes: List[int] = None) -> Tuple[int, int, List[int]]:
        random.seed(42)
        
        memory_blocks = [100, 200, 50, 150, 300, 120, 80, 250] * (frames_count // 8 + 1)
        memory_blocks = memory_blocks[:frames_count]
        
        if process_sizes is None:
            process_sizes = [random.randint(10, 90) for _ in range(len(pages))]
        
        espacio_restante = memory_blocks[:]
        asignados = 0
        fallos_asignacion = 0
        history = []
        
        limit = min(len(process_sizes), 1000)
        
        for i in range(limit):
            proceso_size = process_sizes[i]
            mejor_bloque = -1
            menor_despilfarro = float('inf')
            
            for j, bloque in enumerate(espacio_restante):
                if bloque >= proceso_size:
                    despilfarro = bloque - proceso_size
                    if despilfarro < menor_despilfarro:
                        mejor_bloque = j
                        menor_despilfarro = despilfarro
            
            if mejor_bloque != -1:
                espacio_restante[mejor_bloque] -= proceso_size
                asignados += 1
            else:
                fallos_asignacion += 1
            
            history.append(fallos_asignacion)
            
        return fallos_asignacion, asignados, history

class WorstFitStrategy(MemoryStrategy):
    def simulate(self, pages: List[int], frames_count: int, process_sizes: List[int] = None) -> Tuple[int, int, List[int]]:
        random.seed(42) 
        
        memory_blocks = [100, 200, 50, 150, 300, 120, 80, 250] * (frames_count // 8 + 1)
        memory_blocks = memory_blocks[:frames_count]
        
        if process_sizes is None:
            process_sizes = [random.randint(10, 90) for _ in range(len(pages))]
        
        espacio_restante = memory_blocks[:]
        asignados = 0
        fallos_asignacion = 0
        history = []
        
        limit = min(len(process_sizes), 1000)
        
        for i in range(limit):
            proceso_size = process_sizes[i]
            peor_bloque = -1
            mayor_espacio = -1
            
            for j, bloque in enumerate(espacio_restante):
                if bloque >= proceso_size:
                    if bloque > mayor_espacio:
                        peor_bloque = j
                        mayor_espacio = bloque
            
            if peor_bloque != -1:
                espacio_restante[peor_bloque] -= proceso_size
                asignados += 1
            else:
                fallos_asignacion += 1
            
            history.append(fallos_asignacion)
            
        return fallos_asignacion, asignados, history

class FirstFitStrategy(MemoryStrategy):
    def simulate(self, pages: List[int], frames_count: int, process_sizes: List[int] = None) -> Tuple[int, int, List[int]]:
        random.seed(42) 
        
        memory_blocks = [100, 200, 50, 150, 300, 120, 80, 250] * (frames_count // 8 + 1)
        memory_blocks = memory_blocks[:frames_count]
        
        if process_sizes is None:
            process_sizes = [random.randint(10, 90) for _ in range(len(pages))]
        
        espacio_restante = memory_blocks[:]
        asignados = 0
        fallos_asignacion = 0
        history = []
        
        limit = min(len(process_sizes), 1000)
        
        for i in range(limit):
            proceso_size = process_sizes[i]
            asignado = False
            
            for j, bloque in enumerate(espacio_restante):
                if bloque >= proceso_size:
                    espacio_restante[j] -= proceso_size
                    asignados += 1
                    asignado = True
                    break
            
            if not asignado:
                fallos_asignacion += 1
            
            history.append(fallos_asignacion)
            
        return fallos_asignacion, asignados, history

class RelocatablePartitionStrategy(MemoryStrategy):
    def simulate(self, pages: List[int], frames_count: int, process_sizes: List[int] = None) -> Tuple[int, int, List[int]]:
        random.seed(42) 
        
        memory_blocks = [100, 200, 50, 150, 300, 120, 80, 250] * (frames_count // 8 + 1)
        memory_blocks = memory_blocks[:frames_count]
        
        if process_sizes is None:
            process_sizes = [random.randint(10, 90) for _ in range(len(pages))]
        
        espacio_restante = memory_blocks[:]
        asignados = 0
        fallos_asignacion = 0
        history = []
        
        limit = min(len(process_sizes), 1000)
        
        for i in range(limit):
            proceso_size = process_sizes[i]
            asignado = False
            
            for j, bloque in enumerate(espacio_restante):
                if bloque >= proceso_size:
                    espacio_restante[j] -= proceso_size
                    asignados += 1
                    asignado = True
                    break
            
            if not asignado:
                total_libre = sum(espacio_restante)
                if total_libre >= proceso_size:
                    espacio_restante = [0] * len(espacio_restante)
                    espacio_restante[0] = total_libre
                    
                    if espacio_restante[0] >= proceso_size:
                        espacio_restante[0] -= proceso_size
                        asignados += 1
                        asignado = True
            
            if not asignado:
                fallos_asignacion += 1
            
            history.append(fallos_asignacion)
            
        return fallos_asignacion, asignados, history

class MemoryManager:
    def __init__(self, strategy: MemoryStrategy):
        self.strategy = strategy
        
    def set_strategy(self, strategy: MemoryStrategy):
        self.strategy = strategy
        
    def run(self, pages: List[int], frames_count: int, process_sizes: List[int] = None):
        return self.strategy.simulate(pages, frames_count, process_sizes)
