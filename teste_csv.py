import streamlit as st
import os
import re
import csv

# --- Suas funções existentes (inalteradas) ---

def carregar_dicionario_csv_expandido(nome_arquivo):
    termos = []
    mapa_hierarquia = {}
    try:
        with open(nome_arquivo, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                hierarquia_completa = []
                # Assumindo que o seu CSV tenha colunas termo1, termo2, etc.
                for i in range(3, 7): # Ajuste este range conforme o número de colunas
                    coluna = f'termo{i}'
                    if coluna in row and row[coluna]:
                        hierarquia_completa.append(row[coluna].strip())
                    
                if not hierarquia_completa:
                    continue
                line = " > ".join(hierarquia_completa)
                partes = [p.strip() for p in line.split('>') if p.strip()]
                if not partes:
                    continue
                termo_especifico = partes[-1]
                if termo_especifico:
                    termo_especifico = termo_especifico.replace('\t', '')
                    termos.append(termo_especifico)
                if len(partes) > 1:
                    termo_pai = partes[-2].replace('\t', '')
                    if termo_pai not in mapa_hierarquia:
                        mapa_hierarquia[termo_pai] = []
                    mapa_hierarquia[termo_pai].append(termo_especifico)
    except FileNotFoundError:
        st.error(f"Erro: O arquivo '{nome_arquivo}' não foi encontrado.")
        return [], {}
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar o dicionário: {e}")
        return [], {}
    return termos, mapa_hierarquia

def aplicar_logica_hierarquia(termos_sugeridos, mapa_hierarquia):
    termos_finais = set(termos_sugeridos)
    mapa_inverso_hierarquia = {}
    for pai, filhos in mapa_hierarquia.items():
        for filho in filhos:
            mapa_inverso_hierarquia[filho] = pai
    termos_a_remover = set()
    for termo in termos_sugeridos:
        if termo in mapa_inverso_hierarquia:
            termo_pai = mapa_inverso_hierarquia[termo]
            if termo_pai in termos_finais:
                termos_a_remover.add(termo_pai)
    termos_finais = termos_finais - termos_a_remover
    return list(termos_finais)

def gerar_termos_llm_mock(texto_original, termos_dicionario, num_termos):
    st.info(f"Simulando sugestão de termos para o texto: '{texto_original[:40]}...'")
    if "hospitalização" in texto_original.lower():
        return ["Saúde Pública", "Administração em Saúde", "Hospitalização"]
    if "ensino superior" in texto_original.lower():
        return ["Ensino Superior"]
    return ["Política Pública"]

# --- Bloco de código para o Streamlit ---
st.title("Teste de Carregamento de Dicionário")

arquivo_csv = "saude_dicionario.csv"
termo_dicionario_csv, mapa_hierarquia_csv = carregar_dicionario_csv_expandido(arquivo_csv)

if not termo_dicionario_csv:
    st.warning("Teste não pode continuar: Dicionário não foi carregado.")
else:
    st.success(f"Dicionário CSV carregado com {len(termo_dicionario_csv)} termos.")
    
    st.subheader("Termos carregados do CSV:")
    st.write(termo_dicionario_csv)
    
    st.subheader("Mapa de hierarquia criado:")
    st.write(mapa_hierarquia_csv)

    # Simulação do fluxo de trabalho
    texto_proposicao = st.text_area("Digite um texto para testar a sugestão de termos:", "A proposição visa tratar de temas de hospitalização.")
    num_termos = st.slider("Número de termos a sugerir:", 1, 10, 5)

    if st.button("Gerar Termos"):
        with st.spinner('Gerando...'):
            termos_sugeridos_brutos = gerar_termos_llm_mock(texto_proposicao, termo_dicionario_csv, num_termos)
            
            st.write("---")
            st.subheader("Resultado do Teste")
            st.write(f"Termos sugeridos pela IA (brutos): **{termos_sugeridos_brutos}**")
            
            termos_finais = aplicar_logica_hierarquia(termos_sugeridos_brutos, mapa_hierarquia_csv)
            st.write(f"Termos finais após a lógica de hierarquia: **{termos_finais}**")
