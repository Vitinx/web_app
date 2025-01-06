import streamlit as st
import os
import glob
import pandas as pd
from functions import *
#from backend import corrigir_valor, consolidar_arquivos_ap007b, processar_arquivos_ap007a, processar_dados_cobranca, gerar_arquivo_ap007a_criacao, gerar_arquivo_ap007a_atualizacao, gerar_arquivo_ap007a_inativacao, gerar_arquivo_ap007b_criacao, gerar_arquivo_ap007b_atualizacao, gerar_arquivo_ap007b_inativacao, processar_casos_de_inativacao, carregar_dados_cobranca_relatorio_final_marketup, gerar_relatorio_final_marketup

# Usado para salvar e encontrar os arquivos do dia
data_nome_arquivo = datetime.now().strftime('%Y%m%d')
data_atual = datetime.now().strftime("%d_%m_%Y")

# CONFIGURAÇÕES DE DATAS 
# Obtém o mês atual
mes_atual = datetime.now()

# Cria uma lista com os prefixos dos meses
prefixos_meses = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']

# Usa o número do mês para obter o prefixo correspondente
prefixo_mes = prefixos_meses[mes_atual.month - 1]

# Função para obter o caminho da pasta
def obter_caminho_pasta(file):
    if file is not None:
        return os.path.dirname(file.name)
    return None

# Estilo CSS para centralizar horizontalmente
st.markdown("""
    <style>
    .centered {
        display: flex;
        justify-content: center;
        flex-direction: column;
        align-items: center;
    }
    .stButton button {
        width: 700px;
        height: 50px;
        font-size: 16px;
        margin: 10px;
    }
    .title {
        font-size: 42px;
        font-weight: bold;
        text-align: center;
        white-space: nowrap; /* Evita quebra de linha */
    }
    .subtitle {
        font-size: 32px;
        font-weight: bold;
        text-align: center;
        white-space: nowrap; /* Evita quebra de linha */
    </style>
    """, unsafe_allow_html=True)

# Inicializar a variável de estado
if "page" not in st.session_state:
    st.session_state.page = "home"  # Página inicial

# Funções para cada página
def home():
    st.markdown('<div class="title">Bem-vindo(a) ao criador de relatórios</div>', unsafe_allow_html=True)
    st.markdown('<div class="centered">', unsafe_allow_html=True)
    if st.button("Relatório de Contratos CERC"):
        st.session_state.page = "menu_tipo_relatorio"
        #st.session_state.page = "menu_relatorio_cerc"
    if st.button("Relatório MarketUP"):
        st.session_state.page = "menu_relatorio_marketup"
    if st.button("Relatório Financeiro"):
        st.session_state.page = "menu_relatorio_financeiro"
    st.markdown('</div>', unsafe_allow_html=True)
    
def menu_tipo_relatorio():
    st.markdown('<div class="title">Qual o tipo do relatório?</div>', unsafe_allow_html=True)
    st.markdown('<div class="centered">', unsafe_allow_html=True)
    if st.button("CERC-AP004"):
        st.session_state.page = "ap004"
    if st.button("CERC-AP007A / CERC-AP007B"):
        st.session_state.page = "ap007a_ap007b"
    st.markdown('</div>', unsafe_allow_html=True)
    if st.button("Voltar"):
        st.session_state.page = "home"
    
