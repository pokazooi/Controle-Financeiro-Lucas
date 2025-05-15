import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64

st.set_page_config(page_title="Meu Controle de Apostas", layout="wide")

# Cabeçalho visual com logo
with open("logo_meu_controle_apostas.png", "rb") as image_file:
    base64_logo = base64.b64encode(image_file.read()).decode("utf-8")

st.markdown(f"""
<style>
    .app-header {{
        text-align: center;
        margin-top: -40px;
        margin-bottom: 30px;
    }}
    .app-title {{
        font-size: 40px;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 10px;
    }}
</style>

<div class="app-header">
    <img src='data:image/png;base64,{{base64_logo}}' width='120'/>
    <div class="app-title">Meu Controle de Apostas</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.title("📋 Navegação")
selecao = st.sidebar.radio("Ir para:", ["Bets Futebol", "Bets Basquete", "Saldos"])

# ... O restante do app continuará exatamente como o anterior (será reinserido em partes)