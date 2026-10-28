. 'C:/Users/groov/OneDrive/Documents/My Games/FarmingSimulator2025/MOD PROJECTS/Library/_FS25Knowledge/tools/ge10/ui.ps1'
Assert-Editor;Click 100 324;Start-Sleep 1
Add-Type -AssemblyName System.Drawing;$b=New-Object System.Drawing.Bitmap 1280,1392;$g=[System.Drawing.Graphics]::FromImage($b);$g.CopyFromScreen(0,0,0,0,$b.Size);$b.Save((Join-Path $pwd 'source/integration/export_dialog.png'));$g.Dispose();$b.Dispose()
