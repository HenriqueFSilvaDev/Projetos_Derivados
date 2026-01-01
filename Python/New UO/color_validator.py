#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Color Validator - Validador de Cor de Baixo Nível
Aplicação simples para validar cor específica na tela com detecção não detectável
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import json
import os
import ctypes
from ctypes import wintypes
import win32gui
import win32ui
import win32con
import win32api
import win32process
import psutil
import numpy as np
from PIL import Image, ImageTk
import keyboard
import winsound

# Configurações de baixo nível para evitar detecção
class ProcessManager:
    """Gerenciador de processos para captura focada"""
    
    def __init__(self):
        self.target_process = None
        self.target_hwnd = None
        self.process_name = ""
        
    def get_running_processes(self):
        """Obtém lista de processos com janelas abertas"""
        processes = []
        try:
            # Obter todos os processos
            all_processes = {}
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_info = proc.info
                    if proc_info['name'] and proc_info['pid']:
                        all_processes[proc_info['pid']] = {
                            'pid': proc_info['pid'],
                            'name': proc_info['name'],
                            'exe': proc_info['exe'] or 'N/A'
                        }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Filtrar apenas processos com janelas visíveis
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    if pid in all_processes:
                        windows.append((pid, win32gui.GetWindowText(hwnd)))
                return True
            
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            # Adicionar apenas processos com janelas visíveis
            added_pids = set()
            for pid, window_title in windows:
                if pid not in added_pids and pid in all_processes:
                    processes.append({
                        'pid': pid,
                        'name': all_processes[pid]['name'],
                        'exe': all_processes[pid]['exe'],
                        'window_title': window_title
                    })
                    added_pids.add(pid)
                    
        except Exception as e:
            print(f"Erro ao obter processos: {e}")
        
        return sorted(processes, key=lambda x: x['name'].lower())
    
    def set_target_process(self, pid):
        """Define o processo alvo"""
        try:
            self.target_process = psutil.Process(pid)
            self.process_name = self.target_process.name()
            
            # Encontrar janela principal do processo
            self.target_hwnd = self._find_main_window(pid)
            
            return True
        except Exception as e:
            print(f"Erro ao definir processo: {e}")
            return False
    
    def _find_main_window(self, pid):
        """Encontra a janela principal do processo"""
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                if found_pid == pid:
                    windows.append(hwnd)
            return True
        
        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)
        
        # Retornar a maior janela (provavelmente a principal)
        if windows:
            return max(windows, key=lambda hwnd: win32gui.GetWindowRect(hwnd)[2] * win32gui.GetWindowRect(hwnd)[3])
        
        return None
    
    def get_window_rect(self):
        """Obtém o retângulo da janela do processo"""
        if self.target_hwnd:
            try:
                return win32gui.GetWindowRect(self.target_hwnd)
            except:
                return None
        return None
    
    def is_process_running(self):
        """Verifica se o processo ainda está rodando"""
        try:
            return self.target_process.is_running()
        except:
            return False
    
    def get_process_info(self):
        """Obtém informações do processo"""
        if self.target_process:
            try:
                return {
                    'name': self.target_process.name(),
                    'pid': self.target_process.pid,
                    'exe': self.target_process.exe(),
                    'status': 'running' if self.is_process_running() else 'stopped'
                }
            except:
                return None
        return None

