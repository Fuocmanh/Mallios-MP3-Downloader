Set WshShell = CreateObject("WScript.Shell")
' 0 means hidden window
WshShell.Run chr(34) & WScript.Arguments(0) & chr(34) & " " & chr(34) & WScript.Arguments(1) & chr(34), 0, False
