import heapq
import itertools

a = 4**8
c = 6**8
m = 10**8
semente = 9**8

def proximo_aleatorio():
    global semente
    semente = (a * semente + c) % m
    return semente / m

class Fila:
    def __init__(self, servidores, capacidade, intervalo_chegada, intervalo_saida):
        self.servidores = servidores                    # Nº de servidores
        self.capacidade = capacidade                    # Capacidade máxima
        self.intervalo_chegada = intervalo_chegada      # Intervalo entre chegadas (somente fila 0)
        self.intervalo_saida = intervalo_saida          # Intervalo de serviço
        self.fila = 0                                   # Nº de clientes no sistema
        self.perdas = 0                                 # Contador de perdas
        self.tempos_estados = [0.0] * (capacidade + 1)  # Tempo em cada estado

# Variáveis globais
filas = []                        # Lista de filas
tempo_global = 0.0                # Relógio da simulação
desempatador = itertools.count()  # Contador auxiliar
eventos = []                      # Heap de eventos: (tempo, contador, tipo, idx)

def agenda_evento(tempo, tipo, idx):
    heapq.heappush(eventos, (tempo, next(desempatador), tipo, idx))

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
    if idx == 0:
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

    # Cliente sai se houver alguém
    if fila.fila > 0:
        fila.fila -= 1

    # Agenda nova saída se ainda houver clientes
    if fila.fila > 0:
        t_prox_saida = tempo_global + (
            fila.intervalo_saida[0]
            + proximo_aleatorio() * (fila.intervalo_saida[1] - fila.intervalo_saida[0])
        )
        agenda_evento(t_prox_saida, 'saida', idx)

    # Encaminha cliente à próxima fila se houver
    if idx + 1 < len(filas):
        agenda_evento(tempo_global, 'chegada', idx + 1)

def simular_rede(filas_parametros, primeira_chegada, num_eventos):
    global filas, eventos, tempo_global

    # Inicializa variáveis
    filas = []
    eventos = []
    tempo_global = 0.0

    # Cria filas conforme parâmetros
    for servidores, capacidade, interv_chegada, interv_saida in filas_parametros:
        filas.append(Fila(servidores, capacidade, interv_chegada, interv_saida))

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

# Exemplos com valores referentes à entrega do Módulo 6
simular_rede(
    filas_parametros=[
        (2, 3, (1, 4), (3, 4)),     # Fila 1 - G/G/2/3, chegadas entre 1..4, atendimento entre 3..4
        (1, 5, None, (2, 3))        # Fila 2 - G/G/1/5, atendimento entre 2..3
    ],
    primeira_chegada=1.5,
    num_eventos=100000
)