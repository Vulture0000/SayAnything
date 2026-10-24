' Launch SayAnything silently in the background without any CMD window
Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

currentDir = fso.GetParentFolderName(WScript.ScriptFullName)
venvPythonW = currentDir & "\.venv\Scripts\pythonw.exe"
mainScript = currentDir & "\main.py"

If fso.FileExists(venvPythonW) Then
    WshShell.Run """" & venvPythonW & """ """ & mainScript & """", 0, False
Else
    WshShell.Run "pythonw """ & mainScript & """", 0, False
End If
