namespace BotSpriteValidator
{
    partial class MainForm
    {
        private System.ComponentModel.IContainer components = null;

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        private void InitializeComponent()
        {
            this.txtPID = new System.Windows.Forms.TextBox();
            this.btnSelectProcess = new System.Windows.Forms.Button();
            this.txtX = new System.Windows.Forms.TextBox();
            this.txtY = new System.Windows.Forms.TextBox();
            this.txtW = new System.Windows.Forms.TextBox();
            this.txtH = new System.Windows.Forms.TextBox();
            this.cmbClickType = new System.Windows.Forms.ComboBox();
            this.btnStart = new System.Windows.Forms.Button();
            this.btnStop = new System.Windows.Forms.Button();
            this.btnPickPosition = new System.Windows.Forms.Button();
            this.btnCaptureSprite = new System.Windows.Forms.Button();
            this.btnClearSprite = new System.Windows.Forms.Button();
            this.btnClearAll = new System.Windows.Forms.Button();
            this.listBoxSprites = new System.Windows.Forms.ListBox();
            this.lblBotStatus = new System.Windows.Forms.Label();
            this.lblProcess = new System.Windows.Forms.Label();
            this.lblCoordinates = new System.Windows.Forms.Label();
            this.lblDimensions = new System.Windows.Forms.Label();
            this.lblSprites = new System.Windows.Forms.Label();
            this.btnSelectMonitorArea = new System.Windows.Forms.Button();
            this.lblMonitorArea = new System.Windows.Forms.Label();
            this.lblSimilarity = new System.Windows.Forms.Label();
            this.trackBarSimilarity = new System.Windows.Forms.TrackBar();
            this.lblSimilarityValue = new System.Windows.Forms.Label();
            this.lblBlockSize = new System.Windows.Forms.Label();
            this.numericBlockSize = new System.Windows.Forms.NumericUpDown();
            this.SuspendLayout();

            // lblProcess
            this.lblProcess.AutoSize = true;
            this.lblProcess.Location = new System.Drawing.Point(12, 15);
            this.lblProcess.Name = "lblProcess";
            this.lblProcess.Size = new System.Drawing.Size(50, 13);
            this.lblProcess.Text = "Processo:";

            // txtPID
            this.txtPID.Location = new System.Drawing.Point(70, 12);
            this.txtPID.Name = "txtPID";
            this.txtPID.Size = new System.Drawing.Size(100, 20);
            this.txtPID.PlaceholderText = "PID";

            // btnSelectProcess
            this.btnSelectProcess.Location = new System.Drawing.Point(176, 10);
            this.btnSelectProcess.Name = "btnSelectProcess";
            this.btnSelectProcess.Size = new System.Drawing.Size(75, 23);
            this.btnSelectProcess.Text = "Selecionar";
            this.btnSelectProcess.UseVisualStyleBackColor = true;
            this.btnSelectProcess.Click += new System.EventHandler(this.btnSelectProcess_Click);

            // lblCoordinates
            this.lblCoordinates.AutoSize = true;
            this.lblCoordinates.Location = new System.Drawing.Point(12, 45);
            this.lblCoordinates.Name = "lblCoordinates";
            this.lblCoordinates.Size = new System.Drawing.Size(70, 13);
            this.lblCoordinates.Text = "Coordenadas:";

            // txtX
            this.txtX.Location = new System.Drawing.Point(12, 60);
            this.txtX.Name = "txtX";
            this.txtX.Size = new System.Drawing.Size(50, 20);
            this.txtX.PlaceholderText = "X";

            // txtY
            this.txtY.Location = new System.Drawing.Point(68, 60);
            this.txtY.Name = "txtY";
            this.txtY.Size = new System.Drawing.Size(50, 20);
            this.txtY.PlaceholderText = "Y";

            // btnPickPosition
            this.btnPickPosition.Location = new System.Drawing.Point(130, 58);
            this.btnPickPosition.Name = "btnPickPosition";
            this.btnPickPosition.Size = new System.Drawing.Size(120, 23);
            this.btnPickPosition.Text = "Selecionar Área";
            this.btnPickPosition.UseVisualStyleBackColor = true;
            this.btnPickPosition.Click += new System.EventHandler(this.btnPickPosition_Click);

            // lblDimensions
            this.lblDimensions.AutoSize = true;
            this.lblDimensions.Location = new System.Drawing.Point(12, 90);
            this.lblDimensions.Name = "lblDimensions";
            this.lblDimensions.Size = new System.Drawing.Size(70, 13);
            this.lblDimensions.Text = "Dimensões:";

            // txtW
            this.txtW.Location = new System.Drawing.Point(12, 105);
            this.txtW.Name = "txtW";
            this.txtW.Size = new System.Drawing.Size(50, 20);
            this.txtW.PlaceholderText = "Largura";

            // txtH
            this.txtH.Location = new System.Drawing.Point(68, 105);
            this.txtH.Name = "txtH";
            this.txtH.Size = new System.Drawing.Size(50, 20);
            this.txtH.PlaceholderText = "Altura";

            // btnCaptureSprite
            this.btnCaptureSprite.Location = new System.Drawing.Point(130, 103);
            this.btnCaptureSprite.Name = "btnCaptureSprite";
            this.btnCaptureSprite.Size = new System.Drawing.Size(100, 23);
            this.btnCaptureSprite.Text = "Capturar Sprite";
            this.btnCaptureSprite.UseVisualStyleBackColor = true;
            this.btnCaptureSprite.Click += new System.EventHandler(this.btnCaptureSprite_Click);

            // btnClearSprite
            this.btnClearSprite.Location = new System.Drawing.Point(240, 103);
            this.btnClearSprite.Name = "btnClearSprite";
            this.btnClearSprite.Size = new System.Drawing.Size(80, 23);
            this.btnClearSprite.Text = "Limpar";
            this.btnClearSprite.UseVisualStyleBackColor = true;
            this.btnClearSprite.Click += new System.EventHandler(this.btnClearSprite_Click);

            // cmbClickType
            this.cmbClickType.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.cmbClickType.Items.AddRange(new object[] { "Clique Esquerdo", "Clique Direito" });
            this.cmbClickType.Location = new System.Drawing.Point(12, 140);
            this.cmbClickType.Name = "cmbClickType";
            this.cmbClickType.Size = new System.Drawing.Size(121, 21);

            // btnStart
            this.btnStart.Location = new System.Drawing.Point(12, 170);
            this.btnStart.Name = "btnStart";
            this.btnStart.Size = new System.Drawing.Size(100, 30);
            this.btnStart.Text = "Iniciar Bot";
            this.btnStart.UseVisualStyleBackColor = true;
            this.btnStart.Click += new System.EventHandler(this.btnStart_Click);

            // btnStop
            this.btnStop.Location = new System.Drawing.Point(118, 170);
            this.btnStop.Name = "btnStop";
            this.btnStop.Size = new System.Drawing.Size(100, 30);
            this.btnStop.Text = "Parar Bot";
            this.btnStop.UseVisualStyleBackColor = true;
            this.btnStop.Enabled = false;
            this.btnStop.Click += new System.EventHandler(this.btnStop_Click);

            // btnClearAll
            this.btnClearAll.Location = new System.Drawing.Point(240, 170);
            this.btnClearAll.Name = "btnClearAll";
            this.btnClearAll.Size = new System.Drawing.Size(80, 30);
            this.btnClearAll.Text = "Limpar Tudo";
            this.btnClearAll.UseVisualStyleBackColor = true;
            this.btnClearAll.Click += new System.EventHandler(this.btnClearAll_Click);

            // lblBotStatus
            this.lblBotStatus.AutoSize = true;
            this.lblBotStatus.Font = new System.Drawing.Font("Microsoft Sans Serif", 9F, System.Drawing.FontStyle.Bold);
            this.lblBotStatus.Location = new System.Drawing.Point(12, 210);
            this.lblBotStatus.Name = "lblBotStatus";
            this.lblBotStatus.Size = new System.Drawing.Size(100, 15);
            this.lblBotStatus.Text = "🔴 BOT PARADO";
            this.lblBotStatus.ForeColor = System.Drawing.Color.Red;

            // lblSprites
            this.lblSprites.AutoSize = true;
            this.lblSprites.Location = new System.Drawing.Point(330, 15);
            this.lblSprites.Name = "lblSprites";
            this.lblSprites.Size = new System.Drawing.Size(50, 13);
            this.lblSprites.Text = "Sprites:";

            // listBoxSprites
            this.listBoxSprites.FormattingEnabled = true;
            this.listBoxSprites.Location = new System.Drawing.Point(330, 30);
            this.listBoxSprites.Name = "listBoxSprites";
            this.listBoxSprites.Size = new System.Drawing.Size(150, 150);

            // btnSelectMonitorArea
            this.btnSelectMonitorArea.Location = new System.Drawing.Point(12, 200);
            this.btnSelectMonitorArea.Name = "btnSelectMonitorArea";
            this.btnSelectMonitorArea.Size = new System.Drawing.Size(150, 30);
            this.btnSelectMonitorArea.Text = "Selecionar Área de Monitoramento";
            this.btnSelectMonitorArea.UseVisualStyleBackColor = true;
            this.btnSelectMonitorArea.Click += new System.EventHandler(this.btnSelectMonitorArea_Click);

            // lblMonitorArea
            this.lblMonitorArea.AutoSize = true;
            this.lblMonitorArea.Location = new System.Drawing.Point(12, 235);
            this.lblMonitorArea.Name = "lblMonitorArea";
            this.lblMonitorArea.Size = new System.Drawing.Size(200, 13);
            this.lblMonitorArea.Text = "📍 Área de Monitoramento: Não definida";
            this.lblMonitorArea.ForeColor = System.Drawing.Color.Red;

            // lblSimilarity
            this.lblSimilarity.AutoSize = true;
            this.lblSimilarity.Location = new System.Drawing.Point(12, 260);
            this.lblSimilarity.Name = "lblSimilarity";
            this.lblSimilarity.Size = new System.Drawing.Size(150, 13);
            this.lblSimilarity.Text = "🎯 Tolerância de Similaridade:";

            // trackBarSimilarity
            this.trackBarSimilarity.Location = new System.Drawing.Point(12, 275);
            this.trackBarSimilarity.Name = "trackBarSimilarity";
            this.trackBarSimilarity.Size = new System.Drawing.Size(200, 45);
            this.trackBarSimilarity.Minimum = 50;
            this.trackBarSimilarity.Maximum = 100;
            this.trackBarSimilarity.Value = 80;
            this.trackBarSimilarity.TickFrequency = 10;
            this.trackBarSimilarity.Scroll += new System.EventHandler(this.trackBarSimilarity_Scroll);

            // lblSimilarityValue
            this.lblSimilarityValue.AutoSize = true;
            this.lblSimilarityValue.Location = new System.Drawing.Point(220, 275);
            this.lblSimilarityValue.Name = "lblSimilarityValue";
            this.lblSimilarityValue.Size = new System.Drawing.Size(50, 13);
            this.lblSimilarityValue.Text = "80%";
            this.lblSimilarityValue.Font = new System.Drawing.Font("Arial", 10, System.Drawing.FontStyle.Bold);

            // lblBlockSize
            this.lblBlockSize.AutoSize = true;
            this.lblBlockSize.Location = new System.Drawing.Point(280, 260);
            this.lblBlockSize.Name = "lblBlockSize";
            this.lblBlockSize.Size = new System.Drawing.Size(120, 13);
            this.lblBlockSize.Text = "🔲 Tamanho do Bloco:";

            // numericBlockSize
            this.numericBlockSize.Location = new System.Drawing.Point(280, 275);
            this.numericBlockSize.Name = "numericBlockSize";
            this.numericBlockSize.Size = new System.Drawing.Size(80, 20);
            this.numericBlockSize.Minimum = 2;
            this.numericBlockSize.Maximum = 20;
            this.numericBlockSize.Value = 3;
            this.numericBlockSize.Increment = 1;
            this.numericBlockSize.TextAlign = System.Windows.Forms.HorizontalAlignment.Center;
            this.numericBlockSize.ValueChanged += new System.EventHandler(this.numericBlockSize_ValueChanged);

            // MainForm
            this.ClientSize = new System.Drawing.Size(500, 320);
            this.Controls.Add(this.numericBlockSize);
            this.Controls.Add(this.lblBlockSize);
            this.Controls.Add(this.lblSimilarityValue);
            this.Controls.Add(this.trackBarSimilarity);
            this.Controls.Add(this.lblSimilarity);
            this.Controls.Add(this.lblMonitorArea);
            this.Controls.Add(this.btnSelectMonitorArea);
            this.Controls.Add(this.lblProcess);
            this.Controls.Add(this.txtPID);
            this.Controls.Add(this.btnSelectProcess);
            this.Controls.Add(this.lblCoordinates);
            this.Controls.Add(this.txtX);
            this.Controls.Add(this.txtY);
            this.Controls.Add(this.lblDimensions);
            this.Controls.Add(this.txtW);
            this.Controls.Add(this.txtH);
            this.Controls.Add(this.cmbClickType);
            this.Controls.Add(this.btnPickPosition);
            this.Controls.Add(this.btnCaptureSprite);
            this.Controls.Add(this.btnClearSprite);
            this.Controls.Add(this.btnClearAll);
            this.Controls.Add(this.lblSprites);
            this.Controls.Add(this.listBoxSprites);
            this.Controls.Add(this.btnStart);
            this.Controls.Add(this.btnStop);
            this.Controls.Add(this.lblBotStatus);
            this.Name = "MainForm";
            this.Text = "Bot Sprite Validator";
            this.ResumeLayout(false);
            this.PerformLayout();
        }

