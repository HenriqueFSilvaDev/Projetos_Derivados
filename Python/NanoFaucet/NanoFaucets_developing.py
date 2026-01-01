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

# --- 1. FUNÇÕES DE CHAVES (DO BACKUP - FUNCIONANDO) ---
def get_keys(seed_hex, index):
    try:
        seed_bytes = bytes.fromhex(seed_hex)
        bip44_mst = Bip44.FromSeed(seed_bytes, Bip44Coins.NANO)
        bip44_acc = bip44_mst.Purpose().Coin().Account(index)
        
        address = bip44_acc.PublicKey().ToAddress()
        priv_hex = bip44_acc.PrivateKey().Raw().ToHex()
        
        # Deriva pubkey via nacl
        priv_bytes = bytes.fromhex(priv_hex)
        signing_key = nacl.signing.SigningKey(priv_bytes)
        pub_hex = signing_key.verify_key.encode(encoder=nacl.encoding.HexEncoder).decode().upper()
        
        return address, priv_hex, pub_hex, signing_key
    except Exception as e:
        print(f"[ERRO CHAVES] {e}")
        return None, None, None, None

# --- 2. CONVERSÃO ENDEREÇO → PUBKEY (CORRIGIDA) ---
NANO_ALPHABET = "13456789abcdefghijkmnopqrstuwxyz"

def address_to_pubkey(address):
    """Converte nano_xxx para pubkey hex"""
    try:
        address = address.replace("nano_", "").replace("xrb_", "")
        pub_part = address[:-8]  # Remove checksum
        
        # Decodifica Base32 Nano
        bits = ""
        for char in pub_part:
            bits += bin(NANO_ALPHABET.index(char))[2:].zfill(5)
        
        # Remove padding inicial e converte
        pub_hex = hex(int(bits[4:], 2))[2:].upper().zfill(64)
        return pub_hex
    except Exception as e:
        print(f"[ERRO CONVERSÃO] {e}")
        return None

# --- 3. PROOF OF WORK (CORRIGIDO COM THRESHOLD ATUALIZADO) ---
def solve_pow(hash_hex):
    """Resolve PoW para threshold da rede Nano (pós v19)"""
    print(f"[POW] Iniciando para: {hash_hex[:16]}...")
    
    # THRESHOLD ATUALIZADO (mudou em 2021 para dificultar spam)
    target = int("fffffff800000000", 16)
    hash_bytes = bytes.fromhex(hash_hex)
    nonce = 0
    
    while is_running:
        nonce_bytes = nonce.to_bytes(8, byteorder='little')
        work_hash = hashlib.blake2b(nonce_bytes + hash_bytes, digest_size=8).digest()
        work_value = int.from_bytes(work_hash, byteorder='little')
        
        if work_value >= target:
            # Work = nonce em BIG ENDIAN (reversed)
            work_hex = nonce.to_bytes(8, byteorder='big').hex().upper()
            print(f"[POW] ✅ Resolvido: {work_hex} (tentativas: {nonce:,})")
            return work_hex
        
        nonce += 1
        if nonce % 100000 == 0:
            print(f"[POW] ... {nonce:,} tentativas (work atual: {work_value:016x})")
            time.sleep(0.001)
    
    return None

