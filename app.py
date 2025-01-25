!pip install sqlalchemy

import streamlit as st
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text

# Conexão com o banco de dados
engine = create_engine('sqlite:///banco_de_dados.db')

# Função para criar o banco de dados e tabela, caso não existam
def inicializar_banco():
    with engine.connect() as conn:
        # Criação da tabela, se não existir
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS pessoas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                idade INTEGER NOT NULL,
                cidade TEXT NOT NULL
            )
        """))

# Inicializa o banco de dados
def adicionar_pessoa(nome, idade, cidade):
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO pessoas (nome, idade, cidade)
            VALUES (:nome, :idade, :cidade)
        """), {"nome": nome, "idade": idade, "cidade": cidade})

# Função para buscar dados
def listar_pessoas():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM pessoas"))
        return pd.DataFrame(result.fetchall(), columns=result.keys())

# Configuração da página Streamlit
st.title("Gerenciador de Pessoas")
st.sidebar.header("Menu")

opcao = st.sidebar.selectbox("Escolha uma opção:", ["Visualizar Dados", "Adicionar Pessoa"])

# Inicializa o banco ao iniciar o app
inicializar_banco()

if opcao == "Adicionar Pessoa":
    st.header("Adicionar Nova Pessoa")

    nome = st.text_input("Nome")
    idade = st.number_input("Idade", min_value=0, step=1)
    cidade = st.text_input("Cidade")

    if st.button("Adicionar"):
        if nome and cidade and idade:
            adicionar_pessoa(nome, idade, cidade)
            st.success(f"Pessoa {nome} adicionada com sucesso!")
        else:
            st.error("Por favor, preencha todos os campos corretamente.")

elif opcao == "Visualizar Dados":
    st.header("Lista de Pessoas")

    data = listar_pessoas()

    if data.empty:
        st.warning("Nenhuma pessoa encontrada no banco de dados.")
    else:
        st.dataframe(data)
