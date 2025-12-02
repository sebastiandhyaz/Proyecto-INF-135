import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

# --- CONFIGURACIÓN DE PATH ---
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, 'os_simulator'))

try:
    from os_simulator.simulation_engine import SimulationEngine
    from os_simulator.data_generator import generate_data
except ImportError:
    from simulation_engine import SimulationEngine
    from data_generator import generate_data

# Configuración de la página
st.set_page_config(page_title="OS Simulator", layout="wide", page_icon="🖥️")

# Importar FontAwesome
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">', unsafe_allow_html=True)

# Estilos CSS: Tema Azul Oscuro Profesional (Dashboard)
st.markdown("""
<style>
    /* --- TEMA GENERAL --- */
    .stApp {
        background-color: #0f172a; /* Slate 900 */
        color: #f1f5f9; /* Slate 100 */
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #1e293b; /* Slate 800 */
        border-right: 1px solid #334155;
    }

    /* Títulos */
    h1, h2, h3 {
        color: #60a5fa !important; /* Blue 400 */
        font-weight: 700;
    }
    
    h4, h5, h6 {
        color: #94a3b8 !important; /* Slate 400 */
    }

    /* Tarjetas / Contenedores */
    div[data-testid="stMetric"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    div[data-testid="stMetricValue"] {
        color: #38bdf8 !important; /* Sky 400 */
    }

    /* Botones */
    .stButton button {
        background-color: #2563eb; /* Blue 600 */
        color: white;
        border-radius: 6px;
        border: none;
        font-weight: 600;
        transition: background-color 0.2s;
    }
    
    .stButton button:hover {
        background-color: #1d4ed8; /* Blue 700 */
        color: white;
    }

    /* Inputs */
    .stSelectbox > div > div, .stNumberInput > div > div {
        background-color: #1e293b;
        color: white;
        border-radius: 6px;
        border: 1px solid #475569;
    }

    /* Iconos FontAwesome grandes */
    .fa-icon-header {
        font-size: 2rem;
        color: #60a5fa;
        margin-right: 10px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Inicializar el motor
    if 'engine' not in st.session_state:
        st.session_state.engine = SimulationEngine()
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False

    # --- BARRA LATERAL DE NAVEGACIÓN (Sin Emojis) ---
    with st.sidebar:
        st.markdown("## <i class='fa-solid fa-server'></i> OS SIMULATOR", unsafe_allow_html=True)
        st.markdown("---")
        
        # Menú de navegación
        selected_page = st.radio(
            "NAVEGACIÓN", 
            ["DASHBOARD / IO", "CPU MONITOR", "MEMORY MANAGER", "DISK CONTROLLER", "HELP"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.info("Sistema v2.0 - Stable Build")

    # --- PÁGINA 1: DASHBOARD / IO ---
    if selected_page == "DASHBOARD / IO":
        st.markdown("## <i class='fa-solid fa-database fa-icon-header'></i> GENERACIÓN DE CARGA", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### Configuración")
            num_procs = st.number_input("Cantidad de Procesos", min_value=10, value=1000, step=10)
            seed_val = st.number_input("Semilla (Seed)", value=135)
            
            st.write("")
            if st.button("GENERAR DATOS NUEVOS", type="primary"):
                generate_data(num_processes=num_procs, seed=seed_val)
                st.session_state.engine.load_data("process_data.json")
                st.session_state.data_loaded = True
                st.success(f"Datos generados: {num_procs} procesos")

            if st.button("CARGAR DATOS EXISTENTES"):
                if os.path.exists("process_data.json"):
                    st.session_state.engine.load_data("process_data.json")
                    st.session_state.data_loaded = True
                    st.success("Datos cargados correctamente")
                else:
                    st.error("No se encontró el archivo")

        with col2:
            st.markdown("### Estado del Sistema")
            if st.session_state.data_loaded:
                m1, m2, m3 = st.columns(3)
                m1.metric("Procesos Cargados", len(st.session_state.engine.processes))
                m2.metric("Estado", "LISTO", delta="OK")
                m3.metric("Memoria Total", "1024 MB")
                
                st.markdown("#### Exportar Datos")
                c1, c2, c3 = st.columns(3)
                c1.button("CSV Procesos")
                c2.button("CSV Memoria")
                c3.button("CSV Disco")
            else:
                st.info("Esperando generación de datos...")

    # --- PÁGINA 2: CPU ---
    elif selected_page == "CPU MONITOR":
        st.markdown("## <i class='fa-solid fa-microchip fa-icon-header'></i> PLANIFICADOR DE CPU", unsafe_allow_html=True)
        
        if not st.session_state.data_loaded:
            st.warning("⚠️ Por favor genere los datos en el Dashboard primero.")
        else:
            # Panel de Control
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                cpu_algo = st.selectbox("Algoritmo de Planificación", ["FCFS", "Round Robin", "SJF", "Prioridad"])
            with c2:
                quantum = st.number_input("Quantum (RR)", value=2, min_value=1)
            with c3:
                st.write("")
                st.write("")
                run_cpu = st.button("EJECUTAR", type="primary")

            if run_cpu:
                timeline, avg_wait, avg_turn = st.session_state.engine.run_cpu_simulation(cpu_algo, quantum)
                
                st.markdown("---")
                # Métricas
                kpi1, kpi2, kpi3 = st.columns(3)
                kpi1.metric("Tiempo Espera Promedio", f"{avg_wait:.2f} ms")
                kpi2.metric("Tiempo Retorno Promedio", f"{avg_turn:.2f} ms")
                kpi3.metric("Throughput", f"{len(timeline)/100:.2f} p/s")
                
                st.markdown("---")
                
                # Gráfica y Tabla
                g_col, t_col = st.columns([1, 1])
                
                with g_col:
                    st.markdown("#### Diagrama de Gantt")
                    if timeline:
                        df_timeline = pd.DataFrame(timeline)
                        df_view = df_timeline.head(30)
                        
                        plt.style.use('default') # Fondo blanco solicitado
                        fig, ax = plt.subplots(figsize=(10, 6))
                        
                        for i, row in df_view.iterrows():
                            ax.barh(y=f"P{row['pid']}", width=row['end']-row['start'], left=row['start'], color='#3b82f6')
                        
                        ax.set_xlabel("Tiempo")
                        ax.set_ylabel("Proceso")
                        ax.grid(True, alpha=0.3)
                        st.pyplot(fig)
                
                with t_col:
                    st.markdown("#### Tabla de Procesos")
                    if timeline:
                        st.dataframe(df_timeline, height=400, use_container_width=True)

    # --- PÁGINA 3: MEMORIA ---
    elif selected_page == "MEMORY MANAGER":
        st.markdown("## <i class='fa-solid fa-memory fa-icon-header'></i> GESTIÓN DE MEMORIA", unsafe_allow_html=True)
        
        if not st.session_state.data_loaded:
            st.warning("⚠️ Por favor genere los datos en el Dashboard primero.")
        else:
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                mem_algo = st.selectbox("Estrategia de Asignación", 
                    ["FIFO (Paginación)", "LRU (Paginación)", "Óptimo (Paginación)", 
                     "Best Fit (Bloques)", "Worst Fit (Bloques)", "First Fit (Bloques)", "Partición Reubicable"])
            with c2:
                frames = st.number_input("Marcos / Bloques", value=4, min_value=1)
            with c3:
                st.write("")
                st.write("")
                run_mem = st.button("SIMULAR", type="primary")

            if run_mem:
                algo_map = {
                    "FIFO (Paginación)": "FIFO", "LRU (Paginación)": "LRU", "Óptimo (Paginación)": "Optimal",
                    "Best Fit (Bloques)": "Best Fit", "Worst Fit (Bloques)": "Worst Fit",
                    "First Fit (Bloques)": "First Fit", "Partición Reubicable": "Relocatable"
                }
                internal_name = algo_map.get(mem_algo, "FIFO")
                res_mem = st.session_state.engine.run_memory_simulation(internal_name, frames)
                
                if res_mem:
                    faults, hits, history = res_mem
                    total = faults + hits
                    ratio = (hits / total * 100) if total > 0 else 0
                    
                    st.markdown("---")
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Fallos de Página", faults, delta_color="inverse")
                    m2.metric("Aciertos (Hits)", hits)
                    m3.metric("Eficiencia", f"{ratio:.2f}%")
                    st.markdown("---")
                    
                    g_col, t_col = st.columns([1, 1])
                    with g_col:
                        st.markdown("#### Historial de Fallos")
                        step = max(1, len(history) // 200)
                        sampled_hist = history[::step]
                        
                        plt.style.use('default')
                        fig, ax = plt.subplots(figsize=(10, 5))
                        ax.plot(range(0, len(history), step), sampled_hist, color='#ef4444', linewidth=2)
                        ax.set_xlabel("Tiempo")
                        ax.set_ylabel("Fallos Acumulados")
                        ax.grid(True, alpha=0.3)
                        st.pyplot(fig)
                        
                    with t_col:
                        st.markdown("#### Estadísticas")
                        df_mem = pd.DataFrame({
                            "Métrica": ["Total Accesos", "Fallos", "Aciertos", "Ratio"],
                            "Valor": [total, faults, hits, f"{ratio:.2f}%"]
                        })
                        st.dataframe(df_mem, use_container_width=True)

    # --- PÁGINA 4: DISCO ---
    elif selected_page == "DISK CONTROLLER":
        st.markdown("## <i class='fa-solid fa-hard-drive fa-icon-header'></i> CONTROLADOR DE DISCO", unsafe_allow_html=True)
        
        if not st.session_state.data_loaded:
            st.warning("⚠️ Por favor genere los datos en el Dashboard primero.")
        else:
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                disk_algo = st.selectbox("Algoritmo de Disco", ["FCFS / FIFO", "SSTF", "SCAN"])
            with c2:
                start_pos = st.number_input("Posición Inicial Cabezal", value=50, min_value=0, max_value=199)
            with c3:
                st.write("")
                st.write("")
                run_disk = st.button("EJECUTAR", type="primary")

            if run_disk:
                disk_map = {"FCFS / FIFO": "FCFS", "SSTF": "SSTF", "SCAN": "SCAN"}
                internal_disk_name = disk_map.get(disk_algo, "FCFS")
                res_disk = st.session_state.engine.run_disk_simulation(internal_disk_name, start_pos)

                if res_disk:
                    seek_time, sequence = res_disk
                    
                    st.markdown("---")
                    c_res1, c_res2 = st.columns([1, 2])
                    with c_res1:
                        st.metric("Desplazamiento Total", f"{seek_time}", "cilindros")
                    
                    st.markdown("---")
                    
                    g_col, t_col = st.columns([1, 1])
                    with g_col:
                        st.markdown("#### Secuencia de Acceso")
                        if sequence:
                            plt.style.use('default')
                            fig, ax = plt.subplots(figsize=(10, 6))
                            subset = sequence[:50]
                            ax.plot(subset, range(len(subset)), marker='o', linestyle='-', color='#10b981')
                            ax.set_xlabel("Cilindro")
                            ax.set_ylabel("Secuencia")
                            ax.invert_yaxis()
                            ax.grid(True, alpha=0.3)
                            st.pyplot(fig)
                            
                    with t_col:
                        st.markdown("#### Tabla de Movimientos")
                        if sequence:
                            diffs = [0] + [abs(sequence[i] - sequence[i-1]) for i in range(1, len(sequence))]
                            df_disk = pd.DataFrame({"Paso": range(len(sequence)), "Cilindro": sequence, "Distancia": diffs})
                            st.dataframe(df_disk, height=400, use_container_width=True)

    # --- PÁGINA 5: AYUDA ---
    elif selected_page == "HELP":
        st.markdown("## <i class='fa-solid fa-circle-question fa-icon-header'></i> AYUDA Y DOCUMENTACIÓN", unsafe_allow_html=True)
        st.info("Guía rápida de uso del simulador.")
        
        st.markdown("""
        ### Módulos del Sistema
        
        1.  **Dashboard / IO**:
            *   Genera la carga de trabajo inicial.
            *   Define el número de procesos y la semilla aleatoria.
            
        2.  **CPU Monitor**:
            *   Simula la planificación de procesos.
            *   Algoritmos: FCFS (First Come First Served), Round Robin, SJF (Shortest Job First).
            
        3.  **Memory Manager**:
            *   Simula la asignación de memoria y paginación.
            *   Visualiza fallos de página y eficiencia.
            
        4.  **Disk Controller**:
            *   Simula el movimiento del brazo del disco duro.
            *   Algoritmos: FCFS, SSTF (Shortest Seek Time First), SCAN (Elevator).
        """)

if __name__ == "__main__":
    main()
