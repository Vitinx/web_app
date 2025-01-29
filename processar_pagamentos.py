import pandas as pd
import numpy as np
from datetime import datetime
import locale

# Definir localidade para formatação de moeda
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


def calculate_paid_amount(group):
    """
    Calcula o valor total pago por CNPJ somando todos os valores constituídos
    """
    # Filtra apenas as linhas com data de liquidação
    paid_rows = group[group['data_liquidacao'].notna()]
    if paid_rows.empty:
        return 0
    
    # Soma todos os valores constituídos para o CNPJ
    total_value = paid_rows['valor_constituido_contrato_unidade_recebivel'].sum()
    return total_value

def standardize_cnpj_columns(df_cnpj):
    """
    Padronizando os nomes das colunas do CNPJ DataFrame verificando diversas variações comuns.
    """
    column_mappings = {
        'RAZAO_SOCIAL': [
            'RAZAO_SOCIAL', 'RAZAO SOCIAL', 'razao_social', 'razao social',
            'RAZAOSOCIAL', 'razaosocial', 'Razao Social', 'Razão Social',
            'RAZÃO SOCIAL', 'razão_social', 'VALOR RAZAO SOCIAL'
        ],
        'NOME_FANTASIA': [
            'NOME_FANTASIA', 'NOME FANTASIA', 'nome_fantasia', 'nome fantasia',
            'NOMEFANTASIA', 'nomefantasia', 'Nome Fantasia', 'Nome fantasia',
            'Nome_Fantasia'
        ],
        'CNPJ': [
            'CNPJ', 'cnpj', 'Cnpj', 'CPF_CNPJ', 'cpf_cnpj', 'CPF/CNPJ',
            'DOCUMENTO', 'documento'
        ],
        'CAMPANHA': [
            'CAMPANHA', 'campanha', 'Campanha'
        ],
        'ID': [
            'ID', 'id', 'Id'
        ]
    }
    
    # Imprimir as colunas disponíveis para debug
    print("Colunas disponíveis no DataFrame:", df_cnpj.columns.tolist())
    
    # Criando um mapeamento de nomes de colunas reais para nomes padronizados
    new_columns = {}
    for standard_name, variations in column_mappings.items():
        found = False
        for variant in variations:
            if variant in df_cnpj.columns:
                new_columns[variant] = standard_name
                found = True
                break
                
    # Renomear colunas encontradas
    if new_columns:
        df_cnpj = df_cnpj.rename(columns=new_columns)
    
    # Verificar quais colunas obrigatórias estão faltando
    required_cols = {'RAZAO_SOCIAL', 'NOME_FANTASIA', 'CNPJ', 'CAMPANHA'}
    missing_cols = required_cols - set(df_cnpj.columns)
    
    # Adicionar colunas faltantes com valores padrão
    for col in missing_cols:
        if col == 'CNPJ':
            raise ValueError(f"Coluna CNPJ é obrigatória e não foi encontrada no arquivo.")
        elif col == 'RAZAO_SOCIAL':
            # Se não tiver RAZAO_SOCIAL, usa NOME_FANTASIA se disponível, senão usa "NÃO INFORMADO"
            if 'NOME_FANTASIA' in df_cnpj.columns:
                df_cnpj[col] = df_cnpj['NOME_FANTASIA']
            else:
                df_cnpj[col] = 'NÃO INFORMADO'
        elif col == 'NOME_FANTASIA':
            # Se não tiver NOME_FANTASIA, usa RAZAO_SOCIAL se disponível, senão usa "NÃO INFORMADO"
            if 'RAZAO_SOCIAL' in df_cnpj.columns:
                df_cnpj[col] = df_cnpj['RAZAO_SOCIAL']
            else:
                df_cnpj[col] = 'NÃO INFORMADO'
        elif col == 'CAMPANHA':
            df_cnpj[col] = 'Anúncio'
    
    return df_cnpj

