import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3

# Função para conectar ao banco de dados
def conectar_db():
    conn = sqlite3.connect('agenda.db')
    return conn

# Função para criar a tabela (se não existir)
def criar_tabela():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contatos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        telefone TEXT NOT NULL,
        email TEXT
    )
    """)
    conn.close()

# Funções CRUD (Backend)
def adicionar_contato(nome, telefone, email):
    if not nome or not telefone:
        messagebox.showwarning("Aviso", "Nome e Telefone são obrigatórios!")
        return
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO contatos (nome, telefone, email) VALUES (?, ?, ?)",
                   (nome, telefone, email))
    conn.commit()
    conn.close()
    messagebox.showinfo("Sucesso", "Contato adicionado com sucesso!")

def visualizar_contatos():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contatos ORDER BY nome")
    contatos = cursor.fetchall()
    conn.close()
    return contatos

def atualizar_contato(id_contato, nome, telefone, email):
    if not nome or not telefone:
        messagebox.showwarning("Aviso", "Nome e Telefone são obrigatórios!")
        return
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE contatos SET nome = ?, telefone = ?, email = ? WHERE id = ?
    """, (nome, telefone, email, id_contato))
    conn.commit()
    conn.close()
    messagebox.showinfo("Sucesso", "Contato atualizado com sucesso!")

def deletar_contato(id_contato):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contatos WHERE id = ?", (id_contato,))
    conn.commit()
    conn.close()
    messagebox.showinfo("Sucesso", "Contato deletado com sucesso!")

# Interface Gráfica (Frontend)
class AgendaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Agenda de Contatos")
        self.root.geometry("700x500")

        # Frame para os campos de entrada
        frame_entradas = tk.Frame(self.root, pady=10)
        frame_entradas.pack()

        tk.Label(frame_entradas, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_nome = tk.Entry(frame_entradas, width=30)
        self.entry_nome.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_entradas, text="Telefone:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_telefone = tk.Entry(frame_entradas, width=30)
        self.entry_telefone.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame_entradas, text="Email:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.entry_email = tk.Entry(frame_entradas, width=30)
        self.entry_email.grid(row=2, column=1, padx=5, pady=5)

        # Frame para os botões
        frame_botoes = tk.Frame(self.root, pady=10)
        frame_botoes.pack()

        tk.Button(frame_botoes, text="Adicionar", command=self.adicionar).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_botoes, text="Atualizar", command=self.atualizar).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_botoes, text="Deletar", command=self.deletar).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_botoes, text="Limpar Campos", command=self.limpar_campos).pack(side=tk.LEFT, padx=5)

        # TreeView para exibir os contatos (com scrollbar)
        frame_tree = tk.Frame(self.root)
        frame_tree.pack(pady=20, padx=20, fill="both", expand=True)

        self.tree = ttk.Treeview(frame_tree, columns=("ID", "Nome", "Telefone", "Email"), show='headings')
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Telefone", text="Telefone")
        self.tree.heading("Email", text="Email")

        self.tree.column("ID", width=40)
        self.tree.column("Nome", width=200)
        self.tree.column("Telefone", width=120)
        self.tree.column("Email", width=200)

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(frame_tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind para seleção de item
        self.tree.bind("<<TreeviewSelect>>", self.ao_selecionar)

        # Atualiza a lista ao iniciar
        self.atualizar_lista_contatos()

    def atualizar_lista_contatos(self):
        # Limpa o Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Popula com dados do banco
        contatos = visualizar_contatos()
        for contato in contatos:
            self.tree.insert("", "end", values=contato)

    def adicionar(self):
        nome = self.entry_nome.get().strip()
        telefone = self.entry_telefone.get().strip()
        email = self.entry_email.get().strip() or None  # Email opcional
        adicionar_contato(nome, telefone, email)
        self.limpar_campos()
        self.atualizar_lista_contatos()

    def atualizar(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um contato para atualizar.")
            return

        id_contato = self.tree.item(selected_item, "values")[0]
        nome = self.entry_nome.get().strip()
        telefone = self.entry_telefone.get().strip()
        email = self.entry_email.get().strip() or None

        atualizar_contato(id_contato, nome, telefone, email)
        self.limpar_campos()
        self.atualizar_lista_contatos()

    def deletar(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um contato para deletar.")
            return

        if messagebox.askyesno("Confirmar", "Tem certeza que deseja deletar este contato?"):
            id_contato = self.tree.item(selected_item, "values")[0]
            deletar_contato(id_contato)
            self.limpar_campos()
            self.atualizar_lista_contatos()

    def limpar_campos(self):
        self.entry_nome.delete(0, tk.END)
        self.entry_telefone.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)

    def ao_selecionar(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return

        self.limpar_campos()
        item = self.tree.item(selected_item, "values")
        self.entry_nome.insert(0, item[1])
        self.entry_telefone.insert(0, item[2])
        if item[3]:  # Email pode ser None
            self.entry_email.insert(0, item[3])

# Inicialização da Aplicação
if __name__ == "__main__":
    criar_tabela()  # Garante que a tabela exista
    root = tk.Tk()
    app = AgendaApp(root)
    root.mainloop()
