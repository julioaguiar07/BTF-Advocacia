import streamlit as st
import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env

DATABASE_URL = os.getenv("DATABASE_URL")
try:
    conn = psycopg2.connect(DATABASE_URL)
    print("Conexão bem-sucedida!")
    conn.close()
except Exception as e:
    print(f"Erro ao conectar ao banco de dados: {e}")

# Configuração de estilo
st.set_page_config(page_title="Gestão de Processos", layout="wide")
st.markdown(
    """
    <style>
    .main-container {
        background-color: #f9f9f9;
        padding: 20px;
    }
    .sidebar {
        background-color: #0E2C4E;
        color: white;
    }
    .process-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        color: #333333;
    }
    .process-card h4 {
        color: #0E2C4E;
        margin: 0;
    }
    .metric-box {
        background-color: #CF8C28;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-box h3 {
        margin: 0;
        color: #ffffff;
        font-size: 24px;
        font-weight: bold;
    }
    .metric-box p {
        margin: 0;
        font-size: 20px;
        color: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Função para conectar ao banco de dados PostgreSQL
def conectar_db():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))  # Usa a URL do banco de dados
    return conn

# Função para criar a tabela de processos (se não existir)
def criar_tabela():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS processos (
        id SERIAL PRIMARY KEY,
        numero_processo INTEGER NOT NULL,
        data TEXT NOT NULL,
        acao TEXT NOT NULL,
        instancia TEXT NOT NULL,
        fase TEXT NOT NULL,
        cliente TEXT NOT NULL,
        empresa TEXT NOT NULL,
        advogado TEXT NOT NULL,
        status TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

# Função para adicionar um processo
def adicionar_processo(numero_processo, data, acao, instancia, fase, cliente, empresa, advogado, status):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO processos (numero_processo, data, acao, instancia, fase, cliente, empresa, advogado, status)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (numero_processo, data, acao, instancia, fase, cliente, empresa, advogado, status))
    conn.commit()
    conn.close()

# Função para buscar processos
def buscar_processos(cpf_cnpj=None, status=None):
    conn = conectar_db()
    cursor = conn.cursor()
    query = 'SELECT * FROM processos WHERE 1=1'
    params = []
    if cpf_cnpj:
        query += ' AND cliente = %s'
        params.append(cpf_cnpj)
    if status:
        query += ' AND status = %s'
        params.append(status)
    cursor.execute(query, tuple(params))
    resultados = cursor.fetchall()
    conn.close()
    return resultados

# Função para atualizar o status de um processo
def atualizar_processo(id_processo, novo_status):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE processos SET status = %s WHERE id = %s', (novo_status, id_processo))
    conn.commit()
    conn.close()

# Função para excluir um processo
def excluir_processo(id_processo):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM processos WHERE id = %s', (id_processo,))
    conn.commit()
    conn.close()

# Função para contar processos por status
def contar_processos_por_status():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('SELECT status, COUNT(*) FROM processos GROUP BY status')
    contagem = cursor.fetchall()
    conn.close()
    return {status: count for status, count in contagem}

# Sidebar
st.sidebar.title("BTF ADVOCACIA ⚖️")
st.sidebar.text("Gestão de Processos")

opcao = st.sidebar.radio("Páginas", ["Início", "Cadastrar Processos"])

if opcao == "Início":
    # Página inicial
    st.title("BTF ADVOCACIA")
    st.subheader("Consulta e Atualização de Processos")

    # Exibir contagem de processos por status
    contagem = contar_processos_por_status()
    st.write("### Resumo dos Processos")
    col1, col2, col3 = st.columns(3)
    col1.markdown(f"""<div class='metric-box'><h3>Concluídos</h3><p>{contagem.get('Concluído', 0)}</p></div>""", unsafe_allow_html=True)
    col2.markdown(f"""<div class='metric-box'><h3>Em Andamento</h3><p>{contagem.get('Em andamento', 0)}</p></div>""", unsafe_allow_html=True)
    col3.markdown(f"""<div class='metric-box'><h3>Finalizados</h3><p>{contagem.get('Finalizado', 0)}</p></div>""", unsafe_allow_html=True)

    # Filtros
    st.write("### Filtrar Processos")
    filtro_status = st.selectbox("Filtrar por Situação", ["", "Em andamento", "Concluído", "Finalizado"])
    filtro_cpf_cnpj = st.text_input("Buscar por CPF ou CNPJ do Cliente")

    resultados = buscar_processos(cpf_cnpj=filtro_cpf_cnpj, status=filtro_status if filtro_status else None)

    # Exibir processos encontrados
    st.write("### Processos Encontrados")
    for processo in resultados:
        with st.expander(f"Processo nº {processo[1]} - Cliente: {processo[6]}"):
            st.write(f"**Data:** {processo[2]}")
            st.write(f"**Ação:** {processo[3]}")
            st.write(f"**Instância:** {processo[4]}")
            st.write(f"**Fase:** {processo[5]}")
            st.write(f"**Empresa:** {processo[7]}")
            st.write(f"**Advogado:** {processo[8]}")
            st.write(f"**Status Atual:** {processo[9]}")

            novo_status = st.selectbox("Atualizar Situação", ["Em andamento", "Concluído", "Finalizado"], key=f"status_{processo[0]}")
            if st.button("Atualizar", key=f"atualizar_{processo[0]}"):
                atualizar_processo(processo[0], novo_status)
                st.success("Situação atualizada com sucesso!")

            if st.button("Excluir Processo", key=f"excluir_{processo[0]}"):
                excluir_processo(processo[0])
                st.success("Processo excluído com sucesso!")
                st.experimental_rerun()  # Recarrega a página para atualizar a lista

elif opcao == "Cadastrar Processos":
    # Página de cadastro de processos
    with st.form("form_cadastro"):
        st.title("Cadastrar Novo Processo")
        numero_processo = st.number_input("Nº do Processo", min_value=1)
        data = st.text_input("Data (ex: 2022-10-11 - 2023-09-03)")
        acao = st.text_input("Ação")
        instancia = st.text_input("Instância")
        fase = st.text_input("Fase")
        cliente = st.text_input("Cliente (CPF ou CNPJ)")
        empresa = st.text_input("Empresa")
        advogado = st.text_input("Advogado")
        status = st.selectbox("Situação", ["Em andamento", "Concluído", "Finalizado"])
        enviar = st.form_submit_button("Cadastrar Processo")

        if enviar:
            adicionar_processo(numero_processo, data, acao, instancia, fase, cliente, empresa, advogado, status)
            st.success("Processo cadastrado com sucesso!")

# Criar a tabela (se não existir)
criar_tabela()
