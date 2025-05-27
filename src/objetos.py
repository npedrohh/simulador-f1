import random

# Classe que representa um piloto ativo
class Piloto:
    def __init__(self, nome, sobrenome, equipe, numero, velocidade, concentracao):
        self.nome = nome
        self.sobrenome = sobrenome
        self.equipe = equipe # Equipe pela qual o piloto corre
        self.numero = numero # Número do piloto, pode mudar apenas caso seja campeão
        self.velocidade = int(velocidade) # Utilizada para calcular tempos de volta
        self.concentracao = int(concentracao) # Utilizada para calcular risco de acidente

        # Atributos abaixo precisam ser adicionados na classe Corrida da mesma forma que foi feito na classe Classificacao
        self.tempo_total = 0.0  # Soma de tempo de todas as voltas
        self.voltas = []  # Lista de tempos por volta numa corrida
        self.tempo_volta_classificacao = [] # Lista de tempos por volta numa classificação
        self.abandonou = False # True se o piloto abandonou a corrida, False caso contrário
        self.delta_proximo_piloto = None # Diferença de tempo para o piloto à frente
        self.delta_lider = None # Diferença de tempo para o líder da corrida

    def __str__(self):
        return f"{self.nome} {self.sobrenome} - {self.equipe} #{self.numero}"

    def nome_completo(self):
        return f"{self.nome} {self.sobrenome}"

    def delta_prox_formatado(self):
        return f"+{self.delta_proximo_piloto:01.3f}"

    def delta_lider_formatado(self):
        return f"+{self.delta_lider:01.3f}"

########################################################################################################################

