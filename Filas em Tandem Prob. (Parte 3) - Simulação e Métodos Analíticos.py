import heapq
import itertools

# Gera números aleatórios congruentes
A = 4**8
C = 6**8
M = 10**8
semente = 9**8

def proximo_aleatorio():
    global semente
    semente = (A * semente + C) % M
    return semente / M

# Construtor
class Fila:
    def __init__(self, servidores, capacidade, intervalo_chegada, intervalo_saida, num_eventos):
        self.servidores = servidores                                                            # Nº de servidores
        self.capacidade = capacidade                                                            # Capacidade máxima
        self.intervalo_chegada = intervalo_chegada                                              # Intervalo entre chegadas (somente fila 0)
        self.intervalo_saida = intervalo_saida                                                  # Intervalo de serviço
        self.fila = 0                                                                           # Nº de clientes no sistema
        self.perdas = 0                                                                         # Nº de perdas
        self.num_eventos = num_eventos                                                          # Contador de perdas
        self.capacidade = int(capacidade) if capacidade != float('inf') else self.num_eventos
        self.tempos_estados = [0.0] * (self.capacidade + 1)                                     # Tempo em cada estado

# Variáveis globais
filas = []                        # Lista de filas
tempo_global = 0.0                # Relógio da simulação
desempatador = itertools.count()  # Contador auxiliar
eventos = []                      # Heap de eventos: (tempo, contador, tipo, idx)

def agenda_evento(tempo, tipo, idx):
    heapq.heappush(eventos, (tempo, next(desempatador), tipo, idx))

# Mapeia transições com probabilidades condicionais
transicoes = {
    0: [(1, 0.8), (2, 0.2)],                # Após atendimento na Fila 1: 80% vão para Fila 2, 20% vão para Fila 3
    1: [(0, 0.3), ('out', 0.2), (2, 0.5)],  # Após Fila 2: 30% retornam para Fila 1, 20% saem do sistema, 50% seguem para Fila 3
    2: [(0, 0.7), ('out', 0.3)]             # Após Fila 3: 70% retornam para Fila 1, 30% saem do sistema
}

def escolhe_proxima(origem):
    r = proximo_aleatorio()
    cumulativa = 0.0
    for destino, prob in transicoes.get(origem, []):
        cumulativa += prob
        if r <= cumulativa:
            return destino
    return None

def chegada(evento_tempo, idx):
    global tempo_global
    fila = filas[idx]

    # Atualiza tempo acumulado no estado atual
    delta = evento_tempo - tempo_global
    fila.tempos_estados[fila.fila] += delta

    # Avança o relógio
    tempo_global = evento_tempo

    # Processa chegada: entra ou é perdida
    if fila.fila < fila.capacidade:
        fila.fila += 1
    else:
        fila.perdas += 1

    # Agenda nova chegada externa se for fila 0
    if idx == 0 and fila.intervalo_chegada:
        t_chegada = tempo_global + (
            fila.intervalo_chegada[0]
            + proximo_aleatorio() * (fila.intervalo_chegada[1] - fila.intervalo_chegada[0])
        )
        agenda_evento(t_chegada, 'chegada', 0)

    # Agenda saída se houver servidor livre
    if fila.fila <= fila.servidores:
        t_saida = tempo_global + (
            fila.intervalo_saida[0]
            + proximo_aleatorio() * (fila.intervalo_saida[1] - fila.intervalo_saida[0])
        )
        agenda_evento(t_saida, 'saida', idx)

def saida(evento_tempo, idx):
    global tempo_global
    fila = filas[idx]

    # Atualiza tempo acumulado no estado atual
    delta = evento_tempo - tempo_global
    fila.tempos_estados[fila.fila] += delta

    # Avança o relógio
    tempo_global = evento_tempo

    # Se houver alguém, cliente sai
    if fila.fila > 0:
        fila.fila -= 1

    # Agenda nova saída se ainda houver clientes
    if fila.fila >= fila.servidores:
        t_prox_saida = tempo_global + (
            fila.intervalo_saida[0]
            + proximo_aleatorio() * (fila.intervalo_saida[1] - fila.intervalo_saida[0])
        )
        agenda_evento(t_prox_saida, 'saida', idx)

    # Decide para onde encaminhar
    destino = escolhe_proxima(idx)
    if isinstance(destino, int):
        agenda_evento(tempo_global, 'chegada', destino)
    # Caso seja 'out', nada é feito (cliente sai do sistema)

def simular_rede(filas_parametros, primeira_chegada, num_eventos):
    global filas, eventos, tempo_global

    # Inicializa variáveis
    filas = []
    eventos = []
    tempo_global = 0.0

    # Cria filas conforme parâmetros
    for servidores, capacidade, interv_chegada, interv_saida in filas_parametros:
        filas.append(Fila(servidores, capacidade, interv_chegada, interv_saida, num_eventos))

    # Agenda primeira chegada externa
    agenda_evento(primeira_chegada, 'chegada', 0)

    # Processa eventos
    for _ in range(num_eventos):
        if not eventos:
            break
        tempo, _, tipo, idx = heapq.heappop(eventos)
        if tipo == 'chegada':
            chegada(tempo, idx)
        else:
            saida(tempo, idx)

    # Exibe estatísticas
    for i, fila in enumerate(filas):
        print(f"Fila {i+1} (G/G/{fila.servidores}/{fila.capacidade}):")
        print("Distribuição de probabilidade dos estados da fila:")
        for j, t in enumerate(fila.tempos_estados):
            pct = (t / tempo_global * 100) if tempo_global > 0 else 0.0
            print(f"  {j}: {t:.2f} ({pct:.2f}%)")
        print(f"Perdas: {fila.perdas}")
        print("-" * 40)

    print(f"\nTempo total da simulação: {tempo_global:.2f}")

# Executa com os parâmetros do enunciado
simular_rede(
    filas_parametros=[
        (1, float('inf'), (2, 4), (1, 2)),  # Fila 1: G/G/1, chegada externa
        (2, 5, None, (4, 8)),               # Fila 2: G/G/2/5
        (2, 10, None, (5, 15))              # Fila 3: G/G/2/10
    ],
    primeira_chegada=2.0,
    num_eventos=100000
)