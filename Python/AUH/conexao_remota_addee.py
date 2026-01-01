import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import keyboard
import threading
import time
import random
import json
import os
from PIL import Image, ImageTk
import sys
import psutil

class ConexaoRemotaADDEE:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Conexão Remota - ADDEE")
        self.root.geometry("400x350")
        self.root.resizable(True, True)
        
        # Configurações anti-detecção
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.95)
        
        # Variáveis
        self.posicoes_runa = []
        self.hotkeys_ativas = ["f1", "f2"]  # Hotkeys para cada linha
        self.hotkey_captura = "ctrl+shift+c"
        self.mouse_original_pos = None
        self.ativo = False
        self.processo_selecionado = None
        self.processos_disponiveis = []
        
        # Configurações do PyAutoGUI para parecer mais humano
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.01
        
        self.setup_ui()
        self.atualizar_processos()
        self.load_config()
        self.setup_hotkeys()
        
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        title_label = ttk.Label(main_frame, text="Conexão Remota - ADDEE", 
                               font=("Arial", 10, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Frame para seleção de processo
        processo_frame = ttk.LabelFrame(main_frame, text="Processo/Al aplicativo", padding="5")
        processo_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # ComboBox para seleção de processo
        self.processo_var = tk.StringVar()
        self.processo_combo = ttk.Combobox(processo_frame, textvariable=self.processo_var, 
                                          width=35, state="readonly")
        self.processo_combo.grid(row=0, column=0, padx=(0, 5), sticky=(tk.W, tk.E))
        
        # Botão para atualizar lista de processos
        ttk.Button(processo_frame, text="Atualizar", 
                  command=self.atualizar_processos).grid(row=0, column=1, padx=5)
        
        # Label de status do processo
        self.processo_status = ttk.Label(processo_frame, text="Nenhum processo selecionado", 
                                        foreground="red", font=("Arial", 8))
        self.processo_status.grid(row=1, column=0, columnspan=2, pady=2, sticky=(tk.W, tk.E))
        
        # Configurar grid weights para processo_frame
        processo_frame.columnconfigure(0, weight=1)
        
        # Frame para captura de posições
        posicoes_frame = ttk.LabelFrame(main_frame, text="Captura de Posições", padding="5")
        posicoes_frame.grid(row=2, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # Primeira linha - Posição 1, Posição 2, Hotkey 1
        primeira_linha = ttk.Frame(posicoes_frame)
        primeira_linha.grid(row=0, column=0, columnspan=2, pady=2, sticky=(tk.W, tk.E))
        
        self.btn_pos1 = ttk.Button(primeira_linha, text="Posição 1", 
                                  command=lambda: self.capturar_posicao(0), width=10)
        self.btn_pos1.grid(row=0, column=0, padx=(0, 5))
        
        self.btn_pos2 = ttk.Button(primeira_linha, text="Posição 2", 
                                  command=lambda: self.capturar_posicao(1), width=10)
        self.btn_pos2.grid(row=0, column=1, padx=(0, 5))
        
        ttk.Label(primeira_linha, text="Hotkey:").grid(row=0, column=2, padx=(10, 2))
        self.hotkey_var1 = tk.StringVar(value="f1")
        hotkey_entry1 = ttk.Entry(primeira_linha, textvariable=self.hotkey_var1, width=8)
        hotkey_entry1.grid(row=0, column=3, padx=(0, 5))
        
        # Segunda linha - Posição 3, Posição 4, Hotkey 2
        segunda_linha = ttk.Frame(posicoes_frame)
        segunda_linha.grid(row=1, column=0, columnspan=2, pady=2, sticky=(tk.W, tk.E))
        
        self.btn_pos3 = ttk.Button(segunda_linha, text="Posição 3", 
                                  command=lambda: self.capturar_posicao(2), width=10)
        self.btn_pos3.grid(row=0, column=0, padx=(0, 5))
        
        self.btn_pos4 = ttk.Button(segunda_linha, text="Posição 4", 
                                  command=lambda: self.capturar_posicao(3), width=10)
        self.btn_pos4.grid(row=0, column=1, padx=(0, 5))
        
        ttk.Label(segunda_linha, text="Hotkey:").grid(row=0, column=2, padx=(10, 2))
        self.hotkey_var2 = tk.StringVar(value="f2")
        hotkey_entry2 = ttk.Entry(segunda_linha, textvariable=self.hotkey_var2, width=8)
        hotkey_entry2.grid(row=0, column=3, padx=(0, 5))
        
        # Botão único para atualizar ambas as hotkeys
        hotkey_update_frame = ttk.Frame(posicoes_frame)
        hotkey_update_frame.grid(row=2, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Button(hotkey_update_frame, text="Atualizar Hotkeys", 
                  command=self.atualizar_todas_hotkeys, width=15).grid(row=0, column=0)
        
        # Labels das posições - em linha separada
        labels_frame = ttk.Frame(posicoes_frame)
        labels_frame.grid(row=3, column=0, columnspan=2, pady=2, sticky=(tk.W, tk.E))
        
        self.label_pos1 = ttk.Label(labels_frame, text="Posição 1: Não definida")
        self.label_pos1.grid(row=0, column=0, padx=(0, 10), sticky=tk.W)
        
        self.label_pos2 = ttk.Label(labels_frame, text="Posição 2: Não definida")
        self.label_pos2.grid(row=0, column=1, padx=(0, 10), sticky=tk.W)
        
        self.label_pos3 = ttk.Label(labels_frame, text="Posição 3: Não definida")
        self.label_pos3.grid(row=1, column=0, padx=(0, 10), sticky=tk.W)
        
        self.label_pos4 = ttk.Label(labels_frame, text="Posição 4: Não definida")
        self.label_pos4.grid(row=1, column=1, sticky=tk.W)
        
        # Configurar grid weights para posicoes_frame
        posicoes_frame.columnconfigure(0, weight=1)
        
        # Status e controles - em uma linha
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=3, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        self.status_label = ttk.Label(status_frame, text="Status: Inativo", 
                                     foreground="red")
        self.status_label.grid(row=0, column=0, padx=(0, 10))
        
        self.btn_ativar = ttk.Button(status_frame, text="Ativar", 
                                   command=self.toggle_ativo, width=8)
        self.btn_ativar.grid(row=0, column=1, padx=(0, 5))
        
        ttk.Button(status_frame, text="Salvar", 
                  command=self.save_config, width=8).grid(row=0, column=2)
        
        # Configurar grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Bind para mudança de processo
        self.processo_combo.bind('<<ComboboxSelected>>', self.on_processo_selecionado)
    
    def atualizar_processos(self):
        """Atualiza a lista de processos disponíveis"""
        try:
            processos = []
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    info = proc.info
                    if info['name'] and info['exe']:
                        # Filtra apenas processos com janelas visíveis e nomes relevantes
                        nome_lower = info['name'].lower()
                        # Exclui processos de sistema e console
                        if (self.tem_janela_visivel(info['pid']) and 
                            'console' not in nome_lower and
                            'system' not in nome_lower and
                            'svchost' not in nome_lower and
                            any(keyword in nome_lower for keyword in ['exe', 'game', 'client', 'launcher', 'tibia', 'steam', 'discord', 'chrome', 'firefox', 'edge', 'notepad', 'word', 'excel', 'winrar', 'vlc', 'spotify', 'obs', 'photoshop'])):
                            # Tenta obter o nome da janela principal
                            nome_janela = self.obter_nome_janela(info['pid'])
                            if nome_janela:
                                processos.append(f"{nome_janela} (PID: {info['pid']})")
                            else:
                                processos.append(f"{info['name']} (PID: {info['pid']})")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Remove duplicatas e ordena
            processos = sorted(list(set(processos)))
            self.processos_disponiveis = processos
            
            # Atualiza o ComboBox
            self.processo_combo['values'] = processos
            
            if processos:
                self.processo_status.config(text=f"{len(processos)} aplicativos encontrados", 
                                          foreground="green")
            else:
                self.processo_status.config(text="Nenhum aplicativo encontrado", 
                                          foreground="red")
                
        except Exception as e:
            self.processo_status.config(text=f"Erro ao listar aplicativos: {e}", 
                                      foreground="red")
    
    def tem_janela_visivel(self, pid):
        """Verifica se o processo tem janelas visíveis"""
        try:
            # Método alternativo usando psutil para verificar se o processo tem janelas
            processo = psutil.Process(pid)
            # Verifica se o processo tem threads (indicativo de interface gráfica)
            return len(processo.threads()) > 1
        except:
            return True  # Se não conseguir verificar, assume que tem janela
    
    def obter_nome_janela(self, pid):
        """Obtém o nome da janela principal do processo"""
        try:
            import subprocess
            # Usa tasklist para obter informações detalhadas da janela
            result = subprocess.run(['tasklist', '/v', '/fi', f'PID eq {pid}'], 
                                  capture_output=True, text=True, shell=True)
            
            lines = result.stdout.split('\n')
            for line in lines:
                if str(pid) in line and 'Console' not in line:
                    # Procura por informações da janela na linha
                    parts = line.split()
                    # Procura por texto que não seja PID, memória ou outros dados técnicos
                    for part in parts:
                        # Filtra partes que parecem ser nomes de janela
                        if (len(part) > 3 and 
                            part not in [str(pid), 'N/A', 'Unknown', 'Running', 'Not', 'Responding'] and
                            not part.isdigit() and
                            not part.endswith('K') and  # Memória
                            not part.endswith('M') and  # Memória
                            'Console' not in part):
                            nome_janela = part.replace('"', '').strip()
                            if nome_janela and len(nome_janela) > 2:
                                return nome_janela[:40]  # Limita a 40 caracteres
            
            return None
        except:
            return None
    
    def on_processo_selecionado(self, event):
        """Chamado quando um processo é selecionado"""
        selecionado = self.processo_var.get()
        if selecionado:
            try:
                # Extrai o PID do texto selecionado
                pid = int(selecionado.split('PID: ')[1].split(')')[0])
                self.processo_selecionado = pid
                self.processo_status.config(text=f"Processo selecionado: {selecionado}", 
                                          foreground="green")
            except Exception as e:
                self.processo_status.config(text=f"Erro ao selecionar processo: {e}", 
                                          foreground="red")
    
    def verificar_processo_ativo(self):
        """Verifica se o processo selecionado ainda está ativo"""
        if not self.processo_selecionado:
            return True
            
        try:
            processo = psutil.Process(self.processo_selecionado)
            return processo.is_running()
        except psutil.NoSuchProcess:
            self.processo_status.config(text="Processo não encontrado - selecione outro", 
                                      foreground="red")
            return False
        except Exception as e:
            self.processo_status.config(text=f"Erro ao verificar processo: {e}", 
                                      foreground="red")
            return False
        
    def capturar_posicao(self, index):
        """Captura a posição atual do mouse"""
        # Garante que temos espaço suficiente no array
        while len(self.posicoes_runa) <= index:
            self.posicoes_runa.append(None)
        
        # Mostra contagem regressiva
        self.mostrar_contagem_regressiva(index)
        
    def mostrar_contagem_regressiva(self, index):
        """Mostra contagem regressiva antes de capturar"""
        if index == 0:
            self.label_pos1.config(text="Posição 1: Posicione o mouse...")
        elif index == 1:
            self.label_pos2.config(text="Posição 2: Posicione o mouse...")
        elif index == 2:
            self.label_pos3.config(text="Posição 3: Posicione o mouse...")
        elif index == 3:
            self.label_pos4.config(text="Posição 4: Posicione o mouse...")
        
        # Contagem regressiva de 3 segundos
        for i in range(3, 0, -1):
            self.root.after((3-i) * 1000, lambda i=i: self.atualizar_contagem(index, i))
        
        # Captura após 3 segundos
        self.root.after(3000, lambda: self._capturar_posicao_real(index))
    
    def atualizar_contagem(self, index, segundos):
        """Atualiza a contagem regressiva"""
        if index == 0:
            self.label_pos1.config(text=f"Posição 1: Capturando em {segundos}...")
        elif index == 1:
            self.label_pos2.config(text=f"Posição 2: Capturando em {segundos}...")
        elif index == 2:
            self.label_pos3.config(text=f"Posição 3: Capturando em {segundos}...")
        elif index == 3:
            self.label_pos4.config(text=f"Posição 4: Capturando em {segundos}...")
        
    def _capturar_posicao_real(self, index):
        """Captura a posição real do mouse após o delay"""
        pos = pyautogui.position()
        self.posicoes_runa[index] = pos
        
        if index == 0:
            self.label_pos1.config(text=f"Posição 1: {pos.x}, {pos.y}")
        elif index == 1:
            self.label_pos2.config(text=f"Posição 2: {pos.x}, {pos.y}")
        elif index == 2:
            self.label_pos3.config(text=f"Posição 3: {pos.x}, {pos.y}")
        elif index == 3:
            self.label_pos4.config(text=f"Posição 4: {pos.x}, {pos.y}")
            
        messagebox.showinfo("Posição Capturada", 
                           f"Posição {index + 1} capturada: {pos.x}, {pos.y}")
    
    def setup_hotkeys(self):
        """Configura as hotkeys do sistema"""
        try:
            # Remove hotkeys antigas se existirem
            keyboard.unhook_all()
            
            # Adiciona hotkeys para cada linha
            keyboard.add_hotkey(self.hotkeys_ativas[0], lambda: self.executar_acao_linha(0))
            keyboard.add_hotkey(self.hotkeys_ativas[1], lambda: self.executar_acao_linha(1))
            keyboard.add_hotkey(self.hotkey_captura, self.capturar_posicao_atual)
        except Exception as e:
            print(f"Erro ao configurar hotkeys: {e}")
    
    def atualizar_todas_hotkeys(self):
        """Atualiza todas as hotkeys de uma vez"""
        try:
            keyboard.unhook_all()
            
            # Atualiza hotkey 1
            nova_hotkey1 = self.hotkey_var1.get().lower().strip()
            self.hotkeys_ativas[0] = nova_hotkey1
            keyboard.add_hotkey(nova_hotkey1, lambda: self.executar_acao_linha(0))
            
            # Atualiza hotkey 2
            nova_hotkey2 = self.hotkey_var2.get().lower().strip()
            self.hotkeys_ativas[1] = nova_hotkey2
            keyboard.add_hotkey(nova_hotkey2, lambda: self.executar_acao_linha(1))
            
            # Adiciona hotkey de captura
            keyboard.add_hotkey(self.hotkey_captura, self.capturar_posicao_atual)
            
            messagebox.showinfo("Hotkeys Atualizadas", 
                              f"Hotkey 1: {nova_hotkey1}\nHotkey 2: {nova_hotkey2}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao configurar hotkeys: {e}")
    
    def atualizar_hotkey(self, linha):
        """Método antigo - redireciona para atualizar todas"""
        self.atualizar_todas_hotkeys()
    
    def executar_acao_linha(self, linha):
        """Executa a ação para uma linha específica"""
        if not self.ativo:
            return
            
        # Verifica se o processo selecionado ainda está ativo
        if not self.verificar_processo_ativo():
            return
        
        # Define quais posições usar baseado na linha
        if linha == 0:  # Primeira linha - posições 0 e 1
            posicoes_usar = [self.posicoes_runa[0], self.posicoes_runa[1]]
        else:  # Segunda linha - posições 2 e 3
            posicoes_usar = [self.posicoes_runa[2], self.posicoes_runa[3]]
        
        # Verifica se as posições estão definidas
        if not all(posicoes_usar):
            return
            
        # Salva posição atual do mouse
        self.mouse_original_pos = pyautogui.position()
        
        # Escolhe uma posição aleatória das posições da linha
        posicao_escolhida = random.choice(posicoes_usar)
        
        # Adiciona randomização de pixels
        offset_x = random.randint(-2, 2)
        offset_y = random.randint(-2, 2)
        posicao_final = (posicao_escolhida.x + offset_x, posicao_escolhida.y + offset_y)
        
        # Move o mouse de forma humana até a posição da runa
        self.mover_mouse_humano(posicao_final)
        
        # Delay humano antes do clique
        time.sleep(random.uniform(0.05, 0.12))
        
        # Clique direito na posição exata
        pyautogui.rightClick(posicao_final[0], posicao_final[1])
        
        # Delay humano após o clique
        time.sleep(random.uniform(0.08, 0.18))
        
        # Retorna o mouse para a posição original com variação humana
        self.retornar_mouse_original()
    
    def executar_acao(self):
        """Executa a ação principal do aplicativo"""
        if not self.ativo or len(self.posicoes_runa) < 2 or not all(self.posicoes_runa):
            return
            
        # Verifica se o processo selecionado ainda está ativo
        if not self.verificar_processo_ativo():
            return
            
        # Salva posição atual do mouse
        self.mouse_original_pos = pyautogui.position()
        
        # Escolhe uma posição aleatória
        posicao_escolhida = random.choice(self.posicoes_runa)
        
        # Adiciona randomização de pixels
        offset_x = random.randint(-2, 2)
        offset_y = random.randint(-2, 2)
        posicao_final = (posicao_escolhida.x + offset_x, posicao_escolhida.y + offset_y)
        
        # Move o mouse de forma humana até a posição da runa
        self.mover_mouse_humano(posicao_final)
        
        # Delay humano antes do clique
        time.sleep(random.uniform(0.05, 0.12))
        
        # Clique direito na posição exata
        pyautogui.rightClick(posicao_final[0], posicao_final[1])
        
        # Delay humano após o clique
        time.sleep(random.uniform(0.08, 0.18))
        
        # Retorna o mouse para a posição original com variação humana
        self.retornar_mouse_original()
    
    def mover_mouse_humano(self, destino):
        """Move o mouse de forma rápida e humana"""
        inicio = pyautogui.position()
        
        # Movimento mais rápido - menos pontos intermediários
        pontos_intermediarios = random.randint(1, 2)
        for i in range(1, pontos_intermediarios + 1):
            progresso = i / (pontos_intermediarios + 1)
            
            # Curva menor e mais rápida
            curva_x = random.randint(-3, 3)
            curva_y = random.randint(-3, 3)
            
            x = inicio.x + (destino[0] - inicio.x) * progresso + curva_x
            y = inicio.y + (destino[1] - inicio.y) * progresso + curva_y
            
            # Duração muito mais rápida
            duracao = random.uniform(0.005, 0.015)
            pyautogui.moveTo(x, y, duration=duracao)
            time.sleep(random.uniform(0.003, 0.008))
        
        # Move para a posição final rapidamente
        final_x = destino[0] + random.randint(-1, 1)
        final_y = destino[1] + random.randint(-1, 1)
        pyautogui.moveTo(final_x, final_y, duration=random.uniform(0.005, 0.012))
    
    def retornar_mouse_original(self):
        """Retorna o mouse para a posição original com variação humana"""
        if self.mouse_original_pos:
            # Variação maior para parecer mais humano
            offset_x = random.randint(-5, 5)
            offset_y = random.randint(-5, 5)
            posicao_retorno = (self.mouse_original_pos.x + offset_x, 
                              self.mouse_original_pos.y + offset_y)
            
            # Move de forma humana de volta
            self.mover_mouse_humano(posicao_retorno)
            
            # Pequeno delay final para simular pausa humana
            time.sleep(random.uniform(0.02, 0.08))
    
    def capturar_posicao_atual(self):
        """Captura a posição atual do mouse via hotkey"""
        pos = pyautogui.position()
        messagebox.showinfo("Posição Atual", f"Mouse em: {pos.x}, {pos.y}")
    
    def toggle_ativo(self):
        """Ativa/desativa o sistema"""
        self.ativo = not self.ativo
        
        if self.ativo:
            self.status_label.config(text="Status: Ativo", foreground="green")
            self.btn_ativar.config(text="Desativar")
        else:
            self.status_label.config(text="Status: Inativo", foreground="red")
            self.btn_ativar.config(text="Ativar")
    
    def save_config(self):
        """Salva as configurações em arquivo"""
        config = {
            'posicoes_runa': [(pos.x, pos.y) if pos else None for pos in self.posicoes_runa],
            'hotkey_ativa': self.hotkey_var.get(),
            'ativo': self.ativo,
            'processo_selecionado': self.processo_selecionado
        }
        
        try:
            with open('config_addee.json', 'w') as f:
                json.dump(config, f)
            messagebox.showinfo("Sucesso", "Configurações salvas!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")
    
    def load_config(self):
        """Carrega as configurações do arquivo"""
        try:
            if os.path.exists('config_addee.json'):
                with open('config_addee.json', 'r') as f:
                    config = json.load(f)
                
                # Carrega posições
                self.posicoes_runa = []
                for pos in config.get('posicoes_runa', []):
                    if pos:
                        self.posicoes_runa.append(pyautogui.Point(pos[0], pos[1]))
                    else:
                        self.posicoes_runa.append(None)
                
                # Atualiza labels
                if len(self.posicoes_runa) > 0 and self.posicoes_runa[0]:
                    self.label_pos1.config(text=f"Posição 1: {self.posicoes_runa[0].x}, {self.posicoes_runa[0].y}")
                
                if len(self.posicoes_runa) > 1 and self.posicoes_runa[1]:
                    self.label_pos2.config(text=f"Posição 2: {self.posicoes_runa[1].x}, {self.posicoes_runa[1].y}")
                
                # Carrega hotkey
                self.hotkey_ativa = config.get('hotkey_ativa', 'ctrl')
                self.hotkey_var.set(self.hotkey_ativa)
                
                # Carrega processo selecionado
                processo_salvo = config.get('processo_selecionado')
                if processo_salvo:
                    self.processo_selecionado = processo_salvo
                    # Tenta encontrar o processo na lista atual
                    for processo in self.processos_disponiveis:
                        if f"PID: {processo_salvo}" in processo:
                            self.processo_var.set(processo)
                            self.processo_status.config(text=f"Processo restaurado: {processo}", 
                                                      foreground="green")
                            break
                
                # Carrega status
                self.ativo = config.get('ativo', False)
                if self.ativo:
                    self.status_label.config(text="Status: Ativo", foreground="green")
                    self.btn_ativar.config(text="Desativar")
                
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
    
    def run(self):
        """Inicia o aplicativo"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.root.quit()

if __name__ == "__main__":
    # Configurações anti-detecção adicionais
    import ctypes
    try:
        # Tenta ocultar a janela do console se existir
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except:
        pass
    
    app = ConexaoRemotaADDEE()
    app.run()
