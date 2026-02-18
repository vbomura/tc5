import streamlit as st
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
import joblib
from joblib import load
#from tools.utils import RenomearColunasTransf, MultiLabelEncoder, YesNoToBinaryTransformer, MinMax, OrdinalEncodingTransformer, DummyEncoderTransformer, ColumnsToIntTransformer


def app():
    #importando base (alterar para caminho do GIT)
    url = "https://raw.githubusercontent.com/vbomura/tc5/main/Codigos/base_anos_limpo.xlsx"
    base = pd.read_excel(url)

    st.set_page_config(page_title="Defasagem Passos Mágicos")
    st.title("Defasagem Passos Mágicos")

    #st.write('# Pesquisa sobre obesidade')
    st.warning("Aviso este é um algoritimo de predição, não substitui uma avaliação de um profissional.")

    #Age
    #input_idade = float(st.slider('Selecione sua idade:', 15, 100))
    input_idade = st.number_input(
            "Insira sua Idade (anos)",
            min_value=15,      # idade minima
            max_value=100,     # idade maxima
            value=25,         # Valor padrão
            step=1            # Passo de 1
        )

    #Height
    input_altura = st.number_input(
        "Insira sua altura (em cm)",
        min_value=50,      # Altura mínima
        max_value=300,     # Altura máxima
        value=170,         # Valor padrão
        step=1,            # Passo de 1 cm
        format="%d"        # Garante que o valor seja um inteiro
    )

    #Weight
    input_peso = st.number_input(
        "Insira seu peso (em kg)",
        min_value=10,      # Peso mínima
        max_value=300,     # Peso máxima
        value=80,         # Valor padrão
        step=1            # Passo de 1 kg
    )

    #family_history
    input_historico = st.radio('Tem histórico familiar de excesso de peso?',["***Sim***","***Não***"])

    #CAEC
    input_lanches = st.selectbox('Qual a frequencia de consumo de lanches entre as refeições?', ("Selecione...", "Não consome", "Às vezes", "Frequentemente", "Sempre"))

    #FAVC
    input_alimento_calorico = st.radio('Consumo frequente de alimentos muito calóricos?',["***Sim***","***Não***"])

    # ===========================================================
    # 🔘 Botão e tratamento dos dados
    # ===========================================================

    # Separando os dados em treino e teste
    def data_split(df):
        treino_df, teste_df = train_test_split(df, test_size=0.2, random_state=42)
        return treino_df.reset_index(drop=True), teste_df.reset_index(drop=True)    


    if st.button("Fazer Predição"):

        campos_invalidos = []

        # Verificar se todos foram preenchidos corretamente
        if input_lanches == "Selecione...":
            campos_invalidos.append("Lanches")

        # Se houver campos não preenchidos
        if campos_invalidos:
            st.error(f"⚠️ Por favor, preencha todos os campos obrigatórios: {', '.join(campos_invalidos)}")
        else:
            # Dicionários de conversão da tela de streamlit para poder adicionar o valor no dataframe
            map_binario = {"***Sim***": "yes", "***Não***": "no"}
            map_genero = {"***Masculino***": "Male", "***Feminino***": "Female"}
            map_vegetais = {"Raramente": 1, "Às vezes": 2, "Sempre": 3}
            map_lanches = {"Não consome": "no", "Às vezes": "Sometimes", "Frequentemente": "Frequently", "Sempre": "Always"}
            map_agua = {"***< 1 L/dia***": 1, "***1–2 L/dia***": 2, "***2 L/dia***": 3}
            map_atividade = {"***Nenhuma***": 0, "***~1–2×/sem***": 1, "***~3–4×/sem***": 2, "***5×/sem ou mais***": 3}
            map_dispositivo = {"***~0–2 h/dia***": 0, "***~3–5 h/dia***": 1, "***> 5 h/dia***": 2}
            map_alcoolica = {"Não bebe": "no", "Às vezes": "Sometimes", "Frequentemente": "Frequently", "Sempre": "Always"}
            map_transporte = {"Carro": "Automobile", "Moto": "Motorbike", "Bicicleta": "Bike", "Transporte Público": "Public_Transportation", "A pé": "Walking"}

            # Conversão dos campos
            historico_num = map_binario[input_historico]
            lanches_num = map_lanches[input_lanches]
            calorico_num = map_binario[input_alimento_calorico]
            # Monta lista final tratada

            #Criando objeto de acordo com a planilha base
            nova_pesquisa = [
                "Male",# sexo_num,
                input_idade,
                input_altura,
                input_peso,
                historico_num,
                calorico_num,
                1,#vegetais_num,
                1,#input_refeicoes,
                lanches_num,
                "no",#fuma_num,
                1,#agua_num,
                "no",#calorias_num,
                0,#atividade_num,
                0,#dispositivo_num,
                "no",#alcoolica_num,
                "Automobile",#transporte_num,
                0 #####TRATAR OBESIDADE#####
            ]
            
            treino_df, teste_df = data_split(base)

            #Criando novo paciente
            paciente_predict_df = pd.DataFrame([nova_pesquisa],columns=teste_df.columns)

            #Concatenando novo paciente ao dataframe dos dados de teste
            teste_novo_paciente  = pd.concat([teste_df,paciente_predict_df],ignore_index=True)

            #Deixando somente dados que são utilizados na predição
            cliente_pred = teste_novo_paciente[['peso','historico_familiar_cod', 'idade', 'calorias_frequente_cod', 'entre_refeicao_ord', 'altura']]


            model = joblib.load('RandomForest.joblib')
            final_pred = model.predict(cliente_pred)

            predicaoGerada=-1
            predicaoGerada = final_pred[-1].astype(int)

            # Mostra resultado

            # Tratamento das mensagens
            if predicaoGerada == 0:
                st.warning("""Risco alto de estar abaixo do peso. É importante avaliar se existe alguma causa nutricional ou metabólica. \
                \n\n Busque auxílio nutricional para alcançar um peso saudável.""")

            elif predicaoGerada == 1:
                st.success("""Parabéns! Você aparenta estar dentro do peso considerado saudável. \
                \n\n Continue mantendo bons hábitos alimentares e atividade física! Mas não se esqueça de consultar um médico.""")

            else:
                st.error("Erro na criação da predição para estes valores, por favor realizar uma nova consulta.")
                
