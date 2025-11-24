import random
import json
from models import Process

def generate_data(num_processes=1000, filename="process_data.json", seed=None):
    if seed is not None:
        random.seed(seed)
    
    processes = []
    
    # Configuración de la simulación
    MAX_ARRIVAL_TIME = 5000
    MAX_BURST_TIME = 20
    MAX_PAGES = 20 # Páginas numeradas del 0 al 19
    REF_STRING_LENGTH = 15 # Longitud de la cadena de referencia de memoria
    DISK_CYLINDERS = 200 # 0-199
    DISK_REQUESTS_COUNT = 5

    for i in range(num_processes):
        # Generación de datos aleatorios pero realistas
        pid = i + 1
        arrival_time = random.randint(0, MAX_ARRIVAL_TIME)
        burst_time = random.randint(1, MAX_BURST_TIME)
        priority = random.randint(1, 5) # 1 es mayor prioridad (opcional para futuros usos)
        
        # Principio de localidad temporal/espacial simulado (simple)
        # Generamos referencias a páginas
        memory_refs = [random.randint(0, MAX_PAGES) for _ in range(REF_STRING_LENGTH)]
        
        # Peticiones a disco
        disk_requests = [random.randint(0, DISK_CYLINDERS - 1) for _ in range(DISK_REQUESTS_COUNT)]

        proc = Process(pid, arrival_time, burst_time, priority, memory_refs, disk_requests)
        processes.append(proc.to_dict())

    # Ordenar por tiempo de llegada para simular la realidad
    processes.sort(key=lambda x: x['arrival_time'])

    with open(filename, 'w') as f:
        json.dump(processes, f, indent=2)
    
    print(f"Generado archivo '{filename}' con {num_processes} procesos.")

if __name__ == "__main__":
    generate_data()
