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

def processar_arquivos_ap007b(path_ap007b):
    # Definindo as colunas
    colunas = ['referencia_externa', 'indetificador_do_contrato', 'entidade_registradora', 'instituicao_credenciadora', 
               'usuario_final_recebedor', 'arranjo_de_pagamento', 'data_de_liquidacao', 'titular_da_unidade_recebivel', 
               'constituicao_da_unidade_recebivel', 'valor_constituido_total', 'valor_bloqueado', 'indicador_de_oneracao', 
               'regra_de_divisao', 'valor_onerado_na_ur', 'protocolo', 'data_hora_do_evento', 'status_da_operacao', 
               'erros', 'valor_constituido_da_ur']
    
    
    # Lendo todos os arquivos CSV do diretório
    arquivos_csv = glob.glob(os.path.join(path_ap007b, "*.csv"))
    
    quantidade_arquivos = len(arquivos_csv)
    
    # Concatenando os arquivos em um único dataframe
    df_ap007b = pd.concat([pd.read_csv(arquivo, header=None, delimiter=';', names=colunas) for arquivo in arquivos_csv], ignore_index=True)
    
    # Realizando tratamentos nos dados
    for col in ['entidade_registradora', 'instituicao_credenciadora', 'usuario_final_recebedor', 'titular_da_unidade_recebivel', 
                'constituicao_da_unidade_recebivel', 'indicador_de_oneracao', 'regra_de_divisao', 'erros']:
        df_ap007b[col] = df_ap007b[col].astype(str)
    
    # Ajustar colunas com CNPJ para ter 14 dígitos
    df_ap007b['entidade_registradora'] = df_ap007b['entidade_registradora'].apply(lambda x: x.zfill(14) if len(x) < 14 else x)
    df_ap007b['instituicao_credenciadora'] = df_ap007b['instituicao_credenciadora'].apply(lambda x: x.zfill(14) if len(x) < 14 else x)
    df_ap007b['usuario_final_recebedor'] = df_ap007b['usuario_final_recebedor'].apply(lambda x: x.zfill(14) if len(x) < 14 else x)
    
    # Renomear a coluna 'usuario_final_recebedor' para 'CNPJ'
    df_ap007b_ret = df_ap007b.rename(columns={'usuario_final_recebedor': 'CNPJ'})
    
    df_ap007b_ret['ID'] = df_ap007b_ret['referencia_externa'].str.extract(r'(\d+)')

    df_ap007b_ret = df_ap007b_ret.drop_duplicates(subset='ID')
    
    return df_ap007b_ret