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
                cidade TEXT NOT NULL,
                profissao TEXT NOT NULL
            )
        """))
        # Inserir dados iniciais, se a tabela estiver vazia
        result = conn.execute(text("SELECT COUNT(*) FROM pessoas"))
        count = result.scalar()
        if count == 0:
            dados_iniciais = pd.DataFrame({
                "nome": [f"Pessoa {i}" for i in range(1, 11)],
                "idade": np.random.randint(18, 60, size=10),
                "cidade": np.random.choice(["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Porto Alegre"], size=10),
                "profissao": np.random.choice(["Engenheiro", "Professor", "Médico", "Advogado"], size=10),
            })
            dados_iniciais.to_sql("pessoas", con=engine, if_exists="append", index=False)

# Inicializar banco de dados ao iniciar o aplicativo
inicializar_banco()

# Interface de Navegação com Botões
st.title("Banco de Dados com Streamlit")

# Define a seleção inicial no session_state, caso ainda não exista
if "menu" not in st.session_state:
    st.session_state["menu"] = "Visualizar Dados"

# Botões para cada funcionalidade
st.sidebar.header("Escolha uma opção:")
if st.sidebar.button("Visualizar Dados"):
    st.session_state["menu"] = "Visualizar Dados"
if st.sidebar.button("Inserir Registro"):
    st.session_state["menu"] = "Inserir Registro"
if st.sidebar.button("Alterar Registro"):
    st.session_state["menu"] = "Alterar Registro"
if st.sidebar.button("Excluir Registro"):
    st.session_state["menu"] = "Excluir Registro"

# Verifica qual opção está ativa e exibe a seção correspondente
menu = st.session_state["menu"]

# 1. Visualizar Dados
if menu == "Visualizar Dados":
    st.header("Visualizar Dados")
    query = "SELECT * FROM pessoas"
    df = pd.read_sql(query, con=engine)
    st.dataframe(df)

# 2. Inserir Registro
elif menu == "Inserir Registro":
    st.header("Inserir Novo Registro")
    with st.form("inserir_form"):
        novo_nome = st.text_input("Nome:")
        nova_idade = st.number_input("Idade:", min_value=0, max_value=120, value=30)
        nova_cidade = st.selectbox("Cidade:", ["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Porto Alegre"])
        nova_profissao = st.selectbox("Profissão:", ["Engenheiro", "Professor", "Médico", "Advogado"])
        submit = st.form_submit_button("Inserir Registro")

        if submit:
            if novo_nome.strip() == "":
                st.error("O campo 'Nome' não pode estar vazio!")
            else:
                query = text("""
                    INSERT INTO pessoas (nome, idade, cidade, profissao)
                    VALUES (:nome, :idade, :cidade, :profissao)
                """)
                try:
                    with engine.begin() as conn:
                        conn.execute(query, {
                            "nome": novo_nome,
                            "idade": nova_idade,
                            "cidade": nova_cidade,
                            "profissao": nova_profissao
                        })
                    st.success("Registro inserido com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao inserir registro: {e}")

# 3. Alterar Registro
elif menu == "Alterar Registro":
    st.header("Alterar Registro")
    df = pd.read_sql("SELECT * FROM pessoas", con=engine)
    if df.empty:
        st.error("Não há registros para alterar.")
    else:
        registro_id = st.selectbox("Selecione o ID do registro para alterar:", df["id"])
        registro_atual = df[df["id"] == registro_id]
        st.write("Dados atuais:")
        st.write(registro_atual)

        with st.form("alterar_form"):
            novo_nome = st.text_input("Nome:", value=registro_atual["nome"].values[0])
            nova_idade = st.number_input("Idade:", min_value=0, max_value=120, value=int(registro_atual["idade"].values[0]))
            nova_cidade = st.selectbox(
                "Cidade:",
                ["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Porto Alegre"],
                index=["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Porto Alegre"].index(registro_atual["cidade"].values[0])
            )
            nova_profissao = st.selectbox(
                "Profissão:",
                ["Engenheiro", "Professor", "Médico", "Advogado"],
                index=["Engenheiro", "Professor", "Médico", "Advogado"].index(registro_atual["profissao"].values[0])
            )
            submit = st.form_submit_button("Alterar Registro")

            if submit:
                if novo_nome.strip() == "":
                    st.error("O campo 'Nome' não pode estar vazio!")
                else:
                    query = text("""
                        UPDATE pessoas
                        SET nome = :nome, idade = :idade, cidade = :cidade, profissao = :profissao
                        WHERE id = :id
                    """)
                    try:
                        with engine.begin() as conn:
                            conn.execute(query, {
                                "nome": novo_nome,
                                "idade": nova_idade,
                                "cidade": nova_cidade,
                                "profissao": nova_profissao,
                                "id": registro_id
                            })
                        st.success("Registro atualizado com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao atualizar registro: {e}")

# 4. Excluir Registro
elif menu == "Excluir Registro":
    st.header("Excluir Registro")
    df = pd.read_sql("SELECT * FROM pessoas", con=engine)
    if df.empty:
        st.error("Não há registros para excluir.")
    else:
        registro_id = st.selectbox("Selecione o ID do registro para excluir:", df["id"])
        if st.button("Excluir Registro"):
            query = text("DELETE FROM pessoas WHERE id = :id")
            try:
                with engine.begin() as conn:
                    conn.execute(query, {"id": registro_id})
                st.success("Registro excluído com sucesso!")
            except Exception as e:
                st.error(f"Erro ao excluir registro: {e}")