# Objeto que representa um circuito da temporada
class Circuito:
    def __init__(self, nome, pais, tempo_medio, voltas, retas, curva, probabilidade_chuva):
        self.nome = nome
        self.pais = pais
        self.tempo_medio = converter_tempo(tempo_medio)
        self.voltas = voltas
        self.retas = retas
        self.curva = curva
        self.probabilidade_chuva = probabilidade_chuva

    # Retorna o tempo no formato mm:ss.SSS
    def tempo_formatado(self):
        minutos = int(self.tempo_medio // 60)
        segundos = self.tempo_medio % 60
        return f"{minutos}:{segundos:06.3f}"

    def __str__(self):
        return f"{self.nome} ({self.pais}) - Tempo médio: {self.tempo_formatado()}"

########################################################################################################################

# Classe responsável por simular o sistema de classificação
class Classificacao:
    def __init__(self, circuito, pilotos):
        self.circuito = circuito                      # Objeto com informações do circuito
        self.pilotos = pilotos                        # Lista de objetos piloto
        self.classificacao = []                       # Lista ordenada de pilotos ao final de cada etapa
        self.tempo_atual = 0                          # Tempo atual da simulação, em segundos
        self.tempo_final = 18 * 60                    # Tempo máximo da etapa atual
        self.etapa = 1                                # Etapa atual (Q1, Q2 ou Q3)

        # Dicionários para controlar os dados por piloto
        self.tempos_saida = {piloto.numero: [] for piloto in self.pilotos}           # Tempos em que o piloto sairá para tentar volta
        self.classificou = {piloto.numero: True for piloto in self.pilotos}          # Define se o piloto corre na próxima etapa
        self.melhor_volta = {piloto.numero: float('inf') for piloto in self.pilotos} # Melhor tempo de volta de cada piloto na etapa
        self.eliminado_na_etapa = {piloto.numero: -1 for piloto in self.pilotos}     # Etapa em que o piloto foi eliminado (-1 se não foi)

    # Simula o andamento da classificação a cada segundo
    def simular_segundo(self):
        for piloto in self.pilotos:
            if self.classificou[piloto.numero]:
                # Se o tempo atual for igual a um dos tempos de saída, simula uma volta
                if (self.tempo_atual == self.tempos_saida[piloto.numero][0]) or (self.tempo_atual == self.tempos_saida[piloto.numero][1]):
                    self.simular_volta(piloto)

        self.tempo_atual += 1

    # Define os classificados e eliminados ao fim de uma etapa, a duração da etapa e reseta variáveis da classificação
    def setar_etapa(self):
        match self.etapa:
            case 1:
                self.tempo_final = 18 * 60

            case 2:
                self.tempo_final = 15 * 60
                pilotos_16_a_20 = self.classificacao[-5:]  # Eliminados da 16° à 20° posição
                for piloto in pilotos_16_a_20:
                    self.classificou[piloto.numero] = False
                    self.eliminado_na_etapa[piloto.numero] = 1

            case 3:
                self.tempo_final = 10 * 60
                pilotos_11_a_15 = self.classificacao[10:15]  # Eliminados da 11ª à 15ª posição
                for piloto in pilotos_11_a_15:
                    self.classificou[piloto.numero] = False
                    self.eliminado_na_etapa[piloto.numero] = 2

        # Atualiza os tempos de saída e reseta tempos de volta para nova etapa
        for piloto in self.pilotos:
            if len(self.tempos_saida[piloto.numero]):
                self.tempos_saida[piloto.numero].pop()
                self.tempos_saida[piloto.numero].pop()
            if self.classificou[piloto.numero]:
                self.definir_tempo_saida(piloto)
                self.melhor_volta[piloto.numero] = float('inf')

        self.tempo_atual = 0  # Reinicia o tempo para a nova etapa

    # Gera dois tempos aleatórios para o piloto sair para a pista dentro do intervalo da etapa
    # Os tempos são gerados seguindo uma distribuição normal em diferentes momentos da etapa
    def definir_tempo_saida(self, piloto):
        while True:
            valor1 = round(random.normalvariate(round(self.tempo_final * 0.34), round(self.tempo_final * 0.13)))
            if 0 < valor1 <= (self.tempo_final * 0.6):
                self.tempos_saida[piloto.numero].append(valor1)
                break
        while True:
            valor2 = round(random.normalvariate(round(self.tempo_final * 0.81), round(self.tempo_final * 0.09)))
            if (valor1 + self.tempo_final * 0.13) <= valor2 < self.tempo_final:
                self.tempos_saida[piloto.numero].append(valor2)
                break

    # Simula uma volta para o piloto e atualiza seu melhor tempo se for mais rápido
    def simular_volta(self, piloto):
        ajuste = 1 - (piloto.velocidade - 20) / 3000  # Ajuste baseado na velocidade do piloto
        variacao = random.normalvariate(0, 0.5)       # Variação aleatória no tempo
        tempo_volta_classificacao = self.circuito.tempo_medio * ajuste + variacao

        # Atualiza o melhor tempo se essa volta for mais rápida
        self.melhor_volta[piloto.numero] = min(self.melhor_volta[piloto.numero], tempo_volta_classificacao)

    # Retorna a classificação ordenada dos pilotos
    def tabela_segundo(self):
        self.classificacao = sorted(
            self.pilotos,
            key=lambda p: (
                not self.classificou[p.numero],                              # Classificados vêm antes dos eliminados
                -self.eliminado_na_etapa[p.numero] if not self.classificou[p.numero] else 0,  # Quem foi eliminado no Q2 vem antes de quem foi no Q1
                self.melhor_volta[p.numero]                                  # Menor tempo de volta define o último desempate
            )
        )
        return [(piloto, piloto.tempo_total) for piloto in self.classificacao]

########################################################################################################################

# Classe responsável pela simulação das corridas
class Corrida:
    def __init__(self, circuito, classificacao, pilotos):
        self.circuito = circuito
        self.pilotos = pilotos
        self.classificacao = classificacao
        self.tabela = []
        self.volta_atual = 0
        self.lider = None

    def setar_largada(self):
        temp = 0
        for piloto in self.classificacao.classificacao:
            piloto.tempo_total += temp
            temp += 1

    def simular_primeira_volta(self):
        self.setar_largada()
        self.simular_volta() # Mudar para a lógica de largadas futuramente

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

        # Atualiza líder e classificação
        self.lider = min(
            (p for p in self.pilotos if not p.abandonou),
            key=lambda p: p.tempo_total,
            default=None  # opcional: evita erro se nenhum piloto estiver qualificado
        )
        self.tabela = sorted(
            self.pilotos,
            key=lambda p: (
                p.abandonou,
                p.tempo_total if not p.abandonou else -p.tempo_total
            )
        )

        # juntar+em+grupos+de+ultrapassagens+e+depois+calcular+as+ultrapassagens

        # Atualiza tanto o delta pro Líder quanto o delta para o próximo piloto
        for piloto in self.pilotos:
            if piloto == self.lider:
                piloto.delta_proximo_piloto = "Líder"
                piloto.delta_lider = "Líder"
            else:
                posicao_piloto = self.tabela.index(piloto)
                proximo_piloto = self.tabela[posicao_piloto - 1]
                piloto.delta_proximo_piloto = piloto.tempo_total - proximo_piloto.tempo_total
                piloto.delta_lider = piloto.tempo_total - self.lider.tempo_total

        self.volta_atual += 1

    # Retorna uma lista de tuplas contendo cada piloto e o seu tempo total de corrida
    # Essa lista é ordenada da seguinte forma:
    # - Pilotos que NÃO ABANDONARAM, em ordem crescente de tempo de corrida
    # - Pilotos que ABANDONARAM, em ordem decrescente de tempo de corrida
    def tabela_volta(self):
        self.tabela = sorted(
            self.pilotos,
            key=lambda p: (
                p.abandonou,
                p.tempo_total if not p.abandonou else -p.tempo_total
            )
        )
        return [(piloto, piloto.tempo_total) for piloto in self.tabela]


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
