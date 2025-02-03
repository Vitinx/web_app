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

def processar_um_arquivo_ap007a(path_ap007a, df_cnpj):
    # Lendo todos os arquivos CSV do diretório
    #arquivo = path_ap007a

    # Definindo as colunas do DataFrame
    colunas = ['referencia_externa', 'protocolo', 'qtd_urs_alcancadas', 'valor_urs_alcancadas', 
               'resultado_distribuicao_dos_onus', 'indicadores_de_consistencia', 
               'data_hora_recebimento_arquivo', 'status_operacao', 'erros', 'identificador_do_contrato', 'valor_constituido_da_ur']

    # Consolidando os arquivos CSV em um único DataFrame
    #df_ap007a_ret = pd.read_csv(arquivo, header=None, delimiter=';', names=colunas)
    
    # Lista para armazenar os DataFrames
    
    if path_ap007a:
        # Ler o arquivo Excel em um DataFrame
        df_ap007a_ret = pd.read_csv(path_ap007a, header=None, delimiter=';', names=colunas)

    # Filtrando as URs oneradas
    df_onerados = df_ap007a_ret.query('valor_urs_alcancadas > 0.0')
    df_onerados['ID'] = df_onerados['referencia_externa'].str.extract(r'(\d+)')
    df_onerados = pd.merge(df_onerados, df_cnpj, on='ID', how='left')

    #Calculando a porcentagem do valor onerado
    df_onerados['porcentagem_valor_onerado'] = df_onerados['valor_urs_alcancadas'] / df_onerados['VALOR']

    # Função para distribuir o valor constituído entre os planos
    def distribuir_valores(row, valor_restante):
        if valor_restante <= row['VALOR']:  # Se o valor restante for menor ou igual ao valor da mensalidade
            valor_distribuido = valor_restante
            valor_restante = 0  # Todo o valor foi distribuído
        else:
            valor_distribuido = row['VALOR']
            valor_restante -= row['VALOR']  # Subtrai o valor da mensalidade do restante
        
        return valor_distribuido, valor_restante

    # Variável para manter o valor restante de cada ID
    df_onerados['valor_distribuido'] = 0.0  # Inicializa a coluna
    restantes = {}  # Dicionário para armazenar os valores restantes por ID

    # Iterar sobre o dataframe para distribuir os valores por linha
    for idx, row in df_onerados.iterrows():
        id_atual = row['ID']
        
        # Se for a primeira ocorrência do ID, inicia o valor restante
        if id_atual not in restantes:
            restantes[id_atual] = row['valor_constituido_da_ur']
        
        # Distribui o valor
        valor_distribuido, restantes[id_atual] = distribuir_valores(row, restantes[id_atual])
        
        # Atualiza a coluna com o valor distribuído
        df_onerados.at[idx, 'valor_distribuido'] = valor_distribuido
        
    # Tratamentos de valores zerados
    df_onerados = df_onerados.fillna(0)

    # Calcular a porcentagem paga considerando valores NaN
    df_onerados['porcentagem_paga'] = df_onerados['valor_distribuido'] / df_onerados['VALOR']
    df_onerados['porcentagem_paga'].fillna(0, inplace=True)
    
    # Filtrando URs que precisam ser reenviadas por terem uma porcentagem de valor onerado <= 0.5
    df_reenviar2 = df_onerados.query('porcentagem_paga < 0.5')

    # Filtrando URs que não foram oneradas e precisam ser reenviadas
    df_reenviar = df_ap007a_ret.query('valor_urs_alcancadas == 0.0 and status_operacao == 0')
    df_reenviar['ID'] = df_reenviar['referencia_externa'].str.extract(r'(\d+)')
    df_reenviar = pd.merge(df_reenviar, df_cnpj, on='ID', how='left')

    # Concatenando os dois DataFrames de URs a serem reenviadas
    df_reenviar = pd.concat([df_reenviar, df_reenviar2], ignore_index=True)

    # Filtrando as URs que apresentaram erros
    df_erros = df_ap007a_ret.query('status_operacao == 1')

    # Retornando os resultados
    return df_ap007a_ret, df_onerados, df_reenviar, df_erros