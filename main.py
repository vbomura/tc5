# Verificar arquivo -> requirements.txt
import streamlit as st
import pandas as pd
import io
import numpy as np
import joblib
import os
from tools.utils import FeatureSelector, substituir_valores_coluna, remover_texto_parenteses, normalizar_fase
import base64
import streamlit.components.v1 as components

# --- Configurações Globais  ---
#Features utilizadas no ML (previsao_v2.ipynb) + RA para geração do arquivo modelo
FEATURES_DO_MODELO = [
            'ra',
            'ida', 
            'ipv', 
            'defasagem',
            'fase'
            ]

FEATURES_PARA_PREDICAO = [f for f in FEATURES_DO_MODELO if f != 'ra']

@st.cache_resource
def carregar_modelo():
    caminho = os.path.join(os.path.dirname(__file__), 'tools/DefasagemNew.joblib')
    return joblib.load(caminho)

def gerar_template_excel():
    output = io.BytesIO()
    # Exemplo supondo de informações
    linhas_exemplo = [
        ['RA-9999', 4, 7.28, 0, 'Fase 7'],   # Dados da Linha de Exemplo 1
        ['RA-8888', 5, 5.72, -1, 'ALFA']     # Dados da Linha de Exemplo 2
    ]

    df_template = pd.DataFrame(linhas_exemplo, columns=FEATURES_DO_MODELO)

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_template.to_excel(writer, index=False)
        
    return output.getvalue()

def realizar_predicao(df,tipo = 1):
    #variavel tipo somente para definir se mostra ou não a limpeza de linhas nulas (somente para predição em lote)
    df = df.copy()
    modelo = carregar_modelo()
    
    df["fase"] = df["fase"].map(normalizar_fase)   
    # df["fase_ideal"] = df["fase_ideal"].map(remover_texto_parenteses)
    
    mapeamento_defasagem = {
        'ALFA': 0, 'FASE 1': 1, 'FASE 2': 2, 'FASE 3': 3,
        'FASE 4': 4, 'FASE 5': 5, 'FASE 6': 6, 'FASE 7': 7, 'FASE 8': 8 
    }
    df = substituir_valores_coluna(df=df, coluna='fase', mapeamento=mapeamento_defasagem)

    df[FEATURES_PARA_PREDICAO] = df[FEATURES_PARA_PREDICAO].replace(r'^\s*$', np.nan, regex=True)
    df = df.dropna(subset=FEATURES_PARA_PREDICAO)

    if tipo == 1:
        #Informando quantas linhas ficaram apos as remoções de linhas inválidas
        st.warning(f"Linhas restantes após exclusão de linhas inválidas (nulas): {len(df)}")

    df['predicao_defasagem_aluno'] = modelo.predict(df[FEATURES_PARA_PREDICAO])
    
    cols = ['ra'] + [c for c in df.columns if c != 'ra']
    return df[cols]

def criar_link_download(dados_binarios, nome_arquivo, texto_link):
    b64 = base64.b64encode(dados_binarios).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{nome_arquivo}">{texto_link}</a>'
    return href

# --- Interface Streamlit ---
st.set_page_config(page_title="Datathon FIAP (9DTAT) - Passos Mágicos", layout="wide")

