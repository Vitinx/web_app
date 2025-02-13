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

def gerar_arquivo_ap007a_criacao(df_cnpj, prefixo_mes, data_nome_arquivo, data_inicio_assinatura, data_fim_assinatura, numero_arquivo):
    # Definindo os tipos de operação
    tipo_de_operacao_c = 'C'  # Criar contrato
    tipo_de_operacao_a = 'A'  # Atualizar contrato
    tipo_de_operacao_i = 'I'  # Inativar contrato
    tipo_de_operacao_b = 'B'  # Baixa
    tipo_de_operacao_s = 'S'  # Simular contrato

    # Criando os campos
    referencia_externa = prefixo_mes + df_cnpj['ID'].astype(str)  # Código
    identificador_do_contrato = 'id' + df_cnpj['ID'].astype(str)  # Código
    contratante = df_cnpj['CNPJ']  # CNPJ cliente
    repactuacao = '0'  # Não
    lista_de_identificadores = ''
    participante = '52541797000138'  # CNPJ Veon
    detentor = '52541797000138'  # CNPJ Veon
    tipo_de_efeito = '3'  # Ônus - Outros
    saldo_devedor = df_cnpj['VALOR']  # Valor da mensalidade
    limite_da_operacao = df_cnpj['VALOR']  # Valor da mensalidade
    valor_a_ser_mantido = df_cnpj['VALOR']  # Valor da mensalidade
    data_da_assinatura = data_inicio_assinatura  # Data de início da cobrança
    data_de_vencimento = data_fim_assinatura  # Data de fim da cobrança
    tipo_de_servico = '1'  # Gestão colateral
    modalidade_da_operacao = '3'  # Outros
    lista_de_parcela = ''
    carteira = ''
    tipo_de_avaliacao = ''
    taxa_de_juros = ''
    indexador = ''
    aceite_incondicional_da_operacao = '1'  # Aceitar

    # Montando o dicionário de dados
    dados = {
        'tipo_de_operacao': tipo_de_operacao_c,
        'referencia_externa': referencia_externa,
        'identificador_do_contrato': identificador_do_contrato,
        'contratante': contratante,
        'repactuacao': repactuacao,
        'lista_de_identificadores': lista_de_identificadores,
        'participante': participante,
        'detentor': detentor,
        'tipo_de_efeito': tipo_de_efeito,
        'saldo_devedor': saldo_devedor,
        'limite_da_operacao': limite_da_operacao,
        'valor_a_ser_mantido': valor_a_ser_mantido,
        'data_da_assinatura': data_da_assinatura,
        'data_de_vencimento': data_de_vencimento,
        'tipo_de_servico': tipo_de_servico,
        'modalidade_da_operacao': modalidade_da_operacao,
        'lista_de_parcela': lista_de_parcela,
        'carteira': carteira,
        'tipo_de_avaliacao': tipo_de_avaliacao,
        'taxa_de_juros': taxa_de_juros,
        'indexador': indexador,
        'aceite_incondicional_da_operacao': aceite_incondicional_da_operacao
    }

    # Criando o dataframe
    df_ap007a = pd.DataFrame(dados)
    
    # Corrigindo os valores
    df_ap007a['saldo_devedor'] = df_ap007a['saldo_devedor'].apply(corrigir_valor)
    df_ap007a['saldo_devedor'] = df_ap007a['saldo_devedor'].map('{:.2f}'.format)
    df_ap007a['limite_da_operacao'] = df_ap007a['limite_da_operacao'].apply(corrigir_valor)
    df_ap007a['limite_da_operacao'] = df_ap007a['limite_da_operacao'].map('{:.2f}'.format)
    df_ap007a['valor_a_ser_mantido'] = df_ap007a['valor_a_ser_mantido'].apply(corrigir_valor)
    df_ap007a['valor_a_ser_mantido'] = df_ap007a['valor_a_ser_mantido'].map('{:.2f}'.format)

    # Gerando o nome do arquivo
    nome_arquivo = f'CERC-AP007A_52541797_{data_nome_arquivo}_000000{numero_arquivo}.csv'

    # Salvando o arquivo CSV comprimido
    #df_ap007a.to_csv(f'data/arquivos_entrada/AP_007A/{nome_arquivo}.gz', header=None, sep=';', index=False)
    
    # Salvando o arquivo CSV comprimido em um buffer
    buffer = io.BytesIO()
    df_ap007a.to_csv(buffer, header=None, sep=';', index=False, compression='gzip')
    buffer.seek(0)
    
    return buffer, nome_arquivo
    
    #def save_to_excel(df_ap007a):
    #    df_ap007a.to_csv(f'data/arquivos_entrada/AP_007A/{nome_arquivo}.gz', header=None, sep=';', index=False)
   
