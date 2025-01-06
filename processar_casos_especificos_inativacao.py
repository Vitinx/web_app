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

# Inativação para casos específicos
def processar_casos_de_inativacao(path_casos_inativacao, df_cnpj):

    # Definindo as colunas
    colunas = ['referencia_externa', 'protocolo', 'qtd_urs_alcancadas', 'valor_urs_alcancadas', 
               'resultado_distribuicao_dos_onus', 'indicadores_de_consistencia', 'data_hora_recebimento_arquivo', 
               'status_operacao', 'erros', 'identificador_do_contrato']

    # Lendo o CSV
    df_reenviar = pd.read_csv(path_casos_inativacao, header=None, names=colunas)

    # Extraindo a coluna 'ID' da 'referencia_externa'
    df_reenviar['ID'] = df_reenviar['referencia_externa'].str.extract(r'(\d+)')

    # Realizando o merge com o dataframe de CNPJs
    df_reenviar = pd.merge(df_reenviar, df_cnpj, on='ID', how='left')

    return df_reenviar