class LowLevelCapture:
    """Captura de tela de baixo nível usando Windows API"""
    
    def __init__(self, process_manager=None):
        self.process_manager = process_manager
        
    def capture_region(self, x, y, width, height):
        """Captura uma região específica da tela usando Windows API"""
        try:
            # Obter handle da tela
            hwnd = win32gui.GetDesktopWindow()
            hdc = win32gui.GetWindowDC(hwnd)
            
            # Criar device context compatível
            hdc_mem = win32ui.CreateDCFromHandle(hdc)
            hbitmap = win32ui.CreateBitmap()
            
            # Criar bitmap
            hbitmap.CreateCompatibleBitmap(hdc_mem, width, height)
            hdc_mem.SelectObject(hbitmap)
            
            # Copiar região da tela
            hdc_mem.BitBlt((0, 0), (width, height), hdc, (x, y), win32con.SRCCOPY)
            
            # Converter para array numpy
            bmpinfo = hbitmap.GetInfo()
            bmpstr = hbitmap.GetBitmapBits(True)
            
            # Converter para imagem PIL
            img = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1
            )
            
            # Limpar recursos
            win32gui.DeleteObject(hbitmap.GetHandle())
            win32gui.DeleteDC(hdc_mem.GetHandle())
            win32gui.ReleaseDC(hwnd, hdc)
            
            return img
            
        except Exception as e:
            print(f"Erro na captura: {e}")
            return None
    
    def get_pixel_color(self, x, y):
        """Obtém a cor de um pixel específico usando Windows API"""
        try:
            # Se temos um processo específico, converter coordenadas
            if self.process_manager and self.process_manager.target_hwnd:
                window_rect = self.process_manager.get_window_rect()
                if window_rect:
                    # Converter coordenadas relativas para absolutas
                    abs_x = window_rect[0] + x
                    abs_y = window_rect[1] + y
                else:
                    abs_x, abs_y = x, y
            else:
                abs_x, abs_y = x, y
            
            # Usar GetPixel para máxima eficiência
            hdc = win32gui.GetDC(0)
            color = win32gui.GetPixel(hdc, abs_x, abs_y)
            win32gui.ReleaseDC(0, hdc)
            
            if color != 0xFFFFFFFF:  # Se não for erro
                # Converter de BGR para RGB
                r = color & 0xFF
                g = (color >> 8) & 0xFF
                b = (color >> 16) & 0xFF
                return (r, g, b)
            
            return None
            
        except Exception as e:
            print(f"Erro ao obter pixel: {e}")
            return None

