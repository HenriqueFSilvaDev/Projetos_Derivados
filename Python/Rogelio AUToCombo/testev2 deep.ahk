#Requires AutoHotkey v2.0

SetWorkingDir A_ScriptDir
SendMode "Input"
CoordMode "Mouse", "Screen"
CoordMode "ToolTip", "Screen"
CoordMode "Pixel", "Screen"

; Variáveis globais
global runaX := 0
global runaY := 0
global alvoX := 0
global alvoY := 0
global delay := 100
global captureMode := ""
global selectedRune := "Runa 1"
global iniFile := A_ScriptDir "\config.ini"
global autoCombo := false
global scriptAtivo := true
global randomOffset := 5
global autoComboRunning := false
global autoComboRuna := ""
global autoComboDelay := 0
global autoComboRandomOffset := 0

runes := Map(1, "Runa 1", 2, "Runa 2", 3, "Runa 3", 4, "Runa 4", 5, "Runa 5")

; ====================
; INTERFACE GRÁFICA
; ====================

myGui := Gui()
myGui.Title := "Combo Runa"
myGui.AddText("x10 y10 w250 Center", "COMBO RUNA - Clique Direito/Esquerdo")
myGui.AddText("x10 y35 w250 h2 +0x10") ; Linha separadora
myGui.AddText("x10 y50", "Selecione a runa:")
myGui.AddDropDownList("x10 y70 w230 vSelectedRune Choose1", ["Runa 1", "Runa 2", "Runa 3", "Runa 4", "Runa 5"]).OnEvent("Change", OnRuneChange)
myGui.AddGroupBox("x10 y100 w230 h100", "Posições Marcadas")
myGui.AddText("x20 y120 w210 vTxtRunePos", "Runa: (não marcada)")
myGui.AddText("x20 y140 w210 vTxtAlvoPos", "Alvo: (não marcada)")
myGui.AddText("x20 y160 w210 vTxtCorVerif", "Cor Verif: (não marcada)")
myGui.AddButton("x10 y210 w80 h30 vRuneButton", "Marcar Runa (8)").OnEvent("Click", MarcarRuna)
myGui.AddButton("x95 y210 w80 h30 vTargetButton", "Marcar Alvo (9)").OnEvent("Click", MarcarAlvo)
myGui.AddButton("x180 y210 w80 h30 vColorButton", "Marcar Cor (0)").OnEvent("Click", MarcarCor)
myGui.AddGroupBox("x10 y250 w230 h100", "Configurações")
myGui.AddText("x20 y270", "Delay (ms):")
myGui.AddEdit("x100 y267 w60 vDelayValue", "100")
myGui.AddText("x20 y295", "Randomização:")
myGui.AddEdit("x100 y292 w60 vRandomOffsetValue", "5")
myGui.AddText("x165 y295", "pixels")
myGui.AddCheckBox("x20 y320 vAutoComboCheck", "Auto Combo").OnEvent("Click", OnAutoComboChange)
myGui.AddButton("x10 y360 w230 h35", "🚀 USAR RUNA").OnEvent("Click", UsarRuna)
myGui.AddButton("x10 y405 w110 h25", "Salvar Config").OnEvent("Click", SalvarConfig)
myGui.AddButton("x130 y405 w110 h25", "Carregar Config").OnEvent("Click", CarregarConfig)
myGui.AddText("x10 y440 w230 h20 Center vStatusScript", "Script: ATIVO (Numpad7)")
myGui.AddText("x10 y465 w230 h40 Center", "Hotkeys: Numpad 1-5 runas, 7 toggle, 8/9/0 marcar")

myGui.OnEvent("Close", GuiClose)
myGui.OnEvent("Escape", GuiClose)
myGui.Show("w270 h510")
CarregarConfig()

; ====================
; HOTKEYS
; ====================

Hotkey "Numpad8", Numpad8Handler
Hotkey "Numpad9", Numpad9Handler
Hotkey "Numpad0", Numpad0Handler
Hotkey "Numpad1", (*) => ExecutarComboWrapper("Runa 1")
Hotkey "Numpad2", (*) => ExecutarComboWrapper("Runa 2")
Hotkey "Numpad3", (*) => ExecutarComboWrapper("Runa 3")
Hotkey "Numpad4", (*) => ExecutarComboWrapper("Runa 4")
Hotkey "Numpad5", (*) => ExecutarComboWrapper("Runa 5")
Hotkey "Numpad7", Numpad7Handler

