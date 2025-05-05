
import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Meu Controle de Apostas", layout="wide")
st.sidebar.title("📋 Navegação")
selecao = st.sidebar.radio("Ir para:", ["Bets Futebol", "Bets Basquete", "Saldos"])
st.title("🏆 Meu Controle de Apostas")

# Seção Futebol
if selecao == "Bets Futebol":
    st.header("⚽ Bets Futebol")
    FILE_FUT = "bets_futebol.csv"
    if os.path.exists(FILE_FUT):
        df = pd.read_csv(FILE_FUT)
    else:
        df = pd.DataFrame(columns=["Data", "Jogo", "Mercado", "Valor Apostado", "Odd", "Resultado", "Lucro/Prejuízo", "Saldo Acumulado"])

    with st.form("futebol_form"):
        col1, col2 = st.columns(2)
        data = col1.date_input("Data")
        jogo = col2.text_input("Jogo")
        mercado = st.selectbox("Mercado", [
            "", "OVER GOLS 1º TEMPO", "UNDER GOLS 1º TEMPO", "VENCEDOR 1º TEMPO", "HANDICAP 1º TEMPO",
            "OVER GOLS JOGO", "UNDER GOLS JOGO", "VENCEDOR DO JOGO", "EMPATE ANULA",
            "OVER GOLS VISITANTE", "UNDER GOLS VISITANTE", "OVER GOLS CASA", "UNDER GOLS CASA", "OUTROS"
        ])
        col3, col4 = st.columns(2)
        valor = col3.number_input("Valor Apostado (R$)", min_value=0.0, step=1.0)
        odd = col4.number_input("Odd", min_value=1.01, step=0.01)
        resultado = st.selectbox("Resultado", ["", "GREEN", "RED", "REEMBOLSO"])
        enviar = st.form_submit_button("Adicionar Aposta")

        if enviar and jogo and mercado and resultado:
            lucro = (odd * valor - valor) if resultado == "GREEN" else (-valor if resultado == "RED" else 0)
            saldo_ant = df["Saldo Acumulado"].iloc[-1] if not df.empty else 0
            saldo = saldo_ant + lucro
            nova = pd.DataFrame([{
                "Data": data, "Jogo": jogo, "Mercado": mercado,
                "Valor Apostado": valor, "Odd": odd, "Resultado": resultado,
                "Lucro/Prejuízo": lucro, "Saldo Acumulado": saldo
            }])
            df = pd.concat([df, nova], ignore_index=True)
            df.to_csv(FILE_FUT, index=False)
            st.success("Aposta adicionada com sucesso!")
            st.experimental_rerun()
        st.stop()

    with st.expander("📌 Histórico de Apostas"):
        if not df.empty:
            for i in range(len(df)-1, -1, -1):
                col1, col2 = st.columns([8, 1])
                col1.write(df.iloc[i])
                if col2.button("🗑️", key=f"del_f{i}"):
                    df.drop(index=i, inplace=True)
                    df.reset_index(drop=True, inplace=True)
                    df.to_csv(FILE_FUT, index=False)
                    st.experimental_rerun()
        st.stop()
        else:
            st.info("Nenhuma aposta registrada ainda.")

    st.subheader("📊 Estatísticas")
    if not df.empty:
        contagem = df["Resultado"].value_counts()
        st.plotly_chart(px.pie(values=contagem.values, names=contagem.index, title="Distribuição dos Resultados"), use_container_width=True)
        ranking = df[df["Resultado"] == "GREEN"]["Mercado"].value_counts().reset_index()
        ranking.columns = ["Mercado", "Greens"]
        if not ranking.empty:
            st.plotly_chart(px.bar(ranking, x="Mercado", y="Greens", title="🏆 Mercados com Mais Greens", color="Greens"), use_container_width=True)

