class NoTrie():

    def __init__(self, prefixo):
        self.prefixo = prefixo
        self.filhos = []
        self.noticias = set()


class TrieCompacta():

    def __init__(self):
        self.raiz = NoTrie("")

    def _prefixo_comum(self, str1, str2):
        tamanho = min(len(str1), len(str2))
        i = 0
        while i < tamanho and str1[i] == str2[i]:
            i += 1
        return str1[:i]

    def _buscar(self, no, palavra):
        no_atual = no

        for filho in no_atual.filhos:
            prefixo_comum = self._prefixo_comum(palavra, filho.prefixo)

            # A palavra só pode estar neste galho se o prefixo do filho
            # for um prefixo da palavra
            if prefixo_comum == filho.prefixo:
                resto = palavra[len(prefixo_comum):]
                if resto == "":
                    # Achou a palavra exata
                    return filho.noticias
                else:
                    # Continua a busca recursivamente
                    return self._buscar(filho, resto)

        return set()

    def buscar(self, palavra):
        return self._buscar(self.raiz, palavra)

    def _inserir(self, no, palavra, id_noticia):
        no_atual = no

        # Percorre todos os filhos do nó atual
        for filho in no_atual.filhos:
            prefixo_comum = self._prefixo_comum(palavra, filho.prefixo)

            if prefixo_comum:
                # Caso 1: o prefixo do filho é totalmente contido na palavra
                if prefixo_comum == filho.prefixo and len(palavra) > len(filho.prefixo):
                    # continua a inserção no filho
                    resto = palavra[len(prefixo_comum):]
                    self._inserir(filho, resto, id_noticia)
                    return

                # Caso 2: a palavra é prefixo do filho
                elif prefixo_comum == palavra and len(filho.prefixo) > len(palavra):
                    # precisa dividir o filho
                    resto_filho = filho.prefixo[len(prefixo_comum):]
                    novo_filho = NoTrie(resto_filho)
                    novo_filho.filhos = filho.filhos
                    novo_filho.noticias = filho.noticias

                    # o filho original vira nó intermediário
                    filho.prefixo = prefixo_comum
                    filho.filhos = [novo_filho]  # O novo filho é o único filho

                    # A palavra que estamos inserindo termina aqui,
                    # então ELA se torna o nó que guarda as notícias.
                    filho.noticias = {id_noticia}
                    return

                # Caso 3: palavra e prefixo do filho são idênticos
                elif prefixo_comum == palavra == filho.prefixo:
                    filho.noticias.add(id_noticia)
                    return

                # Caso 4: prefixo parcial (precisa dividir no meio)
                else:
                    resto_filho = filho.prefixo[len(prefixo_comum):]
                    resto_palavra = palavra[len(prefixo_comum):]

                    # novo nó intermediário (o prefixo comum)
                    novo_no = NoTrie(prefixo_comum)

                    # O filho atual tem seu prefixo encurtado
                    filho.prefixo = resto_filho
                    novo_no.filhos.append(filho)

                    # novo filho para o resto da nova palavra
                    novo_filho_palavra = NoTrie(resto_palavra)
                    novo_filho_palavra.noticias.add(id_noticia)
                    novo_no.filhos.append(novo_filho_palavra)

                    # substituir o filho antigo pelo novo nó dividido
                    no_atual.filhos.remove(filho)
                    no_atual.filhos.append(novo_no)
                    return

        # Se não achou prefixo comum, cria um novo nó folha
        novo = NoTrie(palavra)
        novo.noticias.add(id_noticia)
        no_atual.filhos.append(novo)

    def inserir(self, palavra, id_noticia):
        self._inserir(self.raiz, palavra, id_noticia)
