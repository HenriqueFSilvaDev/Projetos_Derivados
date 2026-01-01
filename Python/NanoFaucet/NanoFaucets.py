import os
import threading
import time
import sqlite3
import datetime
import json
import hashlib
import requests
import tkinter as tk
from tkinter import ttk, messagebox
from stem import Signal
from stem.control import Controller
from playwright.sync_api import sync_playwright
from bip_utils import Bip44, Bip44Coins
import nacl.signing
import nacl.encoding

# --- CONFIGURAÇÕES ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FOLDER_PATH = os.path.join(BASE_DIR, "MSR_Nano_Data")
DB_NAME = os.path.join(FOLDER_PATH, "msr_nano_final.db")
CONFIG_FILE = os.path.join(FOLDER_PATH, "config.json")
TOR_PROXY_ADDR = "socks5://127.0.0.1:9150"

RPC_NODES = [
    "https://proxy.nanos.cc/proxy",
    "https://rpc.nano.to"
]

# GLOBAIS
is_running = False
current_tor_ip = "Aguardando..."
status_msg = "Desligado"
next_index = 0

# --- 1. FUNÇÕES DE APOIO ---

def get_keys(seed_hex, index):
    try:
        seed_bytes = bytes.fromhex(seed_hex)
        bip44_mst = Bip44.FromSeed(seed_bytes, Bip44Coins.NANO)
        bip44_acc = bip44_mst.Purpose().Coin().Account(index)
        
        address = bip44_acc.PublicKey().ToAddress()
        priv_hex = bip44_acc.PrivateKey().Raw().ToHex()
        
        # SOLUÇÃO DEFINITIVA: Derivar a PubKey via nacl (Ed25519)
        # Isso evita erros de atributo no bip_utils
        priv_bytes = bytes.fromhex(priv_hex)
        signing_key = nacl.signing.SigningKey(priv_bytes)
        pub_key = signing_key.verify_key.encode(encoder=nacl.encoding.HexEncoder).decode()
        
        return address, priv_hex, pub_key
    except Exception as e:
        print(f"[ERRO CHAVES] {e}")
        return None, None, None

def solve_pow(hash_hex):
    print(f"[POW] Calculando para: {hash_hex}")
    target = int("fffffe0000000000", 16)
    hash_bytes = bytes.fromhex(hash_hex)
    nonce = 0
    while is_running:
        nonce_bytes = nonce.to_bytes(8, byteorder='little')
        attempt = hashlib.blake2b(nonce_bytes + hash_bytes, digest_size=8).digest()
        if int.from_bytes(attempt, byteorder='little') >= target:
            return nonce_bytes.hex()
        nonce += 1
        if nonce % 500000 == 0: time.sleep(0.001)
    return None

def renew_tor_ip():
    print("[TOR] Solicitando novo IP...")
    try:
        with Controller.from_port(port=9151) as ctrl:
            ctrl.authenticate()
            ctrl.signal(Signal.NEWNYM)
        # Aumentamos para 10 segundos para o circuito estabilizar
        time.sleep(10) 
        proxies = {'http': 'socks5h://127.0.0.1:9150', 'https': 'socks5h://127.0.0.1:9150'}
        # Usamos socks5h (o 'h' faz o DNS ser resolvido pelo Tor, evitando o erro de addrinfo)
        ip = requests.get("https://ident.me", proxies=proxies, timeout=15).text.strip()
        print(f"[TOR] Novo IP estável: {ip}")
        return ip
    except Exception as e:
        print(f"[TOR ERRO] Circuito instável: {e}")
        return "Erro Tor"

def update_db(idx, addr, bal, status):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("INSERT OR REPLACE INTO multi_history (idx, address, balance, status, time) VALUES (?,?,?,?,?)",
                 (idx, addr, bal, status, datetime.datetime.now().strftime("%H:%M:%S")))
    conn.commit()
    conn.close()

# --- 2. MOTOR SÍNCRONO (UM POR UM) ---

