import json
import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import Progressbar
import ttkbootstrap as tb
from ttkbootstrap import Window
from ttkbootstrap.widgets import Label, Button, Combobox, Frame, Treeview
from src.objetos import Piloto, Circuito, Corrida, formatar_tempo, Classificacao


class TelaInicial(Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("Simulador de Corrida F1")
        self.geometry("450x400")
        self.pilotos = []
        self.velocidade = 1000
        self.circuito = Circuito("Interlagos", "Brasil", "1:27.452",
                                 70, 5, 3, 0.1)

        self.create_widgets()

    def create_widgets(self):
        Label(self, text="🏁 Simulador de Corrida F1", font=("Arial", 16, "bold")).pack(pady=10)

        # Botões para carregar dados do .json e simular a corrida com esses dados
        Button(self, text="Carregar Pilotos", command=self.carregar_pilotos, width=30).pack(pady=5)
        Button(self, text="Começar Fim de Semana", command=self.abrir_janela_classificacao, width=30).pack(pady=5)

    def carregar_pilotos(self):
        try:
            with open("pilotos.json", "r", encoding="utf-8") as f:
                dados = json.load(f)
                self.pilotos = [Piloto(**p) for p in dados]
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar pilotos: {e}")

    def abrir_janela_classificacao(self):
        if not self.pilotos:
            messagebox.showwarning("Aviso", "Carregue os pilotos primeiro.")
            return
        TelaClassificacao(self)

class TelaCorrida(tb.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.geometry("600x700")
        self.pilotos = self.parent.pilotos
        self.classificacao = self.parent.classificacao
        self.velocidade = 1000
        self.circuito = Circuito("Interlagos", "Brasil", "1:27.452",
                                 70, 5, 3, 0.1)
        self.corrida = Corrida(self.circuito, self.classificacao, self.pilotos)

        self.velocidade_map = {
            "Muito lento": 1600,
            "Lento": 1300,
            "Normal": 1000,
            "Rápido": 600,
            "Muito rápido": 300,
            "Ultra rápido": 50
        }

        self.title(f"GP do {self.circuito.pais} - {self.circuito.nome}")

        self.create_widgets()

    def create_widgets(self):
        Label(self, text=f"GP do {self.circuito.pais} - {self.circuito.nome}", font=("Arial", 16, "bold")).pack(pady=10)

        # Botão para simular a corrida com os dados atuais
        Button(self, text="Começar Corrida", command=self.simular_corrida, width=30).pack(pady=5)

        # Label e Combobox para velocidade
        frame_velocidade = Frame(self)
        frame_velocidade.pack(pady=5)

        Label(frame_velocidade, text="Velocidade da simulação:").pack(side="left", padx=5)

        self.velocidade_var = tk.StringVar()
        self.velocidade_combo = Combobox(
            frame_velocidade, textvariable=self.velocidade_var, state="readonly", width=15
        )
        self.velocidade_combo["values"] = ["Muito lento", "Lento", "Normal", "Rápido", "Muito rápido", "Ultra rápido"]
        self.velocidade_combo.current(2)  # Padrão: "Normal"
        self.velocidade_combo.pack(side="left")

        # Barra de Progresso de voltas
        self.progress = Progressbar(self, orient="horizontal", length=300, mode="determinate",
                                       maximum=self.circuito.voltas, bootstyle="success-striped")
        self.progress.pack(pady=20)
        self.label_voltas = tb.Label(self, text=f"Voltas: 0/{self.circuito.voltas}")
        self.label_voltas.pack()

        # Tabela de resultado da corrida
        self.tree = Treeview(self, columns=("pos", "nome", "equipe", "ultima_volta", "proximo_piloto", "lider"), show="headings", height=20)
        self.tree.heading("pos", text="Pos")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("equipe", text="Equipe")
        self.tree.heading("ultima_volta", text="Últ. Volta")
        self.tree.heading("proximo_piloto", text="Próx.")
        self.tree.heading("lider", text="Líder")

        self.tree.column("pos", width=40, anchor="center")
        self.tree.column("nome", width=150)
        self.tree.column("equipe", width=100, anchor="center")
        self.tree.column("ultima_volta", width=80, anchor="center")
        self.tree.column("proximo_piloto", width=70, anchor="center")
        self.tree.column("lider", width=70, anchor="center")

        self.tree.tag_configure("abandonou", background="#524f4f")
        self.tree.tag_configure("primeiro", background="#bd951b")
        self.tree.tag_configure("segundo", background="#787878")
        self.tree.tag_configure("terceiro", background="#cd7f32")
        self.tree.tag_configure("impar", background="#404040")
        self.tree.tag_configure("par", background="#2f2f2f")

        self.tree.pack(pady=10)

        self.inicia_tabela(self.classificacao.classificacao)

    def simular_corrida(self):
        if not self.pilotos:
            messagebox.showwarning("Aviso", "Carregue os pilotos primeiro.")
            return

        self.simular_primeira_volta()

    def simular_primeira_volta(self):

        self.corrida.simular_primeira_volta()
        tabela = self.corrida.tabela_volta()

        self.atualiza_tabela(tabela)
        self.progress['value'] = self.corrida.volta_atual
        self.label_voltas.config(text=f"Voltas: {self.corrida.volta_atual}/{self.circuito.voltas}")

        self.velocidade = self.velocidade_map.get(self.velocidade_var.get(), 1000)
        self.after(self.velocidade, self.simular_proxima_volta)

    def simular_proxima_volta(self):
        if self.corrida.volta_atual >= self.circuito.voltas:
            resultado = self.corrida.tabela_volta()
            self.atualiza_tabela(resultado)
            return

        self.corrida.simular_volta()
        tabela = self.corrida.tabela_volta()

        self.atualiza_tabela(tabela)
        self.progress['value'] = self.corrida.volta_atual
        self.label_voltas.config(text=f"Voltas: {self.corrida.volta_atual}/{self.circuito.voltas}")

        self.velocidade = self.velocidade_map.get(self.velocidade_var.get(), 1000)
        self.after(self.velocidade, self.simular_proxima_volta)

    def obter_tag_por_posicao(self, pos, abandonou=False):
        if abandonou:
            return "abandonou"
        if pos == 1:
            return "primeiro"
        elif pos == 2:
            return "segundo"
        elif pos == 3:
            return "terceiro"
        return "par" if pos % 2 == 0 else "impar"

    def insere_linha(self, pos, piloto, tag, mostrar_tempos=True):
        if tag == "abandonou":
            valores = (
                f"{pos}º",
                piloto.nome_completo(),
                piloto.equipe,
                "DNF",
                "Acidente",
                "-"
            )
        elif tag == "primeiro" and mostrar_tempos:
            valores = (
                f"{pos}º",
                piloto.nome_completo(),
                piloto.equipe,
                formatar_tempo(piloto.voltas[-1]),
                "Líder",
                "-"
            )
        elif mostrar_tempos:
            valores = (
                f"{pos}º",
                piloto.nome_completo(),
                piloto.equipe,
                formatar_tempo(piloto.voltas[-1]),
                piloto.delta_prox_formatado(),
                piloto.delta_lider_formatado()
            )
        else:
            # Usado na inicia_tabela para mostrar os dados mas esconder tempos
            valores = (
                f"{pos}º",
                piloto.nome_completo(),
                piloto.equipe,
                "-",
                "-",
                "-"
            )

        self.tree.insert("", "end", values=valores, tags=tag)

    def inicia_tabela(self, classificacao):
        for pos, piloto in enumerate(classificacao, start=1):
            tag = self.obter_tag_por_posicao(pos, piloto.abandonou)
            self.insere_linha(pos, piloto, tag, mostrar_tempos=False)

    def atualiza_tabela(self, tabela):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for pos, (piloto, tempo) in enumerate(tabela, start=1):
            tag = self.obter_tag_por_posicao(pos, piloto.abandonou)
            self.insere_linha(pos, piloto, tag, mostrar_tempos=not piloto.abandonou)

class TelaClassificacao(tb.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        self.geometry("600x700")
        self.pilotos = self.parent.pilotos
        self.velocidade = 1000
        self.circuito = Circuito("Interlagos", "Brasil", "1:27.452",
                                 70, 5, 3, 0.1)
        self.classificacao = Classificacao(self.circuito, self.pilotos)
        self.title(f"Q1 - GP do {self.circuito.pais} - {self.circuito.nome}")

        self.create_widgets()

    def create_widgets(self):
        Label(self, text=f"GP do {self.circuito.pais} - {self.circuito.nome}", font=("Arial", 16, "bold")).pack(pady=10)

        # Botão para simular a corrida com os dados atuais
        self.botao_q = Button(self, text="Começar Q1", command=self.simular_classificacao, width=30)
        self.botao_q.pack(pady=5)

        # Label e Combobox para velocidade
        frame_velocidade = Frame(self)
        frame_velocidade.pack(pady=5)

        Label(frame_velocidade, text="Velocidade da simulação:").pack(side="left", padx=5)

        self.velocidade_var = tk.StringVar()
        self.velocidade_combo = Combobox(
            frame_velocidade, textvariable=self.velocidade_var, state="readonly", width=15
        )
        self.velocidade_combo["values"] = ["Muito lento", "Lento", "Normal", "Rápido", "Muito rápido", "Ultra rápido"]
        self.velocidade_combo.current(2)  # Padrão: "Normal"
        self.velocidade_combo.pack(side="left")

        # Barra de Progresso de voltas
        self.progress = Progressbar(self, orient="horizontal", length=300, mode="determinate",
                                       maximum=self.classificacao.tempo_final, bootstyle="success-striped")
        self.progress.pack(pady=20)
        self.label_voltas = tb.Label(self, text=f"Voltas: 0/{self.circuito.voltas}")
        self.label_voltas.pack()

        # Tabela de resultado da corrida
        self.tree = Treeview(self, columns=("pos", "nome", "equipe", "melhor_volta"), show="headings", height=20)
        self.tree.heading("pos", text="Pos")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("equipe", text="Equipe")
        self.tree.heading("melhor_volta", text="Melhor Volta")

        self.tree.column("pos", width=40, anchor="center")
        self.tree.column("nome", width=150)
        self.tree.column("equipe", width=100, anchor="center")
        self.tree.column("melhor_volta", width=120, anchor="center")

        self.tree.tag_configure("abandonou", background="#524f4f")
        self.tree.tag_configure("primeiro", background="#404080")
        self.tree.tag_configure("impar", background="#404040")
        self.tree.tag_configure("par", background="#2f2f2f")
        self.tree.tag_configure("zona_eliminacao_impar", background="#804040")
        self.tree.tag_configure("zona_eliminacao_par", background="#5e2f2f")
        self.tree.tag_configure("eliminados_impar", background="#262626")
        self.tree.tag_configure("eliminados_par", background="#141414")

        self.tree.pack(pady=10)

    def simular_classificacao(self):
        if not self.pilotos:
            messagebox.showwarning("Aviso", "Carregue os pilotos primeiro.")
            return

        self.simular_proxima_etapa()

    def simular_proxima_etapa(self):
        if self.classificacao.etapa > 3:
            resultado = self.classificacao.tabela_segundo()
            self.atualiza_tabela(resultado)
            return


        self.classificacao.setar_etapa()
        self.progress["maximum"] = self.classificacao.tempo_final
        self.botao_q.config(state="disabled", text=f"Simulando Q{self.classificacao.etapa}")

        self.simular_proximo_segundo()

    def simular_proximo_segundo(self):
        if self.classificacao.tempo_atual >= self.classificacao.tempo_final:
            resultado = self.classificacao.tabela_segundo()
            self.atualiza_tabela(resultado)
            self.classificacao.etapa += 1
            if self.classificacao.etapa <= 3:
                self.botao_q.config(state="normal", text=f"Começar Q{self.classificacao.etapa}")
            else:
                self.botao_q.config(state="normal", text=f"Começar Corrida", command=self.abrir_janela_corrida)
            return

        self.classificacao.simular_segundo()
        tabela = self.classificacao.tabela_segundo()
        self.atualiza_tabela(tabela)

        self.progress['value'] = self.classificacao.tempo_atual
        self.label_voltas.config(text=f"Tempo Restante: {self.formatar_tempo_classificacao(self.classificacao.tempo_atual, self.classificacao.tempo_final)}")

        velocidade_map = {
            "Muito lento": 100,
            "Lento": 65,
            "Normal": 40,
            "Rápido": 20,
            "Muito rápido": 5,
            "Ultra rápido": 0
        }
        self.velocidade = velocidade_map.get(self.velocidade_var.get(), 1000)
        self.after(self.velocidade, self.simular_proximo_segundo)

    def insere_linha(self, pos, piloto, tag):
        melhor_tempo = self.classificacao.melhor_volta[piloto.numero]
        tempo_formatado = "-" if melhor_tempo == float('inf') else formatar_tempo(melhor_tempo)

        if tag == "abandonou":
            self.tree.insert("", "end", values=(
                f"{pos}º",
                f"{piloto.nome_completo()}",
                piloto.equipe,
                "DNF",
            ), tags=tag)
        elif tag == "primeiro":
            self.tree.insert("", "end", values=(
                f"{pos}º",
                f"{piloto.nome_completo()}",
                piloto.equipe,
                tempo_formatado,
            ), tags=tag)
        else:
            self.tree.insert("", "end", values=(
                f"{pos}º",
                f"{piloto.nome_completo()}",
                piloto.equipe,
                tempo_formatado,
            ), tags=tag)

    def atualiza_tabela(self, tabela):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for pos, (piloto, tempo) in enumerate(tabela, start=1):
            if pos == 1:
                self.insere_linha(pos, piloto, "primeiro")
            else:
                match self.classificacao.etapa:
                    case 1:
                        if 16 <= pos <= 20:
                            if pos % 2 == 0:
                                self.insere_linha(pos, piloto, "zona_eliminacao_par")
                            else:
                                self.insere_linha(pos, piloto, "zona_eliminacao_impar")
                        else:
                            if pos % 2 == 0:
                                if self.classificacao.classificou[piloto.numero]:
                                    self.insere_linha(pos, piloto, "par")
                                else:
                                    self.insere_linha(pos, piloto, "zona_eliminacao_par")
                            else:
                                if self.classificacao.classificou[piloto.numero]:
                                    self.insere_linha(pos, piloto, "impar")
                                else:
                                    self.insere_linha(pos, piloto, "zona_eliminacao_impar")

                    case 2:
                        if 11 <= pos <= 15:
                            if pos % 2 == 0:
                                self.insere_linha(pos, piloto, "zona_eliminacao_par")
                            else:
                                self.insere_linha(pos, piloto, "zona_eliminacao_impar")
                        elif 16 <= pos <= 20:
                            if pos % 2 == 0:
                                self.insere_linha(pos, piloto, "eliminados_par")
                            else:
                                self.insere_linha(pos, piloto, "eliminados_impar")
                        else:
                            if pos % 2 == 0:
                                if self.classificacao.classificou[piloto.numero]:
                                    self.insere_linha(pos, piloto, "par")
                                else:
                                    self.insere_linha(pos, piloto, "zona_eliminacao_par")
                            else:
                                if self.classificacao.classificou[piloto.numero]:
                                    self.insere_linha(pos, piloto, "impar")
                                else:
                                    self.insere_linha(pos, piloto, "zona_eliminacao_impar")

                    case 3:
                        if 11 <= pos <= 20:
                            if pos % 2 == 0:
                                self.insere_linha(pos, piloto, "eliminados_par")
                            else:
                                self.insere_linha(pos, piloto, "eliminados_impar")
                        else:
                            if pos % 2 == 0:
                                if self.classificacao.classificou[piloto.numero]:
                                    self.insere_linha(pos, piloto, "par")
                                else:
                                    self.insere_linha(pos, piloto, "zona_eliminacao_par")
                            else:
                                if self.classificacao.classificou[piloto.numero]:
                                    self.insere_linha(pos, piloto, "impar")
                                else:
                                    self.insere_linha(pos, piloto, "zona_eliminacao_impar")

                    case _:
                        if pos % 2 == 0:
                            if self.classificacao.classificou[piloto.numero]:
                                self.insere_linha(pos, piloto, "par")
                            else:
                                self.insere_linha(pos, piloto, "zona_eliminacao_par")
                        else:
                            if self.classificacao.classificou[piloto.numero]:
                                self.insere_linha(pos, piloto, "impar")
                            else:
                                self.insere_linha(pos, piloto, "zona_eliminacao_impar")

    def formatar_tempo_classificacao(self, tempo_atual, tempo_max):
        tempo_seg = tempo_max - tempo_atual
        minutos = int(tempo_seg // 60)
        segundos = tempo_seg % 60
        return f"{minutos}:{segundos:02}"

    def abrir_janela_corrida(self):
        TelaCorrida(self)
        self.destroy()