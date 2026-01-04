# Bot Sprite Validator

Um bot automatizado em C# que valida sprites na tela e executa ações baseadas em comparações de imagem.

## Funcionalidades

### 🎯 Captura de Sprites
- **Seleção de Área Retangular**: Clique e arraste para selecionar uma área específica na tela
- **Captura de Sprites de Referência**: Capture sprites individuais para adicionar à lista de monitoramento
- **Lista de Sprites**: Todas as sprites capturadas são salvas em uma lista ao lado direito
- **Visualização em Tempo Real**: Veja as dimensões da área selecionada enquanto arrasta
- **Busca Inteligente**: O bot procura sprites em toda a área de monitoramento, não apenas na posição exata
- **Emulação de Cliques**: Cliques automáticos na posição onde a sprite é encontrada, sem mover o cursor físico
- **Validação por Similaridade**: Detecta sprites com padrões relacionados, mesmo com mudanças de intensidade de cor

### 🎮 Controle do Bot
- **Iniciar Bot**: Inicia a validação automática das sprites
- **Parar Bot**: Para a execução do bot a qualquer momento
- **Indicador de Status**: Mostra visualmente se o bot está rodando (🟢) ou parado (🔴)

### 🧹 Gerenciamento de Sprites
- **Limpar Sprite**: Limpa os campos de entrada (X, Y, Largura, Altura)
- **Limpar Tudo**: Remove todas as sprites da lista e a área de monitoramento
- **Validação Automática**: Compara sprites capturadas em tempo real

### ⚙️ Configurações
- **Tipo de Clique**: Escolha entre clique esquerdo ou direito
- **Seleção de Processo**: Selecione apenas processos maximizados pelo PID
- **Intervalo de Verificação**: O bot verifica as sprites a cada 500ms
- **Área de Monitoramento**: Defina separadamente onde o bot deve procurar pelas sprites
- **Tolerância de Similaridade**: Ajuste a sensibilidade para detectar sprites com mudanças de cor

## Validação por Similaridade

### 🎯 **Como Funciona:**
- **Detecção Inteligente**: O bot não procura por sprites idênticas, mas por padrões similares
- **Tolerância de Cores**: Considera mudanças de intensidade (dia/noite, sombras, iluminação)
- **Porcentagem Configurável**: Ajuste de 50% a 100% de similaridade necessária
- **Padrões Relacionados**: Encontra sprites com o mesmo formato mas cores diferentes
- **Validação por Blocos**: Compara blocos inteiros em vez de pixels individuais para máxima velocidade

### 🔧 **Configuração da Tolerância:**
- **🎯 Tolerância de Similaridade**: Use o slider para ajustar a sensibilidade
- **50%**: Muito tolerante - detecta sprites com grandes diferenças
- **80%**: Padrão recomendado - equilíbrio entre precisão e flexibilidade
- **100%**: Muito restritivo - apenas sprites idênticas

### 🌅 **Exemplos de Uso:**
- **Mudanças de Dia/Noite**: Sprites ficam mais escuras ou claras
- **Diferentes Iluminações**: Sombras, brilhos, contrastes
- **Variações de Cor**: Pequenas diferenças na paleta de cores
- **Compressão de Imagem**: Artefatos de compressão ou resolução

## Validação por Blocos (Alta Performance)

### ⚡ **Como Funciona:**
- **Divisão em Blocos**: A sprite é dividida em blocos configuráveis (ex: 3x3, 5x5 pixels)
- **Comparação de Blocos**: Cada bloco é comparado como uma unidade inteira
- **Validação Rápida**: Blocos são validados se 50% dos pixels são similares
- **Resultado Final**: Sprite é considerada encontrada se threshold de blocos similares for atingido

### 🔧 **Configuração do Tamanho de Bloco:**
- **🔲 Tamanho do Bloco**: Use o numericUpDown para ajustar (2 a 20 pixels)
- **3 pixels**: Padrão recomendado - equilíbrio entre velocidade e precisão
- **5-10 pixels**: Muito rápido - para sprites grandes ou prioridade de velocidade
- **2 pixels**: Muito preciso - para sprites pequenas ou máxima precisão

### 📊 **Ganho de Performance:**
- **Antes (Pixel a Pixel)**: 11x9 = 99 comparações por posição
- **Agora (Blocos 3x3)**: 4x3 = 12 comparações por posição
- **Melhoria**: **8x mais rápido** na detecção!
- **Escalabilidade**: Quanto maior o bloco, mais rápido o processamento

