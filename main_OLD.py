#Necessario instalar:
#pip install streamlit pandas xlsxwriter openpyxl numpy

import streamlit as st
import pandas as pd
import io
import numpy as np
import joblib
import os
from tools.utils import FeatureSelector, substituir_valores_coluna, remover_texto_parenteses, normalizar_fase

# --- Configurações Globais ---
# RA incluído para identificação, mas será separado das features numéricas no modelo
FEATURES_DO_MODELO = [
    'ra', 'inde', 'ieg', 'iaa', 'ips', 'ida', 'ian', 
    'idade', 'ipv', 'defasagem', 'fase', 'fase_ideal'
]

# Apenas as colunas que o modelo realmente espera (numéricas/processadas)
FEATURES_PARA_PREDICAO = [f for f in FEATURES_DO_MODELO if f != 'ra']

@st.cache_resource
def carregar_modelo():
    caminho = os.path.join(os.path.dirname(__file__), 'tools/Defasagem.joblib')
    return joblib.load(caminho)

def gerar_template_excel():
    output = io.BytesIO()
    # Template agora inclui o RA como primeira coluna
    df_template = pd.DataFrame(columns=FEATURES_DO_MODELO + ['pedra'])
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_template.to_excel(writer, index=False)
    return output.getvalue()

def realizar_predicao(df):
    df = df.copy()
    modelo = carregar_modelo()
    
    # Tratamentos de texto/fase
    df["fase"] = df["fase"].map(normalizar_fase)   
    df["fase_ideal"] = df["fase_ideal"].map(remover_texto_parenteses)
    
    mapeamento_defasagem = {
        'ALFA': 0, 'FASE 1': 1, 'FASE 2': 2, 'FASE 3': 3,
        'FASE 4': 4, 'FASE 5': 5, 'FASE 6': 6, 'FASE 7': 7, 'FASE 8': 8 
    }
    df = substituir_valores_coluna(df=df, coluna='fase', mapeamento=mapeamento_defasagem)

    # Limpeza baseada na coluna 'pedra' (se existir)
    if 'pedra' in df.columns:
        base_filtrado = df[df['pedra'].isna() | (df['pedra'].astype(str).str.strip() == '') | (df['pedra'].astype(str).str.strip() == 'INCLUIR')]
        df = df.drop(index=base_filtrado.index)

    # Limpeza de nulos apenas nas colunas de cálculo (ignorando RA para não perder o ID se estiver nulo)
    df[FEATURES_PARA_PREDICAO] = df[FEATURES_PARA_PREDICAO].replace(r'^\s*$', np.nan, regex=True)
    df = df.dropna(subset=FEATURES_PARA_PREDICAO)

    st.info(f"Linhas restantes após limpeza: {len(df)}")
    
    # Predição usando apenas as features numéricas
    df['predicao_defasagem_aluno'] = modelo.predict(df[FEATURES_PARA_PREDICAO])
    
    # Reorganizar colunas para o RA aparecer primeiro no resultado
    cols = ['ra'] + [c for c in df.columns if c != 'ra']
    return df[cols]

# --- Interface Streamlit ---
st.set_page_config(page_title="Passos Mágicos - Datathon FIAP", layout="wide")

st.sidebar.title("📌 Navegação")
pagina = st.sidebar.selectbox("Selecione uma opção:", 
    ["Página Inicial", "Download do Modelo", "Predição via Arquivo", "Predição Individual"])

if pagina == "Página Inicial":
    st.title("🚀 Projeto Datathon: Passos Mágicos & FIAP")
    st.markdown("""
    ### Identificação de Defasagem Acadêmica
    O modelo analisa indicadores do aluno para prever possíveis atrasos no aprendizado.
    
    **Nova Funcionalidade:** Agora o sistema utiliza o **RA (Registro do Aluno)** para garantir que os resultados sejam facilmente vinculados ao cadastro da instituição.
    """)
    st.info("Utilize o menu lateral para navegar entre as ferramentas de predição.")

elif pagina == "Download do Modelo":
    st.title("📄 Download do Template")
    st.write("Baixe o arquivo e preencha o RA e os indicadores de cada aluno.")
    template = gerar_template_excel()
    st.download_button("📥 Baixar Modelo Excel (.xlsx)", data=template, file_name="template_ra_passos_magicos.xlsx")

