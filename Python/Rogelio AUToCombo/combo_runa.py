#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Combo Runa - Versão Python
Conversão do script AutoHotkey para Python
"""

import tkinter as tk
from tkinter import ttk, messagebox
import configparser
import threading
import time
import random
import pyautogui
import keyboard
import sys
import os
from PIL import ImageGrab
import win32gui
import win32con

class ComboRunaApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Combo Runa")
        self.root.geometry("320x620")
        self.root.resizable(False, False)
        
        # Variáveis globais
        self.runa_x = 0
        self.runa_y = 0
        self.alvo_x = 0
        self.alvo_y = 0
        self.delay = 100
        self.capture_mode = ""
        self.selected_rune = "Runa 1"
        self.ini_file = "config.ini"
        self.script_ativo = True
        self.random_offset = 5
        
        # Estado dos botões 1-5 (ativo/inativo)
        self.rune_buttons_active = {
            "Runa 1": True,
            "Runa 2": True, 
            "Runa 3": True,
            "Runa 4": True,
            "Runa 5": True
        }
        
        # Estado da janela (normal/minimizada)
        self.window_minimized = False
        self.mini_window = None
        
        
        # Configurações do pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
        # Configuração INI
        self.config = configparser.ConfigParser()
        self.load_config()
        
        # Interface gráfica
        self.create_gui()
        
        # Hotkeys
        print("🔧 Debug: Iniciando configuração de hotkeys...")
        self.setup_hotkeys()
        print("🔧 Debug: Configuração de hotkeys concluída")
        
        # Timer para auto combo
        self.auto_combo_timer = None
        
        # Timer para captura de posições
        self.capture_timer = None
        self.capture_countdown = 0
        
    def create_gui(self):
        """Cria a interface gráfica"""
        # Título
        title_label = tk.Label(self.root, text="COMBO RUNA - Clique Direito/Esquerdo", 
                              font=("Arial", 10, "bold"))
        title_label.pack(pady=10)
        
        # Linha separadora
        separator1 = ttk.Separator(self.root, orient='horizontal')
        separator1.pack(fill='x', padx=10, pady=5)
        
        # Sistema de abas para runas
        tk.Label(self.root, text="Selecione a runa:", font=('Arial', 10, 'bold')).pack(anchor='w', padx=10, pady=(10, 5))
        
        # Frame para as abas das runas
        self.tabs_frame = tk.Frame(self.root)
        self.tabs_frame.pack(fill='x', padx=10, pady=5)
        
        # Criar abas para cada runa
        self.rune_tabs = {}
        self.selected_rune = "Runa 1"
        
        # Frame centralizado para os botões
        buttons_container = tk.Frame(self.tabs_frame)
        buttons_container.pack(expand=True)
        
        for i in range(1, 6):
            runa_name = f"Runa {i}"
            tab = tk.Button(buttons_container, text=str(i), width=4, height=2,
                          font=('Arial', 10, 'bold'),
                          command=lambda r=runa_name: self.select_rune_tab(r))
            tab.pack(side='left', padx=2)
            self.rune_tabs[runa_name] = tab
            
            # Cria atributo único para cada botão para poder atualizar aparência
            setattr(self, f'rune_button_{i}', tab)
        
        
        # Frame para posições marcadas
        positions_frame = tk.LabelFrame(self.root, text="Posições Marcadas", padx=5, pady=5)
        positions_frame.pack(fill='x', padx=10, pady=10)
        
        self.txt_rune_pos = tk.Label(positions_frame, text="Runa: (não marcada)", anchor='w')
        self.txt_rune_pos.pack(fill='x', pady=2)
        
        self.txt_alvo_pos = tk.Label(positions_frame, text="Alvo: (não marcada)", anchor='w')
        self.txt_alvo_pos.pack(fill='x', pady=2)
        
        
        # Botões de marcação
        buttons_frame = tk.Frame(self.root)
        buttons_frame.pack(fill='x', padx=10, pady=(10, 15))
        
        self.rune_button = tk.Button(buttons_frame, text="🎯 Marcar Runa (8)", 
                                    command=self.marcar_runa, width=15, height=2,
                                    bg='#2196F3', fg='white', font=('Arial', 9, 'bold'),
                                    relief='raised', bd=2)
        self.rune_button.pack(side='left', padx=5)
        
        self.target_button = tk.Button(buttons_frame, text="🎯 Marcar Alvo (9)", 
                                      command=self.marcar_alvo, width=15, height=2,
                                      bg='#FF9800', fg='white', font=('Arial', 9, 'bold'),
                                      relief='raised', bd=2)
        self.target_button.pack(side='left', padx=5)
        
        # Frame para configurações
        config_frame = tk.LabelFrame(self.root, text="Configurações", padx=5, pady=5)
        config_frame.pack(fill='x', padx=10, pady=10)
        
        # Delay
        delay_frame = tk.Frame(config_frame)
        delay_frame.pack(fill='x', pady=2)
        tk.Label(delay_frame, text="Delay (ms):").pack(side='left')
        self.delay_var = tk.StringVar(value=str(self.delay))
        self.delay_entry = tk.Entry(delay_frame, textvariable=self.delay_var, width=10)
        self.delay_entry.pack(side='right')
        
        # Randomização
        random_frame = tk.Frame(config_frame)
        random_frame.pack(fill='x', pady=2)
        tk.Label(random_frame, text="Randomização:").pack(side='left')
        self.random_var = tk.StringVar(value=str(self.random_offset))
        self.random_entry = tk.Entry(random_frame, textvariable=self.random_var, width=10)
        self.random_entry.pack(side='right')
        tk.Label(random_frame, text="pixels").pack(side='right', padx=(5, 0))
        
        
        
        # Botões de configuração
        config_buttons_frame = tk.Frame(self.root)
        config_buttons_frame.pack(fill='x', padx=10, pady=(10, 15))
        
        tk.Button(config_buttons_frame, text="Salvar Config", 
                 command=self.salvar_config).pack(side='left', padx=2)
        tk.Button(config_buttons_frame, text="Carregar Config", 
                 command=self.carregar_config).pack(side='right', padx=2)
        
        # Status
        self.status_label = tk.Label(self.root, text="Script: ATIVO", 
                                    relief='sunken', anchor='center', height=2, bg='lightgreen')
        self.status_label.pack(fill='x', padx=10, pady=(10, 15))
        
        # Botão de ativar/desativar
        self.toggle_button = tk.Button(self.root, text="⏸️ DESATIVAR SCRIPT", 
                                      command=self.toggle_script, height=2, 
                                      bg='#f44336', fg='white', font=('Arial', 10, 'bold'))
        self.toggle_button.pack(fill='x', padx=10, pady=(0, 10))
        
        # Botão de minimizar/maximizar
        self.minimize_button = tk.Button(self.root, text="📱 MINIMIZAR", 
                                        command=self.toggle_window_mode, height=2, 
                                        bg='#2196F3', fg='white', font=('Arial', 10, 'bold'))
        self.minimize_button.pack(fill='x', padx=10, pady=(0, 10))
        
        # Hotkeys info
        hotkeys_label = tk.Label(self.root, 
                                text="Hotkeys: Numpad 1-5 executar runas (se botão ativo), 8/9 marcar, Botões 1-5 toggle ativo/inativo",
                                font=('Arial', 8), wraplength=300, justify='center')
        hotkeys_label.pack(pady=(5, 20))
        
        # Carregar configurações iniciais
        self.carregar_configuracao_runa()
        self.carregar_posicoes()
        
        # Carregar estado dos botões
        self.carregar_estado_botoes()
        
        # Atualizar aparência das abas
        self.update_selected_tab()
        
        # Teste de hotkeys após um pequeno delay
        self.root.after(1000, self.testar_hotkeys)
        
    def setup_hotkeys(self):
        """Configura as hotkeys"""
        try:
            # Remove hotkeys existentes primeiro
            keyboard.unhook_all()
            print("🔧 Debug: Hotkeys anteriores removidas")
            
            # Configuração simples e direta
            print("🔧 Debug: Configurando hotkeys...")
            
            # Hotkeys principais - apenas as essenciais
            keyboard.add_hotkey('numpad 1', lambda: self.executar_runa_direta("Runa 1"))
            keyboard.add_hotkey('numpad 2', lambda: self.executar_runa_direta("Runa 2"))
            keyboard.add_hotkey('numpad 3', lambda: self.executar_runa_direta("Runa 3"))
            keyboard.add_hotkey('numpad 4', lambda: self.executar_runa_direta("Runa 4"))
            keyboard.add_hotkey('numpad 5', lambda: self.executar_runa_direta("Runa 5"))
            keyboard.add_hotkey('numpad 8', self.numpad8_handler)
            keyboard.add_hotkey('numpad 9', self.numpad9_handler)
            
            print("✅ Hotkeys principais configuradas")
            
            # Fallback com teclas básicas
            keyboard.add_hotkey('1', lambda: self.executar_runa_direta("Runa 1"))
            keyboard.add_hotkey('2', lambda: self.executar_runa_direta("Runa 2"))
            keyboard.add_hotkey('3', lambda: self.executar_runa_direta("Runa 3"))
            keyboard.add_hotkey('4', lambda: self.executar_runa_direta("Runa 4"))
            keyboard.add_hotkey('5', lambda: self.executar_runa_direta("Runa 5"))
            keyboard.add_hotkey('8', self.numpad8_handler)
            keyboard.add_hotkey('9', self.numpad9_handler)
            
            print("✅ Hotkeys de fallback configuradas")
            
            # Variações adicionais para garantir funcionamento
            keyboard.add_hotkey('num 1', lambda: self.executar_runa_direta("Runa 1"))
            keyboard.add_hotkey('num 2', lambda: self.executar_runa_direta("Runa 2"))
            keyboard.add_hotkey('num 3', lambda: self.executar_runa_direta("Runa 3"))
            keyboard.add_hotkey('num 4', lambda: self.executar_runa_direta("Runa 4"))
            keyboard.add_hotkey('num 5', lambda: self.executar_runa_direta("Runa 5"))
            
            print("✅ Hotkeys num configuradas")
            
            # Variações com shift para garantir funcionamento
            keyboard.add_hotkey('shift+1', lambda: self.executar_runa_direta("Runa 1"))
            keyboard.add_hotkey('shift+2', lambda: self.executar_runa_direta("Runa 2"))
            keyboard.add_hotkey('shift+3', lambda: self.executar_runa_direta("Runa 3"))
            keyboard.add_hotkey('shift+4', lambda: self.executar_runa_direta("Runa 4"))
            keyboard.add_hotkey('shift+5', lambda: self.executar_runa_direta("Runa 5"))
            
            print("✅ Hotkeys shift configuradas")
            
            # Teste específico da hotkey 4
            print("🔧 Debug: Testando hotkey 4 especificamente...")
            try:
                # Testa se a hotkey 4 foi registrada
                print("🔧 Debug: Hotkey 4 registrada com sucesso")
            except Exception as e:
                print(f"🔧 Debug: Erro ao registrar hotkey 4: {e}")
            
            print("✅ Todas as hotkeys configuradas com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro ao configurar hotkeys: {e}")
            # Fallback básico
            try:
                keyboard.add_hotkey('1', lambda: self.executar_runa_direta("Runa 1"))
                keyboard.add_hotkey('2', lambda: self.executar_runa_direta("Runa 2"))
                keyboard.add_hotkey('3', lambda: self.executar_runa_direta("Runa 3"))
                keyboard.add_hotkey('4', lambda: self.executar_runa_direta("Runa 4"))
                keyboard.add_hotkey('5', lambda: self.executar_runa_direta("Runa 5"))
                print("✅ Hotkeys básicas configuradas como fallback")
            except Exception as e2:
                print(f"❌ Erro no fallback: {e2}")
    
    def load_config(self):
        """Carrega configurações do arquivo INI"""
        if os.path.exists(self.ini_file):
            self.config.read(self.ini_file, encoding='utf-8')
        else:
            # Cria configuração padrão
            self.config['Config'] = {
                'Delay': '100',
                'RandomOffset': '5'
            }
    
    def save_config(self):
        """Salva configurações no arquivo INI"""
        with open(self.ini_file, 'w', encoding='utf-8') as f:
            self.config.write(f)
    
    def select_rune_tab(self, runa_name):
        """Toggle do botão da runa (ativa/desativa)"""
        timestamp = time.strftime('%H:%M:%S')
        
        # Alterna o estado do botão
        self.rune_buttons_active[runa_name] = not self.rune_buttons_active[runa_name]
        
        print(f"🔧 Debug: [{timestamp}] 🔄 BOTÃO TOGGLE PRESSIONADO")
        print(f"🔧 Debug: Runa: {runa_name}")
        print(f"🔧 Debug: Estado anterior: {not self.rune_buttons_active[runa_name]}")
        print(f"🔧 Debug: Estado atual: {self.rune_buttons_active[runa_name]}")
        
        # Atualiza a aparência do botão
        self.update_rune_button_appearance(runa_name)
        
        # Atualiza também os botões da janela minimizada
        self.update_mini_buttons_appearance()
        
        # Salva o estado no config
        self.salvar_estado_botoes()
        
        # Mostra feedback
        if self.rune_buttons_active[runa_name]:
            print(f"🔧 Debug: ✅ Botão {runa_name} ATIVADO")
            self.show_tooltip(f"✅ {runa_name} ATIVADA")
        else:
            print(f"🔧 Debug: ⏸️ Botão {runa_name} DESATIVADO")
            self.show_tooltip(f"⏸️ {runa_name} DESATIVADA")
        
    def update_rune_button_appearance(self, runa_name):
        """Atualiza a aparência do botão da runa baseado no estado"""
        button_number = runa_name[-1]  # Extrai o número da runa
        button = getattr(self, f'rune_button_{button_number}', None)
        
        if button:
            if self.rune_buttons_active[runa_name]:
                # Botão ativo - verde
                button.config(bg='#4CAF50', fg='white', relief='solid', bd=3)
                button.config(text=f"✅ {button_number}")
            else:
                # Botão inativo - vermelho
                button.config(bg='#f44336', fg='white', relief='solid', bd=3)
                button.config(text=f"❌ {button_number}")
    
    def salvar_estado_botoes(self):
        """Salva o estado dos botões no config.ini"""
        try:
            if 'RuneButtons' not in self.config:
                self.config['RuneButtons'] = {}
            
            for runa_name, estado in self.rune_buttons_active.items():
                self.config['RuneButtons'][runa_name] = str(estado)
            
            self.save_config()
            print(f"🔧 Debug: Estado dos botões salvo: {self.rune_buttons_active}")
        except Exception as e:
            print(f"🔧 Debug: Erro ao salvar estado dos botões: {e}")
    
    def carregar_estado_botoes(self):
        """Carrega o estado dos botões do config.ini"""
        try:
            if 'RuneButtons' in self.config:
                for runa_name in self.rune_buttons_active.keys():
                    estado_str = self.config.get('RuneButtons', runa_name, fallback='True')
                    self.rune_buttons_active[runa_name] = estado_str.lower() == 'true'
                
                print(f"🔧 Debug: Estado dos botões carregado: {self.rune_buttons_active}")
                
                # Atualiza a aparência de todos os botões
                for runa_name in self.rune_buttons_active.keys():
                    self.update_rune_button_appearance(runa_name)
                
                # Atualiza também os botões da janela minimizada se existir
                self.update_mini_buttons_appearance()
            else:
                print(f"🔧 Debug: Seção RuneButtons não encontrada - usando padrões")
        except Exception as e:
            print(f"🔧 Debug: Erro ao carregar estado dos botões: {e}")
    
    def update_selected_tab(self):
        """Atualiza a aparência das abas para mostrar qual está selecionada"""
        for runa_name, tab in self.rune_tabs.items():
            if runa_name == self.selected_rune:
                # Destaque para a runa selecionada
                tab.config(bg='#2196F3', fg='white', relief='solid', bd=3)
            else:
                # Aparência normal para as outras
                tab.config(bg='#f0f0f0', fg='black', relief='raised', bd=1)
    
    def toggle_window_mode(self):
        """Alterna entre janela normal e minimizada"""
        timestamp = time.strftime('%H:%M:%S')
        print(f"🔧 Debug: [{timestamp}] 🔄 TOGGLE JANELA PRESSIONADO")
        
        if self.window_minimized:
            # Maximizar (voltar para janela normal)
            self.maximize_window()
        else:
            # Minimizar (criar janela pequena)
            self.minimize_window()
    
    def minimize_window(self):
        """Minimiza para janela pequena com apenas os números"""
        timestamp = time.strftime('%H:%M:%S')
        print(f"🔧 Debug: [{timestamp}] 📱 MINIMIZANDO JANELA")
        
        # Esconde a janela principal
        self.root.withdraw()
        
        # Cria janela minimizada
        self.mini_window = tk.Toplevel()
        self.mini_window.title("Combo Runa - Mini")
        self.mini_window.geometry("200x80")
        self.mini_window.resizable(False, False)
        
        # Configurações da janela minimizada
        self.mini_window.attributes('-topmost', True)  # Sempre no topo
        self.mini_window.attributes('-alpha', 0.8)     # Transparência
        
        # Remove bordas da janela para ficar mais limpa
        self.mini_window.overrideredirect(True)
        
        # Frame principal
        main_frame = tk.Frame(self.mini_window, bg='#2c3e50')
        main_frame.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Título
        title_label = tk.Label(main_frame, text="COMBO RUNA", 
                              bg='#2c3e50', fg='white', font=('Arial', 8, 'bold'))
        title_label.pack(pady=(5, 2))
        
        # Frame para os botões
        buttons_frame = tk.Frame(main_frame, bg='#2c3e50')
        buttons_frame.pack(pady=2)
        
        # Cria botões 1-5 na janela minimizada
        self.mini_buttons = {}
        for i in range(1, 6):
            runa_name = f"Runa {i}"
            button = tk.Button(buttons_frame, text=str(i), width=3, height=1,
                              font=('Arial', 8, 'bold'),
                              command=lambda r=runa_name: self.select_rune_tab(r))
            button.pack(side='left', padx=1)
            self.mini_buttons[runa_name] = button
        
        # Atualiza aparência dos botões na janela minimizada
        self.update_mini_buttons_appearance()
        
        # Botão de maximizar
        maximize_button = tk.Button(main_frame, text="📱", width=3, height=1,
                                   font=('Arial', 8),
                                   command=self.maximize_window,
                                   bg='#3498db', fg='white')
        maximize_button.pack(side='right', padx=2, pady=2)
        
        # Botão de fechar
        close_button = tk.Button(main_frame, text="❌", width=3, height=1,
                                font=('Arial', 8),
                                command=self.close_mini_window,
                                bg='#e74c3c', fg='white')
        close_button.pack(side='right', padx=2, pady=2)
        
        # Permite arrastar a janela
        self.make_window_draggable(self.mini_window, main_frame)
        
        self.window_minimized = True
        self.minimize_button.config(text="📱 MAXIMIZAR")
        
        print(f"🔧 Debug: ✅ Janela minimizada criada")
    
    def maximize_window(self):
        """Maximiza para janela normal"""
        timestamp = time.strftime('%H:%M:%S')
        print(f"🔧 Debug: [{timestamp}] 📱 MAXIMIZANDO JANELA")
        
        # Destroi janela minimizada
        if self.mini_window:
            self.mini_window.destroy()
            self.mini_window = None
        
        # Mostra janela principal
        self.root.deiconify()
        
        self.window_minimized = False
        self.minimize_button.config(text="📱 MINIMIZAR")
        
        print(f"🔧 Debug: ✅ Janela maximizada")
    
    def close_mini_window(self):
        """Fecha a janela minimizada e volta para a principal"""
        timestamp = time.strftime('%H:%M:%S')
        print(f"🔧 Debug: [{timestamp}] ❌ FECHANDO JANELA MINIMIZADA")
        
        self.maximize_window()
    
    def update_mini_buttons_appearance(self):
        """Atualiza a aparência dos botões na janela minimizada"""
        if not self.mini_window or not hasattr(self, 'mini_buttons'):
            return
        
        for runa_name, button in self.mini_buttons.items():
            if self.rune_buttons_active[runa_name]:
                # Botão ativo - verde
                button.config(bg='#27ae60', fg='white', relief='solid', bd=1)
            else:
                # Botão inativo - vermelho
                button.config(bg='#e74c3c', fg='white', relief='solid', bd=1)
    
    def make_window_draggable(self, window, widget):
        """Torna a janela arrastável"""
        def start_move(event):
            window.x = event.x
            window.y = event.y
        
        def stop_move(event):
            window.x = None
            window.y = None
        
        def on_motion(event):
            if window.x is not None and window.y is not None:
                deltax = event.x - window.x
                deltay = event.y - window.y
                x = window.winfo_x() + deltax
                y = window.winfo_y() + deltay
                window.geometry(f"+{x}+{y}")
        
        widget.bind("<Button-1>", start_move)
        widget.bind("<ButtonRelease-1>", stop_move)
        widget.bind("<B1-Motion>", on_motion)
    
    def toggle_script(self):
        """Alterna o estado do script via botão"""
        timestamp = time.strftime('%H:%M:%S')
        print(f"🔧 Debug: [{timestamp}] 🔄 BOTÃO TOGGLE PRESSIONADO")
        print(f"🔧 Debug: script_ativo antes = {self.script_ativo}")
        
        self.script_ativo = not self.script_ativo
        print(f"🔧 Debug: script_ativo depois = {self.script_ativo}")
        
        if self.script_ativo:
            self.status_label.config(text="Script: ATIVO", bg='lightgreen')
            self.toggle_button.config(text="⏸️ DESATIVAR SCRIPT", bg='#f44336')
            print(f"🔧 Debug: ✅ Script ATIVADO")
            self.show_tooltip("✅ Script ATIVADO")
        else:
            self.status_label.config(text="Script: PARADO", bg='lightcoral')
            self.toggle_button.config(text="▶️ ATIVAR SCRIPT", bg='#4CAF50')
            print(f"🔧 Debug: ⏸️ Script DESATIVADO")
            self.show_tooltip("⏸️ Script DESATIVADO")
            
            # Para também o timer de captura se estiver rodando
            self.stop_capture_timer()
            # Limpa modo de captura se estiver ativo
            if self.capture_mode:
                self.capture_mode = ""
                self.rune_button.config(text="🎯 Marcar Runa (8)")
                self.target_button.config(text="🎯 Marcar Alvo (9)")
                self.show_tooltip("🛑 Captura cancelada - Script desativado")
        
        # Salva o estado do script
        try:
            if 'Config' not in self.config:
                self.config['Config'] = {}
            self.config['Config']['ScriptAtivo'] = str(self.script_ativo)
            self.save_config()
            print(f"🔧 Debug: Estado do script salvo: {self.script_ativo}")
        except Exception as e:
            print(f"🔧 Debug: Erro ao salvar estado: {e}")
    
    def executar_runa_direta(self, runa_name):
        """Executa uma runa diretamente via hotkey"""
        timestamp = time.strftime('%H:%M:%S')
        print(f"🔧 Debug: [{timestamp}] 🔥🔥🔥 HOTKEY PRESSIONADA 🔥🔥🔥")
        print(f"🔧 Debug: Tecla: {runa_name}")
        print(f"🔧 Debug: Script ativo: {self.script_ativo}")
        print(f"🔧 Debug: Botão {runa_name} ativo: {self.rune_buttons_active.get(runa_name, False)}")
        
        if not self.script_ativo:
            print(f"🔧 Debug: ❌ Script desativado - {runa_name} não executada")
            return
        
        if not self.rune_buttons_active.get(runa_name, False):
            print(f"🔧 Debug: ❌ Botão {runa_name} desativado - hotkey não executada")
            return
        
        print(f"🔧 Debug: ✅ Script ativo e botão ativo - Executando {runa_name}...")
        
        # Salva configurações da runa atual antes de trocar
        self.salvar_configuracao_runa_atual()
        
        # Troca para nova runa
        self.selected_rune = runa_name
        
        # Carrega configurações da nova runa
        self.carregar_configuracao_runa()
        self.carregar_posicoes()
        
        # Atualiza interface para mostrar a runa selecionada
        self.update_selected_tab()
        
        print(f"🔧 Debug: Runa trocada para: {self.selected_rune}")
        
        # Executa a runa usando a função usar_runa
        self.usar_runa()
        
        print(f"🔧 Debug: [{timestamp}] ⚡ RUNA EXECUTADA VIA HOTKEY")
        print(f"🔧 Debug: Runa: {runa_name}")
        print(f"🔧 Debug: Hotkey ativada - execução via usar_runa")
    
    def salvar_configuracao_runa_atual(self):
        """Salva as configurações da runa atual"""
        try:
            if self.selected_rune not in self.config:
                self.config[self.selected_rune] = {}
            
            # Salva delay e randomização específicos da runa
            self.config[self.selected_rune]['Delay'] = str(self.delay_var.get() if self.delay_var.get() else 100)
            self.config[self.selected_rune]['RandomOffset'] = str(self.random_var.get() if self.random_var.get() else 5)
            
            self.save_config()
        except Exception as e:
            print(f"Erro ao salvar configuração da runa: {e}")
    
    def carregar_configuracao_runa(self):
        """Carrega as configurações específicas da runa selecionada"""
        try:
            # Carrega delay específico da runa (ou usa padrão)
            delay = self.config.get(self.selected_rune, 'Delay', fallback='100')
            self.delay_var.set(delay)
            
            # Carrega randomização específica da runa (ou usa padrão)
            random_offset = self.config.get(self.selected_rune, 'RandomOffset', fallback='5')
            self.random_var.set(random_offset)
            
            
            
        except Exception as e:
            print(f"Erro ao carregar configuração da runa: {e}")
            # Valores padrão em caso de erro
            self.delay_var.set('100')
            self.random_var.set('5')
    
    
    def testar_hotkeys(self):
        """Testa se as hotkeys estão funcionando"""
        print("🔧 Debug: Testando hotkeys...")
        try:
            # Testa se o módulo keyboard está funcionando
            import keyboard
            print("✅ Módulo keyboard importado com sucesso")
            
            # Lista hotkeys registradas
            print("🔧 Debug: Hotkeys registradas:")
            try:
                for hotkey in keyboard._hotkeys:
                    print(f"  - {hotkey}")
            except:
                print("  - Não foi possível listar hotkeys")
            
            # Teste manual das funções
            print("🔧 Debug: Testando executar_runa_direta manualmente...")
            self.executar_runa_direta("Runa 1")
            
            print("🔧 Debug: Testando hotkey 4 especificamente...")
            self.executar_runa_direta("Runa 4")
            
            print("🔧 Debug: Testando toggle_script manualmente...")
            self.toggle_script()
            
            print("✅ Teste de hotkeys concluído!")
            print("🔧 Debug: Se as hotkeys não funcionarem, verifique:")
            print("  - Se o módulo keyboard está instalado")
            print("  - Se há conflitos com outros programas")
            print("  - Se as teclas estão sendo capturadas pelo sistema")
            
        except Exception as e:
            print(f"❌ Erro no teste de hotkeys: {e}")
    
    
    def marcar_runa(self):
        """Alterna modo de captura da runa"""
        if not self.script_ativo:
            return
            
        if self.capture_mode == "runa":
            self.capture_mode = ""
            self.rune_button.config(text="🎯 Marcar Runa (8)")
            self.show_tooltip("")
        else:
            self.capture_mode = "runa"
            self.rune_button.config(text="CANCELAR (8)")
            self.show_tooltip("🎯 Posicione mouse sobre RUNA - captura automática em 3s")
            # Inicia timer de 3 segundos
            self.start_capture_timer("runa")
    
    def marcar_alvo(self):
        """Alterna modo de captura do alvo"""
        if not self.script_ativo:
            return
            
        if self.capture_mode == "alvo":
            self.capture_mode = ""
            self.target_button.config(text="🎯 Marcar Alvo (9)")
            self.show_tooltip("")
        else:
            self.capture_mode = "alvo"
            self.target_button.config(text="CANCELAR (9)")
            self.show_tooltip("🎯 Posicione mouse sobre ALVO - captura automática em 3s")
            # Inicia timer de 3 segundos
            self.start_capture_timer("alvo")
    
    
    def usar_runa(self):
        """Executa o combo da runa selecionada - Versão simplificada"""
        timestamp = time.strftime('%H:%M:%S')
        print(f"🔧 Debug: [{timestamp}] 🎯 USAR RUNA CHAMADA")
        print(f"🔧 Debug: Runa selecionada: {self.selected_rune}")
        print(f"🔧 Debug: Script ativo: {self.script_ativo}")
        
        if not self.script_ativo:
            print(f"🔧 Debug: Script desativado - usar_runa cancelada")
            return
        
        # Obtém posições da runa selecionada
        rp = self.config.get(self.selected_rune, 'RunePos', fallback='')
        tp = self.config.get(self.selected_rune, 'TargetPos', fallback='')
        
        print(f"🔧 Debug: Posição da runa: {rp}")
        print(f"🔧 Debug: Posição do alvo: {tp}")
        
        if not rp or not tp:
            print(f"🔧 Debug: Posições não definidas - usar_runa cancelada")
            self.show_tooltip(f"⚠️ Posições não definidas para {self.selected_rune}")
            return
        
        try:
            # Converte posições para inteiros
            base_rx, base_ry = map(int, rp.split(','))
            base_tx, base_ty = map(int, tp.split(','))
        except ValueError:
            print(f"🔧 Debug: Formato de posição inválido - usar_runa cancelada")
            self.show_tooltip(f"⚠️ Formato de posição inválido para {self.selected_rune}")
            return
        
        # Obtém delay e randomização
        try:
            delay = int(self.delay_var.get()) if self.delay_var.get() else 100
            random_offset = int(self.random_var.get()) if self.random_var.get() else 5
            print(f"🔧 Debug: Delay: {delay}ms | Random: {random_offset}px")
        except ValueError:
            print(f"🔧 Debug: Erro nos valores de delay/random - usando padrões")
            delay = 100
            random_offset = 5
        
        # Aplica randomização
        rand_x1 = random.randint(-random_offset, random_offset)
        rand_y1 = random.randint(-random_offset, random_offset)
        rand_x2 = random.randint(-random_offset, random_offset)
        rand_y2 = random.randint(-random_offset, random_offset)
        
        rx = base_rx + rand_x1
        ry = base_ry + rand_y1
        tx = base_tx + rand_x2
        ty = base_ty + rand_y2
        
        print(f"🔧 Debug: Posições finais: Runa ({rx},{ry}) → Alvo ({tx},{ty})")
        
        # Salva posição original do mouse
        orig_x, orig_y = pyautogui.position()
        
        try:
            print(f"🔧 Debug: [{timestamp}] ⚡ EXECUTANDO COMBO DIRETO")
            
            # 1. Move para a posição da runa e clica direito
            print(f"🔧 Debug: 🖱️ Move para runa ({rx}, {ry})")
            pyautogui.moveTo(rx, ry, duration=0.1)
            time.sleep(0.05)
            
            print(f"🔧 Debug: 🖱️ Right click na runa ({rx}, {ry})")
            pyautogui.rightClick(rx, ry)
            
            # 2. Move para a posição do alvo e clica esquerdo
            print(f"🔧 Debug: 🖱️ Move para alvo ({tx}, {ty})")
            pyautogui.moveTo(tx, ty, duration=0.1)
            time.sleep(0.05)
            
            print(f"🔧 Debug: 🖱️ Left click no alvo ({tx}, {ty})")
            pyautogui.leftClick(tx, ty)
            
            # 3. Retorna mouse para posição original
            print(f"🔧 Debug: 🖱️ Retorna para posição original ({orig_x}, {orig_y})")
            pyautogui.moveTo(orig_x, orig_y, duration=0)
            
            # 4. Aplica delay
            print(f"🔧 Debug: ⏱️ Delay de {delay}ms")
            time.sleep(delay / 1000.0)
            
            timestamp_fim = time.strftime('%H:%M:%S')
            print(f"🔧 Debug: [{timestamp_fim}] ✅ COMBO EXECUTADO COM SUCESSO")
            print(f"🔧 Debug: Runa: {self.selected_rune} | Ações: Right click → Left click")
            
            self.show_tooltip(f"✅ {self.selected_rune} executada! ({rx},{ry}) → ({tx},{ty})")
            
        except Exception as e:
            timestamp_erro = time.strftime('%H:%M:%S')
            print(f"🔧 Debug: [{timestamp_erro}] ❌ ERRO AO EXECUTAR COMBO: {str(e)}")
            self.show_tooltip(f"❌ Erro ao executar combo: {str(e)}")
    
    def salvar_config(self):
        """Salva configurações globais e da runa atual"""
        try:
            # Salva configurações da runa atual
            self.salvar_configuracao_runa_atual()
            
            # Salva configurações globais (apenas para compatibilidade)
            if 'Config' not in self.config:
                self.config['Config'] = {}
            
            self.config['Config']['ScriptAtivo'] = str(self.script_ativo)
            
            self.save_config()
            self.show_tooltip("✅ Configuração salva!")
        except ValueError:
            messagebox.showerror("Erro", "Valores de delay e randomização devem ser números inteiros.")
    
    def carregar_config(self):
        """Carrega configurações globais e da runa atual"""
        self.load_config()
        
        # Carrega configuração global do script
        self.script_ativo = self.config.getboolean('Config', 'ScriptAtivo', fallback=True)
        
        # Atualiza interface do status
        if self.script_ativo:
            self.status_label.config(text="Script: ATIVO (Numpad7)", bg='lightgreen')
        else:
            self.status_label.config(text="Script: PARADO (Numpad7)", bg='lightcoral')
        
        # Carrega configurações específicas da runa atual
        self.carregar_configuracao_runa()
        self.carregar_posicoes()
        self.show_tooltip("✅ Configuração carregada!")
    
    def carregar_posicoes(self):
        """Carrega posições da runa selecionada"""
        rp = self.config.get(self.selected_rune, 'RunePos', fallback='')
        tp = self.config.get(self.selected_rune, 'TargetPos', fallback='')
        
        self.txt_rune_pos.config(text=f"Runa: {rp}" if rp else "Runa: (não marcada)")
        self.txt_alvo_pos.config(text=f"Alvo: {tp}" if tp else "Alvo: (não marcada)")
    
    def numpad8_handler(self):
        """Handler para Numpad8"""
        if not self.script_ativo:
            return
        
        if self.capture_mode == "runa":
            mx, my = pyautogui.position()
            
            if self.selected_rune not in self.config:
                self.config[self.selected_rune] = {}
            
            self.config[self.selected_rune]['RunePos'] = f"{mx},{my}"
            self.save_config()
            
            self.txt_rune_pos.config(text=f"Runa: {mx}, {my}")
            self.rune_button.config(text="🎯 Marcar Runa (8)")
            self.show_tooltip(f"✅ Runa marcada: {mx}, {my}")
            self.capture_mode = ""
            self.stop_capture_timer()
    
    def numpad9_handler(self):
        """Handler para Numpad9"""
        if not self.script_ativo:
            return
        
        if self.capture_mode == "alvo":
            mx, my = pyautogui.position()
            
            if self.selected_rune not in self.config:
                self.config[self.selected_rune] = {}
            
            self.config[self.selected_rune]['TargetPos'] = f"{mx},{my}"
            self.save_config()
            
            self.txt_alvo_pos.config(text=f"Alvo: {mx}, {my}")
            self.target_button.config(text="🎯 Marcar Alvo (9)")
            self.show_tooltip(f"✅ Alvo marcado: {mx}, {my}")
            self.capture_mode = ""
            self.stop_capture_timer()
    
    def numpad0_handler(self):
        """Handler para Numpad0 - Função removida"""
        pass
    
    
    def executar_combo_wrapper(self, runa):
        """Wrapper para executar combo"""
        self.executar_combo(runa)
    
    def executar_combo(self, runa):
        """Executa combo com verificação de auto combo"""
        if not self.script_ativo:
            return
        
        # Verifica se a runa está ativa
        if not self.rune_active.get(runa, False):
            self.show_tooltip(f"⚠️ {runa} está desativada! Use Numpad{runa[-1]} para ativar.")
            return
        
        delay = int(self.config.get(runa, 'Delay', fallback=100))
        random_offset = int(self.config.get(runa, 'RandomOffset', fallback=5))
        
        if self.auto_combo:
            if self.auto_combo_running:
                return
            else:
                self.start_auto_combo(runa, delay, random_offset)
                return
        
        self.executar_combo_uma_vez(runa, delay, random_offset)
    
    def executar_combo_uma_vez(self, runa, delay=100, random_offset=5):
        """Executa o combo uma vez com verificação de cor"""
        timestamp = time.strftime('%H:%M:%S')
        print(f"🔧 Debug: [{timestamp}] {runa} - Iniciando execução do combo")
        print(f"🔧 Debug: Delay: {delay}ms | Randomização: {random_offset}px")
        print(f"🔧 Debug: Auto combo ativo: {self.auto_combo_running}")
        
        # Executa o combo diretamente sem validação de cor
        rp = self.config.get(runa, 'RunePos', fallback='')
        tp = self.config.get(runa, 'TargetPos', fallback='')
        
        if not rp or not tp:
            self.show_tooltip(f"⚠ Posições não definidas para {runa}")
            return False
        
        try:
            base_rx, base_ry = map(int, rp.split(','))
            base_tx, base_ty = map(int, tp.split(','))
        except ValueError:
            self.show_tooltip(f"⚠ Formato de posição inválido para {runa}")
            return False
        
        # Aplica randomização
        rand_x1 = random.randint(-random_offset, random_offset)
        rand_y1 = random.randint(-random_offset, random_offset)
        rand_x2 = random.randint(-random_offset, random_offset)
        rand_y2 = random.randint(-random_offset, random_offset)
        
        rx = base_rx + rand_x1
        ry = base_ry + rand_y1
        tx = base_tx + rand_x2
        ty = base_ty + rand_y2
        
        # Salva posição original do mouse
        orig_x, orig_y = pyautogui.position()
        
        try:
            # Executa as ações SEM delay entre elas
            pyautogui.moveTo(rx, ry, duration=0.1)
            time.sleep(0.05)
            pyautogui.rightClick(rx, ry)
            pyautogui.moveTo(tx, ty, duration=0.1)
            time.sleep(0.05)
            pyautogui.leftClick(tx, ty)
            pyautogui.moveTo(orig_x, orig_y, duration=0)
            
            # Aplica o delay APÓS retornar à posição original
            time.sleep(delay / 1000.0)
            
            timestamp_fim = time.strftime('%H:%M:%S')
            print(f"🔧 Debug: [{timestamp_fim}] ✅ COMBO EXECUTADO COM SUCESSO!")
            print(f"🔧 Debug: Runa: {runa} | Delay: {delay}ms | Random: {random_offset}px")
            print(f"🔧 Debug: Posições - Runa: ({rx}, {ry}) | Alvo: ({tx}, {ty})")
            
            self.show_tooltip(f"✅ {runa} executada! (Random: {random_offset})")
            return True
            
        except Exception as e:
            timestamp_erro = time.strftime('%H:%M:%S')
            print(f"🔧 Debug: [{timestamp_erro}] ❌ ERRO AO EXECUTAR COMBO: {str(e)}")
            self.show_tooltip(f"❌ Erro ao executar combo: {str(e)}")
            return False
    
    
    
    def start_capture_timer(self, mode):
        """Inicia timer de 3 segundos para captura"""
        self.capture_countdown = 3
        self.update_capture_timer(mode)
    
    def update_capture_timer(self, mode):
        """Atualiza o timer de captura"""
        if self.capture_countdown > 0 and self.capture_mode == mode:
            self.show_tooltip(f"⏰ Capturando em {self.capture_countdown}... Posicione o mouse!")
            self.capture_countdown -= 1
            self.capture_timer = self.root.after(1000, lambda: self.update_capture_timer(mode))
        elif self.capture_mode == mode:
            # Timer terminou - captura automaticamente
            self.capture_position_automatically(mode)
    
    def capture_position_automatically(self, mode):
        """Captura a posição automaticamente quando o timer termina"""
        try:
            mx, my = pyautogui.position()
            
            if mode == "runa":
                if self.selected_rune not in self.config:
                    self.config[self.selected_rune] = {}
                
                self.config[self.selected_rune]['RunePos'] = f"{mx},{my}"
                self.save_config()
                
                self.txt_rune_pos.config(text=f"Runa: {mx}, {my}")
                self.rune_button.config(text="🎯 Marcar Runa (8)")
                self.show_tooltip(f"✅ Runa marcada automaticamente: {mx}, {my}")
                
            elif mode == "alvo":
                if self.selected_rune not in self.config:
                    self.config[self.selected_rune] = {}
                
                self.config[self.selected_rune]['TargetPos'] = f"{mx},{my}"
                self.save_config()
                
                self.txt_alvo_pos.config(text=f"Alvo: {mx}, {my}")
                self.target_button.config(text="🎯 Marcar Alvo (9)")
                self.show_tooltip(f"✅ Alvo marcado automaticamente: {mx}, {my}")
                
            elif mode == "cor":
                # Captura a cor do pixel
                screenshot = ImageGrab.grab(bbox=(mx, my, mx+1, my+1))
                pixel_color = screenshot.getpixel((0, 0))
                color_hex = f"#{pixel_color[0]:02x}{pixel_color[1]:02x}{pixel_color[2]:02x}"
                
                if self.selected_rune not in self.config:
                    self.config[self.selected_rune] = {}
                
                self.config[self.selected_rune]['VerifyColor'] = color_hex
                self.save_config()
                
                self.txt_cor_verif.config(text=f"Cor Verif: {color_hex}")
                self.show_tooltip(f"✅ Cor marcada automaticamente: {color_hex}")
            
            # Limpa o modo de captura
            self.capture_mode = ""
            self.stop_capture_timer()
            
        except Exception as e:
            self.show_tooltip(f"❌ Erro na captura automática: {str(e)}")
            self.capture_mode = ""
            self.stop_capture_timer()
    
    def stop_capture_timer(self):
        """Para o timer de captura"""
        if self.capture_timer:
            self.root.after_cancel(self.capture_timer)
            self.capture_timer = None
        self.capture_countdown = 0
    
    def show_tooltip(self, message):
        """Mostra tooltip temporário"""
        if message:
            # Cria uma janela temporária para mostrar a mensagem
            tooltip = tk.Toplevel(self.root)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
            
            label = tk.Label(tooltip, text=message, bg='yellow', font=('Arial', 9))
            label.pack()
            
            # Remove após 1.5 segundos
            tooltip.after(1500, tooltip.destroy)
    
    def run(self):
        """Executa a aplicação"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()
    
    def on_closing(self):
        """Evento de fechamento da aplicação"""
        self.stop_capture_timer()
        try:
            keyboard.unhook_all()
        except:
            pass
        self.root.destroy()
        sys.exit(0)

def main():
    """Função principal"""
    try:
        app = ComboRunaApp()
        app.run()
    except Exception as e:
        print(f"Erro ao iniciar aplicação: {e}")
        messagebox.showerror("Erro", f"Erro ao iniciar aplicação: {e}")

if __name__ == "__main__":
    main()
