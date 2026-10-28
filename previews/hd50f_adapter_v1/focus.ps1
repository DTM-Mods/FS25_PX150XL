. 'C:/Users/groov/OneDrive/Documents/My Games/FarmingSimulator2025/MOD PROJECTS/Library/_FS25Knowledge/tools/ge10/ui.ps1'
$p=Get-Process editor | Select-Object -First 1
[void][U]::ShowWindow($p.MainWindowHandle,9)
$ws=New-Object -ComObject WScript.Shell
$ws.AppActivate($p.Id) | Out-Null
Start-Sleep -Seconds 2
[void][U]::SetForegroundWindow($p.MainWindowHandle)
Foreground-Title
Add-Type -AssemblyName System.Drawing
$b=New-Object System.Drawing.Bitmap 2560,1440
$g=[System.Drawing.Graphics]::FromImage($b)
$g.CopyFromScreen(0,0,0,0,$b.Size)
$b.Save((Join-Path $pwd 'previews/hd50f_adapter_v1/screen.png'))
$g.Dispose();$b.Dispose()
