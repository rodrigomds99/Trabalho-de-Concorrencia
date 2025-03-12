from threading import Thread, Lock, Condition
from queue import Queue
import random
import time
import sys

# Classe que representa a experiência da NASA
class NASAExperience:
    def __init__(self, N_ATRACOES, N_VAGAS):
        # Inicializa o número de atrações e vagas disponíveis
        self.n_atracoes = N_ATRACOES
        self.n_vagas = N_VAGAS

        # Fila para organizar as pessoas
        self.fila = Queue()

        # Contadores de vagas ocupadas e pessoas atendidas
        self.vagas_ocupadas = 0
        self.total_pessoas = 0
        self.pessoas_atendidas = 0

        # A experiência atual em execução
        self.experiencia_atual = None

        # Lock para sincronização de threads
        self.lock = Lock()

        # Condição para pausar ou continuar a execução
        self.cond = Condition(self.lock)

        # Estatísticas
        self.tempo_espera = {f"AT-{i}": [] for i in range(1, N_ATRACOES + 1)}
        self.tempo_ocupacao = {f"AT-{i}": 0 for i in range(1, N_ATRACOES + 1)}
        self.tempo_inicio_simulacao = None
        self.tempo_fim_simulacao = None
        self.tempo_inicio_experiencia = None

    # Método para adicionar uma pessoa na fila
    def entrar_fila(self, pessoa_id, experiencia):
        with self.lock:
            print(f"[Pessoa {pessoa_id} / {experiencia}] Aguardando na Fila.")

            # Adiciona a pessoa na fila
            self.fila.put((pessoa_id, experiencia, time.time()))

            # Notifica as threads
            self.cond.notify_all()

    # Método principal que gerencia a execução das Experiências
    def iniciar_experiencia(self):
        self.tempo_inicio_simulacao = time.time()
        while True:
            with self.lock:
                # Espera até que haja pessoas na fila ou pessoas na experiência
                while self.fila.empty() and self.vagas_ocupadas == 0:
                    if self.pessoas_atendidas == self.total_pessoas:
                        # Pegando o tempo em que a simulação finalizou
                        self.tempo_fim_simulacao = time.time()
                        return  # Todas as pessoas foram atendidas, encerramos a thread
                    self.cond.wait()

                # Inicia uma nova experiência se nenhuma estiver ativa
                if not self.fila.empty() and self.experiencia_atual is None:
                    pessoa_id, experiencia, _ = self.fila.queue[0]
                    self.experiencia_atual = experiencia
                    self.tempo_inicio_experiencia = time.time()
                    print(f"[NASA] Iniciando a experiência {experiencia}.")

                # Permite a entrada de pessoas na experiência atual se houver vagas
                while (not self.fila.empty() and self.experiencia_atual == self.fila.queue[0][1] and self.vagas_ocupadas < self.n_vagas):
                    pessoa_id, experiencia, tempo_chegada = self.fila.get()  # Remove a pessoa da fila
                    self.vagas_ocupadas += 1
                    self.pessoas_atendidas += 1  # Incrementa o número de pessoas atendidas

                    tempo_espera = (time.time() - tempo_chegada) * 1000
                    self.tempo_espera[experiencia].append(tempo_espera)
                    print(f"[Pessoa {pessoa_id} / {experiencia}] Entrou na NASA Experiences (quantidade = {self.vagas_ocupadas}).")

                    # Criando uma Thread para gerenciar a saída da pessoa após a permanência
                    Thread(target=self.sair_da_experiencia, args=(pessoa_id, experiencia)).start()

                # Finaliza a experiência atual se não houver mais vagas ocupadas
                if self.vagas_ocupadas == 0 and self.experiencia_atual:
                    self.tempo_ocupacao[self.experiencia_atual] += time.time() - self.tempo_inicio_experiencia
                    print(f"[NASA] Pausando a experiencia {self.experiencia_atual}. ")
                    self.experiencia_atual = None
                    self.cond.notify_all()

    # Método para gerenciar a saída de uma pessoa após o tempo de permanência
    def sair_da_experiencia(self, pessoa_id, experiencia):
        time.sleep(PERMANENCIA * UNID_TEMPO / 1000.0)  # Ajusta o tempo baseado na unidade de tempo
        with self.lock:
            self.vagas_ocupadas -= 1
            print(f"[Pessoa {pessoa_id} / {experiencia}] Saiu da NASA Experiences (quantidade = {self.vagas_ocupadas}).")

            # Notificando as Threads que estão esperando mudanças
            self.cond.notify_all()

    def gerar_relatorio(self):
        tempo_ocupado_total = 0

        print("\n[Relatório Estatístico]")
        print("Tempo médio de espera (em milissegundos):")
        for experiencia, tempos in self.tempo_espera.items():
            media = sum(tempos) / len(tempos) if tempos else 0
            print(f"Experiência {experiencia}: {media:.2f} ms")

        # Calcula o tempo total da simulação
        tempo_total_simulacao = self.tempo_fim_simulacao - self.tempo_inicio_simulacao
        
        print("\nTaxa de ocupação das atrações:")
        for experiencia, tempo_ocupado in self.tempo_ocupacao.items():
            taxa = (tempo_ocupado / tempo_total_simulacao) * 100 if tempo_total_simulacao > 0 else 0
            print(f"Experiência {experiencia}: {taxa:.2f}%")

        # Soma os tempos de ocupação das atrações, garantindo que não ultrapasse o tempo total da simulação
        tempo_ocupado_total = sum(min(tempo, tempo_total_simulacao) for tempo in self.tempo_ocupacao.values())

        # Calcula a taxa total de ocupação
        taxa_total = (tempo_ocupado_total / tempo_total_simulacao) * 100 if tempo_total_simulacao > 0 else 0
        print(f"\nTaxa de ocupação total: {taxa_total:.2f}%")


