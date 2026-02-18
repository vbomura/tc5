#Necessario instalar:
#pip install streamlit pandas xlsxwriter openpyxl numpy

import sys
import os
import streamlit as st
import pandas as pd
import io
import numpy as np
import joblib
from tools.utils import FeatureSelector,substituir_valores_coluna, remover_texto_parenteses, normalizar_fase


def realizar_predicao(df):
    """Processa os dados e aplica o modelo de Machine Learning."""
    df = df.copy()
    
    # Tratamento de colunas usando as funções do utils.py
    df["fase"] = df["fase"].map(normalizar_fase)   
    df["fase_ideal"] = df["fase_ideal"].map(remover_texto_parenteses)

    mapeamento_defasagem = {
        'ALFA': 0, 'FASE 1': 1, 'FASE 2': 2, 'FASE 3': 3,
        'FASE 4': 4, 'FASE 5': 5, 'FASE 6': 6, 'FASE 7': 7 
    }

    df = substituir_valores_coluna(df=df, coluna='fase', mapeamento=mapeamento_defasagem)

    # Limpeza de dados nulos/vazios
    base_filtrado = df[df['pedra'].isna() | (df['pedra'].astype(str).str.strip() == '') | (df['pedra'].astype(str).str.strip() == 'INCLUIR')]
    df = df.drop(index=base_filtrado.index)

    #Mesmas colunas utilizadas na predição do ML:
    features_do_modelo = [
        'inde', 'ieg', 'iaa', 'ips', 'ida', 'ian', 
        'idade', 'ipv', 'defasagem', 'fase', 'fase_ideal'
    ]

    #Limpando linhas nulas
    df[features_do_modelo] = df[features_do_modelo].replace(r'^\s*$', np.nan, regex=True)
    df = df.dropna(subset=features_do_modelo)
    
    st.info(f"Linhas restantes após limpeza: {len(df)}")
    
    # Carregamento do modelo (ajuste o caminho se necessário)
    caminho_modelo = os.path.join(os.path.dirname(__file__), 'tools/Defasagem.joblib')
    modelo = joblib.load(caminho_modelo)

    #Aplicando o modelo
    df['predicao_grupo'] = modelo.predict(df[features_do_modelo])
    
    return df

# --- Interface Streamlit ---
st.set_page_config(page_title="Sistema de Predição - Passos Mágicos", layout="wide")
st.title("📊 Aplicação de Predição para identificar possivel defasagem")

arquivo_carregado = st.file_uploader("Carregue seu arquivo", type=["xlsx", "xls", "csv"])

if arquivo_carregado:
    try:
        df = pd.read_csv(arquivo_carregado) if arquivo_carregado.name.endswith('.csv') else pd.read_excel(arquivo_carregado)
        
        st.subheader("Pré-visualização")
        st.dataframe(df.head())

        if st.button("Realizar Predição", type="primary"):
            with st.spinner('Processando...'):
                df_resultado = realizar_predicao(df)
                st.success("Sucesso!")
                st.dataframe(df_resultado.head())

                # Download
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df_resultado.to_excel(writer, index=False)
                
                st.download_button(
                    label="📥 Baixar Resultado (.xlsx)",
                    data=buffer.seek(0) or buffer,
                    file_name="resultado_defasagem_passos_magicos.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    except Exception as e:
        st.error(f"Erro: {e}")