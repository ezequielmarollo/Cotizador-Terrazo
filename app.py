import streamlit as st
import math

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Cotizador Terrazo", page_icon="🏗️", layout="wide")

# --- LISTAS Y CATÁLOGOS ---
MAPA_COLORES = {
    "Bco Brillante": "#FFFFFF",
    "Bco Elena": "#F4F1EA",
    "Bardiglio": "#70757A",
    "Verde Alpe": "#2E8B57",
    "Rosa Córdoba": "#C88A8A",
    "Amarillo": "#DAA520",
    "Marrón África": "#4A3525",
    "Napoleon": "#8B3A3A"
}

TAMANOS = ["01 - Chico", "03 - Grande"]

def formato_moneda(valor):
    return f"$ {valor:,.0f}".replace(",", ".")

# --- LÓGICA DE CÁLCULO BASE ---
def calcular_kits(m2, espesor):
    kg_totales = m2 * espesor * 22
    kits = math.ceil(kg_totales / 125)
    bolsas_base = kits * 2
    return kits, bolsas_base

# --- SIDEBAR: INPUTS DEL USUARIO ---
with st.sidebar:
    st.header("1. Dimensiones y Base")
    m2 = st.number_input("Metros Cuadrados (m²)", min_value=1.0, value=10.0, step=0.5)
    espesor = st.number_input("Espesor (cm)", min_value=0.5, value=1.0, step=0.1)
    precio_base = st.number_input("Precio x Bolsa Base ($)", min_value=0.0, value=10000.0, step=500.0)

    kits_necesarios, bolsas_base = calcular_kits(m2, espesor)

    st.header("2. Composición de Áridos")
    num_aridos = st.radio("Cantidad de áridos a combinar:", [1, 2, 3])
    
    aridos_seleccionados = []
    precios_aridos = []
    
    for i in range(num_aridos):
        st.markdown(f"**Árido {i+1}**")
        
        col_swatch, col_color, col_size, col_precio = st.columns([1, 3, 3, 3])
        
        with col_color:
            color = st.selectbox("Color", list(MAPA_COLORES.keys()), key=f"color_{i}")
        with col_swatch:
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
        with col_precio:
            precio = st.number_input("Precio ($)", min_value=0.0, value=5000.0, step=500.0, key=f"precio_{i}")
            
        aridos_seleccionados.append(f"{color} ({tamano})")
        precios_aridos.append(precio)
        st.write("---") 

    st.header("3. Proporción del Batch")
    st.info("La mezcla requiere exactamente 3 bolsas de árido por kit.")
    
    bolsas_por_kit = []
    
    if num_aridos == 1:
        bolsas_por_kit = [3]
        st.success(f"✅ 3 bolsas de {aridos_seleccionados[0]} por kit.")
        
    elif num_aridos == 2:
        opcion = st.radio(
            "Seleccioná la distribución por kit:",
            [
                f"1 tercio de {aridos_seleccionados[0]} y 2 tercios de {aridos_seleccionados[1]}",
                f"2 tercios de {aridos_seleccionados[0]} y 1 tercio de {aridos_seleccionados[1]}"
            ]
        )
        if opcion.startswith("1"):
            bolsas_por_kit = [1, 2]
        else:
            bolsas_por_kit = [2, 1]
            
    elif num_aridos == 3:
        bolsas_por_kit = [1, 1, 1]
        st.success("✅ 1 bolsa de cada color por kit.")

    # Multiplicamos la proporción del kit por la cantidad total de kits
    distribucion = [b * kits_necesarios for b in bolsas_por_kit]


# --- PANTALLA CENTRAL: RESULTADOS ---
st.title("Cotizador de Terrazo")
st.markdown("---")

if st.button("Generar Cotización 📄", type="primary"):
    costo_base = bolsas_base * precio_base
    costo_aridos_total = sum(cant * precio for cant, precio in zip(distribucion, precios_aridos))
    costo_total = costo_base + costo_aridos_total

    st.subheader("Resumen de Pedido")
    
    col1, col2 = st.columns(2)
    col1.metric("Kits de Venta", f"{kits_necesarios} Kits")
    col2.metric("Costo Total de Materiales", formato_moneda(costo_total))

    st.markdown("### Detalle para Carga y Facturación")
    st.write(f"**Base Cementicia (40%):** {bolsas_base} bolsas x {formato_moneda(precio_base)} = {formato_moneda(costo_base)}")
    
    st.write("**Áridos (60%):**")
    for nombre, cant, precio in zip(aridos_seleccionados, distribucion, precios_aridos):
        if cant > 0:
            costo_parcial = cant * precio
            st.write(f"- **{cant}** bolsas de {nombre} x {formato_moneda(precio)} = {formato_moneda(costo_parcial)}")
    
    st.markdown("---")
    st.markdown("<h3 style='text-align: center; color: #d9381e; font-weight: bold;'>PREMECOL</h3>", unsafe_allow_html=True)