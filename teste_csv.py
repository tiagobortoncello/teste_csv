import os
import re
import csv

# Função para carregar o dicionário de um arquivo CSV com hierarquia em colunas
def carregar_dicionario_csv_expandido(nome_arquivo):
    termos = []
    mapa_hierarquia = {}
    try:
        with open(nome_arquivo, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                hierarquia_completa = []
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
        print(f"Erro: O arquivo '{nome_arquivo}' não foi encontrado.")
        return [], {}
    except Exception as e:
        print(f"Ocorreu um erro ao carregar o dicionário: {e}")
        return [], {}
    return termos, mapa_hierarquia

# Função para aplicar a lógica de hierarquia nos termos sugeridos
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

# Mock da função que gera termos, para simular a resposta da IA
def gerar_termos_llm_mock(texto_original, termos_dicionario, num_termos):
    print(f"Simulando sugestão de termos para o texto: '{texto_original[:40]}...'")
    # Simula um cenário onde termos genéricos e específicos são sugeridos
    if "hospitalização" in texto_original.lower():
        return ["Saúde Pública", "Administração em Saúde", "Hospitalização"]
    # Simula um cenário onde apenas termos específicos são sugeridos
    if "ensino superior" in texto_original.lower():
        return ["Ensino Superior"]
    return ["Política Pública"]

# --- Bloco de teste principal ---
if __name__ == "__main__":
    
    # 1. Carrega o dicionário
    arquivo_csv = "saude_dicionario.csv"
    termo_dicionario_csv, mapa_hierarquia_csv = carregar_dicionario_csv_expandido(arquivo_csv)
    
    if not termo_dicionario_csv:
        print("Teste não pode continuar: Dicionário não foi carregado.")
    else:
        print(f"Dicionário CSV carregado com {len(termo_dicionario_csv)} termos.")
        
        # 2. Simula o texto de entrada do usuário
        texto_proposicao_1 = "A proposição visa tratar de temas de hospitalização."
        
        # 3. Gera os termos (simulando a IA)
        termos_sugeridos_brutos_1 = gerar_termos_llm_mock(texto_proposicao_1, termo_dicionario_csv, 5)
        print(f"Termos sugeridos pela IA (brutos): {termos_sugeridos_brutos_1}")
        
        # 4. Aplica a lógica de hierarquia
        termos_finais_1 = aplicar_logica_hierarquia(termos_sugeridos_brutos_1, mapa_hierarquia_csv)
        print(f"Termos finais após a hierarquia: {termos_finais_1}\n")
        
        # --- Segundo cenário de teste ---
        texto_proposicao_2 = "A presente lei aborda o ensino superior."
        termos_sugeridos_brutos_2 = gerar_termos_llm_mock(texto_proposicao_2, termo_dicionario_csv, 5)
        print(f"Termos sugeridos pela IA (brutos): {termos_sugeridos_brutos_2}")
        
        termos_finais_2 = aplicar_logica_hierarquia(termos_sugeridos_brutos_2, mapa_hierarquia_csv)
        print(f"Termos finais após a hierarquia: {termos_finais_2}\n")
