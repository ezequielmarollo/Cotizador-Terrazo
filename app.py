import streamlit as st
import pandas as pd
import math
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Cotizador Terrazo", page_icon="🏗️", layout="wide")

# --- CARGA DE LISTA DE PRECIOS ---
@st.cache_data
def cargar_precios():
    ruta_excel = "Precios.xlsx"
    if os.path.exists(ruta_excel):
        df = pd.read_excel(ruta_excel)
        df.columns = df.columns.str.strip()
        return df
    else:
        return None

df_precios = cargar_precios()

# --- BUSCADOR MEJORADO ---
def buscar_precio(claves):
    if df_precios is not None:
        if isinstance(claves, str):
            claves = [claves]
        mascara = df_precios['Descripción'].apply(
            lambda desc: all(str(clave).lower() in str(desc).lower() for clave in claves)
        )
        fila = df_precios[mascara]
        if not fila.empty:
            return float(fila.iloc[0]['Precio'])
    return 0.0

# --- FUNCIONES AUXILIARES PARA PRECIOS Y DESCUENTOS ---
def formato_moneda(valor, md=False):
    signo = r"\$" if md else "$"
    return f"{signo} {valor:,.0f}".replace(",", ".")

def aplicar_desc(precio, descuento_pct):
    return precio * (1 - (descuento_pct / 100.0))

def txt_desc(descuento_pct):
    return f" (-{descuento_pct}%)" if descuento_pct > 0 else ""

# --- NUEVA FUNCIÓN OPTIMIZADORA DE ENVASES ---
def optimizar_envases(litros_necesarios):
    baldes_20 = math.floor(litros_necesarios / 20)
    resto = litros_necesarios % 20
    bidones_5 = math.ceil(resto / 5)
    
    if bidones_5 == 4:
        baldes_20 += 1
        bidones_5 = 0
        
    return baldes_20, bidones_5

# --- LISTAS Y CATÁLOGOS ---
MAPA_COLORES_ARIDOS = {
    "Blanco Brillante": "#FFFFFF",
    "Blanco Elena": "#F4F1EA",
    "Bardiglio": "#70757A",
    "Verde Alpe": "#2E8B57",
    "Rosa Córdoba": "#C88A8A",
    "Amarillo": "#DAA520",
    "Marrón Africano": "#4A3525",
    "Napoleón": "#8B3A3A"
}

MAPA_COLORES_BASES = {
    "Gris": "#808080",
    "Blanca": "#FFFFFF",
    "Crema": "#FFFDD0",
    "Terracota": "#E2725B",
    "Negra": "#000000"
}

TAMANOS = ["01", "03"]

# --- LÓGICA DE CÁLCULO GENERAL ---
def calcular_materiales(m2, espesor):
    kg_totales = m2 * espesor * 22
    kits = math.ceil(kg_totales / 125)
    bolsas_base = kits * 2
    
    baldes_ret_20, bidones_ret_5 = optimizar_envases(m2 * 0.2)
    kits_puente = math.ceil(m2 * 1.0 / 40)
    baldes_sellador_20, bidones_sellador_5 = optimizar_envases(m2 * 0.18)
    bidones_hidro = math.ceil((m2 * 0.18) / 5)
    
    return kits, bolsas_base, baldes_ret_20, bidones_ret_5, kits_puente, baldes_sellador_20, bidones_sellador_5, bidones_hidro

# --- INTERFAZ PRINCIPAL ---
st.title("Cotizador de Terrazo")
st.markdown("---")