# --- CSS ---
st.markdown("""
<style>
    /* 1. Reduzir o espaço em branco no topo da página */
    .block-container {
        padding-top: 2rem !important; /* Ajuste este valor se quiser mais ou menos espaço (padrão é ~6rem) */
        padding-bottom: 2rem !important;
    }

    /* 2. Espaçamento entre as abas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }

    /* 3. Estilo padrão (desativado) de todas as abas */
    .stTabs [data-baseweb="tab"] {
        background-color: #F0F2F6; 
        border-radius: 8px 8px 0px 0px; 
        padding: 10px 20px;
        font-size: 16px;
        font-weight: 600;
        color: #555555;
        box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.05);
    }

    /* 4. Estilo ao passar o mouse (Hover) */
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #E0E2E6;
        color: #ff4b4b; 
    }

    /* 5. Estilo da aba SELECIONADA (Ativa) */
    .stTabs [aria-selected="true"] {
        background-color: #ff4b4b !important; 
        color: white !important; 
        border: none !important;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)


st.title("🚀 Modelo Preditivo de Risco Educacional ")

# Criando as Abas
tab_home, tab_lote, tab_individual, tab_resposta = st.tabs([
    "🏠 Página Inicial", 
    "📊 Análise em Lote", 
    "📝 Análise por Aluno",
    "🎈 Respostas Datathon"
])

# --- ABA: PÁGINA INICIAL ---
with tab_home:
    st.markdown("""
                ## Projeto Datathon (FIAP): Passos Mágicos

                Com base no histórico de desenvolvimento educacional da **Associação Passos Mágicos** dos anos de 2022, 2023 e 2024, conduzimos uma profunda análise de dados para compreender a evolução dos alunos, além de compreender o passado e o presente para criar uma análise preditiva em Machine Learning. 
                O objetivo central desta solução é identificar padrões nos indicadores que permitem alertar sobre alunos em risco antes que ocorra uma queda no desempenho ou o aumento da defasagem. 
                
                O modelo calcula e demonstra a probabilidade de alunos entrarem em risco de defasagem acadêmica, o mesmo foi integrado a página que está visualizando (Streamlit).                 
                Essa interface intuitiva disponibiliza o modelo treinado diretamente para as equipes da Passos Mágicos, permitindo intervenções pedagógicas e psicológicas com antecedencias e direcionadas, garantindo que nenhum aluno fique para trás.
                           
                ### O que você encontrará aqui?                
                - 📊 Análise dos alunos em lote (excel);
                - 📝 Análise do alunos Individualmente;
                - 🎈 Respostas Perguntas Datathon; 
                - ℹ️ Informações do repositório principal (https://github.com/vbomura/tc5);
                                                
                ### 👨‍💻 Autores
                - Bryan (https://github.com/BryanTieteTanoue)
                - Gustavo (https://github.com/Nadaguty)
                - Luiz (https://github.com/LuisFernandoSantana)
                - Pedro (https://github.com/PedroBaradel)
                - Vitor (https://github.com/vbomura)                
                """)

    st.info("Navegue pelas abas acima para maiores informações.")

with tab_resposta:
    #drive publico com o arquivo: https://drive.google.com/drive/folders/15OClrgIKiZ2oenKGhXZyN3K2V8Fwvib8?hl=pt-br
    components.iframe("https://docs.google.com/presentation/d/e/2PACX-1vQPfRKC71lzFbLlDdOkGSmPrFFIyHuauwmpm88f_K01yq0-uObYvNn_7dmbe25E3A/pubembed?start=false&loop=false&delayms=3000", height=560)

# --- ABA: PREDIÇÃO EM LOTE ---
with tab_lote:
    st.header("📊 Análise em Lote")
    
    # Criando o link formatado para download do modelo:
    template = gerar_template_excel()
    link_html = criar_link_download(template, "modelo_passos_magicos.xlsx", "Clique aqui para baixar o modelo")    
    st.markdown(f"Suba o arquivo preenchido ou baixe o arquivo modelo e preencha as linhas com as informações dos alunos utilizamos as colunas de IDA, IPV, Defasagem e Fase para realizar a predição ({link_html}).", unsafe_allow_html=True)

    #Upload do aruqivo
    arquivo = st.file_uploader("", type=["xlsx", "csv"], key="uploader_lote")
    
    if arquivo:
        df_input = pd.read_csv(arquivo) if arquivo.name.endswith('.csv') else pd.read_excel(arquivo)
        if st.button("Analisar Alunos"):
            colunas_faltantes = set(FEATURES_DO_MODELO) - set(df_input.columns)
            if colunas_faltantes:
                st.error(f"O arquivo enviado está faltando as seguintes colunas obrigatórias: **{', '.join(colunas_faltantes)}**")
                link_html = criar_link_download(template, "modelo_passos_magicos.xlsx", "Clique aqui para baixar o modelo")    
                st.write(f"Por favor, carregue um arquivo válido! ({link_html}).", unsafe_allow_html=True)                
            else:
                try:
                    res = realizar_predicao(df_input,1)
                    st.success("Análise concluída!")
                    #Opção de download da analise
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        res.to_excel(writer, index=False)
                    
                    st.download_button(
                        label="📥 Baixar Resultado Completo (.xlsx)",
                        data=buffer.getvalue(),
                        file_name="resultado_defasagem_passos_magicos.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                    st.dataframe(res[FEATURES_DO_MODELO + ['predicao_defasagem_aluno']])                
                except Exception as e:
                    st.error(f"Erro ao processar arquivo: {e}")

# --- ABA: PREDIÇÃO INDIVIDUAL ---
with tab_individual:
    st.header("📝 Predição por Aluno")
    
    with st.form("form_aluno"):
        ra = st.text_input("RA do Aluno", placeholder="Ex: RA-987654")
        ida = st.number_input("IDA (Aprendizado)", min_value=0.0, max_value=10.0, value=0.0, step=0.1)
        ipv = st.number_input("IPV (Ponto de Virada)", min_value=0.0, max_value=10.0, value=0.0, step=0.1)
        defasagem = st.number_input("Defasagem", min_value=-5.0, max_value=5.0, value=0.0, step=1.0)
        fase = st.selectbox("Fase Atual", ["ALFA"] + [f"FASE {i}" for i in range(1, 9)], key="fase_ind")
            
        enviado = st.form_submit_button("Verificar Aluno")
        
        if enviado:
            dados = pd.DataFrame([{
                'ra': ra, 'ida': ida, 'ipv': ipv, 'defasagem': defasagem,
                'fase': fase
            }])

            resultado = realizar_predicao(dados,0)
            pred = resultado['predicao_defasagem_aluno'].values[0]
            
            st.subheader(f"Resultado para o RA: {ra}")
            if pred != 0:
                st.warning(f"Retorno da Predição: {pred}")
                st.error("🚨 Probabilidade de Defasagem detectada.")
            else:
                st.info(f"Retorno da Predição: {pred}")
                st.success("✅ O aluno apresenta desempenho condizente com sua fase.")