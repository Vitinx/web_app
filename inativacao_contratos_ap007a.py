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

def gerar_arquivo_ap007a_inativacao(df_reenviar, prefixo_mes, data_nome_arquivo, data_inicio_assinatura, data_fim_assinatura, numero_arquivo):
    #Definindo tipo de operacao
    tipo_de_operacao_c = 'C' # Criar contrato
    tipo_de_operacao_a = 'A' # Atualizar contrato
    tipo_de_operacao_i = 'I' # Inativar contrato
    tipo_de_operacao_b = 'B' # Baixa
    tipo_de_operacao_s = 'S' # Simular contrato

    referencia_externa = prefixo_mes+df_reenviar['ID'].astype(str) # Código
    identificador_do_contrato = 'id'+df_reenviar['ID'].astype(str) # Código
    contratante = df_reenviar['CNPJ'] # CNPJ cliente
    repactuacao = '0' # Não
    lista_de_identificadores = ''
    participante = '52541797000138' # CNPJ Veon
    detentor = '52541797000138' # CNPJ Veon
    tipo_de_efeito = '3' # Ônus - Outros
    saldo_devedor = df_reenviar['VALOR'] # Valor da mensalidade
    limite_da_operacao = df_reenviar['VALOR'] # Valor da mensalidade
    valor_a_ser_mantido = df_reenviar['VALOR'] # Valor da mensalidade
    data_da_assinatura = data_inicio_assinatura # Data de início da cobrança
    data_de_vencimento = data_fim_assinatura # Data de fim da cobrança
    tipo_de_servico = '1' # Gestão colateral
    modalidade_da_operacao = '3' # Outros
    lista_de_parcela = ''
    carteira = ''
    tipo_de_avaliacao = ''
    taxa_de_juros = ''
    indexador = ''
    aceite_incondicional_da_operacao = '1' # Aceitar
    
    dados = {
    'tipo_de_operacao':tipo_de_operacao_i,
    'referencia_externa':referencia_externa,
    'identificador_do_contrato':identificador_do_contrato,
    'contratante':contratante,
    'repactuacao':repactuacao,
    'lista_de_identificadores':lista_de_identificadores,
    'participante':participante,
    'detentor':detentor,
    'tipo_de_efeito':tipo_de_efeito,
    'saldo_devedor':saldo_devedor,
    'limite_da_operacao':limite_da_operacao,
    'valor_a_ser_mantido':valor_a_ser_mantido,
    'data_da_assinatura':data_da_assinatura,
    'data_de_vencimento':data_de_vencimento,
    'tipo_de_servico':tipo_de_servico,
    'modalidade_da_operacao':modalidade_da_operacao,
    'lista_de_parcela':lista_de_parcela,
    'carteira':carteira,
    'tipo_de_avaliacao':tipo_de_avaliacao,
    'taxa_de_juros':taxa_de_juros,
    'indexador':indexador,
    'aceite_incondicional_da_operacao':aceite_incondicional_da_operacao
    }
    
    df_ap007a = pd.DataFrame(dados)
    
    # Corrigindo os valores
    df_ap007a['saldo_devedor'] = df_ap007a['saldo_devedor'].apply(corrigir_valor)
    df_ap007a['saldo_devedor'] = df_ap007a['saldo_devedor'].map('{:.2f}'.format)
    df_ap007a['limite_da_operacao'] = df_ap007a['limite_da_operacao'].apply(corrigir_valor)
    df_ap007a['limite_da_operacao'] = df_ap007a['limite_da_operacao'].map('{:.2f}'.format)
    df_ap007a['valor_a_ser_mantido'] = df_ap007a['valor_a_ser_mantido'].apply(corrigir_valor)
    df_ap007a['valor_a_ser_mantido'] = df_ap007a['valor_a_ser_mantido'].map('{:.2f}'.format)
    
    nome_arquivo = f'CERC-AP007A_52541797_{data_nome_arquivo}_000000{numero_arquivo}.csv'
    df_ap007a.to_csv(f'arquivos_entrada/AP_007A/{nome_arquivo}.gz', header=None, sep=';', index=False)     