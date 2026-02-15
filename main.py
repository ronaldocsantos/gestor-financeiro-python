import customtkinter as ctk
from tkinter import messagebox, ttk
import pandas as pd
from datetime import datetime
import os
import csv
from fpdf import FPDF

# Configurações de aparência
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

ARQUIVO_CSV = 'minhas_despesas.csv'
CATEGORIAS = sorted([
    "Aluguéis e Condomínios", "Conta de Luz", "Conta de Água",
    "Material de Escritório", "Materiais de uso e consumo", "Seguro",
    "Despesas com vigilância", "Estacionamento", "Pedágio",
    "Alimentação", "Representações", "Prestação de serviço", "Combustiveis", "Fármacia", "Cartao de credito"
])


class AppFinanceiro(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurações de Aparência Global
        ctk.set_appearance_mode("light")  # Estilo Apple é predominantemente claro

        self.title("Gestor Financeiro Pro")
        self.geometry("900x850")
        self.configure(fg_color="#F5F5F7")  # Fundo cinza suave típico da Apple

        # --- CABEÇALHO ---
        self.label_titulo = ctk.CTkLabel(
            self,
            text="Projeto Mensal",
            font=("SF Pro Display", 24, "bold"),  # San Francisco é a fonte da Apple
            text_color="#1D1D1F"
        )
        self.label_titulo.pack(pady=(20, 10), padx=30, anchor="w")

        # --- DASHBOARD (CARD DE RESUMO) ---
        self.frame_dash = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=20,
            border_width=1,
            border_color="#E5E5E7"
        )
        self.frame_dash.pack(pady=10, padx=30, fill="x")

        self.label_meta = ctk.CTkLabel(
            self.frame_dash,
            text="Total Gasto em Fevereiro",
            font=("SF Pro Text", 14),
            text_color="#86868B"
        )
        self.label_meta.pack(pady=(15, 0), padx=20, anchor="w")

        self.label_resumo = ctk.CTkLabel(
            self.frame_dash,
            text="R$ 718,97",
            font=("SF Pro Display", 36, "bold"),
            text_color="#1D1D1F"
        )
        self.label_resumo.pack(pady=(0, 15), padx=20, anchor="w")

        # --- CORPO PRINCIPAL ---
        self.corpo = ctk.CTkFrame(self, fg_color="transparent")
        self.corpo.pack(pady=10, padx=30, fill="both", expand=True)

        # LADO ESQUERDO: CADASTRO (CARD)
        self.lado_esq = ctk.CTkFrame(
            self.corpo,
            fg_color="white",
            corner_radius=20,
            width=320,
            border_width=1,
            border_color="#E5E5E7"
        )
        self.lado_esq.pack(side="left", fill="y", padx=(0, 10))
        self.lado_esq.pack_propagate(False)

        ctk.CTkLabel(
            self.lado_esq,
            text="NOVA DESPESA",
            font=("SF Pro Text", 13, "bold"),
            text_color="#1D1D1F"
        ).pack(pady=(20, 15))

        # Inputs com estilo minimalista
        input_kwargs = {
            "width": 260,
            "height": 45,
            "corner_radius": 12,
            "border_color": "#E5E5E7",
            "fg_color": "#F5F5F7",
            "text_color": "#1D1D1F",
            "placeholder_text_color": "#86868B"
        }

        self.entry_data = ctk.CTkEntry(self.lado_esq, placeholder_text="Data: DD/MM/AAAA", **input_kwargs)
        self.entry_data.pack(pady=8)
        self.entry_data.bind("<KeyRelease>", self.formatar_data)

        self.combo_categoria = ctk.CTkOptionMenu(
            self.lado_esq,
            values=CATEGORIAS,
            width=260,
            height=45,
            corner_radius=12,
            fg_color="#F5F5F7",
            button_color="#F5F5F7",
            button_hover_color="#E5E5E7",
            text_color="#1D1D1F",
            dropdown_fg_color="white"
        )
        self.combo_categoria.set("Selecione a Categoria")
        self.combo_categoria.pack(pady=8)

        self.entry_valor = ctk.CTkEntry(self.lado_esq, placeholder_text="Valor (Ex: 150.50)", **input_kwargs)
        self.entry_valor.pack(pady=8)

        self.entry_obs = ctk.CTkEntry(self.lado_esq, placeholder_text="Histórico", **input_kwargs)
        self.entry_obs.pack(pady=8)

        self.btn_salvar = ctk.CTkButton(
            self.lado_esq,
            text="Salvar Despesa",
            command=self.salvar,
            fg_color="#34C759",  # Verde Apple
            hover_color="#28A745",
            font=("SF Pro Text", 15, "bold"),
            height=50,
            width=260,
            corner_radius=15
        )
        self.btn_salvar.pack(pady=25)

        # LADO DIREITO: LANÇAMENTOS
        self.lado_dir = ctk.CTkFrame(self.corpo, fg_color="white", corner_radius=20, border_width=1,
                                     border_color="#E5E5E7")
        self.lado_dir.pack(side="right", fill="both", expand=True)

        ctk.CTkLabel(
            self.lado_dir,
            text="LANÇAMENTOS",
            font=("SF Pro Text", 13, "bold"),
            text_color="#1D1D1F"
        ).pack(pady=(20, 10))

        # Estilo da Tabela para modo claro
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background="white",
            foreground="#1D1D1F",
            fieldbackground="white",
            rowheight=40,
            font=("SF Pro Text", 11),
            borderwidth=0
        )
        style.configure("Treeview.Heading", font=("SF Pro Text", 11, "bold"), background="#F5F5F7", borderwidth=0)
        style.map("Treeview", background=[('selected', '#E8F2FF')], foreground=[('selected', '#007AFF')])

        self.tabela = ttk.Treeview(self.lado_dir, columns=("Data", "Categoria", "Valor"), show='headings')
        self.tabela.heading("Data", text="DATA")
        self.tabela.heading("Categoria", text="CATEGORIA")
        self.tabela.heading("Valor", text="VALOR")
        self.tabela.pack(pady=10, padx=20, fill="both", expand=True)

        self.btn_excluir = ctk.CTkButton(
            self.lado_dir,
            text="Excluir Selecionado",
            fg_color="transparent",
            text_color="#FF3B30",  # Vermelho Apple
            hover_color="#FFF1F0",
            command=self.excluir_item,
            font=("SF Pro Text", 12, "bold")
        )
        self.btn_excluir.pack(pady=15)

        # --- RODAPÉ: RELATÓRIOS ---

        # --- RODAPÉ: RELATÓRIOS ---
        self.frame_rel = ctk.CTkFrame(self)
        self.frame_rel.pack(pady=10, padx=20, fill="x")

        # ADICIONE ESTE TÍTULO AQUI:
        self.label_rel_titulo = ctk.CTkLabel(self.frame_rel, text="GERAR RELATÓRIO POR PERÍODO",
                                             font=("Arial", 14, "bold"))
        self.label_rel_titulo.pack(pady=(10, 5))  # Dá um espaçamento maior em cima

        # Crie um sub-frame para os botões e campos ficarem na mesma linha
        self.frame_campos_rel = ctk.CTkFrame(self.frame_rel, fg_color="transparent")
        self.frame_campos_rel.pack(pady=5, padx=10, fill="x")

        # Mova os campos de data e botões para dentro desse frame_campos_rel
        self.data_ini = ctk.CTkEntry(self.frame_campos_rel, placeholder_text="Início (DD/MM/AAAA)", width=120)
        self.data_ini.pack(side="left", padx=5, pady=10)
        self.data_ini.bind("<KeyRelease>", lambda e: self.formatar_data(e, "ini"))

        self.data_fim = ctk.CTkEntry(self.frame_campos_rel, placeholder_text="Fim (DD/MM/AAAA)", width=120)
        self.data_fim.pack(side="left", padx=5, pady=10)
        self.data_fim.bind("<KeyRelease>", lambda e: self.formatar_data(e, "fim"))

        # Botões alinhados à direita                          Este código cria o botão visualmente
        self.btn_pasta = ctk.CTkButton(self.frame_campos_rel, text="📂 ABRIR PASTA", width=80,
                                       fg_color="#7f8c8d", command=self.abrir_pasta_relatorios)
        self.btn_pasta.pack(side="right", padx=5)

        self.btn_xlsx = ctk.CTkButton(self.frame_campos_rel, text="Excel", width=80,
                                      command=lambda: self.gerar_relatorio("excel"))
        self.btn_xlsx.pack(side="right", padx=5)

        self.btn_pdf = ctk.CTkButton(self.frame_campos_rel, text="PDF", width=80,
                                     command=lambda: self.gerar_relatorio("pdf"))
        self.btn_pdf.pack(side="right", padx=5)


        self.atualizar_interface()

    # --- LÓGICA: DATA AUTOMÁTICA ---
    def formatar_data(self, event, campo="cadastro"):
        if event.keysym == "BackSpace": return

        if campo == "cadastro":
            widget = self.entry_data
        elif campo == "ini":
            widget = self.data_ini
        else:
            widget = self.data_fim

        texto = widget.get().replace("/", "")
        novo_texto = ""

        if len(texto) >= 2: novo_texto += texto[:2] + "/"
        if len(texto) >= 4: novo_texto += texto[2:4] + "/"
        if len(texto) >= 4:
            novo_texto += texto[4:8]
        else:
            novo_texto += texto[2:]

        if len(widget.get()) in [2, 5]:
            widget.delete(0, 'end')
            widget.insert(0, novo_texto)

    # --- LÓGICA: DASHBOARD E TABELA ---
    def atualizar_interface(self):
        # 1. Limpa a tabela antes de preencher
        for i in self.tabela.get_children():
            self.tabela.delete(i)

        if not os.path.exists(ARQUIVO_CSV):
            return

        # 2. Tenta ler o arquivo
        try:
            df = pd.read_csv(ARQUIVO_CSV)
        except:
            return

        # 3. BLOCO DA DASHBOARD (Onde estava o erro de sintaxe)
        try:
            # Converte a coluna de data para cálculos
            df['Data_Obj'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')

            # Dicionário de tradução
            meses_pt = {
                "January": "Janeiro", "February": "Fevereiro", "March": "Março",
                "April": "Abril", "May": "Maio", "June": "Junho",
                "July": "Julho", "August": "Agosto", "September": "Setembro",
                "October": "Outubro", "November": "Novembro", "December": "Dezembro"
            }

            agora = datetime.now()
            mes_nome_en = agora.strftime('%B')
            mes_nome_pt = meses_pt.get(mes_nome_en, mes_nome_en)

            # Filtra e soma o mês atual
            mascara_mes = (df['Data_Obj'].dt.month == agora.month) & (df['Data_Obj'].dt.year == agora.year)
            total_mes = df[mascara_mes]['Valor'].sum()

            # Atualiza o texto na tela
            self.label_resumo.configure(text=f"Total Gasto em {mes_nome_pt}: R$ {total_mes:.2f}")

        except Exception as e:
            # Se algo der errado no cálculo, ele apenas ignora e não trava o programa
            print(f"Erro ao calcular dashboard: {e}")

        # 4. PREENCHER TABELA (Últimas 15 despesas)
        # Este bloco deve estar alinhado com o 'try' lá de cima
        for _, row in df.tail(15).iterrows():
            self.tabela.insert("", "end", values=(row['Data'], row['Tipo de Despesa'], f"{float(row['Valor']):.2f}"))

    def salvar(self):
        data = self.entry_data.get()
        cat = self.combo_categoria.get()
        valor = self.entry_valor.get().replace(',', '.')
        obs = self.entry_obs.get()

        if len(data) < 10 or cat == "Selecione a Categoria" or not valor:
            messagebox.showwarning("Erro", "Preencha todos os campos corretamente!")
            return

        arquivo_existe = os.path.isfile(ARQUIVO_CSV)
        with open(ARQUIVO_CSV, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not arquivo_existe: writer.writerow(['Data', 'Tipo de Despesa', 'Valor', 'Historico'])
            writer.writerow([data, cat, valor, obs])

        self.entry_valor.delete(0, 'end');
        self.entry_obs.delete(0, 'end');
        self.entry_data.delete(0, 'end')
        self.atualizar_interface()
        messagebox.showinfo("Sucesso", "Dados salvos!")

    def excluir_item(self):
        selecionado = self.tabela.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um item na tabela para excluir!")
            return

        item_values = self.tabela.item(selecionado)['values']
        df = pd.read_csv(ARQUIVO_CSV)

        # Filtra o dataframe removendo o item que bate com os valores selecionados
        df = df[~((df['Data'] == str(item_values[0])) &
                  (df['Tipo de Despesa'] == str(item_values[1])) &
                  (df['Valor'] == float(item_values[2])))]

        df.to_csv(ARQUIVO_CSV, index=False)
        self.atualizar_interface()
        messagebox.showinfo("Excluído", "Registro removido com sucesso!")

    def abrir_pasta_relatorios(self):
        # Pega o caminho da pasta onde o programa está rodando
        caminho_atual = os.getcwd()
        try:
            os.startfile(caminho_atual)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir a pasta: {e}")

    def gerar_relatorio(self, formato):
        if not os.path.exists(ARQUIVO_CSV):
            messagebox.showwarning("Aviso", "Não há dados para gerar relatório.")
            return

        data_hora = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_arquivo = f"Relatorio_Contabil_{data_hora}.pdf"
        caminho_final = os.path.abspath(nome_arquivo)

        try:
            # 1. Carrega os dados
            df = pd.read_csv(ARQUIVO_CSV)

            # --- FILTRO DE DATAS ---
            data_inicio_str = self.data_ini.get()
            data_fim_str = self.data_fim.get()

            # Converte as datas do CSV para um formato que o Python entenda para comparar
            df['Data_Conv'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')

            # Se o usuário preencheu as datas de filtro, aplicamos a "peneira"
            if data_inicio_str and data_fim_str:
                try:
                    dt_ini = pd.to_datetime(data_inicio_str, format='%d/%m/%Y')
                    dt_fim = pd.to_datetime(data_fim_str, format='%d/%m/%Y')

                    # Mantém no relatório apenas o que estiver entre as datas
                    df = df[(df['Data_Conv'] >= dt_ini) & (df['Data_Conv'] <= dt_fim)]
                    # Ordena o relatório por data para ficar organizado
                    df = df.sort_values(by='Data_Conv')
                except:
                    messagebox.showerror("Erro", "Formato de data inválido nos filtros! Use DD/MM/AAAA")
                    return

            if df.empty:
                messagebox.showinfo("Aviso", "Nenhuma despesa encontrada para o período selecionado.")
                return
            # -----------------------

            if formato == "pdf":
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", "B", 16)
                pdf.cell(190, 10, "RELATÓRIO DE DESPESAS - CONTABILIDADE", ln=True, align="C")

                # Se houver filtro, mostra o período no topo do PDF
                if data_inicio_str and data_fim_str:
                    pdf.set_font("Arial", "", 10)
                    pdf.cell(190, 10, f"Período: {data_inicio_str} até {data_fim_str}", ln=True, align="C")

                pdf.ln(5)

                # Cabeçalho da Tabela
                pdf.set_font("Arial", "B", 10)
                pdf.cell(25, 10, "Data", 1)
                pdf.cell(50, 10, "Categoria", 1)
                pdf.cell(85, 10, "Historico", 1)
                pdf.cell(30, 10, "Valor (R$)", 1)
                pdf.ln()

                # Dados (Loop para preencher as linhas)
                pdf.set_font("Arial", size=9)
                for _, row in df.iterrows():
                    pdf.cell(25, 10, str(row['Data']), 1)
                    pdf.cell(50, 10, str(row['Tipo de Despesa'])[:25], 1)
                    pdf.cell(85, 10, str(row['Historico'])[:45], 1)
                    pdf.cell(30, 10, f"{float(row['Valor']):.2f}", 1)
                    pdf.ln()

                # 2. Calcula a soma total apenas dos itens filtrados
                total_geral = df['Valor'].sum()

                # 3. Linha do Total (Fora do loop!)
                pdf.set_font("Arial", "B", 10)
                pdf.set_fill_color(200, 200, 200)
                pdf.cell(160, 10, "VALOR TOTAL ACUMULADO NO PERÍODO:", 1, 0, "R", fill=True)
                pdf.cell(30, 10, f"R$ {total_geral:.2f}", 1, 1, "C", fill=True)

                # 4. Salva e abre o arquivo
                pdf.output(caminho_final)
                os.startfile(caminho_final)
                messagebox.showinfo("Sucesso", "Relatório Contábil gerado com sucesso!")

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar relatório: {e}")

if __name__ == "__main__":
    app = AppFinanceiro()
    app.mainloop()

    # instale no terminal o pip install pyinstaller, depois no terminal pyinstaller -w nome_do_software
    # O CustomTkinter e o Pandas precisam que o PyInstaller saiba onde eles estão. Use este comando específico
    #python -m PyInstaller --onefile --noconsole --clean --collect-all customtkinter --collect-all matplotlib main.py