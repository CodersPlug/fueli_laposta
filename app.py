import streamlit as st
import tabs.gnc as gnc
import tabs.liquidos as liquidos
import tabs.taller as taller
import tabs.tienda as tienda
import tabs.proveedores as proveedores

# Set page config
st.set_page_config(
    page_title="Fueli La Posta",
    page_icon="⛽",
    layout="wide"
)

# Add a header
st.title("Tablero de Control")
st.markdown("---")

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["GNC", "Líquidos", "Taller", "Tienda", "Proveedores"])

# Render each tab
with tab1:
    gnc.render()

with tab2:
    liquidos.render()

with tab3:
    taller.render()

with tab4:
    tienda.render()

with tab5:
    proveedores.render()

# Add footer
st.markdown("---")
st.markdown("<div style='text-align: center; font-size: 0.8em; color: #666;'>Desarrollado por Fueli</div>", unsafe_allow_html=True)
