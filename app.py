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

# --- LÓGICA DE CÁLCULO BASE Y ADITIVOS ---
def calcular_materiales(m2, espesor):
    # Kits y Base
    kg_totales = m2 * espesor * 22
    kits = math.ceil(kg_totales / 125)
    bolsas_base = kits * 2
    
    # Retardante (Rinde 0.2 kg/m2 - Prioriza 20kg y completa con 5kg)
    kg_retardante = m2 * 0.2
    baldes_ret_20 = math.floor(kg_retardante / 20)
    resto_ret = kg_retardante % 20
    bidones_ret_5 = math.ceil(resto_ret / 5)
    
    # Puente Adherente (Rinde 1 kg/m2 - Kit compuesto por 1 Polvo y 1 Líquido)
    kits_puente = math.ceil(m2 * 1.0 / 40)
    
    # Sellador (Rinde 0.18 L/m2 - Balde de 20L)
    baldes_sellador = math.ceil(m2 * 0.18 / 20)
    
    return kits, bolsas_base, baldes_ret_20, bidones_ret_5, kits_puente, baldes_sellador


# --- INTERFAZ PRINCIPAL ---
st.title("Cotizador de Terrazo")
st.markdown("---")

# Creación de Pestañas Horizontales
tab1, tab2, tab3 = st.tabs(["1. Dimensiones y Aditivos", "2. Áridos", "3. Resultados"])

# --- PESTAÑA 1: DIMENSIONES Y ADITIVOS ---
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Dimensiones")
        m2 = st.number_input("Metros Cuadrados (m²)", min_value=1.0, value=10.0, step=0.5)
        espesor = st.number_input("Espesor (cm)", min_value=0.5, value=1.0, step=0.1)
    with col2:
        st.subheader("Base Cementicia")
        precio_base = st.number_input("Precio x Bolsa Base 25kg ($)", min_value=0.0, value=10000.0, step=500.0)

    st.markdown("---")
    st.subheader("Aditivos y Complementos")
    
    # Retardante
    st.markdown("**Retardante Superficial (Obligatorio)** - *Rinde 0.2 kg / m²*")
    col_ret1, col_ret2 = st.columns(2)
    precio_ret_20 = col_ret1.number_input("Precio Balde 20 kg ($)", min_value=0.0, value=20000.0, step=500.0)
    precio_ret_5 = col_ret2.number_input("Precio Bidón 5 kg ($)", min_value=0.0, value=6000.0, step=500.0)
    
    st.write("") # Espaciador
    
    # Puente Adherente
    usa_puente = st.checkbox("Incluir Puente Adherente", value=True)
    if usa_puente:
        st.info("Rendimiento: 1 kg / m² (Cada kit requiere 1 bolsa de polvo y 1 balde de líquido)")
        col_p1, col_p2 = st.columns(2)
        precio_puente_polvo = col_p1.number_input("Precio Polvo 25 kg ($)", min_value=0.0, value=12000.0, step=500.0)
        precio_puente_liquido = col_p2.number_input("Precio Líquido 15 kg ($)", min_value=0.0, value=15000.0, step=500.0)
    else:
        precio_puente_polvo = 0.0
        precio_puente_liquido = 0.0

    st.write("") # Espaciador

    # Sellador
    usa_sellador = st.checkbox("Incluir Sellador Acrílico", value=True)
    if usa_sellador:
        st.info("Rendimiento: 0.18 L / m² (Baldes de 20 L)")
        precio_sellador = st.number_input("Precio Balde 20 L ($)", min_value=0.0, value=25000.0, step=500.0)
    else:
        precio_sellador = 0.0

# --- PESTAÑA 2: ÁRIDOS ---
with tab2:
    st.subheader("Composición de Áridos")
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
            precio = st.number_input("Precio Bolsa 25kg ($)", min_value=0.0, value=5000.0, step=500.0, key=f"precio_{i}")
            
        aridos_seleccionados.append(f"{color} ({tamano})")
        precios_aridos.append(precio)
        st.write("---") 

    st.subheader("Proporción del Batch")
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


# --- PESTAÑA 3: RESULTADOS ---
with tab3:
    if st.button("Generar Cotización 📄", type="primary", use_container_width=True):
        
        # Procesamos los cálculos de materiales
        kits_necesarios, bolsas_base, baldes_ret_20, bidones_ret_5, kits_puente, baldes_sellador = calcular_materiales(m2, espesor)
        distribucion = [b * kits_necesarios for b in bolsas_por_kit]

        # Procesamos los costos
        costo_base = bolsas_base * precio_base
        costo_aridos_total = sum(cant * precio for cant, precio in zip(distribucion, precios_aridos))
        costo_retardante = (baldes_ret_20 * precio_ret_20) + (bidones_ret_5 * precio_ret_5)
        
        costo_puente_polvo = kits_puente * precio_puente_polvo if usa_puente else 0
        costo_puente_liquido = kits_puente * precio_puente_liquido if usa_puente else 0
        costo_puente = costo_puente_polvo + costo_puente_liquido
        
        costo_sellador = baldes_sellador * precio_sellador if usa_sellador else 0
        
        costo_total = costo_base + costo_aridos_total + costo_retardante + costo_puente + costo_sellador

        st.subheader("Resumen de Pedido")
        
        col1, col2 = st.columns(2)
        col1.metric("Kits de Venta (Mezcla Principal)", f"{kits_necesarios} Kits")
        col2.metric("Costo Total de Materiales", formato_moneda(costo_total))

        st.markdown("### Detalle para Carga y Facturación")
        st.write("**Base Cementicia (40%):**")
        st.write(f"- **{bolsas_base}** bolsas x {formato_moneda(precio_base)} = {formato_moneda(costo_base)}")
        
        st.write("**Áridos (60%):**")
        for nombre, cant, precio in zip(aridos_seleccionados, distribucion, precios_aridos):
            if cant > 0:
                costo_parcial = cant * precio
                st.write(f"- **{cant}** bolsas de {nombre} x {formato_moneda(precio)} = {formato_moneda(costo_parcial)}")
        
        st.write("**Aditivos y Complementos:**")
        if baldes_ret_20 > 0:
            st.write(f"- **Retardante (Balde 20kg):** {baldes_ret_20} un. x {formato_moneda(precio_ret_20)} = {formato_moneda(baldes_ret_20 * precio_ret_20)}")
        if bidones_ret_5 > 0:
            st.write(f"- **Retardante (Bidón 5kg):** {bidones_ret_5} un. x {formato_moneda(precio_ret_5)} = {formato_moneda(bidones_ret_5 * precio_ret_5)}")
        
        if usa_puente:
            st.write(f"- **Puente Adherente (Polvo 25kg):** {kits_puente} un. x {formato_moneda(precio_puente_polvo)} = {formato_moneda(costo_puente_polvo)}")
            st.write(f"- **Puente Adherente (Líquido 15kg):** {kits_puente} un. x {formato_moneda(precio_puente_liquido)} = {formato_moneda(costo_puente_liquido)}")
        
        if usa_sellador:
            st.write(f"- **Sellador Acrílico (20L):** {baldes_sellador} un. x {formato_moneda(precio_sellador)} = {formato_moneda(costo_sellador)}")
        
        st.markdown("---")
        st.markdown("<h3 style='text-align: center; color: #d9381e; font-weight: bold;'>PREMECOL</h3>", unsafe_allow_html=True)