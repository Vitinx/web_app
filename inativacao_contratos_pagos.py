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
import io
import gzip

def gerar_arquivos_inativacao(path_ap007a, path_ap007b, path_inativacao, data_nome_arquivo, numero_arquivo):
    
    # Lendo arquivo de retorno AP007A
    colunas_ap007a = [
        'tipo_de_operacao',
        'referencia_externa',
        'identificador_do_contrato',
        'contratante',
        'repactuacao',
        'lista_de_identificadores',
        'participante',
        'detentor',
        'tipo_de_efeito',
        'saldo_devedor',
        'limite_da_operacao',
        'valor_a_ser_mantido',
        'data_da_assinatura',
        'data_de_vencimento',
        'tipo_de_servico',
        'modalidade_da_operacao',
        'lista_de_parcela',
        'carteira',
        'tipo_de_avaliacao',
        'taxa_de_juros',
        'indexador',
        'aceite_incondicional_da_operacao'
    ]

    df = []
    
    if path_ap007a:
        df_ap007a = pd.read_csv(path_ap007a, compression='gzip', header=None, delimiter=';', names=colunas_ap007a)
            
    df_ap007a = df_ap007a.astype(str)
    
    # Lendo arquivo de retorno AP007B
    colunas_ap007b = [
        'tipo_de_operacao',
        'referencia_externa',
        'identificador_do_contrato',
        'instituicao_credenciadora',
        'usuario_final_recebedor',
        'arranjo_de_pagamento',
        'data_liquidacao_inicio',
        'data_liquidacao_fim',
        'titular',
        'regras_de_divisao',
        'valor_a_onerar',
        'tipo_de_distribuicao',
        'numero_documento_titular',
        'tipo_de_conta',
        'compe',
        'ispb',
        'agencia',
        'numero_da_conta',
        'nome_titular'
    ]

    df = []
    
    if path_ap007b:
        df_ap007b = pd.read_csv(path_ap007b, compression='gzip', header=None, delimiter=';', names=colunas_ap007b)
            
    df_ap007b = df_ap007b.astype(str)
    
    # Juntando os dois arquivos
    df_merged = pd.merge(
                df_ap007a,
                df_ap007b, 
                left_on='contratante', 
                right_on='usuario_final_recebedor',
                how='left', 
                suffixes=('', '_drop'))

    df_merged = df_merged.loc[:, ~df_merged.columns.str.endswith('_drop')]
    
    
    # Lendo arquivo com CNPJs para inativação
    df = []
    
    if path_inativacao:
        df_cnpj = pd.read_excel(path_inativacao)

    
    df_cnpj = df_cnpj.astype(str)

    # Juntando os CNPJs com as informações de pagamento
    result = pd.merge(
            df_cnpj,
            df_merged,
            left_on='CNPJ',
            right_on='usuario_final_recebedor',
            how='left'
        )
    
    # Preenchendo arquivo AP007A para inativação
    dados = {
        'tipo_de_operacao':'I',
        'referencia_externa':result['referencia_externa'],
        'identificador_do_contrato':result['identificador_do_contrato'],
        'contratante':result['contratante'],
        'repactuacao':result['repactuacao'],
        'lista_de_identificadores':result['lista_de_identificadores'],
        'participante':result['participante'],
        'detentor':result['detentor'],
        'tipo_de_efeito':result['tipo_de_efeito'],
        'saldo_devedor':result['saldo_devedor'],
        'limite_da_operacao':result['limite_da_operacao'],
        'valor_a_ser_mantido':result['valor_a_ser_mantido'],
        'data_da_assinatura':result['data_da_assinatura'],
        'data_de_vencimento':result['data_de_vencimento'],
        'tipo_de_servico':result['tipo_de_servico'],
        'modalidade_da_operacao':result['modalidade_da_operacao'],
        'lista_de_parcela':result['lista_de_parcela'],
        'carteira':result['carteira'],
        'tipo_de_avaliacao':result['tipo_de_avaliacao'],
        'taxa_de_juros':result['taxa_de_juros'],
        'indexador':result['indexador'],
        'aceite_incondicional_da_operacao':result['aceite_incondicional_da_operacao']
    }

    df_ap007a_final = pd.DataFrame(dados)
   
    # Preenchendo arquivo AP007B para inativação
    dados = {
        'tipo_de_operacao':'I',
        'referencia_externa':result['referencia_externa'],
        'identificador_do_contrato':result['identificador_do_contrato'],
        'instituicao_credenciadora':result['instituicao_credenciadora'],
        'usuario_final_recebedor':result['usuario_final_recebedor'],
        'arranjo_de_pagamento':result['arranjo_de_pagamento'],
        'data_liquidacao_inicio':result['data_liquidacao_inicio'],
        'data_liquidacao_fim':result['data_liquidacao_fim'],
        'titular':result['titular'],
        'regras_de_divisao':result['regras_de_divisao'],
        'valor_a_onerar':result['valor_a_onerar'],
        'tipo_de_distribuicao':result['tipo_de_operacao'],
        'numero_documento_titular':result['numero_documento_titular'],
        'tipo_de_conta':result['tipo_de_conta'],
        'compe':result['compe'],
        'ispb':result['ispb'],
        'agencia':result['agencia'],
        'numero_da_conta':result['numero_da_conta'],
        'nome_titular':result['nome_titular']
    }

    df_ap007b_final = pd.DataFrame(dados)
    
    # Salvando arquivo final AP007A
    nome_arquivo_ap007a = f'CERC-AP007A_52541797_{data_nome_arquivo}_000000{numero_arquivo}.csv'

    buffer_ap007a = io.BytesIO()
    df_ap007a_final.to_csv(buffer_ap007a, header=None, sep=';', index=False, compression='gzip')
    buffer_ap007a.seek(0)
       
    # Salvando arquivo final AP007B    
    nome_arquivo_a077b = f'CERC-AP007B_52541797_{data_nome_arquivo}_000000{numero_arquivo}.csv'

    buffer_ap007b = io.BytesIO()
    df_ap007b_final.to_csv(buffer_ap007b, header=None, sep=';', index=False, compression='gzip')
    buffer_ap007b.seek(0)    
        
    return buffer_ap007a, nome_arquivo_ap007a, buffer_ap007b, nome_arquivo_a077b