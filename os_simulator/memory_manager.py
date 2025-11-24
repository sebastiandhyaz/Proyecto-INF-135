from abc import ABC, abstractmethod
from typing import List, Tuple

class MemoryStrategy(ABC):
    @abstractmethod
    def simulate(self, pages: List[int], frames_count: int) -> Tuple[int, int, List[int]]:
        """
        Retorna: (Page Faults, Hits, History of Faults (cumulative))
        """
        pass

class FIFOStrategy(MemoryStrategy):
    def simulate(self, pages: List[int], frames_count: int) -> Tuple[int, int, List[int]]:
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
    def simulate(self, pages: List[int], frames_count: int) -> Tuple[int, int, List[int]]:
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
    def simulate(self, pages: List[int], frames_count: int) -> Tuple[int, int, List[int]]:
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

class MemoryManager:
    def __init__(self, strategy: MemoryStrategy):
        self.strategy = strategy
        
    def set_strategy(self, strategy: MemoryStrategy):
        self.strategy = strategy
        
    def run(self, pages: List[int], frames_count: int):
        return self.strategy.simulate(pages, frames_count)