return

; ====================
; HOTKEY WRAPPER
; ====================

ExecutarComboWrapper(runa, *) {
    ExecutarCombo(runa)
}

; ====================
; EVENTOS DA GUI
; ====================

OnRuneChange(guiCtrl, *) {
    global selectedRune
    selectedRune := guiCtrl.Value
    CarregarPosicoes()
}

OnAutoComboChange(guiCtrl, *) {
    global autoCombo
    autoCombo := guiCtrl.Value
}

MarcarRuna(guiCtrl, *) {
    global captureMode
    if (captureMode = "runa") {
        captureMode := ""
        ToolTip()
        guiCtrl.Text := "Marcar Runa (8)"
    } else {
        captureMode := "runa"
        guiCtrl.Text := "CANCELAR (8)"
        ToolTip("🎯 Posicione mouse sobre RUNA e pressione Numpad8")
    }
}

MarcarAlvo(guiCtrl, *) {
    global captureMode
    if (captureMode = "alvo") {
        captureMode := ""
        ToolTip()
        guiCtrl.Text := "Marcar Alvo (9)"
    } else {
        captureMode := "alvo"
        guiCtrl.Text := "CANCELAR (9)"
        ToolTip("🎯 Posicione mouse sobre ALVO e pressione Numpad9")
    }
}

MarcarCor(guiCtrl, *) {
    global captureMode
    if (captureMode = "cor") {
        captureMode := ""
        ToolTip()
        guiCtrl.Text := "Marcar Cor (0)"
    } else {
        captureMode := "cor"
        guiCtrl.Text := "CANCELAR (0)"
        ToolTip("🎯 Posicione mouse sobre a COR DO FUNDO (sem alvo) e pressione Numpad0")
    }
}

UsarRuna(guiCtrl, *) {
    global selectedRune, iniFile, myGui, delay, randomOffset
    rp := IniRead(iniFile, selectedRune, "RunePos", "")
    tp := IniRead(iniFile, selectedRune, "TargetPos", "")
    if (rp = "" || rp = "ERROR") {
        MsgBox("⚠ Erro: Posição da runa não definida para '" selectedRune "'.", 48)
        return
    }
    if (tp = "" || tp = "ERROR") {
        MsgBox("⚠ Erro: Posição do alvo não definida para '" selectedRune "'.", 48)
        return
    }
    delay := myGui["DelayValue"].Value ? myGui["DelayValue"].Value : 100
    randomOffset := myGui["RandomOffsetValue"].Value ? myGui["RandomOffsetValue"].Value : 5
    ExecutarComboUmaVez(selectedRune, delay, randomOffset)
    ToolTip("✅ Combo executado!")
    SetTimer(LimparTooltip, -1500)
}

LimparTooltip(*) {
    ToolTip()
}

LimparTrayTip(*) {
    TrayTip ; Clears the tray tip
}

SalvarConfig(guiCtrl, *) {
    global iniFile, myGui, autoCombo
    delay := myGui["DelayValue"].Value ? myGui["DelayValue"].Value : 100
    randomOffset := myGui["RandomOffsetValue"].Value ? myGui["RandomOffsetValue"].Value : 5
    IniWrite(delay, iniFile, "Config", "Delay")
    IniWrite(randomOffset, iniFile, "Config", "RandomOffset")
    IniWrite(autoCombo, iniFile, "Config", "AutoCombo")
    TrayTip "✅ Configuração salva!", ""
    SetTimer(LimparTrayTip, -1000)
}

CarregarConfig(*) {
    global iniFile, myGui, delay, randomOffset, autoCombo
    delay := IniRead(iniFile, "Config", "Delay", 100)
    randomOffset := IniRead(iniFile, "Config", "RandomOffset", 5)
    autoCombo := IniRead(iniFile, "Config", "AutoCombo", 0)
    myGui["DelayValue"].Value := delay
    myGui["RandomOffsetValue"].Value := randomOffset
    myGui["AutoComboCheck"].Value := autoCombo
    CarregarPosicoes()
    TrayTip "✅ Configuração carregada!", ""
    SetTimer(LimparTrayTip, -1000)
}