def process_payment_data(df_ap005, df_cnpj):
    """
    Processa dados de pagamento com correção no processamento dos valores
    """
    try:
        # Imprimir as colunas disponíveis para debug
        print("Colunas no DataFrame CNPJ antes da padronização:", df_cnpj.columns.tolist())
        
        # Padroniza as colunas do DataFrame CNPJ
        df_cnpj = standardize_cnpj_columns(df_cnpj)
        
        print("Colunas no DataFrame CNPJ após a padronização:", df_cnpj.columns.tolist())
        
        # Converte os valores do CNPJ para numérico
        if 'VALOR' in df_cnpj.columns:
            df_cnpj['VALOR'] = pd.to_numeric(df_cnpj['VALOR'].astype(str).str.replace(',', '.'), errors='coerce')
        else:
            raise ValueError("Coluna 'VALOR' não encontrada no DataFrame CNPJ")
        
        # Converte usuario_final_recebedor para string
        df_ap005['usuario_final_recebedor'] = df_ap005['usuario_final_recebedor'].astype(str).str.replace('[^0-9]', '', regex=True)
        
        # Remove pontos e traços do CNPJ
        df_cnpj['CNPJ'] = df_cnpj['CNPJ'].astype(str).str.replace('[^0-9]', '', regex=True)
        
        # Processamento da coluna informacoes_pagamento
        df_ap005['informacoes_pagamento'] = df_ap005['informacoes_pagamento'].str.split('|').str[0]
        
        # Separa as informações de pagamento
        df_separado = df_ap005['informacoes_pagamento'].str.split(';', expand=True)
        
        # Define as novas colunas
        novas_colunas = [
            "numero_documento_titular", "tipo_conta", "compe", "ispb", 
            "agencia", "numero_conta", "valor_a_pagar", "beneficiario", 
            "data_liquidacao_efetiva", "valor_liquidacao_efetiva", "regra_divisao",
            "valor_onerado_unidade_recebivel", "tipo_informacao_pagamento", 
            "indicador_ordem_efeito", "valor_constituido_contrato_unidade_recebivel"
        ]
        
        # Atribui nomes às colunas
        df_separado.columns = novas_colunas[:df_separado.shape[1]]
        
        # Concatena com o DataFrame original
        df_ap005 = pd.concat([
            df_ap005.drop('informacoes_pagamento', axis=1),
            df_separado
        ], axis=1)
        
        # Converte valor_constituido_contrato_unidade_recebivel para numérico
        df_ap005['valor_constituido_contrato_unidade_recebivel'] = pd.to_numeric(
            df_ap005['valor_constituido_contrato_unidade_recebivel'].replace('', '0').fillna('0'),
            errors='coerce'
        )
        
        # Converte data_liquidacao_efetiva para datetime
        df_ap005['data_liquidacao'] = pd.to_datetime(
            df_ap005['data_liquidacao_efetiva'],
            errors='coerce'
        )

        # Remove registros duplicados considerando todas as colunas
        df_ap005 = df_ap005.drop_duplicates()
        
        # Converte o número do documento do titular para string
        df_ap005['numero_documento_titular'] =  df_ap005['numero_documento_titular'].astype(str)
        
        # Filtra apenas o documento do titular: '13998916000124'
        df_ap005 = df_ap005[df_ap005['numero_documento_titular'] == '13998916000124']
        
        # Agrupa por usuário final recebedor, mas só considera valores onde há data de liquidação
        df_grouped = df_ap005.groupby('usuario_final_recebedor').agg({
            'valor_constituido_contrato_unidade_recebivel': 'sum',
            'data_liquidacao': 'max'
        }).reset_index()
        
        # Merge com dados de CNPJ
        result = pd.merge(
            df_cnpj,
            df_grouped,
            left_on='CNPJ',
            right_on='usuario_final_recebedor',
            how='left'
        )
        
        # Determina status de pagamento com nova lógica
        def determine_status(row):
            if pd.isna(row['data_liquidacao']) or float(row['valor_constituido_contrato_unidade_recebivel']) == 0:
                return 'NÃO PAGO'
            
            valor_mensalidade = float(row['VALOR'])
            valor_pago = float(row['valor_constituido_contrato_unidade_recebivel'])
            
            percentual_pago = (valor_pago / valor_mensalidade * 100) if valor_mensalidade > 0 else 0
            
            return 'PAGO' if percentual_pago >= 50 else 'NÃO PAGO'
        
        # Criar DataFrame final com nova lógica para valor cobrado e data
        final_result = pd.DataFrame({
            'ID': result['ID'],
            'CNPJ': result['CNPJ'],
            'CAMPANHA': result['CAMPANHA'],
            'RAZAO_SOCIAL': result['RAZAO_SOCIAL'],
            'NOME_FANTASIA': result.apply(
                lambda x: x['RAZAO_SOCIAL'] if pd.isna(x['NOME_FANTASIA']) or x['NOME_FANTASIA'].strip() == '' 
                else x['NOME_FANTASIA'], 
                axis=1
            ),
            'VALOR_MENSALIDADE': result['VALOR'],
            'DATA_LIQUIDACAO': result.apply(
                lambda x: x['data_liquidacao'] if pd.notnull(x['data_liquidacao']) and float(x['valor_constituido_contrato_unidade_recebivel']) > 0 else None,
                axis=1
            ),
            'VALOR_COBRADO': result.apply(
                lambda x: x['valor_constituido_contrato_unidade_recebivel'] if pd.notnull(x['data_liquidacao']) else 0,
                axis=1
            ),
            'STATUS_PAGAMENTO': result.apply(determine_status, axis=1)
        })
        
        # Formata valores monetários
        for col in ['VALOR_MENSALIDADE', 'VALOR_COBRADO']:
            final_result[col] = final_result[col].apply(
                lambda x: locale.currency(x, grouping=True, symbol=None) if pd.notnull(x) else '0,00'
            )
        
        # Formata data
        final_result['DATA_LIQUIDACAO'] = final_result['DATA_LIQUIDACAO'].apply(
            lambda x: x.strftime('%d/%m/%Y') if pd.notnull(x) else ''
        )
        
        return final_result
    
    except Exception as e:
        print(f"Erro detalhado: {str(e)}")
        print("Colunas disponíveis no df_ap005:", df_ap005.columns)
        print("Colunas disponíveis no df_cnpj:", df_cnpj.columns)
        raise Exception(f"Erro ao processar dados de pagamento: {str(e)}")
    
