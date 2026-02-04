import streamlit as st
import pandas as pd

url = "https://raw.githubusercontent.com/vbomura/tc5/main/Codigos/base_anos_limpo.xlsx"
base = pd.read_excel(url)

st.set_page_config(page_title="Defasagem Passos Mágicos")
st.title("Defasagem Passos Mágicos")

#st.write('# Pesquisa sobre obesidade')
st.warning("Aviso este é um algoritimo de predição, não substitui uma avaliação de um profissional.")

#features = ['ian', 'ida', 'ieg', 'ipp', 'ipv']

#ian - Média das Notas de Adequaça o do Aluno ao ní vel atua
input_ian = st.number_input(
        "Média das Notas de Adequaça o do Aluno ao ní vel atua",
        min_value=0,      # idade minima
        max_value=100,     # idade maxima
        value=10,         # Valor padrão
        step=1            # Passo de 1
    )

#ida -  Média das Notas do Indicador de Aprendizagem
input_ida = st.number_input(
        "Média das Notas do Indicador de Aprendizagem",
        min_value=0,      # idade minima
        max_value=100,     # idade maxima
        value=10,         # Valor padrão
        step=1            # Passo de 1
    )

#ieg -  Média das Notas do Indicador de Aprendizagem
input_ieg = st.number_input(
        "Média das Notas do Indicador de Aprendizagem",
        min_value=0,      # idade minima
        max_value=100,     # idade maxima
        value=10,         # Valor padrão
        step=1            # Passo de 1
    )


IDA (Indicador de Desempenho Acadêmico)

Fórmula: IDA = (Nota Matemática + Nota Português + Nota Inglês) / 3

Dados necessários:
-	Notas (internas da associação)