if df_precios is None:
    st.error("⚠️ No se encontró el archivo 'Precios.xlsx'. Por favor, subilo a la misma carpeta que app.py.")

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
        color_base = st.selectbox("Color de Base", list(MAPA_COLORES_BASES.keys()))
        hex_base = MAPA_COLORES_BASES[color_base]
        
        st.markdown(f"<div style='margin-bottom: 10px; background-color: {hex_base}; width: 100%; height: 25px; border-radius: 5px; border: 1px solid #ccc;'></div>", unsafe_allow_html=True)
        
        precio_base = buscar_precio(["Base", color_base])
        col_pb, col_db = st.columns([3, 2])
        with col_pb:
            st.info(f"Lista: {formato_moneda(precio_base)}")
        with col_db:
            desc_base = st.number_input("% Desc.", min_value=0, max_value=100, value=0, step=1, key="desc_base")

    st.markdown("---")
    st.subheader("Aditivos y Complementos")
    
    with st.container(border=True):
        st.markdown("💧 **Retardante Superficial (Obligatorio)**")
        st.caption("Rendimiento: 0.2 L / m² (Calculado automáticamente en el mejor formato posible)")
        precio_ret_20 = buscar_precio(["Retardante", "20"])
        precio_ret_5 = buscar_precio(["Retardante", "5"])
        
        col_ret1, col_ret2 = st.columns([3, 1])
        with col_ret1:
            st.write(f"🏷️ *Lista: 20L ({formato_moneda(precio_ret_20)}) | 5L ({formato_moneda(precio_ret_5)})*")
        with col_ret2:
            desc_ret = st.number_input("% Desc.", 0, 100, 0, key="desc_ret")
    
    with st.container(border=True):
        usa_puente = st.toggle("🔗 **Incluir Puente Adherente**", value=True)
        if usa_puente:
            st.caption("Rendimiento: 1 kg / m² (Cada kit requiere 1 bolsa de polvo y 1 balde de líquido)")
            precio_puente_polvo = buscar_precio(["Componente A"])
            precio_puente_liquido = buscar_precio(["Componente B"])
            
            col_pte1, col_pte2 = st.columns([3, 1])
            with col_pte1:
                st.write(f"🏷️ *Lista: Polvo ({formato_moneda(precio_puente_polvo)}) | Líquido ({formato_moneda(precio_puente_liquido)})*")
            with col_pte2:
                desc_pte = st.number_input("% Desc.", 0, 100, 0, key="desc_pte")
        else:
            precio_puente_polvo = 0.0
            precio_puente_liquido = 0.0
            desc_pte = 0

    with st.container(border=True):
        st.markdown("🛡️ **Protección Final (Opcional)**")
        st.caption("Rendimiento: 0.18 L / m²")
        opcion_proteccion = st.radio(
            "Seleccioná el acabado deseado:",
            ["Ninguno", "Consolidante Sellador Acrílico", "Hidrolaca"],
            horizontal=True
        )
        
        precio_sellador_20, precio_sellador_5, precio_hidrolaca, desc_prot = 0.0, 0.0, 0.0, 0
        
        if opcion_proteccion != "Ninguno":
            col_prot1, col_prot2 = st.columns([3, 1])
            with col_prot2:
                desc_prot = st.number_input("% Desc.", 0, 100, 0, key="desc_prot")
                
            if opcion_proteccion == "Consolidante Sellador Acrílico":
                precio_sellador_20 = buscar_precio(["Consolidante", "20"])
                precio_sellador_5 = buscar_precio(["Consolidante", "5"])
                with col_prot1:
                    st.write(f"🏷️ *Lista: 20L ({formato_moneda(precio_sellador_20)}) | 5L ({formato_moneda(precio_sellador_5)})*")
            elif opcion_proteccion == "Hidrolaca":
                precio_hidrolaca = buscar_precio(["Hidrolaca", "5"])
                with col_prot1:
                    st.write(f"🏷️ *Lista: 5L ({formato_moneda(precio_hidrolaca)})*")