CarregarPosicoes(*) {
    global selectedRune, iniFile, myGui
    rp := IniRead(iniFile, selectedRune, "RunePos", "")
    tp := IniRead(iniFile, selectedRune, "TargetPos", "")
    cp := IniRead(iniFile, selectedRune, "VerifyColor", "")
    myGui["TxtRunePos"].Value := (rp != "" && rp != "ERROR") ? "Runa: " rp : "Runa: (não marcada)"
    myGui["TxtAlvoPos"].Value := (tp != "" && tp != "ERROR") ? "Alvo: " tp : "Alvo: (não marcada)"
    myGui["TxtCorVerif"].Value := (cp != "" && cp != "ERROR") ? "Cor Verif: " cp : "Cor Verif: (não marcada)"
}

; ====================
; HOTKEY HANDLERS
; ====================

Numpad8Handler(*) {
    global captureMode, selectedRune, iniFile, myGui, scriptAtivo
    if (!scriptAtivo)
        return
    if (captureMode = "runa") {
        mx := 0, my := 0
        MouseGetPos(&mx, &my)
        IniWrite(mx "," my, iniFile, selectedRune, "RunePos")
        myGui["TxtRunePos"].Value := "Runa: " mx ", " my
        myGui["RuneButton"].Text := "Marcar Runa (8)"
        ToolTip("✅ Runa marcada: " mx ", " my)
        SetTimer(LimparTooltip, -1500)
        captureMode := ""
    }
}

Numpad9Handler(*) {
    global captureMode, selectedRune, iniFile, myGui, scriptAtivo
    if (!scriptAtivo)
        return
    if (captureMode = "alvo") {
        mx := 0, my := 0
        MouseGetPos(&mx, &my)
        IniWrite(mx "," my, iniFile, selectedRune, "TargetPos")
        myGui["TxtAlvoPos"].Value := "Alvo: " mx ", " my
        myGui["TargetButton"].Text := "Marcar Alvo (9)"
        ToolTip("✅ Alvo marcado: " mx ", " my)
        SetTimer(LimparTooltip, -1500)
        captureMode := ""
    }
}

Numpad0Handler(*) {
    global captureMode, selectedRune, iniFile, myGui, scriptAtivo
    if (!scriptAtivo)
        return
    if (captureMode = "cor") {
        mx := 0, my := 0
        MouseGetPos(&mx, &my)
        col := PixelGetColor(mx, my, "RGB")
        IniWrite(col, iniFile, selectedRune, "VerifyColor")
        myGui["TxtCorVerif"].Value := "Cor Verif: " col
        myGui["ColorButton"].Text := "Marcar Cor (0)"
        ToolTip("✅ Cor do FUNDO (sem alvo) marcada: " col)
        SetTimer(LimparTooltip, -1500)
        captureMode := ""
    }
}

Numpad7Handler(*) {
    global scriptAtivo, myGui
    scriptAtivo := !scriptAtivo
    if (scriptAtivo) {
        myGui["StatusScript"].Value := "Script: ATIVO (Numpad7)"
        TrayTip "✅ Script ativado", ""
        SetTimer(LimparTrayTip, -1000)
    } else {
        myGui["StatusScript"].Value := "Script: PARADO (Numpad7)"
        TrayTip "⏸️ Script pausado", ""
        SetTimer(LimparTrayTip, -1000)
        StopAutoCombo()
    }
}

; ====================
; FUNÇÕES
; ====================

ExecutarCombo(runa) {
    global iniFile, autoCombo, scriptAtivo, autoComboRunning
    if (!scriptAtivo)
        return
    delay := IniRead(iniFile, "Config", "Delay", 100)
    randomOffset := IniRead(iniFile, "Config", "RandomOffset", 5)
    if (autoCombo) {
        if (autoComboRunning) {
            StopAutoCombo()
            return
        } else {
            StartAutoCombo(runa, delay, randomOffset)
            return
        }
    }
    ExecutarComboUmaVez(runa, delay, randomOffset)
}

