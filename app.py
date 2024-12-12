import streamlit as st
import pandas as pd
import psycopg2
from datetime import date
from datetime import datetime
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
import unidecode

# Configuração da página
st.set_page_config(
    page_title="Financeiro LBB/LBS",
    page_icon="https://site.labrasaburger.com.br/wp-content/uploads/2021/09/logo.png",
    layout="wide"
)

# CSS customizado para a página
st.markdown(
    """
    <style>
    .stApp {
        background: rgba(0, 0, 0, 0.5) url('https://site.labrasaburger.com.br/wp-content/uploads/2021/09/logo.png') no-repeat center center fixed; 
        background-size: 200px;
        font-family: 'Roboto', sans-serif;
    }
    .sidebar .sidebar-content {
        transition: all 0.5s ease;
    }
    .sidebar:hover .sidebar-content {
        transform: scale(1.05);
    }
    .emoji {
        font-size: 2em;
        transition: transform 0.3s;
    }
    .emoji:hover {
        transform: rotate(20deg);
    }
    .pulse {
        display: inline-block;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.1);
        }
        100% {
            transform: scale(1);
        }
    }
    .stForm {
        background-color: rgba(211, 211, 211, 0.5);
        padding: 20px;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Conexão com a base de dados PostgreSQL
DATABASE_URL = "postgresql://postgres.fmsgllkgkzhytjryzctp:%40baconese%2Bfritas@aws-0-sa-east-1.pooler.supabase.com:6543/postgres"
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
c = conn.cursor()

# CSS do Sidebar
def sidebar_menu():
    # CSS customizado para o sidebar
    st.markdown(
        """
        <style>
        .sidebar .sidebar-content {
            background-color: #FF5733;  /* Cor de fundo do sidebar */
            padding: 10px;
            position: fixed;
            width: 100%;
            height: 100%;
            top: 0;
            left: 0;
            z-index: 1000;
        }
        .sidebar .sidebar-content .sidebar-header {
            display: flex;
            align-items: center;
            justify-content: flex-start;
            color: white;
            font-size: 18px; /* Diminui o tamanho do título */
            padding-top: 20px; /* Adiciona padding para ajustar o espaço */
        }
        .sidebar .sidebar-content .option-menu {
            margin-top: 20px;
        }
        .sidebar .sidebar-content .option-menu a {
            background: rgba(255, 255, 255, 0.3);
            color: white;
            font-weight: bold;
            padding: 6px; /* Diminui o padding das opções */
            border-radius: 5px;
            margin-bottom: 6px; /* Diminui o espaçamento entre as opções */
            display: block;
            text-align: left; /* Alinha o texto à esquerda */
            text-decoration: none;
            font-size: 14px; /* Diminui o tamanho da fonte das opções */
        }
        .sidebar .sidebar-content .option-menu a:hover {
            background: white;
            color: #FF5733;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Sidebar com o título e o menu de opções
    with st.sidebar:
        st.markdown(
            '<div class="sidebar-header">'
            '<span>📊 Financeiro La Brasa</span>'
            '</div>',
            unsafe_allow_html=True
        )
        
        selected = option_menu(
            menu_title="Menu",
            options=["Dashboard Financeiro", "Registros Financeiros"],
            icons=["bar-chart", "file-text"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "5!important", "background-color": "#FF5733"},
                "icon": {"color": "white", "font-size": "18px"},  # Diminui o tamanho dos ícones
                "nav-link": {"font-size": "14px", "text-align": "left", "margin": "0px", "--hover-color": "#FFF"},  # Diminui o tamanho do texto das opções
                "nav-link-selected": {"background-color": "white", "color": "#FF5733"},
            }
        )
    
    return selected

# Funções de criação e carregamento de tabelas
# Funções de criação e carregamento de tabelas
def criar_tabela_recebedores(c):
    c.execute('''
        CREATE TABLE IF NOT EXISTS recebedores (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(30) UNIQUE NOT NULL CHECK (nome ~ '^[A-Za-z ]+$'),
            tipo VARCHAR(20) NOT NULL
        );
    ''')
    conn.commit()

def carregar_recebedores():
    df_recebedores = pd.read_sql('SELECT * FROM recebedores', conn)
    return df_recebedores

# Função para remover acentos
def remover_acentos(nome):
    return unidecode.unidecode(nome)

# Função para validar o nome
def validar_nome(nome):
    import re
    nome = remover_acentos(nome)
    if not re.match(r'^[A-Za-z ]+$', nome):
        return False, nome
    return True, nome

# Função para verificar duplicidade
def verificar_duplicidade(nome):
    c.execute('SELECT COUNT(*) FROM recebedores WHERE nome = %s', (nome,))
    count = c.fetchone()[0]
    return count > 0

# Função para registro de recebedores
def registrar_recebedor(nome, tipo):
    valido, nome_sem_acentos = validar_nome(nome)
    if not valido:
        st.error("Nome inválido! O nome deve conter apenas letras e espaços, sem números ou caracteres especiais.")
        return
    if verificar_duplicidade(nome_sem_acentos):
        st.error("Nome já existe! Por favor, escolha um nome diferente.")
        return
    try:
        c.execute('''
            INSERT INTO recebedores (nome, tipo)
            VALUES (%s, %s)
        ''', (nome_sem_acentos, tipo))
        conn.commit()
        st.success("Recebedor registrado com sucesso!")
        st.rerun()
    except Exception as e:
        st.error(f"Erro ao registrar: {e}")

# Função para editar recebedores
def editar_recebedor(id, novo_nome, novo_tipo):
    valido, nome_sem_acentos = validar_nome(novo_nome)
    if not valido:
        st.error("Nome inválido! O nome deve conter apenas letras e espaços, sem números ou caracteres especiais.")
        return
    if verificar_duplicidade(nome_sem_acentos):
        st.error("Nome já existe! Por favor, escolha um nome diferente.")
        return
    try:
        if id:
            c.execute('''
                UPDATE recebedores
                SET nome = %s, tipo = %s
                WHERE id = %s
            ''', (nome_sem_acentos, novo_tipo, int(id)))  # Convertendo o id para int
            conn.commit()
            st.success("Recebedor atualizado com sucesso!")
            st.rerun()
        else:
            st.error("Recebedor não encontrado!")
    except Exception as e:
        st.error(f"Erro ao atualizar: {e}")

# Função para excluir recebedores
def excluir_recebedor(id):
    try:
        if id:
            c.execute('''
                DELETE FROM recebedores
                WHERE id = %s
            ''', (int(id),))  # Convertendo o id para int
            conn.commit()
            st.success("Recebedor excluído com sucesso!")
            st.rerun()
        else:
            st.error("Recebedor não encontrado!")
    except Exception as e:
        st.error(f"Erro ao excluir: {e}")



# Criação da tabela de transacoes
def criar_tabela_transacoes(c):
    c.execute('''
        CREATE TABLE IF NOT EXISTS transacoes (
            id SERIAL PRIMARY KEY,
            data_pagamento DATE NOT NULL,
            fluxo VARCHAR(10) NOT NULL,
            recebedor VARCHAR(30) NOT NULL,
            forma VARCHAR(10) NOT NULL,
            valor NUMERIC NOT NULL,
            descricao VARCHAR(200),
            lojas VARCHAR(100) NOT NULL
        );
    ''')
    conn.commit()



# Função para verificar duplicidade
def verificar_duplicidade(data_pagamento, fluxo, recebedor, forma, valor, descricao, lojas):
    c.execute('''
        SELECT COUNT(*)
        FROM transacoes
        WHERE data_pagamento = %s AND fluxo = %s AND recebedor = %s AND forma = %s AND valor = %s AND descricao = %s AND lojas = %s
    ''', (data_pagamento, fluxo, recebedor, forma, valor, descricao, lojas))
    count = c.fetchone()[0]
    return count > 0


# Função para tratamento de dados xlsx
def tratar_arquivo_xlsx(file):
    df = pd.read_excel(file)
    
    # Verificar se as colunas esperadas estão presentes
    colunas_esperadas = ['pedido', 'abertura', 'fechamento', 'mesa', 'comanda', 'garcom', 'servico', 'tipo_pagamento', 'valor_pagamento', 'desconto', 'valor_consumo', 'troco', 'valor_total']
    if not all(coluna in df.columns for coluna in colunas_esperadas):
        st.error("O arquivo deve conter as colunas: 'pedido', 'abertura', 'fechamento', 'mesa', 'comanda', 'garcom', 'servico', 'tipo_pagamento', 'valor_pagamento', 'desconto', 'valor_consumo', 'troco', 'valor_total'. Envie um relatório correto do Abrahão.")
        return None, None, None, None
    
    # Remover colunas indesejadas
    colunas_remover = ['pedido', 'abertura', 'mesa', 'comanda', 'garcom', 'servico', 'desconto', 'valor_consumo', 'troco', 'valor_pagamento']
    df = df.drop(columns=colunas_remover)
    
    # Remover colunas vazias e linhas com células vazias
    df = df.dropna(axis=1, how='all')
    df = df.dropna(axis=0, how='any')
    
    # Separar data e hora da coluna fechamento
    df[['data', 'hora']] = df['fechamento'].str.split(' ', expand=True)
    df = df.drop(columns=['fechamento'])

    # Converter valores de pagamento com descontos e arredondar para 2 casas decimais
    df['valor_total'] = df.apply(lambda row: round(row['valor_total'] * (1 - 0.0179), 2) if row['tipo_pagamento'] == 'Débito' else round(row['valor_total'] * (1 - 0.0274), 2) if row['tipo_pagamento'] == 'Crédito' else round(row['valor_total'], 2), axis=1)
    
    # Classificar transações por loja com base na hora
    df['loja'] = df['hora'].apply(lambda x: 'La Brasa Burger' if datetime.strptime(x, '%H:%M').hour > 16 and datetime.strptime(x, '%H:%M').hour < 24 else 'La Brasa Steak')
    
    # Calcular os totais dos descontos
    total_desconto_debito = round(df[df['tipo_pagamento'] == 'Débito']['valor_total'].sum() * 0.0179, 2)
    total_desconto_credito = round(df[df['tipo_pagamento'] == 'Crédito']['valor_total'].sum() * 0.0274, 2)
    total_desconto = total_desconto_debito + total_desconto_credito
    
    return df, total_desconto_debito, total_desconto_credito, total_desconto



# Função para salvar transação diretamente na tabela
def salvar_transacoes(df):
    transacoes_salvas = 0
    transacoes_duplicadas = 0

    for index, row in df.iterrows():
        data_pagamento = datetime.strptime(row['data'], '%d/%m/%Y').strftime('%Y-%m-%d')
        fluxo = 'Entrada'
        recebedor = row['loja']
        forma = 'Abrahão'
        valor = row['valor_total']
        descricao = row['tipo_pagamento']
        lojas = recebedor

        if not verificar_duplicidade(data_pagamento, fluxo, recebedor, forma, valor, descricao, lojas):
            try:
                c.execute('''
                    INSERT INTO transacoes (data_pagamento, fluxo, recebedor, forma, valor, descricao, lojas)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (data_pagamento, fluxo, recebedor, forma, valor, descricao, lojas))
                conn.commit()
                transacoes_salvas += 1
            except Exception as e:
                st.error(f"Erro ao salvar transação: {e}")
        else:
            transacoes_duplicadas += 1

    return transacoes_salvas, transacoes_duplicadas

# Interface do Streamlit para registro de recebedores
def form_recebedores():
    st.markdown(
        """
        <style>
        .title {
            font-size: 2.5em;
            font-weight: bold;
            color: #FF5733;
            text-align: center;
            margin-top: 20px;
        }
        .emoji {
            display: inline-block;
            animation: bounce 2s infinite;
        }
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        </style>
        <h1 class="title">Registro de Recebedores <span class="emoji">📝</span></h1>
        """,
        unsafe_allow_html=True
    )

    with st.form("form_recebedores"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome", help="Insira o nome do recebedor (máximo 30 caracteres, sem números ou caracteres especiais) 📝")
        
        with col2:
            tipo = st.selectbox("Tipo", ["", "Custo Fixo", "Entregador", "Fornecedor", "Freelancer", "Loja", "Mercado", "Outros", "Segurança", "Serviços", "Uber Funcionarios"], help="Selecione o tipo de recebedor 🏷️")

        if st.form_submit_button("Salvar"):
            if nome and tipo:
                registrar_recebedor(nome, tipo)
            else:
                st.error("Todos os campos são obrigatórios!")

        with st.expander("Editar Recebedor ✏️"):
            df_recebedores = carregar_recebedores()
            recebedor_selecionado = st.selectbox("Selecione o recebedor para editar", df_recebedores['nome'])
            novo_nome = st.text_input("Novo Nome", help="Insira o novo nome do recebedor (máximo 30 caracteres, sem números ou caracteres especiais) 📝")
            novo_tipo = st.selectbox("Novo Tipo", ["", "Custo Fixo", "Entregador", "Fornecedor", "Freelancer", "Loja", "Mercado", "Outros", "Segurança", "Serviços", "Uber Funcionarios"], help="Selecione o novo tipo de recebedor 🏷️")

            if st.form_submit_button("Salvar Alterações"):
                if novo_nome and novo_tipo:
                    if not recebedor_selecionado:
                        st.error("Recebedor não encontrado!")
                    else:
                        recebedor_id = df_recebedores[df_recebedores['nome'] == recebedor_selecionado]['id'].values[0]
                        editar_recebedor(recebedor_id, novo_nome, novo_tipo)
                else:
                    st.error("Todos os campos são obrigatórios para editar!")

        with st.expander("Excluir Recebedor 🗑️"):
            df_recebedores = carregar_recebedores()
            recebedor_selecionado = st.selectbox("Selecione o recebedor para excluir", df_recebedores['nome'])
            
            if st.form_submit_button("Excluir"):
                if not recebedor_selecionado:
                    st.error("Por favor, selecione um recebedor para excluir!")
                else:
                    recebedor_id = df_recebedores[df_recebedores['nome'] == recebedor_selecionado]['id'].values[0]
                    excluir_recebedor(recebedor_id)

        with st.expander("Lista de Recebedores 📋"):
            df_recebedores = carregar_recebedores()
            st.write(df_recebedores)




# Função para carregar as transacoes
def carregar_transacoes():
    df_transacoes = pd.read_sql('SELECT * FROM transacoes', conn)
    return df_transacoes


# Função para registrar as transacoes
def registrar_transacao(data_pagamento, fluxo, recebedor, forma, valor, descricao, lojas):
    if fluxo == 'Saída':
        valor = -abs(valor)
    try:
        lojas_str = ', '.join(lojas)
        c.execute('''
            INSERT INTO transacoes (data_pagamento, fluxo, recebedor, forma, valor, descricao, lojas)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (data_pagamento, fluxo, recebedor, forma, valor, descricao, lojas_str))
        conn.commit()
        st.success("Transação registrada com sucesso!")
        st.rerun()
    except Exception as e:
        st.error(f"Erro ao registrar transação: {e}")


# Função para excluir as transacoes
def excluir_transacoes(ids):
    try:
        c.execute('''
            DELETE FROM transacoes
            WHERE id = ANY(%s)
        ''', (ids,))
        conn.commit()
        st.success("Transações excluídas com sucesso!")
        st.rerun()
    except Exception as e:
        st.error(f"Erro ao excluir transações: {e}")




# Função para o formulário de pagamentos
def form_transacoes():
    st.markdown(
        """
        <style>
        .transacoes-title {
            font-size: 2.5em;
            font-weight: bold;
            color: #FF5733;
            text-align: center;
            margin-top: 20px;
        }
        .transacoes-emoji {
            display: inline-block;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        </style>
        <h1 class="transacoes-title">Registro de Transações <span class="transacoes-emoji">💰</span></h1>
        """,
        unsafe_allow_html=True
    )

    with st.form("form_transacoes"):
        col1, col2, col3 = st.columns(3)
        col4, col5, col6 = st.columns(3)

        with col1:
            data_pagamento = st.date_input("Data de Pagamento", help="Selecione a data do pagamento", min_value=date(2020, 1, 1), max_value=date(2040, 12, 31), value=date.today(), label_visibility='visible')
        with col2:
            fluxo = st.selectbox("Fluxo", ["Entrada", "Saída"], help="Selecione o fluxo do pagamento")
        with col3:
            df_recebedores = carregar_recebedores()
            recebedor = st.selectbox("Recebedor", df_recebedores['nome'], help="Selecione o recebedor")

        with col4:
            forma = st.selectbox("Forma", ["Abrahão", "Consumer", "Crédito", "Débito", "Dinheiro", "Pix"], help="Selecione a forma de pagamento")
        with col5:
            valor = st.number_input("Valor (R$)", min_value=0.01, format="%.2f", help="Insira o valor do pagamento")
        with col6:
            lojas = st.multiselect("Loja", ["La Brasa Burger", "La Brasa Steak"], help="Selecione a loja")

        descricao = st.text_input("Descrição", max_chars=200, help="Insira uma descrição para o pagamento (opcional)")

        if st.form_submit_button("Salvar"):
            if data_pagamento and fluxo and recebedor and forma and valor and lojas:
                registrar_transacao(data_pagamento, fluxo, recebedor, forma, valor, descricao, lojas)
            else:
                st.error("Todos os campos obrigatórios devem ser preenchidos!")

        with st.expander("Excluir Transações 🗑️"):
            df_transacoes = carregar_transacoes()
            transacoes_selecionadas = st.multiselect("Selecione as transações para excluir", df_transacoes['id'])
            
            if st.form_submit_button("Excluir Transações"):
                if transacoes_selecionadas:
                    excluir_transacoes(transacoes_selecionadas)
                else:
                    st.error("Selecione pelo menos uma transação para excluir")

        with st.expander("Lista de Transações 📋"):
            df_transacoes = carregar_transacoes()
            st.write(df_transacoes)

            total_entrada = df_transacoes[df_transacoes['fluxo'] == 'Entrada']['valor'].sum()
            total_saida = df_transacoes[df_transacoes['fluxo'] == 'Saída']['valor'].sum()

            st.markdown(f"**Total de Entradas:** <span style='color:green'>{total_entrada:.2f} R$</span>", unsafe_allow_html=True)
            st.markdown(f"**Total de Saídas:** <span style='color:red'>{total_saida:.2f} R$</span>", unsafe_allow_html=True)



# Função para o formulário de upload e processamento de arquivo xlsx
def form_upload_xlsx():
    st.markdown(
        """
        <style>
        .upload-title {
            font-size: 2.5em;
            font-weight: bold;
            color: #FF5733;
            text-align: center;
            margin-top: 20px;
        }
        .upload-emoji {
            display: inline-block;
            animation: bounce 2s infinite;
        }
        @keyframes bounce {
            0%, 100% { transform: scale(1); }
            50% { transform: translateY(-10px); }
        }
        </style>
        <h1 class="upload-title">Upload de Arquivo <img src="https://www.abrahao.com.br/images/abrahao-goomer-logo.svg" alt="Logo" height="40"></h1>
        """,
        unsafe_allow_html=True
    )
    
    file = st.file_uploader("Upload do arquivo XLSX", type=["xlsx"], help="Escolha o arquivo XLSX para fazer o upload")
    
    if file is not None:
        df, total_desconto_debito, total_desconto_credito, total_desconto = tratar_arquivo_xlsx(file)
        
        if df is not None:
            st.write("Tabela de Transações Tratadas")
            st.dataframe(df)

            total_la_brasa_steak = df[df['loja'] == 'La Brasa Steak']['valor_total'].sum()
            total_la_brasa_burger = df[df['loja'] == 'La Brasa Burger']['valor_total'].sum()

            st.markdown(f"**Total La Brasa Steak:** <span style='color:green'>{total_la_brasa_steak:.2f} R$</span>", unsafe_allow_html=True)
            st.markdown(f"**Total La Brasa Burger:** <span style='color:green'>{total_la_brasa_burger:.2f} R$</span>", unsafe_allow_html=True)

            st.markdown(f"**Total Desconto Débito:** <span style='color:red'>-{total_desconto_debito:.2f} R$</span>", unsafe_allow_html=True)
            st.markdown(f"**Total Desconto Crédito:** <span style='color:red'>-{total_desconto_credito:.2f} R$</span>", unsafe_allow_html=True)
            st.markdown(f"**Total Geral de Descontos:** <span style='color:red'>-{total_desconto:.2f} R$</span>", unsafe_allow_html=True)

            if st.button("Limpar"):
                st.cache_data.clear()
                st.rerun()

            if st.button("Salvar"):
                transacoes_salvas, transacoes_duplicadas = salvar_transacoes(df)
                
                st.success(f"Transações salvas com sucesso: {transacoes_salvas}")
                if transacoes_duplicadas > 0:
                    st.warning(f"Transações duplicadas não salvas: {transacoes_duplicadas}")
                st.rerun()



# Função para calcular os valores de faturamento
def calcular_faturamento(df_transacoes):
    # Entradas e Saídas La Brasa Steak
    entradas_steak = df_transacoes[df_transacoes['lojas'].str.contains('La Brasa Steak')]
    total_entrada_steak = entradas_steak[entradas_steak['fluxo'] == 'Entrada']['valor'].sum()
    total_saida_steak = entradas_steak[entradas_steak['fluxo'] == 'Saída']['valor'].sum()
    # Total Faturamento La Brasa Steak
    faturamento_steak = total_entrada_steak + total_saida_steak

    # Entradas e Saídas La Brasa Burger
    entradas_burger = df_transacoes[df_transacoes['lojas'].str.contains('La Brasa Burger')]
    total_entrada_burger = entradas_burger[entradas_burger['fluxo'] == 'Entrada']['valor'].sum()
    total_saida_burger = entradas_burger[entradas_burger['fluxo'] == 'Saída']['valor'].sum()
    # Total Faturamento La Brasa Burger
    faturamento_burger = total_entrada_burger + total_saida_burger

    # Totais Gerais
    total_entrada = total_entrada_steak + total_entrada_burger
    total_saida = total_saida_steak + total_saida_burger
    faturamento_total = total_entrada + total_saida

    return total_entrada_steak, total_saida_steak, faturamento_steak, total_entrada_burger, total_saida_burger, faturamento_burger, total_entrada, total_saida, faturamento_total


# Função para exibir o Dashboard
# Função para exibir o Dashboard
# Função para exibir o Dashboard
# Função para exibir o Dashboard
def exibir_dashboard():
    df_transacoes = carregar_transacoes()  # Função que carrega as transações do banco de dados

    total_entrada_steak, total_saida_steak, faturamento_steak, total_entrada_burger, total_saida_burger, faturamento_burger, total_entrada, total_saida, faturamento_total = calcular_faturamento(df_transacoes)

    st.markdown(
        """
        <style>
        .dashboard-container {
            display: flex;
            justify-content: space-between;
            padding: 20px;
            background-color: rgba(220, 220, 220, 0.8);
            border-radius: 15px;
        }
        .dashboard-card {
            text-align: center;
            width: 30%;
        }
        .dashboard-card img {
            width: 100px;
            height: 100px;
        }
        .burger-img {
            width: 100px;
            height: 80px;
        }
        .dashboard-card h3 {
            margin-top: 20px;
        }
        .faturamento-total {
            display: flex;
            justify-content: center;
        }
        .faturamento-total img {
            width: 100px;
            height: 100px;
            margin: 0 10px;
        }
        .positive {
            color: green;
        }
        .negative {
            color: red;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="dashboard-container">
            <div class="dashboard-card">
                <img src="https://mir-s3-cdn-cf.behance.net/projects/404/089fb5201452905.6729456c257a1.jpg" alt="La Brasa Steak">
                <h3>La Brasa Steak</h3>
                <p><strong>Total de Entradas:</strong> <span class="positive">R$ {total_entrada_steak:.2f}</span></p>
                <p><strong>Total de Saídas:</strong> <span class="negative">R$ {total_saida_steak:.2f}</span></p>
                <p><strong>Faturamento:</strong> <span class="{ 'positive' if faturamento_steak >= 0 else 'negative' }">
                    R$ {faturamento_steak:.2f} {'&#x25B2;' if faturamento_steak >= 0 else '&#x25BC;'}</span>
                </p>
            </div>
            <div class="dashboard-card">
                <div class="faturamento-total">
                    <img src="https://mir-s3-cdn-cf.behance.net/projects/404/089fb5201452905.6729456c257a1.jpg" alt="La Brasa Steak">
                    <img src="https://site.labrasaburger.com.br/wp-content/uploads/2021/09/logo.png" alt="La Brasa Burger" class="burger-img">
                </div>
                <h3>Faturamento Total</h3>
                <p><strong>Total de Entradas:</strong> <span class="positive">R$ {total_entrada:.2f}</span></p>
                <p><strong>Total de Saídas:</strong> <span class="negative">R$ {total_saida:.2f}</span></p>
                <p><strong>Faturamento Total:</strong> <span class="{ 'positive' if faturamento_total >= 0 else 'negative' }">
                    R$ {faturamento_total:.2f} {'&#x25B2;' if faturamento_total >= 0 else '&#x25BC;'}</span>
                </p>
            </div>
            <div class="dashboard-card">
                <img src="https://site.labrasaburger.com.br/wp-content/uploads/2021/09/logo.png" alt="La Brasa Burger" class="burger-img">
                <h3>La Brasa Burger</h3>
                <p><strong>Total de Entradas:</strong> <span class="positive">R$ {total_entrada_burger:.2f}</span></p>
                <p><strong>Total de Saídas:</strong> <span class="negative">R$ {total_saida_burger:.2f}</span></p>
                <p><strong>Faturamento:</strong> <span class="{ 'positive' if faturamento_burger >= 0 else 'negative' }">
                    R$ {faturamento_burger:.2f} {'&#x25B2;' if faturamento_burger >= 0 else '&#x25BC;'}</span>
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )




# Função para exibir o gráfico de linha do tempo
# Função para exibir o gráfico de linha do tempo
def exibir_grafico(df_transacoes):
    st.markdown(
        """
        <style>
        .grafico-container {
            padding: 20px;
            background-color: rgba(220, 220, 220, 0.8);
            border-radius: 15px;
        }
        .positive {
            color: green;
        }
        .negative {
            color: red;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='grafico-container'>", unsafe_allow_html=True)

    # Converter a coluna 'data_pagamento' para datetime
    df_transacoes['data_pagamento'] = pd.to_datetime(df_transacoes['data_pagamento'])

    # Filtros
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        data_inicio = st.date_input("Data de Início", value=df_transacoes['data_pagamento'].min().date(), help="Selecione a data inicial")
    with col2:
        data_fim = st.date_input("Data de Fim", value=df_transacoes['data_pagamento'].max().date(), help="Selecione a data final")
    with col3:
        fluxo = st.selectbox("Fluxo", ["Todas", "Entrada", "Saída"], help="Selecione o tipo de fluxo")

    # Converter as datas para datetime
    data_inicio = pd.to_datetime(data_inicio)
    data_fim = pd.to_datetime(data_fim)

    # Filtrar os dados conforme os filtros
    if fluxo != "Todas":
        df_filtrado = df_transacoes[(df_transacoes['data_pagamento'] >= data_inicio) & (df_transacoes['data_pagamento'] <= data_fim) & (df_transacoes['fluxo'] == fluxo)]
    else:
        df_filtrado = df_transacoes[(df_transacoes['data_pagamento'] >= data_inicio) & (df_transacoes['data_pagamento'] <= data_fim)]

    if df_filtrado.empty:
        st.warning("Não há dados para o período selecionado.")
        return

    # Agrupar por data e somar os valores
    df_agrupado_entrada = df_filtrado[df_filtrado['fluxo'] == 'Entrada'].groupby('data_pagamento')['valor'].sum().reset_index()
    df_agrupado_saida = df_filtrado[df_filtrado['fluxo'] == 'Saída'].groupby('data_pagamento')['valor'].sum().reset_index()

    # Criar gráfico de linha
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df_agrupado_entrada['data_pagamento'], y=df_agrupado_entrada['valor'], mode='lines+markers', name='Entradas', line=dict(color='green')))
    fig.add_trace(go.Scatter(x=df_agrupado_saida['data_pagamento'], y=df_agrupado_saida['valor'], mode='lines+markers', name='Saídas', line=dict(color='red')))

    fig.update_layout(title='Fluxo ao Longo do Tempo', xaxis_title='Data', yaxis_title='Valor (R$)')
    st.plotly_chart(fig)

    # Calcular o total de entradas, saídas e total geral no período filtrado
    total_entrada = df_filtrado[df_filtrado['fluxo'] == 'Entrada']['valor'].sum()
    total_saida = df_filtrado[df_filtrado['fluxo'] == 'Saída']['valor'].sum()
    total_geral = total_entrada + total_saida

    st.markdown(f"**Total de Entradas no Período:** <span class='positive'>{total_entrada:.2f} R$</span>", unsafe_allow_html=True)
    st.markdown(f"**Total de Saídas no Período:** <span class='negative'>{total_saida:.2f} R$</span>", unsafe_allow_html=True)
    st.markdown(f"**Total Geral no Período:** <span class='{ 'positive' if total_geral >= 0 else 'negative' }'>{total_geral:.2f} R$</span>", unsafe_allow_html=True)

    # Mostrar maiores motivos
    maior_motivo_entrada = df_filtrado[df_filtrado['fluxo'] == 'Entrada'].groupby('recebedor')['valor'].sum().reset_index()
    maior_motivo_saida = df_filtrado[df_filtrado['fluxo'] == 'Saída'].groupby('recebedor')['valor'].sum().reset_index()

    col1, col2 = st.columns(2)
    with col1:
        if not maior_motivo_entrada.empty:
            maior_motivo_entrada = maior_motivo_entrada.sort_values(by='valor', ascending=False).iloc[0]
            st.markdown(f"<strong>Maior Motivo para Entrada:</strong> <span class='positive'>{maior_motivo_entrada['recebedor']} (R$ {maior_motivo_entrada['valor']:.2f})</span>", unsafe_allow_html=True)
        else:
            st.markdown("<strong>Maior Motivo para Entrada:</strong> <span class='positive'>Nenhum</span>", unsafe_allow_html=True)

    with col2:
        if not maior_motivo_saida.empty:
            maior_motivo_saida = maior_motivo_saida.sort_values(by='valor', ascending=True).iloc[0]
            st.markdown(f"<strong>Maior Motivo para Saída:</strong> <span class='negative'>{maior_motivo_saida['recebedor']} (R$ {maior_motivo_saida['valor']:.2f})</span>", unsafe_allow_html=True)
        else:
            st.markdown("<strong>Maior Motivo para Saída:</strong> <span class='negative'>Nenhum</span>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)





# Função principal
def main():
    criar_tabela_recebedores(c)
    criar_tabela_transacoes(c)
    selected = sidebar_menu()
    
    if selected == "Dashboard Financeiro":
        st.title("Dashboard Financeiro 📊")
        exibir_dashboard()
        exibir_grafico(carregar_transacoes())
    elif selected == "Registros Financeiros":
        form_recebedores()
        form_transacoes()
        form_upload_xlsx()

if __name__ == "__main__":
    main()
