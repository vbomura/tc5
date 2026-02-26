# 📊 Tech Challenge – Fase 5 (Datathon)

## Identificação de Risco sobre desempenho de alunos

Este projeto foi desenvolvido como parte do **Datathon da FIAP – Fase 5**, com foco em criar uma aplicação para predição para identificar alunos em risco antes de queda no desempenho ou aumento da defasagem.

Utilizamos o **Machine Learning**, para criar as previsões além de analisarmos e respondermos algumas perguntas. A interface para a análise dos alunos está interativa no **Streamlit**.

A aplicação está publicada e acessível pelo link:

👉 **[https://datathon-n2psikjxmocweyspvzihfb.streamlit.app/]**


---

# 🚀 Objetivo do Projeto

O objetivo principal deste trabalho é:

- Realizar análises gráficas e estatísticas sobre fatores relacionados aos indices utilizados pela Associação Passos Mágicos na avaliação dos alunos
- Construir modelos de **Machine Learning** que podem identificar padrões
- Criar uma interface interativa em **Streamlit** para predição sobre desempenho dos alunos

O projeto engloba desde a preparação dos dados até a disponibilização online da solução.

---

# 🖥️ Funcionalidades da Aplicação

A interface web possui:

### ✔ **Análise de Alunos**
- Analise individual ou em lote (Excel)

### ✔ **Sobre o Projeto**
- Informações gerais  
- Uma apresentação respondendo perguntas para entendimento das características do projeto

---

# 🧠 Machine Learning

O projeto inclui:

- Pré-processamento de dados;
- Tratamento de variáveis, transformações e normalizações;
- Aplicação de modelos;

### Modelos testados:
- Regressão Logística
- Random Forest  

### Métricas avaliadas:
- Acurácia  
- Precision  
- Recall  
- Matriz de confusão  


### Modelo escolhido foi: **Random Forest**  
---

# 📁 Estrutura do Projeto

```bash
tc5/
│
│── Apresentacao/            		    # Pasta com a apresentação em PPT do trabalho
│   └──Apresentação_Datathon.pptx   # Arqvuivo com as respostas das questões do Datathon
│
│── Base_Passos_Magicos/            # Dados disponibilizados pela Passos Mágicos
│   └── ......                      # Dados disponibilizados pela Passos Mágicos
│
│── Codigos/                        # Análise exploratória, tratamento dos dados, comparações entre modelos de ML, etc
│   └── Algoritmo V2 - NOVO.ipynb   # Análise e tratamento da base de dados utilizada
│   └── previsao_v2.ipynb           # Análise e estruturação do Machine Learning
│   └── base_anos_limpo.xlsx        # Base tratada e salva para as análises para respostas do desafio Datathon
│
│── tools/                          # Arquivos para Pipeline e modelo salvo
│   ├── DefasagemNew.joblib         # Modelo de ML utilizado no Streamlit
│   └── utils.py                    # Funções utilizadas no Streamlit
│
│── Respostas_Pesquisa/             # Análises e identificação das respostas do desafio do Datathon
│   ├── Questoes_1_2.ipynb          # Tratamentos e análises para responder as questões 1 e 2 
│   ├── Questoes_3_4.ipynb          # Tratamentos e análises para responder as questões 3 e 4
│   ├── Questoes_5_6.ipynb          # Tratamentos e análises para responder as questões 5 e 6
│   ├── Questoes_7_10.ipynb         # Tratamentos e análises para responder as questões 7, 8 e 10
│
│── main.py                         # Arquivo principal da aplicação Streamlit/Boas Vindas
│── requirements.txt                # Dependências do projeto
│── README.md                       # Documentação do repositório
```

# 📦 Requisitos

- As principais dependências para execução do projeto está no arquivo requirements.txt.


# 👨‍💻 Autores
- Bryan (https://github.com/BryanTieteTanoue)
- Gustavo (https://github.com/Nadaguty)
- Luiz (https://github.com/LuisFernandoSantana)
- Pedro (https://github.com/PedroBaradel)
- Vitor (https://github.com/vbomura)