# --- PESTAÑA 2: ÁRIDOS ---
with tab2:
    st.subheader("Composición de Áridos")
    num_aridos = st.radio("Cantidad de áridos a combinar:", [1, 2, 3], horizontal=True)
    
    aridos_seleccionados = []
    precios_aridos = []
    descuentos_aridos = []
    
    for i in range(num_aridos):
        with st.container(border=True):
            st.markdown(f"**Árido {i+1}**")
            col_swatch, col_color, col_size, col_precio, col_desc = st.columns([1, 3, 2, 2, 2])
            
            with col_color:
                color = st.selectbox("Color", list(MAPA_COLORES_ARIDOS.keys()), key=f"color_{i}")
            with col_swatch:
                hex_color = MAPA_COLORES_ARIDOS[color]
                st.markdown(f"<div style='margin-top: 28px; background-color: {hex_color}; width: 100%; height: 38px; border-radius: 5px; border: 1px solid #ccc;'></div>", unsafe_allow_html=True)
            with col_size:
                tamano = st.selectbox("Tamaño", TAMANOS, key=f"tamano_{i}")
            with col_precio:
                precio = buscar_precio(["Árido", tamano, color])
                st.metric("Precio Lista", formato_moneda(precio))
            with col_desc:
                desc = st.number_input("% Desc.", 0, 100, 0, key=f"desc_arido_{i}")
                
            aridos_seleccionados.append(f"{color} ({tamano})")
            precios_aridos.append(precio)
            descuentos_aridos.append(desc)

    st.subheader("Proporción del Batch")
    st.info("La mezcla requiere exactamente 3 bolsas de árido por kit.")
    
    bolsas_por_kit = []
    if num_aridos == 1:
        bolsas_por_kit = [3]
        st.success(f"✅ 3 bolsas de {aridos_seleccionados[0]} por kit.")
    elif num_aridos == 2:
        opcion = st.radio("Seleccioná la distribución por kit:", [
            f"1 tercio de {aridos_seleccionados[0]} y 2 tercios de {aridos_seleccionados[1]}",
            f"2 tercios de {aridos_seleccionados[0]} y 1 tercio de {aridos_seleccionados[1]}"
        ])
        bolsas_por_kit = [1, 2] if opcion.startswith("1") else [2, 1]
    elif num_aridos == 3:
        bolsas_por_kit = [1, 1, 1]
        st.success("✅ 1 bolsa de cada color por kit.")


