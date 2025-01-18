import pandas as pd
import numpy as np
from datetime import datetime
import locale

# Definir localidade para formatação de moeda
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

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
        ]
    }
    
    # Criando um mapeamento de nomes de colunas reais para nomes padronizados
    new_columns = {}
    for standard_name, variations in column_mappings.items():
        for variant in variations:
            if variant in df_cnpj.columns:
                new_columns[variant] = standard_name
                break
    
    # Se não encontrou a coluna de nome fantasia, procura pelo nome exato da coluna
    if 'Nome fantasia' in df_cnpj.columns:
        new_columns['Nome fantasia'] = 'NOME_FANTASIA'
    
    # Renomear colunas encontradas
    if new_columns:
        df_cnpj = df_cnpj.rename(columns=new_columns)
    
    # Garantir que as colunas existem com valores padrão apenas se necessário
    required_cols = {'RAZAO_SOCIAL', 'NOME_FANTASIA', 'CNPJ', 'CAMPANHA'}
    for col in required_cols:
        if col not in df_cnpj.columns:
            if col == 'CNPJ':
                raise ValueError(f"Coluna CNPJ é obrigatória e não foi encontrada no arquivo.")
            if col == 'CAMPANHA':
                df_cnpj[col] = 'Anúncio'
            else:
                df_cnpj[col] = df_cnpj['RAZAO_SOCIAL'] if col == 'NOME_FANTASIA' else 'NÃO INFORMADO'
    
    return df_cnpj

def process_payment_data(df_ap005, df_cnpj):
    """
    Processa dados de pagamento do AP005 e CNPJ DataFrames
    """
    try:
        # Padroniza as colunas do DataFrame CNPJ
        df_cnpj = standardize_cnpj_columns(df_cnpj)
        
        # Converte os valores do CNPJ para numérico
        df_cnpj['VALOR'] = pd.to_numeric(df_cnpj['VALOR'].astype(str).str.replace(',', '.'), errors='coerce')
        
        # Processa a coluna informacoes_pagamento do AP005
        df_ap005['informacoes_pagamento'] = df_ap005['informacoes_pagamento'].str.split('|').str[0]
        novas_colunas = [
            "numero_documento_titular", "tipo_conta", "compe", "ispb", 
            "agencia", "numero_conta", "valor_a_pagar", "beneficiario", 
            "data_liquidacao_efetiva", "valor_liquidacao_efetiva", "regra_divisao",
            "valor_onerado_unidade_recebivel", "tipo_informacao_pagamento", 
            "indicador_ordem_efeito", "valor_constituido_contrato_unidade_recebivel"
        ]
        
        # Separa as informações de pagamento
        df_separado = df_ap005['informacoes_pagamento'].str.split(';', expand=True)
        df_separado.columns = novas_colunas[:df_separado.shape[1]]
        
        # Adiciona as novas colunas ao DataFrame original
        df_ap005 = pd.concat([df_ap005.drop('informacoes_pagamento', axis=1), df_separado], axis=1)
        
        # Converte valor_constituido_contrato_unidade_recebivel para numérico
        df_ap005['valor_constituido_contrato_unidade_recebivel'] = pd.to_numeric(
            df_ap005['valor_constituido_contrato_unidade_recebivel'].replace('', '0').fillna('0'),
            errors='coerce'
        )
        
        # Converte data_liquidacao para datetime
        df_ap005['data_liquidacao'] = pd.to_datetime(
            df_ap005['data_liquidacao'], 
            errors='coerce'
        )
        
        # Remove duplicatas do AP005 antes de processar
        df_ap005 = df_ap005.drop_duplicates(subset=['usuario_final_recebedor', 'valor_constituido_contrato_unidade_recebivel'])
        
        # Agrupa os valores totais de mensalidade por CNPJ
        cnpj_mensalidades = df_cnpj.groupby('CNPJ').agg({
            'VALOR': 'sum',
            'RAZAO_SOCIAL': 'first',
            'NOME_FANTASIA': 'first',
            'CAMPANHA': 'first'
        }).reset_index()
        
        # Calcula o valor total pago por CNPJ
        def calculate_paid_amount(group):
            # Filtra apenas as linhas com data de liquidação
            paid_rows = group[group['data_liquidacao'].notna()]
            if paid_rows.empty:
                return 0
                
            # Pega o valor mais recente para cada CNPJ
            latest_payment = paid_rows.sort_values('data_liquidacao', ascending=False).iloc[0]
            return latest_payment['valor_constituido_contrato_unidade_recebivel']
        
        # Agrupa AP005 por CNPJ
        grouped_ap005 = df_ap005.groupby('usuario_final_recebedor').agg({
            'data_liquidacao': lambda x: x.max() if x.notna().any() else pd.NaT,
            'referencia_externa': 'first'
        }).reset_index()
        
        # Calcula valor total pago por CNPJ considerando apenas o pagamento mais recente
        paid_amounts = df_ap005.groupby('usuario_final_recebedor').apply(calculate_paid_amount)
        grouped_ap005['valor_pago'] = grouped_ap005['usuario_final_recebedor'].map(paid_amounts)
        
        # Merge dos dados
        result = pd.merge(
            grouped_ap005,
            cnpj_mensalidades,
            left_on='usuario_final_recebedor',
            right_on='CNPJ',
            how='inner'
        )
        
        # Determina status de pagamento
        def determine_status(row):
            if pd.isna(row['data_liquidacao']):
                return 'NÃO PAGO'
            
            valor_mensalidade = float(row['VALOR'])
            valor_pago = float(row['valor_pago'])
            
            if valor_mensalidade == 0:
                return 'NÃO PAGO'
                
            percentual_pago = (valor_pago / valor_mensalidade * 100)
            
            if percentual_pago >= 100:
                return 'PAGO'
            elif percentual_pago >= 50:
                return 'PAGO PARCIALMENTE'
            else:
                return 'NÃO PAGO'
        
        result['status_pagamento'] = result.apply(determine_status, axis=1)
        
        # Usa RAZAO_SOCIAL quando NOME_FANTASIA estiver vazio
        result['NOME_FANTASIA'] = result.apply(
            lambda x: x['RAZAO_SOCIAL'] if pd.isna(x['NOME_FANTASIA']) or x['NOME_FANTASIA'].strip() == '' 
            else x['NOME_FANTASIA'], 
            axis=1
        )
        
        # Cria resultado final
        final_result = pd.DataFrame({
            'ID': result['referencia_externa'],
            'CNPJ': result['CNPJ'],
            'CAMPANHA': result['CAMPANHA'],
            'RAZAO_SOCIAL': result['RAZAO_SOCIAL'],
            'NOME_FANTASIA': result['NOME_FANTASIA'],
            'VALOR_MENSALIDADE': result['VALOR'],
            'DATA_LIQUIDACAO': result['data_liquidacao'],
            'VALOR_COBRADO': result['valor_pago'],
            'STATUS_PAGAMENTO': result['status_pagamento']
        })
        
        # Remove duplicatas mantendo apenas o registro mais recente por CNPJ
        final_result = final_result.sort_values('DATA_LIQUIDACAO', ascending=False).drop_duplicates(subset=['CNPJ'])
        
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