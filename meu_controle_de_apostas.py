
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64

st.set_page_config(page_title="Meu Controle de Apostas", layout="wide")

# Logo e título
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
    <img src='data:image/png;base64,{base64_logo}' width='120'/>
    <div class="app-title">Meu Controle de Apostas</div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# Tema
tema = st.sidebar.selectbox("🎨 Tema", ["Claro", "Escuro"])
tema_css = """
    <style>
        body, .stApp { background-color: #f0f2f6; color: #000000; }
    </style>
""" if tema == "Claro" else """
    <style>
        body, .stApp { background-color: #1e1e1e; color: #ffffff; }
        .stButton>button { background-color: #313131; color: white; }
    </style>
"""
st.markdown(tema_css, unsafe_allow_html=True)

st.sidebar.title("📋 Navegação")
selecao = st.sidebar.radio("Ir para:", ["Bets Futebol", "Bets Basquete", "Saldos"])

def salvar_df(df, caminho):
    df.to_csv(caminho, index=False)
    st.experimental_rerun()
    st.stop()

def exibir_apostas(nome, arquivo, mercados):
    st.header(f"📘 {nome}")
    df = pd.read_csv(arquivo) if os.path.exists(arquivo) else pd.DataFrame(columns=["Data", "Jogo", "Mercado", "Valor", "Odd", "Resultado", "Lucro", "Saldo"])
    
    with st.form(f"form_{nome}"):
        col1, col2 = st.columns(2)
        data = col1.date_input("Data")
        jogo = col2.text_input("Jogo")
        mercado = st.selectbox("Mercado", mercados)
        col3, col4 = st.columns(2)
        valor = col3.number_input("Valor", min_value=0.0)
        odd = col4.number_input("Odd", min_value=1.01)
        resultado = st.selectbox("Resultado", ["", "GREEN", "RED", "REEMBOLSO"])
        enviar = st.form_submit_button("Salvar Aposta")

        if enviar and resultado:
            lucro = (odd * valor - valor) if resultado == "GREEN" else (-valor if resultado == "RED" else 0)
            saldo_ant = df["Saldo"].iloc[-1] if not df.empty else 0
            saldo = saldo_ant + lucro
            nova = pd.DataFrame([{
                "Data": data,
                "Jogo": jogo,
                "Mercado": mercado,
                "Valor": valor,
                "Odd": odd,
                "Resultado": resultado,
                "Lucro": lucro,
                "Saldo": saldo
            }])
            df = pd.concat([df, nova], ignore_index=True)
            salvar_df(df, arquivo)

    if not df.empty:
        st.subheader("📌 Resumo Geral")
        greens = df[df["Resultado"] == "GREEN"]
        reds = df[df["Resultado"] == "RED"]
        lucro_total = df["Lucro"].sum()
        valor_total = df["Valor"].sum()
        roi = (lucro_total / valor_total * 100) if valor_total > 0 else 0
        taxa_acerto = (len(greens) / (len(greens) + len(reds)) * 100) if (len(greens) + len(reds)) > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Apostas", len(df))
        col2.metric("Acerto", f"{taxa_acerto:.1f}%")
        col3.metric("ROI", f"{roi:.2f}%")
        col4.metric("Lucro", f"R$ {lucro_total:.2f}")

        st.subheader("🔎 Filtros")
        colf1, colf2, colf3 = st.columns(3)
        data_inicial = colf1.date_input("De", value=pd.to_datetime(df["Data"]).min())
        data_final = colf2.date_input("Até", value=pd.to_datetime(df["Data"]).max())
        mercado_filtro = colf3.selectbox("Mercado", ["Todos"] + sorted(df["Mercado"].dropna().unique().tolist()))
        resultado_filtro = st.selectbox("Resultado", ["Todos", "GREEN", "RED", "REEMBOLSO"])

        df["Data"] = pd.to_datetime(df["Data"])
        df_filt = df[(df["Data"] >= data_inicial) & (df["Data"] <= data_final)]
        if mercado_filtro != "Todos":
            df_filt = df_filt[df_filt["Mercado"] == mercado_filtro]
        if resultado_filtro != "Todos":
            df_filt = df_filt[df_filt["Resultado"] == resultado_filtro]

        st.dataframe(df_filt[::-1], use_container_width=True)
        st.download_button("📥 Exportar CSV", data=df_filt.to_csv(index=False).encode("utf-8"), file_name=f"{nome.replace(' ', '_').lower()}_exportado.csv", mime="text/csv")

        st.subheader("📊 Estatísticas")
        if not df_filt.empty:
            st.plotly_chart(px.pie(df_filt, names="Resultado", title="Distribuição dos Resultados"), use_container_width=True)
            ranking = df_filt[df_filt["Resultado"] == "GREEN"]["Mercado"].value_counts().reset_index()
            ranking.columns = ["Mercado", "Greens"]
            st.plotly_chart(px.bar(ranking, x="Mercado", y="Greens", title="Mercados com mais GREEN"), use_container_width=True)
    else:
        st.info("Nenhuma aposta registrada ainda.")

