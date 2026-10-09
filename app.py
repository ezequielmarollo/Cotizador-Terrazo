import streamlit as st
import math

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Cotizador Terrazo", page_icon="🏗️", layout="wide")

# --- LISTAS Y CATÁLOGOS ---
# Diccionario con colores HEX aproximados para cada árido
MAPA_COLORES = {
    "Bco Brillante": "#FFFFFF",
    "Bco Elena": "#F4F1EA",       # Blanco crema / tiza
    "Bardiglio": "#70757A",       # Gris oscuro
    "Verde Alpe": "#1A442D",      # Verde oscuro
    "Rosa Córdoba": "#C88A8A",    # Rosa apagado / terracota
    "Amarillo": "#DAA520",        # Ocre / amarillo
    "Marrón África": "#4A3525",   # Marrón oscuro
    "Napoleon": "#8B3A3A"         # Rojo oscuro / bordó
}

TAMANOS = ["01 - Chico", "03 - Grande"]

# --- LÓGICA DE CÁLCULO BASE ---
def calcular_kits(m2, espesor):
    kg_totales = m2 * espesor * 22
    kits = math.ceil(kg_totales / 125)
    bolsas_base = kits * 2
    bolsas_arido = kits * 3
    return kg_totales, kits, bolsas_base, bolsas_arido

# --- SIDEBAR: INPUTS DEL USUARIO ---
with st.sidebar:
    st.header("1. Dimensiones")
    m2 = st.number_input("Metros Cuadrados (m²)", min_value=1.0, value=10.0, step=0.5)
    espesor = st.number_input("Espesor (cm)", min_value=0.5, value=1.0, step=0.1)

    kg_totales, kits_necesarios, bolsas_base, bolsas_arido_total = calcular_kits(m2, espesor)

    st.header("2. Composición de Áridos")
    num_aridos = st.radio("Cantidad de áridos a combinar:", [1, 2, 3])
    
    aridos_seleccionados = []
    
    for i in range(num_aridos):
        st.markdown(f"**Árido {i+1}**")
        
        # 3 columnas: [Cuadrado de color (pequeño)] [Selector de Color] [Selector de Tamaño]
        col_swatch, col_color, col_size = st.columns([1, 5, 4])
        
        with col_color:
            color = st.selectbox("Color", list(MAPA_COLORES.keys()), key=f"color_{i}")
        
        with col_swatch:
            # Inyectamos HTML para dibujar el cuadrado de color. 
            # El margin-top de 28px lo alinea con el menú desplegable.
            hex_color = MAPA_COLORES[color]
            st.markdown(f"""
                <div style='
                    margin-top: 28px; 
                    background-color: {hex_color}; 
                    width: 100%; 
                    height: 38px; 
                    border-radius: 5px; 
                    border: 1px solid #555;'>
                </div>
            """, unsafe_allow_html=True)
            
        with col_size:
            tamano = st.selectbox("Tamaño", TAMANOS, key=f"tamano_{i}")
            
        aridos_seleccionados.append(f"{color} ({tamano})")
        st.write("---") 

    st.header("3. Distribución de Bolsas")
    st.info(f"Total disponible: **{bolsas_arido_total} bolsas**")
    
    distribucion = []
    
    # Lógica de auto-ajuste (cálculo por descarte)
    if num_aridos == 1:
        distribucion = [bolsas_arido_total]
        st.success(f"✅ {bolsas_arido_total} bolsas asignadas automáticamente.")
        
    elif num_aridos == 2:
        bolsas_1 = st.slider(f"{aridos_seleccionados[0]}", 0, bolsas_arido_total, bolsas_arido_total // 2)
        bolsas_2 = bolsas_arido_total - bolsas_1
        distribucion = [bolsas_1, bolsas_2]
        st.success(f"✅ {aridos_seleccionados[1]} se auto-ajustó a: **{bolsas_2} bolsas**.")
        
    elif num_aridos == 3:
        bolsas_1 = st.slider(f"{aridos_seleccionados[0]}", 0, bolsas_arido_total, bolsas_arido_total // 3)
        restante_1 = bolsas_arido_total - bolsas_1
        
        bolsas_2 = st.slider(f"{aridos_seleccionados[1]}", 0, restante_1, restante_1 // 2)
        bolsas_3 = restante_1 - bolsas_2
        
        distribucion = [bolsas_1, bolsas_2, bolsas_3]
        st.success(f"✅ {aridos_seleccionados[2]} se auto-ajustó a: **{bolsas_3} bolsas**.")

# --- PANTALLA CENTRAL: RESULTADOS ---
st.title("Cotizador de Terrazo")
st.markdown("---")

if st.button("Generar Cotización 📄", type="primary"):
    st.subheader("Resumen de Pedido")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Kilos de Mezcla (Teórico)", f"{kg_totales:.1f} kg")
    col2.metric("Kits de Venta (125 kg)", f"{kits_necesarios} Kits")
    col3.metric("Peso Final Despachado", f"{kits_necesarios * 125} kg")

    st.markdown("### Detalle para Carga (Bolsas de 25 kg)")
    st.write(f"**Base Cementicia (40%):** {bolsas_base} bolsas")
    
    st.write("**Áridos (60%):**")
    for nombre, cant in zip(aridos_seleccionados, distribucion):
        if cant > 0:
            st.write(f"- **{cant}** bolsas de {nombre}")
    
    st.info("💡 TODO SE CONSTRUYE")