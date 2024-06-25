import time
import matplotlib.pyplot as plt
import numpy as np

class Processo:
    def __init__(self, id, tempo_chegada, tempo_execucao, deadline, quantum_sistema, sobrecarga_sistema, paginas):
        self.id = id
        self.tempo_chegada = tempo_chegada
        self.tempo_execucao = tempo_execucao
        self.deadline = deadline
        self.quantum_sistema = quantum_sistema
        self.sobrecarga_sistema = sobrecarga_sistema
        self.paginas = paginas
        self.tempo_restante = tempo_execucao
        self.paginas_na_ram = []

    def __repr__(self):
        return (f"Processo(id={self.id}, tempo_chegada={self.tempo_chegada}, "
                f"tempo_execucao={self.tempo_execucao}, deadline={self.deadline}, "
                f"tempo_restante={self.tempo_restante}, paginas={self.paginas})")
        
        
def fifo(processos):
    tempo_atual = 0
    for processo in processos:
        if tempo_atual < processo.tempo_chegada:
            tempo_atual = processo.tempo_chegada
        print(f"Executando {processo} no tempo {tempo_atual}")
        tempo_atual += processo.tempo_execucao + processo.sobrecarga_sistema


def sjf(processos):
    processos_ordenados = sorted(processos, key=lambda p: (p.tempo_chegada, p.tempo_execucao))
    fifo(processos_ordenados)


def round_robin(processos, quantum):
    fila = processos[:]
    tempo_atual = 0

    while fila:
        processo = fila.pop(0)
        if tempo_atual < processo.tempo_chegada:
            tempo_atual = processo.tempo_chegada
        
        tempo_executado = min(processo.tempo_restante, quantum)
        processo.tempo_restante -= tempo_executado
        print(f"Executando {processo} no tempo {tempo_atual}")
        tempo_atual += tempo_executado + processo.sobrecarga_sistema

        if processo.tempo_restante > 0:
            fila.append(processo)


def edf(processos):
    processos_ordenados = sorted(processos, key=lambda p: (p.deadline, p.tempo_chegada))
    fifo(processos_ordenados)

class Memoria:
    def __init__(self, tamanho_ram, tamanho_disco, tempo_acesso_disco):
        self.tamanho_ram = tamanho_ram
        self.tamanho_disco = tamanho_disco
        self.tempo_acesso_disco = tempo_acesso_disco
        self.ram = []
        self.disco = []
        self.mapa_ram = {}

    def adicionar_pagina(self, processo_id, pagina, algoritmo):
        if len(self.ram) < self.tamanho_ram:
            self.ram.append((processo_id, pagina))
            self.mapa_ram[(processo_id, pagina)] = time.time()
        else:
            if algoritmo == 'FIFO':
                self.substituir_pagina_fifo(processo_id, pagina)
            elif algoritmo == 'LRU':
                self.substituir_pagina_lru(processo_id, pagina)

    def substituir_pagina_fifo(self, processo_id, pagina):
        processo_id_removido, pagina_removida = self.ram.pop(0)
        self.disco.append((processo_id_removido, pagina_removida))
        self.ram.append((processo_id, pagina))
        self.mapa_ram[(processo_id, pagina)] = time.time()

    def substituir_pagina_lru(self, processo_id, pagina):
        pagina_menos_recente = min(self.mapa_ram, key=self.mapa_ram.get)
        self.ram.remove(pagina_menos_recente)
        self.disco.append(pagina_menos_recente)
        self.ram.append((processo_id, pagina))
        self.mapa_ram[(processo_id, pagina)] = time.time()

    def acessar_pagina(self, processo_id, pagina):
        if (processo_id, pagina) not in self.ram:
            if (processo_id, pagina) in self.disco:
                time.sleep(self.tempo_acesso_disco)
                self.adicionar_pagina(processo_id, pagina, 'LRU')  # Troca padrão LRU
            else:
                print("Página não encontrada no disco!")
        else:
            self.mapa_ram[(processo_id, pagina)] = time.time()

    def mostrar_memoria(self):
        print("RAM: ", self.ram)
        print("Disco: ", self.disco)


def criar_grafico_gantt(processos, tempo_total):
    fig, gnt = plt.subplots()

    gnt.set_xlabel('Tempo')
    gnt.set_ylabel('Processos')

    y_ticks = []
    y_labels = []

    for idx, processo in enumerate(processos):
        y_ticks.append(10 * (idx + 1))
        y_labels.append(f'Processo {processo.id}')
        gnt.broken_barh([(processo.tempo_chegada, processo.tempo_execucao)], (10 * idx, 9))

    gnt.set_yticks(y_ticks)
    gnt.set_yticklabels(y_labels)
    gnt.grid(True)

    plt.show()

def criar_grafico_memoria(ram, disco):
    fig, ax = plt.subplots(2, 1, figsize=(10, 8))

    ax[0].barh(range(len(ram)), [x[1] for x in ram], color='blue')
    ax[0].set_yticks(range(len(ram)))
    ax[0].set_yticklabels([f'P{p[0]}-Pag{p[1]}' for p in ram])
    ax[0].set_title('RAM')

    ax[1].barh(range(len(disco)), [x[1] for x in disco], color='red')
    ax[1].set_yticks(range(len(disco)))
    ax[1].set_yticklabels([f'P{p[0]}-Pag{p[1]}' for p in disco])
    ax[1].set_title('Disco')

    plt.tight_layout()
    plt.show()


def main():
    quantum_sistema = 4
    sobrecarga_sistema = 1
    tempo_acesso_disco = 2  # Unidades de tempo para acesso ao disco

    lista_processos = [
        Processo(1, 0, 8, 10, quantum_sistema, sobrecarga_sistema, [1, 2]),
        Processo(2, 1, 4, 12, quantum_sistema, sobrecarga_sistema, [3, 4]),
        Processo(3, 2, 9, 14, quantum_sistema, sobrecarga_sistema, [5, 6]),
        Processo(4, 3, 5, 16, quantum_sistema, sobrecarga_sistema, [7, 8]),
    ]

    memoria = Memoria(tamanho_ram=10, tamanho_disco=20, tempo_acesso_disco=tempo_acesso_disco)

    print("FIFO:")
    fifo(lista_processos[:])

    print("\nSJF:")
    sjf(lista_processos[:])

    print("\nRound Robin:")
    round_robin(lista_processos[:], quantum_sistema)

    print("\nEDF:")
    edf(lista_processos[:])

    criar_grafico_gantt(lista_processos, 20)
    criar_grafico_memoria(memoria.ram, memoria.disco)

if __name__ == "__main__":
    main()
