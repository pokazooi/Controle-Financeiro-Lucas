
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64

st.set_page_config(page_title="Meu Controle de Apostas", layout="wide")

# Tema claro ou escuro
tema = st.sidebar.selectbox("🎨 Tema", ["Claro", "Escuro"])
tema_css = """
    <style>
        body, .stApp {
            background-color: #f0f2f6;
            color: #000000;
        }
    </style>
"""
if tema == "Escuro":
    tema_css = """
    <style>
        body, .stApp {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        .stButton>button {
            background-color: #313131;
            color: white;
        }
    </style>
    """
st.markdown(tema_css, unsafe_allow_html=True)

# Cabeçalho visual com logo

# Cabeçalho visual com logo
with open("logo_meu_controle_apostas.png", "rb") as image_file:
    base64_logo = base64.b64encode(image_file.read()).decode("utf-8")

header_html = f"""
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
"""
st.markdown(header_html, unsafe_allow_html=True)


st.sidebar.title("📋 Navegação")
selecao = st.sidebar.radio("Ir para:", ["Bets Futebol", "Bets Basquete", "Saldos"])
# ...continuação do app (omitido neste trecho)


# ===== FUNÇÃO UTILITÁRIA
def salvar_df(df, caminho):
    df.to_csv(caminho, index=False)
    st.experimental_rerun()
    st.stop()

# ===== SEÇÃO FUTEBOL

    st.subheader("🔎 Filtros")
    colf1, colf2, colf3 = st.columns(3)
    data_inicial = colf1.date_input("De", value=pd.to_datetime(df["Data"]).min() if not df.empty else pd.to_datetime("today"))
    data_final = colf2.date_input("Até", value=pd.to_datetime(df["Data"]).max() if not df.empty else pd.to_datetime("today"))
    mercado_filtro = colf3.selectbox("Mercado", ["Todos"] + sorted(df["Mercado"].dropna().unique().tolist()))
    resultado_filtro = st.selectbox("Resultado", ["Todos", "GREEN", "RED", "REEMBOLSO"])

    df["Data"] = pd.to_datetime(df["Data"])
    df_filtrado = df[(df["Data"] >= pd.to_datetime(data_inicial)) & (df["Data"] <= pd.to_datetime(data_final))]

    if mercado_filtro != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Mercado"] == mercado_filtro]

    if resultado_filtro != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Resultado"] == resultado_filtro]
if selecao == "Bets Futebol":
    st.header("⚽ Bets Futebol")
    FILE = "bets_futebol.csv"
    df = pd.read_csv(FILE) if os.path.exists(FILE) else pd.DataFrame(columns=["Data", "Jogo", "Mercado", "Valor", "Odd", "Resultado", "Lucro", "Saldo"])

    if not df.empty:
        st.subheader("📌 Resumo Geral")
        total_apostas = len(df)
        greens = df_filtrado[df_filtrado["Resultado"] == "GREEN"]
        reds = df[df["Resultado"] == "RED"]
        reembolsos = df[df["Resultado"] == "REEMBOLSO"]

        total_greens = len(greens)
        total_reds = len(reds)
        total_reembolsos = len(reembolsos)

        lucro_total = df["Lucro"].sum()
        valor_total_apostado = df["Valor"].sum()
        roi = (lucro_total / valor_total_apostado * 100) if valor_total_apostado > 0 else 0
        taxa_acerto = (total_greens / (total_greens + total_reds) * 100) if (total_greens + total_reds) > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🎯 Total Apostas", total_apostas)
        col2.metric("✅ Taxa de Acerto", f"{taxa_acerto:.1f}%")
        col3.metric("📈 ROI", f"{roi:.2f}%")
        col4.metric("💰 Lucro Total", f"R$ {lucro_total:,.2f}")

    with st.form("form_futebol"):
        col1, col2 = st.columns(2)
        data = col1.date_input("Data")
        jogo = col2.text_input("Jogo")
        mercado = st.selectbox("Mercado", ["", "OVER GOLS", "UNDER GOLS", "EMPATE", "VITÓRIA", "HANDICAP"])
        col3, col4 = st.columns(2)
        valor = col3.number_input("Valor", min_value=0.0)
        odd = col4.number_input("Odd", min_value=1.01)
        resultado = st.selectbox("Resultado", ["", "GREEN", "RED", "REEMBOLSO"])
        enviar = st.form_submit_button("Salvar Aposta")

        if enviar and resultado:
            lucro = (odd * valor - valor) if resultado == "GREEN" else (-valor if resultado == "RED" else 0)
            saldo_ant = df["Saldo"].iloc[-1] if not df.empty else 0
            saldo = saldo_ant + lucro
            nova = pd.DataFrame([{"Data": data, "Jogo": jogo, "Mercado": mercado, "Valor": valor, "Odd": odd, "Resultado": resultado, "Lucro": lucro, "Saldo": saldo}])
            df = pd.concat([df, nova], ignore_index=True)
            salvar_df(df, FILE)

    st.subheader("📌 Histórico de Apostas")
    if not df.empty:
        st.dataframe(df_filtrado[::-1], use_container_width=True)

    st.download_button(
        label="📥 Exportar para CSV",
        data=df_filtrado.to_csv(index=False).encode("utf-8"),
        file_name=f"{FILE.replace('.csv','')}_filtrado.csv",
        mime="text/csv"
    )
        st.subheader("📊 Estatísticas")
        st.plotly_chart(px.pie(df_filtrado, names="Resultado", title="Distribuição dos Resultados"), use_container_width=True)
        ranking = df_filtrado[df_filtrado["Resultado"] == "GREEN"]["Mercado"].value_counts().reset_index()
        ranking.columns = ["Mercado", "Greens"]
        st.plotly_chart(px.bar(ranking, x="Mercado", y="Greens", title="Mercados com mais GREEN"), use_container_width=True)

