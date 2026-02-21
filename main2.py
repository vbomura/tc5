# Verificar arquivo -> requirements.txt
import streamlit as st
import pandas as pd
import io
import numpy as np
import joblib
import os
from tools.utils import FeatureSelector, substituir_valores_coluna, remover_texto_parenteses, normalizar_fase
import base64

# --- Configurações Globais ---
FEATURES_DO_MODELO = [
    'ra', 'inde', 'ieg', 'iaa', 'ips', 'ida', 'ian', 
    'idade', 'ipv', 'defasagem', 'fase', 'fase_ideal'
]

FEATURES_PARA_PREDICAO = [f for f in FEATURES_DO_MODELO if f != 'ra']

@st.cache_resource
def carregar_modelo():
    caminho = os.path.join(os.path.dirname(__file__), 'tools/Defasagem.joblib')
    return joblib.load(caminho)

def gerar_template_excel():
    output = io.BytesIO()
    df_template = pd.DataFrame(columns=FEATURES_DO_MODELO)
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_template.to_excel(writer, index=False)
    return output.getvalue()

def realizar_predicao(df):
    df = df.copy()
    modelo = carregar_modelo()
    
    df["fase"] = df["fase"].map(normalizar_fase)   
    df["fase_ideal"] = df["fase_ideal"].map(remover_texto_parenteses)
    
    mapeamento_defasagem = {
        'ALFA': 0, 'FASE 1': 1, 'FASE 2': 2, 'FASE 3': 3,
        'FASE 4': 4, 'FASE 5': 5, 'FASE 6': 6, 'FASE 7': 7, 'FASE 8': 8 
    }
    df = substituir_valores_coluna(df=df, coluna='fase', mapeamento=mapeamento_defasagem)

    df[FEATURES_PARA_PREDICAO] = df[FEATURES_PARA_PREDICAO].replace(r'^\s*$', np.nan, regex=True)
    df = df.dropna(subset=FEATURES_PARA_PREDICAO)

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

st.title("🚀 Projeto Datathon: Passos Mágicos - Defasagem Alunos")

# Criando as Abas
tab_home, tab_lote, tab_individual = st.tabs([
    "🏠 Página Inicial", 
    #"📄 Download do Modelo", 
    "📊 Análise em Lote", 
    "📝 Análise por Aluno"
])

# --- ABA: PÁGINA INICIAL ---
with tab_home:
    st.markdown("""
                ## Bem-vindo ao Sistema de Identificação de Defasagem Acadêmica

                Este sistema foi desenvolvido para realizar previsões relacionadas a provaveis defasagem nos alunos da Passos Mágisos. 
                
                Utilizamos as informações fornecidas no Datathon da **Fase 5 - Data Analytics (FIAP - 9DTAT)**.

                ### O que você encontrará aqui?                
                - 📊 Análise dos alunos em lote (excel);
                - 📝 Análise do alunos Individualmente;
                - ℹ️ Informações sobre o modelo de Machine Learning; **----->>>>>>>>????????????**
                - ℹ️ Informações sobre analise e estudos realizados; **----->>>>>>>>????????????**
                - ℹ️ Informações do repositório principal (https://github.com/vbomura/tc5);

                O objetivo é fornecer para a empresa **Passos Mágicos** uma forma de conseguir identificar alunos em risco antes de queda no desempenho ou aumento da defasagem, por meio de uma predição criada.
                                                
                ### 👨‍💻 Autores
                - Bryan (https://github.com/BryanTieteTanoue)
                - Gustavo (https://github.com/Nadaguty)
                - Luiz (https://github.com/LFAJOGA5)
                - Pedro (https://github.com/PedroBaradel)
                - Vitor (https://github.com/vbomura)                
                """)

    st.info("Navegue pelas abas acima para maiores informações.")

# # --- ABA: DOWNLOAD ---
# with tab_download:
#     st.header("📄 Download do Template")
#     st.write("Baixe o arquivo e preencha o RA e os indicadores de cada aluno.")
#     template = gerar_template_excel()
#     st.download_button("📥 Baixar Modelo Excel (.xlsx)", data=template, file_name="template_ra_passos_magicos.xlsx")