# --- 4. CONSTRUÇÃO E ASSINATURA DO STATE BLOCK (CORRIGIDA) ---
def create_and_sign_receive_block(address, pub_hex, priv_hex, signing_key, 
                                   frontier, current_balance, pending_hash, amount, representative):
    """
    Monta um State Block para receive seguindo especificação Nano
    """
    try:
        # 1. Calcula novo balance
        new_balance = current_balance + amount
        
        # 2. Resolve PoW (sobre frontier se conta existe, senão sobre pubkey)
        pow_base = frontier if frontier != "0"*64 else pub_hex
        
        # OPÇÃO 1: Tenta PoW via RPC (mais rápido e confiável)
        work = None
        try:
            pow_res = requests.post("https://rpc.nano.to", json={
                "action": "work_generate",
                "hash": pow_base,
                "difficulty": "fffffff800000000"
            }, timeout=30).json()
            
            if "work" in pow_res:
                work = pow_res["work"]
                print(f"[POW] ✅ Gerado via RPC: {work}")
        except:
            print("[POW] ⚠️ RPC falhou, calculando localmente...")
        
        # OPÇÃO 2: Se RPC falhar, calcula localmente
        if not work:
            work = solve_pow(pow_base)
            if not work:
                return None
        
        # 3. Converte representative para pubkey
        rep_pubkey = address_to_pubkey(representative)
        if not rep_pubkey:
            return None
        
        # 4. Monta o bloco binário (ORDEM EXATA)
        preamble = bytes.fromhex("0000000000000000000000000000000000000000000000000000000000000006")
        account_bytes = bytes.fromhex(pub_hex)
        previous_bytes = bytes.fromhex(frontier)
        rep_bytes = bytes.fromhex(rep_pubkey)
        balance_bytes = new_balance.to_bytes(16, byteorder='big')
        link_bytes = bytes.fromhex(pending_hash)
        
        block_data = preamble + account_bytes + previous_bytes + rep_bytes + balance_bytes + link_bytes
        
        # 5. Hash do bloco
        block_hash = hashlib.blake2b(block_data, digest_size=32).digest()
        
        # 6. Assina com nacl
        signature = signing_key.sign(block_hash).signature.hex().upper()
        
        # 7. Monta JSON do bloco
        block_json = {
            "type": "state",
            "account": address,
            "previous": frontier,
            "representative": representative,
            "balance": str(new_balance),
            "link": pending_hash,
            "work": work,
            "signature": signature
        }
        
        return block_json, block_hash.hex().upper()
        
    except Exception as e:
        print(f"[ERRO BLOCO] {e}")
        return None

# --- 5. PROCESSADOR DE BLOCOS PENDENTES (CORRIGIDO) ---
def process_pending_blocks(address, pub_hex, priv_hex, signing_key, proxies):
    """
    Processa TODOS os blocos pendentes, um por um
    """
    try:
        # Estado local inicial
        frontier = "0" * 64
        balance = 0
        rep = "nano_1natrium1o3z5519ifou7xii8crpxpk8y65qmkih8e8bpsjri651oza8imdd"
        
        for rpc in RPC_NODES:
            try:
                # Busca info da conta
                info_res = requests.post(rpc, json={
                    "action": "account_info",
                    "account": address,
                    "representative": "true"
                }, proxies=proxies, timeout=15).json()
                
                if "error" not in info_res:
                    frontier = info_res["frontier"]
                    balance = int(info_res["balance"])
                    rep = info_res.get("representative", rep)
                    print(f"[RECEIVE] Conta existente | Frontier: {frontier[:16]}... | Balance: {balance}")
                else:
                    print(f"[RECEIVE] Conta nova | PoW será sobre pubkey")
                
                # Busca blocos pendentes (até 50 por vez)
                pending_res = requests.post(rpc, json={
                    "action": "pending",
                    "account": address,
                    "count": "50",
                    "include_active": "true"
                }, proxies=proxies, timeout=15).json()
                
                pending_hashes = pending_res.get("blocks", [])
                if not pending_hashes:
                    print(f"[RECEIVE] ✅ Nenhum bloco pendente")
                    return balance / (10**30)
                
                print(f"[RECEIVE] 📦 {len(pending_hashes)} blocos para processar")
                
                # Processa cada bloco
                for i, p_hash in enumerate(pending_hashes, 1):
                    if not is_running:
                        break
                    
                    print(f"\n[RECEIVE] Processando bloco {i}/{len(pending_hashes)}: {p_hash[:16]}...")
                    
                    # Busca info do bloco
                    block_info = requests.post(rpc, json={
                        "action": "blocks_info",
                        "hashes": [p_hash],
                        "json_block": "true"
                    }, proxies=proxies, timeout=15).json()
                    
                    amount = int(block_info["blocks"][p_hash]["amount"])
                    print(f"[RECEIVE] Valor: {amount / (10**30):.8f} XNO")
                    
                    # Cria e assina o bloco
                    result = create_and_sign_receive_block(
                        address, pub_hex, priv_hex, signing_key,
                        frontier, balance, p_hash, amount, rep
                    )
                    
                    if not result:
                        print(f"[RECEIVE] ❌ Falha ao criar bloco")
                        continue
                    
                    block_json, new_hash = result
                    
                    # Transmite para a rede
                    process_res = requests.post(rpc, json={
                        "action": "process",
                        "json_block": "true",
                        "block": block_json
                    }, proxies=proxies, timeout=15).json()
                    
                    if "hash" in process_res:
                        print(f"[RECEIVE] ✅ SUCESSO! Hash: {process_res['hash'][:16]}...")
                        # Atualiza estado local para próximo bloco
                        frontier = process_res["hash"]
                        balance += amount
                    else:
                        error = process_res.get("error", "Desconhecido")
                        print(f"[RECEIVE] ❌ Erro RPC: {error}")
                        if "Fork" in error or "Old block" in error:
                            continue  # Pode tentar próximo
                        break
                    
                    time.sleep(1)  # Evita spam
                
                return balance / (10**30)
                
            except Exception as e:
                print(f"[RECEIVE] Erro com nó {rpc}: {e}")
                continue
        
        return 0.0
        
    except Exception as e:
        print(f"[RECEIVE] ERRO CRÍTICO: {e}")
        return 0.0