# ===== SEÇÃO BASQUETE
elif selecao == "Bets Basquete":

    st.subheader("🔎 Filtros")
    colf1, colf2, colf3 = st.columns(3)
    data_inicial = colf1.date_input("De", value=pd.to_datetime(df["Data"]).min() if not df.empty else pd.to_datetime("today"))
    data_final = colf2.date_input("Até", value=pd.to_datetime(df["Data"]).max() if not df.empty else pd.to_datetime("today"))
    mercado_filtro = colf3.selectbox("Mercado", ["Todos"] + sorted(df["Mercado"].dropna().unique().tolist()))
    resultado_filtro = st.selectbox("Resultado", ["Todos", "GREEN", "RED", "REEMBOLSO"])

    df["Data"] = pd.to_datetime(df["Data"])
    df_filtrado = df[(df["Data"] >= pd.to_datetime(data_inicial)) & (df["Data"] <= pd.to_datetime(data_final))]

    if mercado_filtro != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Mercado"] == mercado_filtro]

    if resultado_filtro != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Resultado"] == resultado_filtro]
    st.header("🏀 Bets Basquete")
    FILE = "bets_basquete.csv"
    df = pd.read_csv(FILE) if os.path.exists(FILE) else pd.DataFrame(columns=["Data", "Jogo", "Mercado", "Valor", "Odd", "Resultado", "Lucro", "Saldo"])

    if not df.empty:
        st.subheader("📌 Resumo Geral")
        total_apostas = len(df)
        greens = df_filtrado[df_filtrado["Resultado"] == "GREEN"]
        reds = df[df["Resultado"] == "RED"]
        reembolsos = df[df["Resultado"] == "REEMBOLSO"]

        total_greens = len(greens)
        total_reds = len(reds)
        total_reembolsos = len(reembolsos)

        lucro_total = df["Lucro"].sum()
        valor_total_apostado = df["Valor"].sum()
        roi = (lucro_total / valor_total_apostado * 100) if valor_total_apostado > 0 else 0
        taxa_acerto = (total_greens / (total_greens + total_reds) * 100) if (total_greens + total_reds) > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🎯 Total Apostas", total_apostas)
        col2.metric("✅ Taxa de Acerto", f"{taxa_acerto:.1f}%")
        col3.metric("📈 ROI", f"{roi:.2f}%")
        col4.metric("💰 Lucro Total", f"R$ {lucro_total:,.2f}")

    with st.form("form_basquete"):
        col1, col2 = st.columns(2)
        data = col1.date_input("Data")
        jogo = col2.text_input("Jogo")
        mercado = st.selectbox("Mercado", ["", "OVER PONTOS", "UNDER PONTOS", "HANDICAP", "1º TEMPO", "QUARTO"])
        col3, col4 = st.columns(2)
        valor = col3.number_input("Valor", min_value=0.0)
        odd = col4.number_input("Odd", min_value=1.01)
        resultado = st.selectbox("Resultado", ["", "GREEN", "RED", "REEMBOLSO"])
        enviar = st.form_submit_button("Salvar Aposta")

        if enviar and resultado:
            lucro = (odd * valor - valor) if resultado == "GREEN" else (-valor if resultado == "RED" else 0)
            saldo_ant = df["Saldo"].iloc[-1] if not df.empty else 0
            saldo = saldo_ant + lucro
            nova = pd.DataFrame([{"Data": data, "Jogo": jogo, "Mercado": mercado, "Valor": valor, "Odd": odd, "Resultado": resultado, "Lucro": lucro, "Saldo": saldo}])
            df = pd.concat([df, nova], ignore_index=True)
            salvar_df(df, FILE)

    st.subheader("📌 Histórico de Apostas")
    if not df.empty:
        st.dataframe(df_filtrado[::-1], use_container_width=True)

    st.download_button(
        label="📥 Exportar para CSV",
        data=df_filtrado.to_csv(index=False).encode("utf-8"),
        file_name=f"{FILE.replace('.csv','')}_filtrado.csv",
        mime="text/csv"
    )
        st.subheader("📊 Estatísticas")
        st.plotly_chart(px.pie(df_filtrado, names="Resultado", title="Distribuição dos Resultados"), use_container_width=True)
        ranking = df_filtrado[df_filtrado["Resultado"] == "GREEN"]["Mercado"].value_counts().reset_index()
        ranking.columns = ["Mercado", "Greens"]
        st.plotly_chart(px.bar(ranking, x="Mercado", y="Greens", title="Mercados com mais GREEN"), use_container_width=True)

