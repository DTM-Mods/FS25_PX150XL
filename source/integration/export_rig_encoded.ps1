param([string]$Lua,[string]$Out)
. 'C:/Users/groov/OneDrive/Documents/My Games/FarmingSimulator2025/MOD PROJECTS/Library/_FS25Knowledge/tools/ge10/ui.ps1'
$p=Get-Process -Id 3284
Add-Type @"
using System;using System.Runtime.InteropServices;public class FHD { [DllImport("user32.dll")]public static extern uint GetWindowThreadProcessId(IntPtr h,IntPtr p);[DllImport("kernel32.dll")]public static extern uint GetCurrentThreadId();[DllImport("user32.dll")]public static extern bool AttachThreadInput(uint a,uint b,bool c);[DllImport("user32.dll")]public static extern bool BringWindowToTop(IntPtr h);}
"@
$a=[FHD]::GetCurrentThreadId();$b=[FHD]::GetWindowThreadProcessId([U]::GetForegroundWindow(),[IntPtr]::Zero)
[void][FHD]::AttachThreadInput($a,$b,$true)
[void][U]::ShowWindow($p.MainWindowHandle,9);[void][FHD]::BringWindowToTop($p.MainWindowHandle);[void][U]::SetForegroundWindow($p.MainWindowHandle)
[void][FHD]::AttachThreadInput($a,$b,$false);Start-Sleep 1
Assert-Editor;Send '{ESC}';Click 300 1310;Send '^a';Paste ('source("'+$Lua.Replace('\','/')+'")');Send '+{ENTER}';Start-Sleep 2
if($Out){ & 'C:/Users/groov/OneDrive/Documents/My Games/FarmingSimulator2025/MOD PROJECTS/Library/_FS25Knowledge/tools/ge10/mockup/cap.ps1' $Out }




Send '%f';Click 100 324;Start-Sleep 1;Click 1185 654;Send '{END}';Send '{ENTER}';Click 400 628;Paste (Join-Path $pwd 'source/integration/rig_encoded.obj');Click 1040 734;Start-Sleep 3;Click 300 1310;Send '^a';Paste ('source("'+$pwd.Path.Replace('\','/')+'/source/integration/restore_pose.lua")');Send '+{ENTER}';Start-Sleep 1