# --- 6. TOR ---
def renew_tor_ip():
    print("[TOR] Solicitando novo IP...")
    try:
        with Controller.from_port(port=9151) as ctrl:
            ctrl.authenticate()
            ctrl.signal(Signal.NEWNYM)
        time.sleep(10)
        proxies = {'http': 'socks5h://127.0.0.1:9150', 'https': 'socks5h://127.0.0.1:9150'}
        ip = requests.get("https://ident.me", proxies=proxies, timeout=15).text.strip()
        print(f"[TOR] Novo IP: {ip}")
        return ip
    except Exception as e:
        print(f"[TOR ERRO] {e}")
        return "Erro Tor"

def update_db(idx, addr, bal, status):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("INSERT OR REPLACE INTO multi_history (idx, address, balance, status, time) VALUES (?,?,?,?,?)",
                 (idx, addr, bal, status, datetime.datetime.now().strftime("%H:%M:%S")))
    conn.commit()
    conn.close()

# --- 7. HUNTER (CLAIMS) ---
def run_hunter_claims(address):
    print(f"[HUNTER] Iniciando claims para {address[:15]}...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(proxy={"server": TOR_PROXY_ADDR})
            page = context.new_page()
            
            # FreeNanoFaucet
            try:
                page.goto("https://freenanofaucet.com/faucet", wait_until="load", timeout=60000)
                if page.locator("input[name='address']").is_visible():
                    page.fill("input[name='address']", address)
                    page.click("#getNano")
                    time.sleep(5)
                    print("[HUNTER] ✅ FreeNanoFaucet")
            except: print("[HUNTER] ❌ FreeNanoFaucet")
            
            # NanSwap
            try:
                page.goto("https://nanswap.com/nano-faucet", wait_until="load", timeout=60000)
                time.sleep(3)
                print("[HUNTER] ✅ NanSwap")
            except: print("[HUNTER] ❌ NanSwap")
            
            browser.close()
    except Exception as e:
        print(f"[HUNTER] ERRO: {e}")

# --- 8. MOTOR PRINCIPAL ---
def main_sync_engine(seed_hex):
    global next_index, status_msg, current_tor_ip, is_running
    
    while is_running:
        idx = next_index
        result = get_keys(seed_hex, idx)
        
        if not result[0]:
            print(f"[MOTOR] Erro ao gerar chaves #{idx}")
            next_index += 1
            continue
        
        addr, priv, pub, signing_key = result
        print(f"\n{'='*60}")
        print(f"[MOTOR] CICLO #{idx}")
        print(f"Endereço: {addr}")
        print(f"{'='*60}")
        
        # 1. Renova IP
        status_msg = f"#{idx}: Renovando IP..."
        current_tor_ip = renew_tor_ip()
        
        # 2. Faz claims
        status_msg = f"#{idx}: Fazendo Claims..."
        run_hunter_claims(addr)
        
        # 3. Aguarda propagação
        print("[MOTOR] Aguardando 30s para propagação dos blocos...")
        time.sleep(30)
        
        # 4. Processa receives
        status_msg = f"#{idx}: Processando Receives..."
        proxies = {'http': "socks5h://127.0.0.1:9150", 'https': "socks5h://127.0.0.1:9150"}
        final_balance = process_pending_blocks(addr, pub, priv, signing_key, proxies)
        
        # 5. Salva resultado
        if final_balance > 0:
            update_db(idx, addr, final_balance, "✅ COMPLETO")
            print(f"[MOTOR] ✅ Saldo Final: {final_balance:.8f} XNO")
        else:
            update_db(idx, addr, 0.0, "⏳ PENDENTE")
            print(f"[MOTOR] ⏳ Nenhum saldo confirmado ainda")
        
        next_index += 1
        time.sleep(5)

# --- 9. INTERFACE ---
class NanoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MSR Nano Hunter v21.0 - Receive CORRIGIDO")
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

        tk.Label(self, text="HISTÓRICO DE TRANSAÇÕES", fg="#3498db", bg="#050505", font="bold").pack(pady=5)
        f = tk.Frame(self, bg="#050505")
        f.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree = ttk.Treeview(f, columns=("idx", "addr", "bal", "st", "time"), show="headings")
        self.tree.heading("idx", text="Índice")
        self.tree.heading("addr", text="Endereço")
        self.tree.heading("bal", text="Saldo (XNO)")
        self.tree.heading("st", text="Status")
        self.tree.heading("time", text="Hora")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        s = ttk.Scrollbar(f, orient="vertical", command=self.tree.yview)
        s.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=s.set)

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.load_init()
        self.refresh_ui()

    def load_init(self):
        global next_index
        if not os.path.exists(FOLDER_PATH):
            os.makedirs(FOLDER_PATH)
        conn = sqlite3.connect(DB_NAME)
        conn.execute('''CREATE TABLE IF NOT EXISTS multi_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            idx INTEGER UNIQUE, address TEXT, balance REAL, status TEXT, time TEXT)''')
        res = conn.execute("SELECT MAX(idx) FROM multi_history").fetchone()
        next_index = (res[0] + 1) if res[0] is not None else 0
        conn.close()
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                c = json.load(f)
                self.ent_seed.insert(0, c.get("seed", ""))

    def toggle(self):
        global is_running
        if not is_running:
            seed = self.ent_seed.get().strip()
            if not seed:
                messagebox.showerror("Erro", "Insira uma seed válida!")
                return
            with open(CONFIG_FILE, 'w') as f:
                json.dump({"seed": seed}, f)
            is_running = True
            self.btn_toggle.config(text="PARAR", bg="#c0392b")
            threading.Thread(target=main_sync_engine, args=(seed,), daemon=True).start()
        else:
            is_running = False
            self.btn_toggle.config(text="LIGAR", bg="#27ae60")

    def refresh_ui(self):
        if self.is_closing:
            return
        self.lbl_status.config(text=f"STATUS: {status_msg}")
        self.lbl_ip.config(text=f"IP: {current_tor_ip}")
        try:
            conn = sqlite3.connect(DB_NAME)
            rows = conn.execute("SELECT idx, address, balance, status, time FROM multi_history ORDER BY idx DESC LIMIT 50").fetchall()
            self.tree.delete(*self.tree.get_children())
            for r in rows:
                self.tree.insert("", "end", values=(f"#{r[0]}", r[1], f"{r[2]:.8f}", r[3], r[4]))
            conn.close()
        except:
            pass
        self.after(3000, self.refresh_ui)

    def on_close(self):
        self.is_closing = True
        global is_running
        is_running = False
        self.destroy()

if __name__ == "__main__":
    app = NanoApp()
    app.mainloop()