### 🎯 **Exemplo Prático:**
- **Sprite 11x9 pixels** com bloco 3x3:
  - **Blocos horizontais**: 4 (11 ÷ 3 = 3.67 → 4)
  - **Blocos verticais**: 3 (9 ÷ 3 = 3)
  - **Total de blocos**: 4 × 3 = 12 comparações
  - **Antes**: 99 comparações pixel a pixel
  - **Ganho**: 8.25x mais rápido!

## Como Usar

### 🔍 **Passo 1: Definir Área de Monitoramento**
1. **Selecione o Processo**: Clique em "Selecionar" para escolher o processo do jogo
2. **Defina a Área de Monitoramento**: Clique em "Selecionar Área de Monitoramento" para definir onde o bot deve procurar pelas sprites
3. **Confirme a Seleção**: A área será marcada em azul e as coordenadas serão salvas

### 🎯 **Passo 2: Capturar Sprites de Referência**
1. **Selecione a Área da Sprite**: Use "Selecionar Área" para definir X, Y, Largura e Altura da sprite
2. **Capture a Sprite**: Clique em "Capturar Sprite" para salvar na lista de monitoramento
3. **Repita para Mais Sprites**: Capture quantas sprites diferentes quiser monitorar

### 🎮 **Passo 3: Configurar e Executar**
1. **Escolha o Tipo de Clique**: Selecione esquerdo ou direito
2. **Inicie o Bot**: Clique em "Iniciar Bot" para começar a validação
3. **Monitore o Status**: Acompanhe o indicador visual do status do bot

## Seleção de Área

### 🖱️ **Como Selecionar:**
1. Clique em "Selecionar Área"
2. Uma tela escura aparecerá sobre toda a tela
3. Clique e arraste para desenhar um retângulo
4. As dimensões aparecem em tempo real
5. Solte o mouse para confirmar a seleção
6. Pressione ESC para cancelar

### 📐 **Coordenadas Capturadas:**
- **X, Y**: Posição do canto superior esquerdo
- **Largura, Altura**: Dimensões da área selecionada

## Área de Monitoramento

### 🔍 **Definição da Área de Monitoramento:**
1. **Clique em "Selecionar Área de Monitoramento"**
2. Uma tela escura aparecerá sobre toda a tela
3. **Clique e arraste para desenhar um retângulo AZUL** (diferente da seleção de sprites)
4. **Esta área define onde o bot vai procurar** pelas sprites de referência
5. **Pode ser diferente** da área onde você capturou as sprites

### 📊 **Indicador Visual:**
- **📍 Verde**: Área de monitoramento definida com coordenadas
- **📍 Vermelho**: Área de monitoramento não definida
- **Coordenadas sempre visíveis** na interface

### ⚡ **Vantagens da Separação:**
- **Flexibilidade total**: Capture sprites em qualquer lugar, monitore em outro
- **Monitoramento amplo**: Defina uma área grande para procurar sprites
- **Captura precisa**: Capture sprites em áreas específicas para melhor qualidade
- **Reutilização**: Use a mesma área de monitoramento para diferentes conjuntos de sprites

## Funcionamento do Bot

### 🔍 **Busca de Sprites em Área:**
- O bot **não procura apenas na posição exata** onde você capturou a sprite
- Ele **escaneia toda a área selecionada** procurando por sprites similares
- Quando encontra uma sprite, identifica **exatamente onde ela está** na tela

### 🖱️ **Emulação de Cliques Inteligente:**
- **Cursor virtual**: O bot move o cursor virtualmente para a posição da sprite
- **Clique na posição correta**: O bot clica exatamente onde a sprite foi encontrada
- **Suporte a clique esquerdo e direito**: Configurável via dropdown
- **Prevenção de cliques múltiplos**: Aguarda 100ms entre cliques para evitar spam
- **Movimento do cursor**: O cursor se move para a posição da sprite antes de clicar

### ⚡ **Como Funciona:**
1. **Captura da área**: O bot captura toda a área selecionada
2. **Busca sistemática**: Procura cada sprite em todas as posições possíveis
3. **Detecção precisa**: Identifica a posição exata onde a sprite está
4. **Movimento do cursor**: Move o cursor virtualmente para a posição da sprite
5. **Clique emulado**: Executa o clique na posição correta
6. **Repetição**: Continua monitorando a cada 500ms

