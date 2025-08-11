#Requires AutoHotKey v2.0
#SingleInstance Force

TraySetIcon "{resources}\mouse.ico"

global targetExe := ""
global ini := A_ScriptDir "\Cursor.ini"
global moving := false  ; 控制光标移动的全局变量

; 读取上次保存的目标进程名
if FileExist(ini)
    targetExe := IniRead(ini, "config", "executable", targetExe)

; 解析命令行参数：-e xxx / --executable=xxx
for i, arg in A_Args {
    if (arg = "-e" || arg = "--executable") {
        if (i+1 <= A_Args.Length)
            targetExe := A_Args[i+1]
    } else if RegExMatch(arg, "^-e=(.+)$", &m) {
        targetExe := m[1]
    } else if RegExMatch(arg, "^--executable=(.+)$", &m) {
        targetExe := m[1]
    }
}

; 热键绑定
Hotkey("^!F1", StartMoving)  ; 按 Ctrl+Alt+F1 启动移动
Hotkey("^!F2", EndMoving)    ; 按 Ctrl+Alt+F2 停止移动

; 托盘菜单
A_TrayMenu.Delete()
A_TrayMenu.Add("Start Moving", StartMoving)
A_TrayMenu.Add("End Moving", EndMoving)
A_TrayMenu.Add("Set target executable...", SetTarget)
A_TrayMenu.Add("Edit script", EditSelf)
A_TrayMenu.Add()
A_TrayMenu.Add("Exit", (*) => ExitApp())

; 定时检测 + 随机抖动
SetTimer(Watch, 200)
return

Watch() {
    global targetExe, moving
    if (moving) {
        MovePattern()  ; 如果正在移动，则调用移动模式
    } else if (targetExe = "" || ProcessExist(targetExe)) {
        ; if (Random(1, 10) = 1) { ; 10% tick 概率抖动，避免过于频繁
            MovePattern()
        ; }
    }
}

MovePattern() {
    ; Move right 5 times, 1 pixel each time with 0.1s sleep
    Loop 5 {
        MouseMove 1, 0, 0, "R"
        Sleep 100
    }
    ; Move left 5 times, 1 pixel each time with 0.1s sleep
    Loop 5 {
        MouseMove -1, 0, 0, "R"
        Sleep 100
    }
}

StartMoving(*) {
    global moving
    moving := true
}

EndMoving(*) {
    global moving
    moving := false
}

SetTarget(*) {
    global targetExe, ini
    ib := InputBox(
        "Enter target executable name (e.g. game.exe). Leave blank to always move.",
        "Set Executable", "w320 h150", targetExe
    )
    if (ib.Result = "OK") {
        targetExe := Trim(ib.Value)
        try IniWrite(targetExe, ini, "config", "executable")
    }
}

EditSelf(*) {
    Run("c:\Program Files\Notepad++\notepad++.exe " A_ScriptFullPath)
}
