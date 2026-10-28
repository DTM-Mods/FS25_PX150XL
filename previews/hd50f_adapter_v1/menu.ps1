. 'C:/Users/groov/OneDrive/Documents/My Games/FarmingSimulator2025/MOD PROJECTS/Library/_FS25Knowledge/tools/ge10/ui.ps1'
$p=Get-Process editor | Where-Object MainWindowHandle -ne 0 | Select-Object -First 1
[void][U]::ShowWindow($p.MainWindowHandle,3); [void][U]::SetForegroundWindow($p.MainWindowHandle);Start-Sleep 1
Click 16 32
& 'C:/Users/groov/OneDrive/Documents/My Games/FarmingSimulator2025/MOD PROJECTS/Library/_FS25Knowledge/tools/ge10/mockup/cap.ps1' (Join-Path $pwd 'previews/hd50f_adapter_v1/menu.png')
