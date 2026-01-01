import ctypes
import sys
import os
import json
import random
import string
import time
import threading
import subprocess
import traceback
import requests
from stem.control import Controller
from stem import Signal

# --- ELEVAÇÃO DE PRIVILÉGIO ---
def run_as_admin():
    try:
        if ctypes.windll.shell32.IsUserAnAdmin():
            return True
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{__file__}"', None, 1)
        return False
    except:
        return False

if __name__ == "__main__":
    if not run_as_admin():
        sys.exit()

import tkinter as tk
from tkinter import filedialog, scrolledtext
import frida
import win32gui
import win32con
import win32api
import win32process

class SandboxPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("MSR Sandbox - Master Tor Ultimate v7")
        self.root.geometry("900x950")
        self.root.configure(bg="#050505")

        self.config_file = "config.json"
        self.active_apps = {}
        self.border_thickness = 18  # Grossa e externa

        self.tor_proxy_port = 9150
        self.tor_control_port = 9151

        self.app_path = tk.StringVar()
        self.fake_name = tk.StringVar()
        self.fake_mac = tk.StringVar()
        self.fake_serial = tk.StringVar()
        self.fake_guid = self.generate_guid()

        self.setup_ui()
        self.load_config()
        self.log("Sistema pronto. Tor SOCKS: 9150 | Controle: 9151")

    def generate_guid(self):
        return f"{''.join(random.choices('abcdef0123456789', k=8))}-4bd1-4f1b-b789-{''.join(random.choices('abcdef0123456789', k=12))}"

    # --- TROCA DE IP TOR ---
    def get_new_tor_ip(self):
        try:
            self.log("Renovando circuito Tor...")
            with Controller.from_port(port=self.tor_control_port) as controller:
                possible_paths = [
                    os.path.expandvars(r"%APPDATA%\Tor Browser\Browser\TorBrowser\Data\Tor\control_auth_cookie"),
                    os.path.expandvars(r"%APPDATA%\tor-browser\Browser\TorBrowser\Data\Tor\control_auth_cookie"),
                    os.path.expandvars(r"%APPDATA%\Tor Browser\TorBrowser\Data\Tor\control_auth_cookie"),
                ]
                authenticated = False
                for path in possible_paths:
                    if os.path.exists(path):
                        self.log(f"Cookie encontrado: {path}")
                        controller.authenticate(cookie_path=path)
                        authenticated = True
                        break
                if not authenticated:
                    try:
                        controller.authenticate()
                        self.log("Autenticação vazia OK.")
                        authenticated = True
                    except:
                        pass
                
                if not authenticated:
                    self.log("ERRO: Falha na autenticação Tor. Tor Browser aberto?")
                    return False

                controller.signal(Signal.NEWNYM)
                self.log("NEWNYM enviado. Estabilizando (~15s)...")

            time.sleep(15)

            proxies = {"http": "socks5h://127.0.0.1:9150", "https": "socks5h://127.0.0.1:9150"}
            new_ip = requests.get("https://ident.me", proxies=proxies, timeout=20).text.strip()
            self.log(f"✅ NOVO IP TOR CONFIRMADO: {new_ip}")
            return True
        except Exception as e:
            self.log(f"ERRO TOR: {traceback.format_exc()}")
            return False

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.fake_name.set(data.get("name", "MSR-VIRTUAL"))
                    self.fake_mac.set(data.get("mac", "00:AA:BB:CC:DD:EE"))
                    self.fake_serial.set(data.get("serial", "A1B2C3D4"))
            else:
                self.generate_new_hardware()
        except:
            self.generate_new_hardware()

    def generate_new_hardware(self):
        try:
            name = "MSR-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            mac = ":".join(["%02x" % random.randint(0, 255) for _ in range(6)]).upper()
            serial = ''.join(random.choices("0123456789ABCDEF", k=8))
            self.fake_name.set(name)
            self.fake_mac.set(mac)
            self.fake_serial.set(serial)
            with open(self.config_file, 'w') as f:
                json.dump({"name": name, "mac": mac, "serial": serial}, f)
            self.log(f"Novo HWID gerado: {name} | MAC: {mac}")
        except:
            pass

    def setup_ui(self):
        tk.Label(self.root, text="MSR MASTER TOR SANDBOX v7", font=("Arial Black", 20), bg="#050505", fg="#00d8d6").pack(pady=15)

        f = tk.Frame(self.root, bg="#050505")
        f.pack(pady=8)
        tk.Entry(f, textvariable=self.app_path, width=60, bg="#1a1a1a", fg="white").pack(side=tk.LEFT, padx=10)
        tk.Button(f, text="BUSCAR EXE", command=self.browse_file, bg="#2d3436", fg="white").pack(side=tk.LEFT)

        hw = tk.LabelFrame(self.root, text=" Identidade Virtual ", bg="#050505", fg="#3ae374", padx=20, pady=15)
        hw.pack(pady=15, fill="x", padx=50)
        for l, v in [("PC Name:", self.fake_name), ("MAC Address:", self.fake_mac), ("Disk Serial:", self.fake_serial)]:
            row = tk.Frame(hw, bg="#050505")
            row.pack(fill="x", pady=4)
            tk.Label(row, text=l, width=15, bg="#050505", fg="white", anchor="w").pack(side=tk.LEFT)
            tk.Entry(row, textvariable=v, bg="#1a1a1a", fg="#00ff00").pack(side=tk.LEFT, fill="x", expand=True)

        tk.Button(hw, text="🔄 GIRAR HWID", command=self.generate_new_hardware, bg="#ff9f1a", font=("Arial", 10, "bold")).pack(pady=12)

        tk.Button(self.root, text="LANÇAR COM NOVO IP TOR", font=("Arial", 16, "bold"), bg="#6c5ce7", fg="white", height=2,
                  command=self.start_launch).pack(pady=20, fill="x", padx=150)

        self.log_area = scrolledtext.ScrolledText(self.root, height=22, bg="black", fg="#00ff00", font=("Consolas", 10))
        self.log_area.pack(padx=30, pady=15, fill="both", expand=True)

    def log(self, msg):
        ts = time.strftime("%H:%M:%S")
        self.log_area.insert(tk.END, f"[{ts}] {msg}\n")
        self.log_area.see(tk.END)
        self.root.update_idletasks()

    def browse_file(self):
        p = filedialog.askopenfilename(filetypes=[("Executáveis", "*.exe")])
        if p:
            self.app_path.set(p)

    def start_launch(self):
        threading.Thread(target=self.launch_logic, daemon=True).start()

    def launch_logic(self):
        pid = None
        try:
            target = self.app_path.get().strip()
            if not os.path.exists(target):
                self.log("ERRO: Caminho do EXE inválido.")
                return

            self.get_new_tor_ip()

            # FORÇA PROXY VIA ENV VARS (funciona em browsers e muitas apps)
            env = {
                "http_proxy": "socks5h://127.0.0.1:9150",
                "https_proxy": "socks5h://127.0.0.1:9150",
                "all_proxy": "socks5h://127.0.0.1:9150",
                "HTTP_PROXY": "socks5h://127.0.0.1:9150",
                "HTTPS_PROXY": "socks5h://127.0.0.1:9150",
                "ALL_PROXY": "socks5h://127.0.0.1:9150"
            }

            self.log(f"Spawando {os.path.basename(target)} com Tor forçado...")
            pid = frida.spawn([target], env=env)
            session = frida.attach(pid)

            js_code = f"""
            (function() {{
                try {{
                    const fakeName = "{self.fake_name.get()}";
                    const fakeMac = "{self.fake_mac.get()}";
                    const fakeSerial = parseInt("{self.fake_serial.get()}", 16);
                    const fakeGuid = "{self.fake_guid}";
                    const torPort = {self.tor_proxy_port};

                    const resolver = new ApiResolver('module');

                    // HWID SPOOF COMPLETO
                    const pGetComp = resolver.enumerateMatches('exports:kernel32!GetComputerNameW')[0];
                    if (pGetComp) Interceptor.attach(pGetComp.address, {{
                        onEnter: function(args) {{ this.buf = args[0]; }},
                        onLeave: function(ret) {{ if (this.buf) this.buf.writeUtf16String(fakeName); }}
                    }});

                    const pGetVol = resolver.enumerateMatches('exports:kernel32!GetVolumeInformationW')[0];
                    if (pGetVol) Interceptor.attach(pGetVol.address, {{
                        onEnter: function(args) {{ this.serialPtr = args[6]; }},
                        onLeave: function(ret) {{ if (this.serialPtr) this.serialPtr.writeU32(fakeSerial); }}
                    }});

                    const pRegQuery = resolver.enumerateMatches('exports:advapi32!RegQueryValueExW')[0];
                    if (pRegQuery) Interceptor.attach(pRegQuery.address, {{
                        onEnter: function(args) {{ this.keyName = args[1].readUtf16String(); }},
                        onLeave: function(ret) {{
                            if (this.keyName && (this.keyName.includes("MachineGuid") || this.keyName.includes("HwProfileGuid") || this.keyName.includes("HardwareID"))) {{
                                args[4].writeUtf16String(fakeGuid);
                                send("HWID: Registry spoofado");
                            }}
                        }}
                    }});

                    const pAdapters = resolver.enumerateMatches('exports:iphlpapi!GetAdaptersInfo')[0];
                    if (pAdapters) Interceptor.attach(pAdapters.address, {{
                        onLeave: function(ret) {{
                            let ptr = args[0].readPointer();
                            while (!ptr.isNull()) {{
                                ptr.add(8).writeByteArray([0x00,0xAA,0xBB,0xCC,0xDD,0xEE]);
                                ptr = ptr.readPointer();
                            }}
                        }}
                    }});

                    // FORÇAR TOR (inspirado em Proxifier / Mudfish)
                    const pWinHttpOpen = resolver.enumerateMatches('exports:winhttp!WinHttpOpen')[0];
                    if (pWinHttpOpen) {{
                        Interceptor.attach(pWinHttpOpen.address, {{
                            onEnter: function(args) {{
                                send("🔥 TOR FORÇADO: WinHttpOpen → SOCKS5");
                                args[1] = ptr(3);
                                args[2] = Memory.allocUtf16String("socks=127.0.0.1:" + torPort);
                            }}
                        }});
                    }}

                    const ws2 = Module.load('ws2_32.dll');
                    ['connect', 'WSAConnect'].forEach(name => {{
                        const addr = ws2.findExportByName(name);
                        if (addr) {{
                            Interceptor.attach(addr, {{
                                onEnter: function(args) {{
                                    const sockaddr = args[1];
                                    const port = sockaddr.add(2).readU16();
                                    if (port !== torPort && port !== 9050) {{
                                        send("🔥 TOR FORÇADO: " + name);
                                        sockaddr.add(4).writeU32(0x0100007f);
                                        sockaddr.add(2).writeU16(torPort);
                                    }}
                                }}
                            }});
                        }}
                    }});

                    const pMutex = resolver.enumerateMatches('exports:kernel32!CreateMutexW')[0];
                    if (pMutex) Interceptor.attach(pMutex.address, {{
                        onEnter: function(args) {{
                            if (args[2].isNull() === false) {{
                                let name = args[2].readUtf16String();
                                args[2].writeUtf16String(name + "_virtual");
                            }}
                        }}
                    }});

                    send("✅ SANDBOX ATIVADA: HWID spoof + Tor forçado");
                }} catch(e) {{
                    send("ERRO_JS: " + e.message);
                }}
            }})();
            """

            script = session.create_script(js_code)
            script.on('message', lambda msg, data: self.log(msg.get('payload', str(msg))))
            script.load()

            self.active_apps[pid] = {'session': session, 'script': script}
            frida.resume(pid)
            self.log(f"✅ Aplicação lançada em sandbox (PID {pid})")
            self.root.after(1500, lambda: self.draw_border_tracker(pid))

        except Exception as e:
            self.log(f"ERRO CRÍTICO: {traceback.format_exc()}")

    # --- BORDA AZUL EXTERNA + LIMITA MAXIMIZAÇÃO ---
    def draw_border_tracker(self, pid):
        try:
            overlay = tk.Toplevel(self.root)
            overlay.overrideredirect(True)
            overlay.attributes("-topmost", True)
            overlay.attributes("-transparentcolor", "black")
            overlay.config(bg="black")

            canvas = tk.Canvas(overlay, bg="black", highlightthickness=0)
            canvas.pack(fill="both", expand=True)

            t = self.border_thickness
            start_time = time.time()
            max_wait = 25

            def find_main_window():
                windows = []
                def enum(hwnd, _):
                    if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                        _, wpid = win32process.GetWindowThreadProcessId(hwnd)
                        if wpid == pid:
                            rect = win32gui.GetWindowRect(hwnd)
                            area = (rect[2] - rect[0]) * (rect[3] - rect[1])
                            if area > 80000:
                                windows.append((hwnd, area, rect))
                win32gui.EnumWindows(enum, None)
                if windows:
                    windows.sort(key=lambda x: x[1], reverse=True)
                    return windows[0][2], windows[0][0]
                return None, None

            def update_border():
                try:
                    # Verifica se processo ainda existe
                    try:
                        h = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, pid)
                        win32api.CloseHandle(h)
                    except:
                        self.log("Aplicação encerrada. Removendo borda.")
                        overlay.destroy()
                        return

                    rect, hwnd = find_main_window()
                    if hwnd:
                        x, y, r, b = win32gui.GetWindowRect(hwnd)
                        w = r - x
                        h = b - y

                        # Borda externa
                        border_x = x - t
                        border_y = y - t
                        border_w = w + 2 * t
                        border_h = h + 2 * t

                        overlay.geometry(f"{border_w}x{border_h}+{border_x}+{border_y}")
                        canvas.delete("all")
                        canvas.create_rectangle(t, t, border_w - t, border_h - t, outline="#00ddff", width=t)

                        # Limita maximização para deixar borda visível
                        if win32gui.GetWindowPlacement(hwnd)[1] == win32con.SW_SHOWMAXIMIZED:
                            mon = win32api.MonitorFromWindow(hwnd)
                            mi = win32api.GetMonitorInfo(mon)['Work']
                            new_w = mi[2] - mi[0] - 2*t
                            new_h = mi[3] - mi[1] - 2*t
                            win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, mi[0] + t, mi[1] + t, new_w, new_h, win32con.SWP_SHOWWINDOW)

                        overlay.deiconify()
                        self.log("🔵 Borda externa ativada e maximização limitada!")
                    else:
                        if time.time() - start_time > max_wait:
                            self.log("AVISO: Janela principal não detectada após 25s.")
                            overlay.destroy()
                            return
                        overlay.withdraw()

                    overlay.after(150, update_border)
                except Exception as e:
                    self.log(f"Erro na borda: {e}")

            update_border()
        except Exception as e:
            self.log(f"Erro criando borda externa: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SandboxPanel(root)
    root.mainloop()