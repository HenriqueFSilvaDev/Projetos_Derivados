# Conexão Remota - ADDEE

## Instalação

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Execute o aplicativo:
```bash
python conexao_remota_addee.py
```

## Como usar

1. **Selecionar Processo/Aplicativo**:
   - Clique em "Atualizar" para listar todos os processos com janelas visíveis
   - Selecione o processo do seu jogo/aplicativo na lista
   - O status mostrará se o processo foi selecionado corretamente

2. **Capturar Posições**: 
   - Clique em "Capturar Posição 1" e posicione o mouse sobre a primeira runa azul
   - **Contagem regressiva de 3 segundos** para você posicionar o mouse
   - Clique em "Capturar Posição 2" e posicione o mouse sobre a segunda runa azul
   - **Contagem regressiva de 3 segundos** para você posicionar o mouse

3. **Configurar Hotkey**:
   - Por padrão é **CTRL**, mas você pode alterar no campo "Hotkey Ativação"
   - Exemplos: `ctrl`, `f1`, `ctrl+1`, `ctrl+q`, `ctrl+space`
   - Hotkey para capturar posição atual: Ctrl+Shift+C
   - **IMPORTANTE**: Clique em "Atualizar Hotkey" após alterar
   - **Fallback**: Se CTRL não funcionar, automaticamente usa F1

4. **Ativar Sistema**:
   - Clique em "Ativar" para habilitar o sistema
   - Pressione a hotkey definida para executar a ação

5. **Salvar Configurações**:
   - Clique em "Salvar Config" para salvar suas configurações

## Características Anti-Detecção

- **Seleção de Processo**: Trabalha apenas com o aplicativo selecionado
- **Validação de Processo**: Verifica se o processo ainda está ativo antes de executar
- **Movimento de mouse humano** com curvas aleatórias
- **Randomização de pixels** nas posições (±2 pixels)
- **Delays aleatórios** entre ações
- **Retorno do mouse** com pequena variação (±3 pixels)
- **Interface discreta** e pequena
- **Configurações salvas** automaticamente

## Funcionamento

Quando você pressionar a hotkey ativação:
1. **Verifica** se o processo selecionado ainda está ativo
2. **Salva** a posição atual do mouse
3. **Escolhe aleatoriamente** uma das duas posições de runa
4. **Move** o mouse de forma humana até a posição (com randomização)
5. **Executa** clique direito na runa azul
6. **Retorna** o mouse para a posição original com pequena variação

## Dependências

O aplicativo requer as seguintes dependências:
- `pyautogui`: Para automação de mouse e teclado
- `keyboard`: Para captura de hotkeys
- `Pillow`: Para processamento de imagens
- `psutil`: Para gerenciar processos

Instale com:
```bash
pip install -r requirements.txt
```
