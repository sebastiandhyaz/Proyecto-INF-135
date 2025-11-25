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

# Estilos CSS para hacer la interfaz más compacta y simétrica (Flexbox)
st.markdown("""
<style>
    /* Contenedor principal centrado y con ancho máximo controlado */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Títulos centrados */
    h1, h2, h3, h4, h5 {
        text-align: center !important;
    }
    
    /* Botones con tamaño uniforme y centrados */
    .stButton button {
        width: 100%;
        /* height: 45px;  <-- Eliminamos altura fija que causaba desproporción */
        margin-top: 28px; /* Ajuste para alinear con los inputs que tienen label arriba */
        border-radius: 8px;
        font-weight: bold;
    }
    
    /* Métricas centradas usando Flexbox */
    div[data-testid="stMetric"] {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background-color: #262730; /* Fondo sutil para métricas */
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 1rem !important;
    }

    /* Ajuste de columnas para alineación vertical */
    div[data-testid="column"] {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("🖥️ Simulador de Sistema Operativo")

    # Inicializar el motor en session_state
    if 'engine' not in st.session_state:
        st.session_state.engine = SimulationEngine()
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False

    # Pestañas principales (Imitando la imagen de referencia)
    tab_io, tab_cpu, tab_mem, tab_disk, tab_help = st.tabs(["Mezcla/IO", "CPU", "Memoria", "Disco", "Ayuda"])

    # --- PESTAÑA 1: MEZCLA / IO (Generación de Datos) ---
    with tab_io:
        st.markdown("#### Generar mezcla de trabajos")
        
        # Fila 1: Inputs centrados
        c_input1, c_input2 = st.columns(2)
        with c_input1:
            num_procs = st.number_input("# Procesos:", min_value=10, value=1000, step=10)
        with c_input2:
            seed_val = st.number_input("Semilla (Seed):", value=135)
        
        st.write("") # Espacio
        
        # Fila 2: Botones de acción centrados
        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            if st.button("Generar Datos Nuevos", type="primary"):
                generate_data(num_processes=num_procs, seed=seed_val)
                st.session_state.engine.load_data("process_data.json")
                st.session_state.data_loaded = True
                st.success(f"Generados {num_procs} procesos (Seed: {seed_val})")
        
        with c_btn2:
            if st.button("Cargar JSON Existente"):
                if os.path.exists("process_data.json"):
                    st.session_state.engine.load_data("process_data.json")
                    st.session_state.data_loaded = True
                    st.success("Datos cargados correctamente.")
                else:
                    st.error("No se encontró process_data.json")

        st.divider()
        st.markdown("#### Exportar Datos")
        # Botones de exportación simétricos
        c1, c2, c3 = st.columns(3)
        with c1: st.button("Exportar Procesos (CSV)")
        with c2: st.button("Exportar Memoria (CSV)")
        with c3: st.button("Exportar Disco (CSV)")

    # --- PESTAÑA 2: CPU ---
    with tab_cpu:
        if not st.session_state.data_loaded:
            st.warning("⚠️ Primero genera los datos en la pestaña 'Mezcla/IO'")
        else:
            st.markdown("#### Planificación de CPU")
            
            # Controles simétricos [1, 1, 1]
            c_algo, c_quantum, c_exec = st.columns([1, 1, 1])
            with c_algo:
                cpu_algo = st.selectbox("Algoritmo CPU", ["FCFS", "Round Robin", "SJF", "Prioridad"])
            with c_quantum:
                quantum = st.number_input("Quantum (RR)", value=2, min_value=1)
            with c_exec:
                # st.write("") # Eliminamos espaciadores manuales ya que usamos CSS margin-top
                # st.write("")
                run_cpu = st.button("Ejecutar CPU", type="primary")

            if run_cpu:
                timeline, avg_wait, avg_turn = st.session_state.engine.run_cpu_simulation(cpu_algo, quantum)
                
                st.divider()
                # Métricas centradas
                m1, m2, m3 = st.columns(3)
                m1.metric("Espera Promedio", f"{avg_wait:.2f}")
                m2.metric("Retorno Promedio", f"{avg_turn:.2f}")
                m3.metric("Procesos", len(st.session_state.engine.processes))
                
                st.divider()
                
                # Layout Simétrico: Gráfica | Tabla [1, 1]
                col_graph, col_table = st.columns([1, 1])
                
                with col_graph:
                    st.markdown("##### Diagrama de Gantt (Top 30)")
                    if timeline:
                        df_timeline = pd.DataFrame(timeline)
                        df_view = df_timeline.head(30)
                        
                        dynamic_height = max(5, len(df_view) * 0.3)
                        
                        fig, ax = plt.subplots(figsize=(8, dynamic_height)) # Ajuste de ancho
                        for i, row in df_view.iterrows():
                            ax.barh(y=f"P{row['pid']}", width=row['end']-row['start'], left=row['start'], color='#4CAF50')
                        
                        ax.set_xlabel("Tiempo")
                        ax.set_ylabel("Proceso")
                        ax.tick_params(axis='y', labelsize=8)
                        st.pyplot(fig)
                
                with col_table:
                    st.markdown("##### Tabla de Ejecución")
                    if timeline:
                        st.dataframe(df_timeline, height=400, hide_index=True, use_container_width=True)

    # --- PESTAÑA 3: MEMORIA ---
    with tab_mem:
        if not st.session_state.data_loaded:
            st.warning("⚠️ Primero genera los datos en la pestaña 'Mezcla/IO'")
        else:
            st.markdown("#### Gestión de Memoria")
            
            # Layout simétrico [1, 1, 1]
            c_mem_algo, c_mem_frames, c_mem_exec = st.columns([1, 1, 1])
            
            with c_mem_algo:
                mem_algo = st.selectbox(
                    "Algoritmo de Memoria", 
                    [
                        "FIFO (Paginación)", 
                        "LRU (Paginación)", 
                        "Óptimo (Paginación)", 
                        "Best Fit (Bloques)", 
                        "Worst Fit (Bloques)", 
                        "First Fit (Bloques)", 
                        "Partición Reubicable"
                    ]
                )
            
            with c_mem_frames:
                frames = st.number_input("Marcos / Bloques:", value=4, min_value=1)
                
            with c_mem_exec:
                # st.write("") # Eliminamos espaciadores manuales
                # st.write("")
                run_mem = st.button("Ejecutar Memoria", type="primary")

            if run_mem:
                # Mapear nombre del selector al nombre interno del motor
                algo_map = {
                    "FIFO (Paginación)": "FIFO",
                    "LRU (Paginación)": "LRU",
                    "Óptimo (Paginación)": "Optimal",
                    "Best Fit (Bloques)": "Best Fit",
                    "Worst Fit (Bloques)": "Worst Fit",
                    "First Fit (Bloques)": "First Fit",
                    "Partición Reubicable": "Relocatable"
                }
                
                internal_name = algo_map.get(mem_algo, "FIFO") # Fallback seguro
                res_mem = st.session_state.engine.run_memory_simulation(internal_name, frames)
                
                if res_mem:
                    faults, hits, history = res_mem
                    total = faults + hits
                    ratio = (hits / total * 100) if total > 0 else 0
                    
                    st.divider()
                    st.markdown(f"##### Resultados: {mem_algo}")
                    
                    # Métricas centradas
                    cm1, cm2, cm3 = st.columns(3)
                    cm1.metric("Fallos / No Asignados", faults)
                    cm2.metric("Aciertos / Asignados", hits)
                    cm3.metric("Ratio Éxito", f"{ratio:.2f}%")
                    
                    st.divider()
                    
                    # Layout Simétrico: Gráfica | Tabla [1, 1]
                    col_g_mem, col_t_mem = st.columns([1, 1])
                    
                    with col_g_mem:
                        st.markdown("###### Evolución de Fallos")
                        # Graficar historial de fallos acumulados
                        step = max(1, len(history) // 200)
                        sampled_hist = history[::step]
                        
                        fig_m, ax_m = plt.subplots(figsize=(8, 4))
                        ax_m.plot(range(0, len(history), step), sampled_hist, color='#2196F3', linewidth=2)
                        ax_m.set_xlabel("Eventos")
                        ax_m.set_ylabel("Fallos Acumulados")
                        ax_m.grid(True, alpha=0.3)
                        st.pyplot(fig_m)
                        
                    with col_t_mem:
                        st.markdown("###### Resumen de Rendimiento")
                        df_mem = pd.DataFrame({
                            "Métrica": ["Total Eventos", "Fallos", "Éxitos", "Ratio Éxito", "Ratio Fallo"],
                            "Valor": [str(total), str(faults), str(hits), f"{ratio:.2f}%", f"{(100-ratio):.2f}%"]
                        })
                        st.dataframe(df_mem, hide_index=True, use_container_width=True)

    # --- PESTAÑA 4: DISCO ---
    with tab_disk:
        if not st.session_state.data_loaded:
            st.warning("⚠️ Primero genera los datos en la pestaña 'Mezcla/IO'")
        else:
            st.markdown("#### Planificación de Disco")
            
            # Layout simétrico [1, 1, 1]
            c_disk_algo, c_disk_start, c_disk_exec = st.columns([1, 1, 1])
            
            with c_disk_algo:
                disk_algo = st.selectbox("Algoritmo de Disco", ["FCFS / FIFO", "SSTF", "SCAN"])
            
            with c_disk_start:
                start_pos = st.number_input("Cabezal inicial:", value=50, min_value=0, max_value=199)
                
            with c_disk_exec:
                # st.write("") # Eliminamos espaciadores manuales
                # st.write("")
                run_disk = st.button("Ejecutar Disco", type="primary")

            if run_disk:
                # Mapear nombre
                disk_map = {
                    "FCFS / FIFO": "FCFS",
                    "SSTF": "SSTF",
                    "SCAN": "SCAN"
                }
                internal_disk_name = disk_map.get(disk_algo, "FCFS")
                
                res_disk = st.session_state.engine.run_disk_simulation(internal_disk_name, start_pos)

                if res_disk:
                    seek_time, sequence = res_disk
                    
                    st.divider()
                    st.markdown(f"##### Resultados: {disk_algo}")
                    
                    # Métrica centrada (usando columnas para centrar una sola métrica)
                    dm1, dm2, dm3 = st.columns([1, 2, 1])
                    with dm2:
                        st.metric("Total Movimientos (Seek Time)", f"{seek_time} cilindros")
                    
                    st.divider()
                    
                    # Layout Simétrico: Gráfica | Tabla [1, 1]
                    col_g_disk, col_t_disk = st.columns([1, 1])
                    
                    with col_g_disk:
                        st.markdown("###### Secuencia de Atención (Top 50)")
                        if sequence:
                            fig_d, ax_d = plt.subplots(figsize=(8, 5))
                            subset = sequence[:50] # Solo primeros 50
                            ax_d.plot(subset, range(len(subset)), marker='o', linestyle='-', markersize=6, color='#FF5722')
                            ax_d.set_ylabel("Secuencia (Paso)")
                            ax_d.set_xlabel("Cilindro")
                            ax_d.invert_yaxis()
                            ax_d.grid(True, alpha=0.3)
                            st.pyplot(fig_d)
                    
                    with col_t_disk:
                        st.markdown("###### Tabla de Movimientos")
                        if sequence:
                            # Calcular distancias paso a paso para la tabla
                            diffs = [0] + [abs(sequence[i] - sequence[i-1]) for i in range(1, len(sequence))]
                            df_disk = pd.DataFrame({
                                "Paso": range(len(sequence)),
                                "Cilindro": sequence,
                                "Distancia": diffs
                            })
                            st.dataframe(df_disk, height=400, hide_index=True, use_container_width=True)

    # --- PESTAÑA 5: AYUDA ---
    with tab_help:
        st.markdown("""
        ### Ayuda del Simulador
        *   **Mezcla/IO:** Genera los datos aleatorios. Usa 'Seed' para repetir el mismo experimento.
        *   **CPU:** Compara FCFS, RR y SJF. Ajusta el Quantum para RR.
        *   **Memoria:** Simula paginación. Cambia los 'Marcos disponibles' para ver cómo afectan los fallos (Anomalía de Belady).
        *   **Disco:** Simula el movimiento del brazo mecánico.
        """)

if __name__ == "__main__":
    main()
