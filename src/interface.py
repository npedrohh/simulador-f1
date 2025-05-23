import json
import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import Progressbar
import ttkbootstrap as tb
from ttkbootstrap import Window
from ttkbootstrap.widgets import Label, Button, Combobox, Frame, Treeview
from src.objetos import Piloto, Circuito, Corrida, formatar_tempo


class AppCorrida(Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("Simulador de Corrida F1")
        self.geometry("600x750")
        self.pilotos = []
        self.velocidade = 1000
        self.circuito = Circuito("Interlagos", "Brasil", "1:27.452", 70, 5, 3)

        self.create_widgets()

    def create_widgets(self):
        Label(self, text="🏁 Simulador de Corrida F1", font=("Arial", 16, "bold")).pack(pady=10)

        # Botões para carregar dados do .json e simular a corrida com esses dados
        Button(self, text="1. Carregar Pilotos", command=self.carregar_pilotos, width=30).pack(pady=5)
        Button(self, text="2. Simular Corrida", command=self.simular_corrida, width=30).pack(pady=5)

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

    def carregar_pilotos(self):
        try:
            with open("pilotos.json", "r", encoding="utf-8") as f:
                dados = json.load(f)
                self.pilotos = [Piloto(**p) for p in dados]
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar pilotos: {e}")

    def simular_corrida(self):
        if not self.pilotos:
            messagebox.showwarning("Aviso", "Carregue os pilotos primeiro.")
            return

        self.corrida = Corrida(self.circuito, self.pilotos)
        self.corrida.volta_atual = 0
        self.simular_proxima_volta()

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

        velocidade_map = {
            "Muito lento": 1600,
            "Lento": 1300,
            "Normal": 1000,
            "Rápido": 600,
            "Muito rápido": 300,
            "Ultra rápido": 50
        }
        self.velocidade = velocidade_map.get(self.velocidade_var.get(), 1000)
        self.after(self.velocidade, self.simular_proxima_volta)

    def insere_linha(self, pos, piloto, tag):
        if tag == "abandonou":
            self.tree.insert("", "end", values=(
                f"{pos}º",
                f"{piloto.nome_completo()}",
                piloto.equipe,
                "DNF",
                "Acidente",
                "-"
            ), tags=tag)
        elif tag == "primeiro":
            self.tree.insert("", "end", values=(
                f"{pos}º",
                f"{piloto.nome_completo()}",
                piloto.equipe,
                formatar_tempo(piloto.voltas[-1]),
                "Líder",
                "-"
            ), tags=tag)
        else:
            self.tree.insert("", "end", values=(
                f"{pos}º",
                f"{piloto.nome_completo()}",
                piloto.equipe,
                formatar_tempo(piloto.voltas[-1]),
                piloto.delta_prox_formatado(),
                piloto.delta_lider_formatado()
            ), tags=tag)

    def atualiza_tabela(self, tabela):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for pos, (piloto, tempo) in enumerate(tabela, start=1):
            if piloto.abandonou:
                self.insere_linha(pos, piloto, "abandonou")
            else:
                match pos:
                    case 1:
                        self.insere_linha(pos, piloto, "primeiro")

                    case 2:
                        self.insere_linha(pos, piloto, "segundo")

                    case 3:
                        self.insere_linha(pos, piloto, "terceiro")

                    case _:
                        if pos % 2 == 0:
                            self.insere_linha(pos, piloto, "par")

                        else:
                            self.insere_linha(pos, piloto, "impar")