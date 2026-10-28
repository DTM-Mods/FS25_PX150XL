. 'C:/Users/groov/OneDrive/Documents/My Games/FarmingSimulator2025/MOD PROJECTS/Library/_FS25Knowledge/tools/ge10/ui.ps1'
Assert-Editor;Click 24 40;Click 100 324;Start-Sleep 1;Click 1185 654;Send '{HOME}';Send '{ENTER}';Click 400 628;Paste (Join-Path $pwd 'source/integration/final_binary.i3d');Click 1040 734;Start-Sleep 4
Add-Type -AssemblyName System.Drawing;$b=New-Object System.Drawing.Bitmap 752,1102;$g=[System.Drawing.Graphics]::FromImage($b);$g.CopyFromScreen(192,86,0,0,$b.Size);$b.Save((Join-Path $pwd 'previews/hd50f_adapter_v1/final_runtime_ge_v1.png'));$g.Dispose();$b.Dispose()

