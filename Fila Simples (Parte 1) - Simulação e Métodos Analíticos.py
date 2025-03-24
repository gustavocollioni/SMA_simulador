a = 4**8
c = 6**8
m = 10**8
semente = 9**8

def proximo_aleatorio():
    global semente
    semente = (a * semente + c) % m
    return semente / m

def chegada(evento, servidores_ocupados, capacidade_fila, num_servidores, intervalo_chegada_min, intervalo_chegada_max):
    global fila, tempo_global, tempos_estados, perdas

    if fila < capacidade_fila:
        fila += 1
    else:
        perdas += 1

    if fila < len(tempos_estados):
        tempos_estados[fila] += evento['tempo'] - tempo_global

    tempo_global = evento['tempo']
    proxima_chegada = {
        'tipo': 'chegada',
        'tempo': tempo_global + intervalo_chegada_min + proximo_aleatorio() * (intervalo_chegada_max - intervalo_chegada_min)
    }
    eventos.append(proxima_chegada)
    eventos.sort(key=lambda x: x['tempo'])

    if servidores_ocupados < num_servidores and fila > 0:
        proxima_saida = {
            'tipo': 'saida',
            'tempo': tempo_global + 3 + proximo_aleatorio() * 2
        }
        eventos.append(proxima_saida)
        eventos.sort(key=lambda x: x['tempo'])

def saida(evento, servidores_ocupados, capacidade_fila, num_servidores, intervalo_saida_min, intervalo_saida_max):
    global fila, tempo_global, tempos_estados

    if fila > 0:
        fila -= 1

    if fila < len(tempos_estados):
        tempos_estados[fila] += evento['tempo'] - tempo_global

    tempo_global = evento['tempo']

    if fila > 0 and servidores_ocupados < num_servidores:
        proxima_saida = {
            'tipo': 'saida',
            'tempo': tempo_global + intervalo_saida_min + proximo_aleatorio() * (intervalo_saida_max - intervalo_saida_min)
        }
        eventos.append(proxima_saida)
        eventos.sort(key=lambda x: x['tempo'])

def simular_fila(num_servidores, capacidade_fila, intervalo_chegada_min, intervalo_chegada_max, intervalo_saida_min, intervalo_saida_max, primeira_chegada, num_pseudoaleatorios):
    global fila, tempo_global, tempos_estados, perdas, eventos

    fila = 0
    tempo_global = 0
    tempos_estados = [0] * (capacidade_fila + 1)
    perdas = 0
    eventos = [{'tipo': 'chegada', 'tempo': primeira_chegada}]

    count = num_pseudoaleatorios
    while count > 0 and eventos:
        evento = eventos.pop(0)
        servidores_ocupados = fila if fila < num_servidores else num_servidores

        if evento['tipo'] == 'chegada':
            chegada(evento, servidores_ocupados, capacidade_fila, num_servidores, intervalo_chegada_min, intervalo_chegada_max)
        elif evento['tipo'] == 'saida':
            saida(evento, servidores_ocupados, capacidade_fila, num_servidores, intervalo_saida_min, intervalo_saida_max)

        count -= 1

    print(f"Simulação G/G/{num_servidores}/{capacidade_fila}:")
    print("Distribuição de probabilidade dos estados da fila:")
    for i, tempo in enumerate(tempos_estados):
        print(f"{i}: {tempo} ({tempo/tempo_global*100:.2f}%)")
    print(f"Número de perdas de clientes: {perdas}")
    print(f"Tempo global da simulação: {tempo_global:.2f}\n")

simular_fila(num_servidores=1, capacidade_fila=5, intervalo_chegada_min=2, intervalo_chegada_max=5, intervalo_saida_min=3, intervalo_saida_max=5, primeira_chegada=2, num_pseudoaleatorios=100000)
simular_fila(num_servidores=2, capacidade_fila=5, intervalo_chegada_min=2, intervalo_chegada_max=5, intervalo_saida_min=3, intervalo_saida_max=5, primeira_chegada=2, num_pseudoaleatorios=100000)