def style_excel(writer, df):
    """
    Aplica estilização ao arquivo Excel
    """
    workbook = writer.book
    worksheet = writer.sheets['Payments']
    
    # Define formatos
    header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'fg_color': '#D7E4BC',
        'border': 1
    })
    
    # Adiciona mais formatos para melhor visualização
    money_format = workbook.add_format({
        'num_format': 'R$ #,##0.00',
        'border': 1
    })
    
    date_format = workbook.add_format({
        'num_format': 'dd/mm/yyyy',
        'border': 1
    })
    
    # Formato padrão para células
    cell_format = workbook.add_format({
        'border': 1,
        'align': 'center'
    })
    
    # Aplica formatos
    for idx, col in enumerate(df.columns):
        # Ajusta largura da coluna baseado no conteúdo
        max_length = max(df[col].astype(str).apply(len).max(), len(col))
        worksheet.set_column(idx, idx, max_length + 2)
        
        # Aplica formatos específicos para cada tipo de coluna
        if 'VALOR' in col:
            worksheet.set_column(idx, idx, max_length + 2, money_format)
        elif 'DATA' in col:
            worksheet.set_column(idx, idx, max_length + 2, date_format)
        else:
            worksheet.set_column(idx, idx, max_length + 2, cell_format)
    
    # Escreve cabeçalhos com formato
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)
    
    # Adiciona cores alternadas nas linhas
    for row_num in range(1, len(df) + 1):
        row_format = workbook.add_format({
            'bg_color': '#F0F0F0' if row_num % 2 == 0 else '#FFFFFF',
            'border': 1
        })
        
        for col_num in range(len(df.columns)):
            value = df.iloc[row_num-1, col_num]
            if pd.isna(value):
                worksheet.write_string(row_num, col_num, '', row_format)
            else:
                worksheet.write(row_num, col_num, value, row_format)

def save_to_excel(df, output_path):
    """
    Salva os dados processados em um arquivo Excel estilizado
    """
    writer = pd.ExcelWriter(output_path, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Payments', index=False)
    style_excel(writer, df)
    writer.close()

def main(ap005_df, cnpj_df, output_path):
    try:
        result_df = process_payment_data(ap005_df, cnpj_df)
        save_to_excel(result_df, output_path)
        return True, result_df
    except Exception as e:
        return False, str(e)