def menu_relatorio_cerc():
    st.markdown('<div class="title">Relatório de Contratos CERC</div>', unsafe_allow_html=True)
    st.markdown('<div class="centered">', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Escolha o tipo da operação</div>', unsafe_allow_html=True)
    st.markdown('<div class="centered">', unsafe_allow_html=True)
    if st.button("Criação de contratos CERC"):
        st.session_state.page = "criacao_contratos"
    if st.button("Atualização de contratos CERC"):
        st.session_state.page = "atualizacao_contratos"
    if st.button("Inativação de contratos CERC"):
        st.session_state.page = "inativacao_contratos"
    st.markdown('</div>', unsafe_allow_html=True)
    if st.button("Voltar"):
        st.session_state.page = "home"
 
###################### CRIAÇÃO DE AGENDA OPT-IN ################################

def criacao_agenda():
    st.markdown('<div class="title">Criação de Agendas OPT-IN CERC</div>', unsafe_allow_html=True)
    st.markdown('<div class="centered">', unsafe_allow_html=True)
    
    def fluxo_processamento_criacao_agenda():
        # Define variáveis na sessão para armazenar os inputs dos usuários
        if "df_ap007b_ret" not in st.session_state:
            st.session_state.df_ap007b_ret = None
        if "df_cnpj" not in st.session_state:
            st.session_state.df_cnpj = None

        # Input para o caminho da pasta AP007B
        st.markdown('<div class="subtitle">Insira o caminho da pasta com os arquivos AP007B</div>', unsafe_allow_html=True)
        path_ap007b = st.text_input("Digite o caminho da pasta (AP007B):")

        # Input para o caminho do arquivo de cobrança
        st.markdown('<div class="subtitle">Insira o caminho do arquivo de cobrança</div>', unsafe_allow_html=True)
        path_cobranca = st.text_input("Digite o caminho do arquivo (Cobrança):")

        # Input para datas de início e fim da assinatura
        st.markdown('<div class="subtitle">Insira a data de início da assinatura (YYYY-MM-DD):</div>', unsafe_allow_html=True)
        data_inicio_assinatura = st.text_input("Data de início da assinatura:")

        st.markdown('<div class="subtitle">Insira a data de fim da assinatura (YYYY-MM-DD):</div>', unsafe_allow_html=True)
        data_fim_assinatura = st.text_input("Data de fim da assinatura:")

        # Input para o número do arquivo
        st.markdown('<div class="subtitle">Insira o número deste arquivo</div>', unsafe_allow_html=True)
        numero_arquivo = st.text_input("Número do arquivo:")

        # Botão para processar tudo
        if st.button("Processar Tudo"):
            # Verifica se todos os campos foram preenchidos
            if path_ap007b and path_cobranca and data_inicio_assinatura and data_fim_assinatura and numero_arquivo:
                # Processa os arquivos com base nos inputs fornecidos
                df_ap007b_ret = processar_arquivos_ap007b(path_ap007b)
                df_cnpj = processar_cnpj_cobranca(path_cobranca, df_ap007b_ret)
                
                # Gerando arquivo AP007A
                gerar_arquivo_ap004_criacao(df_cnpj, prefixo_mes=prefixo_mes, data_nome_arquivo=datetime.now().strftime('%Y%m%d'), data_inicio_assinatura=data_inicio_assinatura, data_fim_assinatura=data_fim_assinatura, numero_arquivo=numero_arquivo)
                                
                # Mensagens ao usuário
                st.markdown('<div class="subtitle">Arquivo AP004 gerado com sucesso!</div>', unsafe_allow_html=True)

            else:
                st.warning("Por favor, preencha todos os campos antes de processar.")

    fluxo_processamento_criacao_agenda()
    
    if st.button("Voltar"):
        st.session_state.page = "menu_tipo_relatorio"        
        
def atualizacao_agenda():
    st.markdown('<div class="title">Atualização de Agenda OPT-IN CERC</div>', unsafe_allow_html=True)
    st.markdown('<div class="centered">', unsafe_allow_html=True)
    
    def fluxo_processamento_atualizacao_agenda():
            # Armazenar o estado das etapas
            if "consultado" not in st.session_state:
                st.session_state.consultado = False
            if "continuar" not in st.session_state:
                st.session_state.continuar = False
            # Define variáveis na sessão para armazenar os inputs dos usuários
            if "df_ap007b_ret" not in st.session_state:
                st.session_state.df_ap007b_ret = None
            if "df_cnpj" not in st.session_state:
                st.session_state.df_cnpj = None

            # Caminho dos arquivos de retorno, nesta etapa processamos todos os arquivos
            path_ap007b = 'C:/Users/Vítor/Documents/VEON/arquivos_retorno/arquivos_ap007b'

            # Input para o caminho do arquivo de cobrança
            st.markdown('<div class="subtitle">Insira o caminho do arquivo de cobrança</div>', unsafe_allow_html=True)
            path_cobranca = st.text_input("Digite o caminho do arquivo (Cobrança):")
            
            # Input para o caminho do arquivo AP007A
            st.markdown('<div class="subtitle">Insira o caminho do arquivo AP004</div>', unsafe_allow_html=True)
            path_ap007a = st.text_input("Digite o caminho do arquivo (AP004):")
            
            # Botão para consultar os arquivos
            if st.button("Consultar"):
                if path_ap007b and path_cobranca and path_ap007a:
                    df_ap007b_ret = processar_arquivos_ap007b(path_ap007b)
                    df_cnpj = processar_cnpj_cobranca(path_cobranca, df_ap007b_ret)
                    df_ap007a_ret, df_onerados, df_reenviar, df_erros = processar_um_arquivo_ap007a(path_ap007a, df_cnpj)
                    
                    onerados = df_onerados.shape[0]
                    atualizar = df_reenviar.shape[0]
                    erros = df_erros.shape[0]
                    
                    st.write(f'Foram encontrados {onerados} URs oneradas, {atualizar} para atualizar e {erros} deram erro')
                    
                    # Define o estado como consultado para mostrar o botão "Continuar"
                    st.session_state.consultado = True
                    
            # Botão de "Continuar" para avançar para as próximas etapas
            if st.session_state.consultado:
                if st.button("Continuar"):
                    st.session_state.continuar = True

            if st.session_state.continuar:
                # Input para datas de início e fim da assinatura
                st.markdown('<div class="subtitle">Insira a data de início da assinatura (YYYY-MM-DD):</div>', unsafe_allow_html=True)
                data_inicio_assinatura = st.text_input("Data de início da assinatura:")

                st.markdown('<div class="subtitle">Insira a data de fim da assinatura (YYYY-MM-DD):</div>', unsafe_allow_html=True)
                data_fim_assinatura = st.text_input("Data de fim da assinatura:")

                # Input para o número do arquivo
                st.markdown('<div class="subtitle">Insira o número deste arquivo</div>', unsafe_allow_html=True)
                numero_arquivo = st.text_input("Número do arquivo:")

                # Botão para processar tudo
                if st.button("Processar Tudo"):
                    # Verifica se todos os campos foram preenchidos
                    if path_ap007b and path_cobranca and data_inicio_assinatura and data_fim_assinatura and numero_arquivo:
                        # Processa os arquivos com base nos inputs fornecidos
                        df_ap007b_ret = processar_arquivos_ap007b(path_ap007b)
                        df_cnpj = processar_cnpj_cobranca(path_cobranca, df_ap007b_ret)
                        
                        # Exibe mensagens de sucesso e/ou dados processados
                        st.write("Processamento completo!")
                        st.write("Arquivos AP007B e cobrança processados com sucesso!")
                        
                        # Gerando arquivo AP007A
                        gerar_arquivo_ap007a_atualizacao(df_cnpj, prefixo_mes=prefixo_mes, data_nome_arquivo=datetime.now().strftime('%Y%m%d'), data_inicio_assinatura=data_inicio_assinatura, data_fim_assinatura=data_fim_assinatura, numero_arquivo=numero_arquivo)
                                        
                        # Mensagens ao usuário
                        st.markdown('<div class="subtitle">Arquivo AP007A gerado com sucesso!</div>', unsafe_allow_html=True)
                            
                        # Gerando arquivo AP007B
                        gerar_arquivo_ap007b_atualizacao(df_cnpj, prefixo_mes=prefixo_mes, data_nome_arquivo=datetime.now().strftime('%Y%m%d'), data_inicio_assinatura=data_inicio_assinatura, data_fim_assinatura=data_fim_assinatura, numero_arquivo=numero_arquivo)
                                        
                        # Mensagens ao usuário
                        st.markdown('<div class="subtitle">Arquivo AP007B gerado com sucesso!</div>', unsafe_allow_html=True)

                    else:
                        st.warning("Por favor, preencha todos os campos antes de processar.")

    fluxo_processamento_atualizacao_agenda()
    
    if st.button("Voltar"):
        st.session_state.page = "menu_relatorio_cerc"        
        
###################### CRIAÇÃO DOS CONTRATOS ###################################        
def criacao_contratos():
    st.markdown('<div class="title">Criação de contratos CERC</div>', unsafe_allow_html=True)
    st.markdown('<div class="centered">', unsafe_allow_html=True)
    
    def fluxo_processamento_criacao():
        # Define variáveis na sessão para armazenar os inputs dos usuários
        if "df_ap007b_ret" not in st.session_state:
            st.session_state.df_ap007b_ret = None
        if "df_cnpj" not in st.session_state:
            st.session_state.df_cnpj = None

        # Input para o caminho da pasta AP007B
        st.markdown('<div class="subtitle">Insira o caminho da pasta com os arquivos AP007B</div>', unsafe_allow_html=True)
        path_ap007b = st.text_input("Digite o caminho da pasta (AP007B):")

        # Input para o caminho do arquivo de cobrança
        st.markdown('<div class="subtitle">Insira o caminho do arquivo de cobrança</div>', unsafe_allow_html=True)
        path_cobranca = st.text_input("Digite o caminho do arquivo (Cobrança):")

        # Input para datas de início e fim da assinatura
        st.markdown('<div class="subtitle">Insira a data de início da assinatura (YYYY-MM-DD):</div>', unsafe_allow_html=True)
        data_inicio_assinatura = st.text_input("Data de início da assinatura:")

        st.markdown('<div class="subtitle">Insira a data de fim da assinatura (YYYY-MM-DD):</div>', unsafe_allow_html=True)
        data_fim_assinatura = st.text_input("Data de fim da assinatura:")

        # Input para o número do arquivo
        st.markdown('<div class="subtitle">Insira o número deste arquivo</div>', unsafe_allow_html=True)
        numero_arquivo = st.text_input("Número do arquivo:")

        # Botão para processar tudo
        if st.button("Processar Tudo"):
            # Verifica se todos os campos foram preenchidos
            if path_ap007b and path_cobranca and data_inicio_assinatura and data_fim_assinatura and numero_arquivo:
                # Processa os arquivos com base nos inputs fornecidos
                df_ap007b_ret = processar_arquivos_ap007b(path_ap007b)
                df_cnpj = processar_cnpj_cobranca(path_cobranca, df_ap007b_ret)
                
                # Exibe mensagens de sucesso e/ou dados processados
                st.write("Processamento completo!")
                st.write("Arquivos AP007B e cobrança processados com sucesso!")
                
                # Gerando arquivo AP007A
                gerar_arquivo_ap007a_criacao(df_cnpj, prefixo_mes=prefixo_mes, data_nome_arquivo=datetime.now().strftime('%Y%m%d'), data_inicio_assinatura=data_inicio_assinatura, data_fim_assinatura=data_fim_assinatura, numero_arquivo=numero_arquivo)
                                
                # Mensagens ao usuário
                st.markdown('<div class="subtitle">Arquivo AP007A gerado com sucesso!</div>', unsafe_allow_html=True)
                    
                # Gerando arquivo AP007B
                gerar_arquivo_ap007b_criacao(df_cnpj, prefixo_mes=prefixo_mes, data_nome_arquivo=datetime.now().strftime('%Y%m%d'), data_inicio_assinatura=data_inicio_assinatura, data_fim_assinatura=data_fim_assinatura, numero_arquivo=numero_arquivo)
                                
                # Mensagens ao usuário
                st.markdown('<div class="subtitle">Arquivo AP007B gerado com sucesso!</div>', unsafe_allow_html=True)

            else:
                st.warning("Por favor, preencha todos os campos antes de processar.")

    fluxo_processamento_criacao()
    
    if st.button("Voltar"):
        st.session_state.page = "menu_relatorio_cerc"
        
def atualizacao_contratos():
    st.markdown('<div class="title">Atualização de contratos CERC</div>', unsafe_allow_html=True)
    st.markdown('<div class="centered">', unsafe_allow_html=True)
    
    def fluxo_processamento_atualizacao():
            # Armazenar o estado das etapas
            if "consultado" not in st.session_state:
                st.session_state.consultado = False
            if "continuar" not in st.session_state:
                st.session_state.continuar = False
            # Define variáveis na sessão para armazenar os inputs dos usuários
            if "df_ap007b_ret" not in st.session_state:
                st.session_state.df_ap007b_ret = None
            if "df_cnpj" not in st.session_state:
                st.session_state.df_cnpj = None

            # Caminho dos arquivos de retorno, nesta etapa processamos todos os arquivos
            path_ap007b = 'C:/Users/Vítor/Documents/VEON/arquivos_retorno/arquivos_ap007b'

            # Input para o caminho do arquivo de cobrança
            st.markdown('<div class="subtitle">Insira o caminho do arquivo de cobrança</div>', unsafe_allow_html=True)
            path_cobranca = st.text_input("Digite o caminho do arquivo (Cobrança):")
            
            # Input para o caminho do arquivo AP007A
            st.markdown('<div class="subtitle">Insira o caminho do arquivo AP007A</div>', unsafe_allow_html=True)
            path_ap007a = st.text_input("Digite o caminho do arquivo (AP007A):")
            
            # Botão para consultar os arquivos
            if st.button("Consultar"):
                if path_ap007b and path_cobranca and path_ap007a:
                    df_ap007b_ret = processar_arquivos_ap007b(path_ap007b)
                    df_cnpj = processar_cnpj_cobranca(path_cobranca, df_ap007b_ret)
                    df_ap007a_ret, df_onerados, df_reenviar, df_erros = processar_um_arquivo_ap007a(path_ap007a, df_cnpj)
                    
                    onerados = df_onerados.shape[0]
                    atualizar = df_reenviar.shape[0]
                    erros = df_erros.shape[0]
                    
                    st.write(f'Foram encontrados {onerados} URs oneradas, {atualizar} para atualizar e {erros} deram erro')
                    
                    # Define o estado como consultado para mostrar o botão "Continuar"
                    st.session_state.consultado = True
                    
            # Botão de "Continuar" para avançar para as próximas etapas
            if st.session_state.consultado:
                if st.button("Continuar"):
                    st.session_state.continuar = True

            if st.session_state.continuar:
                # Input para datas de início e fim da assinatura
                st.markdown('<div class="subtitle">Insira a data de início da assinatura (YYYY-MM-DD):</div>', unsafe_allow_html=True)
                data_inicio_assinatura = st.text_input("Data de início da assinatura:")

                st.markdown('<div class="subtitle">Insira a data de fim da assinatura (YYYY-MM-DD):</div>', unsafe_allow_html=True)
                data_fim_assinatura = st.text_input("Data de fim da assinatura:")

                # Input para o número do arquivo
                st.markdown('<div class="subtitle">Insira o número deste arquivo</div>', unsafe_allow_html=True)
                numero_arquivo = st.text_input("Número do arquivo:")

                # Botão para processar tudo
                if st.button("Processar Tudo"):
                    # Verifica se todos os campos foram preenchidos
                    if path_ap007b and path_cobranca and data_inicio_assinatura and data_fim_assinatura and numero_arquivo:
                        # Processa os arquivos com base nos inputs fornecidos
                        df_ap007b_ret = processar_arquivos_ap007b(path_ap007b)
                        df_cnpj = processar_cnpj_cobranca(path_cobranca, df_ap007b_ret)
                        
                        # Exibe mensagens de sucesso e/ou dados processados
                        st.write("Processamento completo!")
                        st.write("Arquivos AP007B e cobrança processados com sucesso!")
                        
                        # Gerando arquivo AP007A
                        gerar_arquivo_ap007a_atualizacao(df_cnpj, prefixo_mes=prefixo_mes, data_nome_arquivo=datetime.now().strftime('%Y%m%d'), data_inicio_assinatura=data_inicio_assinatura, data_fim_assinatura=data_fim_assinatura, numero_arquivo=numero_arquivo)
                                        
                        # Mensagens ao usuário
                        st.markdown('<div class="subtitle">Arquivo AP007A gerado com sucesso!</div>', unsafe_allow_html=True)
                            
                        # Gerando arquivo AP007B
                        gerar_arquivo_ap007b_atualizacao(df_cnpj, prefixo_mes=prefixo_mes, data_nome_arquivo=datetime.now().strftime('%Y%m%d'), data_inicio_assinatura=data_inicio_assinatura, data_fim_assinatura=data_fim_assinatura, numero_arquivo=numero_arquivo)
                                        
                        # Mensagens ao usuário
                        st.markdown('<div class="subtitle">Arquivo AP007B gerado com sucesso!</div>', unsafe_allow_html=True)

                    else:
                        st.warning("Por favor, preencha todos os campos antes de processar.")

    fluxo_processamento_atualizacao()
    
    if st.button("Voltar"):
        st.session_state.page = "menu_relatorio_cerc"
        
def inativacao_contratos():
    st.markdown('<div class="title">Inativação de contratos CERC</div>', unsafe_allow_html=True)
    st.markdown('<div class="centered">', unsafe_allow_html=True)
    
    def fluxo_processamento():
            
        # Define variáveis na sessão para armazenar os inputs dos usuários
        if "df_ap007b_ret" not in st.session_state:
            st.session_state.df_ap007b_ret = None
        if "df_cnpj" not in st.session_state:
            st.session_state.df_cnpj = None
        
        # Caminho dos arquivos de retorno, nesta etapa processamos todos os arquivos
        path_ap007b = 'C:/Users/Vítor/Documents/VEON/arquivos_retorno/arquivos_ap007b'
        
        # Input para o caminho do arquivo de cobrança
        st.markdown('<div class="subtitle">Insira o caminho do arquivo de cobrança</div>', unsafe_allow_html=True)
        path_cobranca = st.text_input("Digite o caminho do arquivo (Cobrança):")
        
        # Input para o caminho do arquivo AP007A
        st.markdown('<div class="subtitle">Insira o caminho do arquivo AP007A</div>', unsafe_allow_html=True)
        path_ap007a = st.text_input("Digite o caminho do arquivo (AP007A):")
        
        # Botão para consultar os arquivos
        if st.button("Consultar"):
            if path_ap007b and path_cobranca and path_ap007a:
                df_ap007b_ret = processar_arquivos_ap007b(path_ap007b)
                df_cnpj = processar_cnpj_cobranca(path_cobranca, df_ap007b_ret)
                df_ap007a_ret, df_onerados, df_reenviar, df_erros = processar_um_arquivo_ap007a(path_ap007a, df_cnpj)
                
                onerados = df_onerados.shape[0]
                atualizar = df_reenviar.shape[0]
                erros = df_erros.shape[0]
                
                st.write(f'Foram encontrados {onerados} URs oneradas, {atualizar} para atualizar e {erros} deram erro')
                
                # Define o estado como consultado para mostrar o botão "Continuar"
                st.session_state.consultado = True
            
    fluxo_processamento()
    
    if st.button("Voltar"):
        st.session_state.page = "menu_relatorio_cerc"

def menu_relatorio_marketup():
    st.markdown('<div class="title">Relatório MarketUP</div>', unsafe_allow_html=True)
    st.write("Conteúdo do Relatório MarketUP.")
    if st.button("Voltar"):
        st.session_state.page = "home"

def menu_relatorio_financeiro():
    st.markdown('<div class="title">Relatório Financeiro</div>', unsafe_allow_html=True)
    st.write("Conteúdo do Relatório Financeiro.")
    if st.button("Voltar"):
        st.session_state.page = "home"

# Navegação entre as páginas
if st.session_state.page == "home":
    home()
elif st.session_state.page == "menu_tipo_relatorio":
    menu_tipo_relatorio()
elif st.session_state.page == "ap004":
    criacao_agenda()
elif st.session_state.page == "ap007a_ap007b":
    menu_relatorio_cerc()
# elif st.session_state.page == "menu_relatorio_cerc":
#     menu_relatorio_cerc()
elif st.session_state.page == "criacao_contratos":
    criacao_contratos()
elif st.session_state.page == "atualizacao_contratos":
    atualizacao_contratos()
elif st.session_state.page == "inativacao_contratos":
    inativacao_contratos()
elif st.session_state.page == "menu_relatorio_marketup":
    menu_relatorio_marketup()
elif st.session_state.page == "menu_relatorio_financeiro":
    menu_relatorio_financeiro()