class ColorValidator:
    """Validador de cor principal"""
    
    def __init__(self):
        self.running = False
        self.process_manager = ProcessManager()
        self.capture = LowLevelCapture(self.process_manager)
        self.monitor_thread = None
        
        # Configurações
        self.monitor_x = 0
        self.monitor_y = 0
        self.target_color = (0, 0, 0)
        self.tolerance = 10
        self.check_interval = 100  # ms
        
        # Ações
        self.hotkey_enabled = False
        self.hotkey = "F1"
        self.click_enabled = False
        self.click_x = 0
        self.click_y = 0
        
        # Posições salvas
        self.saved_positions = {}
        
    def start_monitoring(self):
        """Inicia o monitoramento"""
        if self.running:
            return
            
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Para o monitoramento"""
        self.running = False
        
    def _monitor_loop(self):
        """Loop principal de monitoramento"""
        while self.running:
            try:
                # Obter cor atual
                current_color = self.capture.get_pixel_color(self.monitor_x, self.monitor_y)
                
                if current_color:
                    # Verificar se a cor mudou
                    if not self._colors_match(current_color, self.target_color, self.tolerance):
                        # Cor mudou - executar ações
                        self._execute_actions()
                
                # Aguardar próximo check
                time.sleep(self.check_interval / 1000.0)
                
            except Exception as e:
                print(f"Erro no monitoramento: {e}")
                time.sleep(1)
    
    def _colors_match(self, color1, color2, tolerance):
        """Verifica se duas cores são similares"""
        diff = sum(abs(a - b) for a, b in zip(color1, color2))
        return diff <= tolerance
    
    def _execute_actions(self):
        """Executa as ações configuradas"""
        try:
            # Executar hotkey se habilitada
            if self.hotkey_enabled:
                keyboard.press_and_release(self.hotkey)
                
            # Executar click se habilitado
            if self.click_enabled:
                # Converter coordenadas para absolutas se necessário
                if self.process_manager.target_hwnd:
                    window_rect = self.process_manager.get_window_rect()
                    if window_rect:
                        abs_x = window_rect[0] + self.click_x
                        abs_y = window_rect[1] + self.click_y
                    else:
                        abs_x, abs_y = self.click_x, self.click_y
                else:
                    abs_x, abs_y = self.click_x, self.click_y
                
                # Usar Windows API para click de baixo nível
                win32api.SetCursorPos((abs_x, abs_y))
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, abs_x, abs_y, 0, 0)
                time.sleep(0.01)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, abs_x, abs_y, 0, 0)
                
        except Exception as e:
            print(f"Erro ao executar ações: {e}")
    
    def save_position(self, name, x, y):
        """Salva uma posição"""
        self.saved_positions[name] = (x, y)
        
    def load_position(self, name):
        """Carrega uma posição"""
        return self.saved_positions.get(name, (0, 0))

class ScreenSelector:
    """Seletor de área da tela"""
    
    def __init__(self, callback, process_manager=None):
        self.callback = callback
        self.process_manager = process_manager
        self.selection_window = None
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0
        
    def start_selection(self):
        """Inicia a seleção de área"""
        # Se temos um processo específico, focar na sua janela
        if self.process_manager and self.process_manager.target_hwnd:
            window_rect = self.process_manager.get_window_rect()
            if window_rect:
                # Criar janela transparente apenas sobre a janela do processo
                self.selection_window = tk.Toplevel()
                self.selection_window.geometry(f"{window_rect[2]-window_rect[0]}x{window_rect[3]-window_rect[1]}+{window_rect[0]}+{window_rect[1]}")
                self.selection_window.attributes('-alpha', 0.3)
                self.selection_window.configure(bg='black')
                self.selection_window.attributes('-topmost', True)
            else:
                # Fallback para tela cheia
                self.selection_window = tk.Toplevel()
                self.selection_window.attributes('-fullscreen', True)
                self.selection_window.attributes('-alpha', 0.3)
                self.selection_window.configure(bg='black')
                self.selection_window.attributes('-topmost', True)
        else:
            # Criar janela transparente para seleção em tela cheia
            self.selection_window = tk.Toplevel()
            self.selection_window.attributes('-fullscreen', True)
            self.selection_window.attributes('-alpha', 0.3)
            self.selection_window.configure(bg='black')
            self.selection_window.attributes('-topmost', True)
        
        # Canvas para desenhar a seleção
        self.canvas = tk.Canvas(
            self.selection_window,
            highlightthickness=0,
            bg='black'
        )
        self.canvas.pack(fill='both', expand=True)
        
        # Bind eventos
        self.canvas.bind('<Button-1>', self._on_click)
        self.canvas.bind('<B1-Motion>', self._on_drag)
        self.canvas.bind('<ButtonRelease-1>', self._on_release)
        self.canvas.bind('<Escape>', self._cancel_selection)
        
        # Instruções
        self.canvas.create_text(
            self.selection_window.winfo_screenwidth() // 2,
            50,
            text="Clique e arraste para selecionar a área. ESC para cancelar.",
            fill='white',
            font=('Arial', 14)
        )
        
        # Focar na janela
        self.selection_window.focus_set()
        
    def _on_click(self, event):
        """Início da seleção"""
        self.start_x = event.x
        self.start_y = event.y
        
    def _on_drag(self, event):
        """Durante o arraste"""
        self.end_x = event.x
        self.end_y = event.y
        
        # Limpar canvas
        self.canvas.delete('selection')
        
        # Desenhar retângulo de seleção
        self.canvas.create_rectangle(
            self.start_x, self.start_y,
            self.end_x, self.end_y,
            outline='red',
            width=2,
            tags='selection'
        )
        
    def _on_release(self, event):
        """Fim da seleção"""
        self.end_x = event.x
        self.end_y = event.y
        
        # Calcular área selecionada
        x1, y1 = min(self.start_x, self.end_x), min(self.start_y, self.end_y)
        x2, y2 = max(self.start_x, self.end_x), max(self.start_y, self.end_y)
        
        # Se temos um processo específico, as coordenadas já são relativas
        # Se não, precisamos converter para coordenadas da tela
        if not (self.process_manager and self.process_manager.target_hwnd):
            # Para seleção em tela cheia, usar coordenadas absolutas
            pass
        
        # Chamar callback com a área selecionada
        self.callback(x1, y1, x2 - x1, y2 - y1)
        
        # Fechar janela
        self.selection_window.destroy()
        
    def _cancel_selection(self, event):
        """Cancelar seleção"""
        self.selection_window.destroy()

class ColorValidatorApp:
    """Aplicação principal"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Color Validator - Validador de Cor")
        self.root.geometry("500x600")
        self.root.configure(bg='#2b2b2b')
        
        # Validador
        self.validator = ColorValidator()
        self.countdown_active = False
        
        # Interface
        self.create_widgets()
        
        # Carregar configurações
        self.load_settings()
        
    def create_widgets(self):
        """Cria a interface"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Título
        title_label = ttk.Label(main_frame, text="Color Validator", font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Seção de Processo
        process_frame = ttk.LabelFrame(main_frame, text="Seleção de Processo")
        process_frame.pack(fill='x', pady=10)
        
        # Botão de seleção de processo
        ttk.Button(process_frame, text="Selecionar Processo", command=self.select_process).pack(pady=5)
        
        # Informações do processo
        self.process_label = ttk.Label(process_frame, text="Nenhum processo selecionado")
        self.process_label.pack(pady=5)
        
        # Seção de Monitoramento
        monitor_frame = ttk.LabelFrame(main_frame, text="Monitoramento de Cor")
        monitor_frame.pack(fill='x', pady=10)
        
        # Linha compacta com todas as informações
        info_frame = ttk.Frame(monitor_frame)
        info_frame.pack(fill='x', pady=5)
        
        # Botão de seleção
        ttk.Button(info_frame, text="Selecionar Área", command=self.select_area).pack(side='left', padx=(0, 10))
        
        # Informações em linha
        self.monitor_info_label = ttk.Label(info_frame, text="Área: N/A | Cor: N/A")
        self.monitor_info_label.pack(side='left')
        
        # Validação de cor atual
        validation_frame = ttk.Frame(monitor_frame)
        validation_frame.pack(fill='x', pady=5)
        
        ttk.Button(validation_frame, text="Validar Cor Atual", command=self.validate_current_color).pack(side='left', padx=(0, 10))
        
        self.validation_label = ttk.Label(validation_frame, text="Status: Aguardando validação")
        self.validation_label.pack(side='left')
        
        # Seção de Configuração
        config_frame = ttk.LabelFrame(main_frame, text="Configurações")
        config_frame.pack(fill='x', pady=10)
        
        # Tolerância
        ttk.Label(config_frame, text="Tolerância:").pack(anchor='w')
        self.tolerance_var = tk.IntVar(value=10)
        tolerance_scale = ttk.Scale(config_frame, from_=0, to=50, variable=self.tolerance_var, orient='horizontal')
        tolerance_scale.pack(fill='x', pady=5)
        
        # Intervalo de verificação
        ttk.Label(config_frame, text="Intervalo (ms):").pack(anchor='w')
        self.interval_var = tk.IntVar(value=100)
        interval_scale = ttk.Scale(config_frame, from_=50, to=1000, variable=self.interval_var, orient='horizontal')
        interval_scale.pack(fill='x', pady=5)
        
        # Seção de Ações
        actions_frame = ttk.LabelFrame(main_frame, text="Ações")
        actions_frame.pack(fill='x', pady=10)
        
        # Hotkey
        hotkey_frame = ttk.Frame(actions_frame)
        hotkey_frame.pack(fill='x', pady=5)
        
        self.hotkey_enabled_var = tk.BooleanVar()
        ttk.Checkbutton(hotkey_frame, text="Habilitar Hotkey", variable=self.hotkey_enabled_var).pack(side='left')
        
        ttk.Label(hotkey_frame, text="Tecla:").pack(side='left', padx=(20, 5))
        self.hotkey_var = tk.StringVar(value="F1")
        hotkey_entry = ttk.Entry(hotkey_frame, textvariable=self.hotkey_var, width=10)
        hotkey_entry.pack(side='left')
        
        # Click
        click_frame = ttk.Frame(actions_frame)
        click_frame.pack(fill='x', pady=5)
        
        self.click_enabled_var = tk.BooleanVar()
        ttk.Checkbutton(click_frame, text="Habilitar Click", variable=self.click_enabled_var).pack(side='left')
        
        # Delay configurável
        ttk.Label(click_frame, text="Delay:").pack(side='left', padx=(20, 5))
        self.delay_var = tk.StringVar(value="3")
        delay_entry = ttk.Entry(click_frame, textvariable=self.delay_var, width=5)
        delay_entry.pack(side='left')
        ttk.Label(click_frame, text="seg").pack(side='left', padx=(2, 5))
        
        ttk.Button(click_frame, text="Gravar Posição", command=self.record_click_position_with_delay).pack(side='left', padx=(10, 5))
        
        self.stop_countdown_button = ttk.Button(click_frame, text="Parar Countdown", command=self.stop_countdown, state='disabled')
        self.stop_countdown_button.pack(side='left', padx=(5, 0))
        
        self.click_pos_label = ttk.Label(click_frame, text="Posição: (0, 0)")
        self.click_pos_label.pack(side='left', padx=(10, 0))
        
        # Controles
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill='x', pady=20)
        
        self.start_button = ttk.Button(controls_frame, text="▶ Iniciar Monitoramento", command=self.start_monitoring)
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = ttk.Button(controls_frame, text="⏹ Parar", command=self.stop_monitoring, state='disabled')
        self.stop_button.pack(side='left', padx=5)
        
        ttk.Button(controls_frame, text="Salvar Config", command=self.save_settings).pack(side='right', padx=5)
        ttk.Button(controls_frame, text="Carregar Config", command=self.load_settings).pack(side='right', padx=5)
        
        # Status
        self.status_label = ttk.Label(main_frame, text="Pronto", relief='sunken')
        self.status_label.pack(fill='x', pady=10)
        
    def select_area(self):
        """Seleciona área da tela"""
        if not self.validator.process_manager.target_process:
            messagebox.showwarning("Aviso", "Selecione um processo primeiro!")
            return
            
        def on_area_selected(x, y, width, height):
            self.validator.monitor_x = x + width // 2
            self.validator.monitor_y = y + height // 2
            
            # Obter cor atual da área selecionada
            current_color = self.validator.capture.get_pixel_color(self.validator.monitor_x, self.validator.monitor_y)
            if current_color:
                self.validator.target_color = current_color
                self.update_display()
                
        selector = ScreenSelector(on_area_selected, self.validator.process_manager)
        selector.start_selection()
        
    def select_process(self):
        """Seleciona um processo"""
        # Criar janela de seleção de processo
        process_window = tk.Toplevel(self.root)
        process_window.title("Selecionar Processo")
        process_window.geometry("600x400")
        process_window.transient(self.root)
        process_window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(process_window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Título
        ttk.Label(main_frame, text="Selecionar Processo", font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Lista de processos
        process_frame = ttk.Frame(main_frame)
        process_frame.pack(fill='both', expand=True)
        
        # Treeview para processos
        columns = ('PID', 'Nome', 'Janela')
        process_tree = ttk.Treeview(process_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            process_tree.heading(col, text=col)
            process_tree.column(col, width=150)
        
        process_tree.pack(fill='both', expand=True, pady=10)
        
        # Carregar processos
        processes = self.validator.process_manager.get_running_processes()
        for proc in processes:
            process_tree.insert('', 'end', values=(proc['pid'], proc['name'], proc['window_title']))
        
        # Botões
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=10)
        
        def on_select():
            selection = process_tree.selection()
            if selection:
                item = process_tree.item(selection[0])
                pid = int(item['values'][0])
                name = item['values'][1]
                
                if self.validator.process_manager.set_target_process(pid):
                    self.process_label.config(text=f"Processo: {name} (PID: {pid})")
                    self.update_status(f"Processo {name} selecionado!")
                    process_window.destroy()
                else:
                    messagebox.showerror("Erro", "Erro ao selecionar processo!")
        
        ttk.Button(button_frame, text="Selecionar", command=on_select).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancelar", command=process_window.destroy).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Atualizar Lista", command=lambda: self.refresh_process_list(process_tree)).pack(side='right', padx=5)
        
    def refresh_process_list(self, process_tree):
        """Atualiza a lista de processos"""
        # Limpar lista atual
        for item in process_tree.get_children():
            process_tree.delete(item)
        
        # Carregar processos atualizados
        processes = self.validator.process_manager.get_running_processes()
        for proc in processes:
            process_tree.insert('', 'end', values=(proc['pid'], proc['name'], proc['window_title']))
    
    def record_click_position_with_delay(self):
        """Grava posição do mouse com delay configurável"""
        if self.countdown_active:
            messagebox.showwarning("Aviso", "Countdown já está em andamento!")
            return
            
        try:
            delay = int(self.delay_var.get())
            if delay < 1 or delay > 30:
                messagebox.showerror("Erro", "Delay deve estar entre 1 e 30 segundos!")
                return
        except ValueError:
            messagebox.showerror("Erro", "Delay deve ser um número válido!")
            return
        
        self.countdown_active = True
        self.stop_countdown_button.config(state='normal')
        
        def countdown_and_capture():
            try:
                for i in range(delay, 0, -1):
                    if not self.countdown_active:
                        self.update_status("Countdown cancelado!")
                        return
                    self.update_status(f"Clique em qualquer lugar... {i}")
                    time.sleep(1)
                
                if not self.countdown_active:
                    self.update_status("Countdown cancelado!")
                    return
                
                self.update_status("Capturando posição...")
                time.sleep(0.1)  # Pequeno delay para garantir que o click foi registrado
                
                cursor_pos = win32gui.GetCursorPos()
                
                # Se temos um processo específico, converter para coordenadas relativas
                if self.validator.process_manager.target_hwnd:
                    window_rect = self.validator.process_manager.get_window_rect()
                    if window_rect:
                        self.validator.click_x = cursor_pos[0] - window_rect[0]
                        self.validator.click_y = cursor_pos[1] - window_rect[1]
                        self.click_pos_label.config(text=f"Posição Relativa: ({self.validator.click_x}, {self.validator.click_y})")
                    else:
                        self.validator.click_x = cursor_pos[0]
                        self.validator.click_y = cursor_pos[1]
                        self.click_pos_label.config(text=f"Posição: ({cursor_pos[0]}, {cursor_pos[1]})")
                else:
                    self.validator.click_x = cursor_pos[0]
                    self.validator.click_y = cursor_pos[1]
                    self.click_pos_label.config(text=f"Posição: ({cursor_pos[0]}, {cursor_pos[1]})")
                    
                self.update_status("Posição gravada!")
            except Exception as e:
                self.update_status(f"Erro ao gravar posição: {e}")
            finally:
                self.countdown_active = False
                self.stop_countdown_button.config(state='disabled')
        
        # Executar em thread separada para não travar a interface
        threading.Thread(target=countdown_and_capture, daemon=True).start()
    
    def stop_countdown(self):
        """Para o countdown ativo"""
        if self.countdown_active:
            self.countdown_active = False
            self.stop_countdown_button.config(state='disabled')
            self.update_status("Countdown cancelado!")
    
    def validate_current_color(self):
        """Valida a cor atual na área selecionada"""
        if not hasattr(self.validator, 'monitor_x') or self.validator.monitor_x == 0:
            messagebox.showwarning("Aviso", "Selecione uma área primeiro!")
            return
        
        try:
            # Obter cor atual
            current_color = self.validator.capture.get_pixel_color(self.validator.monitor_x, self.validator.monitor_y)
            
            if current_color:
                # Comparar com cor alvo
                tolerance = int(self.tolerance_var.get())
                if self.validator._colors_match(current_color, self.validator.target_color, tolerance):
                    self.validation_label.config(text=f"✅ CORES IGUAIS - Atual: RGB{current_color}")
                    self.validation_label.configure(foreground='green')
                else:
                    self.validation_label.config(text=f"❌ CORES DIFERENTES - Atual: RGB{current_color} | Alvo: RGB{self.validator.target_color}")
                    self.validation_label.configure(foreground='red')
            else:
                self.validation_label.config(text="❌ Erro ao obter cor atual")
                self.validation_label.configure(foreground='red')
                
        except Exception as e:
            self.validation_label.config(text=f"❌ Erro: {e}")
            self.validation_label.configure(foreground='red')
        
    def record_click_position(self):
        """Grava posição atual do mouse"""
        try:
            cursor_pos = win32gui.GetCursorPos()
            
            # Se temos um processo específico, converter para coordenadas relativas
            if self.validator.process_manager.target_hwnd:
                window_rect = self.validator.process_manager.get_window_rect()
                if window_rect:
                    self.validator.click_x = cursor_pos[0] - window_rect[0]
                    self.validator.click_y = cursor_pos[1] - window_rect[1]
                    self.click_pos_label.config(text=f"Posição Relativa: ({self.validator.click_x}, {self.validator.click_y})")
                else:
                    self.validator.click_x = cursor_pos[0]
                    self.validator.click_y = cursor_pos[1]
                    self.click_pos_label.config(text=f"Posição: ({cursor_pos[0]}, {cursor_pos[1]})")
            else:
                self.validator.click_x = cursor_pos[0]
                self.validator.click_y = cursor_pos[1]
                self.click_pos_label.config(text=f"Posição: ({cursor_pos[0]}, {cursor_pos[1]})")
                
            self.update_status("Posição gravada!")
        except Exception as e:
            self.update_status(f"Erro ao gravar posição: {e}")
            
    def start_monitoring(self):
        """Inicia o monitoramento"""
        if not hasattr(self.validator, 'monitor_x') or self.validator.monitor_x == 0:
            messagebox.showwarning("Aviso", "Selecione uma área primeiro!")
            return
            
        # Atualizar configurações
        self.validator.tolerance = self.tolerance_var.get()
        self.validator.check_interval = self.interval_var.get()
        self.validator.hotkey_enabled = self.hotkey_enabled_var.get()
        self.validator.hotkey = self.hotkey_var.get()
        self.validator.click_enabled = self.click_enabled_var.get()
        
        # Iniciar monitoramento
        self.validator.start_monitoring()
        
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.update_status("Monitoramento iniciado!")
        
    def stop_monitoring(self):
        """Para o monitoramento"""
        self.validator.stop_monitoring()
        
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.update_status("Monitoramento parado!")
        
    def update_display(self):
        """Atualiza a exibição"""
        area_text = f"Área: ({self.validator.monitor_x}, {self.validator.monitor_y})"
        color_text = f"Cor: RGB{self.validator.target_color}"
        self.monitor_info_label.config(text=f"{area_text} | {color_text}")
        
    def update_status(self, message):
        """Atualiza o status"""
        self.status_label.config(text=message)
        
    def save_settings(self):
        """Salva as configurações"""
        settings = {
            'monitor_x': self.validator.monitor_x,
            'monitor_y': self.validator.monitor_y,
            'target_color': self.validator.target_color,
            'tolerance': self.tolerance_var.get(),
            'interval': self.interval_var.get(),
            'hotkey_enabled': self.hotkey_enabled_var.get(),
            'hotkey': self.hotkey_var.get(),
            'click_enabled': self.click_enabled_var.get(),
            'click_x': self.validator.click_x,
            'click_y': self.validator.click_y,
            'saved_positions': self.validator.saved_positions
        }
        
        try:
            with open('color_validator_settings.json', 'w') as f:
                json.dump(settings, f, indent=2)
            self.update_status("Configurações salvas!")
        except Exception as e:
            self.update_status(f"Erro ao salvar: {e}")
            
    def load_settings(self):
        """Carrega as configurações"""
        try:
            if os.path.exists('color_validator_settings.json'):
                with open('color_validator_settings.json', 'r') as f:
                    settings = json.load(f)
                    
                self.validator.monitor_x = settings.get('monitor_x', 0)
                self.validator.monitor_y = settings.get('monitor_y', 0)
                self.validator.target_color = tuple(settings.get('target_color', (0, 0, 0)))
                self.tolerance_var.set(settings.get('tolerance', 10))
                self.interval_var.set(settings.get('interval', 100))
                self.hotkey_enabled_var.set(settings.get('hotkey_enabled', False))
                self.hotkey_var.set(settings.get('hotkey', 'F1'))
                self.click_enabled_var.set(settings.get('click_enabled', False))
                self.validator.click_x = settings.get('click_x', 0)
                self.validator.click_y = settings.get('click_y', 0)
                self.validator.saved_positions = settings.get('saved_positions', {})
                
                self.update_display()
                self.click_pos_label.config(text=f"Posição: ({self.validator.click_x}, {self.validator.click_y})")
                
                self.update_status("Configurações carregadas!")
        except Exception as e:
            self.update_status(f"Erro ao carregar: {e}")

def main():
    root = tk.Tk()
    app = ColorValidatorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