# Seção Basquete
elif selecao == "Bets Basquete":
    st.header("🏀 Bets Basquete")
    FILE_BASQ = "bets_basquete.csv"
    if os.path.exists(FILE_BASQ):
        df = pd.read_csv(FILE_BASQ)
    else:
        df = pd.DataFrame(columns=["Data", "Jogo", "Mercado", "Valor Apostado", "Odd", "Resultado", "Lucro/Prejuízo", "Saldo Acumulado"])

    with st.form("basquete_form"):
        col1, col2 = st.columns(2)
        data = col1.date_input("Data")
        jogo = col2.text_input("Jogo")
        mercado = st.selectbox("Mercado", [
            "", "VENCER 1º TEMPO", "VENCER JOGO", "HANDICAP", "OVER PONTOS",
            "UNDER PONTOS", "HANDICAP 1º TEMPO", "VENCER QUARTO", "HANDICAP QUARTO"
        ])
        col3, col4 = st.columns(2)
        valor = col3.number_input("Valor Apostado (R$)", min_value=0.0, step=1.0)
        odd = col4.number_input("Odd", min_value=1.01, step=0.01)
        resultado = st.selectbox("Resultado", ["", "GREEN", "RED", "REEMBOLSO"])
        enviar = st.form_submit_button("Adicionar Aposta")

        if enviar and jogo and mercado and resultado:
            lucro = (odd * valor - valor) if resultado == "GREEN" else (-valor if resultado == "RED" else 0)
            saldo_ant = df["Saldo Acumulado"].iloc[-1] if not df.empty else 0
            saldo = saldo_ant + lucro
            nova = pd.DataFrame([{
                "Data": data, "Jogo": jogo, "Mercado": mercado,
                "Valor Apostado": valor, "Odd": odd, "Resultado": resultado,
                "Lucro/Prejuízo": lucro, "Saldo Acumulado": saldo
            }])
            df = pd.concat([df, nova], ignore_index=True)
            df.to_csv(FILE_BASQ, index=False)
            st.success("Aposta adicionada com sucesso!")
            st.experimental_rerun()
        st.stop()

    with st.expander("📌 Histórico de Apostas"):
        if not df.empty:
            for i in range(len(df)-1, -1, -1):
                col1, col2 = st.columns([8, 1])
                col1.write(df.iloc[i])
                if col2.button("🗑️", key=f"del_b{i}"):
                    df.drop(index=i, inplace=True)
                    df.reset_index(drop=True, inplace=True)
                    df.to_csv(FILE_BASQ, index=False)
                    st.experimental_rerun()
        st.stop()
        else:
            st.info("Nenhuma aposta registrada ainda.")

    st.subheader("📊 Estatísticas")
    if not df.empty:
        contagem = df["Resultado"].value_counts()
        st.plotly_chart(px.pie(values=contagem.values, names=contagem.index, title="Distribuição dos Resultados"), use_container_width=True)
        ranking = df[df["Resultado"] == "GREEN"]["Mercado"].value_counts().reset_index()
        ranking.columns = ["Mercado", "Greens"]
        if not ranking.empty:
            st.plotly_chart(px.bar(ranking, x="Mercado", y="Greens", title="🏆 Mercados com Mais Greens", color="Greens"), use_container_width=True)

# Seção Saldos com carteiras
elif selecao == "Saldos":
    st.header("💰 Controle de Saldos por Carteiras")

    CARTEIRAS_DIR = "carteiras"
    os.makedirs(CARTEIRAS_DIR, exist_ok=True)

    with st.form("nova_carteira"):
        st.subheader("➕ Criar Nova Carteira")
        nome = st.text_input("Nome da Carteira")
        saldo_inicial = st.number_input("Saldo Inicial (R$)", min_value=0.0, step=1.0)
        criar = st.form_submit_button("Criar")
        if criar and nome:
            path = f"{CARTEIRAS_DIR}/{nome}.csv"
            if not os.path.exists(path):
                df = pd.DataFrame([{
                    "Data": pd.to_datetime("today").date(),
                    "Descrição": "Saldo Inicial",
                    "Tipo": "GANHO",
                    "Valor": saldo_inicial
                }])
                df.to_csv(path, index=False)
                st.success(f"Carteira '{nome}' criada!")
                st.experimental_rerun()
        st.stop()
            else:
                st.warning("Essa carteira já existe!")

    carteiras = [f.replace(".csv", "") for f in os.listdir(CARTEIRAS_DIR) if f.endswith(".csv")]
    if not carteiras:
        st.info("Nenhuma carteira criada ainda.")
    else:
        for carteira in carteiras:
            with st.expander(f"📁 {carteira}"):
                path = f"{CARTEIRAS_DIR}/{carteira}.csv"
                df = pd.read_csv(path)

                with st.form(f"lanc_{carteira}"):
                    st.markdown("### ➕ Novo Lançamento")
                    col1, col2 = st.columns(2)
                    data = col1.date_input("Data", key=f"data_{carteira}")
                    tipo = col2.selectbox("Tipo", ["GANHO", "GASTO"], key=f"tipo_{carteira}")
                    descricao = st.text_input("Descrição", key=f"desc_{carteira}")
                    valor = st.number_input("Valor (R$)", min_value=0.0, step=1.0, key=f"val_{carteira}")
                    enviar = st.form_submit_button("Adicionar Lançamento")
                    if enviar and descricao:
                        nova = pd.DataFrame([{
                            "Data": data,
                            "Descrição": descricao,
                            "Tipo": tipo,
                            "Valor": valor if tipo == "GANHO" else -valor
                        }])
                        df = pd.concat([df, nova], ignore_index=True)
                        df.to_csv(path, index=False)
                        st.success("Lançamento adicionado.")
                        st.experimental_rerun()
        st.stop()

                saldo = df["Valor"].sum()
                st.metric(label="💵 Saldo Atual", value=f"R$ {saldo:,.2f}")

                with st.expander("📜 Histórico de Lançamentos"):
                    for i in range(len(df)-1, -1, -1):
                        col1, col2 = st.columns([8, 1])
                        col1.write(df.iloc[i])
                        if col2.button("🗑️", key=f"del_{carteira}_{i}"):
                            df.drop(index=i, inplace=True)
                            df.reset_index(drop=True, inplace=True)
                            df.to_csv(path, index=False)
                            st.experimental_rerun()
        st.stop()
