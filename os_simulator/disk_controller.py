from abc import ABC, abstractmethod
from typing import List, Tuple

class DiskStrategy(ABC):
    @abstractmethod
    def execute(self, requests: List[int], start_pos: int) -> Tuple[int, List[int]]:
        """
        Retorna: (Total Seek Time, Secuencia de Atención)
        """
        pass

class FCFSDiskStrategy(DiskStrategy):
    def execute(self, requests: List[int], start_pos: int) -> Tuple[int, List[int]]:
        seek_time = 0
        current_pos = start_pos
        sequence = [start_pos]
        
        for req in requests:
            seek_time += abs(req - current_pos)
            current_pos = req
            sequence.append(current_pos)
            
        return seek_time, sequence

class SSTFStrategy(DiskStrategy):
    def execute(self, requests: List[int], start_pos: int) -> Tuple[int, List[int]]:
        seek_time = 0
        current_pos = start_pos
        sequence = [start_pos]
        pending = requests.copy()
        
        while pending:
            # Encontrar el más cercano
            closest_req = min(pending, key=lambda x: abs(x - current_pos))
            
            seek_time += abs(closest_req - current_pos)
            current_pos = closest_req
            sequence.append(current_pos)
            pending.remove(closest_req)
            
        return seek_time, sequence

class SCANStrategy(DiskStrategy):
    def execute(self, requests: List[int], start_pos: int) -> Tuple[int, List[int]]:
        # Asumimos dirección hacia arriba (incrementando cilindros) por defecto
        # Rango de disco 0-199 (hardcoded por simplicidad del ejemplo, podría ser paramétrico)
        DISK_SIZE = 200
        
        seek_time = 0
        current_pos = start_pos
        sequence = [start_pos]
        
        # Separar en izquierda y derecha
        left = [r for r in requests if r < start_pos]
        right = [r for r in requests if r >= start_pos]
        
        # Ordenar
        left.sort(reverse=True) # Descendente para ir bajando
        right.sort() # Ascendente para ir subiendo
        
        # Ejecución: Subir hasta el final, luego bajar (o viceversa, aquí asumimos subir primero)
        # SCAN típico va hasta el extremo
        
        # 1. Atender derecha
        for r in right:
            seek_time += abs(r - current_pos)
            current_pos = r
            sequence.append(current_pos)
            
        # Si había peticiones a la izquierda, tenemos que ir al extremo derecho primero (199)
        # Solo si SCAN va hasta el final. Si es LOOK, no va al final.
        # El prompt pide SCAN (Elevador), que usualmente toca el extremo.
        if left:
            if current_pos != DISK_SIZE - 1:
                seek_time += abs((DISK_SIZE - 1) - current_pos)
                current_pos = DISK_SIZE - 1
                sequence.append(current_pos)
            
            # 2. Atender izquierda
            for r in left:
                seek_time += abs(r - current_pos)
                current_pos = r
                sequence.append(current_pos)
                
        return seek_time, sequence

class DiskController:
    def __init__(self, strategy: DiskStrategy):
        self.strategy = strategy
        
    def set_strategy(self, strategy: DiskStrategy):
        self.strategy = strategy
        
    def run(self, requests: List[int], start_pos: int):
        return self.strategy.execute(requests, start_pos)