## Comportamento da Janela

### 🪟 **Janela Sempre Visível:**
- **Sempre no topo**: Permanece visível sobre outras aplicações
- **Tamanho normal**: O bot não inicia maximizado
- **Não minimiza automaticamente**: Permanece visível mesmo ao clicar em outros aplicativos
- **Controle manual**: Você pode minimizar ou redimensionar quando quiser
- **Fácil acesso**: Sempre disponível para controle e monitoramento

## Filtro de Processos

### 🔍 **Busca Inteligente:**
- **Campo de Busca**: Digite o nome do jogo ou ID do processo
- **Detecção Automática**: Botão "Detectar Ativo" para o processo em foco
- **Processos Ativos**: Marcados com [ATIVO] para fácil identificação
- **Processos Maximizados**: Marcados com [MAXIMIZADO]
- **Atualização em Tempo Real**: Lista se atualiza conforme você digita

### 🎯 **Como Encontrar seu Jogo:**
1. **Método 1 - Detecção Automática**: 
   - Clique em "Detectar Ativo"
   - O bot detecta automaticamente o processo da janela em foco
2. **Método 2 - Busca por Nome**:
   - Digite o nome do jogo no campo de busca
   - Ex: "minecraft", "roblox", "game"
3. **Método 3 - Busca por ID**:
   - Digite o PID do processo
4. **Método 4 - Lista Completa**:
   - Navegue pela lista de todos os processos
   - Procure por processos marcados [ATIVO] ou [MAXIMIZADO]

## Melhorias Implementadas

### ✅ **Funcionalidades Adicionadas**
- Seleção de área retangular com arrastar e soltar
- Filtro de processos apenas maximizados
- Visualização em tempo real das dimensões
- Botão "Parar Bot" para controle total
- Botão "Limpar Sprite" para limpar campos individuais
- Botão "Limpar Tudo" para remover todas as sprites
- Indicador visual de status (🟢/🔴)
- Controle de execução com CancellationToken
- Tratamento de erros melhorado
- **Busca de sprites em área completa**: Procura sprites em toda a área selecionada
- **Emulação de cliques sem mover cursor**: Cliques automáticos na posição exata da sprite
- **Validação por similaridade**: Detecta sprites com padrões relacionados e mudanças de cor
- **Tolerância configurável**: Ajuste de 50% a 100% de similaridade necessária
- **Validação por blocos**: Compara blocos inteiros em vez de pixels individuais para máxima velocidade
- **Tamanho de bloco configurável**: Ajuste de 2 a 20 pixels para otimizar performance vs precisão

### 🔧 **Correções Técnicas**
- Resolvido conflito de nomes com método MouseClick
- Implementado gerenciamento adequado de recursos
- Adicionado tratamento de erros melhorado
- Melhorada a interface do usuário
- Implementadas APIs Win32 para detecção de janelas maximizadas
- **Corrigido erro de execução**: O bot agora salva as coordenadas da área selecionada para uso durante a execução
- **Corrigido conflito de recursos**: Implementado gerenciamento adequado de CancellationTokenSource e limpeza de recursos ao parar/reiniciar o bot
- **Corrigido erro de referência nula**: Implementadas verificações robustas para evitar erros ao parar o bot e durante o fechamento da aplicação

### 🎨 **Interface Atualizada**
- Layout reorganizado com labels informativos
- Placeholders nos campos de entrada
- Botões com tamanhos otimizados
- Janela redimensionada para acomodar novos controles
- Organização visual melhorada por seções

## Requisitos

- .NET 9.0 ou superior
- Windows Forms
- Sistema operacional Windows

## Compilação

```bash
dotnet build
dotnet run
```

## Estrutura do Projeto

- `Program.cs` - Ponto de entrada da aplicação
- `MainForm.cs` - Lógica principal do formulário
- `MainForm.Designer.cs` - Design da interface do usuário
- `BotSpriteValidator.csproj` - Configuração do projeto

## Segurança

⚠️ **Atenção**: Este bot utiliza funções de baixo nível do Windows (mouse_event) e captura de tela. Use com responsabilidade e apenas em aplicações autorizadas.

## Licença

Este projeto é fornecido como está, para fins educacionais e de desenvolvimento.