        #endregion

        private System.Windows.Forms.TextBox txtPID;
        private System.Windows.Forms.Button btnSelectProcess;
        private System.Windows.Forms.TextBox txtX;
        private System.Windows.Forms.TextBox txtY;
        private System.Windows.Forms.TextBox txtW;
        private System.Windows.Forms.TextBox txtH;
        private System.Windows.Forms.ComboBox cmbClickType;
        private System.Windows.Forms.Button btnStart;
        private System.Windows.Forms.Button btnStop;
        private System.Windows.Forms.Button btnPickPosition;
        private System.Windows.Forms.Button btnCaptureSprite;
        private System.Windows.Forms.Button btnClearSprite;
        private System.Windows.Forms.Button btnClearAll;
        private System.Windows.Forms.ListBox listBoxSprites;
        private System.Windows.Forms.Label lblBotStatus;
        private System.Windows.Forms.Label lblProcess;
        private System.Windows.Forms.Label lblCoordinates;
        private System.Windows.Forms.Label lblDimensions;
        private System.Windows.Forms.Label lblSprites;
        private System.Windows.Forms.Button btnSelectMonitorArea;
        private System.Windows.Forms.Label lblMonitorArea;
        private System.Windows.Forms.Label lblSimilarity;
        private System.Windows.Forms.TrackBar trackBarSimilarity;
        private System.Windows.Forms.Label lblSimilarityValue;
        private System.Windows.Forms.Label lblBlockSize;
        private System.Windows.Forms.NumericUpDown numericBlockSize;
    }
}
