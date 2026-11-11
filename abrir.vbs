' Abre el Asistente Legal sin mostrar ninguna ventana negra.
' Es lo que ejecutan los accesos directos del escritorio y del menu Inicio.
Set sh = CreateObject("WScript.Shell")
carpeta = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
sh.Run "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File """ & carpeta & "\abrir.ps1""", 0, False
