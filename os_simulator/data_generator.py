import random
import json
from models import Process

def generate_data(num_processes=1000, filename="process_data.json", seed=None):
    if seed is not None:
        random.seed(seed)
    
    processes = []
    
    # Configuración de la simulación basada en el código del usuario
    # rango_llegada = (0, 100) -> Escalado para 1000 procesos
    # rango_servicio = (1, 20)
    # prioti = (1, 10)
    # procesos (tamaño) = (10, 90)
    
    MAX_ARRIVAL_TIME = num_processes * 5 # Escalamos el tiempo de llegada para que no lleguen todos juntos
    MAX_BURST_TIME = 20
    MAX_PRIORITY = 10
    
    # Configuración de Memoria y Disco (Mantenemos lógica robusta)
    MAX_PAGES = 20 
    REF_STRING_LENGTH = 15 
    DISK_CYLINDERS = 200 
    DISK_REQUESTS_COUNT = 5

    for i in range(num_processes):
        pid = i + 1
        
        # Generación basada en los rangos del usuario
        arrival_time = random.randint(0, MAX_ARRIVAL_TIME)
        burst_time = random.randint(1, MAX_BURST_TIME)
        priority = random.randint(1, MAX_PRIORITY)
        
        # Tamaño del proceso en memoria (Simulado para Mejor Ajuste)
        process_size = random.randint(10, 90)
        
        # Referencias a páginas (Para algoritmos de paginación)
        memory_refs = [random.randint(0, MAX_PAGES) for _ in range(REF_STRING_LENGTH)]
        
        # Peticiones a disco
        disk_requests = [random.randint(0, DISK_CYLINDERS - 1) for _ in range(DISK_REQUESTS_COUNT)]

        # Creamos el objeto Process.
        proc = Process(pid, arrival_time, burst_time, priority, memory_refs, disk_requests, process_size)
        proc_dict = proc.to_dict()
        
        processes.append(proc_dict)

    # Ordenar por tiempo de llegada
    processes.sort(key=lambda x: x['arrival_time'])

    with open(filename, 'w') as f:
        json.dump(processes, f, indent=2)
    
    print(f"Generado archivo '{filename}' con {num_processes} procesos.")

if __name__ == "__main__":
    generate_data()
