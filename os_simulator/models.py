import json
from dataclasses import dataclass, asdict
from typing import List

@dataclass
class Process:
    pid: int
    arrival_time: int
    burst_time: int
    priority: int
    memory_refs: List[int]  # Secuencia de referencias a páginas
    disk_requests: List[int] # Lista de cilindros solicitados

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data):
        return Process(**data)
