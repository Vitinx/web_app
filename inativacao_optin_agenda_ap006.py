import pandas as pd
import numpy as np
import csv
import glob
import warnings
warnings.filterwarnings('ignore')
import datetime
from datetime import datetime
import calendar
import time
import os
import platform

def corrigir_valor(valor):
    # Converter para string para tratar os valores
    valor_str = str(valor)
    
    # Verificar se há mais de um ponto no valor
    if valor_str.count('.') > 1:
        # Remover pontos extras e ajustar para que os dois últimos dígitos sejam as casas decimais
        valor_limpo = valor_str.replace('.', '')
        valor_final = float(valor_limpo[:-2] + '.' + valor_limpo[-2:])
    else:
        # Se já estiver correto, converte diretamente para float
        valor_final = float(valor_str)
    
    return valor_final    

def gerar_arquivo_ap006_inativacao(df_cnpj, prefixo_mes, data_nome_arquivo, data_de_inicio, data_de_fim, numero_arquivo):
    
    # Criando os campos do relatório
    tipo_de_operacao_i = 'I'  # Criar contrato
    referencia_externa = prefixo_mes + df_cnpj['ID'].astype(str)  # Código
    solicitante = '52541797000138' # CNPJ Veon
    financiador = '52541797000138' # CNPJ Veon
    instituicao_credenciadora = df_cnpj['instituicao_credenciadora'] # Traz o CNPJ do histórico ou 99T para todas
    usuario_final_recebedor = df_cnpj['CNPJ'] # CNPJ do cliente
    arranjo_de_pagamento = 'MCC|VCC|ECC|HCC|ACC|MCD|VCD|ECD' # Arranjos mais comuns, criar código para trazer o histórico dos arranjos que pagam em cada CNPJ
    data_optin = datetime.now().strftime('%Y-%m-%d') # Traz a data atual do processamento
    data_de_inicio_agenda = data_de_inicio  # Data de início da assinatura
    data_de_fim_agenda = data_de_fim  # Data de fim da assinatura
    titular_ur = '' # Verificar
    carteira = '' # Verificar
    protocolo = '' # Verificar
    instituicao_recebedora = '' # Verificar
    
    # Montando o dicionário de dados
    dados = {
        'tipo_de_operacao': tipo_de_operacao_i,
        'referencia_externa': referencia_externa,
        'solicitante':solicitante,
        'financiador':financiador,
        'instituicao_credenciadora':instituicao_credenciadora,
        'usuario_final_recebedor':usuario_final_recebedor,
        'arranjo_de_pagamento':arranjo_de_pagamento,
        'data_optin':data_optin,
        'data_de_inicio_agenda':data_de_inicio_agenda,
        'data_de_fim_agenda':data_de_fim_agenda,
        'titular_ur':titular_ur,
        'carteira':carteira,
        'protocolo':protocolo,
        'instituicao_recebedora':instituicao_recebedora
    }

    # Criando o dataframe
    df_ap004 = pd.DataFrame(dados)
    
    # Gerando o nome do arquivo
    nome_arquivo = f'CERC-AP004_52541797_{data_nome_arquivo}_000000{numero_arquivo}.csv'

    # Salvando o arquivo CSV comprimido
    df_ap004.to_csv(f'C:/Users/Vítor/Documents/VEON/Projeto Web App/data/arquivos_entrada/AP_004/{nome_arquivo}.gz', header=None, sep=';', index=False)