# Classe para criar as Threads que representam as Pessoas
class CriaPessoas(Thread):
    def __init__(self, N_PESSOAS, MAX_INTERVALO, nasa_experience):
        super().__init__()
        # Número de pessoas a serem criadas
        self.n_pessoas = N_PESSOAS

        # Intervalo máximo entre a chegada de pessoas
        self.max_intervalo = MAX_INTERVALO

        # Referência à instância da experiência
        self.nasa_experience = nasa_experience

    # Método principal que executa a criação das Pessoas
    def run(self):
        for i in range(1, self.n_pessoas + 1):
            # Escolhendo aleatoriamente uma experiência para a pessoa
            experiencia = f"AT-{random.randint(1, self.nasa_experience.n_atracoes)}"

            # Adicionando a pessoa na fila
            self.nasa_experience.entrar_fila(i, experiencia)

            # Espera um intervalo aleatório antes de criar a próxima pessoa
            time.sleep(random.randint(0, self.max_intervalo) * UNID_TEMPO / 1000.0)

if __name__ == "__main__":
    # Verificando os argumentos
    if len(sys.argv) != 8:
        print("Uso: python programa.py <N_ATRACOES> <N_PESSOAS> <N_VAGAS> <PERMANENCIA> <MAX_INTERVALO> <SEMENTE> <UNID_TEMPO>")
        sys.exit(1)

    try:
        # Lê os argumentos da linha de comando
        N_ATRACOES, N_PESSOAS, N_VAGAS, PERMANENCIA, MAX_INTERVALO, SEMENTE, UNID_TEMPO = map(int, sys.argv[1:])

        # Validação dos parâmetros
        if N_ATRACOES <= 0 or N_PESSOAS <= 0 or N_VAGAS <= 0 or PERMANENCIA <= 0 or MAX_INTERVALO < 0 or SEMENTE < 0 or UNID_TEMPO <= 0:
            raise ValueError("Todos os parâmetros devem ser números inteiros positivos.")

        # Configura a semente para números aleatórios
        random.seed(SEMENTE)

        # Cria a instância da experiência
        nasa_experience = NASAExperience(N_ATRACOES, N_VAGAS)
        nasa_experience.total_pessoas = N_PESSOAS

        print("[NASA] Simulação iniciada.")

        # Cria a thread responsável por adicionar pessoas à fila
        criador_pessoas = CriaPessoas(N_PESSOAS, MAX_INTERVALO, nasa_experience)
        criador_pessoas.start()

        # Cria a thread responsável pela execução das experiências
        experiencia_thread = Thread(target=nasa_experience.iniciar_experiencia)
        experiencia_thread.start()

        # Aguarda a finalização das threads
        criador_pessoas.join()
        experiencia_thread.join()

        print("[NASA] Simulação finalizada.")

        nasa_experience.gerar_relatorio()

    except ValueError as e:
        print(f"Erro nos parâmetros: {e}")
        sys.exit(1)
