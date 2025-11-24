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

# Estilos CSS para hacer la interfaz más compacta
st.markdown("""
<style>
    .block-container {
        padding-top: 3rem;
        padding-bottom: 1rem;
    }
    h1 {
        font-size: 1.5rem !important;
        margin-bottom: 0 !important;
    }
    .stButton button {
        width: 100%;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.2rem !important;
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
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            num_procs = st.number_input("#Procesos:", min_value=10, value=1000, step=10)
            seed_val = st.number_input("Seed:", value=135)
        
        with col2:
            # Espaciadores para alinear botones
            st.write("") 
            st.write("")
            if st.button("Generar Datos", type="primary"):
                generate_data(num_processes=num_procs, seed=seed_val)
                st.session_state.engine.load_data("process_data.json")
                st.session_state.data_loaded = True
                st.success(f"Generados {num_procs} procesos (Seed: {seed_val})")
            
            if st.button("Cargar JSON Existente"):
                if os.path.exists("process_data.json"):
                    st.session_state.engine.load_data("process_data.json")
                    st.session_state.data_loaded = True
                    st.success("Datos cargados.")
                else:
                    st.error("No existe process_data.json")

        st.divider()
        st.markdown("#### Exportar Datos")
        c1, c2, c3 = st.columns(3)
        with c1: st.button("Exportar procesos CSV")
        with c2: st.button("Exportar refs memoria CSV")
        with c3: st.button("Exportar disco CSV")

    # --- PESTAÑA 2: CPU ---
    with tab_cpu:
        if not st.session_state.data_loaded:
            st.warning("Primero genera los datos en la pestaña 'Mezcla/IO'")
        else:
            st.markdown("#### Planificación de CPU")
            
            # Controles compactos
            c_algo, c_quantum, c_exec = st.columns([2, 1, 1])
            with c_algo:
                cpu_algo = st.selectbox("Algoritmo CPU", ["FCFS", "Round Robin", "SJF"], label_visibility="collapsed")
            with c_quantum:
                quantum = st.number_input("Quantum (RR)", value=2, min_value=1)
            with c_exec:
                run_cpu = st.button("Ejecutar CPU", type="primary")

            if run_cpu:
                timeline, avg_wait, avg_turn = st.session_state.engine.run_cpu_simulation(cpu_algo, quantum)
                
                # Métricas en una fila compacta
                m1, m2, m3 = st.columns(3)
                m1.metric("Espera Promedio", f"{avg_wait:.2f}")
                m2.metric("Retorno Promedio", f"{avg_turn:.2f}")
                m3.metric("Procesos", len(st.session_state.engine.processes))
                
                st.divider()
                
                # Layout Horizontal: Gráfica | Tabla
                col_graph, col_table = st.columns([2, 1])
                
                with col_graph:
                    st.markdown("##### Diagrama de Gantt (Top 30)")
                    if timeline:
                        df_timeline = pd.DataFrame(timeline)
                        # Graficar solo los primeros 30 para legibilidad
                        df_view = df_timeline.head(30)
                        
                        fig, ax = plt.subplots(figsize=(10, 4))
                        for i, row in df_view.iterrows():
                            ax.barh(y=f"P{row['pid']}", width=row['end']-row['start'], left=row['start'], color='#4CAF50')
                        ax.set_xlabel("Tiempo")
                        ax.set_ylabel("Proceso")
                        st.pyplot(fig)
                
                with col_table:
                    st.markdown("##### Tabla de Ejecución")
                    if timeline:
                        st.dataframe(df_timeline, height=350, hide_index=True)

    # --- PESTAÑA 3: MEMORIA ---
    with tab_mem:
        if not st.session_state.data_loaded:
            st.warning("Primero genera los datos en la pestaña 'Mezcla/IO'")
        else:
            st.markdown("#### Reemplazo de Página")
            
            # Input de Marcos
            col_frames, col_btns = st.columns([1, 3])
            with col_frames:
                frames = st.number_input("Marcos disponibles:", value=4, min_value=1)
            
            # Botones de algoritmos individuales
            with col_btns:
                st.write("") # Espacio
                b_fifo, b_lru, b_opt = st.columns(3)
                res_mem = None
                algo_name = ""
                
                if b_fifo.button("FIFO"):
                    res_mem = st.session_state.engine.run_memory_simulation("FIFO", frames)
                    algo_name = "FIFO"
                if b_lru.button("LRU"):
                    res_mem = st.session_state.engine.run_memory_simulation("LRU", frames)
                    algo_name = "LRU"
                if b_opt.button("Óptimo"):
                    res_mem = st.session_state.engine.run_memory_simulation("Optimal", frames)
                    algo_name = "Óptimo"

            if res_mem:
                faults, hits, history = res_mem
                total = faults + hits
                ratio = (hits / total * 100) if total > 0 else 0
                
                st.divider()
                st.markdown(f"##### Resultados: {algo_name}")
                
                # Métricas
                cm1, cm2, cm3 = st.columns(3)
                cm1.metric("Fallos (Faults)", faults)
                cm2.metric("Aciertos (Hits)", hits)
                cm3.metric("Hit Ratio", f"{ratio:.2f}%")
                
                # Layout Horizontal: Gráfica | Tabla (Resumen)
                col_g_mem, col_t_mem = st.columns([2, 1])
                
                with col_g_mem:
                    st.markdown("###### Evolución de Fallos")
                    # Graficar historial de fallos acumulados
                    # Muestrear para no saturar si son muchos datos
                    step = max(1, len(history) // 200)
                    sampled_hist = history[::step]
                    
                    fig_m, ax_m = plt.subplots(figsize=(8, 3))
                    ax_m.plot(range(0, len(history), step), sampled_hist, color='#2196F3')
                    ax_m.set_xlabel("Referencias de Memoria")
                    ax_m.set_ylabel("Fallos Acumulados")
                    ax_m.grid(True, alpha=0.3)
                    st.pyplot(fig_m)
                    
                with col_t_mem:
                    st.markdown("###### Resumen de Rendimiento")
                    # Crear una tabla resumen simple
                    # Convertimos todo a string explícitamente para evitar problemas de tipos mixtos en Arrow
                    df_mem = pd.DataFrame({
                        "Métrica": ["Total Referencias", "Fallos", "Aciertos", "Ratio Acierto", "Ratio Fallo"],
                        "Valor": [str(total), str(faults), str(hits), f"{ratio:.2f}%", f"{(100-ratio):.2f}%"]
                    })
                    st.dataframe(df_mem, hide_index=True, use_container_width=True)

    # --- PESTAÑA 4: DISCO ---
    with tab_disk:
        if not st.session_state.data_loaded:
            st.warning("Primero genera los datos en la pestaña 'Mezcla/IO'")
        else:
            st.markdown("#### Planificación de Disco")
            
            # Inputs de configuración
            cd1, cd2 = st.columns(2)
            with cd1:
                start_pos = st.number_input("Cabezal inicial:", value=50, min_value=0, max_value=199)
            with cd2:
                st.number_input("Pista máxima:", value=200, disabled=True)

            # Botones de algoritmos
            st.write("Algoritmos:")
            bd1, bd2, bd3 = st.columns(3)
            
            res_disk = None
            disk_algo_name = ""
            
            if bd1.button("FCFS"):
                res_disk = st.session_state.engine.run_disk_simulation("FCFS", start_pos)
                disk_algo_name = "FCFS"
            if bd2.button("SSTF"):
                res_disk = st.session_state.engine.run_disk_simulation("SSTF", start_pos)
                disk_algo_name = "SSTF"
            if bd3.button("SCAN"):
                res_disk = st.session_state.engine.run_disk_simulation("SCAN", start_pos)
                disk_algo_name = "SCAN"

            if res_disk:
                seek_time, sequence = res_disk
                
                st.divider()
                st.markdown(f"##### Resultados: {disk_algo_name}")
                st.metric("Total Movimientos (Seek Time)", f"{seek_time} cilindros")
                
                # Layout Horizontal: Gráfica | Tabla
                col_g_disk, col_t_disk = st.columns([2, 1])
                
                with col_g_disk:
                    st.markdown("###### Secuencia de Atención (Top 50)")
                    if sequence:
                        fig_d, ax_d = plt.subplots(figsize=(8, 4))
                        subset = sequence[:50] # Solo primeros 50
                        ax_d.plot(subset, range(len(subset)), marker='o', linestyle='-', markersize=4, color='#FF5722')
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
                        st.dataframe(df_disk, height=350, hide_index=True)

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
