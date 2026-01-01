import os
import threading
import time
import sqlite3
import datetime
import requests
import collections
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox
from mnemonic import Mnemonic
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes, Bip84, Bip84Coins
from stem import Signal
from stem.control import Controller

# --- NOVAS IMPORTAÇÕES PARA O TRAY ---
import pystray
from PIL import Image, ImageDraw

# --- CONFIGURAÇÕES DE AMBIENTE ---
FOLDER_PATH = r"C:\Users\Pichau\Desktop\ServerCoin"
DB_NAME = os.path.join(FOLDER_PATH, "msr_hunter.db")

# GLOBAIS DE CONTROLE
manual_queue = collections.deque()
current_delay = 1.0 
current_bip_mode = "BIP44"
total_scanned = 0
total_found = 0
current_tor_ip = "Verificando..."
active_provider = "Iniciando..."

# Configuração Proxy Tor (Tor Browser padrão)
tor_proxy = {'http': 'socks5h://127.0.0.1:9150', 'https': 'socks5h://127.0.0.1:9150'}

# --- FUNÇÕES DE REDE E TOR ---

def get_current_ip():
    global current_tor_ip
    try:
        res = requests.get("https://ident.me", proxies=tor_proxy, timeout=10)
        current_tor_ip = res.text.strip()
    except: current_tor_ip = "Tor Off"

def renew_tor_ip():
    global active_provider
    try:
        with Controller.from_port(port=9151) as controller:
            controller.authenticate()
            controller.signal(Signal.NEWNYM)
            active_provider = "🔄 IP RENOVADO"
            time.sleep(5)
            get_current_ip()
    except: active_provider = "⚠️ TOR CONTROL OFF"

def fetch_balance(address):
    providers = [
        ("Blockchain.info", f"https://blockchain.info/rawaddr/{address}"),
        ("BlockCypher", f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/balance"),
        ("Blockchair", f"https://api.blockchair.com/bitcoin/dashboards/address/{address}")
    ]
    for name, url in providers:
        try:
            res = requests.get(url, timeout=12, proxies=tor_proxy)
            if res.status_code == 200:
                data = res.json()
                if name == "Blockchain.info": return data.get("final_balance", 0) / 100_000_000, name
                if name == "BlockCypher": return data.get("balance", 0) / 100_000_000, name
                if name == "Blockchair": return data["data"][address]["address"]["balance"] / 100_000_000, name
            if res.status_code == 429: continue
        except: continue
    return -1, "LIMIT"

# --- WORKER DE BUSCA ---

def wallet_worker():
    global total_scanned, total_found, active_provider
    mnemo = Mnemonic("english")
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    
    while True:
        mode = current_bip_mode
        is_man = len(manual_queue) > 0
        words = manual_queue.popleft() if is_man else mnemo.generate(strength=128)
        
        try:
            seed_bytes = Bip39SeedGenerator(words).Generate()
            if mode == "BIP84":
                address = Bip84.FromSeed(seed_bytes, Bip84Coins.BITCOIN).Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0).PublicKey().ToAddress()
            else:
                address = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN).Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0).PublicKey().ToAddress()
            
            balance, api_name = fetch_balance(address)
            
            if balance == -1:
                renew_tor_ip()
                continue

            total_scanned += 1
            active_provider = api_name
            now = datetime.datetime.now().strftime("%H:%M:%S")
            
            cur = conn.cursor()
            cur.execute("INSERT INTO scan_log (api_name, tech, public_key, seed, balance, last_update, is_manual) VALUES (?,?,?,?,?,?,?)",
                        (api_name, mode, address, words, balance, now, 1 if is_man else 0))
            
            if balance > 0:
                total_found += 1
                cur.execute("INSERT INTO found_keys (api_name, tech, public_key, seed, balance, last_update) VALUES (?,?,?,?,?,?)",
                           (api_name, mode, address, words, balance, now))
            conn.commit()
            
        except: pass
        time.sleep(current_delay)

# --- INTERFACE GRÁFICA ---

class HunterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MSR Wallet Hunter v10.2")
        self.root.geometry("1500x900")
        self.root.configure(bg="#0a0a0a")

        # Configuração do Tray Icon
        self.setup_tray()
        # Interceptar o evento de minimizar
        self.root.bind("<Unmap>", self.on_minimize)

        # --- ESTILO ---
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#1a1a1a", foreground="white", fieldbackground="#1a1a1a", rowheight=25)
        style.configure("Treeview.Heading", background="#333", foreground="white", font=("Arial", 9, "bold"))

        # Painel Stats
        top = tk.Frame(self.root, bg="#111", pady=15)
        top.pack(fill=tk.X)
        self.lbl_scan = tk.Label(top, text="VARREDURAS: 0", fg="#3498db", bg="#111", font=("Consolas", 18, "bold"))
        self.lbl_scan.pack(side=tk.LEFT, padx=30)
        self.lbl_found = tk.Label(top, text="ACHADOS: 0", fg="#2ecc71", bg="#111", font=("Consolas", 18, "bold"))
        self.lbl_found.pack(side=tk.LEFT, padx=30)
        
        # Painel de Comandos
        cmd = tk.Frame(self.root, bg="#1a1a1a", pady=10)
        cmd.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(cmd, text="INJETAR SEED/KEY:", fg="#aaa", bg="#1a1a1a").pack(side=tk.LEFT, padx=5)
        self.ent_seed = tk.Entry(cmd, width=35, bg="#262626", fg="white", borderwidth=0)
        self.ent_seed.pack(side=tk.LEFT, padx=5)
        tk.Button(cmd, text="INJETAR", bg="#2980b9", fg="white", command=self.add_manual).pack(side=tk.LEFT, padx=5)
        
        self.bip_var = tk.StringVar(value="BIP44")
        self.bip_menu = ttk.Combobox(cmd, textvariable=self.bip_var, values=["BIP44", "BIP84"], width=8, state="readonly")
        self.bip_menu.pack(side=tk.LEFT, padx=5)
        self.bip_menu.bind("<<ComboboxSelected>>", self.update_bip_mode)

        self.speed = tk.Scale(cmd, from_=0.0, to=5.0, resolution=0.1, orient=tk.HORIZONTAL, bg="#1a1a1a", fg="white", command=self.set_delay)
        self.speed.set(1.0)
        self.speed.pack(side=tk.LEFT, padx=15)
        
        self.lbl_ip = tk.Label(cmd, text="IP: --", fg="#e67e22", bg="#1a1a1a", font=("Consolas", 10))
        self.lbl_ip.pack(side=tk.RIGHT, padx=10)
        
        self.lbl_api = tk.Label(cmd, text="FONTE: ---", fg="#f1c40f", bg="#1a1a1a", font=("Consolas", 10))
        self.lbl_api.pack(side=tk.RIGHT, padx=10)
        
        tk.Button(cmd, text="LIMPAR LOG", bg="#c0392b", fg="white", command=self.clear_logs).pack(side=tk.RIGHT, padx=5)

        # Tabelas
        self.cols = ("api", "tech", "key", "seed", "bal", "time", "link")
        self.tree_logs = self.create_tree(self.root, "VARREDURA EM TEMPO REAL (AZUL = MANUAL)", 18)
        self.tree_found = self.create_tree(self.root, "CARTEIRAS COM SALDO IDENTIFICADO", 8)

        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Copiar dado", command=self.copy_cell)

        self.refresh_ui()

    # --- LÓGICA DO TRAY ---
    def setup_tray(self):
        # Cria uma imagem simples para o ícone (Círculo azul)
        image = Image.new('RGB', (64, 64), color='#1a1a1a')
        d = ImageDraw.Draw(image)
        d.ellipse((10, 10, 54, 54), fill='#3498db')
        
        menu = pystray.Menu(
            pystray.MenuItem('Abrir Hunter', self.restore_from_tray, default=True),
            pystray.MenuItem('Sair', self.quit_app)
        )
        self.tray_icon = pystray.Icon("MSR Hunter", image, "MSR Hunter Iniciando...", menu)
        # Rodar o tray em uma thread separada para não travar o Tkinter
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def on_minimize(self, event):
        if self.root.state() == 'iconic':
            self.root.withdraw() # Esconde a janela da barra de tarefas

    def restore_from_tray(self, icon=None, item=None):
        self.root.deiconify()
        self.root.state('normal')
        self.root.focus_force()

    def quit_app(self, icon, item):
        self.tray_icon.stop()
        self.root.quit()

    # --- MÉTODOS AUXILIARES ---
    def create_tree(self, parent, title, height):
        tk.Label(parent, text=title, bg="#0a0a0a", fg="#555", font=("Arial", 9, "bold")).pack()
        f = tk.Frame(parent, bg="#0a0a0a")
        f.pack(fill=tk.BOTH, expand=True, padx=15, pady=2)
        t = ttk.Treeview(f, columns=self.cols, show="headings", height=height)
        h_names = ["API Utilizada", "Tecnologia", "Public Key", "Seed / Private Key", "Saldo BTC", "Update", "Explorer"]
        w_sizes = [110, 100, 240, 400, 100, 90, 90]
        for c, h, w in zip(self.cols, h_names, w_sizes):
            t.heading(c, text=h)
            t.column(c, width=w, anchor="center")
        t.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        t.bind("<Button-3>", self.show_menu)
        t.bind("<Double-1>", self.open_link)
        t.tag_configure("manual", foreground="#3498db", font=("Arial", 9, "bold"))
        return t

    def update_bip_mode(self, e): 
        global current_bip_mode
        current_bip_mode = self.bip_var.get()

    def set_delay(self, v): 
        global current_delay
        current_delay = float(v)
    
    def show_menu(self, e):
        row = e.widget.identify_row(e.y)
        if row:
            e.widget.selection_set(row)
            self.last_tree = e.widget
            self.last_col = int(e.widget.identify_column(e.x).replace('#','')) - 1
            self.menu.post(e.x_root, e.y_root)

    def copy_cell(self):
        item = self.last_tree.selection()[0]
        val = self.last_tree.item(item)['values'][self.last_col]
        self.root.clipboard_clear()
        self.root.clipboard_append(str(val))

    def open_link(self, e):
        if e.widget.identify_column(e.x) == "#7":
            addr = e.widget.item(e.widget.selection()[0])['values'][2]
            webbrowser.open(f"https://blockchair.com/bitcoin/address/{addr}")

    def add_manual(self):
        raw = self.ent_seed.get().strip().replace(',', ' ').replace('.', ' ')
        parts = raw.split()
        if len(parts) >= 12 or (len(parts) == 1 and len(parts[0]) > 30):
            manual_queue.append(" ".join(parts))
            self.ent_seed.delete(0, tk.END)
            messagebox.showinfo("Fila", "Adicionado com sucesso!")
        else: messagebox.showwarning("Erro", "Formato inválido.")

    def clear_logs(self):
        conn = sqlite3.connect(DB_NAME)
        conn.execute("DELETE FROM scan_log")
        conn.commit()
        conn.close()

    def refresh_ui(self):
        self.lbl_scan.config(text=f"VARREDURAS: {total_scanned}")
        self.lbl_found.config(text=f"ACHADOS: {total_found}")
        self.lbl_ip.config(text=f"IP: {current_tor_ip}")
        self.lbl_api.config(text=f"FONTE: {active_provider}")
        
        # ATUALIZAÇÃO DO TOOLTIP DO TRAY
        if hasattr(self, 'tray_icon'):
            self.tray_icon.title = f"MSR Hunter\nVARREDURAS: {total_scanned}\nACHADOS: {total_found}"
        
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        
        cur.execute("SELECT api_name, tech, public_key, seed, balance, last_update, is_manual FROM scan_log ORDER BY id DESC LIMIT 100")
        self.tree_logs.delete(*self.tree_logs.get_children())
        for r in cur.fetchall():
            tag = "manual" if r[6] == 1 else ""
            self.tree_logs.insert("", "end", values=(r[0], r[1], r[2], r[3], f"{r[4]:.8f}", r[5], "🔗 ABRIR"), tags=(tag,))

        cur.execute("SELECT api_name, tech, public_key, seed, balance, last_update FROM found_keys ORDER BY id DESC")
        self.tree_found.delete(*self.tree_found.get_children())
        for r in cur.fetchall():
            self.tree_found.insert("", "end", values=(r[0], r[1], r[2], r[3], f"{r[4]:.8f}", r[5], "🔗 ABRIR"))
            
        conn.close()
        self.root.after(3500, self.refresh_ui)

# --- INICIALIZAÇÃO ---

def init_db():
    if not os.path.exists(FOLDER_PATH): os.makedirs(FOLDER_PATH)
    conn = sqlite3.connect(DB_NAME)
    conn.execute('''CREATE TABLE IF NOT EXISTS scan_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT, api_name TEXT, tech TEXT, public_key TEXT, 
        seed TEXT, balance REAL, last_update TEXT, is_manual INTEGER)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS found_keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT, api_name TEXT, tech TEXT, public_key TEXT, 
        seed TEXT, balance REAL, last_update TEXT)''')
    
    colunas = [("scan_log", "api_name", "TEXT"), ("scan_log", "tech", "TEXT"), 
               ("scan_log", "is_manual", "INTEGER"), ("found_keys", "api_name", "TEXT"), ("found_keys", "tech", "TEXT")]
    for tab, col, tipo in colunas:
        try: conn.execute(f"ALTER TABLE {tab} ADD COLUMN {col} {tipo}")
        except: pass
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    get_current_ip()
    for _ in range(30): threading.Thread(target=wallet_worker, daemon=True).start()
    root = tk.Tk()
    app = HunterApp(root)
    root.mainloop()