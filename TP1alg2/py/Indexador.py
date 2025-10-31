import os
import re
from TrieCompacta import TrieCompacta


class Indexador():

    def __init__(self, caminho_corpus):
        self.caminho_corpus = caminho_corpus
        self.trie = TrieCompacta()
        self.freqs_das_palavras = {} # palavra -> {id_doc: freq}
        self.id_doc_mapa = {} # id_doc -> caminho do arquivo
        self.total_docs = 0

    def _processar_arquivo(self, caminho_arquivo, id_doc):
        try:
            with open(caminho_arquivo, 'r', encoding="utf-8") as arquivo:
                texto = arquivo.read().lower()
            palavras = re.findall(r'\b[a-záéíóúãõç]+\b', texto)
            for palavra in palavras:
                self.trie.inserir(palavra, id_doc)
                self.freqs_das_palavras.setdefault(palavra, {})
                self.freqs_das_palavras[palavra][id_doc] = self.freqs_das_palavras[palavra].get(
                    id_doc, 0) + 1
        except Exception as e:
            print(f"Erro ao processar {caminho_arquivo}: {e}")

    # Salva o índice em um arquivo .txt próprio
    def salvar_indice(self, caminho_arquivo_indice):
        print(f"Salvando índice em {caminho_arquivo_indice}...")
        with open(caminho_arquivo_indice, 'w', encoding="utf8") as indice:
            indice.write(f"DOCMAP_START\n")
            for id_doc, caminho in self.id_doc_mapa.items():
                indice.write(f"doc:{id_doc}:{caminho}\n")
            indice.write(f"DOCMAP_END\n")
            for palavra, docs in self.freqs_das_palavras.items():
                linha = palavra + ":" + \
                    ";".join(f"{id_doc},{freq}" for id_doc,
                             freq in docs.items())
                indice.write(linha + "\n")
        print("Índice salvo.")

    # Carrega índice a partir do arquivo salvo
    def carregar_indice(self, caminho_arquivo_indice):
        print(f"Carregando índice de {caminho_arquivo_indice}...")
        with open(caminho_arquivo_indice, 'r', encoding="utf8") as indice:
            linha = indice.readline()
            while True:
                linha = indice.readline().strip()
                if linha == "DOCMAP_END":
                    break
                if linha.startswith("doc:"):
                    _, id_doc, caminho = linha.split(":", 2)
                    self.id_doc_mapa[int(id_doc)] = caminho
            self.total_docs = len(self.id_doc_mapa)
            for linha in indice:
                if ":" not in linha:
                    continue
                palavra, lista = linha.strip().split(":", 1)
                self.freqs_das_palavras[palavra] = {}
                pares = lista.split(";")
                for p in pares:
                    if "," in p:
                        id_doc, freq = p.split(",")
                        id_doc_int = int(id_doc)
                        self.freqs_das_palavras[palavra][id_doc_int] = int(
                            freq)
                        self.trie.inserir(palavra, id_doc_int)
        print(f"Índice carregado. {self.total_docs} documentos.")

    # Faz a indexação, lendo todos os arquivos da pasta bbc e inserindo as palavras na Trie
    def criar_indice(self):
        print("Criando índice do zero...")
        contador = 0
        for categoria in os.listdir(self.caminho_corpus):
            pasta = os.path.join(self.caminho_corpus, categoria)
            if not os.path.isdir(pasta):
                continue
            for arquivo in os.listdir(pasta):
                if arquivo.endswith(".txt"):
                    contador += 1
                    caminho_arquivo = os.path.join(pasta, arquivo)
                    self.id_doc_mapa[contador] = caminho_arquivo
                    self._processar_arquivo(caminho_arquivo, contador)

        self.total_docs = contador
        print(f"Indexação completa. {self.total_docs} documentos processados.")