# Aplicações
if selecao == "Bets Futebol":
    mercados = ["", "OVER GOLS 1º TEMPO", "UNDER GOLS 1º TEMPO", "VENCEDOR 1º TEMPO", "HANDICAP 1º TEMPO",
                "OVER GOLS JOGO", "UNDER GOLS JOGO", "VENCEDOR DO JOGO", "EMPATE ANULA",
                "OVER GOLS VISITANTE", "UNDER GOLS VISITANTE", "OVER GOLS CASA", "UNDER GOLS CASA", "OUTROS"]
    exibir_apostas("Bets Futebol", "bets_futebol.csv", mercados)

elif selecao == "Bets Basquete":
    mercados = ["", "VENCER 1º TEMPO", "VENCER JOGO", "HANDICAP", "OVER PONTOS",
                "UNDER PONTOS", "HANDICAP 1º TEMPO", "VENCER QUARTO", "HANDICAP QUARTO"]
    exibir_apostas("Bets Basquete", "bets_basquete.csv", mercados)

elif selecao == "Saldos":
    st.header("💰 Controle de Saldos por Carteiras")
    pasta = "carteiras"
    os.makedirs(pasta, exist_ok=True)

    with st.form("nova_carteira"):
        nome = st.text_input("Nome da Carteira")
        saldo_inicial = st.number_input("Saldo Inicial", min_value=0.0)
        criar = st.form_submit_button("Criar")
        if criar and nome:
            path = f"{pasta}/{nome}.csv"
            if not os.path.exists(path):
                df = pd.DataFrame([{"Data": pd.to_datetime("today").date(), "Descrição": "Saldo Inicial", "Tipo": "GANHO", "Valor": saldo_inicial}])
                df.to_csv(path, index=False)
                st.experimental_rerun()
                st.stop()

    for file in os.listdir(pasta):
        if file.endswith(".csv"):
            nome = file.replace(".csv", "")
            path = f"{pasta}/{file}"
            df = pd.read_csv(path)
            with st.expander(f"📁 {nome}"):
                st.metric("Saldo Atual", f"R$ {df['Valor'].sum():,.2f}")
                with st.form(f"form_{nome}"):
                    col1, col2 = st.columns(2)
                    data = col1.date_input("Data", key=f"data_{nome}")
                    tipo = col2.selectbox("Tipo", ["GANHO", "GASTO"], key=f"tipo_{nome}")
                    descricao = st.text_input("Descrição", key=f"desc_{nome}")
                    valor = st.number_input("Valor", min_value=0.0, key=f"valor_{nome}")
                    enviar = st.form_submit_button("Adicionar")
                    if enviar and descricao:
                        nova = pd.DataFrame([{
                            "Data": data,
                            "Descrição": descricao,
                            "Tipo": tipo,
                            "Valor": valor if tipo == "GANHO" else -valor
                        }])
                        df = pd.concat([df, nova], ignore_index=True)
                        df.to_csv(path, index=False)
                        st.experimental_rerun()
                        st.stop()
                st.markdown("### Histórico de Lançamentos")
                st.dataframe(df[::-1], use_container_width=True)