; 🧩 Verifica a cor do alvo antes de executar o combo
ExecutarComboUmaVez(runa, delay := 100, randomOffset := 5) {
    global iniFile, autoComboRunning
    
    ; Verificação ANTES de qualquer processamento
    if (!VerificarCorAlvo(runa)) {
        ; Se a cor for IGUAL (sem alvo), para o Auto Combo se estiver rodando
        if (autoComboRunning) {
            StopAutoCombo(runa)
        }
        return false
    }
    
    ; Se passou na verificação de cor (alvo presente), executa o combo
    rp := IniRead(iniFile, runa, "RunePos", "")
    tp := IniRead(iniFile, runa, "TargetPos", "")
    
    if (rp = "" || rp = "ERROR" || tp = "" || tp = "ERROR") {
        TrayTip "⚠ Posições não definidas para " runa, ""
        SetTimer(LimparTrayTip, -2000)
        return false
    }
    
    rarr := StrSplit(rp, ",")
    tarr := StrSplit(tp, ",")
    baseRx := Integer(rarr[1])
    baseRy := Integer(rarr[2])
    baseTx := Integer(tarr[1])
    baseTy := Integer(tarr[2])

    randX1 := Random(-randomOffset, randomOffset)
    randY1 := Random(-randomOffset, randomOffset)
    randX2 := Random(-randomOffset, randomOffset)
    randY2 := Random(-randomOffset, randomOffset)
    rx := baseRx + randX1
    ry := baseRy + randY1
    tx := baseTx + randX2
    ty := baseTy + randY2

    origX := 0, origY := 0
    MouseGetPos(&origX, &origY)
    
    ; Executa as ações SEM delay entre elas
    MouseMove rx, ry, 2
    Sleep 50
    Click "Right", rx, ry
    MouseMove tx, ty, 2
    Sleep 50
    Click "Left", tx, ty
    MouseMove origX, origY, 0
    
    ; Aplica o delay APÓS retornar à posição original
    Sleep delay

    TrayTip "✅ " runa " executada! (Random: " randomOffset ")", ""
    SetTimer(LimparTrayTip, -1000)
    return true
}

; Função separada para verificar a cor do alvo
; Retorna TRUE se deve executar (alvo presente), FALSE se não deve executar (sem alvo)
VerificarCorAlvo(runa) {
    global iniFile
    
    verifyColor := IniRead(iniFile, runa, "VerifyColor", "ERROR")
    
    ; Se não tem cor definida, sempre executa
    if (verifyColor = "" || verifyColor = "ERROR") {
        return true
    }
    
    ; Obtém posição do alvo para verificar a cor
    tp := IniRead(iniFile, runa, "TargetPos", "")
    if (tp = "" || tp = "ERROR") {
        return true
    }
    
    tarr := StrSplit(tp, ",")
    baseTx := Integer(tarr[1])
    baseTy := Integer(tarr[2])
    
    currentColor := PixelGetColor(baseTx, baseTy, "RGB")
    
    ; 🔄 LÓGICA CORRETA: 
    ; Se a cor atual for DIFERENTE da cor marcada (do fundo), significa que o ALVO ESTÁ PRESENTE
    if (currentColor != verifyColor) {
        TrayTip "✅ Alvo detectado! (Cor diferente do fundo)", ""
        SetTimer(LimparTrayTip, -800)
        return true
    }
    
    ; Se a cor for IGUAL ao fundo, significa que NÃO TEM ALVO
    TrayTip "⏹️ Sem alvo! (Cor igual ao fundo)", ""
    SetTimer(LimparTrayTip, -1500)
    return false
}

StartAutoCombo(runa, delay, randomOffset) {
    global autoComboRuna, autoComboDelay, autoComboRandomOffset, autoComboRunning
    autoComboRuna := runa
    autoComboDelay := delay
    autoComboRandomOffset := randomOffset
    autoComboRunning := true
    
    ; Intervalo mais rápido para verificação contínua
    totalInterval := 300  ; Verifica a cada 300ms
    
    SetTimer AutoComboLoop, totalInterval
    TrayTip "🔄 Auto Combo iniciado para " runa, ""
    SetTimer(LimparTrayTip, -1000)
}

StopAutoCombo(runa := "") {
    global autoComboRunning
    autoComboRunning := false
    SetTimer AutoComboLoop, 0  ; Para completamente o timer
    TrayTip (runa ? "⏹️ Auto Combo parado para " runa : "⏹️ Auto Combo parado"), ""
    SetTimer(LimparTrayTip, -1000)
}

AutoComboLoop(*) {
    global autoComboRunning, autoComboRuna, autoComboDelay, autoComboRandomOffset
    if (autoComboRunning) {
        ; A verificação de cor é feita dentro de ExecutarComboUmaVez
        ExecutarComboUmaVez(autoComboRuna, autoComboDelay, autoComboRandomOffset)
    }
}

GuiClose(*) {
    ExitApp
}