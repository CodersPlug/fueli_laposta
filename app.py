import streamlit as st

# Set page config
st.set_page_config(
    page_title="Fueli Petrol",
    page_icon="⛽",
    layout="wide"
)

# Add a header
st.title("Tablero Petrol")
st.markdown("---")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["Líquidos", "GNC", "Taller", "Tienda"])

# Tab 1 - Líquidos
with tab1:
    st.header("Líquidos")
    st.write("""
    En esta sección podrás:
    - Ver el estado actual de los tanques de combustible
    - Monitorear las ventas de combustible en tiempo real
    - Gestionar los precios de los diferentes tipos de combustible
    - Visualizar reportes de ventas y consumo
    """)

# Tab 2 - GNC
with tab2:
    st.header("GNC")
    st.write("""
    En esta sección podrás:
    - Controlar el estado del surtidor de GNC
    - Monitorear las ventas de GNC
    - Gestionar los precios del GNC
    - Ver estadísticas de consumo y ventas
    """)

# Tab 3 - Taller
with tab3:
    st.header("Taller")
    st.write("""
    En esta sección podrás:
    - Gestionar los servicios del taller
    - Ver el estado de los trabajos en curso
    - Administrar el inventario de repuestos
    - Controlar los ingresos y gastos del taller
    """)

# Tab 4 - Tienda
with tab4:
    st.header("Tienda")
    st.write("""
    En esta sección podrás:
    - Controlar el inventario de la tienda
    - Gestionar las ventas de productos
    - Monitorear los productos más vendidos
    - Administrar precios y promociones
    """)

# Add footer
st.markdown("---")
st.markdown("<div style='text-align: center; font-size: 0.8em; color: #666;'>Powered by Fueli</div>", unsafe_allow_html=True)