# --- PESTAÑA 3: RESULTADOS ---
with tab3:
    if st.button("Generar Cotización 📄", type="primary", use_container_width=True):
        
        kits_necesarios, bolsas_base, baldes_ret_20, bidones_ret_5, kits_puente, baldes_sellador_20, bidones_sellador_5, bidones_hidro = calcular_materiales(m2, espesor)
        distribucion = [b * kits_necesarios for b in bolsas_por_kit]

        # Cálculos de Costos con Descuentos
        precio_base_final = aplicar_desc(precio_base, desc_base)
        costo_base = bolsas_base * precio_base_final
        
        costo_aridos_total = 0
        for cant, precio, desc in zip(distribucion, precios_aridos, descuentos_aridos):
            costo_aridos_total += cant * aplicar_desc(precio, desc)
            
        precio_ret_20_final = aplicar_desc(precio_ret_20, desc_ret)
        precio_ret_5_final = aplicar_desc(precio_ret_5, desc_ret)
        costo_retardante = (baldes_ret_20 * precio_ret_20_final) + (bidones_ret_5 * precio_ret_5_final)
        
        precio_pte_polvo_final = aplicar_desc(precio_puente_polvo, desc_pte)
        precio_pte_liq_final = aplicar_desc(precio_puente_liquido, desc_pte)
        costo_puente = (kits_puente * precio_pte_polvo_final) + (kits_puente * precio_pte_liq_final) if usa_puente else 0
        
        costo_proteccion = 0
        precio_sellador_20_final = aplicar_desc(precio_sellador_20, desc_prot)
        precio_sellador_5_final = aplicar_desc(precio_sellador_5, desc_prot)
        precio_hidrolaca_final = aplicar_desc(precio_hidrolaca, desc_prot)
        
        if opcion_proteccion == "Consolidante Sellador Acrílico":
            costo_proteccion = (baldes_sellador_20 * precio_sellador_20_final) + (bidones_sellador_5 * precio_sellador_5_final)
        elif opcion_proteccion == "Hidrolaca":
            costo_proteccion = bidones_hidro * precio_hidrolaca_final
        
        costo_total = costo_base + costo_aridos_total + costo_retardante + costo_puente + costo_proteccion

        # Interfaz de Resultados
        st.subheader("Resumen de Pedido")
        col1, col2 = st.columns(2)
        col1.metric("Kits de Venta (Mezcla Principal)", f"{kits_necesarios} Kits")
        col2.metric("Costo Total con Descuentos", formato_moneda(costo_total))

        with st.container(border=True):
            st.markdown("### Detalle para Carga y Facturación")
            
            st.write("**Base Cementicia (40%):**")
            st.write(f"- **{bolsas_base}** bolsas de Base {color_base} x {formato_moneda(precio_base_final, True)}{txt_desc(desc_base)} = {formato_moneda(costo_base, True)}")
            
            st.write("**Áridos (60%):**")
            for nombre, cant, precio, desc in zip(aridos_seleccionados, distribucion, precios_aridos, descuentos_aridos):
                if cant > 0:
                    precio_final = aplicar_desc(precio, desc)
                    st.write(f"- **{cant}** bolsas de {nombre} x {formato_moneda(precio_final, True)}{txt_desc(desc)} = {formato_moneda(cant * precio_final, True)}")
            
            st.write("**Aditivos y Complementos:**")
            if baldes_ret_20 > 0:
                st.write(f"- **Retardante (20L):** {baldes_ret_20} un. x {formato_moneda(precio_ret_20_final, True)}{txt_desc(desc_ret)} = {formato_moneda(baldes_ret_20 * precio_ret_20_final, True)}")
            if bidones_ret_5 > 0:
                st.write(f"- **Retardante (5L):** {bidones_ret_5} un. x {formato_moneda(precio_ret_5_final, True)}{txt_desc(desc_ret)} = {formato_moneda(bidones_ret_5 * precio_ret_5_final, True)}")
            
            if usa_puente:
                st.write(f"- **Puente Adherente (Polvo 25kg):** {kits_puente} un. x {formato_moneda(precio_pte_polvo_final, True)}{txt_desc(desc_pte)} = {formato_moneda(kits_puente * precio_pte_polvo_final, True)}")
                st.write(f"- **Puente Adherente (Líquido 15kg):** {kits_puente} un. x {formato_moneda(precio_pte_liq_final, True)}{txt_desc(desc_pte)} = {formato_moneda(kits_puente * precio_pte_liq_final, True)}")
            
            if opcion_proteccion == "Consolidante Sellador Acrílico":
                if baldes_sellador_20 > 0:
                    st.write(f"- **Sellador Acrílico (20L):** {baldes_sellador_20} un. x {formato_moneda(precio_sellador_20_final, True)}{txt_desc(desc_prot)} = {formato_moneda(baldes_sellador_20 * precio_sellador_20_final, True)}")
                if bidones_sellador_5 > 0:
                    st.write(f"- **Sellador Acrílico (5L):** {bidones_sellador_5} un. x {formato_moneda(precio_sellador_5_final, True)}{txt_desc(desc_prot)} = {formato_moneda(bidones_sellador_5 * precio_sellador_5_final, True)}")
            elif opcion_proteccion == "Hidrolaca":
                if bidones_hidro > 0:
                    st.write(f"- **Hidrolaca (5L):** {bidones_hidro} un. x {formato_moneda(precio_hidrolaca_final, True)}{txt_desc(desc_prot)} = {formato_moneda(bidones_hidro * precio_hidrolaca_final, True)}")
            
        st.markdown("<h3 style='text-align: center; color: #d9381e; font-weight: bold;'>PREMECOL</h3>", unsafe_allow_html=True)