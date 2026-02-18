import pandas as pd
import re
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

# Seleciona apenas as fetures necessárias e evita erros
class FeatureSelector(BaseEstimator, TransformerMixin):
    def __init__(self, features=None):
        self.features = features

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X[list(self.features)]
    
def substituir_valores_coluna(df: pd.DataFrame, coluna: str, mapeamento: dict, converter_numerico: bool = True) -> pd.DataFrame:
    """Substitui valores específicos de uma coluna usando um dicionário."""
    df = df.copy()
    df[coluna] = df[coluna].replace(mapeamento)
    if converter_numerico:
        df[coluna] = pd.to_numeric(df[coluna], errors='coerce')
    return df

def remover_texto_parenteses(valor):
    """Remove qualquer texto entre parênteses e retorna o texto em MAIÚSCULO."""
    if pd.isna(valor):
        return valor
    texto_limpo = re.sub(r"\s*\(.*?\)", "", str(valor)).strip()
    return texto_limpo.upper()

def normalizar_fase(valor):
    """Converte valores como '1A', '2C' ou 9 em 'FASE X'."""
    valor_str = str(valor)
    numeros = "".join(filter(str.isdigit, valor_str))
    if numeros:
        return f"FASE {numeros}"
    return valor