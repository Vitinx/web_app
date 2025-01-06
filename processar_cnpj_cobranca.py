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

def processar_cnpj_cobranca(path_cobranca, df_ap007b_ret):
    
    # Ler arquivo Excel
    df_mktup = pd.read_excel(f'{path_cobranca}')
    
    # Ajustar colunas ID e CNPJ
    df_mktup['ID'] = df_mktup['ID'].astype(str).str.replace(r'\.0$', '', regex=True)
    df_mktup['CNPJ'] = df_mktup['CNPJ'].astype(str).str.replace(r'\.0$', '', regex=True)
    df_mktup['CNPJ'] = df_mktup['CNPJ'].apply(lambda x: x.zfill(14) if len(x) < 14 else x)
    
    # Agrupar por ID e CNPJ, somar valores e ordenar
    df_cnpj = df_mktup.groupby(['ID', 'CNPJ'])['VALOR'].sum().sort_values(ascending=False).reset_index()
    
    # Fazer merge com o dataframe de retorno AP007B
    df_cnpj = pd.merge(df_cnpj, df_ap007b_ret[['CNPJ', 'instituicao_credenciadora']], on='CNPJ', how='left')
    
    # Preencher valores faltantes e remover duplicatas
    df_cnpj['instituicao_credenciadora'] = df_cnpj['instituicao_credenciadora'].fillna('99T')
    df_cnpj = df_cnpj.drop_duplicates(subset='CNPJ')
    
    return df_cnpj