# ===== SEÇÃO SALDOS
elif selecao == "Saldos":
    st.header("💰 Controle de Saldos por Carteiras")
    CARTEIRAS_DIR = "carteiras"
    os.makedirs(CARTEIRAS_DIR, exist_ok=True)

    with st.form("nova_carteira"):
        st.subheader("➕ Nova Carteira")
        nome = st.text_input("Nome da Carteira")
        saldo_inicial = st.number_input("Saldo Inicial (R$)", min_value=0.0)
        criar = st.form_submit_button("Criar Carteira")
        if criar and nome:
            path = f"{CARTEIRAS_DIR}/{nome}.csv"
            if not os.path.exists(path):
                df = pd.DataFrame([{"Data": pd.to_datetime("today").date(), "Descrição": "Saldo Inicial", "Tipo": "GANHO", "Valor": saldo_inicial}])
                df.to_csv(path, index=False)
                st.success(f"Carteira '{nome}' criada!")
                st.experimental_rerun()
                st.stop()

    carteiras = [f.replace(".csv", "") for f in os.listdir(CARTEIRAS_DIR) if f.endswith(".csv")]
    for carteira in carteiras:
        path = f"{CARTEIRAS_DIR}/{carteira}.csv"
        if not os.path.exists(path): continue
        df = pd.read_csv(path)

        with st.expander(f"📁 {carteira}"):
            with st.form(f"form_{carteira}"):
                col1, col2 = st.columns(2)
                data = col1.date_input("Data", key=f"data_{carteira}")
                tipo = col2.selectbox("Tipo", ["GANHO", "GASTO"], key=f"tipo_{carteira}")
                descricao = st.text_input("Descrição", key=f"desc_{carteira}")
                valor = st.number_input("Valor", min_value=0.0, key=f"valor_{carteira}")
                enviar = st.form_submit_button("Adicionar")
                if enviar and descricao:
                    nova = pd.DataFrame([{"Data": data, "Descrição": descricao, "Tipo": tipo, "Valor": valor if tipo == "GANHO" else -valor}])
                    df = pd.concat([df, nova], ignore_index=True)
                    df.to_csv(path, index=False)
                    st.success("Lançamento adicionado.")
                    st.experimental_rerun()
                    st.stop()

            saldo = df["Valor"].sum()
            st.metric(label="💵 Saldo Atual", value=f"R$ {saldo:,.2f}")
            st.markdown("### Histórico de Lançamentos")
            st.dataframe(df_filtrado[::-1], use_container_width=True)
