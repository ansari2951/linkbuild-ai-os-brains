Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "python run_247_daemon.py --interval 30", 0, False
Set WshShell = Nothing
