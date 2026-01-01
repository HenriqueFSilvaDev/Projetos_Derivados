# Color Validator - Validador de Cor Focado em Processo

Uma aplicação simples e eficiente para validar cores específicas na tela com detecção de baixo nível, focada em um processo específico para não interferir com outros programas.

## 🎯 Características

- **Seleção de Processo**: Foque apenas em aplicações com janelas abertas
- **Seleção de Área**: Selecione exatamente onde quer monitorar dentro do processo
- **Validação de Baixo Nível**: Usa Windows API para captura não detectável
- **Hotkeys Configuráveis**: Execute teclas quando a cor mudar
- **Clicks Automáticos**: Clique em posições específicas quando detectar mudança
- **Gravação com Delay**: Capture posição com delay configurável (1-30 segundos)
- **Validação de Cor**: Compare cor atual com cor selecionada em tempo real
- **Interface Compacta**: Informações de área e cor em uma linha
- **Interface Simples**: Foco apenas no essencial

## 🚀 Instalação

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Execute a aplicação:
```bash
python color_validator.py
```
ou
```bash
start.bat
```

## 📖 Como Usar

### 1. Selecionar Processo
- Clique em "Selecionar Processo"
- Escolha apenas entre aplicações com janelas abertas (não todos os processos do sistema)
- A aplicação focará apenas nesse processo

### 2. Selecionar Área
- Clique em "Selecionar Área"
- A seleção será limitada à janela do processo selecionado
- A cor atual será capturada automaticamente
- Informações aparecem em linha compacta: "Área: (x, y) | Cor: RGB(r, g, b)"

### 3. Configurar Ações
- **Hotkey**: Habilite e configure a tecla a ser pressionada
- **Click**: Habilite e configure o delay (1-30 segundos) para capturar posição
- **Validação**: Use "Validar Cor Atual" para comparar com a cor selecionada
- Ajuste a tolerância e intervalo de verificação

### 4. Iniciar Monitoramento
- Clique em "Iniciar Monitoramento"
- A aplicação verificará constantemente se a cor mudou
- Quando detectar mudança, executará as ações configuradas

## ⚙️ Configurações

- **Tolerância**: Sensibilidade da detecção de cor (0-50)
- **Intervalo**: Frequência de verificação em milissegundos (50-1000ms)
- **Hotkey**: Tecla a ser pressionada (ex: F1, F2, etc.)
- **Click**: Posição onde clicar quando detectar mudança (relativa ao processo)

## 🔧 Tecnologias

- **Windows API**: `GetPixel`, `SetCursorPos`, `mouse_event`
- **PyWin32**: Interface com Windows API
- **PSUtil**: Gerenciamento de processos
- **Tkinter**: Interface gráfica simples
- **NumPy**: Processamento eficiente de dados
- **PIL**: Processamento de imagem

## 🛡️ Anti-Detecção

- Usa Windows API diretamente (não bibliotecas de captura)
- Captura apenas 1x1 pixel para máxima eficiência
- Sem hooks de sistema ou DLLs externas
- Operações de baixo nível para evitar detecção
- Foco em processo específico reduz interferência

## 📁 Arquivos

- `color_validator.py` - Aplicação principal
- `requirements.txt` - Dependências
- `start.bat` - Script de inicialização
- `README.md` - Este arquivo

## 🎮 Casos de Uso

### Jogos
- Monitorar vida/mana em MMORPGs
- Detectar mudanças de status
- Automação baseada em cores da interface
- Não interfere com outros jogos ou aplicações

### Produtividade
- Monitorar notificações específicas
- Detectar mudanças em aplicações específicas
- Automação baseada em estado visual
- Foco apenas na aplicação desejada

## ⚠️ Importante

- Use com responsabilidade
- Respeite os termos de serviço dos jogos
- Teste em ambiente seguro primeiro
- A aplicação é para fins educacionais
- Foque apenas no processo necessário

---

**Desenvolvido para validação de cor eficiente e focada em processo**