# --- ABA: PREDIÇÃO EM LOTE ---
with tab_lote:
    st.header("📊 Análise em Lote")
    
    # Criando o link formatado para download do modelo:
    template = gerar_template_excel()
    link_html = criar_link_download(template, "modelo_passos_magicos.xlsx", "Clique aqui para baixar o modelo")    
    st.markdown(f"Suba o arquivo preenchido ou baixe o arquivo modelo e preencha as linhas com as informações dos alunos ({link_html}).", unsafe_allow_html=True)

    #Upload do aruqivo
    arquivo = st.file_uploader("", type=["xlsx", "csv"], key="uploader_lote")
    
    if arquivo:
        df_input = pd.read_csv(arquivo) if arquivo.name.endswith('.csv') else pd.read_excel(arquivo)
        if st.button("Analisar Alunos"):
            colunas_faltantes = set(FEATURES_DO_MODELO) - set(df_input.columns)
            if colunas_faltantes:
                st.error(f"O arquivo enviado está faltando as seguintes colunas obrigatórias: **{', '.join(colunas_faltantes)}**")
                # st.write(f"Por favor, carregue um arquivo válido!")
                link_html = criar_link_download(template, "modelo_passos_magicos.xlsx", "Clique aqui para baixar o modelo")    
                st.write(f"Por favor, carregue um arquivo válido! ({link_html}).", unsafe_allow_html=True)                
            else:
                try:
                    res = realizar_predicao(df_input)
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

                    st.dataframe(res)                
                except Exception as e:
                    st.error(f"Erro ao processar arquivo: {e}")

# --- ABA: PREDIÇÃO INDIVIDUAL ---
with tab_individual:
    st.header("📝 Predição por Aluno")
    
    with st.form("form_aluno"):
        ra = st.text_input("RA do Aluno", placeholder="Ex: PM-2026-001")
        col1, col2 = st.columns(2)
        with col1:
            inde = st.number_input("INDE", min_value=0.0, max_value=10.0, value=0.0, step=0.1)
            ieg = st.number_input("IEG (Engajamento)", min_value=0.0, max_value=10.0, value=0.0, step=0.1)
            iaa = st.number_input("IAA (Autoavaliação)", min_value=0.0, max_value=10.0, value=0.0, step=0.1)
            ips = st.number_input("IPS (Social)", min_value=0.0, max_value=10.0, value=0.0, step=0.1)
            ida = st.number_input("IDA (Aprendizado)", min_value=0.0, max_value=10.0, value=0.0, step=0.1)

        with col2:
            ian = st.number_input("IAN (Nível)", min_value=0.0, max_value=10.0, value=0.0, step=0.1)
            idade = st.number_input("Idade", min_value=0, max_value=25, value=10, step=1)
            ipv = st.number_input("IPV (Ponto de Virada)", min_value=0.0, max_value=10.0, value=0.0, step=0.1)
            defasagem = st.number_input("Defasagem", min_value=-5.0, max_value=5.0, value=0.0, step=1.0)
            fase = st.selectbox("Fase Atual", ["ALFA"] + [f"FASE {i}" for i in range(1, 9)], key="fase_ind")
            fase_ideal = st.selectbox("Fase Ideal", ["ALFA"] + [f"FASE {i}" for i in range(1, 9)], key="fase_ideal_ind")
            
        enviado = st.form_submit_button("Verificar Aluno")
        
        if enviado:
            dados = pd.DataFrame([{
                'ra': ra, 'inde': inde, 'ieg': ieg, 'iaa': iaa, 'ips': ips, 'ida': ida,
                'ian': ian, 'idade': idade, 'ipv': ipv, 'defasagem': defasagem,
                'fase': fase, 'fase_ideal': fase_ideal
            }])

            resultado = realizar_predicao(dados)
            pred = resultado['predicao_defasagem_aluno'].values[0]
            
            st.subheader(f"Resultado para o RA: {ra}")
            if pred != 0:
                st.warning(f"Retorno da Predição: {pred}")
                st.error("🚨 Probabilidade de Defasagem detectada.")
            else:
                st.info(f"Retorno da Predição: {pred}")
                st.success("✅ O aluno apresenta desempenho condizente com sua fase.")