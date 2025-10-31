import re
import os
import statistics
from TrieCompacta import TrieCompacta
from Indexador import Indexador


class Recuperador():

    def __init__(self, recuperador_de_indice):
        self.recuperador = recuperador_de_indice


    # Processa uma consulta booleana simples com AND e OR
    def _processar_consulta(self, consulta):
        # Separa termos e operadores
        tokens = re.findall(r'\w+|AND|OR|\(|\)', consulta)
        return tokens


    # Avalia uma expressão booleana
    def _avaliar_expressao(self, tokens):
        termos_puros = [t.lower() for t in tokens if t.isalpha()
                        and t not in ("AND", "OR")]
        resultados = {}

        for termo in termos_puros:
            resultados[termo] = set(self.recuperador.trie.buscar(termo))

        # Monta expressão substituindo cada termo pelo conjunto de docs
        expr = []
        for t in tokens:
            if t == "AND":
                expr.append("&")
            elif t == "OR":
                expr.append("|")
            elif t.isalpha():
                # Adiciona 'resultados' para o escopo do eval
                expr.append(f"resultados.get('{t.lower()}', set())")
            else:
                if t in ("(", ")"):
                    expr.append(t)

        try:
            # Avalia a expressão booleana usando python (por exemplo: (A & B) | C)
            docs = eval(" ".join(expr), {"resultados": resultados})
        except Exception:
            docs = set()  # Retorna vazio em caso de consulta mal formada

        return docs, termos_puros


    # Calcula a relevância dos documentos (média dos z-scores dos termos da consulta)
    def _calcular_relevancia_docs(self, docs, palavras):
        relevancias = {}
        if not palavras:
            return []

        for termo in palavras:
            # Usa o recuperador
            freqs = self.recuperador.freqs_das_palavras.get(termo, {})
            if not freqs:
                continue

            valores = list(freqs.values())
            # Usa o recuperador
            num_docs = self.recuperador.total_docs

            # Soma das frequências
            soma_freqs = sum(valores)

            # Média considerando zeros (documentos sem o termo)
            media = soma_freqs / num_docs

            # Desvio padrão, também considerando zeros
            valores_com_zeros = valores + [0] * (num_docs - len(valores))
            desvio = statistics.pstdev(valores_com_zeros) or 1

            for doc_id in docs:
                freq = freqs.get(doc_id, 0)
                z = (freq - media) / desvio
                relevancias[doc_id] = relevancias.get(doc_id, 0) + z

        # Média dos z-scores por documento
        for doc in relevancias:
            relevancias[doc] /= len(palavras)
        return sorted(relevancias.items(), key=lambda x: x[1], reverse=True)


    # Gera um pequeno snippet com destaque
    def _gerar_snippet(self, caminho_arquivo, palavra):
        try:
            with open(caminho_arquivo, "r", encoding="utf8") as arquivo:
                texto = arquivo.read()

            # Usa \b (word-boundary) para evitar substrings e re.IGNORECASE para case-insensitive
            padrao = re.compile(r'\b' + re.escape(palavra) + r'\b', flags=re.IGNORECASE)
            match = padrao.search(texto)

            if not match:
                return texto[:160].replace("\n", " ") + "..."

            idx = match.start()
            termo_original = match.group(0)

            ini = max(0, idx - 80)
            fim = min(len(texto), idx + len(termo_original) + 80)

            snippet = (texto[ini:idx] +
                    "<strong>" + termo_original + "</strong>" +
                    texto[idx + len(termo_original): fim])

            prefixo = "..." if ini > 0 else ""
            sufixo = "..." if fim < len(texto) else ""

            return prefixo + snippet.replace("\n", " ") + sufixo

        except Exception:
            return "Erro ao gerar snippet."


    def _termo_mais_frequente_no_doc(self, doc_id, termos):
        melhor_termo = None
        melhor_freq = -1
        for termo in termos:
            # Usa o recuperador
            freqs = self.recuperador.freqs_das_palavras.get(termo, {})
            f = freqs.get(doc_id, 0)
            if f > melhor_freq:
                melhor_freq = f
                melhor_termo = termo
        return melhor_termo or (termos[0] if termos else "")


    # Função principal de busca
    def buscar(self, consulta):
        tokens = self._processar_consulta(consulta)
        docs, termos = self._avaliar_expressao(tokens)
        relevancias = self._calcular_relevancia_docs(docs, termos)

        resultados = []
        for doc_id, score in relevancias:
            # Usa o recuperador
            caminho = self.recuperador.id_doc_mapa.get(doc_id, "")
            if not caminho:
                continue

            caminho_limpo = "/".join(caminho.split(os.path.sep)[-2:])

            termo_para_snippet = self._termo_mais_frequente_no_doc(
                doc_id, termos)

            snippet = self._gerar_snippet(caminho, termo_para_snippet)

            resultados.append({
                "id_doc": doc_id,
                "caminho_exibicao": caminho_limpo,
                "snippet": snippet,
                "relevancia": score
            })
        return resultados