elif pagina == "Predição via Arquivo":

    st.title("📊 Predição em Lote")
    arquivo = st.file_uploader("Suba o arquivo preenchido", type=["xlsx", "csv"])
    if arquivo:
        df_input = pd.read_csv(arquivo) if arquivo.name.endswith('.csv') else pd.read_excel(arquivo)
        if st.button("Analisar Alunos"):

            # Validação simples de colunas
            colunas_faltantes = set(FEATURES_DO_MODELO) - set(df_input.columns)
            if colunas_faltantes:
                st.error(f"O arquivo enviado está faltando as seguintes colunas obrigatórias: **{', '.join(colunas_faltantes)}**")
                # st.info(f"Por favor, carregue um arquivo válido! (Se necessário faça o download do Modelo para verificar as colunas)")
                st.write(f"Por favor, carregue um arquivo válido! (Se necessário faça o download do Modelo para verificar as colunas)")
                template = gerar_template_excel()
                st.download_button("📥 Baixar Modelo Excel (.xlsx)", data=template, file_name="template_ra_passos_magicos.xlsx")
            
            else:
                try:
                    res = realizar_predicao(df_input)
                    st.success("Análise concluída!")
                    st.dataframe(res)
                    # Download do Resultado
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        res.to_excel(writer, index=False)
                    
                    st.download_button(
                        label="📥 Baixar Resultado Completo (.xlsx)",
                        data=buffer.getvalue(),
                        file_name="resultado_defasagem_passos_magicos.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                except Exception as e:
                    st.error(f"Ocorreu um erro ao tentar realizar a análise do arquivo.")

elif pagina == "Predição Individual":
    st.title("📝 Simulação por Aluno")
    
    with st.form("form_aluno"):
        ra = st.text_input("RA do Aluno", placeholder="Ex: PM-2026-001")
        col1, col2 = st.columns(2)
        with col1:
            # Definindo mínimo de 0.0 e máximo de 10.0 para os índices
            inde = st.number_input("INDE", min_value=0.0, max_value=10.0, value=0.0, step=0.1)
            ieg = st.number_input("IEG (Engajamento)", min_value=0.0, max_value=10.0, value=0.0, step=0.1)
            iaa = st.number_input("IAA (Autoavaliação)", min_value=0.0, max_value=10.0, value=0.0, step=0.1)
            ips = st.number_input("IPS (Social)", min_value=0.0, max_value=10.0, value=0.0, step=0.1)
            ida = st.number_input("IDA (Aprendizado)", min_value=0.0, max_value=10.0, value=0.0, step=0.1)

        with col2:
            ian = st.number_input("IAN (Nível)", min_value=0.0, max_value=10.0, value=0.0, step=0.1)
            
            # Para idade, podemos definir um intervalo realista (ex: 6 a 20 anos)
            idade = st.number_input("Idade", min_value=0, max_value=25, value=10, step=1)
            
            ipv = st.number_input("IPV (Ponto de Virada)", min_value=0.0, max_value=10.0, value=0.0, step=0.1)
            
            # Defasagem costuma ser um valor calculado, ajuste conforme sua regra de negócio
            defasagem = st.number_input("Defasagem", min_value=-5.0, max_value=5.0, value=0.0, step=1.0)
            
            fase = st.selectbox("Fase Atual", ["ALFA"] + [f"FASE {i}" for i in range(1, 9)])
            fase_ideal = st.selectbox("Fase", ["ALFA"] + [f"FASE {i}" for i in range(1, 9)])
            
        enviado = st.form_submit_button("Verificar Aluno")
        
        if enviado:
            dados = pd.DataFrame([{
                'ra': ra, 'inde': inde, 'ieg': ieg, 'iaa': iaa, 'ips': ips, 'ida': ida,
                'ian': ian, 'idade': idade, 'ipv': ipv, 'defasagem': defasagem,
                'fase': fase, 'fase_ideal': fase_ideal
            }])

            #Visualizar dados preenchidos em formato de tabela:
            #st.dataframe(dados)

            resultado = realizar_predicao(dados)
            pred = resultado['predicao_defasagem_aluno'].values[0]
            
            st.subheader(f"Resultado para o RA: {ra}")

            if pred != 0:
                st.warning(f"Retorno da Predição: {pred}")
                st.error("🚨 Probabilidade de Defasagem detectada.")
            else:
                st.info(f"Retorno da Predição: {pred}")
                st.success("✅ O aluno apresenta desempenho condizente com sua fase.")