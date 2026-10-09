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

# Función auxiliar para formatear moneda estilo Argentina ($ 10.000)
def formato_moneda(valor):
    return f"$ {valor:,.0f}".replace(",", ".")

# --- LÓGICA DE CÁLCULO BASE ---
def calcular_kits(m2, espesor):
    kg_totales = m2 * espesor * 22
    kits = math.ceil(kg_totales / 125)
    bolsas_base = kits * 2
    bolsas_arido = kits * 3
    return kg_totales, kits, bolsas_base, bolsas_arido

# --- SIDEBAR: INPUTS DEL USUARIO ---
with st.sidebar:
    st.header("1. Dimensiones y Base")
    m2 = st.number_input("Metros Cuadrados (m²)", min_value=1.0, value=10.0, step=0.5)
    espesor = st.number_input("Espesor (cm)", min_value=0.5, value=1.0, step=0.1)
    precio_base = st.number_input("Precio x Bolsa Base ($)", min_value=0.0, value=10000.0, step=500.0)

    kg_totales, kits_necesarios, bolsas_base, bolsas_arido_total = calcular_kits(m2, espesor)

    st.header("2. Composición de Áridos")
    num_aridos = st.radio("Cantidad de áridos a combinar:", [1, 2, 3])
    
    aridos_seleccionados = []
    precios_aridos = []
    
    for i in range(num_aridos):
        st.markdown(f"**Árido {i+1}**")
        
        # 4 columnas: [Muestra] [Color] [Tamaño] [Precio]
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

    st.header("3. Distribución de Bolsas")
    st.info(f"Total disponible: **{bolsas_arido_total} bolsas**")
    
    distribucion = []
    
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
    # Cálculos económicos
    costo_base = bolsas_base * precio_base
    costo_aridos_total = 0
    
    for cant, precio in zip(distribucion, precios_aridos):
        costo_aridos_total += cant * precio
        
    costo_total = costo_base + costo_aridos_total

    st.subheader("Resumen de Pedido")
    
    # Añadimos una 4ta columna para el costo total
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Kilos de Mezcla (Teórico)", f"{kg_totales:.1f} kg")
    col2.metric("Kits de Venta (125 kg)", f"{kits_necesarios} Kits")
    col3.metric("Peso Final Despachado", f"{kits_necesarios * 125} kg")
    col4.metric("Costo Total de Materiales", formato_moneda(costo_total))

    st.markdown("### Detalle para Carga y Facturación")
    st.write(f"**Base Cementicia (40%):** {bolsas_base} bolsas x {formato_moneda(precio_base)} = {formato_moneda(costo_base)}")
    
    st.write("**Áridos (60%):**")
    for nombre, cant, precio in zip(aridos_seleccionados, distribucion, precios_aridos):
        if cant > 0:
            costo_parcial = cant * precio
            st.write(f"- **{cant}** bolsas de {nombre} x {formato_moneda(precio)} = {formato_moneda(costo_parcial)}")
    
    st.info("💡 PREMECOL")