. 'C:/Users/groov/OneDrive/Documents/My Games/FarmingSimulator2025/MOD PROJECTS/Library/_FS25Knowledge/tools/ge10/ui.ps1'
$p=Get-Process editor | Where-Object MainWindowHandle -ne 0 | Select-Object -First 1
[void][U]::ShowWindow($p.MainWindowHandle,3); [void][U]::SetForegroundWindow($p.MainWindowHandle);Start-Sleep 1
Send "%f"
& 'C:/Users/groov/OneDrive/Documents/My Games/FarmingSimulator2025/MOD PROJECTS/Library/_FS25Knowledge/tools/ge10/mockup/cap.ps1' (Join-Path $pwd 'previews/hd50f_adapter_v1/menu.png')

Add-Type -AssemblyName System.Drawing
$b=New-Object System.Drawing.Bitmap 2560,1440
$g=[System.Drawing.Graphics]::FromImage($b)
$g.CopyFromScreen(0,0,0,0,$b.Size)
$b.Save((Join-Path $pwd 'previews/hd50f_adapter_v1/fullmenu.png'))
$g.Dispose();$b.Dispose()


