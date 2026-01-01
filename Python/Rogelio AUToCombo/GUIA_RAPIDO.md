# 🚀 Guia Rápido - Combo Runa Python

## ⚡ Início Rápido

### 1. Instalar Dependências
```bash
pip install -r requirements_simple.txt
```

### 2. Executar Programa
```bash
python combo_runa.py
```

### 3. Testar Funcionalidades (Opcional)
```bash
python teste_funcionalidades.py
```

### 4. Testar Layout da Interface (Opcional)
```bash
python teste_layout.py
```

## 🎮 Como Usar

### Primeira Configuração
1. **Abrir o programa** - Execute `python combo_runa.py`
2. **Ativar script** - Pressione **Numpad7** (deve ficar verde)
3. **Selecionar runa** - Clique na aba numerada (1-5) - todas começam vermelhas
4. **Ativar runa** - Pressione **Numpad1-5** correspondente (aba fica verde)
5. **Marcar posições**:
   - Clique em "Marcar Runa (8)"
   - Posicione o mouse sobre a runa no jogo
   - **Aguarde 3 segundos** - captura automática!
   - Clique em "Marcar Alvo (9)"
   - Posicione o mouse sobre o alvo no jogo
   - **Aguarde 3 segundos** - captura automática!
   - Clique em "Marcar Cor (0)"
   - Posicione o mouse sobre o fundo (sem alvo)
   - **Aguarde 3 segundos** - captura automática!

### Configurações
- **Delay**: Tempo entre execuções (ms)
- **Randomização**: Variação de posição (pixels)
- **Auto Combo**: Execução automática contínua

### Hotkeys Disponíveis
- **Numpad 1-5**: Ativar/Desativar runas individuais
- **Numpad 7**: Ativar/Desativar script (CONTROLE PRINCIPAL)
- **Numpad 8**: Marcar posição da runa (captura automática)
- **Numpad 9**: Marcar posição do alvo (captura automática)
- **Numpad 0**: Marcar cor de verificação (captura automática)

### ⚠️ IMPORTANTE - Controles
- **Numpad7**: Ativar/Desativar script global (verde/vermelho)
- **Numpad1-5**: Ativar/Desativar runas individuais (abas verde/vermelho)
- **Estado inicial**: Todas as runas começam DESATIVADAS (vermelhas)
- **Primeiro passo**: Sempre ativar script com Numpad7 antes de usar
- **Segundo passo**: Ativar runas individuais com Numpad1-5

## 🔧 Funcionalidades

### Combo Manual
- Clique no botão "🚀 USAR RUNA"
- Executa uma vez o combo da runa selecionada

### Combo Automático
- Marque a opção "Auto Combo"
- Use Numpad 1-5 para iniciar
- Para automaticamente quando não há alvo

### Verificação de Cor
- Detecta automaticamente se há alvo presente
- Para execução quando não há alvo
- Evita spam desnecessário

## 📁 Arquivos

- `combo_runa.py` - Programa principal
- `config.ini` - Configurações salvas automaticamente
- `requirements_simple.txt` - Dependências
- `teste_funcionalidades.py` - Teste das bibliotecas

## ⚠️ Importante

1. **Execute como administrador** para hotkeys funcionarem
2. **Configure as posições** antes de usar
3. **Teste primeiro** com delay alto (500ms+)
4. **Use o failsafe** - mova mouse para canto superior esquerdo para parar

## 🆘 Solução de Problemas

### Hotkeys não funcionam
- Execute como administrador
- Verifique se não há outros programas usando as teclas

### Erro de instalação
```bash
pip install --upgrade pip
pip install -r requirements_simple.txt
```

### Programa não abre
```bash
python teste_funcionalidades.py
```

## 🎯 Dicas de Uso

1. **Configure todas as runas** antes de usar
2. **Teste com delay alto** primeiro
3. **Use randomização baixa** (1-3 pixels)
4. **Marque a cor do fundo** para melhor detecção
5. **Salve as configurações** regularmente