def main_sync_engine(seed_hex):
    global next_index, status_msg, current_tor_ip, is_running
    
    while is_running:
        idx = next_index
        addr, priv, pub_key = get_keys(seed_hex, idx)
        
        if not addr:
            print(f"[FALHA] Erro Crítico ao gerar chaves para #{idx}")
            next_index += 1
            continue

        print(f"\n--- [INICIANDO CICLO CONTA #{idx}] ---")
        print(f"Endereço: {addr}")
        
        # 1. TROCA DE IP
        status_msg = f"#{idx}: Renovando IP Tor..."
        current_tor_ip = renew_tor_ip()
        
        # 2. PROCESSO HUNTER (CLAIM)
        print(f"[HUNTER] Acessando sites de faucet...")
        status_msg = f"#{idx}: Fazendo Claims..."
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=False)
                context = browser.new_context(proxy={"server": TOR_PROXY_ADDR})
                page = context.new_page()                
                print(f"  > Solicitando no FreeNanoFaucet...")
                page.goto("https://freenanofaucet.com/faucet", wait_until="load", timeout=60000)
                if page.locator("input[name='address']").is_visible():
                    page.fill("input[name='address']", addr)
                    page.click("#getNano")
                    time.sleep(10)
                
                print(f"  > Solicitando no NanSwap...")
                page.goto("https://nanswap.com/nano-faucet", wait_until="load", timeout=60000)
                page.fill("input[placeholder*='nano_']", addr)
                time.sleep(10)
                
                browser.close()
                print("[HUNTER] Claims finalizados.")
            except Exception as e:
                print(f"[HUNTER FALHOU] Erro na automação: {e}")
                if 'browser' in locals(): browser.close()

        # 3. VALIDAÇÃO SÍNCRONA (RECEIVER)
        print(f"[RECEIVER] Validando rede para #{idx}...")
        status_msg = f"#{idx}: Validando Rede..."
        
        success = False
        bal_final = 0.0
        proxies = {'http': "socks5h://127.0.0.1:9150", 'https': "socks5h://127.0.0.1:9150"}
        
        try:
            for rpc in RPC_NODES:
                print(f"  > Consultando nó RPC: {rpc}")
                try:
                    res = requests.post(rpc, json={"action": "pending", "account": addr, "count": "1"}, 
                                        proxies=proxies, timeout=15).json()
                    
                    if "blocks" in res and res["blocks"]:
                        source_hash = res["blocks"][0]
                        print(f"  > BLOCO DETECTADO: {source_hash}")
                        
                        info = requests.post(rpc, json={"action": "account_info", "account": addr}, 
                                             proxies=proxies, timeout=15).json()
                        
                        # Se conta nova, PoW sobre a pub_key local; se velha, sobre o frontier
                        pow_target = info.get("frontier", pub_key)
                        
                        status_msg = f"#{idx}: Resolvendo PoW..."
                        work = solve_pow(pow_target)
                        
                        if work:
                            res_bal = requests.post(rpc, json={"action": "account_balance", "account": addr}, 
                                                    proxies=proxies, timeout=15).json()
                            bal_raw = int(res_bal.get("balance", 0)) + int(res_bal.get("pending", 0))
                            bal_final = bal_raw / (10**30)
                            
                            if bal_final > 0:
                                update_db(idx, addr, bal_final, "✅ COMPLETO")
                                print(f"  > SUCESSO! Saldo: {bal_final} XNO")
                                success = True
                                break
                except: continue

        except Exception as e:
            print(f"[RECEIVER ERRO CRÍTICO] {e}")

        if not success:
            update_db(idx, addr, 0.0, "❌ FALHA/TIMEOUT")

        next_index += 1
        time.sleep(5)

# --- 3. INTERFACE ---

class NanoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MSR Nano Hunter v18.0 - Linear Sync")
        self.geometry("1200x850")
        self.configure(bg="#050505")
        self.is_closing = False
        
        top = tk.Frame(self, bg="#111", pady=20)
        top.pack(fill=tk.X)
        tk.Label(top, text="SEED:", fg="#888", bg="#111").grid(row=0, column=0, padx=10)
        self.ent_seed = tk.Entry(top, width=65, bg="#222", fg="#3498db", font=("Consolas", 10))
        self.ent_seed.grid(row=0, column=1)
        self.btn_toggle = tk.Button(top, text="LIGAR", bg="#27ae60", fg="white", width=15, command=self.toggle)
        self.btn_toggle.grid(row=0, column=2, padx=20)

        st = tk.Frame(self, bg="#1a1a1a", pady=8)
        st.pack(fill=tk.X)
        self.lbl_status = tk.Label(st, text="STATUS: Desligado", fg="#f1c40f", bg="#1a1a1a", font=("bold", 10))
        self.lbl_status.pack(side=tk.LEFT, padx=20)
        self.lbl_ip = tk.Label(st, text="IP TOR: --", fg="#e67e22", bg="#1a1a1a")
        self.lbl_ip.pack(side=tk.RIGHT, padx=20)

        # TABELAS COM SCROLLBARS
        tk.Label(self, text="LISTA 1: HISTÓRICO DE CLAIMS", fg="#3498db", bg="#050505", font="bold").pack(pady=5)
        f1 = tk.Frame(self, bg="#050505")
        f1.pack(fill=tk.X, padx=10)
        self.tree1 = ttk.Treeview(f1, columns=("idx", "addr", "time"), show="headings", height=8)
        self.tree1.heading("idx", text="Índice"); self.tree1.heading("addr", text="Endereço"); self.tree1.heading("time", text="Hora")
        self.tree1.pack(side=tk.LEFT, fill=tk.X, expand=True)
        s1 = ttk.Scrollbar(f1, orient="vertical", command=self.tree1.yview); s1.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree1.configure(yscrollcommand=s1.set)

        tk.Label(self, text="LISTA 2: VALIDAÇÕES (RESULTADO ÚNICO)", fg="#2ecc71", bg="#050505", font="bold").pack(pady=(15, 5))
        f2 = tk.Frame(self, bg="#050505")
        f2.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree2 = ttk.Treeview(f2, columns=("idx", "addr", "bal", "st"), show="headings")
        self.tree2.heading("idx", text="Índice"); self.tree2.heading("addr", text="Endereço")
        self.tree2.heading("bal", text="Saldo (XNO)"); self.tree2.heading("st", text="Status")
        self.tree2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        s2 = ttk.Scrollbar(f2, orient="vertical", command=self.tree2.yview); s2.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree2.configure(yscrollcommand=s2.set)

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.load_init(); self.refresh_ui()

    def load_init(self):
        global next_index
        if not os.path.exists(FOLDER_PATH): os.makedirs(FOLDER_PATH)
        conn = sqlite3.connect(DB_NAME)
        conn.execute('''CREATE TABLE IF NOT EXISTS multi_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            idx INTEGER UNIQUE, address TEXT, balance REAL, status TEXT, time TEXT)''')
        res = conn.execute("SELECT MAX(idx) FROM multi_history").fetchone()
        next_index = (res[0] + 1) if res[0] is not None else 0
        conn.close()
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                c = json.load(f); self.ent_seed.insert(0, c.get("seed", ""))

    def toggle(self):
        global is_running
        if not is_running:
            is_running = True; self.btn_toggle.config(text="PARAR", bg="#c0392b")
            seed = self.ent_seed.get()
            threading.Thread(target=main_sync_engine, args=(seed,), daemon=True).start()
        else:
            is_running = False; self.btn_toggle.config(text="LIGAR", bg="#27ae60")

    def refresh_ui(self):
        if self.is_closing: return
        self.lbl_status.config(text=f"STATUS: {status_msg}")
        self.lbl_ip.config(text=f"IP: {current_tor_ip}")
        try:
            conn = sqlite3.connect(DB_NAME)
            h = conn.execute("SELECT idx, address, time FROM multi_history ORDER BY idx DESC").fetchall()
            self.tree1.delete(*self.tree1.get_children())
            for r in h: self.tree1.insert("", "end", values=(f"#{r[0]}", r[1], r[2]))
            
            b = conn.execute("SELECT idx, address, balance, status FROM multi_history ORDER BY idx DESC").fetchall()
            self.tree2.delete(*self.tree2.get_children())
            for r in b: self.tree2.insert("", "end", values=(f"#{r[0]}", r[1], f"{r[2]:.8f}", r[3]))
            conn.close()
        except: pass
        self.after(3000, self.refresh_ui)

    def on_close(self):
        self.is_closing = True; global is_running; is_running = False; self.destroy()

if __name__ == "__main__":
    app = NanoApp(); app.mainloop()