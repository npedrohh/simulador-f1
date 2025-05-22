import random

# Objeto que representa um piloto ativo
class Piloto:
    def __init__(self, nome, sobrenome, equipe, numero, velocidade, concentracao):
        self.nome = nome
        self.sobrenome = sobrenome
        self.equipe = equipe # equipe pela qual o piloto corre
        self.numero = numero # número do piloto, pode mudar apenas caso seja campeão
        self.velocidade = int(velocidade) # utilizada para calcular tempos de volta
        self.concentracao = int(concentracao) # utilizada para calcular risco de acidente
        self.tempo_total = 0.0  # soma de tempo de todas as voltas
        self.voltas = []  # lista de tempos por volta numa corrida
        self.abandonou = False # True se o piloto abandonou a corrida, False caso contrário

    def __str__(self):
        return f"{self.nome} {self.sobrenome} - {self.equipe} #{self.numero}"

    def nome_completo(self):
        return f"{self.nome} {self.sobrenome}"

###

# Objeto que representa um circuito da temporada
class Circuito:
    def __init__(self, nome, pais, tempo_medio, voltas, retas, curva):
        self.nome = nome
        self.pais = pais
        self.tempo_medio = converter_tempo(tempo_medio)
        self.voltas = voltas
        self.retas = retas
        self.curva = curva

    # Retorna o tempo no formato mm:ss.SSS
    def tempo_formatado(self):
        """Retorna tempo_medio no formato mm:ss.SSS"""
        minutos = int(self.tempo_medio // 60)
        segundos = self.tempo_medio % 60
        return f"{minutos}:{segundos:06.3f}"

    def __str__(self):
        return f"{self.nome} ({self.pais}) - Tempo médio: {self.tempo_formatado()}"

####

# Objeto para
class Corrida:
    def __init__(self, circuito, pilotos):
        self.circuito = circuito
        self.pilotos = pilotos
        self.classificados = []
        self.volta_atual = 0

    def simular_corrida(self):

        self.simular_proxima_volta()

    def simular_volta(self):
        for piloto in self.pilotos:
            if piloto.abandonou:
                continue  # pula quem já abandonou

            # Verifica se o piloto abandona nesta volta
            chance_base = 0.001
            # Conta de risco ainda precisa de um pouco mais de aleatoriedade
            risco = chance_base * (100 - piloto.concentracao) / 100
            temp = random.random()
            if temp < risco:
                piloto.abandonou = True
                continue

            # Fórmula para calcular o tempo de volta do piloto
            ajuste = 1 - (piloto.velocidade-20) / 3000
            variacao = random.normalvariate(0, 0.5)
            tempo_volta = self.circuito.tempo_medio * ajuste + variacao

            # Soma do tempo de volta ao tempo total de corrida e adição de tempo_volta na lista voltas
            piloto.tempo_total += tempo_volta
            piloto.voltas.append(tempo_volta)

        # Incrementa o número de voltas
        self.volta_atual += 1

    # Retorna uma lista de tuplas contendo cada piloto e o seu tempo total de corrida
    # Essa lista é ordenada da seguinte forma:
    # - Pilotos que NÃO ABANDONARAM, em ordem crescente de tempo de corrida
    # - Pilotos que ABANDONARAM, em ordem decrescente de tempo de corrida
    def tabela_volta(self):
        self.classificados = sorted(
            self.pilotos,
            key=lambda p: (
                p.abandonou,
                p.tempo_total if not p.abandonou else -p.tempo_total
            )
        )
        return [(piloto, piloto.tempo_total) for piloto in self.classificados]


########################################################################################################################

# Converte tempo no formato string para float na medida de segundos
def converter_tempo(tempo):
    if isinstance(tempo, (int, float)):
        return float(tempo)
    minutos, segundos = tempo.split(":")
    return int(minutos) * 60 + float(segundos)

# Formata o tempo em float (em segundos) para uma string no formato mm:ss.SSS
def formatar_tempo(tempo_seg):
    minutos = int(tempo_seg // 60)
    segundos = tempo_seg % 60
    return f"{minutos}:{segundos:06.3f}"

########################################################################################################################
