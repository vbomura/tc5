import pandas as pd
import unicodedata
import re

# Como estamos importando de um excel, vamos ter que ajustar o nome das colunas
def normalizar_colunas(df):
    def remover_acentos(texto):
        return ''.join(
            c for c in unicodedata.normalize('NFKD', texto)
            if not unicodedata.combining(c)
        )

    df = df.copy()
    df.columns = [
        remover_acentos(col)
            .lower()
            .replace(' ', '_')
        for col in df.columns
    ]

    return df

# Como vamos juntar alguns dataframes, é melhor que estejam com os mesmos nomes algumas colunas
def renomear_colunas(df, mapa_colunas):
    """
    Parâmetros:
    df (pd.DataFrame): DataFrame original
    mapa_colunas (dict): {'nome_antigo': 'nome_novo'}

    Retorna:
    pd.DataFrame: DataFrame com colunas renomeadas
    """
    df = df.copy()

    # Aplica somente às colunas que existem no DataFrame
    mapa_valido = {
        col_antiga: col_nova
        for col_antiga, col_nova in mapa_colunas.items()
        if col_antiga in df.columns
    }

    df.rename(columns=mapa_valido, inplace=True)
    return df

"""
Como os dataframes tem colunas diferentes, na hora de juntar essa função irá ajudar.
Iremos adicionar colunas nos outros dataframes para que a junção possa ocorrer (as colunas terão dasdos vazios)
"""
def adaptar_dataframe(df, colunas_base, origem, lista_ids):
    df=df.copy()

     # filtra apenas os IDs desejados
    df = df[df['ra'].isin(lista_ids)]

    # adiciona colunas que faltam
    for col in colunas_base:
        if col not in df.columns:
            df[col] = pd.NA

    # mantém apenas as colunas do principal
    df = df[colunas_base]

    # cria coluna de origem
    df['ano_dataframe'] = origem

    return df

# Função correção de tipo de colunas
def corrigir_dados(tipo, dataframe, colunas):
    """
    Corrige o tipo de dados de colunas de um DataFrame.

    Parâmetros:
    tipo (str): tipo alvo ('int', 'float', 'str', 'data')
    dataframe (pd.DataFrame): DataFrame original
    colunas (list ou str): coluna ou lista de colunas

    Retorna:
    pd.DataFrame: DataFrame com colunas corrigidas
    """
    df = dataframe.copy()

    if isinstance(colunas, str):
        colunas = [colunas]

    match tipo.lower():
        case 'int':
            for col in colunas:
                df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

        case 'float':
            for col in colunas:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        case 'str':
            for col in colunas:
                df[col] = df[col].astype(str).str.strip()

        case 'data' | 'datetime':
            for col in colunas:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        case _:
            raise ValueError(
                f"Tipo '{tipo}' não suportado. "
                "Use: int, float, str, data"
            )

    return df

def colunas_totalmente_vazias(df):
    """
    Identifica colunas que possuem apenas valores vazios e deleta

    Parâmetros:
    df (pd.DataFrame): DataFrame de entrada
    remover (bool): se True, remove as colunas vazias

    Retorna:
    pd.DataFrame:
        - DataFrame sem colunas vazias (remover=True)
    """
    df_tmp = df.copy()

    # considera strings vazias como NaN
    df_tmp = df_tmp.replace(r'^\s*$', pd.NA, regex=True)

    colunas_vazias = [
        col for col in df_tmp.columns
        if df_tmp[col].isna().all()
    ]

    return df_tmp.drop(columns=colunas_vazias)
def arredondar_floats(df, casas=2):
    """
    Arredonda todas as colunas float de um DataFrame.

    Parâmetros:
    df (pd.DataFrame): DataFrame de entrada
    casas (int): número de casas decimais (padrão = 2)

    Retorna:
    pd.DataFrame: DataFrame com floats arredondados
    """
    df = df.copy()

    colunas_float = df.select_dtypes(include=['float', 'float64', 'float32']).columns

    df[colunas_float] = df[colunas_float].round(casas)

    return df

def normalizar_fase(valor):
    """
    Converte valores como '1A', '2C', '8F' ou 9 em 'FASE X'.
    Mantém valores sem número (ex: 'ALFA').
    """
    valor_str = str(valor)
    numeros = "".join(filter(str.isdigit, valor_str))
    
    if numeros:
        return f"FASE {numeros}"
    else:
        return valor

def remover_texto_parenteses(valor):
    """
    Remove qualquer texto entre parênteses e retorna o texto em MAIÚSCULO.
    Ex: 'Fase 1 (3° e 4° ano)' , 'Fase 2 (5° e 6° ano)', 'Fase 3 (7° e 8° ano)', 'Fase 4 (9° ano)',
       'Fase 6 (2° EM)', 'Fase 5 (1° EM)', 'Fase 7 (3° EM)',
       'Fase 8 (Universitários)' -> 'FASE 1', 'FASE 2', 'FASE 3', etc
    """
    if pd.isna(valor):
        return valor
    
    texto_limpo = re.sub(r"\s*\(.*?\)", "", str(valor)).strip()
    return texto_limpo.upper()
