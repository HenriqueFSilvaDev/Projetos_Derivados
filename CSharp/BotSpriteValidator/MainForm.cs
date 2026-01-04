using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.Runtime.InteropServices;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace BotSpriteValidator
{
    public partial class MainForm : Form
    {
        private List<Bitmap> spriteList = new List<Bitmap>();
        private CancellationTokenSource? cancellationTokenSource = null;
        private bool isBotRunning = false;
        private Point? startPoint = null;
        private Point? endPoint = null;
        
        // Variáveis para armazenar as coordenadas da área selecionada
        private int selectedX = 0;
        private int selectedY = 0;
        private int selectedWidth = 0;
        private int selectedHeight = 0;

        public MainForm()
        {
            InitializeComponent();
            cmbClickType.SelectedIndex = 0; // Default clique esquerdo
            UpdateBotStatus();
            
            // Bot sempre no topo, mas não maximizado
            this.TopMost = true;
            
            // Inicializar label da área de monitoramento
            UpdateMonitorAreaLabels();
        }

        private void btnSelectProcess_Click(object sender, EventArgs e)
        {
            var processes = Process.GetProcesses();
            using (var dlg = new Form())
            {
                dlg.Text = "Selecione o processo";
                dlg.Size = new Size(500, 600);
                dlg.StartPosition = FormStartPosition.CenterParent;
                
                var panel = new Panel() { Dock = DockStyle.Fill };
                dlg.Controls.Add(panel);
                
                // Campo de busca
                var lblSearch = new Label() { Text = "Buscar processo:", Location = new Point(10, 10), AutoSize = true };
                var txtSearch = new TextBox() { Location = new Point(10, 30), Size = new Size(200, 20) };
                var btnRefresh = new Button() { Text = "Atualizar", Location = new Point(220, 28), Size = new Size(80, 23) };
                var btnDetectActive = new Button() { Text = "Detectar Ativo", Location = new Point(310, 28), Size = new Size(100, 23) };
                
                panel.Controls.Add(lblSearch);
                panel.Controls.Add(txtSearch);
                panel.Controls.Add(btnRefresh);
                panel.Controls.Add(btnDetectActive);
                
                // Lista de processos
                var list = new ListBox() { 
                    Location = new Point(10, 60), 
                    Size = new Size(460, 480),
                    Font = new Font("Consolas", 9)
                };
                panel.Controls.Add(list);

                void RefreshProcessList()
                {
                    list.Items.Clear();
                    var searchText = txtSearch.Text.ToLower();
                    
                    foreach (var proc in processes)
                    {
                        try 
                        { 
                            var processInfo = $"{proc.Id} - {proc.ProcessName}";
                            var isMaximized = IsProcessMaximized(proc.Id);
                            var isActive = IsProcessActive(proc.Id);
                            
                            if (string.IsNullOrEmpty(searchText) || 
                                proc.ProcessName.ToLower().Contains(searchText) ||
                                proc.Id.ToString().Contains(searchText))
                            {
                                if (isActive)
                                {
                                    processInfo += " [ATIVO]";
                                    list.Items.Add(processInfo);
                                }
                                else if (isMaximized)
                                {
                                    processInfo += " [MAXIMIZADO]";
                                    list.Items.Add(processInfo);
                                }
                                else
                                {
                                    list.Items.Add(processInfo);
                                }
                            }
                        }
                        catch { }
                    }
                    
                    if (list.Items.Count == 0)
                    {
                        list.Items.Add("Nenhum processo encontrado.");
                    }
                }

                // Eventos
                txtSearch.TextChanged += (s, ev) => RefreshProcessList();
                btnRefresh.Click += (s, ev) => RefreshProcessList();
                
                btnDetectActive.Click += (s, ev) =>
                {
                    var activeProcess = GetActiveProcess();
                    if (activeProcess != null)
                    {
                        txtPID.Text = activeProcess.Id.ToString();
                        dlg.Close();
                    }
                    else
                    {
                        MessageBox.Show("Não foi possível detectar o processo ativo.", "Aviso", 
                            MessageBoxButtons.OK, MessageBoxIcon.Information);
                    }
                };
                
                list.DoubleClick += (s, ev) =>
                {
                    if (list.SelectedItem != null)
                    {
                        var selectedText = list.SelectedItem.ToString()!;
                        if (selectedText.Contains(" - "))
                        {
                            txtPID.Text = selectedText.Split('-')[0].Trim();
                            dlg.Close();
                        }
                    }
                };

                // Carregar lista inicial
                RefreshProcessList();
                
                // Dicas de uso
                var lblTip = new Label() { 
                    Text = "💡 Dica: Use 'Detectar Ativo' para o processo em foco, ou busque por nome/ID", 
                    Location = new Point(10, 545), 
                    Size = new Size(460, 30),
                    ForeColor = Color.Blue,
                    Font = new Font("Arial", 8)
                };
                panel.Controls.Add(lblTip);
                
                dlg.ShowDialog();
            }
        }

        private bool IsProcessMaximized(int processId)
        {
            try
            {
                var windows = GetProcessWindows(processId);
                foreach (var hwnd in windows)
                {
                    if (IsWindowMaximized(hwnd))
                        return true;
                }
                return false;
            }
            catch
            {
                return false;
            }
        }

        private List<IntPtr> GetProcessWindows(int processId)
        {
            var windows = new List<IntPtr>();
            EnumWindows((hwnd, lParam) =>
            {
                GetWindowThreadProcessId(hwnd, out int pid);
                if (pid == processId && IsWindowVisible(hwnd))
                {
                    windows.Add(hwnd);
                }
                return true;
            }, IntPtr.Zero);
            return windows;
        }

        private bool IsWindowMaximized(IntPtr hwnd)
        {
            var placement = new WINDOWPLACEMENT();
            GetWindowPlacement(hwnd, ref placement);
            return placement.showCmd == SW_SHOWMAXIMIZED;
        }

        private void btnPickPosition_Click(object sender, EventArgs e)
        {
            using (Form overlay = new Form())
            {
                overlay.FormBorderStyle = FormBorderStyle.None;
                overlay.WindowState = FormWindowState.Maximized;
                overlay.Opacity = 0.3;
                overlay.BackColor = Color.Black;
                overlay.TopMost = true;
                overlay.Cursor = Cursors.Cross;

                var isSelecting = false;

                overlay.Paint += (s, ev) =>
                {
                    if (isSelecting && startPoint.HasValue && endPoint.HasValue)
                    {
                        using (var pen = new Pen(Color.Red, 2))
                        {
                            var rect = GetSelectionRectangle();
                            ev.Graphics.DrawRectangle(pen, rect);
                            
                            // Desenhar texto com as dimensões
                            using (var brush = new SolidBrush(Color.Red))
                            using (var font = new Font("Arial", 12, FontStyle.Bold))
                            {
                                var text = $"{rect.Width} x {rect.Height}";
                                var textSize = ev.Graphics.MeasureString(text, font);
                                ev.Graphics.FillRectangle(new SolidBrush(Color.Black), 
                                    rect.X, rect.Y - textSize.Height - 5, textSize.Width + 10, textSize.Height + 5);
                                ev.Graphics.DrawString(text, font, brush, rect.X + 5, rect.Y - textSize.Height);
                            }
                        }
                    }
                };

                overlay.MouseDown += (s, ev) =>
                {
                    if (ev.Button == MouseButtons.Left)
                    {
                        startPoint = ev.Location;
                        isSelecting = true;
                        overlay.Invalidate();
                    }
                };

                overlay.MouseMove += (s, ev) =>
                {
                    if (isSelecting && startPoint.HasValue)
                    {
                        endPoint = ev.Location;
                        overlay.Invalidate();
                    }
                };

                overlay.MouseUp += (s, ev) =>
                {
                    if (ev.Button == MouseButtons.Left && startPoint.HasValue && endPoint.HasValue)
                    {
                        var rect = GetSelectionRectangle();
                        txtX.Text = rect.X.ToString();
                        txtY.Text = rect.Y.ToString();
                        txtW.Text = rect.Width.ToString();
                        txtH.Text = rect.Height.ToString();
                        
                        // Limpar seleção
                        startPoint = null;
                        endPoint = null;
                        overlay.Close();
                    }
                };

                overlay.KeyDown += (s, ev) =>
                {
                    if (ev.KeyCode == Keys.Escape)
                    {
                        startPoint = null;
                        endPoint = null;
                        overlay.Close();
                    }
                };

                overlay.ShowDialog();
            }
        }

        private void btnSelectMonitorArea_Click(object sender, EventArgs e)
        {
            using (Form overlay = new Form())
            {
                overlay.FormBorderStyle = FormBorderStyle.None;
                overlay.WindowState = FormWindowState.Maximized;
                overlay.Opacity = 0.3;
                overlay.BackColor = Color.Black;
                overlay.TopMost = true;
                overlay.Cursor = Cursors.Cross;

                var isSelecting = false;

                overlay.Paint += (s, ev) =>
                {
                    if (isSelecting && startPoint.HasValue && endPoint.HasValue)
                    {
                        using (var pen = new Pen(Color.Blue, 3))
                        {
                            var rect = GetSelectionRectangle();
                            ev.Graphics.DrawRectangle(pen, rect);
                            
                            // Desenhar texto com as dimensões
                            using (var brush = new SolidBrush(Color.Blue))
                            using (var font = new Font("Arial", 14, FontStyle.Bold))
                            {
                                var text = $"ÁREA DE MONITORAMENTO: {rect.Width} x {rect.Height}";
                                var textSize = ev.Graphics.MeasureString(text, font);
                                ev.Graphics.FillRectangle(new SolidBrush(Color.Black), 
                                    rect.X, rect.Y - textSize.Height - 5, textSize.Width + 10, textSize.Height + 5);
                                ev.Graphics.DrawString(text, font, brush, rect.X + 5, rect.Y - textSize.Height);
                            }
                        }
                    }
                };

                overlay.MouseDown += (s, ev) =>
                {
                    if (ev.Button == MouseButtons.Left)
                    {
                        startPoint = ev.Location;
                        isSelecting = true;
                        overlay.Invalidate();
                    }
                };

                overlay.MouseMove += (s, ev) =>
                {
                    if (isSelecting && startPoint.HasValue)
                    {
                        endPoint = ev.Location;
                        overlay.Invalidate();
                    }
                };

                overlay.MouseUp += (s, ev) =>
                {
                    if (ev.Button == MouseButtons.Left && startPoint.HasValue && endPoint.HasValue)
                    {
                        var rect = GetSelectionRectangle();
                        
                        // Salvar as coordenadas da área de monitoramento
                        selectedX = rect.X;
                        selectedY = rect.Y;
                        selectedWidth = rect.Width;
                        selectedHeight = rect.Height;
                        
                        // Atualizar labels para mostrar a área selecionada
                        UpdateMonitorAreaLabels();
                        
                        // Limpar seleção
                        startPoint = null;
                        endPoint = null;
                        overlay.Close();
                        
                        MessageBox.Show($"Área de monitoramento definida!\nPosição: ({rect.X}, {rect.Y})\nTamanho: {rect.Width} x {rect.Height}", 
                            "Área Definida", MessageBoxButtons.OK, MessageBoxIcon.Information);
                    }
                };

                overlay.KeyDown += (s, ev) =>
                {
                    if (ev.KeyCode == Keys.Escape)
                    {
                        startPoint = null;
                        endPoint = null;
                        overlay.Close();
                    }
                };

                overlay.ShowDialog();
            }
        }

        private void UpdateMonitorAreaLabels()
        {
            if (lblMonitorArea.InvokeRequired)
            {
                lblMonitorArea.Invoke(new Action(UpdateMonitorAreaLabels));
                return;
            }

            if (selectedWidth > 0 && selectedHeight > 0)
            {
                lblMonitorArea.Text = $"📍 Área de Monitoramento: ({selectedX}, {selectedY}) - {selectedWidth} x {selectedHeight}";
                lblMonitorArea.ForeColor = Color.Green;
            }
            else
            {
                lblMonitorArea.Text = "📍 Área de Monitoramento: Não definida";
                lblMonitorArea.ForeColor = Color.Red;
            }
        }

        private void trackBarSimilarity_Scroll(object sender, EventArgs e)
        {
            if (lblSimilarityValue.InvokeRequired)
            {
                lblSimilarityValue.Invoke(new Action(() => trackBarSimilarity_Scroll(sender, e)));
                return;
            }

            int similarityThreshold = trackBarSimilarity.Value;
            lblSimilarityValue.Text = $"{similarityThreshold}%";
        }

        private void numericBlockSize_ValueChanged(object sender, EventArgs e)
        {
            // O tamanho do bloco é atualizado automaticamente quando usado
        }

        private Rectangle GetSelectionRectangle()
        {
            if (!startPoint.HasValue || !endPoint.HasValue)
                return Rectangle.Empty;

            var x = Math.Min(startPoint.Value.X, endPoint.Value.X);
            var y = Math.Min(startPoint.Value.Y, endPoint.Value.Y);
            var width = Math.Abs(endPoint.Value.X - startPoint.Value.X);
            var height = Math.Abs(endPoint.Value.Y - startPoint.Value.Y);

            return new Rectangle(x, y, width, height);
        }

        private void btnCaptureSprite_Click(object sender, EventArgs e)
        {
            if (!int.TryParse(txtX.Text, out int x) ||
                !int.TryParse(txtY.Text, out int y) ||
                !int.TryParse(txtW.Text, out int w) ||
                !int.TryParse(txtH.Text, out int h))
            {
                MessageBox.Show("Preencha X, Y, Largura e Altura corretamente.");
                return;
            }

            if (w <= 0 || h <= 0)
            {
                MessageBox.Show("Largura e Altura devem ser maiores que zero.");
                return;
            }

            try
            {
                // Capturar a sprite na posição especificada (não salvar como área de monitoramento)
                Bitmap bmp = new Bitmap(w, h);
                using (Graphics g = Graphics.FromImage(bmp))
                {
                    g.CopyFromScreen(x, y, 0, 0, bmp.Size);
                }

                spriteList.Add(bmp);
                listBoxSprites.Items.Add($"Sprite {spriteList.Count} ({w}x{h}) - Pos: ({x}, {y})");
                
                // Limpar campos após captura
                ClearSpriteFields();
                
                MessageBox.Show($"Sprite capturada com sucesso! Dimensões: {w}x{h}", "Sucesso", 
                    MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Erro ao capturar sprite: {ex.Message}", "Erro", 
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void ClearSpriteFields()
        {
            txtX.Clear();
            txtY.Clear();
            txtW.Clear();
            txtH.Clear();
            startPoint = null;
            endPoint = null;
            // Não limpar selectedX, selectedY, selectedWidth, selectedHeight (área de monitoramento)
        }

        private void btnClearSprite_Click(object sender, EventArgs e)
        {
            ClearSpriteFields();
        }

        private void btnClearAll_Click(object sender, EventArgs e)
        {
            if (MessageBox.Show("Deseja limpar todas as sprites e a área de monitoramento?", "Confirmar", 
                MessageBoxButtons.YesNo, MessageBoxIcon.Question) == DialogResult.Yes)
            {
                foreach (var sprite in spriteList)
                {
                    sprite.Dispose();
                }
                spriteList.Clear();
                listBoxSprites.Items.Clear();
                
                // Limpar coordenadas da área de monitoramento
                selectedX = 0;
                selectedY = 0;
                selectedWidth = 0;
                selectedHeight = 0;
                
                // Atualizar labels
                UpdateMonitorAreaLabels();
            }
        }

        private async void btnStart_Click(object sender, EventArgs e)
        {
            if (spriteList.Count == 0)
            {
                MessageBox.Show("Adicione pelo menos uma sprite de referência.");
                return;
            }

            if (isBotRunning)
            {
                MessageBox.Show("O bot já está rodando!");
                return;
            }

            // Verificar se a área de monitoramento foi definida
            if (selectedWidth <= 0 || selectedHeight <= 0)
            {
                MessageBox.Show("Selecione primeiro a área de monitoramento onde o bot deve procurar pelas sprites.", 
                    "Área Não Definida", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            bool clickRight = cmbClickType.SelectedIndex == 1;
            isBotRunning = true;
            UpdateBotStatus();

            // Criar novo CancellationTokenSource
            cancellationTokenSource = new CancellationTokenSource();

            await Task.Run(async () =>
            {
                try
                {
                    while (!cancellationTokenSource.Token.IsCancellationRequested)
                    {
                        foreach (var sprite in spriteList)
                        {
                            if (cancellationTokenSource.Token.IsCancellationRequested)
                                break;

                            try
                            {
                                // Procurar a sprite em toda a área de monitoramento
                                var foundPosition = FindSpriteInArea(sprite, selectedX, selectedY, selectedWidth, selectedHeight);
                                
                                if (foundPosition.HasValue)
                                {
                                    // Emular clique na posição onde a sprite foi encontrada
                                    PerformMouseClickAtPosition(foundPosition.Value.X, foundPosition.Value.Y, clickRight);
                                    
                                    // Aguardar um pouco para evitar cliques múltiplos
                                    await Task.Delay(100, cancellationTokenSource.Token);
                                }
                            }
                            catch (Exception ex)
                            {
                                // Log do erro mas continua executando
                                this.Invoke(() => Console.WriteLine($"Erro ao processar sprite: {ex.Message}"));
                            }
                        }
                        
                        if (!cancellationTokenSource.Token.IsCancellationRequested)
                        {
                            await Task.Delay(500, cancellationTokenSource.Token);
                        }
                    }
                }
                catch (OperationCanceledException)
                {
                    // Bot foi parado - isso é normal
                }
                catch (Exception ex)
                {
                    this.Invoke(() => MessageBox.Show($"Erro durante execução: {ex.Message}", "Erro", 
                        MessageBoxButtons.OK, MessageBoxIcon.Error));
                }
                finally
                {
                    // Garantir que o status seja atualizado mesmo em caso de erro
                    this.Invoke(() => 
                    {
                        isBotRunning = false;
                        UpdateBotStatus();
                    });
                }
            });
        }

        private Point? FindSpriteInArea(Bitmap targetSprite, int areaX, int areaY, int areaWidth, int areaHeight)
        {
            try
            {
                // Capturar toda a área de monitoramento
                using (Bitmap areaCapture = new Bitmap(areaWidth, areaHeight))
                {
                    using (Graphics g = Graphics.FromImage(areaCapture))
                    {
                        g.CopyFromScreen(areaX, areaY, 0, 0, areaCapture.Size);
                    }

                    // Procurar a sprite em toda a área
                    for (int x = 0; x <= areaWidth - targetSprite.Width; x++)
                    {
                        for (int y = 0; y <= areaHeight - targetSprite.Height; y++)
                        {
                            if (IsSpriteAtPosition(areaCapture, targetSprite, x, y))
                            {
                                // Retornar posição absoluta na tela
                                return new Point(areaX + x, areaY + y);
                            }
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                // Log do erro mas não mostrar MessageBox para evitar spam
                Console.WriteLine($"Erro ao procurar sprite: {ex.Message}");
            }
            
            return null;
        }

        private bool IsSpriteAtPosition(Bitmap areaCapture, Bitmap targetSprite, int offsetX, int offsetY)
        {
            try
            {
                // Validação por blocos para maior velocidade
                int blockSize = (int)numericBlockSize.Value; // Tamanho do bloco (3x3 pixels)
                int totalBlocks = 0;
                int similarBlocks = 0;
                int similarityThreshold = trackBarSimilarity.Value;

                // Calcular quantos blocos cabem na sprite
                int blocksX = (int)Math.Ceiling((double)targetSprite.Width / blockSize);
                int blocksY = (int)Math.Ceiling((double)targetSprite.Height / blockSize);
                totalBlocks = blocksX * blocksY;

                // Verificar cada bloco
                for (int blockX = 0; blockX < blocksX; blockX++)
                {
                    for (int blockY = 0; blockY < blocksY; blockY++)
                    {
                        if (IsBlockSimilar(areaCapture, targetSprite, offsetX, offsetY, blockX, blockY, blockSize))
                        {
                            similarBlocks++;
                        }
                    }
                }

                // Calcular porcentagem de similaridade baseada em blocos
                double similarityPercentage = (double)similarBlocks / totalBlocks * 100;
                return similarityPercentage >= similarityThreshold;
            }
            catch
            {
                return false;
            }
        }

        private bool IsBlockSimilar(Bitmap areaCapture, Bitmap targetSprite, int offsetX, int offsetY, int blockX, int blockY, int blockSize)
        {
            try
            {
                // Calcular posição inicial do bloco
                int startX = blockX * blockSize;
                int startY = blockY * blockSize;
                
                // Calcular posição final do bloco (considerando bordas)
                int endX = Math.Min(startX + blockSize, targetSprite.Width);
                int endY = Math.Min(startY + blockSize, targetSprite.Height);

                // Verificar se o bloco tem pelo menos 50% de pixels similares
                int totalPixelsInBlock = (endX - startX) * (endY - startY);
                int similarPixelsInBlock = 0;

                for (int x = startX; x < endX; x++)
                {
                    for (int y = startY; y < endY; y++)
                    {
                        Color targetColor = targetSprite.GetPixel(x, y);
                        Color capturedColor = areaCapture.GetPixel(offsetX + x, offsetY + y);

                        if (AreColorsSimilar(targetColor, capturedColor, 30))
                        {
                            similarPixelsInBlock++;
                        }
                    }
                }

                // Bloco é similar se pelo menos 50% dos pixels são similares
                return (double)similarPixelsInBlock / totalPixelsInBlock >= 0.5;
            }
            catch
            {
                return false;
            }
        }

        private bool AreColorsSimilar(Color color1, Color color2, int tolerance)
        {
            // Calcular diferença para cada componente de cor (R, G, B)
            int diffR = Math.Abs(color1.R - color2.R);
            int diffG = Math.Abs(color1.G - color2.G);
            int diffB = Math.Abs(color1.B - color2.B);

            // Verificar se a diferença está dentro da tolerância
            return diffR <= tolerance && diffG <= tolerance && diffB <= tolerance;
        }

        private void PerformMouseClickAtPosition(int x, int y, bool rightClick)
        {
            try
            {
                // Mover o cursor virtualmente para a posição da sprite
                SetCursorPos(x, y);
                
                // Aguardar um pouco para garantir que o cursor chegou na posição
                Thread.Sleep(10);
                
                // Emular clique na posição específica
                if (rightClick)
                {
                    // Clique direito na posição específica
                    mouse_event(0x0008, 0, 0, 0, 0); // Right Down
                    Thread.Sleep(10);
                    mouse_event(0x0010, 0, 0, 0, 0); // Right Up
                }
                else
                {
                    // Clique esquerdo na posição específica
                    mouse_event(0x0002, 0, 0, 0, 0); // Left Down
                    Thread.Sleep(10);
                    mouse_event(0x0004, 0, 0, 0, 0); // Left Up
                }
            }
            catch (Exception ex)
            {
                this.Invoke(() => MessageBox.Show($"Erro ao executar clique: {ex.Message}"));
            }
        }

        private void btnStop_Click(object sender, EventArgs e)
        {
            try
            {
                // Verificar se o bot está realmente rodando
                if (!isBotRunning)
                {
                    return; // Bot já está parado
                }

                // Cancelar a execução de forma segura
                if (cancellationTokenSource != null && !cancellationTokenSource.Token.IsCancellationRequested)
                {
                    // Cancelar a execução
                    cancellationTokenSource.Cancel();
                    
                    // Aguardar um pouco para garantir que a tarefa seja cancelada
                    Thread.Sleep(100);
                    
                    // Dispose do CancellationTokenSource de forma segura
                    try
                    {
                        cancellationTokenSource.Dispose();
                    }
                    catch { }
                    finally
                    {
                        cancellationTokenSource = null;
                    }
                }
                
                // Atualizar status de forma segura
                isBotRunning = false;
                
                // Atualizar interface de forma thread-safe
                if (this.IsHandleCreated && !this.IsDisposed)
                {
                    this.BeginInvoke(new Action(() =>
                    {
                        try
                        {
                            UpdateBotStatus();
                        }
                        catch { }
                    }));
                }
                
                // Forçar coleta de lixo de forma segura
                try
                {
                    GC.Collect();
                    GC.WaitForPendingFinalizers();
                }
                catch { }
            }
            catch (Exception ex)
            {
                // Log do erro mas não mostrar MessageBox para evitar loops
                Console.WriteLine($"Erro ao parar o bot: {ex.Message}");
                
                // Forçar parada mesmo em caso de erro
                isBotRunning = false;
                cancellationTokenSource = null;
            }
        }

        private void UpdateBotStatus()
        {
            try
            {
                // Verificar se o controle existe e está válido
                if (lblBotStatus == null || lblBotStatus.IsDisposed || !lblBotStatus.IsHandleCreated)
                {
                    return;
                }

                if (lblBotStatus.InvokeRequired)
                {
                    try
                    {
                        lblBotStatus.Invoke(new Action(UpdateBotStatus));
                    }
                    catch
                    {
                        // Se falhar o invoke, tentar BeginInvoke
                        try
                        {
                            lblBotStatus.BeginInvoke(new Action(UpdateBotStatus));
                        }
                        catch { }
                    }
                    return;
                }

                // Atualizar status de forma segura
                if (isBotRunning)
                {
                    lblBotStatus.Text = "🟢 BOT RODANDO";
                    lblBotStatus.ForeColor = Color.Green;
                    
                    // Verificar se os botões existem antes de atualizar
                    if (btnStart != null && !btnStart.IsDisposed)
                        btnStart.Enabled = false;
                    if (btnStop != null && !btnStop.IsDisposed)
                        btnStop.Enabled = true;
                }
                else
                {
                    lblBotStatus.Text = "🔴 BOT PARADO";
                    lblBotStatus.ForeColor = Color.Red;
                    
                    // Verificar se os botões existem antes de atualizar
                    if (btnStart != null && !btnStart.IsDisposed)
                        btnStart.Enabled = true;
                    if (btnStop != null && !btnStop.IsDisposed)
                        btnStop.Enabled = false;
                }
            }
            catch (Exception ex)
            {
                // Log do erro mas não falhar
                Console.WriteLine($"Erro ao atualizar status do bot: {ex.Message}");
            }
        }

        private bool CompareBitmaps(Bitmap bmp1, Bitmap bmp2)
        {
            if (bmp1.Width != bmp2.Width || bmp1.Height != bmp2.Height) return false;

            for (int x = 0; x < bmp1.Width; x++)
            {
                for (int y = 0; y < bmp1.Height; y++)
                {
                    if (bmp1.GetPixel(x, y) != bmp2.GetPixel(x, y))
                        return false;
                }
            }
            return true;
        }

        private Process? GetActiveProcess()
        {
            try
            {
                var hwnd = GetForegroundWindow();
                if (hwnd != IntPtr.Zero)
                {
                    GetWindowThreadProcessId(hwnd, out int processId);
                    return Process.GetProcessById(processId);
                }
            }
            catch { }
            return null;
        }

        private bool IsProcessActive(int processId)
        {
            try
            {
                var hwnd = GetForegroundWindow();
                if (hwnd != IntPtr.Zero)
                {
                    GetWindowThreadProcessId(hwnd, out int activeProcessId);
                    return activeProcessId == processId;
                }
            }
            catch { }
            return false;
        }

        #region Win32 API
        [DllImport("user32.dll")]
        private static extern bool EnumWindows(EnumWindowsProc enumProc, IntPtr lParam);

        [DllImport("user32.dll")]
        private static extern bool GetWindowThreadProcessId(IntPtr hWnd, out int lpdwProcessId);

        [DllImport("user32.dll")]
        private static extern bool IsWindowVisible(IntPtr hWnd);

        [DllImport("user32.dll")]
        private static extern bool GetWindowPlacement(IntPtr hWnd, ref WINDOWPLACEMENT lpwndpl);

        [DllImport("user32.dll")]
        private static extern IntPtr GetForegroundWindow();

        [DllImport("user32.dll")]
        private static extern void mouse_event(int dwFlags, int dx, int dy, int dwData, int dwExtraInfo);

        [DllImport("user32.dll")]
        private static extern bool GetCursorPos(ref POINT lpPoint);

        [DllImport("user32.dll")]
        private static extern bool SetCursorPos(int x, int y);

        private delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

        private const int SW_SHOWMAXIMIZED = 3;

        [StructLayout(LayoutKind.Sequential)]
        private struct WINDOWPLACEMENT
        {
            public int length;
            public int flags;
            public int showCmd;
            public Point ptMinPosition;
            public Point ptMaxPosition;
            public Rectangle rcNormalPosition;
        }

        [StructLayout(LayoutKind.Sequential)]
        private struct POINT
        {
            public int x;
            public int y;
        }
        #endregion

        protected override void OnFormClosing(FormClosingEventArgs e)
        {
            try
            {
                // Parar o bot se estiver rodando
                if (isBotRunning && cancellationTokenSource != null)
                {
                    try
                    {
                        cancellationTokenSource.Cancel();
                        Thread.Sleep(100);
                        cancellationTokenSource.Dispose();
                    }
                    catch { }
                    finally
                    {
                        cancellationTokenSource = null;
                        isBotRunning = false;
                    }
                }
                
                // Limpar recursos das sprites de forma segura
                if (spriteList != null)
                {
                    foreach (var sprite in spriteList)
                    {
                        try
                        {
                            if (sprite != null)
                            {
                                sprite.Dispose();
                            }
                        }
                        catch { }
                    }
                    spriteList.Clear();
                }
                
                // Forçar coleta de lixo de forma segura
                try
                {
                    GC.Collect();
                    GC.WaitForPendingFinalizers();
                }
                catch { }
            }
            catch (Exception ex)
            {
                // Log do erro mas não falhar o fechamento
                Console.WriteLine($"Erro durante fechamento: {ex.Message}");
            }
            finally
            {
                // Garantir que o formulário seja fechado
                base.OnFormClosing(e);
            }
        }
    }
}
