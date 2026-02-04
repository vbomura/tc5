import streamlit as st
import pandas as pd

url = "https://raw.githubusercontent.com/vbomura/tc5/main/Codigos/base_anos_limpo.xlsx"
base = pd.read_excel(url)

st.set_page_config(page_title="Defasagem Passos Mágicos")
st.title("Defasagem Passos Mágicos")

#st.write('# Pesquisa sobre obesidade')
st.warning("Aviso este é um algoritimo de predição, não substitui uma avaliação de um profissional.")

#features = ['idade','ian', 'ida', 'ieg', 'ipv']

FASES = ['ALFA', 'FASE 1', 'FASE 2', 'FASE 3', 'FASE 4','FASE 5', 'FASE 6', 'FASE 7', 'FASE 8', 'FASE 9']

#idade
input_idade = st.number_input(
        "Insira sua Idade (anos)",
        min_value=5,      # idade minima
        max_value=30,     # idade maxima
        value=12,         # Valor padrão
        step=1            # Passo de 1
    )

#Gerar ian
inputs = {}
for label in ["Fase Efetiva", "Fase Ideal"]:
    inputs[label] = st.selectbox(label, FASES)

fase_efetiva = inputs["Fase Efetiva"]
fase_ideal = inputs["Fase Ideal"]


#Gerar ida
input_Matematica = st.number_input(
        "Nota Matematica",
        min_value=0.0,
        max_value=10.0,
        value=5.0,
        step=0.1
    )
input_Portugues = st.number_input(
        "Nota Portugues",
        min_value=0.0,
        max_value=10.0,
        value=5.0,
        step=0.1
    )
input_Ingles = st.number_input(
        "Nota Ingles",
        min_value=0.0,
        max_value=10.0,
        value=5.0,
        step=0.1
    )

#ieg -  Média das Notas do Indicador de Aprendizagem
input_ieg = st.number_input(
        "Média das Notas do Indicador de Aprendizagem",
        min_value=0.0,
        max_value=10.0,
        value=5.0,
        step=0.1
    )

#ipv -  Média das Notas do Indicador de Aprendizagem
input_ieg = st.number_input(
        "Observaço es dos Mestres Sobre o Aluno referente ao “Indicador de Ponto de Virada”",
        min_value=0.0,
        max_value=10.0,
        value=5.0,
        step=0.1
    )