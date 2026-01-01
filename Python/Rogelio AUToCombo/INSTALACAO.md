# Combo Runa - Instruções de Instalação e Execução

## 📋 Pré-requisitos

- Python 3.7 ou superior
- Windows (para funcionalidades específicas do Windows)

## 🔧 Instalação das Bibliotecas

### Opção 1: Instalação Simplificada (Recomendada)
```bash
pip install -r requirements_simple.txt
```

### Opção 2: Instalação Automática com Versões Flexíveis
```bash
pip install -r requirements.txt
```

### Opção 3: Instalação Manual (Se houver problemas)
```bash
pip install pyautogui
pip install keyboard
pip install Pillow
pip install pywin32
```

### Opção 4: Instalação Individual (Para resolver conflitos)
```bash
pip install --upgrade pip
pip install pyautogui --no-cache-dir
pip install keyboard --no-cache-dir
pip install Pillow --no-cache-dir
pip install pywin32 --no-cache-dir
```

## 🚀 Execução do Programa

### Comando Principal
```bash
python combo_runa.py
```

### Execução em Background (Opcional)
```bash
pythonw combo_runa.py
```

## 📚 Bibliotecas Utilizadas

### Bibliotecas Externas (Precisam ser instaladas):
- **pyautogui**: Automação de mouse e teclado
- **keyboard**: Captura de teclas e hotkeys
- **Pillow**: Manipulação de imagens e captura de pixels
- **pywin32**: Funcionalidades específicas do Windows

### Bibliotecas Padrão do Python (Não precisam instalar):
- **tkinter**: Interface gráfica
- **configparser**: Manipulação de arquivos INI
- **threading**: Execução em threads
- **os, sys, time, random**: Operações básicas do sistema

## ⚠️ Observações Importantes

1. **Execução como Administrador**: Para algumas funcionalidades de hotkey, pode ser necessário executar como administrador
2. **Antivírus**: Alguns antivírus podem bloquear a execução automática de mouse/teclado
3. **Failsafe**: O pyautogui tem um failsafe - mova o mouse para o canto superior esquerdo para parar emergencialmente

## 🎮 Hotkeys Disponíveis

- **Numpad 1-5**: Executar combo das runas 1-5
- **Numpad 7**: Ativar/Desativar script
- **Numpad 8**: Marcar posição da runa
- **Numpad 9**: Marcar posição do alvo
- **Numpad 0**: Marcar cor de verificação

## 📁 Arquivos Gerados

- `config.ini`: Arquivo de configuração com posições e configurações
- `combo_runa.py`: Script principal em Python
- `requirements.txt`: Lista de dependências

## 🔧 Solução de Problemas

### Erro de Instalação do Pillow
```bash
# Solução 1: Atualizar pip primeiro
python -m pip install --upgrade pip

# Solução 2: Instalar versão específica do Pillow
pip install Pillow==9.5.0

# Solução 3: Instalar sem cache
pip install Pillow --no-cache-dir

# Solução 4: Usar versão pré-compilada
pip install Pillow --only-binary=all
```

### Erro de Permissão
```bash
# Execute como administrador no PowerShell
Start-Process powershell -Verb runAs
```

### Erro de Módulo Não Encontrado
```bash
# Reinstale as dependências
pip uninstall pyautogui keyboard Pillow pywin32
pip install -r requirements_simple.txt
```

### Hotkeys Não Funcionam
- Execute como administrador
- Verifique se não há outros programas usando as mesmas teclas
- Teste com `keyboard` isoladamente

### Problemas com pywin32
```bash
# Se pywin32 der erro, tente:
pip install pywin32
python Scripts/pywin32_postinstall.py -install
```

## 📞 Suporte

Em caso de problemas:
1. Verifique se todas as dependências estão instaladas
2. Execute como administrador
3. Verifique se o Python está na versão 3.7+
4. Teste as bibliotecas individualmente
