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

def gerar_arquivo_ap007b_inativacao(df_reenviar, prefixo_mes, data_nome_arquivo, data_inicio_assinatura, data_fim_assinatura, numero_arquivo):
    tipo_de_operacao_c = 'C' # Criar contrato
    tipo_de_operacao_a = 'A' # Atualizar contrato
    tipo_de_operacao_i = 'I' # Inativar contrato
    tipo_de_operacao_b = 'B' # Baixa
    tipo_de_operacao_s = 'S' # Simular contrato

    referencia_externa = prefixo_mes+df_reenviar['ID'].astype(str) # Código
    identificador_do_contrato = 'id'+df_reenviar['ID'].astype(str) # Código
    instituicao_credenciadora = df_reenviar['instituicao_credenciadora'] # Todas as credenciadoras, criar código para trazer o histórico das que pagam em cada CNPJ
    usuario_final_recebedor = df_reenviar['CNPJ'] # CNPJ do cliente
    arranjo_de_pagamento = 'MCC|VCC|ECC|HCC|ACC|MCD|VCD|ECD' # Arranjos mais comuns, criar código para trazer o histórico dos arranjos que pagam em cada CNPJ
    data_liquidacao_inicio = data_inicio_assinatura # Data de início da cobrança
    data_liquidacao_fim = data_fim_assinatura # Data de fim da cobrança
    titular = df_reenviar['CNPJ'] # CNPJ do cliente
    regras_de_divisao = '1' # Comprometimento de valor definido
    valor_a_onerar = df_reenviar['VALOR'] # Valor da mensalidade
    tipo_de_distribuicao = 'ap_fixo_empilhamento' # Padrão
    numero_documento_titular = '13998916000124' # CNPJ MarketUP
    tipo_de_conta = 'CC' # Conta corrente
    compe = ''
    ispb = '60746948'
    agencia = '138'
    numero_da_conta = '0009350-5'
    nome_titular = ''
    
    dados_ap007b = {
    'tipo_de_operacao':tipo_de_operacao_i,
    'referencia_externa':referencia_externa,
    'identificador_do_contrato':identificador_do_contrato,
    'instituicao_credenciadora':instituicao_credenciadora,
    'usuario_final_recebedor':usuario_final_recebedor,
    'arranjo_de_pagamento':arranjo_de_pagamento,
    'data_liquidacao_inicio':data_liquidacao_inicio,
    'data_liquidacao_fim':data_liquidacao_fim,
    'titular':titular,
    'regras_de_divisao':regras_de_divisao,
    'valor_a_onerar':valor_a_onerar,
    'tipo_de_distribuicao':tipo_de_distribuicao,
    'numero_documento_titular':numero_documento_titular,
    'tipo_de_conta':tipo_de_conta,
    'compe':compe,
    'ispb':ispb,
    'agencia':agencia,
    'numero_da_conta':numero_da_conta,
    'nome_titular':nome_titular
    }
    
    df_ap007b = pd.DataFrame(dados_ap007b)
    
    # Corrigindo valores
    df_ap007b['valor_a_onerar'] = df_ap007b['valor_a_onerar'].apply(corrigir_valor)
    df_ap007b['valor_a_onerar'] = df_ap007b['valor_a_onerar'].map('{:.2f}'.format)
    
    nome_arquivo = f'CERC-AP007B_52541797_{data_nome_arquivo}_000000{numero_arquivo}.csv'
    df_ap007b.to_csv(f'arquivos_entrada/AP_007B/{nome_arquivo}.gz', header=None, sep=';', index=False)